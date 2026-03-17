# ReadmeAI

<video src="https://github.com/DitisAlex/google-hackathon/raw/main/stitch-design/WhatsApp%20Video%202026-03-17%20at%2011.14.08.mp4" controls width="100%"></video>

> Onboarding into a new internal codebase often means wading through READMEs that are outdated or missing altogether, plus scattered internal documentation, before you can write a single line of code. **ReadmeAI** analyzes public or your internal GitHub repositories to generate clear, detailed, and always up-to-date READMEs tailored for new developers today — and tomorrow can power rich documentation for other internal tools and artifacts, from Jira projects to runbooks and beyond.

## How It Works

1. Paste a GitHub repository URL into the web app
2. A **Researcher Agent** analyzes the repo structure, tech stack, config files, and entry points
3. A **Technical Writer Agent** transforms that research into a polished, comprehensive README
4. View the result with an interactive preview, table of contents, and copy-to-clipboard

```
User → GitHub URL → Researcher Agent → Technical Writer Agent → Generated README
```

## Tech Stack

### Backend

| Technology | Purpose |
|---|---|
| Python 3.11+ | Runtime |
| FastAPI + Uvicorn | Async HTTP server |
| Google ADK v0.3+ | Agent orchestration framework |
| Gemini (2.0 Flash) | LLM for research & writing agents |
| httpx | Async GitHub API client |
| Pydantic v2 | Request/response validation |
| slowapi | Rate limiting |
| structlog | JSON structured logging |
| OpenTelemetry | Cloud Trace observability |

### Frontend

| Technology | Purpose |
|---|---|
| React 19 | UI framework |
| Vite 8 | Build tool & dev server |
| Tailwind CSS v3.4 | Styling |
| React Router DOM v7 | Client-side routing |
| react-markdown + remark-gfm | Markdown rendering |

### Deployment

| Technology | Purpose |
|---|---|
| Docker | Containerization (Python 3.11-slim) |
| Google Cloud Run | Managed serverless hosting |
| Cloud Trace | Distributed tracing |

## Project Structure

```
google-hackathon/
├── src/                            # Python backend
│   ├── main.py                     # FastAPI app entry point & middleware
│   ├── config.py                   # Environment config (Pydantic Settings)
│   ├── api/
│   │   ├── routes/
│   │   │   ├── generate.py         # POST /api/v1/generate & GET /api/v1/generate/{job_id}
│   │   │   └── health.py           # GET /api/v1/health
│   │   └── errors.py               # API error handling
│   ├── adk/
│   │   ├── orchestrator.py         # SequentialAgent pipeline (Researcher → Writer)
│   │   ├── agents/
│   │   │   ├── researcher.py       # Analyzes repo structure & tech stack
│   │   │   └── technical_writer.py # Produces polished markdown README
│   │   └── tools/
│   │       └── github_tool.py      # GitHub API wrapper (fetch tree, read files)
│   ├── models/
│   │   └── schemas.py              # Pydantic request/response models
│   ├── storage/
│   │   └── job_store.py            # In-memory job store + JSON snapshot persistence
│   └── utils/
│       ├── logger.py               # structlog config
│       └── tracing.py              # OpenTelemetry / Cloud Trace hooks
│
├── frontend/                       # React frontend
│   ├── src/
│   │   ├── App.jsx                 # Router setup
│   │   ├── pages/
│   │   │   ├── HomePage.jsx        # Landing page with repo URL input
│   │   │   └── ResultPage.jsx      # Generated README display with sidebar & preview
│   │   ├── components/
│   │   │   ├── Header.jsx          # Sticky navigation
│   │   │   ├── RepoInput.jsx       # GitHub URL input form
│   │   │   ├── ReadmePreview.jsx   # Preview / Raw markdown toggle
│   │   │   ├── ReadmeSidebar.jsx   # Auto-generated table of contents
│   │   │   ├── FeedbackForm.jsx    # Rating & comments
│   │   │   └── SummaryCard.jsx     # Info cards
│   │   └── services/
│   │       └── api.js              # Backend API client + mock data support
│   └── package.json
│
├── tests/                          # Backend test suite
├── Dockerfile                      # Production container image
├── Makefile                        # Build & test automation
├── requirements.txt                # Python dependencies
├── requirements-dev.txt            # Dev dependencies (pytest, ruff, mypy)
└── pyproject.toml                  # Ruff, pytest, mypy config
```

## Architecture

The backend uses a **two-agent sequential pipeline** powered by Google's Agent Development Kit (ADK):

```
POST /api/v1/generate
        │
        ▼
  Create async job (UUID)
  Return 202 Accepted
        │
        ▼
┌─────────────────────┐
│   Researcher Agent   │  Fetches repo tree, reads config files,
│   (Gemini 2.0 Flash) │  detects stack, identifies architecture
└────────┬────────────┘
         │ JSON research report
         ▼
┌─────────────────────────┐
│  Technical Writer Agent  │  Transforms research into
│   (Gemini 2.0 Flash)    │  structured markdown README
└────────┬────────────────┘
         │
         ▼
  Store result in JobStore
        │
        ▼
GET /api/v1/generate/{job_id}
  → Poll until completed
```

**Job lifecycle:** `queued` → `processing` → `completed` | `failed`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/generate` | Submit a repo URL for README generation (returns 202 + job ID) |
| `GET` | `/api/v1/generate/{job_id}` | Poll job status and retrieve generated README |
| `GET` | `/api/v1/health` | Health check |

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- A [Google AI API key](https://aistudio.google.com/apikey) (for Gemini)

### Backend

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # Add your GOOGLE_API_KEY
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev   # Runs on http://localhost:5173
```

### Docker

```bash
docker build -t readmeai:latest .
docker run --rm -p 8000:8000 --env-file .env readmeai:latest
```

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GOOGLE_API_KEY` | Yes | — | Gemini API key |
| `GITHUB_TOKEN` | No | — | GitHub PAT for higher rate limits |
| `GCP_PROJECT_ID` | No | — | Google Cloud project (for Cloud Trace) |
| `GEMINI_PRIMARY_MODEL` | No | `gemini-2.0-flash` | Primary LLM model |
| `GEMINI_FALLBACK_MODEL` | No | `gemini-2.0-flash` | Fallback LLM model |
| `MAX_JOB_TIMEOUT_SECONDS` | No | `120` | Max time per generation job |
| `REQUEST_RATE_LIMIT` | No | `10/minute` | API rate limit |
| `VITE_API_BASE_URL` | No | `http://localhost:8000` | Backend URL for frontend |
| `VITE_USE_MOCK` | No | `false` | Use mock data (no backend needed) |

## Testing & Linting

```bash
pytest -v                    # Run tests
ruff check src tests         # Lint
ruff format src tests        # Format
mypy src                     # Type check
```

## Cloud Run Deployment

```bash
gcloud auth application-default login
gcloud config set project <PROJECT_ID>
gcloud run deploy readmeai \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```
