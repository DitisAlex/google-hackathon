"""FastAPI application bootstrap and runtime wiring.

Data flow:
     1. Settings are loaded and used to configure logging/tracing/middleware.
    2. Shared app-state services (job store, orchestrator) are
         initialized once at startup.
     3. ``POST /generate`` enqueues background work via ``run_generation``.
    4. Background processing delegates README generation to an internal agent.
     5. ``GET /generate/{job_id}`` returns persisted status/result data.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from time import perf_counter
from uuid import uuid4
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from src.adk.orchestrator import DocumentationOrchestrator
from src.api.errors import ApiError
from src.api.routes.generate import router as generate_router
from src.api.routes.health import router as health_router
from src.config import get_settings
from src.models.schemas import GenerateOptions
from src.storage.job_store import JobStore
from src.utils.logger import bind_log_context, clear_log_context, configure_logger, get_logger
from src.utils.tracing import configure_tracing

settings = get_settings()

# Propagate API key loaded from .env into process env for ADK/GenAI SDKs.
if settings.google_api_key:
    os.environ["GOOGLE_API_KEY"] = settings.google_api_key

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

app.state.job_store = JobStore()
app.state.orchestrator = DocumentationOrchestrator(
    timeout_seconds=settings.max_job_timeout_seconds,
)
logger.info(
    "app_initialized",
    app_name=settings.app_name,
    env=settings.app_env,
    max_job_timeout_seconds=settings.max_job_timeout_seconds,
    google_api_key_set=bool(settings.google_api_key),
)


async def run_generation(job_id: str, github_url: str, options: GenerateOptions) -> None:
    """Execute the full generation pipeline for a submitted job.

    Args:
        job_id: Existing job identifier in ``JobStore``.
        github_url: Target repository URL.
        options: Generation options supplied by the request.

    Data flow:
        Marks the job as processing, requests README generation from the
        internal agent via
        the orchestrator, and persists final success/failure state.
    """
    try:
        bind_log_context(job_id=job_id)
        logger.info("job_started", github_url=github_url)
        app.state.job_store.set_processing(job_id)
        result = await app.state.orchestrator.run(github_url, options)
        app.state.job_store.set_completed(job_id, result)
        logger.info("job_completed", readme_chars=len(result.markdown or ""))
    except TimeoutError:
        app.state.job_store.set_failed(job_id, "TIMEOUT", "Job exceeded timeout")
        logger.warning("job_timeout")
    except Exception as exc:  # noqa: BLE001
        app.state.job_store.set_failed(job_id, "JOB_FAILED", str(exc))
        logger.exception("job_failed")
    finally:
        clear_log_context()


app.state.run_generation = run_generation


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Emit structured start/end logs with request ID and latency."""
    request_id = request.headers.get("x-request-id") or str(uuid4())
    start = perf_counter()
    bind_log_context(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    )

    logger.info("request_started")
    try:
        response = await call_next(request)
    except Exception:  # noqa: BLE001
        elapsed_ms = round((perf_counter() - start) * 1000, 2)
        logger.exception("request_unhandled_error", duration_ms=elapsed_ms)
        clear_log_context()
        raise

    elapsed_ms = round((perf_counter() - start) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info("request_completed", status_code=response.status_code, duration_ms=elapsed_ms)
    clear_log_context()
    return response


@app.middleware("http")
async def enforce_body_size_limit(request: Request, call_next):
    """Reject oversized request bodies before route handlers execute.

    Args:
        request: Incoming HTTP request.
        call_next: FastAPI middleware continuation callable.

    Returns:
        The downstream response when size checks pass.

    Raises:
        ApiError: If ``Content-Length`` exceeds configured limit.
    """
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.max_request_body_bytes:
        logger.warning("request_payload_too_large", content_length=int(content_length))
        raise ApiError(
            status_code=413,
            code="PAYLOAD_TOO_LARGE",
            message="Payload exceeds allowed limit",
            details={"max_bytes": settings.max_request_body_bytes},
        )
    return await call_next(request)


@app.exception_handler(ApiError)
async def api_error_handler(_: Request, exc: ApiError):
    """Render project-standard JSON response for :class:`ApiError`.

    Args:
        _: Unused request object required by FastAPI signature.
        exc: Raised application error.

    Returns:
        JSON response with status code and ``{"error": ...}`` payload.
    """
    logger.warning("api_error", status_code=exc.status_code, error=exc.detail)
    return JSONResponse(status_code=exc.status_code, content=exc.detail)


app.include_router(health_router)
app.include_router(generate_router)
