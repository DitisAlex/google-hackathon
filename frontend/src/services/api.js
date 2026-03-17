const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

// ---------------------------------------------------------------------------
// Mock — set VITE_USE_MOCK=true in .env to skip the real backend
// ---------------------------------------------------------------------------
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

function mockResponse(repoUrl) {
  const repoName = repoUrl.split('/').filter(Boolean).slice(-1)[0] ?? 'my-repo';
  const owner = repoUrl.split('/').filter(Boolean).slice(-2)[0] ?? 'owner';
  return {
    repoName,
    summary:
      `${repoName} is an open-source tool that automatically analyses a GitHub repository's ` +
      `file structure, commit history, and source code to generate a comprehensive, human-readable ` +
      `README. It identifies the primary programming language, dependencies, entry points, and ` +
      `key modules so you never have to write boilerplate documentation again.`,
    techStack: ['Python 3.11', 'FastAPI', 'Gemini 1.5 Pro', 'React', 'Tailwind CSS', 'Docker'],
    setupSteps: [
      'Clone the repository: git clone ' + repoUrl,
      'Copy the example env file: cp .env.example .env',
      'Add your GEMINI_API_KEY to .env',
      'Install dependencies: pip install -r requirements.txt',
      'Start the server: uvicorn main:app --reload',
    ],
    usageExamples:
      `# Summarise a repo via the API\n` +
      `curl -X POST http://localhost:8000/api/summarize \\\n` +
      `  -H "Content-Type: application/json" \\\n` +
      `  -d '{"repoUrl": "https://github.com/owner/repo"}'`,
    readme: [
      `# ${repoName}`,
      ``,
      `> **${repoName}** automatically analyses any GitHub repository and produces a clear, structured README — so new contributors understand the project in minutes, not hours.`,
      ``,
      `[![License: MIT](https://img.shields.io/badge/License-MIT-violet.svg)](https://opensource.org/licenses/MIT) [![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/) [![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green.svg)](https://fastapi.tiangolo.com/)`,
      ``,
      `---`,
      ``,
      `## 📖 Overview`,
      ``,
      `Many open-source projects suffer from missing or outdated documentation. Onboarding a new developer can take days of reading source code before they even run the project locally. **${repoName}** solves this by combining static analysis with the reasoning power of Gemini 1.5 Pro to produce a README draft that covers everything a new contributor needs.`,
      ``,
      `The tool walks the repository tree, parses imports and entry points, infers the tech stack, and extracts setup commands from \`Makefile\`, \`package.json\`, \`pyproject.toml\`, and similar files. It then feeds that structured context to Gemini and renders the result in a clean, copy-ready markdown document.`,
      ``,
      `## ✨ Features`,
      ``,
      `- 🔍 **Deep file-tree analysis** — understands folder conventions for Python, Node, Go, Rust, and more`,
      `- 🤖 **Gemini 1.5 Pro** — long-context model reads the entire codebase at once`,
      `- ⚡ **Fast** — typical repository analysed and documented in under 10 seconds`,
      `- 🌿 **Branch-aware** — targets any branch, not just \`main\``,
      `- 📋 **Copy-ready output** — one click to copy the finished markdown`,
      `- 🔒 **Read-only** — only clones/reads, never writes back to your repository`,
      ``,
      `## 🗂️ Project Structure`,
      ``,
      `\`\`\``,
      `${repoName}/`,
      `├── backend/`,
      `│   ├── main.py                 # FastAPI application entry point`,
      `│   ├── analyzer/`,
      `│   │   ├── __init__.py`,
      `│   │   ├── repo_walker.py      # Clones repo & builds file tree`,
      `│   │   ├── stack_detector.py   # Infers language & framework`,
      `│   │   └── prompt_builder.py   # Assembles Gemini prompt`,
      `│   ├── services/`,
      `│   │   └── gemini.py           # Gemini API client wrapper`,
      `│   └── requirements.txt`,
      `├── frontend/`,
      `│   ├── src/`,
      `│   │   ├── components/         # Reusable React components`,
      `│   │   ├── pages/              # Route-level page components`,
      `│   │   ├── services/api.js     # REST API calls`,
      `│   │   └── utils/              # Shared helpers`,
      `│   ├── index.html`,
      `│   └── package.json`,
      `├── docker-compose.yml`,
      `└── README.md`,
      `\`\`\``,
      ``,
      `## 🚀 Getting Started`,
      ``,
      `### Prerequisites`,
      ``,
      `- Python 3.11+`,
      `- Node.js 18+`,
      `- A [Google AI Studio](https://aistudio.google.com/) API key`,
      ``,
      `### Installation`,
      ``,
      `\`\`\`bash`,
      `# 1. Clone the repo`,
      `git clone ${repoUrl}`,
      `cd ${repoName}`,
      ``,
      `# 2. Configure environment`,
      `cp .env.example .env`,
      `# Edit .env and set GEMINI_API_KEY=your_key_here`,
      ``,
      `# 3. Start everything with Docker Compose`,
      `docker-compose up --build`,
      `\`\`\``,
      ``,
      `Or run services individually:`,
      ``,
      `\`\`\`bash`,
      `# Backend`,
      `cd backend`,
      `pip install -r requirements.txt`,
      `uvicorn main:app --reload`,
      ``,
      `# Frontend (separate terminal)`,
      `cd frontend`,
      `npm install && npm run dev`,
      `\`\`\``,
      ``,
      `## 📖 API Reference`,
      ``,
      `### \`POST /api/summarize\``,
      ``,
      `Analyse a repository and return a generated README.`,
      ``,
      `**Request body**`,
      ``,
      `\`\`\`json`,
      `{`,
      `  "repoUrl": "https://github.com/${owner}/${repoName}",`,
      `  "branch": "main"`,
      `}`,
      `\`\`\``,
      ``,
      `**Response**`,
      ``,
      `\`\`\`json`,
      `{`,
      `  "repoName": "${repoName}",`,
      `  "summary": "...",`,
      `  "techStack": ["Python", "FastAPI", "Gemini"],`,
      `  "setupSteps": ["git clone ...", "pip install ..."],`,
      `  "readme": "# ${repoName}\\n\\n..."`,
      `}`,
      `\`\`\``,
      ``,
      `| Status | Meaning |`,
      `|--------|---------|`,
      `| 200 | Success — README generated |`,
      `| 422 | Invalid or private repository URL |`,
      `| 500 | Gemini API error |`,
      ``,
      `## 🛠️ Tech Stack`,
      ``,
      `| Layer    | Technology           |`,
      `|----------|----------------------|`,
      `| Backend  | FastAPI + Python 3.11 |`,
      `| AI       | Gemini 1.5 Pro        |`,
      `| Frontend | React + Tailwind CSS  |`,
      `| Deploy   | Docker + Compose      |`,
      ``,
      `## 🤝 Contributing`,
      ``,
      `Contributions are welcome! Please open an issue first to discuss what you would like to change.`,
      ``,
      `1. Fork the repository`,
      `2. Create a feature branch: \`git checkout -b feat/my-feature\``,
      `3. Commit your changes: \`git commit -m "feat: add my feature"\``,
      `4. Push and open a Pull Request`,
      ``,
      `## 📄 License`,
      ``,
      `Distributed under the MIT License. See \`LICENSE\` for more information.`,
      ``,
      `---`,
      ``,
    ].join('\n'),
  };
}

// ---------------------------------------------------------------------------

/**
 * Ask the backend to summarize a GitHub repository and generate a README.
 *
 * @param {string} repoUrl - Full GitHub repository URL
 * @returns {Promise<{
 *   repoName: string,
 *   summary: string,
 *   techStack: string[],
 *   setupSteps: string[],
 *   usageExamples: string,
 *   readme: string,
 * }>}
 */
async function apiFetch(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    let message = `Server error: ${response.status}`;
    try {
      const body = await response.json();
      if (body?.error?.message) message = body.error.message;
      else if (body?.detail || body?.message) message = body.detail ?? body.message;
    } catch {
      // not JSON — keep the status-based message
    }
    throw new Error(message);
  }
  return response.json();
}

const POLL_INTERVAL_MS = 2000;
const POLL_TIMEOUT_MS = 300_000; // 5 minutes

export async function summarizeRepo(repoUrl) {
  if (USE_MOCK) {
    // Simulate network latency so the loading spinner is visible
    await new Promise((resolve) => setTimeout(resolve, 2200));
    return mockResponse(repoUrl);
  }

  // Step 1: submit the job
  const { job_id } = await apiFetch(`${API_BASE}/api/v1/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ github_url: repoUrl }),
  });

  // Step 2: poll until completed or failed
  const deadline = Date.now() + POLL_TIMEOUT_MS;
  while (Date.now() < deadline) {
    await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
    const job = await apiFetch(`${API_BASE}/api/v1/generate/${job_id}`);

    if (job.status === 'completed') {
      const repoName = repoUrl.split('/').filter(Boolean).slice(-1)[0] ?? 'repo';
      return {
        repoName,
        readme: job.result?.markdown ?? '',
      };
    }

    if (job.status === 'failed') {
      throw new Error(job.error?.message ?? 'Generation failed');
    }
    // status is 'queued' or 'processing' — keep polling
  }

  throw new Error('Request timed out. Please try again.');
}
