**Backend PRD**

ADK-Powered GitHub Repository Documentation Generator

| **Version** | 1.0         |
| ----------- | ----------- |
| **Status**  | Draft       |
| **Date**    | 2026-03-16  |
| **Author**  | Engineering |

## **1\. Overview**

This document defines the backend architecture and implementation requirements for an ADK-powered service that accepts a GitHub repository URL, analyzes its contents through a multi-agent pipeline, and produces structured Markdown documentation. The system comprises two primary subsystems: the ADK Core (agent orchestration and tooling) and the HTTP API layer that exposes it.

## **2\. System Architecture**

The backend follows a layered architecture with clear separation of concerns between the API surface, the agent orchestration layer, and the external integrations.

### **2.1 High-Level Components**

- **API Layer:** Express/Fastify HTTP server exposing RESTful endpoints for generation requests and job management.
- **ADK Orchestration:** A ManagedLoop that coordinates the Researcher and Technical Writer agents in sequence.
- **GithubTool:** A custom ADK tool responsible for fetching repository file trees and reading file content via the GitHub API.
- **Output Formatter:** Transforms the Technical Writer's raw output into the final deliverable format (Markdown or extended).

### **2.2 Request Lifecycle**

- Client sends POST /api/v1/generate with a GitHub URL.
- Validation middleware checks URL format, reachability, and public accessibility.
- A job is created and the ADK ManagedLoop is triggered asynchronously.
- Agent 1 (Researcher) uses GithubTool to analyze the repo's file tree, identify entry points, detect the tech stack, and infer project purpose.
- Agent 2 (Technical Writer) receives the Researcher's structured output and transforms it into polished Markdown documentation.
- The final output is stored and returned to the client via polling or real-time stream.

## **3\. ADK Core Implementation**

### **3.1 GithubTool**

A custom ADK tool that wraps the GitHub REST API (or GraphQL API) to provide two core capabilities:

- **fetchTree(repoUrl):** Retrieves the full file/directory tree of a repository, returning paths, types, and sizes. Supports filtering by depth and file extension.
- **readFile(repoUrl, filePath):** Fetches the raw content of a single file. Handles encoding (base64 for binary detection, UTF-8 for text). Respects rate limits with exponential backoff.

Configuration parameters:

- MAX_FILE_SIZE: 100 KB (skip large binaries/generated files)
- RATE_LIMIT_RETRY: 3 attempts with exponential backoff
- GITHUB_TOKEN: Optional personal access token for higher rate limits

### **3.2 Agent 1 - Researcher**

Goal: Analyze the repository and produce a structured research report covering:

- Detected tech stack and frameworks (language, package manager, build tools)
- Project entry points (main files, index files, CLI entrypoints)
- Inferred project purpose and domain
- Key dependencies and their roles
- Directory structure summary with annotations

The Researcher agent receives language-specific prompt augmentations. When the detected primary language is Python, the prompts emphasize pyproject.toml, setup.py, and \__init_\_.py conventions. For JavaScript/TypeScript, they emphasize package.json, tsconfig, and module resolution. Similar augmentations exist for Go, Rust, Java, and Ruby.

### **3.3 Agent 2 - Technical Writer**

Goal: Transform the Researcher's structured output into clean, well-organized Markdown documentation containing:

- Project title and one-line description
- Tech stack summary table
- Architecture overview with entry points
- Directory structure (tree format)
- Setup and installation instructions (inferred from config files)
- Key modules and their responsibilities

### **3.4 ManagedLoop Orchestration**

The ManagedLoop is configured to execute the agents sequentially. The Researcher's output object is injected into the Technical Writer's context as a structured input variable. The loop supports optional callbacks for real-time event emission (used by the SSE stream).

## **4\. API Specification**

### **4.1 Endpoints**

| **Method** | **Path**                       | **Body / Params**                                 | **Description**                                                                              |
| ---------- | ------------------------------ | ------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| **POST**   | /api/v1/generate               | { github_url: string, options?: GenerateOptions } | Accepts a GitHub repo URL, triggers the ADK agent loop, returns the generated documentation. |
| **GET**    | /api/v1/generate/:jobId        | -                                                 | Poll job status and retrieve results for async generation.                                   |
| **GET**    | /api/v1/health                 | -                                                 | Health check endpoint for load balancers and monitoring.                                     |
| **GET**    | /api/v1/generate/:jobId/stream | -                                                 | (Optional) SSE stream for real-time agent thought output.                                    |

### **4.2 POST /api/v1/generate - Request Schema**

The request body must be JSON with the following fields:

| **Field**             | **Type** | **Required** | **Description**                                |
| --------------------- | -------- | ------------ | ---------------------------------------------- |
| github_url            | string   | Yes          | Full HTTPS URL to a public GitHub repository.  |
| options.branch        | string   | No           | Target branch (default: default branch).       |
| options.max_depth     | integer  | No           | Max directory depth to traverse (default: 5).  |
| options.include_tests | boolean  | No           | Include test file analysis (default: false).   |
| options.output_format | string   | No           | Output format: 'markdown' (default) or 'json'. |

### **4.3 Response Schema (Success)**

On successful completion, the API returns:

| **Field**       | **Type** | **Description**                                        |
| --------------- | -------- | ------------------------------------------------------ |
| job_id          | string   | Unique identifier for the generation job.              |
| status          | string   | One of: queued, processing, completed, failed.         |
| result.markdown | string   | Generated Markdown documentation (when completed).     |
| result.metadata | object   | Detected tech stack, file count, and processing stats. |
| created_at      | string   | ISO 8601 timestamp of job creation.                    |

## **5\. Validation and Error Handling**

### **5.1 Input Validation**

All incoming requests to /api/v1/generate must pass the following checks before the ADK loop is triggered:

- **URL Format:** Must be a valid HTTPS URL matching the pattern <https://github.com/{owner}/{repo}>. Reject malformed URLs with 400.
- **Repository Accessibility:** Perform a lightweight HEAD request to the GitHub API to confirm the repo exists and is public. Return 404 for missing repos, 403 for private repos.
- **Rate Limiting:** Enforce per-IP rate limits (configurable, default 10 requests/minute). Return 429 with Retry-After header.
- **Payload Size:** Reject request bodies exceeding 10 KB with 413.

### **5.2 Error Response Format**

All errors follow a consistent JSON structure:

- error.code: Machine-readable error code (e.g., INVALID_URL, REPO_NOT_FOUND, RATE_LIMITED)
- error.message: Human-readable description
- error.details: Optional object with additional context (e.g., retry_after for rate limits)

### **5.3 ADK Error Handling**

If an agent fails mid-loop (GitHub API outage, context overflow, timeout), the job status transitions to 'failed' with a diagnostic payload. Partial results from the Researcher are preserved when possible so the client can retry from a checkpoint.

## **6\. Real-Time Output Stream (Optional)**

For clients that want to observe the agent's reasoning in real time, the backend optionally supports Server-Sent Events (SSE) on the /api/v1/generate/:jobId/stream endpoint.

### **6.1 Event Types**

| **Event**      | **Payload**                         | **Description**                                  |
| -------------- | ----------------------------------- | ------------------------------------------------ |
| agent:start    | { agent: 'researcher' \| 'writer' } | Emitted when an agent begins execution.          |
| agent:thought  | { agent: string, thought: string }  | Intermediate reasoning or action from the agent. |
| agent:complete | { agent: string, summary: string }  | Agent finished; includes output summary.         |
| job:complete   | { markdown: string }                | Final documentation ready.                       |
| job:error      | { code: string, message: string }   | Unrecoverable error during generation.           |

## **7\. Recommended Project Structure**

The following directory layout provides clear separation between the API layer, agent orchestration, and shared utilities:

src/

api/

routes/generate.ts - POST /generate and GET /generate/:jobId

routes/health.ts - GET /health

middleware/validation.ts - URL format, repo accessibility checks

middleware/rateLimit.ts - Per-IP rate limiting

middleware/errorHandler.ts - Global error handler

adk/

tools/GithubTool.ts - fetchTree + readFile implementations

agents/researcher.ts - Agent 1 definition and goal

agents/technicalWriter.ts - Agent 2 definition and goal

orchestrator.ts - ManagedLoop configuration

prompts/ - Language-specific prompt templates

config/

index.ts - Environment variable loader

types/

index.ts - Shared TypeScript interfaces

index.ts - Application entry point

## **8\. Non-Functional Requirements**

- **Timeout:** Maximum 120 seconds per generation job. Configurable via environment variable.
- **Concurrency:** Support at least 10 concurrent generation jobs per instance.
- **Logging:** Structured JSON logs (pino or winston) with correlation IDs per request.
- **Environment:** Node.js 20+ / TypeScript 5+. Docker-ready with multi-stage build.
- **Testing:** Unit tests for GithubTool, integration tests for the /generate endpoint, and agent output snapshot tests.
- **Security:** No credentials stored in code. GitHub tokens injected via environment. CORS restricted to allowed origins.

## **9\. Out of Scope (v1)**

- Authentication and user accounts
- Persistent storage / database for job history
- Private repository support (requires OAuth flow)
- Frontend application
- CI/CD pipeline configuration
- Multi-repo or monorepo analysis