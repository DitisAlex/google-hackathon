export default function ReadmeSidebar({ headings, onHeadingClick }) {
  if (!headings.length) return null;

  function scrollTo(id) {
    if (onHeadingClick) {
      onHeadingClick(id);
    } else {
      document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  return (
    <nav className="sticky top-20 space-y-0.5">
      <div className="text-xs font-bold text-gray-400 uppercase tracking-widest px-3 mb-3">
        Contents
      </div>
      {headings.map(({ id, text, level }) => (
        <button
          key={id}
          onClick={() => scrollTo(id)}
          className={[
            'w-full text-left flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-colors',
            'text-gray-500 hover:bg-brand-50 hover:text-brand-600',
            level === 1 ? 'font-semibold text-gray-700' : '',
            level === 2 ? 'font-medium text-gray-600' : '',
            level === 3 ? 'pl-6 text-xs text-gray-400' : '',
          ].join(' ')}
        >
          {level === 2 && (
            <span className="text-gray-300 text-xs font-bold leading-none flex-shrink-0">#</span>
          )}
          <span className="truncate">{text}</span>
        </button>
      ))}
    </nav>
  );
}
