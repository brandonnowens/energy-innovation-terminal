import React, { useState, useEffect, useMemo, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Minimize2, Maximize2, X, Eye, EyeOff,
  Sparkles, ExternalLink, ArrowRight, Zap, Radio, Pause, Play,
  ChevronLeft, ChevronRight, FileSearch, Building2, Lightbulb,
  Scale, Trophy, Layers, Clock, Calendar, Database, History,
  Filter, Search, ArrowUpRight
} from 'lucide-react';
import { fetchNewsTicker, fetchNewsDetail, NewsTickerItem, NewsItemDetail, NewsItemLink } from '../api/client';

export function FloatingNewsTicker() {
  const navigate = useNavigate();

  // Collapsed bottom strip state
  const [isCollapsed, setIsCollapsed] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem('energy_ticker_collapsed_v2');
      return saved ? JSON.parse(saved) : false;
    } catch {
      return false;
    }
  });

  // Hidden state (completely dismissed until un-hidden)
  const [isHidden, setIsHidden] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem('energy_ticker_hidden_v2');
      return saved ? JSON.parse(saved) : false;
    } catch {
      return false;
    }
  });

  // Ticker animation pause state
  const [isPaused, setIsPaused] = useState(false);

  // Speed state: 'normal' (35s) | 'slow' (55s) | 'fast' (20s)
  const [tickerSpeed, setTickerSpeed] = useState<'normal' | 'slow' | 'fast'>('normal');

  // Active selected news item for the Intelligence Dossier Modal
  const [selectedNewsId, setSelectedNewsId] = useState<number | null>(null);

  // Slide-up Daily Archive running ledger drawer state
  const [showArchiveDrawer, setShowArchiveDrawer] = useState(false);
  const [archiveSearch, setArchiveSearch] = useState('');
  const [archiveCategoryFilter, setArchiveCategoryFilter] = useState<string>('all');

  // Selected news detail query
  const { data: newsDetail, isLoading: isLoadingDetail } = useQuery<NewsItemDetail>({
    queryKey: ['news-detail', selectedNewsId],
    queryFn: () => fetchNewsDetail(selectedNewsId!),
    enabled: selectedNewsId !== null,
    staleTime: 5 * 60 * 1000,
  });

  // Query live news ticker feed
  const { data: tickerData, isLoading } = useQuery({
    queryKey: ['energy-news-ticker'],
    queryFn: () => fetchNewsTicker(35),
    staleTime: 60 * 1000,
    refetchInterval: 3 * 60 * 1000, // Background refresh every 3 minutes
  });

  const newsItems = useMemo(() => tickerData?.items || [], [tickerData]);

  // Group news items by Date for the running archive
  const newsByDate = useMemo(() => {
    const groups: Record<string, NewsTickerItem[]> = {};
    newsItems.forEach(item => {
      const dateStr = item.published_at
        ? new Date(item.published_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
        : 'Recent Ingestion';
      if (!groups[dateStr]) groups[dateStr] = [];
      groups[dateStr].push(item);
    });
    return groups;
  }, [newsItems]);

  // Filtered archive list
  const filteredArchiveItems = useMemo(() => {
    return newsItems.filter(item => {
      const matchCat = archiveCategoryFilter === 'all' || item.category_tag.toLowerCase().includes(archiveCategoryFilter.toLowerCase());
      const matchSearch = !archiveSearch.trim() ||
        item.title.toLowerCase().includes(archiveSearch.toLowerCase()) ||
        item.summary.toLowerCase().includes(archiveSearch.toLowerCase()) ||
        item.source_name.toLowerCase().includes(archiveSearch.toLowerCase());
      return matchCat && matchSearch;
    });
  }, [newsItems, archiveCategoryFilter, archiveSearch]);

  // Save collapsed state
  useEffect(() => {
    try {
      localStorage.setItem('energy_ticker_collapsed_v2', JSON.stringify(isCollapsed));
    } catch {}
  }, [isCollapsed]);

  // Save hidden state
  useEffect(() => {
    try {
      localStorage.setItem('energy_ticker_hidden_v2', JSON.stringify(isHidden));
    } catch {}
  }, [isHidden]);

  const getSentimentBadge = (sentiment: string) => {
    switch (sentiment) {
      case 'breakthrough':
        return { label: 'BREAKTHROUGH', color: 'bg-emerald-500/20 text-[#00F5A0] border-emerald-500/40' };
      case 'grant_awarded':
        return { label: 'GRANT AWARD', color: 'bg-cyan-500/20 text-[#00E5FF] border-cyan-500/40' };
      case 'funding_round':
        return { label: 'CAPITAL ROUND', color: 'bg-purple-500/20 text-purple-300 border-purple-500/40' };
      case 'commercial':
        return { label: 'COMMERCIAL', color: 'bg-blue-500/20 text-blue-300 border-blue-500/40' };
      case 'regulatory':
        return { label: 'REGULATORY', color: 'bg-amber-500/20 text-amber-300 border-amber-500/40' };
      case 'milestone':
        return { label: 'MILESTONE', color: 'bg-teal-500/20 text-teal-300 border-teal-500/40' };
      default:
        return { label: 'WIRE REPORT', color: 'bg-slate-500/20 text-slate-300 border-slate-500/40' };
    }
  };

  const getElementTypeIcon = (elemType: string) => {
    switch (elemType) {
      case 'opportunity':
        return <FileSearch size={12} className="text-cyan-400 shrink-0" />;
      case 'organization':
        return <Building2 size={12} className="text-indigo-400 shrink-0" />;
      case 'technology':
        return <Lightbulb size={12} className="text-amber-400 shrink-0" />;
      case 'policy':
      case 'proceeding':
        return <Scale size={12} className="text-purple-400 shrink-0" />;
      case 'award':
        return <Trophy size={12} className="text-emerald-400 shrink-0" />;
      case 'program':
        return <Layers size={12} className="text-teal-400 shrink-0" />;
      default:
        return <Layers size={12} className="text-slate-400 shrink-0" />;
    }
  };

  // Formatted date string
  const formatItemDate = (dateStr?: string) => {
    if (!dateStr) return 'Today';
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } catch {
      return 'Today';
    }
  };

  // Duplicate items for continuous infinite marquee looping
  const marqueeItems = useMemo(() => {
    if (newsItems.length === 0) return [];
    return [...newsItems, ...newsItems];
  }, [newsItems]);

  // Calculate smooth reading speed (approx 30px/sec)
  const animationDuration = useMemo(() => {
    const itemCount = newsItems.length || 20;
    const baseDuration = Math.max(160, itemCount * 8.5);
    if (tickerSpeed === 'slow') return `${Math.round(baseDuration * 1.6)}s`;
    if (tickerSpeed === 'fast') return `${Math.round(baseDuration * 0.6)}s`;
    return `${baseDuration}s`;
  }, [newsItems.length, tickerSpeed]);

  // If hidden, show floating unhide trigger pill in bottom-left
  if (isHidden) {
    return (
      <button
        type="button"
        onClick={() => setIsHidden(false)}
        title="Restore Energy Innovation Wire"
        className="fixed bottom-4 left-4 z-40 flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#070a12]/92 hover:bg-[#0f172a] backdrop-blur-md border border-cyan-500/40 text-white shadow-xl hover:shadow-cyan-500/20 transition-all cursor-pointer group animate-in fade-in"
      >
        <Radio size={12} className="text-[#00F5A0] animate-pulse" />
        <span className="text-[11px] font-mono font-bold text-slate-200 group-hover:text-cyan-300">
          Energy Innovation Wire ({newsItems.length})
        </span>
        <Eye size={12} className="text-slate-400 group-hover:text-white" />
      </button>
    );
  }

  return (
    <>
      <style>{`
        @keyframes ticker-scroll {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        .animate-ticker-marquee {
          display: flex;
          width: max-content;
          animation: ticker-scroll ${animationDuration} linear infinite;
        }
        .ticker-paused {
          animation-play-state: paused !important;
        }
      `}</style>

      {/* ── 1. FULL-WIDTH BOTTOM ENERGY INNOVATION WIRE TICKER BAR ── */}
      <div className="fixed bottom-0 left-0 right-0 z-40 w-full select-none">
        
        {isCollapsed ? (
          /* Collapsed Bottom Strip */
          <div className="h-8 bg-[#070a12]/95 backdrop-blur-md border-t border-cyan-500/30 px-4 flex items-center justify-between text-slate-300 shadow-2xl">
            <div className="flex items-center gap-2.5">
              <span className="relative flex h-2 w-2 shrink-0">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00F5A0] opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-[#00F5A0]" />
              </span>
              <span className="text-[11px] font-mono font-bold text-white tracking-wider">
                Energy Innovation Wire: <span className="text-[#00F5A0]">{newsItems.length} Stories</span>
              </span>
              <span className="hidden sm:inline-block text-[10px] font-mono text-slate-400">
                · Sovereign Energy Innovation Ledger
              </span>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setShowArchiveDrawer(true)}
                className="flex items-center gap-1 px-2 py-0.5 rounded bg-white/[0.06] hover:bg-white/[0.12] text-[10px] font-mono text-cyan-300 transition-all cursor-pointer"
              >
                <History size={11} />
                <span>Daily Archive</span>
              </button>
              <button
                type="button"
                onClick={() => setIsCollapsed(false)}
                title="Expand Full-Width Energy Innovation Wire"
                className="p-1 rounded bg-white/[0.08] hover:bg-white/[0.15] text-slate-300 hover:text-white transition-all cursor-pointer"
              >
                <Maximize2 size={11} />
              </button>
            </div>
          </div>
        ) : (
          /* Full Expanded Bottom Energy Innovation Wire Ticker */
          <div
            className="bg-[#070a12]/98 backdrop-blur-xl border-t border-cyan-500/40 text-slate-200 shadow-[0_-8px_30px_rgba(0,0,0,0.7)] relative overflow-hidden"
            onMouseEnter={() => setIsPaused(true)}
            onMouseLeave={() => setIsPaused(false)}
          >
            {/* Ambient Top Glow Line */}
            <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-[#00F5A0] via-[#00E5FF] to-transparent pointer-events-none" />

            <div className="h-11 flex items-center justify-between">
              
              {/* Left Pinned Anchor: Live Brand & Date Indicator */}
              <div className="h-full px-3.5 bg-[#0b101b] border-r border-white/[0.1] flex items-center gap-2.5 shrink-0 z-10 shadow-lg">
                <div className="flex items-center gap-1.5">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00F5A0] opacity-75" />
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-[#00F5A0]" />
                  </span>
                  <span className="text-[10.5px] font-extrabold uppercase tracking-wider text-white font-mono">
                    Energy Innovation Wire
                  </span>
                </div>

                <span className="hidden sm:inline-flex items-center gap-1 text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                  <Calendar size={10} />
                  <span>Sep 2, 2026</span>
                </span>
              </div>

              {/* Center Continuous Infinite Marquee Scroller */}
              <div className="flex-1 overflow-hidden relative flex items-center h-full">
                {isLoading ? (
                  <div className="px-6 flex items-center gap-2 text-[11px] font-mono text-slate-400">
                    <Zap size={13} className="animate-spin text-cyan-400" />
                    <span>Loading daily energy innovation news stream...</span>
                  </div>
                ) : (
                  <div className={`animate-ticker-marquee ${isPaused ? 'ticker-paused' : ''}`}>
                    {marqueeItems.map((item, idx) => {
                      const badge = getSentimentBadge(item.sentiment);
                      const hasSpecificLink = Boolean(item.primary_link && item.total_links_count > 0);

                      return (
                        <div
                          key={`${item.id}-${idx}`}
                          onClick={() => {
                            if (hasSpecificLink) setSelectedNewsId(item.id);
                          }}
                          className={`inline-flex items-center gap-2.5 px-4 h-11 border-r border-white/[0.08] transition-colors ${
                            hasSpecificLink
                              ? 'cursor-pointer hover:bg-white/[0.06] group/item'
                              : 'cursor-default'
                          }`}
                        >
                          {/* Date Stamp */}
                          <span className="text-[9.5px] font-mono font-bold text-slate-400 shrink-0 bg-white/[0.06] px-1.5 py-0.5 rounded border border-white/[0.06]">
                            {formatItemDate(item.published_at)}
                          </span>

                          {/* Sentiment Badge */}
                          <span className={`text-[8.5px] font-mono font-black uppercase px-1.5 py-0.5 rounded border tracking-wider shrink-0 ${badge.color}`}>
                            {badge.label}
                          </span>

                          {/* Source Tag */}
                          <span className="text-[10px] font-mono text-cyan-300/90 font-bold shrink-0">
                            {item.source_name}:
                          </span>

                          {/* Title */}
                          <span className="text-[11.5px] font-bold text-slate-100 group-hover/item:text-cyan-300 transition-colors whitespace-nowrap tracking-tight">
                            {item.title}
                          </span>

                          {/* Specific Database Linkage Pill (if matched) */}
                          {hasSpecificLink && item.primary_link && (
                            <div className="inline-flex items-center gap-1 text-[9.5px] font-mono font-bold px-2 py-0.5 rounded-full bg-cyan-950/70 text-cyan-300 border border-cyan-500/35 shrink-0">
                              {getElementTypeIcon(item.primary_link.element_type)}
                              <span className="truncate max-w-[170px]">{item.primary_link.element_title}</span>
                              <span className="text-[8.5px] text-[#00F5A0] font-bold pl-0.5">· Inspect →</span>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Right Pinned Controls: Pause/Play, Speed, Daily Archive, Minimize, Dismiss */}
              <div className="h-full px-3 bg-[#0b101b] border-l border-white/[0.1] flex items-center gap-1.5 shrink-0 z-10 shadow-lg">
                {/* Pause/Play Toggle */}
                <button
                  type="button"
                  onClick={() => setIsPaused(prev => !prev)}
                  title={isPaused ? "Resume continuous ticker scrolling" : "Pause ticker scrolling"}
                  className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-white/10 transition-all cursor-pointer"
                >
                  {isPaused ? <Play size={11} className="text-[#00F5A0]" /> : <Pause size={11} />}
                </button>

                {/* Speed Toggle */}
                <button
                  type="button"
                  onClick={() => {
                    setTickerSpeed(prev => prev === 'normal' ? 'fast' : prev === 'fast' ? 'slow' : 'normal');
                  }}
                  title={`Ticker Speed: ${tickerSpeed.toUpperCase()} (Click to toggle)`}
                  className="hidden md:inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-mono text-slate-400 hover:text-cyan-300 hover:bg-white/10 transition-all cursor-pointer"
                >
                  <span>{tickerSpeed === 'fast' ? '2x' : tickerSpeed === 'slow' ? '0.5x' : '1x'}</span>
                </button>

                {/* Daily Running Archive Button */}
                <button
                  type="button"
                  onClick={() => setShowArchiveDrawer(true)}
                  title="Open Cumulative Daily News Archive"
                  className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-cyan-500/15 hover:bg-cyan-500/25 border border-cyan-500/35 text-cyan-300 text-[10px] font-mono font-bold transition-all cursor-pointer"
                >
                  <History size={11} />
                  <span className="hidden sm:inline">Daily Archive</span>
                </button>

                {/* Collapse to Slim Strip */}
                <button
                  type="button"
                  onClick={() => setIsCollapsed(true)}
                  title="Collapse to minimal bottom bar"
                  className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-white/10 transition-all cursor-pointer"
                >
                  <Minimize2 size={11} />
                </button>

                {/* Dismiss / Hide */}
                <button
                  type="button"
                  onClick={() => setIsHidden(true)}
                  title="Hide ticker"
                  className="p-1 rounded-md text-slate-400 hover:text-rose-400 hover:bg-white/10 transition-all cursor-pointer"
                >
                  <X size={11} />
                </button>
              </div>

            </div>
          </div>
        )}
      </div>

      {/* ── 2. CUMULATIVE DAILY ARCHIVE DRAWER (SLIDE-UP RUNNING LIST) ── */}
      {showArchiveDrawer && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/75 backdrop-blur-sm animate-in fade-in duration-150">
          <div
            className="w-full max-w-4xl max-h-[82vh] rounded-t-3xl bg-[#080d16] border-t border-x border-cyan-500/40 shadow-2xl text-slate-200 overflow-hidden flex flex-col relative animate-in slide-in-from-bottom duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Ambient Top Glow Accent */}
            <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-[#00F5A0] via-[#00E5FF] to-transparent pointer-events-none" />

            {/* Archive Drawer Header */}
            <div className="px-6 py-4 border-b border-white/[0.08] bg-white/[0.02] flex items-center justify-between gap-4 shrink-0">
              <div className="flex items-center gap-2.5">
                <span className="p-2 rounded-xl bg-cyan-500/15 border border-cyan-500/30 text-cyan-400">
                  <Database size={16} />
                </span>
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
                      Energy Innovation Daily News Archive &amp; Running Ledger
                    </h2>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/15 text-[#00F5A0] border border-emerald-500/30 font-bold">
                      {newsItems.length} Cumulative Stories
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 font-mono">
                    PostgreSQL Permanent Archive · Ingested Once Daily · Strictly Grounded
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setShowArchiveDrawer(false)}
                className="p-1.5 rounded-xl bg-white/[0.06] hover:bg-white/[0.12] text-slate-400 hover:text-white transition-all cursor-pointer"
              >
                <X size={16} />
              </button>
            </div>

            {/* Filter & Search Toolbar */}
            <div className="px-6 py-3 border-b border-white/[0.08] bg-[#0b101b] flex flex-wrap items-center justify-between gap-3 shrink-0">
              <div className="flex items-center gap-2 flex-1 min-w-[240px]">
                <Search size={13} className="text-slate-400" />
                <input
                  type="text"
                  value={archiveSearch}
                  onChange={(e) => setArchiveSearch(e.target.value)}
                  placeholder="Search daily archive by title, source, or technology..."
                  className="w-full bg-transparent text-xs text-white placeholder:text-slate-500 focus:outline-hidden font-mono"
                />
              </div>

              <div className="flex items-center gap-2">
                <Filter size={12} className="text-slate-400" />
                <select
                  value={archiveCategoryFilter}
                  onChange={(e) => setArchiveCategoryFilter(e.target.value)}
                  className="bg-white/[0.06] border border-white/[0.1] rounded-lg px-2.5 py-1 text-[11px] font-mono text-slate-200 focus:outline-hidden cursor-pointer"
                >
                  <option value="all">All Sectors ({newsItems.length})</option>
                  <option value="storage">Long-Duration Storage</option>
                  <option value="grid">Grid Modernization</option>
                  <option value="hydrogen">Clean Hydrogen</option>
                  <option value="nuclear">Advanced Nuclear / SMR</option>
                  <option value="building">Building Decarbonization</option>
                  <option value="solar">Solar &amp; PV</option>
                  <option value="offshore">Offshore Wind</option>
                  <option value="policy">Policy &amp; Codes</option>
                </select>
              </div>
            </div>

            {/* Archive Chronological List Body */}
            <div className="p-6 space-y-6 overflow-y-auto custom-scrollbar flex-1">
              {filteredArchiveItems.length === 0 ? (
                <div className="py-12 text-center text-slate-400 font-mono text-xs">
                  No news items match the current search filters.
                </div>
              ) : (
                Object.entries(newsByDate).map(([dateHeader, items]) => {
                  const matchingItems = items.filter(i => filteredArchiveItems.some(fa => fa.id === i.id));
                  if (matchingItems.length === 0) return null;

                  return (
                    <div key={dateHeader} className="space-y-3">
                      {/* Date Heading */}
                      <div className="flex items-center gap-2 pb-1 border-b border-white/[0.08]">
                        <Calendar size={13} className="text-[#00E5FF]" />
                        <span className="text-[12px] font-mono font-bold text-white uppercase tracking-wider">
                          {dateHeader}
                        </span>
                        <span className="text-[10px] font-mono text-slate-400">
                          ({matchingItems.length} records ingested)
                        </span>
                      </div>

                      {/* Items Grid */}
                      <div className="grid grid-cols-1 gap-2.5">
                        {matchingItems.map(item => {
                          const badge = getSentimentBadge(item.sentiment);
                          const hasSpecificLink = Boolean(item.primary_link && item.total_links_count > 0);

                          return (
                            <div
                              key={item.id}
                              className="p-3.5 rounded-xl bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.08] hover:border-cyan-500/40 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                            >
                              <div className="space-y-1.5 min-w-0">
                                <div className="flex items-center gap-2 flex-wrap">
                                  <span className={`text-[8.5px] font-mono font-black uppercase px-1.5 py-0.5 rounded border tracking-wider ${badge.color}`}>
                                    {badge.label}
                                  </span>
                                  <span className="text-[10px] font-mono font-bold text-slate-300 bg-white/[0.06] px-1.5 py-0.5 rounded border border-white/[0.06]">
                                    {item.source_name}
                                  </span>
                                  <span className="text-[10px] font-mono text-cyan-400/90 font-semibold">
                                    {item.category_tag}
                                  </span>
                                </div>

                                <h4 className="text-[12.5px] font-bold text-white tracking-tight leading-snug">
                                  {item.title}
                                </h4>

                                <p className="text-[11px] text-slate-300 font-sans leading-relaxed line-clamp-2">
                                  {item.summary}
                                </p>

                                {hasSpecificLink && item.primary_link && (
                                  <div className="pt-0.5 flex items-center gap-1.5 text-[10px] font-mono text-cyan-300">
                                    <span className="text-slate-400">Linked to:</span>
                                    <span className="inline-flex items-center gap-1 font-bold bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-500/30">
                                      {getElementTypeIcon(item.primary_link.element_type)}
                                      <span>{item.primary_link.element_title}</span>
                                    </span>
                                  </div>
                                )}
                              </div>

                              <div className="shrink-0 flex items-center gap-2">
                                <a
                                  href={item.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="p-2 rounded-lg bg-white/[0.06] hover:bg-white/[0.12] text-slate-300 hover:text-white transition-all"
                                  title="Open original source article"
                                >
                                  <ExternalLink size={13} />
                                </a>

                                {hasSpecificLink && (
                                  <button
                                    type="button"
                                    onClick={() => {
                                      setShowArchiveDrawer(false);
                                      setSelectedNewsId(item.id);
                                    }}
                                    className="px-3 py-1.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-500 text-cyan-300 hover:text-slate-950 font-mono text-[11px] font-bold border border-cyan-500/40 transition-all cursor-pointer shadow-xs flex items-center gap-1"
                                  >
                                    <span>Inspect</span>
                                    <ArrowRight size={11} />
                                  </button>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── 3. SPECIFIC ENTITY INSPECT INTELLIGENCE DOSSIER MODAL ── */}
      {selectedNewsId !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-150">
          <div
            className="w-full max-w-2xl rounded-2xl bg-[#0b101b] border border-white/[0.18] shadow-2xl text-slate-200 overflow-hidden flex flex-col max-h-[90vh] relative"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Ambient Modal Top Glow */}
            <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-[#00F5A0] via-[#00E5FF] to-transparent pointer-events-none" />

            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-white/[0.08] bg-white/[0.03] flex items-center justify-between gap-3 shrink-0">
              <div className="flex items-center gap-2.5 min-w-0">
                <span className="p-1.5 rounded-lg bg-cyan-500/15 border border-cyan-500/30 text-cyan-400">
                  <Radio size={14} className="animate-pulse" />
                </span>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono uppercase font-extrabold tracking-wider text-[#00F5A0]">
                      Energy Innovation Wire · Intelligence Dossier
                    </span>
                    {newsDetail && (
                      <span className="text-[9.5px] font-mono px-2 py-0.2 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30 font-bold">
                        {newsDetail.category_tag}
                      </span>
                    )}
                  </div>
                  <div className="text-[11px] text-slate-400 font-mono">
                    PostgreSQL Sovereign Ledger · Explicit Entity Linkages
                  </div>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setSelectedNewsId(null)}
                className="p-1.5 rounded-xl bg-white/[0.06] hover:bg-white/[0.12] text-slate-400 hover:text-white transition-all cursor-pointer"
              >
                <X size={15} />
              </button>
            </div>

            {/* Modal Scrollable Body */}
            <div className="p-6 space-y-5 overflow-y-auto custom-scrollbar flex-1">
              {isLoadingDetail || !newsDetail ? (
                <div className="py-12 flex flex-col items-center justify-center gap-3 text-slate-400 font-mono text-xs">
                  <Zap size={20} className="animate-spin text-cyan-400" />
                  <span>Loading Grounded Database Linkages...</span>
                </div>
              ) : (
                <>
                  {/* Article Title & Source Attribution */}
                  <div className="space-y-2">
                    <div className="flex flex-wrap items-center gap-2 text-[10.5px] font-mono text-slate-400">
                      <span className="font-bold text-white bg-white/[0.08] px-2 py-0.5 rounded">
                        {newsDetail.source_name}
                      </span>
                      <span>·</span>
                      <span className="flex items-center gap-1 text-cyan-300 font-semibold">
                        <Calendar size={11} />
                        <span>{new Date(newsDetail.published_at || '').toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                      </span>
                      {newsDetail.author && (
                        <>
                          <span>·</span>
                          <span>By {newsDetail.author}</span>
                        </>
                      )}
                    </div>

                    <h3 className="text-lg font-bold text-white tracking-tight leading-snug">
                      {newsDetail.title}
                    </h3>

                    {/* External Link */}
                    <div className="pt-1">
                      <a
                        href={newsDetail.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 text-[11.5px] font-mono text-cyan-400 hover:text-cyan-300 font-semibold hover:underline"
                      >
                        <span>Read original article on {newsDetail.source_name}</span>
                        <ExternalLink size={12} />
                      </a>
                    </div>
                  </div>

                  {/* LLM-Generated Executive Briefing Card */}
                  <div className="p-4 rounded-xl bg-gradient-to-br from-cyan-950/40 via-[#0c1424] to-slate-900/80 border border-cyan-500/30 space-y-2 relative overflow-hidden">
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-1.5 text-[11px] font-mono font-bold text-white uppercase tracking-wider">
                        <Sparkles size={13} className="text-[#00F5A0]" />
                        <span>AI Executive Briefing &amp; Impact Analysis</span>
                      </span>
                      <span className="text-[9.5px] font-mono text-[#00F5A0] font-bold px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/25">
                        Synthesized
                      </span>
                    </div>

                    <p className="text-[12.5px] text-slate-200 leading-relaxed font-sans">
                      {newsDetail.summary}
                    </p>
                  </div>

                  {/* Explicit Database Entity Linkages */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between border-b border-white/[0.08] pb-2">
                      <div className="flex items-center gap-2">
                        <Database size={14} className="text-[#00E5FF]" />
                        <span className="text-[12px] font-bold text-white font-mono uppercase tracking-wider">
                          Connected Database Elements ({newsDetail.links.length})
                        </span>
                      </div>
                      <span className="text-[10px] font-mono text-slate-400">
                        Direct Navigation
                      </span>
                    </div>

                    {newsDetail.links.length === 0 ? (
                      <div className="text-[11px] font-mono text-slate-400 py-2">
                        No specific entity linkages cataloged for this entry.
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 gap-2.5">
                        {newsDetail.links.map((link: NewsItemLink, idx: number) => (
                          <div
                            key={link.id || idx}
                            className="p-3.5 rounded-xl bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.08] hover:border-cyan-500/40 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 group/link"
                          >
                            <div className="space-y-1 min-w-0">
                              <div className="flex items-center gap-2 flex-wrap">
                                <span className="inline-flex items-center gap-1 text-[9px] font-mono font-black uppercase px-2 py-0.5 rounded bg-white/[0.08] text-cyan-300 border border-white/[0.1]">
                                  {getElementTypeIcon(link.element_type)}
                                  <span>{link.element_type}</span>
                                </span>
                                <span className="text-[12px] font-bold text-white font-mono group-hover/link:text-cyan-300 transition-colors truncate">
                                  {link.element_title}
                                </span>
                              </div>
                              <p className="text-[11px] text-slate-300 leading-snug">
                                {link.link_rationale}
                              </p>
                            </div>

                            <button
                              type="button"
                              onClick={() => {
                                setSelectedNewsId(null);
                                navigate(link.element_url_path);
                              }}
                              className="shrink-0 flex items-center justify-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-500 text-cyan-300 hover:text-slate-950 font-mono text-[11px] font-bold border border-cyan-500/40 transition-all cursor-pointer shadow-xs"
                            >
                              <span>Open {link.element_type}</span>
                              <ArrowRight size={11} />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Provenance & Deduplication Footer Note */}
                  <div className="pt-2 border-t border-white/[0.08] flex items-center justify-between text-[9.5px] font-mono text-slate-400">
                    <span className="flex items-center gap-1">
                      <Calendar size={11} className="text-[#00F5A0]" />
                      <span>Ingested: {new Date(newsDetail.published_at || '').toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                    </span>
                    <span className="text-slate-400">
                      PostgreSQL DB Record #{newsDetail.id}
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
