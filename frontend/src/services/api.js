import { mockResponse } from './mockData.js';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

// ---------------------------------------------------------------------------
// Auth API
// ---------------------------------------------------------------------------

const GITHUB_CLIENT_ID = import.meta.env.VITE_GITHUB_CLIENT_ID ?? '';

export function getGitHubLoginUrl() {
  if (!GITHUB_CLIENT_ID) {
    throw new Error('GitHub OAuth is not configured. Set VITE_GITHUB_CLIENT_ID in .env');
  }
  const state = crypto.randomUUID();
  const authorize_url =
    `https://github.com/login/oauth/authorize` +
    `?client_id=${encodeURIComponent(GITHUB_CLIENT_ID)}` +
    `&scope=repo` +
    `&state=${encodeURIComponent(state)}`;
  return { authorize_url, state };
}

export async function exchangeGitHubCode(code, state) {
  const response = await fetch(`${API_BASE}/api/v1/auth/github/callback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, state }),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body?.message || 'Failed to complete GitHub sign-in');
  }
  return response.json();
}

export async function getMe(token) {
  const response = await fetch(`${API_BASE}/api/v1/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error('Not authenticated');
  return response.json();
}

export async function getUserRepos(token) {
  const response = await fetch(`${API_BASE}/api/v1/auth/repos?per_page=50`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error('Failed to fetch repositories');
  return response.json();
}

// ---------------------------------------------------------------------------
// Generate API
// ---------------------------------------------------------------------------

/**
 * Ask the backend to generate a README for a GitHub repository.
 *
 * @param {object} params
 * @param {string} params.repoUrl - Full GitHub repository URL
 * @param {string|null} params.token - JWT auth token (null if not signed in)
 * @returns {Promise<{ job_id: string, status: string, created_at: string }>}
 */
export async function generateReadme({ repoUrl, token = null }) {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 2200));
    return mockResponse(repoUrl);
  }

  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}/api/v1/generate`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ github_url: repoUrl }),
  });

  if (!response.ok) {
    let message = `Server error: ${response.status}`;
    try {
      const errBody = await response.json();
      if (errBody?.detail || errBody?.message) {
        message = errBody.detail ?? errBody.message;
      }
    } catch {
      // not JSON — keep the status-based message
    }
    throw new Error(message);
  }

  return response.json();
}

/**
 * Poll a generation job until it completes or fails.
 *
 * @param {string} jobId - The job ID from generateReadme
 * @param {object} [opts]
 * @param {number} [opts.interval=2000] - Polling interval in ms
 * @param {number} [opts.timeout=300000] - Max wait time in ms (should match backend timeout)
 * @returns {Promise<{ status: string, result: object|null, error: object|null }>}
 */
export async function pollJobStatus(jobId, { interval = 2000, timeout = 180_000 } = {}) {
  const deadline = Date.now() + timeout;

  while (Date.now() < deadline) {
    const response = await fetch(`${API_BASE}/api/v1/generate/${jobId}`);
    if (!response.ok) throw new Error(`Failed to check job status: ${response.status}`);

    const data = await response.json();
    if (data.status === 'completed' || data.status === 'failed') {
      return data;
    }

    await new Promise((resolve) => setTimeout(resolve, interval));
  }

  throw new Error('Request timed out. Please try again.');
}
