# Full Data Workflow

## Overview
This service is a polling-based FastAPI backend that accepts repository-documentation jobs from a frontend, delegates README generation to the in-repo writer agent (`get_writer_agent()`), stores job state/results, and serves status updates back to clients.

## Components
- API entrypoint: `src/main.py`
- Request/response contracts: `src/models/schemas.py`
- HTTP routes: `src/api/routes/generate.py`, `src/api/routes/health.py`
- Error model/envelope: `src/api/errors.py`
- Orchestration layer: `src/adk/orchestrator.py`
- Job persistence and status state machine: `src/storage/job_store.py`
- Runtime configuration: `src/config.py`
- Logging/tracing hooks: `src/utils/logger.py`, `src/utils/tracing.py`

## Startup Workflow
1. `src/main.py` loads settings via `get_settings()` from `src/config.py`.
2. Logger and tracing are initialized.
3. Middleware is attached:
- CORS middleware.
- `slowapi` rate limiter middleware.
- Body-size guard middleware (`enforce_body_size_limit`).
4. App state dependencies are created:
- `JobStore` for in-memory + snapshot persistence.
- `DocumentationOrchestrator` that wraps internal agent invocation with timeout logic.
5. Routers are mounted for `/api/v1/health` and `/api/v1/generate*`.

## Request Lifecycle: Generate Job
### 1. Submit job
`POST /api/v1/generate`

Input shape (`GenerateRequest`):
- `github_url: str`
- `options: GenerateOptions`

Flow:
1. Route validates URL format against GitHub URL regex.
2. A `job_id` (UUID) is created.
3. `JobStore.create_job()` persists a `queued` job.
4. FastAPI `BackgroundTasks` schedules `run_generation(job_id, github_url, options)`.
5. API immediately returns `202 Accepted` with `GenerateAcceptedResponse`.

### 2. Background execution
`run_generation` in `src/main.py`

Flow:
1. `JobStore.set_processing(job_id)` transitions state to `processing`.
2. `DocumentationOrchestrator.run(...)` is called.
3. Orchestrator invokes `get_writer_agent()` from `src/adk/agents/skills/writer_agent.py` under `asyncio.wait_for(...)` timeout.
4. Function input is:
```json
{
  "github_url": "https://github.com/owner/repo",
  "options": {
    "branch": null,
    "max_depth": 5,
    "include_tests": false,
    "output_format": "markdown"
  }
}
```
5. Agent output is normalized into a JSON payload expected to include:
```json
{
  "readme.md": "# Generated README ..."
}
```
6. On success, backend stores only README text via `JobResult(markdown=...)` and marks job `completed`.
7. On timeout, backend marks job `failed` with `TIMEOUT`.
8. On any other exception, backend marks job `failed` with `JOB_FAILED`.

### 3. Poll status
`GET /api/v1/generate/{job_id}`

Flow:
1. Route fetches record using `JobStore.get_job(job_id)`.
2. If missing, returns `JOB_NOT_FOUND` (404).
3. If present, returns `JobStatusResponse` containing:
- `job_id`
- `status` (`queued`, `processing`, `completed`, `failed`)
- `result` (contains `markdown` when completed)
- `error` (contains `code/message/details` when failed)
- `created_at`

## Health Workflow
`GET /api/v1/health`

Returns:
- `status: "ok"`
- UTC `timestamp`

## Persistence Workflow
`JobStore` keeps data in two places:
1. In-memory dictionary for fast runtime access.
2. Snapshot file (`.jobs_snapshot.json`) for best-effort restart recovery.

Every state-changing call persists snapshot:
- `create_job`
- `set_processing`
- `set_completed`
- `set_failed`

At startup, `JobStore` tries to load snapshot; invalid/corrupt snapshots are ignored and state resets safely.

## Error Workflow
- Route/domain errors raise `ApiError` (`src/api/errors.py`).
- Global handler in `src/main.py` serializes errors in standard shape:
```json
{
  "error": {
    "code": "...",
    "message": "...",
    "details": {}
  }
}
```
- Rate-limit violations are handled by `slowapi` exception handler.
- Oversized payloads are rejected with `PAYLOAD_TOO_LARGE` (413) before route logic.

## Configuration Workflow
Environment variables are parsed into `Settings`:
- API/middleware settings (rate limit, max body bytes, timeout, CORS).

These are wired once at startup and reused via app state.

## Observability Workflow
- Logs are emitted as JSON via `structlog`.
- Tracing hook exists and can be expanded for OpenTelemetry/Cloud Trace.

## Test Workflow
- `tests/test_generate_endpoint.py` validates URL rejection and accepted-job behavior.
- `tests/test_health_endpoint.py` validates health response contract.
- `tests/conftest.py` provides a shared FastAPI test client.
