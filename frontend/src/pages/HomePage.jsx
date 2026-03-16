import Header from '../components/Header';
import RepoInput from '../components/RepoInput';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />

      <main className="flex-1 flex flex-col items-center justify-center px-4 py-8">
        {/* Hero */}
        <div className="text-center mb-7 max-w-2xl">
          <div className="inline-flex items-center gap-2 bg-brand-50 text-brand-600 text-sm font-medium
            px-4 py-1.5 rounded-full mb-6 border border-brand-100">
            Powered by Gemini AI
          </div>
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight mb-4">
            Turn any GitHub repo into a<br />
            <span className="text-brand-600">crystal-clear README</span>
          </h1>
          <p className="text-gray-500 text-lg leading-relaxed">
            Paste a GitHub repository URL and get an auto-generated README that developers
            actually understand — complete with setup steps, architecture overview, and usage examples.
          </p>
        </div>

        {/* Input card */}
        <div className="w-full max-w-2xl bg-white rounded-2xl border border-gray-200 shadow-md p-8">
          <RepoInput />
        </div>

        {/* Feature cards */}
        <div className="mt-6 w-full max-w-2xl grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { icon: '🗂️', label: 'Repo structure', desc: 'Full file tree analysis' },
            { icon: '🛠️', label: 'Tech stack', desc: 'Auto-detected languages & tools' },
            { icon: '⚙️', label: 'Setup steps', desc: 'Install & run instructions' },
            { icon: '▶️', label: 'Usage examples', desc: 'Code snippets & commands' },
          ].map(({ icon, label, desc }) => (
            <div key={label} className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm flex flex-col gap-1.5 hover:border-brand-300 hover:shadow-md transition">
              <span className="text-2xl">{icon}</span>
              <span className="text-sm font-semibold text-gray-800">{label}</span>
              <span className="text-xs text-gray-500 leading-snug">{desc}</span>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
