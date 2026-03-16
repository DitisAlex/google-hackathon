# ADK-Powered GitHub Repository Documentation Generator

Python + FastAPI backend boilerplate for Track 2 constraints:

- Vertex AI Agent Engine compatible orchestration pattern
- Cloud Run-first deployment
- Cloud Trace hooks (OpenTelemetry-ready)
- ADC-based authentication flow
- ADK-style two-agent pipeline (Researcher -> Technical Writer)
- Gemini model fallback policy (Gemini 3 preferred, fallback to Gemini 2.0 Flash)

## Stack

- Python 3.11+
- FastAPI + Uvicorn
- Pydantic v2
- httpx for GitHub API access
- slowapi for rate limiting
- structlog for JSON logging
- OpenTelemetry dependencies for Cloud Trace

## Implemented v1 Boilerplate

- POST /api/v1/generate
- GET /api/v1/generate/{job_id}
- GET /api/v1/health
- In-memory job store with local snapshot persistence (.jobs_snapshot.json)
- GitHub repo validation and repository tree retrieval
- Sequential two-stage orchestration (Researcher then Technical Writer)
- 120-second job timeout support

## Quickstart

1. Create a virtual environment and install dependencies.

	python3 -m venv .venv
	source .venv/bin/activate
	pip install -r requirements-dev.txt

2. Configure environment variables.

	cp .env.example .env

3. Start the service.

	uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

4. Test health endpoint.

	curl http://localhost:8000/api/v1/health

## API Examples

Create a generation job:

curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
	 "github_url": "https://github.com/owner/repo",
	 "options": {
		"max_depth": 5,
		"include_tests": false,
		"output_format": "markdown"
	 }
  }'

Poll job status:

curl http://localhost:8000/api/v1/generate/<job_id>

## Test and Lint

- Run tests: pytest -v
- Run lint: ruff check src tests
- Format: ruff format src tests

## Docker

Build image:

docker build -t repo-doc-generator:latest .

Run container:

docker run --rm -p 8000:8000 --env-file .env repo-doc-generator:latest

## Cloud Run Deployment

1. Authenticate with ADC:

	gcloud auth application-default login

2. Set project:

	gcloud config set project <PROJECT_ID>

3. Deploy:

	gcloud run deploy repo-doc-generator \
	  --source . \
	  --platform managed \
	  --region us-central1 \
	  --allow-unauthenticated

## Notes

- This is polling-only in v1 (SSE intentionally deferred).
- GKE is not configured in this boilerplate (Cloud Run primary).
- Local disk snapshots are best-effort and ephemeral on Cloud Run instances.
- Private repositories are out of scope in v1.