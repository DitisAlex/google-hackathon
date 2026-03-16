export default function SummaryCard({ title, icon, children }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-2 mb-3">
        {icon && <span className="text-brand-600 text-lg">{icon}</span>}
        <h3 className="font-semibold text-gray-800 text-base">{title}</h3>
      </div>
      <div className="text-gray-600 text-sm leading-relaxed">{children}</div>
    </div>
  );
}
