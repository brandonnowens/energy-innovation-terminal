import React, { useEffect, useRef, useState } from 'react';
import { Network, Copy, Check, AlertCircle, RefreshCw } from 'lucide-react';

interface MermaidDiagramProps {
  chart: string;
  id?: string;
}

export const MermaidDiagram: React.FC<MermaidDiagramProps> = ({ chart }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svgContent, setSvgContent] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const uniqueId = useRef(`mermaid_${Math.random().toString(36).substring(2, 9)}`);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);

    const renderChart = async () => {
      try {
        // Dynamically load mermaid from CDN if not already on window
        if (!(window as any).mermaid) {
          const importMermaid = new Function("url", "return import(url)");
          const mermaidModule = await importMermaid('https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs');
          (window as any).mermaid = mermaidModule.default;
          (window as any).mermaid.initialize({
            startOnLoad: false,
            theme: 'neutral',
            securityLevel: 'loose',
            fontFamily: 'system-ui, -apple-system, sans-serif',
            fontSize: 13,
            flowchart: {
              curve: 'basis',
              padding: 16,
              nodeSpacing: 40,
              rankSpacing: 40,
            }
          });
        }

        const mermaid = (window as any).mermaid;
        const cleanChart = chart.trim();
        const renderId = `${uniqueId.current}_${Date.now()}`;
        
        const { svg } = await mermaid.render(renderId, cleanChart);
        if (isMounted) {
          setSvgContent(svg);
          setIsLoading(false);
        }
      } catch (err: any) {
        if (isMounted) {
          console.warn('Mermaid render error:', err);
          setError(err.message || 'Failed to render diagram');
          setIsLoading(false);
        }
      }
    };

    renderChart();

    return () => {
      isMounted = false;
    };
  }, [chart]);

  const handleCopyCode = () => {
    navigator.clipboard.writeText(chart);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Extract diagram type
  const firstLine = chart.trim().split('\n')[0].trim().toLowerCase();
  let diagramType = 'Diagram';
  if (firstLine.startsWith('graph') || firstLine.startsWith('flowchart')) diagramType = 'Flowchart';
  else if (firstLine.startsWith('gantt')) diagramType = 'Gantt Timeline';
  else if (firstLine.startsWith('sequence')) diagramType = 'Sequence Diagram';
  else if (firstLine.startsWith('state')) diagramType = 'State Flow';
  else if (firstLine.startsWith('mindmap')) diagramType = 'Mindmap';
  else if (firstLine.startsWith('erdiagram') || firstLine.startsWith('er')) diagramType = 'Entity Model';

  return (
    <div className="my-4 rounded-2xl border border-slate-200 bg-white overflow-hidden shadow-2xs">
      {/* Diagram Header Bar */}
      <div className="bg-slate-50/80 px-3.5 py-2 border-b border-slate-100 flex items-center justify-between text-[11.5px] text-slate-500 font-medium">
        <div className="flex items-center gap-2">
          <Network size={13} className="text-cyan-600" />
          <span className="font-semibold text-slate-700">{diagramType}</span>
        </div>

        <button
          type="button"
          onClick={handleCopyCode}
          className="inline-flex items-center gap-1 text-[11px] text-slate-500 hover:text-slate-800 transition-colors cursor-pointer px-2 py-0.5 rounded-md hover:bg-slate-200/60"
          title="Copy Diagram Source Code"
        >
          {copied ? <Check size={11} className="text-emerald-600" /> : <Copy size={11} />}
          <span>{copied ? 'Copied' : 'Copy Code'}</span>
        </button>
      </div>

      {/* Diagram Canvas Body */}
      <div className="p-4 bg-slate-50/30 overflow-x-auto flex justify-center min-h-[140px] items-center">
        {isLoading ? (
          <div className="flex items-center gap-2 text-slate-400 text-[12px] py-6 animate-pulse">
            <RefreshCw size={13} className="animate-spin text-cyan-600" />
            <span>Rendering visual architecture diagram...</span>
          </div>
        ) : error ? (
          <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-[12px] flex items-start gap-2 max-w-lg">
            <AlertCircle size={14} className="text-amber-600 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <span className="font-semibold block">Diagram Code:</span>
              <pre className="font-mono text-[11px] text-slate-700 whitespace-pre-wrap">{chart}</pre>
            </div>
          </div>
        ) : (
          <div
            ref={containerRef}
            className="mermaid-svg-container w-full flex justify-center [&>svg]:max-w-full [&>svg]:h-auto [&>svg]:drop-shadow-2xs"
            dangerouslySetInnerHTML={{ __html: svgContent }}
          />
        )}
      </div>
    </div>
  );
};
