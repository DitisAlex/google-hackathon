/**
 * Mock response used when VITE_USE_MOCK=true.
 * Keeps the main api.js free of dev scaffolding.
 */
export function mockResponse(repoUrl) {
  const repoName = repoUrl.split('/').filter(Boolean).slice(-1)[0] ?? 'my-repo';
  const owner = repoUrl.split('/').filter(Boolean).slice(-2)[0] ?? 'owner';
  return {
    repoName,
    summary:
      `${repoName} is an open-source tool that automatically analyses a GitHub repository's ` +
      `file structure, commit history, and source code to generate a comprehensive, human-readable ` +
      `README. It identifies the primary programming language, dependencies, entry points, and ` +
      `key modules so you never have to write boilerplate documentation again.`,
    techStack: ['Python 3.11', 'FastAPI', 'Gemini 2.5 Flash', 'React', 'Tailwind CSS', 'Docker'],
    readme: [
      `# ${repoName}`,
      ``,
      `> **${repoName}** automatically analyses any GitHub repository and produces a clear, structured README.`,
      ``,
      `## Overview`,
      ``,
      `Paste a GitHub URL and get an auto-generated README covering setup, architecture, and usage.`,
      ``,
      `## Tech Stack`,
      ``,
      `| Layer    | Technology           |`,
      `|----------|----------------------|`,
      `| Backend  | FastAPI + Python 3.11 |`,
      `| AI       | Gemini 2.5 Flash      |`,
      `| Frontend | React + Tailwind CSS  |`,
      `| Deploy   | Docker + Cloud Run    |`,
      ``,
      `## Getting Started`,
      ``,
      `\`\`\`bash`,
      `git clone ${repoUrl}`,
      `cd ${repoName}`,
      `cp .env.example .env`,
      `# Set GOOGLE_API_KEY in .env`,
      `docker-compose up --build`,
      `\`\`\``,
      ``,
      `## API`,
      ``,
      `\`POST /api/v1/generate\` — submit a repo URL, returns \`{ job_id }\``,
      ``,
      `\`GET /api/v1/generate/{job_id}\` — poll for result`,
    ].join('\n'),
  };
}
