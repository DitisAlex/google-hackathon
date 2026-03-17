from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from src.adk.orchestrator import DocumentationOrchestrator
from src.adk.tools.github_tool import GithubTool
from src.api.errors import ApiError
from src.api.routes.auth import router as auth_router
from src.api.routes.generate import router as generate_router
from src.api.routes.health import router as health_router
from src.config import get_settings
from src.models.schemas import GenerateOptions
from src.storage.job_store import JobStore
from src.utils.logger import configure_logger, get_logger
from src.utils.tracing import configure_tracing

settings = get_settings()
configure_logger(settings.log_level)
configure_tracing(settings)
logger = get_logger(__name__)

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.request_rate_limit])

app = FastAPI(title=settings.app_name)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.settings = settings
app.state.job_store = JobStore()


async def run_generation(job_id: str, github_tool: GithubTool, github_url: str, options: GenerateOptions) -> None:
    orchestrator = DocumentationOrchestrator(
        github_tool=github_tool,
        timeout_seconds=settings.max_job_timeout_seconds,
        model=settings.gemini_primary_model,
        api_key=settings.google_api_key,
    )
    try:
        app.state.job_store.set_processing(job_id)
        research, result = await orchestrator.run(github_url, options)
        app.state.job_store.set_researcher_output(job_id, research)
        app.state.job_store.set_completed(job_id, result)
        logger.info("job_completed", job_id=job_id)
    except TimeoutError:
        app.state.job_store.set_failed(job_id, "TIMEOUT", "Job exceeded timeout")
        logger.warning("job_timeout", job_id=job_id)
    except Exception as exc:  # noqa: BLE001
        app.state.job_store.set_failed(job_id, "JOB_FAILED", str(exc))
        logger.exception("job_failed", job_id=job_id)


app.state.run_generation = run_generation


@app.middleware("http")
async def enforce_body_size_limit(request: Request, call_next) -> JSONResponse:
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.max_request_body_bytes:
        raise ApiError(
            status_code=413,
            code="PAYLOAD_TOO_LARGE",
            message="Payload exceeds allowed limit",
            details={"max_bytes": settings.max_request_body_bytes},
        )
    return await call_next(request)


@app.exception_handler(ApiError)
async def api_error_handler(_: Request, exc: ApiError):
    return JSONResponse(status_code=exc.status_code, content=exc.detail)


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(generate_router)

# Mount static files for the frontend
if os.path.exists("frontend/dist"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Serve actual files if they exist
        file_path = os.path.join("frontend/dist", full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        # Otherwise, serve index.html for SPA routing
        return FileResponse("frontend/dist/index.html")
