import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function RepoInput() {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

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

  return (
    <form onSubmit={handleSubmit} className="w-full">
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
  );
}
