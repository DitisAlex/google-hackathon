import { useEffect, useState, useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import ReadmePreview from '../components/ReadmePreview';
import ReadmeSidebar from '../components/ReadmeSidebar';
import FeedbackForm from '../components/FeedbackForm';
import { summarizeRepo } from '../services/api';
import { extractHeadings } from '../utils/headings';

export default function ResultPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const repoUrl = location.state?.repoUrl;

  const [status, setStatus] = useState('loading'); // 'loading' | 'success' | 'error'
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    if (!repoUrl) {
      navigate('/', { replace: true });
      return;
    }

    let cancelled = false;
    setStatus('loading');
    setResult(null);

    async function fetchSummary() {
      try {
        const data = await summarizeRepo(repoUrl);
        if (!cancelled) {
          setResult(data);
          setStatus('success');
        }
      } catch (err) {
        if (!cancelled) {
          setErrorMsg(err.message || 'Something went wrong. Please try again.');
          setStatus('error');
        }
      }
    }

    fetchSummary();
    return () => { cancelled = true; };
  }, [repoUrl, navigate, refreshKey]);

  const headings = useMemo(
    () => (result?.readme ? extractHeadings(result.readme) : []),
    [result?.readme]
  );

  const [readmeView, setReadmeView] = useState('preview');

  function handleHeadingClick(id) {
    setReadmeView('preview');
    // Give React one tick to render the preview before scrolling
    setTimeout(() => {
      document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 50);
  }

  function handleRegenerate() {
    setErrorMsg('');
    setStatus('loading');
    setResult(null);
    setRefreshKey((k) => k + 1);
  }

  const repoName = result?.repoName
    ?? repoUrl?.split('/').filter(Boolean).slice(-1)[0]
    ?? '';

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />

      <main className="flex-1 max-w-5xl w-full mx-auto px-4 py-8">

        {/* ── Page title + action buttons ── */}
        <div className="flex items-start justify-between gap-4 mb-8">
          <div className="min-w-0">
            <h1 className="text-2xl font-bold text-gray-900 truncate">{repoName}</h1>
            {repoUrl && (
              <a
                href={repoUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-gray-400 hover:text-brand-600 transition truncate block mt-0.5"
              >
                {repoUrl}
              </a>
            )}
          </div>
          <div className="flex items-center gap-2 flex-shrink-0 pt-1">
            <button
              onClick={handleRegenerate}
              className="text-sm border border-gray-300 hover:border-brand-400 hover:text-brand-600 text-gray-600 rounded-lg px-4 py-2 font-medium transition"
            >
              ↺ Regenerate
            </button>
            <button
              onClick={() => navigate('/')}
              className="text-sm bg-brand-600 hover:bg-brand-700 text-white rounded-lg px-4 py-2 font-medium transition"
            >
              ← Home
            </button>
          </div>
        </div>

        {/* ── Loading ── */}
        {status === 'loading' && (
          <div className="flex flex-col items-center justify-center py-40 gap-5">
            <div className="w-12 h-12 rounded-full border-4 border-brand-200 border-t-brand-600 animate-spin" />
            <p className="text-gray-500 text-base">Analyzing repository…</p>
          </div>
        )}

        {/* ── Error ── */}
        {status === 'error' && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center">
            <p className="text-red-700 font-medium mb-4">{errorMsg}</p>
            <button
              onClick={() => navigate('/')}
              className="bg-brand-600 hover:bg-brand-700 text-white rounded-lg px-5 py-2 font-semibold transition"
            >
              Try another repo
            </button>
          </div>
        )}

        {/* ── Success: sidebar + content ── */}
        {status === 'success' && result && (
          <div className="flex gap-8">

            {/* Left sidebar — README heading navigation */}
            <aside className="w-52 flex-shrink-0 hidden md:block">
              <ReadmeSidebar headings={headings} onHeadingClick={handleHeadingClick} />
            </aside>

            {/* Right content */}
            <div className="flex-1 min-w-0 space-y-6">

              {/* Generated README */}
              <div>
                <h2 className="text-base font-semibold text-gray-700 mb-3">Generated README</h2>
                <ReadmePreview markdown={result.readme} view={readmeView} onViewChange={setReadmeView} />
              </div>

              {/* Feedback */}
              <FeedbackForm repoUrl={repoUrl} />

            </div>
          </div>
        )}
      </main>
    </div>
  );
}

