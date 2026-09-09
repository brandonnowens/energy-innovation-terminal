import React, { useState, useEffect, useRef } from 'react';
import {
  Download, X, Sparkles, Image as ImageIcon, Check, Sliders,
  Layers, MapPin, DollarSign, Calendar, Eye, Loader2,
  Printer, Share2, Smartphone, Monitor, Globe
} from 'lucide-react';
import { saveAs } from 'file-saver';
import { AwardMapMarker, AwardMapSummary } from '../api/client';

export type MapPresetCategory = 'publication' | 'social';

export type AspectRatio =
  | '16:9'              // 4K Wall Art (3840x2160)
  | '4:3'               // Poster (3200x2400)
  | '3:2'               // Publication (3600x2400)
  | '1:1'               // Gallery Square (2400x2400)
  | '9:16'              // Instagram Story (2160x3840)
  | 'social_landscape'  // X & LinkedIn (2400x1350)
  | 'social_banner';    // OpenGraph Banner (2400x1256)

export type MapTheme = 'editorial' | 'dark' | 'minimal' | 'blueprint';

interface AwardMapNYTExportProps {
  isOpen: boolean;
  onClose: () => void;
  getMapCanvas: () => HTMLCanvasElement | null;
  markers: AwardMapMarker[];
  summary?: AwardMapSummary | null;
  activeFiltersDesc?: string;
  colorByMode: string;
  colorPalette: Record<string, string>;
}

export const AwardMapNYTExport: React.FC<AwardMapNYTExportProps> = ({
  isOpen,
  onClose,
  getMapCanvas,
  markers,
  summary,
  activeFiltersDesc = 'All Tracked Energy Innovation Innovation Awards & Programs',
  colorByMode,
  colorPalette,
}) => {
  const [aspectRatio, setAspectRatio] = useState<AspectRatio>('16:9');
  const [presetCategory, setPresetCategory] = useState<MapPresetCategory>('publication');
  const [theme, setTheme] = useState<MapTheme>('editorial');
  const [title, setTitle] = useState('THE GEOGRAPHY OF ENERGY INNOVATION INNOVATION');
  const [subtitle, setSubtitle] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  // Set default subtitle when summary updates
  useEffect(() => {
    if (summary) {
      const fundStr = summary.total_funding >= 1e9
        ? `$${(summary.total_funding / 1e9).toFixed(1)} Billion`
        : `$${(summary.total_funding / 1e6).toFixed(1)} Million`;
      setSubtitle(`Distribution of ${fundStr} across ${summary.total_matches.toLocaleString()} energy innovation awards spanning 50 states, federal & state agencies, electric utilities, and research laboratories.`);
    }
  }, [summary]);

  // Re-render preview canvas whenever settings change
  useEffect(() => {
    if (!isOpen) return;
    generateCanvasPreview();
  }, [isOpen, aspectRatio, theme, title, subtitle, markers, colorByMode]);

  const getDimensions = (): { width: number; height: number; isVertical: boolean; isSquare: boolean } => {
    switch (aspectRatio) {
      case '16:9':
        return { width: 3840, height: 2160, isVertical: false, isSquare: false }; // 4K Master Ultra-HD
      case '4:3':
        return { width: 3200, height: 2400, isVertical: false, isSquare: false }; // Exhibition Poster
      case '3:2':
        return { width: 3600, height: 2400, isVertical: false, isSquare: false }; // Broadside
      case '1:1':
        return { width: 2400, height: 2400, isVertical: false, isSquare: true };  // Square Gallery Post
      case '9:16':
        return { width: 2160, height: 3840, isVertical: true, isSquare: false };  // Instagram Story / Vertical 4K
      case 'social_landscape':
        return { width: 2400, height: 1350, isVertical: false, isSquare: false }; // X (Twitter) / LinkedIn
      case 'social_banner':
        return { width: 2400, height: 1256, isVertical: false, isSquare: false }; // Banner 1.91:1
      default:
        return { width: 3840, height: 2160, isVertical: false, isSquare: false };
    }
  };

  const generateCanvas = (): HTMLCanvasElement | null => {
    const mapCanvas = getMapCanvas();
    if (!mapCanvas) return null;

    const { width, height, isVertical, isSquare } = getDimensions();

    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;

    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';

    // Theme Color Schemes
    const themeColors = {
      editorial: {
        bg: '#FDFBF7',
        border: '#1A202C',
        textPrimary: '#111827',
        textSecondary: '#4B5563',
        textMuted: '#6B7280',
        cardBg: 'rgba(255, 255, 255, 0.94)',
        cardBorder: '#E5E7EB',
        accent: '#4F46E5',
        gold: '#B45309',
        divider: '#E5E7EB',
      },
      dark: {
        bg: '#090D16',
        border: '#334155',
        textPrimary: '#F8FAFC',
        textSecondary: '#94A3B8',
        textMuted: '#64748B',
        cardBg: 'rgba(15, 23, 42, 0.90)',
        cardBorder: '#334155',
        accent: '#6366F1',
        gold: '#F59E0B',
        divider: '#1E293B',
      },
      minimal: {
        bg: '#FFFFFF',
        border: '#0F172A',
        textPrimary: '#0F172A',
        textSecondary: '#334155',
        textMuted: '#64748B',
        cardBg: 'rgba(248, 250, 252, 0.96)',
        cardBorder: '#E2E8F0',
        accent: '#2563EB',
        gold: '#92400E',
        divider: '#E2E8F0',
      },
      blueprint: {
        bg: '#0A192F',
        border: '#38BDF8',
        textPrimary: '#E0F2FE',
        textSecondary: '#7DD3FC',
        textMuted: '#38BDF8',
        cardBg: 'rgba(12, 34, 64, 0.88)',
        cardBorder: '#0284C7',
        accent: '#38BDF8',
        gold: '#FBBF24',
        divider: '#0369A1',
      },
    }[theme];

    // 1. Background
    ctx.fillStyle = themeColors.bg;
    ctx.fillRect(0, 0, width, height);

    // 2. Outer Neatline & Frame Border
    const margin = Math.round(width * 0.022);
    ctx.strokeStyle = themeColors.border;
    ctx.lineWidth = Math.max(3, Math.round(width * 0.0015));
    ctx.strokeRect(margin, margin, width - margin * 2, height - margin * 2);

    const innerMarginOffset = Math.round(margin * 0.2);
    ctx.strokeStyle = themeColors.border;
    ctx.lineWidth = Math.max(1, Math.round(width * 0.0005));
    ctx.strokeRect(
      margin + innerMarginOffset,
      margin + innerMarginOffset,
      width - (margin + innerMarginOffset) * 2,
      height - (margin + innerMarginOffset) * 2
    );

    // Corner tick crosshairs
    const tickLen = Math.round(margin * 0.45);
    ctx.lineWidth = Math.max(1.5, Math.round(width * 0.0007));
    ctx.beginPath();
    ctx.moveTo(margin - tickLen, margin); ctx.lineTo(margin + tickLen, margin);
    ctx.moveTo(margin, margin - tickLen); ctx.lineTo(margin, margin + tickLen);
    ctx.moveTo(width - margin - tickLen, margin); ctx.lineTo(width - margin + tickLen, margin);
    ctx.moveTo(width - margin, margin - tickLen); ctx.lineTo(width - margin, margin + tickLen);
    ctx.moveTo(margin - tickLen, height - margin); ctx.lineTo(margin + tickLen, height - margin);
    ctx.moveTo(margin, height - margin - tickLen); ctx.lineTo(margin, height - margin + tickLen);
    ctx.moveTo(width - margin - tickLen, height - margin); ctx.lineTo(width - margin + tickLen, height - margin);
    ctx.moveTo(width - margin, height - margin - tickLen); ctx.lineTo(width - margin, height - margin + tickLen);
    ctx.stroke();

    // 3. Header Block
    const headerTop = margin + Math.round(margin * 0.7);
    const contentLeft = margin + Math.round(margin * 0.9);
    const contentRight = width - margin - Math.round(margin * 0.9);

    // Eyebrow
    const eyebrowSize = Math.max(14, Math.round(width * 0.007));
    ctx.font = `700 ${eyebrowSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
    ctx.fillStyle = themeColors.gold;
    ctx.fillText('ENERGY INNOVATION GEOSPATIAL INTELLIGENCE · NATIONAL ATLAS', contentLeft, headerTop + eyebrowSize);

    // Main Title (Executive Serif Style)
    const titleSize = isVertical
      ? Math.max(38, Math.round(width * 0.032))
      : isSquare
      ? Math.max(40, Math.round(width * 0.024))
      : Math.max(44, Math.round(width * 0.021));
    ctx.font = `bold ${titleSize}px Georgia, "Playfair Display", "Times New Roman", serif`;
    ctx.fillStyle = themeColors.textPrimary;
    const titleY = headerTop + eyebrowSize + Math.round(titleSize * 1.25);
    ctx.fillText(title || 'THE GEOGRAPHY OF ENERGY INNOVATION INNOVATION', contentLeft, titleY);

    // Dynamic Subtitle
    const subtitleSize = isVertical
      ? Math.max(18, Math.round(width * 0.015))
      : Math.max(18, Math.round(width * 0.010));
    ctx.font = `400 ${subtitleSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
    ctx.fillStyle = themeColors.textSecondary;
    const subText = subtitle || `Visualizing spatial capital deployment across ${markers.length.toLocaleString()} energy innovation innovation awards.`;
    const subtitleY = titleY + Math.round(subtitleSize * 1.7);
    ctx.fillText(subText, contentLeft, subtitleY);

    // Header Right Meta (if not vertical)
    if (!isVertical) {
      const today = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
      const metaSize = Math.max(13, Math.round(width * 0.0065));
      ctx.font = `500 ${metaSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
      ctx.fillStyle = themeColors.textMuted;
      ctx.textAlign = 'right';
      ctx.fillText(`Cartography Date: ${today}`, contentRight, headerTop + metaSize);
      ctx.fillText(`Database Scope: ${activeFiltersDesc.slice(0, 48)}`, contentRight, headerTop + metaSize * 2.4);
      ctx.textAlign = 'left';
    }

    // Header divider line
    const headerDividerY = subtitleY + Math.round(margin * 0.6);
    ctx.strokeStyle = themeColors.divider;
    ctx.lineWidth = Math.max(1, Math.round(width * 0.0006));
    ctx.beginPath();
    ctx.moveTo(contentLeft, headerDividerY);
    ctx.lineTo(contentRight, headerDividerY);
    ctx.stroke();

    // 4. Map Image Rendering Frame
    const footerHeight = Math.max(40, Math.round(height * 0.035));
    const footerBottom = height - margin - Math.round(margin * 0.4);
    const mapTop = headerDividerY + Math.round(margin * 0.4);
    const mapBottom = footerBottom - footerHeight;
    const mapHeight = mapBottom - mapTop;
    const mapWidth = contentRight - contentLeft;

    ctx.save();
    ctx.beginPath();
    ctx.roundRect(contentLeft, mapTop, mapWidth, mapHeight, Math.round(width * 0.003));
    ctx.clip();
    ctx.drawImage(mapCanvas, contentLeft, mapTop, mapWidth, mapHeight);
    ctx.restore();

    ctx.strokeStyle = themeColors.border;
    ctx.lineWidth = Math.max(1.2, Math.round(width * 0.0006));
    ctx.strokeRect(contentLeft, mapTop, mapWidth, mapHeight);

    // 5. Inset Legend Card (Bottom Left)
    const colorEntries = Object.entries(colorPalette).slice(0, 6);
    const legWidth = Math.min(Math.round(mapWidth * 0.38), Math.round(width * 0.24));
    const itemRowHeight = Math.max(22, Math.round(height * 0.015));
    const legHeight = Math.min(
      Math.round(mapHeight * 0.45),
      Math.round(height * 0.04) + colorEntries.length * itemRowHeight + Math.round(height * 0.07)
    );
    const legendX = contentLeft + Math.round(margin * 0.5);
    const legendY = mapTop + mapHeight - legHeight - Math.round(margin * 0.5);

    ctx.fillStyle = themeColors.cardBg;
    ctx.beginPath();
    ctx.roundRect(legendX, legendY, legWidth, legHeight, 10);
    ctx.fill();
    ctx.strokeStyle = themeColors.cardBorder;
    ctx.lineWidth = Math.max(1, Math.round(width * 0.0005));
    ctx.stroke();

    const legTitleSize = Math.max(12, Math.round(width * 0.006));
    ctx.font = `bold ${legTitleSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
    ctx.fillStyle = themeColors.textPrimary;
    ctx.fillText(`LEGEND · COLOR BY ${colorByMode.toUpperCase()}`, legendX + Math.round(legWidth * 0.06), legendY + legTitleSize * 1.8);

    let swatchY = legendY + legTitleSize * 3.2;
    const swatchRadius = Math.max(5, Math.round(width * 0.0025));
    const swatchFontSize = Math.max(11, Math.round(width * 0.0055));

    colorEntries.forEach(([key, color]) => {
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(legendX + Math.round(legWidth * 0.08), swatchY - swatchRadius * 0.4, swatchRadius, 0, Math.PI * 2);
      ctx.fill();

      ctx.font = `500 ${swatchFontSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
      ctx.fillStyle = themeColors.textSecondary;
      const maxChars = isVertical ? 18 : 26;
      const labelText = key.length > maxChars ? key.slice(0, maxChars) + '…' : key;
      ctx.fillText(labelText, legendX + Math.round(legWidth * 0.15), swatchY);
      swatchY += itemRowHeight;
    });

    // Proportional Funding Bubble Size Reference
    const bubbleY = swatchY + Math.round(height * 0.008);
    const scaleLabelSize = Math.max(10, Math.round(width * 0.005));
    ctx.font = `bold ${scaleLabelSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
    ctx.fillStyle = themeColors.textMuted;
    ctx.fillText('AWARD FUNDING SCALE', legendX + Math.round(legWidth * 0.06), bubbleY);

    const sizes = [
      { label: '$100K', r: Math.max(3, Math.round(width * 0.002)) },
      { label: '$1M', r: Math.max(6, Math.round(width * 0.0035)) },
      { label: '$10M', r: Math.max(10, Math.round(width * 0.0055)) },
      { label: '$50M+', r: Math.max(14, Math.round(width * 0.008)) },
    ];
    let bubbleX = legendX + Math.round(legWidth * 0.12);
    const bubbleStep = Math.round((legWidth * 0.78) / sizes.length);

    sizes.forEach((s) => {
      ctx.fillStyle = themeColors.accent;
      ctx.globalAlpha = 0.65;
      ctx.beginPath();
      ctx.arc(bubbleX, bubbleY + Math.round(height * 0.02), s.r, 0, Math.PI * 2);
      ctx.fill();
      ctx.globalAlpha = 1.0;
      ctx.strokeStyle = themeColors.border;
      ctx.lineWidth = Math.max(0.8, Math.round(width * 0.0004));
      ctx.stroke();

      ctx.font = `500 ${scaleLabelSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
      ctx.fillStyle = themeColors.textMuted;
      ctx.textAlign = 'center';
      ctx.fillText(s.label, bubbleX, bubbleY + Math.round(height * 0.04));
      bubbleX += bubbleStep;
    });
    ctx.textAlign = 'left';

    // 6. Inset Summary Stats Card (Bottom Right)
    if (summary) {
      const statsWidth = Math.min(Math.round(mapWidth * 0.36), Math.round(width * 0.22));
      const statRowHeight = Math.max(28, Math.round(height * 0.018));
      const statsHeight = Math.round(height * 0.035) + 4 * statRowHeight;
      const statsX = contentRight - statsWidth - Math.round(margin * 0.5);
      const statsY = mapTop + mapHeight - statsHeight - Math.round(margin * 0.5);

      ctx.fillStyle = themeColors.cardBg;
      ctx.beginPath();
      ctx.roundRect(statsX, statsY, statsWidth, statsHeight, 10);
      ctx.fill();
      ctx.strokeStyle = themeColors.cardBorder;
      ctx.lineWidth = Math.max(1, Math.round(width * 0.0005));
      ctx.stroke();

      const statTitleSize = Math.max(12, Math.round(width * 0.006));
      ctx.font = `bold ${statTitleSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
      ctx.fillStyle = themeColors.textPrimary;
      ctx.fillText('EXECUTIVE SUMMARY STATS', statsX + Math.round(statsWidth * 0.06), statsY + statTitleSize * 1.8);

      const kpis = [
        { label: 'Total Funding', val: `$${(summary.total_funding / 1e9).toFixed(2)}B` },
        { label: 'Mapped Awards', val: summary.total_matches.toLocaleString() },
        { label: 'Unique Recipients', val: summary.unique_recipients.toLocaleString() },
        { label: 'States Covered', val: `${summary.states_covered} Covered` },
      ];

      let kpiY = statsY + statTitleSize * 3.4;
      const statLabelSize = Math.max(12, Math.round(width * 0.0055));
      const statValSize = Math.max(13, Math.round(width * 0.006));

      kpis.forEach((kpi) => {
        ctx.font = `400 ${statLabelSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
        ctx.fillStyle = themeColors.textSecondary;
        ctx.fillText(kpi.label, statsX + Math.round(statsWidth * 0.06), kpiY);

        ctx.font = `bold ${statValSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
        ctx.fillStyle = themeColors.textPrimary;
        ctx.textAlign = 'right';
        ctx.fillText(kpi.val, statsX + statsWidth - Math.round(statsWidth * 0.06), kpiY);
        ctx.textAlign = 'left';

        kpiY += statRowHeight;
      });
    }

    // 7. Footer Attribution Block (Prominently displayed)
    const footerY = height - margin + Math.max(4, Math.round(margin * 0.1));
    const footerFontSize = Math.max(12, Math.round(width * 0.006));
    ctx.font = `500 ${footerFontSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
    ctx.fillStyle = themeColors.textMuted;
    ctx.fillText(
      'U.S. Energy Innovation Database by Brandon N. Owens',
      contentLeft,
      footerY
    );

    ctx.textAlign = 'right';
    ctx.fillText('Public Open Records (Not Affiliated with NYSERDA or US DOE)', contentRight, footerY);
    ctx.textAlign = 'left';

    return canvas;
  };

  const generateCanvasPreview = () => {
    setIsGenerating(true);
    try {
      const c = generateCanvas();
      if (c) {
        setPreviewUrl(c.toDataURL('image/png'));
      }
    } catch (e) {
      console.error('Error rendering preview:', e);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = () => {
    const c = generateCanvas();
    if (!c) return;

    c.toBlob((blob) => {
      if (blob) {
        const ts = new Date().toISOString().slice(0, 10);
        const presetTag = aspectRatio.replace(':', 'x');
        saveAs(blob, `energy-innovation-terminal-wall-map-${presetTag}-${ts}.png`);
      }
    }, 'image/png');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-md">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-6xl w-full max-h-[92vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/80">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-700 text-white shadow-md">
              <Sparkles size={18} />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <span>Executive GIS Wall Map &amp; Publication Studio</span>
                <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold border border-emerald-200">
                  4K / 300 DPI Ultra-HD
                </span>
              </h2>
              <p className="text-xs text-slate-500">
                Download a high-resolution, publication-ready thematic wall map citing <strong>U.S. Energy Innovation Database by Brandon N. Owens</strong>.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left: Customization Settings */}
          <div className="lg:col-span-5 space-y-4">
            {/* Category Mode Switcher */}
            <div>
              <label className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block mb-2">
                Export Category &amp; Target Medium
              </label>
              <div className="flex bg-slate-100 p-1 rounded-xl">
                <button
                  onClick={() => {
                    setPresetCategory('publication');
                    setAspectRatio('16:9');
                  }}
                  className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                    presetCategory === 'publication'
                      ? 'bg-white text-indigo-700 shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <Printer size={14} /> Executive Wall Art &amp; Print
                </button>
                <button
                  onClick={() => {
                    setPresetCategory('social');
                    setAspectRatio('social_landscape');
                  }}
                  className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                    presetCategory === 'social'
                      ? 'bg-white text-indigo-700 shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <Share2 size={14} /> Social Media Optimized
                </button>
              </div>
            </div>

            {/* Aspect Ratio / Print Ratio */}
            {presetCategory === 'publication' ? (
              <div>
                <label className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block mb-1.5">
                  Editorial Print &amp; Display Aspect Ratio
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { id: '16:9', label: '16:9 Wall Art', desc: '3840×2160 (4K Master)' },
                    { id: '4:3', label: '4:3 Exhibition', desc: '3200×2400 (Poster)' },
                    { id: '3:2', label: '3:2 Broadside', desc: '3600×2400 (Publication)' },
                    { id: '1:1', label: '1:1 Gallery Square', desc: '2400×2400 (Art Print)' },
                  ].map((ar) => (
                    <button
                      key={ar.id}
                      onClick={() => setAspectRatio(ar.id as AspectRatio)}
                      className={`p-2.5 rounded-xl border text-left transition-all ${
                        aspectRatio === ar.id
                          ? 'border-indigo-600 bg-indigo-50/60 shadow-xs'
                          : 'border-slate-200 hover:border-slate-300 bg-white'
                      }`}
                    >
                      <span className="text-xs font-bold text-slate-800 block">{ar.label}</span>
                      <span className="text-[10px] text-slate-500 block mt-0.5">{ar.desc}</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div>
                <label className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block mb-1.5">
                  Social Media Presets
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { id: 'social_landscape', label: 'X & LinkedIn Feed', desc: '2400×1350 (Landscape 16:9)', icon: <Share2 size={12} /> },
                    { id: '1:1', label: 'Instagram & Square', desc: '2160×2160 (Feed 1:1)', icon: <Monitor size={12} /> },
                    { id: '9:16', label: 'Instagram Story', desc: '2160×3840 (Vertical 9:16)', icon: <Smartphone size={12} /> },
                    { id: 'social_banner', label: 'LinkedIn Article Banner', desc: '2400×1256 (Banner 1.91:1)', icon: <Globe size={12} /> },
                  ].map((ar) => (
                    <button
                      key={ar.id}
                      onClick={() => setAspectRatio(ar.id as AspectRatio)}
                      className={`p-2.5 rounded-xl border text-left transition-all ${
                        aspectRatio === ar.id
                          ? 'border-indigo-600 bg-indigo-50/60 shadow-xs'
                          : 'border-slate-200 hover:border-slate-300 bg-white'
                      }`}
                    >
                      <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                        {ar.icon} {ar.label}
                      </span>
                      <span className="text-[10px] text-slate-500 block mt-0.5">{ar.desc}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Cartographic Theme */}
            <div>
              <label className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block mb-1.5">
                Cartographic Theme
              </label>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { id: 'editorial', label: 'Classic Ivory Editorial', desc: 'Warm archival newsprint' },
                  { id: 'dark', label: 'Midnight Slate', desc: 'High-contrast luminescent dark' },
                  { id: 'minimal', label: 'Clean Academic', desc: 'Crisp minimal white' },
                  { id: 'blueprint', label: 'Archival Blueprint', desc: 'Technical cyan & navy' },
                ].map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setTheme(t.id as MapTheme)}
                    className={`p-2.5 rounded-xl border text-left transition-all ${
                      theme === t.id
                        ? 'border-indigo-600 bg-indigo-50/60 shadow-xs'
                        : 'border-slate-200 hover:border-slate-300 bg-white'
                    }`}
                  >
                    <span className="text-xs font-bold text-slate-800 block">{t.label}</span>
                    <span className="text-[10px] text-slate-500 block mt-0.5">{t.desc}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Title Customization */}
            <div>
              <label className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block mb-1">
                Master Headline (Executive Serif)
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500 font-serif font-bold text-slate-900"
                placeholder="Title..."
              />
            </div>

            {/* Subtitle Customization */}
            <div>
              <label className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block mb-1">
                Editorial Subtitle
              </label>
              <textarea
                rows={2}
                value={subtitle}
                onChange={(e) => setSubtitle(e.target.value)}
                className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500 leading-relaxed text-slate-700"
                placeholder="Description of mapped data..."
              />
            </div>

            {/* Features Included Callout */}
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/80 space-y-1 text-xs text-slate-600">
              <span className="font-bold text-slate-700 block mb-1">Included GIS Elements:</span>
              <div className="flex items-center gap-1.5 text-[11px]">
                <Check size={13} className="text-emerald-600 shrink-0" />
                <span>Executive Serif Title &amp; Archival Neatline Framing</span>
              </div>
              <div className="flex items-center gap-1.5 text-[11px]">
                <Check size={13} className="text-emerald-600 shrink-0" />
                <span>Proportional Funding Bubble Scale Legend</span>
              </div>
              <div className="flex items-center gap-1.5 text-[11px]">
                <Check size={13} className="text-emerald-600 shrink-0" />
                <span>U.S. Energy Innovation Database by Brandon N. Owens</span>
              </div>
            </div>
          </div>

          {/* Right: Live Preview */}
          <div className="lg:col-span-7 flex flex-col">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                <Eye size={13} className="text-indigo-600" />
                <span>Live Rendering Preview ({getDimensions().width}×{getDimensions().height}px)</span>
              </span>
              <button
                onClick={generateCanvasPreview}
                className="text-xs text-indigo-600 hover:text-indigo-800 font-semibold flex items-center gap-1 cursor-pointer"
              >
                Refresh Preview
              </button>
            </div>

            <div className="flex-1 bg-slate-100 rounded-2xl border border-slate-200 p-4 flex items-center justify-center min-h-[400px] max-h-[560px] overflow-hidden shadow-inner">
              {isGenerating ? (
                <div className="flex flex-col items-center gap-2 text-slate-400">
                  <Loader2 className="animate-spin text-indigo-600" size={36} />
                  <span className="text-xs font-semibold">Composing cartographic artwork...</span>
                </div>
              ) : previewUrl ? (
                <img
                  src={previewUrl}
                  alt="Executive Map Wall Art Preview"
                  className="max-h-[500px] max-w-full object-contain rounded-lg shadow-xl border border-slate-300 transition-all"
                />
              ) : (
                <div className="text-xs text-slate-400">Preview not available</div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between">
          <span className="text-xs text-slate-500 flex items-center gap-2">
            <span>Resolution: <strong>{getDimensions().width}×{getDimensions().height}px (300 DPI Print Quality)</strong></span>
            <span>·</span>
            <span>Source: <em>U.S. Energy Innovation Database by Brandon N. Owens</em></span>
          </span>
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded-xl shadow-xs hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleDownload}
              className="px-5 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-md transition-all flex items-center gap-2 cursor-pointer"
            >
              <Download size={14} /> Download High-Res PNG ({getDimensions().width}px)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
