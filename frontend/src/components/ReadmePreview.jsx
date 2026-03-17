import { useState, useEffect, useRef, useId } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import mermaid from 'mermaid';
import { slugify } from '../utils/headings';

mermaid.initialize({ startOnLoad: false, theme: 'default', securityLevel: 'strict' });

function MermaidBlock({ chart }) {
  const ref = useRef(null);
  const uniqueId = useId().replaceAll(':', '_');
  const [svg, setSvg] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const { svg: rendered } = await mermaid.render(`mermaid${uniqueId}`, chart);
        if (!cancelled) setSvg(rendered);
      } catch (err) {
        if (!cancelled) setError(err.message || 'Failed to render diagram');
      }
    })();
    return () => { cancelled = true; };
  }, [chart, uniqueId]);

  if (error) {
    return (
      <pre className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700 overflow-x-auto mb-4">
        {chart}
      </pre>
    );
  }

  return (
    <div
      ref={ref}
      className="my-6 flex justify-center overflow-x-auto"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}

function nodeText(node) {
  if (!node) return '';
  if (node.type === 'text') return node.value;
  if (node.children) return node.children.map(nodeText).join('');
  return '';
}

// Explicit per-element renderers — no typography plugin needed
const mdComponents = {
  h1: ({ node, children }) => (
    <h1 id={slugify(nodeText(node))} className="text-3xl font-black text-gray-900 mt-8 mb-4 scroll-mt-24 first:mt-0">{children}</h1>
  ),
  h2: ({ node, children }) => (
    <h2 id={slugify(nodeText(node))} className="text-xl font-bold text-gray-800 mt-10 mb-3 pb-2 border-b border-gray-200 scroll-mt-24">{children}</h2>
  ),
  h3: ({ node, children }) => (
    <h3 id={slugify(nodeText(node))} className="text-base font-semibold text-gray-700 mt-6 mb-2 scroll-mt-24">{children}</h3>
  ),
  p: ({ children }) => (
    <p className="text-gray-600 leading-7 mb-4">{children}</p>
  ),
  ul: ({ children }) => (
    <ul className="list-disc pl-6 mb-4 space-y-1 text-gray-600">{children}</ul>
  ),
  ol: ({ children }) => (
    <ol className="list-decimal pl-6 mb-4 space-y-1 text-gray-600">{children}</ol>
  ),
  li: ({ children }) => (
    <li className="leading-7">{children}</li>
  ),
  a: ({ href, children }) => (
    <a href={href} target="_blank" rel="noopener noreferrer" className="text-brand-600 hover:underline">{children}</a>
  ),
  blockquote: ({ children }) => (
    <blockquote className="border-l-4 border-brand-300 pl-4 my-4 italic text-gray-500">{children}</blockquote>
  ),
  hr: () => (
    <hr className="border-gray-200 my-6" />
  ),
  // Inline code
  code: ({ inline, className, children }) => {
    // Detect mermaid fenced code blocks
    if (!inline && /language-mermaid/.test(className || '')) {
      const chart = String(children).replace(/\n$/, '');
      return <MermaidBlock chart={chart} />;
    }
    if (inline) {
      return (
        <code className="bg-gray-100 rounded px-1 py-0.5 text-sm font-mono text-gray-800">{children}</code>
      );
    }
    return (
      <code className={className}>{children}</code>
    );
  },
  pre: ({ children }) => {
    // If the child is a MermaidBlock, render it directly without the <pre> wrapper
    if (children?.type === MermaidBlock) {
      return children;
    }
    return (
      <pre className="bg-gray-900 text-gray-100 rounded-xl p-4 overflow-x-auto mb-4 text-sm font-mono leading-relaxed">{children}</pre>
    );
  },
  table: ({ children }) => (
    <div className="overflow-x-auto mb-4">
      <table className="w-full text-sm border-collapse">{children}</table>
    </div>
  ),
  th: ({ children }) => (
    <th className="bg-gray-50 border border-gray-200 px-3 py-2 text-left font-semibold text-gray-700">{children}</th>
  ),
  td: ({ children }) => (
    <td className="border border-gray-200 px-3 py-2 text-gray-600">{children}</td>
  ),
  strong: ({ children }) => (
    <strong className="font-semibold text-gray-800">{children}</strong>
  ),
};

export default function ReadmePreview({ markdown, view, onViewChange }) {
  const [internalView, setInternalView] = useState('preview');
  const activeView = view ?? internalView;
  function setView(v) { onViewChange ? onViewChange(v) : setInternalView(v); }
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(markdown);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // clipboard API unavailable — silently fail
    }
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-5 py-2.5 border-b border-gray-100 bg-gray-50">
        <div className="flex items-center gap-0.5 bg-gray-200 rounded-md p-0.5">
          {['preview', 'raw'].map((v) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`text-sm px-3 py-1 rounded font-medium capitalize transition ${
                activeView === v
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {v}
            </button>
          ))}
        </div>
        <button
          onClick={handleCopy}
          className="text-sm text-brand-600 hover:text-brand-700 font-medium transition"
        >
          {copied ? '✓ Copied!' : 'Copy to clipboard'}
        </button>
      </div>

      {/* Content */}
      {activeView === 'preview' ? (
        <div className="px-8 py-7">
          <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
            {markdown}
          </ReactMarkdown>
        </div>
      ) : (
        <pre className="p-6 overflow-x-auto text-sm font-mono leading-relaxed whitespace-pre-wrap break-words bg-gray-950 text-green-400">
          {markdown}
        </pre>
      )}
    </div>
  );
}


