import React, { useMemo } from 'react';
import { ResponsiveContainer, LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { Download, Sparkles, FileText, Image as ImageIcon } from 'lucide-react';
import html2canvas from 'html2canvas';
import { saveAs } from 'file-saver';

export interface ChartBuilderProps {
  type: 'line' | 'area' | 'bar' | 'stacked_bar';
  data: any[];
  config: {
    xAxisKey: string;
    series: Array<{ key: string; color: string; name: string }>;
  };
  title?: string;
  subtitle?: string;
  sourceAttribution?: string;
  onExport?: (format: 'png' | 'svg') => void;
}

export function ChartBuilder({
  type,
  data,
  config,
  title = 'Energy Innovation Analytics Chart',
  subtitle = 'Visual analysis of energy innovation metrics and trends',
  sourceAttribution = 'U.S. Energy Innovation Database by Brandon N. Owens',
  onExport
}: ChartBuilderProps) {
  const chartId = `chart-${Math.random().toString(36).substr(2, 9)}`;

  const handleExportPNG = async () => {
    const el = document.getElementById(chartId);
    if (!el) return;

    try {
      // 1. Capture inner chart with high-density supersampling (scale: 3.5)
      const chartCanvas = await html2canvas(el, {
        backgroundColor: '#ffffff',
        scale: 3.5,
        useCORS: true,
        logging: false,
      });

      // 2. Composite into NYT / WSJ Executive Infographic
      const width = 2400;
      const padding = 80;
      const headerHeight = 220;
      const footerHeight = 100;
      const chartAspect = chartCanvas.height / chartCanvas.width;
      const chartAreaHeight = Math.round((width - padding * 2) * chartAspect);
      const height = headerHeight + chartAreaHeight + footerHeight;

      const compCanvas = document.createElement('canvas');
      compCanvas.width = width;
      compCanvas.height = height;
      const ctx = compCanvas.getContext('2d');
      if (!ctx) return;

      // Fill background
      ctx.fillStyle = '#FFFFFF';
      ctx.fillRect(0, 0, width, height);

      // Top Eyebrow Header
      ctx.font = '700 13px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
      ctx.fillStyle = '#0284C7';
      ctx.fillText('ENERGY INNOVATION TERMINAL · SOVEREIGN INTELLIGENCE EDITION', padding, 75);

      // Headline
      ctx.font = 'bold 42px Georgia, "Playfair Display", "Times New Roman", serif';
      ctx.fillStyle = '#0F172A';
      ctx.fillText(title, padding, 140);

      // Subtitle & Date
      ctx.font = '400 20px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
      ctx.fillStyle = '#64748B';
      ctx.fillText(subtitle, padding, 180);

      const today = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
      ctx.textAlign = 'right';
      ctx.fillText(`Edition: ${today}`, width - padding, 85);
      ctx.fillText('U.S. Energy Innovation Database by Brandon N. Owens', width - padding, 115);
      ctx.textAlign = 'left';

      // Divider
      ctx.strokeStyle = '#E2E8F0';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(padding, 205);
      ctx.lineTo(width - padding, 205);
      ctx.stroke();

      // Render chart
      const chartTop = 225;
      const chartW = width - padding * 2;
      const chartH = chartAreaHeight;

      ctx.drawImage(chartCanvas, 0, 0, chartCanvas.width, chartCanvas.height, padding, chartTop, chartW, chartH);

      // Frame around chart
      ctx.strokeStyle = '#CBD5E1';
      ctx.lineWidth = 1.5;
      ctx.strokeRect(padding, chartTop, chartW, chartH);

      // Footer Source Attribution
      const footerY = height - 45;
      ctx.font = '500 16px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
      ctx.fillStyle = '#64748B';
      ctx.fillText(sourceAttribution, padding, footerY);

      ctx.textAlign = 'right';
      ctx.fillText('U.S. Energy Innovation Database · Public Open Records (Not Affiliated with NYSERDA or US DOE)', width - padding, footerY);
      ctx.textAlign = 'left';

      compCanvas.toBlob((blob) => {
        if (blob) {
          const cleanName = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 40);
          saveAs(blob, `${cleanName}-highres.png`);
        }
      }, 'image/png');

      if (onExport) onExport('png');
    } catch (e) {
      console.error('Error exporting chart PNG:', e);
    }
  };

  if (!data || data.length === 0) {
    return (
      <div className="w-full h-64 flex items-center justify-center bg-slate-50 border border-slate-200 rounded-xl">
        <p className="text-slate-500">No data available</p>
      </div>
    );
  }

  const renderChart = () => {
    const commonProps = {
      data,
      margin: { top: 10, right: 30, left: 0, bottom: 0 }
    };

    switch (type) {
      case 'line':
        return (
          <LineChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
            <XAxis dataKey={config.xAxisKey} stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => val.toLocaleString()} />
            <Tooltip contentStyle={{ borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', background: 'rgba(255, 255, 255, 0.95)' }} />
            <Legend wrapperStyle={{ paddingTop: '20px', fontSize: '12px' }} />
            {config.series.map(s => (
              <Line key={s.key} type="monotone" dataKey={s.key} name={s.name} stroke={s.color} strokeWidth={2.5} dot={false} activeDot={{ r: 5, fill: s.color, stroke: '#ffffff', strokeWidth: 2 }} />
            ))}
          </LineChart>
        );
      case 'area':
        return (
          <AreaChart {...commonProps}>
            <defs>
              {config.series.map((s, i) => (
                <linearGradient key={`grad-area-${i}`} id={`grad-area-${s.key}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={s.color} stopOpacity={0.4}/>
                  <stop offset="95%" stopColor={s.color} stopOpacity={0.02}/>
                </linearGradient>
              ))}
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
            <XAxis dataKey={config.xAxisKey} stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => val.toLocaleString()} />
            <Tooltip contentStyle={{ borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', background: 'rgba(255, 255, 255, 0.95)' }} />
            <Legend wrapperStyle={{ paddingTop: '20px', fontSize: '12px' }} />
            {config.series.map(s => (
              <Area key={s.key} type="monotone" dataKey={s.key} name={s.name} fill={`url(#grad-area-${s.key})`} stroke={s.color} strokeWidth={2} activeDot={{ r: 5, fill: s.color, stroke: '#ffffff', strokeWidth: 2 }} />
            ))}
          </AreaChart>
        );
      case 'bar':
      case 'stacked_bar':
        return (
          <BarChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
            <XAxis dataKey={config.xAxisKey} stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => val.toLocaleString()} />
            <Tooltip contentStyle={{ borderRadius: '10px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', background: 'rgba(255, 255, 255, 0.95)' }} />
            <Legend wrapperStyle={{ paddingTop: '20px', fontSize: '12px' }} />
            {config.series.map(s => (
              <Bar key={s.key} dataKey={s.key} name={s.name} fill={s.color} radius={[6, 6, 0, 0]} stackId={type === 'stacked_bar' ? 'a' : undefined} />
            ))}
          </BarChart>
        );
    }
  };

  return (
    <div className="bg-white border border-slate-200 shadow-sm rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-slate-900 font-serif">{title}</h3>
          {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleExportPNG}
            className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold text-indigo-700 bg-indigo-50 border border-indigo-200 hover:bg-indigo-100 rounded-lg shadow-2xs transition-colors"
            title="Download High-Resolution PNG with Source Attribution"
          >
            <Download size={13} />
            <span>High-Res PNG</span>
          </button>
        </div>
      </div>
      <div id={chartId} className="w-full h-72 bg-white rounded-lg p-2">
        <ResponsiveContainer width="100%" height="100%">
          {renderChart()}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
