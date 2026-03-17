import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getGitHubLoginUrl, getUserRepos } from '../services/api';

export default function RepoInput() {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');
  const [repos, setRepos] = useState([]);
  const [loadingRepos, setLoadingRepos] = useState(false);
  const navigate = useNavigate();
  const { user, token } = useAuth();

  useEffect(() => {
    if (!token) {
      setRepos([]);
      return;
    }
    setLoadingRepos(true);
    getUserRepos(token)
      .then(setRepos)
      .catch(() => setRepos([]))
      .finally(() => setLoadingRepos(false));
  }, [token]);

  function handleSignIn() {
    try {
      const { authorize_url, state } = getGitHubLoginUrl();
      sessionStorage.setItem('oauth_state', state);
      window.location.href = authorize_url;
    } catch (err) {
      alert(err.message);
    }
  }

  function isValidGitHubUrl(value) {
    return /^https:\/\/github\.com\/[\w.-]+\/[\w.-]+(\/.*)?$/.test(value.trim());
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!isValidGitHubUrl(url)) {
      setError('Please enter a valid GitHub repository URL (e.g. https://github.com/owner/repo)');
      return;
    }
    setError('');
    navigate('/result', { state: { repoUrl: url.trim() } });
  }

  function handleSelectRepo(repo) {
    setUrl(repo.html_url);
    setError('');
    navigate('/result', { state: { repoUrl: repo.html_url } });
  }

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit}>
        <label htmlFor="repo-url" className="block text-sm font-medium text-gray-700 mb-2">
          GitHub Repository URL
        </label>
        <div className="flex gap-3">
          <input
            id="repo-url"
            type="url"
            value={url}
            onChange={(e) => { setUrl(e.target.value); setError(''); }}
            placeholder="https://github.com/owner/repository"
            className="flex-1 rounded-lg border border-gray-300 px-4 py-3 text-gray-900 text-base
              placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent
              transition"
            autoComplete="off"
            spellCheck={false}
          />
          <button
            type="submit"
            className="whitespace-nowrap rounded-lg bg-brand-600 hover:bg-brand-700 active:bg-brand-700
              text-white font-semibold px-6 py-3 transition focus:outline-none focus:ring-2
              focus:ring-brand-500 focus:ring-offset-2"
          >
            Generate README
          </button>
        </div>
        {error && (
          <p className="mt-2 text-sm text-red-600">{error}</p>
        )}
      </form>

      {!user && (
        <div className="mt-3 flex items-center gap-2">
          <button
            type="button"
            onClick={handleSignIn}
            className="inline-flex items-center gap-2 rounded-lg border border-gray-300 px-3 py-1.5
              text-sm font-medium text-gray-700 hover:bg-gray-50 transition"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57
                0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695
                -.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99
                .105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225
                -.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405
                c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225
                0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3
                0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
            </svg>
            Sign in with GitHub
          </button>
          <span className="text-sm text-gray-500">to access private repositories</span>
        </div>
      )}

      {user && (
        <div className="mt-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Your repositories</p>
          {loadingRepos ? (
            <div className="flex items-center gap-2 py-3">
              <div className="w-4 h-4 rounded-full border-2 border-brand-200 border-t-brand-600 animate-spin" />
              <span className="text-sm text-gray-500">Loading repos...</span>
            </div>
          ) : repos.length === 0 ? (
            <p className="text-sm text-gray-400 py-2">No repositories found.</p>
          ) : (
            <div className="max-h-56 overflow-y-auto rounded-lg border border-gray-200 divide-y divide-gray-100">
              {repos.map((repo) => (
                <button
                  key={repo.full_name}
                  type="button"
                  onClick={() => handleSelectRepo(repo)}
                  className="w-full text-left px-3 py-2.5 hover:bg-brand-50 transition flex items-center gap-3 group"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-900 truncate group-hover:text-brand-600">
                        {repo.full_name}
                      </span>
                      {repo.private && (
                        <span className="flex-shrink-0 text-[10px] font-medium bg-yellow-100 text-yellow-700 px-1.5 py-0.5 rounded">
                          Private
                        </span>
                      )}
                      {repo.language && (
                        <span className="flex-shrink-0 text-[10px] font-medium bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded">
                          {repo.language}
                        </span>
                      )}
                    </div>
                    {repo.description && (
                      <p className="text-xs text-gray-500 truncate mt-0.5">{repo.description}</p>
                    )}
                  </div>
                  <svg className="w-4 h-4 text-gray-300 group-hover:text-brand-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
