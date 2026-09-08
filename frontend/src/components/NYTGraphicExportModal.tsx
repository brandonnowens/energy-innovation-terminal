import React, { useState, useEffect, useRef } from 'react';
import {
  Download, X, Sparkles, Eye, Check, Sliders, Loader2, Image as ImageIcon,
  Share2, Printer, Smartphone, Monitor, Globe, FileText
} from 'lucide-react';
import { saveAs } from 'file-saver';
import html2canvas from 'html2canvas';

export type NYTPresetCategory = 'publication' | 'social';

export type NYTAspectRatio =
  | '16:9'      // 4K Ultra-HD Wall Art / Landscape
  | '4:3'       // Exhibition Poster
  | '3:2'       // Classic Publication Format
  | '1:1'       // Square Post (Instagram / LinkedIn)
  | '9:16'      // Vertical Story (Instagram / Mobile Feed)
  | 'social_landscape' // X / Twitter & LinkedIn Feed (1200x675 / 2400x1350)
  | 'social_banner';   // OpenGraph / Article Banner (1200x628 / 2400x1256)

export type NYTTheme = 'editorial' | 'dark' | 'minimal' | 'blueprint';

export interface NYTLegendItem {
  label: string;
  color: string;
  count?: number | string;
}

export interface NYTStatItem {
  label: string;
  val: string;
}

interface NYTGraphicExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultTitle: string;
  defaultSubtitle?: string;
  eyebrow?: string;
  getContentCanvas?: () => HTMLCanvasElement | null;
  targetElementId?: string;
  stats?: NYTStatItem[];
  legendItems?: NYTLegendItem[];
  legendTitle?: string;
  sourceAttribution?: string;
  filenamePrefix?: string;
}

export const NYTGraphicExportModal: React.FC<NYTGraphicExportModalProps> = ({
  isOpen,
  onClose,
  defaultTitle,
  defaultSubtitle = '',
  eyebrow = 'ENERGY INNOVATION TERMINAL · DECISION SUPPORT',
  getContentCanvas,
  targetElementId,
  stats = [],
  legendItems = [],
  legendTitle = 'LEGEND & KEY',
  sourceAttribution = 'U.S. Energy Innovation Database by Brandon N. Owens',
  filenamePrefix = 'energy-innovation-terminal-export',
}) => {
  const [aspectRatio, setAspectRatio] = useState<NYTAspectRatio>('16:9');
  const [presetCategory, setPresetCategory] = useState<NYTPresetCategory>('publication');
  const [theme, setTheme] = useState<NYTTheme>('editorial');
  const [title, setTitle] = useState(defaultTitle);
  const [subtitle, setSubtitle] = useState(defaultSubtitle);
  const [isGenerating, setIsGenerating] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  useEffect(() => {
    setTitle(defaultTitle);
  }, [defaultTitle]);

  useEffect(() => {
    if (defaultSubtitle) setSubtitle(defaultSubtitle);
  }, [defaultSubtitle]);

  // Re-generate canvas preview when settings change
  useEffect(() => {
    if (!isOpen) return;
    generateCanvasPreview();
  }, [isOpen, aspectRatio, theme, title, subtitle]);

  const captureSourceContent = async (): Promise<HTMLCanvasElement | null> => {
    if (getContentCanvas) {
      const c = getContentCanvas();
      if (c) return c;
    }

    if (targetElementId) {
      const el = document.getElementById(targetElementId);
      if (el) {
        return await html2canvas(el, {
          backgroundColor: null,
          scale: 3.5, // 3.5x supersampling for razor sharp vectors and charts
          useCORS: true,
          logging: false,
          imageTimeout: 0,
        });
      }
    }

    return null;
  };

  const getDimensions = (): { width: number; height: number; scale: number; isVertical: boolean; isSquare: boolean } => {
    switch (aspectRatio) {
      case '16:9':
        return { width: 3840, height: 2160, scale: 1.0, isVertical: false, isSquare: false }; // 4K Master Ultra-HD
      case '4:3':
        return { width: 3200, height: 2400, scale: 1.0, isVertical: false, isSquare: false }; // Exhibition Poster
      case '3:2':
        return { width: 3600, height: 2400, scale: 1.0, isVertical: false, isSquare: false }; // Classic Broadside
      case '1:1':
        return { width: 2400, height: 2400, scale: 1.0, isVertical: false, isSquare: true };  // Square Gallery Post
      case '9:16':
        return { width: 2160, height: 3840, scale: 1.0, isVertical: true, isSquare: false };  // Instagram Story / Mobile 4K
      case 'social_landscape':
        return { width: 2400, height: 1350, scale: 1.0, isVertical: false, isSquare: false }; // X (Twitter) / LinkedIn Feed
      case 'social_banner':
        return { width: 2400, height: 1256, scale: 1.0, isVertical: false, isSquare: false }; // LinkedIn Article / OpenGraph
      default:
        return { width: 3840, height: 2160, scale: 1.0, isVertical: false, isSquare: false };
    }
  };

  const renderCompositeCanvas = async (): Promise<HTMLCanvasElement | null> => {
    const sourceCanvas = await captureSourceContent();
    if (!sourceCanvas) return null;

    const { width, height, isVertical, isSquare } = getDimensions();

    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;

    // Enable highest quality image smoothing
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';

    const themeColors = {
      editorial: {
        bg: '#FDFBF7',
        border: '#1A202C',
        textPrimary: '#111827',
        textSecondary: '#4B5563',
        textMuted: '#6B7280',
        cardBg: 'rgba(255, 255, 255, 0.95)',
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
        cardBg: 'rgba(15, 23, 42, 0.92)',
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
        cardBg: 'rgba(12, 34, 64, 0.90)',
        cardBorder: '#0284C7',
        accent: '#38BDF8',
        gold: '#FBBF24',
        divider: '#0369A1',
      },
    }[theme];

    // 1. Solid Canvas Background
    ctx.fillStyle = themeColors.bg;
    ctx.fillRect(0, 0, width, height);

    // 2. Outer Neatline & Archival Double Framing
    const margin = Math.round(width * 0.022); // dynamic margin scaling
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

    // Corner crosshairs / tick marks for editorial precision
    const tickLen = Math.round(margin * 0.45);
    ctx.lineWidth = Math.max(1.5, Math.round(width * 0.0007));
    ctx.beginPath();
    // Top-left
    ctx.moveTo(margin - tickLen, margin); ctx.lineTo(margin + tickLen, margin);
    ctx.moveTo(margin, margin - tickLen); ctx.lineTo(margin, margin + tickLen);
    // Top-right
    ctx.moveTo(width - margin - tickLen, margin); ctx.lineTo(width - margin + tickLen, margin);
    ctx.moveTo(width - margin, margin - tickLen); ctx.lineTo(width - margin, margin + tickLen);
    // Bottom-left
    ctx.moveTo(margin - tickLen, height - margin); ctx.lineTo(margin + tickLen, height - margin);
    ctx.moveTo(margin, height - margin - tickLen); ctx.lineTo(margin, height - margin + tickLen);
    // Bottom-right
    ctx.moveTo(width - margin - tickLen, height - margin); ctx.lineTo(width - margin + tickLen, height - margin);
    ctx.moveTo(width - margin, height - margin - tickLen); ctx.lineTo(width - margin, height - margin + tickLen);
    ctx.stroke();

    // 3. Header Block (Top Editorial Section)
    const headerTop = margin + Math.round(margin * 0.7);
    const contentLeft = margin + Math.round(margin * 0.9);
    const contentRight = width - margin - Math.round(margin * 0.9);
    const availableHeaderWidth = contentRight - contentLeft;

    // Eyebrow label
    const eyebrowSize = Math.max(14, Math.round(width * 0.007));
    ctx.font = `700 ${eyebrowSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
    ctx.fillStyle = themeColors.gold;
    ctx.fillText(eyebrow.toUpperCase(), contentLeft, headerTop + eyebrowSize);

    // Main Master Headline (Executive Serif Style)
    const titleSize = isVertical
      ? Math.max(38, Math.round(width * 0.032))
      : isSquare
      ? Math.max(40, Math.round(width * 0.024))
      : Math.max(44, Math.round(width * 0.021));
    ctx.font = `bold ${titleSize}px Georgia, "Playfair Display", "Times New Roman", serif`;
    ctx.fillStyle = themeColors.textPrimary;
    
    // Auto-wrap title if necessary
    const titleY = headerTop + eyebrowSize + Math.round(titleSize * 1.25);
    ctx.fillText(title, contentLeft, titleY);

    // Subtitle
    const subtitleSize = isVertical
      ? Math.max(18, Math.round(width * 0.015))
      : Math.max(18, Math.round(width * 0.010));
    ctx.font = `400 ${subtitleSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
    ctx.fillStyle = themeColors.textSecondary;
    const subText = subtitle || `Visual analytics and data intelligence citing Energy Innovation Terminal.`;
    const subtitleY = titleY + Math.round(subtitleSize * 1.7);
    ctx.fillText(subText, contentLeft, subtitleY);

    // Date & Archival Badge in Header Right (if wide enough)
    if (!isVertical) {
      const today = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
      const metaSize = Math.max(13, Math.round(width * 0.0065));
      ctx.font = `500 ${metaSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
      ctx.fillStyle = themeColors.textMuted;
      ctx.textAlign = 'right';
      ctx.fillText(`Edition: ${today}`, contentRight, headerTop + metaSize);
      ctx.fillText('Energy Innovation Terminal Official Archive', contentRight, headerTop + metaSize * 2.4);
      ctx.textAlign = 'left';
    }

    // Header Divider Line
    const headerDividerY = subtitleY + Math.round(margin * 0.6);
    ctx.strokeStyle = themeColors.divider;
    ctx.lineWidth = Math.max(1, Math.round(width * 0.0006));
    ctx.beginPath();
    ctx.moveTo(contentLeft, headerDividerY);
    ctx.lineTo(contentRight, headerDividerY);
    ctx.stroke();

    // 4. Source Graphic Main Canvas Frame
    const footerHeight = Math.max(40, Math.round(height * 0.035));
    const footerBottom = height - margin - Math.round(margin * 0.4);
    const graphicTop = headerDividerY + Math.round(margin * 0.4);
    const graphicBottom = footerBottom - footerHeight;
    const graphicHeight = graphicBottom - graphicTop;
    const graphicWidth = contentRight - contentLeft;

    // Draw source graphic into frame with high-fidelity scaling
    ctx.save();
    ctx.beginPath();
    ctx.roundRect(contentLeft, graphicTop, graphicWidth, graphicHeight, Math.round(width * 0.003));
    ctx.clip();

    ctx.fillStyle = themeColors.cardBg;
    ctx.fillRect(contentLeft, graphicTop, graphicWidth, graphicHeight);

    const hRatio = graphicWidth / sourceCanvas.width;
    const vRatio = graphicHeight / sourceCanvas.height;
    const ratio = Math.min(hRatio, vRatio);
    const centerShiftX = (graphicWidth - sourceCanvas.width * ratio) / 2;
    const centerShiftY = (graphicHeight - sourceCanvas.height * ratio) / 2;

    ctx.drawImage(
      sourceCanvas,
      0, 0, sourceCanvas.width, sourceCanvas.height,
      contentLeft + centerShiftX, graphicTop + centerShiftY,
      sourceCanvas.width * ratio, sourceCanvas.height * ratio
    );
    ctx.restore();

    // Frame border
    ctx.strokeStyle = themeColors.border;
    ctx.lineWidth = Math.max(1.2, Math.round(width * 0.0006));
    ctx.strokeRect(contentLeft, graphicTop, graphicWidth, graphicHeight);

    // 5. Inset Legend Panel (if provided)
    if (legendItems && legendItems.length > 0) {
      const legWidth = Math.min(Math.round(graphicWidth * 0.38), Math.round(width * 0.22));
      const itemRowHeight = Math.max(24, Math.round(height * 0.016));
      const legHeight = Math.min(
        Math.round(graphicHeight * 0.45),
        Math.round(height * 0.04) + Math.min(legendItems.length, 8) * itemRowHeight
      );
      const legX = contentLeft + Math.round(margin * 0.5);
      const legY = graphicTop + graphicHeight - legHeight - Math.round(margin * 0.5);

      ctx.fillStyle = themeColors.cardBg;
      ctx.beginPath();
      ctx.roundRect(legX, legY, legWidth, legHeight, 10);
      ctx.fill();
      ctx.strokeStyle = themeColors.cardBorder;
      ctx.lineWidth = Math.max(1, Math.round(width * 0.0005));
      ctx.stroke();

      const legTitleSize = Math.max(12, Math.round(width * 0.006));
      ctx.font = `bold ${legTitleSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
      ctx.fillStyle = themeColors.textPrimary;
      ctx.fillText(legendTitle.toUpperCase(), legX + Math.round(legWidth * 0.06), legY + legTitleSize * 1.8);

      let itemY = legY + legTitleSize * 3.2;
      const legItemFontSize = Math.max(11, Math.round(width * 0.0055));
      const swatchRadius = Math.max(5, Math.round(width * 0.0025));

      legendItems.slice(0, 8).forEach((item) => {
        ctx.fillStyle = item.color;
        ctx.beginPath();
        ctx.arc(legX + Math.round(legWidth * 0.08), itemY - swatchRadius * 0.4, swatchRadius, 0, Math.PI * 2);
        ctx.fill();

        ctx.font = `500 ${legItemFontSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
        ctx.fillStyle = themeColors.textSecondary;
        const maxChars = isVertical ? 18 : 26;
        const labelStr = item.label.length > maxChars ? item.label.slice(0, maxChars) + '…' : item.label;
        ctx.fillText(labelStr, legX + Math.round(legWidth * 0.15), itemY);

        if (item.count !== undefined) {
          ctx.font = `bold ${legItemFontSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
          ctx.fillStyle = themeColors.textMuted;
          ctx.textAlign = 'right';
          ctx.fillText(item.count.toString(), legX + legWidth - Math.round(legWidth * 0.06), itemY);
          ctx.textAlign = 'left';
        }
        itemY += itemRowHeight;
      });
    }

    // 6. Inset Stats Panel (if provided)
    if (stats && stats.length > 0) {
      const statWidth = Math.min(Math.round(graphicWidth * 0.36), Math.round(width * 0.20));
      const statRowHeight = Math.max(28, Math.round(height * 0.018));
      const statHeight = Math.round(height * 0.035) + stats.length * statRowHeight;
      const statX = contentRight - statWidth - Math.round(margin * 0.5);
      const statY = graphicTop + graphicHeight - statHeight - Math.round(margin * 0.5);

      ctx.fillStyle = themeColors.cardBg;
      ctx.beginPath();
      ctx.roundRect(statX, statY, statWidth, statHeight, 10);
      ctx.fill();
      ctx.strokeStyle = themeColors.cardBorder;
      ctx.lineWidth = Math.max(1, Math.round(width * 0.0005));
      ctx.stroke();

      const statTitleSize = Math.max(12, Math.round(width * 0.006));
      ctx.font = `bold ${statTitleSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
      ctx.fillStyle = themeColors.textPrimary;
      ctx.fillText('KEY METRICS & TOTALS', statX + Math.round(statWidth * 0.06), statY + statTitleSize * 1.8);

      let sY = statY + statTitleSize * 3.4;
      const statLabelSize = Math.max(12, Math.round(width * 0.0055));
      const statValSize = Math.max(13, Math.round(width * 0.006));

      stats.forEach((s) => {
        ctx.font = `400 ${statLabelSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
        ctx.fillStyle = themeColors.textSecondary;
        ctx.fillText(s.label, statX + Math.round(statWidth * 0.06), sY);

        ctx.font = `bold ${statValSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
        ctx.fillStyle = themeColors.textPrimary;
        ctx.textAlign = 'right';
        ctx.fillText(s.val, statX + statWidth - Math.round(statWidth * 0.06), sY);
        ctx.textAlign = 'left';

        sY += statRowHeight;
      });
    }

    // 7. Footer Official Source Attribution Block (Prominently displayed)
    const footerY = height - margin + Math.max(4, Math.round(margin * 0.1));
    const footerFontSize = Math.max(12, Math.round(width * 0.006));
    ctx.font = `500 ${footerFontSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
    ctx.fillStyle = themeColors.textMuted;
    ctx.fillText(sourceAttribution, contentLeft, footerY);

    ctx.textAlign = 'right';
    ctx.fillText('Energy Innovation Terminal · Sovereign Publication Edition (Cleared for Board & C-Suite Briefings)', contentRight, footerY);
    ctx.textAlign = 'left';

    return canvas;
  };

  const generateCanvasPreview = async () => {
    setIsGenerating(true);
    try {
      const c = await renderCompositeCanvas();
      if (c) {
        setPreviewUrl(c.toDataURL('image/png'));
      }
    } catch (e) {
      console.error('Error rendering graphic preview:', e);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = async () => {
    const c = await renderCompositeCanvas();
    if (!c) return;

    c.toBlob((blob) => {
      if (blob) {
        const ts = new Date().toISOString().slice(0, 10);
        const presetTag = aspectRatio.replace(':', 'x');
        saveAs(blob, `${filenamePrefix}-${presetTag}-${ts}.png`);
      }
    }, 'image/png');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-md">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-6xl w-full max-h-[92vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/80">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-700 text-white shadow-md">
              <Sparkles size={18} />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <span>Executive Publication &amp; Social Graphic Studio</span>
                <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold border border-emerald-200">
                  4K / 300 DPI Ultra-HD
                </span>
              </h2>
              <p className="text-xs text-slate-500">
                Export museum-grade and social-ready infographics citing <strong>U.S. Energy Innovation Database by Brandon N. Owens</strong>.
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
            {/* Preset Mode Tabs */}
            <div>
              <label className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block mb-2">
                Export Category &amp; Target Channel
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

            {/* Aspect Ratio / Format Presets */}
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
                      onClick={() => setAspectRatio(ar.id as NYTAspectRatio)}
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
                  Social Platform Presets
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
                      onClick={() => setAspectRatio(ar.id as NYTAspectRatio)}
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
                Editorial Cartographic Theme
              </label>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { id: 'editorial', label: 'Classic Ivory Editorial', desc: 'Warm archival newsprint' },
                  { id: 'dark', label: 'Midnight Slate', desc: 'High-contrast luminescent dark' },
                  { id: 'minimal', label: 'Clean Academic', desc: 'Crisp minimal white paper' },
                  { id: 'blueprint', label: 'Archival Blueprint', desc: 'Technical cyan & navy' },
                ].map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setTheme(t.id as NYTTheme)}
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

            {/* Headline */}
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

            {/* Subtitle */}
            <div>
              <label className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block mb-1">
                Editorial Subtitle
              </label>
              <textarea
                rows={2}
                value={subtitle}
                onChange={(e) => setSubtitle(e.target.value)}
                className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500 leading-relaxed text-slate-700"
                placeholder="Explanation of visual analytics..."
              />
            </div>

            {/* Included Quality Highlights */}
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/80 space-y-1 text-xs text-slate-600">
              <span className="font-bold text-slate-700 block mb-1">Included Editorial Specifications:</span>
              <div className="flex items-center gap-1.5 text-[11px]">
                <Check size={13} className="text-emerald-600 shrink-0" />
                <span>Executive Serif Headline, Eyebrow &amp; Archival Neatline Framing</span>
              </div>
              <div className="flex items-center gap-1.5 text-[11px]">
                <Check size={13} className="text-emerald-600 shrink-0" />
                <span>Executive Metric Stats &amp; Proportional Legend Inset</span>
              </div>
              <div className="flex items-center gap-1.5 text-[11px]">
                <Check size={13} className="text-emerald-600 shrink-0" />
                <span>U.S. Energy Innovation Database by Brandon N. Owens</span>
              </div>
            </div>
          </div>

          {/* Right: Live Interactive High-Res Preview */}
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
                  <span className="text-xs font-semibold">Composing 4K publication artwork...</span>
                </div>
              ) : previewUrl ? (
                <img
                  src={previewUrl}
                  alt="Executive Graphic Preview"
                  className="max-h-[500px] max-w-full object-contain rounded-lg shadow-xl border border-slate-300 transition-all"
                />
              ) : (
                <div className="text-xs text-slate-400">Click Refresh to generate preview</div>
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
