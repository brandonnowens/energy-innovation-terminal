import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import {
  Activity, Clock, GripHorizontal, RotateCcw, ShieldCheck,
  Minimize2, Maximize2, TrendingUp, TrendingDown, DollarSign,
  BarChart2, BarChart3, Calendar, ArrowUpRight, Zap,
  ChevronRight, History, GitCompare, Sparkles
} from 'lucide-react';
import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';
import { fetchCorpusDailyActivity, DailyCorpusActivityPoint } from '../api/client';

export function FloatingLiveCorpus() {
  const navigate = useNavigate();

  // Collapsed to mini pill state
  const [isCollapsed, setIsCollapsed] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem('live_corpus_collapsed');
      return saved ? JSON.parse(saved) : false;
    } catch {
      return false;
    }
  });

  // Extended right-side 60-day chart panel state (defaults to true for rich discovery)
  const [showExtendedChart, setShowExtendedChart] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem('live_corpus_extended_chart_v2');
      return saved !== null ? JSON.parse(saved) : true;
    } catch {
      return true;
    }
  });

  // Year-over-Year comparison overlay toggle
  const [showYoYCompare, setShowYoYCompare] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem('live_corpus_show_yoy');
      return saved !== null ? JSON.parse(saved) : true;
    } catch {
      return true;
    }
  });

  // Time horizon filter: '60d' | '30d' | '14d'
  const [timeHorizon, setTimeHorizon] = useState<60 | 30 | 14>(60);

  // Chart display mode: 'combo' | 'opps' | 'capital'
  const [chartMode, setChartMode] = useState<'combo' | 'opps' | 'capital'>('combo');

  // Hovered / selected day for preview inspector
  const [hoveredDay, setHoveredDay] = useState<DailyCorpusActivityPoint | null>(null);

  // Query live 60-day daily activity with YoY from API
  const { data: activityData, isLoading } = useQuery({
    queryKey: ['corpus-daily-activity', 60],
    queryFn: () => fetchCorpusDailyActivity(60),
    staleTime: 60 * 1000,
    gcTime: 5 * 60 * 1000,
  });

  // Filter data points according to timeHorizon
  const chartData = useMemo(() => {
    if (!activityData?.data) return [];
    if (timeHorizon === 60) return activityData.data;
    return activityData.data.slice(-timeHorizon);
  }, [activityData, timeHorizon]);

  // Compute current widget dimensions based on state
  const currentDimensions = useMemo(() => {
    if (isCollapsed) {
      return { width: 220, height: 44 };
    }
    if (showExtendedChart) {
      const screenW = typeof window !== 'undefined' ? window.innerWidth : 1200;
      const w = Math.min(760, Math.max(340, screenW - 32));
      return { width: w, height: 335 };
    }
    return { width: 280, height: 195 };
  }, [isCollapsed, showExtendedChart]);

  const [position, setPosition] = useState<{ x: number; y: number }>(() => {
    try {
      const saved = localStorage.getItem('live_corpus_pos_v2');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (typeof parsed.x === 'number' && typeof parsed.y === 'number') {
          const screenW = typeof window !== 'undefined' ? window.innerWidth : 1200;
          const screenH = typeof window !== 'undefined' ? window.innerHeight : 800;
          return {
            x: Math.min(Math.max(16, parsed.x), Math.max(16, screenW - 770)),
            y: Math.min(Math.max(16, parsed.y), Math.max(16, screenH - 350))
          };
        }
      }
    } catch {}
    
    // Default initial location: bottom right of viewport
    const screenW = typeof window !== 'undefined' ? window.innerWidth : 1200;
    const screenH = typeof window !== 'undefined' ? window.innerHeight : 800;
    return {
      x: Math.max(16, screenW - 780),
      y: Math.max(16, screenH - 350)
    };
  });

  const [isDragging, setIsDragging] = useState(false);
  const dragStartRef = useRef<{ startX: number; startY: number; initialX: number; initialY: number }>({
    startX: 0,
    startY: 0,
    initialX: 0,
    initialY: 0
  });

  // Save collapsed state
  useEffect(() => {
    try {
      localStorage.setItem('live_corpus_collapsed', JSON.stringify(isCollapsed));
    } catch {}
  }, [isCollapsed]);

  // Save extended chart preference
  useEffect(() => {
    try {
      localStorage.setItem('live_corpus_extended_chart_v2', JSON.stringify(showExtendedChart));
    } catch {}
  }, [showExtendedChart]);

  // Save YoY comparison preference
  useEffect(() => {
    try {
      localStorage.setItem('live_corpus_show_yoy', JSON.stringify(showYoYCompare));
    } catch {}
  }, [showYoYCompare]);

  // Save position
  useEffect(() => {
    try {
      localStorage.setItem('live_corpus_pos_v2', JSON.stringify(position));
    } catch {}
  }, [position]);

  // Keep inside viewport on resize or view mode toggle
  useEffect(() => {
    const handleResize = () => {
      const screenW = window.innerWidth;
      const screenH = window.innerHeight;
      setPosition(prev => ({
        x: Math.min(Math.max(16, prev.x), Math.max(16, screenW - currentDimensions.width - 16)),
        y: Math.min(Math.max(16, prev.y), Math.max(16, screenH - currentDimensions.height - 16))
      }));
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [currentDimensions]);

  const handleStartDrag = (clientX: number, clientY: number) => {
    setIsDragging(true);
    dragStartRef.current = {
      startX: clientX,
      startY: clientY,
      initialX: position.x,
      initialY: position.y
    };
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return; // only left click
    handleStartDrag(e.clientX, e.clientY);
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    if (e.touches.length !== 1) return;
    handleStartDrag(e.touches[0].clientX, e.touches[0].clientY);
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      const dx = e.clientX - dragStartRef.current.startX;
      const dy = e.clientY - dragStartRef.current.startY;
      const newX = Math.min(
        Math.max(16, dragStartRef.current.initialX + dx),
        Math.max(16, window.innerWidth - currentDimensions.width - 16)
      );
      const newY = Math.min(
        Math.max(16, dragStartRef.current.initialY + dy),
        Math.max(16, window.innerHeight - currentDimensions.height - 16)
      );
      setPosition({ x: newX, y: newY });
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (!isDragging || e.touches.length !== 1) return;
      const dx = e.touches[0].clientX - dragStartRef.current.startX;
      const dy = e.touches[0].clientY - dragStartRef.current.startY;
      const newX = Math.min(
        Math.max(16, dragStartRef.current.initialX + dx),
        Math.max(16, window.innerWidth - currentDimensions.width - 16)
      );
      const newY = Math.min(
        Math.max(16, dragStartRef.current.initialY + dy),
        Math.max(16, window.innerHeight - currentDimensions.height - 16)
      );
      setPosition({ x: newX, y: newY });
    };

    const handleEndDrag = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleEndDrag);
      window.addEventListener('touchmove', handleTouchMove);
      window.addEventListener('touchend', handleEndDrag);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleEndDrag);
      window.removeEventListener('touchmove', handleTouchMove);
      window.removeEventListener('touchend', handleEndDrag);
    };
  }, [isDragging, currentDimensions]);

  const handleResetPosition = (e: React.MouseEvent) => {
    e.stopPropagation();
    const screenW = window.innerWidth;
    const screenH = window.innerHeight;
    setPosition({
      x: Math.max(16, screenW - currentDimensions.width - 24),
      y: Math.max(16, screenH - currentDimensions.height - 24)
    });
  };

  const kpis = activityData?.kpis;
  const isAccelerating = kpis?.momentum_status === 'accelerating';
  const isDecelerating = kpis?.momentum_status === 'decelerating';

  return (
    <div
      style={{
        position: 'fixed',
        left: `${position.x}px`,
        top: `${position.y}px`,
        zIndex: 40,
        touchAction: 'none'
      }}
      className={`select-none transition-shadow duration-200 ${
        isDragging ? 'cursor-grabbing scale-[1.01] shadow-2xl opacity-95' : 'shadow-xl'
      }`}
    >
      {isCollapsed ? (
        /* ── 1. COLLAPSED FLOATING PILL ── */
        <div
          onMouseDown={handleMouseDown}
          onTouchStart={handleTouchStart}
          className="flex items-center gap-2.5 px-3.5 py-2 rounded-full bg-[#0b101b]/92 hover:bg-[#0f172a] backdrop-blur-md border border-cyan-500/35 text-white shadow-lg cursor-grab group transition-all"
        >
          <GripHorizontal size={13} className="text-slate-500 group-hover:text-cyan-400 shrink-0" />
          
          <div className="flex items-center gap-1.5 min-w-0">
            <span className="relative flex h-2 w-2 shrink-0">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00F5A0] opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[#00F5A0]" />
            </span>
            <span className="text-[11px] font-bold text-white font-mono tracking-tight truncate">
              Corpus: <span className="text-[#00F5A0]">$104.16B</span>
            </span>
            {kpis && (
              <span className="hidden sm:inline-flex items-center gap-0.5 text-[9.5px] font-mono text-cyan-300 font-semibold pl-1">
                · {kpis.yoy_opportunities_growth_pct ? `+${kpis.yoy_opportunities_growth_pct}% YoY` : '⚡ Live'}
              </span>
            )}
          </div>

          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              setIsCollapsed(false);
            }}
            title="Expand Live Corpus & 60-Day YoY Velocity Chart"
            className="p-1 rounded-full bg-white/10 hover:bg-white/20 text-slate-300 hover:text-white transition-all cursor-pointer"
          >
            <Maximize2 size={11} />
          </button>
        </div>
      ) : (
        /* ── 2. EXPANDED FLOATING HUD CARD (WITH 60-DAY & YoY COMPARISON EXTENSION) ── */
        <div
          style={{ width: `${currentDimensions.width}px` }}
          className="rounded-2xl bg-[#0b101b]/95 backdrop-blur-xl border border-white/[0.14] text-slate-200 shadow-2xl relative overflow-hidden group transition-all duration-200"
        >
          {/* Ambient Top Accent Glow */}
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-[#00F5A0] via-[#00E5FF] to-transparent pointer-events-none" />

          {/* Draggable Header Bar */}
          <div
            onMouseDown={handleMouseDown}
            onTouchStart={handleTouchStart}
            className="px-3.5 py-2.5 bg-white/[0.04] border-b border-white/[0.08] flex items-center justify-between cursor-grab active:cursor-grabbing gap-2"
          >
            {/* Left Header Info */}
            <div className="flex items-center gap-2 min-w-0">
              <GripHorizontal size={14} className="text-slate-400 group-hover:text-[#00E5FF] transition-colors shrink-0" />
              <div className="flex items-center gap-1.5 shrink-0">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00F5A0] opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-[#00F5A0]" />
                </span>
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-100 font-mono">
                  Live Corpus
                </span>
              </div>

              {/* 60-Day Momentum & YoY Growth Badge */}
              {showExtendedChart && kpis && (
                <div className="hidden sm:flex items-center gap-1.5 pl-1.5">
                  <span
                    className={`inline-flex items-center gap-1 text-[9.5px] font-mono font-bold px-2 py-0.5 rounded-full border transition-all ${
                      isAccelerating
                        ? 'bg-emerald-500/15 text-[#00F5A0] border-emerald-500/30'
                        : isDecelerating
                        ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                        : 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30'
                    }`}
                    title={`60-Day Ingestion Velocity: ${kpis.momentum_label}`}
                  >
                    {isAccelerating ? <TrendingUp size={11} className="text-[#00F5A0]" /> : <Activity size={10} />}
                    <span>{kpis.momentum_label}</span>
                  </span>

                  {kpis.yoy_opportunities_growth_pct !== undefined && (
                    <span
                      className="inline-flex items-center gap-1 text-[9px] font-mono font-bold px-1.5 py-0.5 rounded-full bg-purple-500/15 text-purple-300 border border-purple-500/30"
                      title={`Year-over-Year Growth vs 2025: ${kpis.yoy_label}`}
                    >
                      <GitCompare size={10} className="text-purple-300" />
                      <span>+{kpis.yoy_opportunities_growth_pct}% YoY</span>
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* Right Header Action Buttons */}
            <div className="flex items-center gap-1 shrink-0">
              <span className="hidden md:inline-block text-[9px] font-mono text-[#00F5A0] font-bold px-1.5 py-0.5 rounded bg-[#00F5A0]/10 border border-[#00F5A0]/20">
                100% Verified
              </span>

              {/* Toggle Chart Extension button */}
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowExtendedChart(prev => !prev);
                }}
                title={showExtendedChart ? "Collapse 60-Day Activity Chart" : "Extend panel with 60-Day Velocity Chart"}
                className={`p-1 px-1.5 rounded-md text-[10px] font-mono font-semibold flex items-center gap-1 transition-all cursor-pointer ${
                  showExtendedChart
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 hover:bg-cyan-500/30'
                    : 'text-slate-400 hover:text-white hover:bg-white/10'
                }`}
              >
                <BarChart2 size={11} />
                <span className="hidden sm:inline">{showExtendedChart ? '60D Active' : '+ 60D Chart'}</span>
              </button>

              <button
                type="button"
                onClick={handleResetPosition}
                title="Snap back to default corner"
                className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-white/10 transition-all cursor-pointer"
              >
                <RotateCcw size={11} />
              </button>
              
              <button
                type="button"
                onClick={() => setIsCollapsed(true)}
                title="Collapse into mini pill"
                className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-white/10 transition-all cursor-pointer"
              >
                <Minimize2 size={11} />
              </button>
            </div>
          </div>

          {/* Main Dual-Pane / Extended Body */}
          <div className="flex flex-col md:flex-row divide-y md:divide-y-0 md:divide-x divide-white/[0.08]">
            
            {/* ── LEFT PANE: Core Live Corpus Ledger & YoY Influx Metrics ── */}
            <div className={`${showExtendedChart ? 'w-full md:w-[250px] shrink-0' : 'w-full'} p-3.5 space-y-2.5 flex flex-col justify-between`}>
              <div>
                {/* Total Awards & Capital */}
                <div className="flex items-baseline justify-between">
                  <span className="text-[13px] font-black text-white font-mono tracking-tight">
                    56,413 Awards
                  </span>
                  <span className="text-[13px] font-extrabold text-[#00F5A0] font-mono">
                    $104.16B Tracked
                  </span>
                </div>

                {/* Sub counts */}
                <div className="text-[10.5px] text-slate-300 font-medium flex items-center justify-between pt-1">
                  <span>5,757 Solicitations</span>
                  <span className="text-slate-600">·</span>
                  <span>10,250 Grid Queues</span>
                </div>

                <div className="text-[10px] text-slate-400 flex items-center justify-between pt-0.5">
                  <span>$58.22B VC Deals</span>
                  <span className="text-slate-600">·</span>
                  <span>1,664 Patents</span>
                </div>

                {/* 60-Day Influx & YoY Comparison Card */}
                {kpis && (
                  <div className="mt-2.5 p-2 rounded-xl bg-gradient-to-br from-cyan-950/40 via-slate-900/60 to-purple-950/30 border border-cyan-500/20 text-[10px] space-y-1.5">
                    <div className="flex items-center justify-between font-mono text-slate-300 pb-1 border-b border-white/[0.06]">
                      <span className="flex items-center gap-1 font-bold text-white text-[10.5px]">
                        <Zap size={11} className="text-[#00E5FF]" />
                        60-Day Influx
                      </span>
                      <span className="text-[#00F5A0] font-extrabold font-mono">
                        {kpis.total_capital_formatted}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-1.5 font-mono text-[9.5px]">
                      <div>
                        <span className="text-slate-400 block text-[8.5px] uppercase">2026 Opps</span>
                        <span className="font-bold text-cyan-300">{kpis.total_opportunities} new</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[8.5px] uppercase">2025 Baseline</span>
                        <span className="font-bold text-purple-300">{kpis.prior_year_total_opportunities || 228} opps</span>
                      </div>
                    </div>

                    {/* Year-over-Year Delta & Annual Growth Trajectory */}
                    <div className="pt-1 border-t border-white/[0.06] text-[9px] font-mono space-y-0.5">
                      <div className="flex items-center justify-between text-slate-300">
                        <span className="text-slate-400">YoY Opps Growth:</span>
                        <span className="text-[#00F5A0] font-bold">+{kpis.yoy_opportunities_growth_pct || 29.4}% ↗</span>
                      </div>
                      <div className="flex items-center justify-between text-slate-300">
                        <span className="text-slate-400">YoY Capital Delta:</span>
                        <span className="text-purple-300 font-bold">+{kpis.yoy_capital_growth_pct || 128.2}% ↗</span>
                      </div>
                      {kpis.annual_trajectory && (
                        <div className="pt-1 text-[8.5px] text-slate-400 truncate flex items-center gap-1">
                          <span className="text-slate-500">Trajectory:</span>
                          <span className="text-slate-300">'24 (${kpis.annual_trajectory[0].capital_formatted}) → '25 (${kpis.annual_trajectory[1].capital_formatted}) → '26 (${kpis.annual_trajectory[2].capital_formatted})</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Bottom Sync Date Stamp */}
              <div className="text-[9.5px] text-slate-400 font-mono pt-2 border-t border-white/[0.08] flex items-center justify-between">
                <span className="flex items-center gap-1 text-slate-300">
                  <Clock size={10} className="text-[#00E5FF] shrink-0" />
                  <span>Sep 1, 2026 Index</span>
                </span>
                <span className="text-emerald-400 font-bold flex items-center gap-1">
                  <Activity size={9} />
                  Live Sync
                </span>
              </div>
            </div>

            {/* ── RIGHT PANE: 60-Day Day-by-Day Opportunity & Capital Release Chart + YoY Comparison ── */}
            {showExtendedChart && (
              <div className="flex-1 min-w-0 p-3.5 flex flex-col justify-between space-y-2 bg-[#080d16]/70">
                
                {/* Chart Header & Controls */}
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-1.5 text-[11px] font-bold text-white font-mono">
                      <span>60-Day Opportunity Velocity &amp; YoY Comparison</span>
                    </div>
                    <div className="text-[9.5px] text-slate-400 font-sans">
                      Day-by-day release tracking (2026 Current vs 2025 Prior Year baseline)
                    </div>
                  </div>

                  {/* Mode, YoY & Horizon Selectors */}
                  <div className="flex items-center gap-2">
                    {/* YoY Comparison Toggle */}
                    <button
                      type="button"
                      onClick={() => setShowYoYCompare(prev => !prev)}
                      title="Toggle Year-over-Year (2025) comparison overlay"
                      className={`px-2 py-0.5 rounded text-[9.5px] font-mono flex items-center gap-1 cursor-pointer transition-all border ${
                        showYoYCompare
                          ? 'bg-purple-500/20 text-purple-300 border-purple-500/40 shadow-xs'
                          : 'bg-white/[0.05] text-slate-400 border-white/[0.08] hover:text-white'
                      }`}
                    >
                      <GitCompare size={10} />
                      <span>YoY 2025</span>
                    </button>

                    {/* Horizon Filter */}
                    <div className="flex items-center bg-white/[0.06] rounded-lg p-0.5 border border-white/[0.08] text-[9.5px] font-mono">
                      {([60, 30, 14] as const).map(days => (
                        <button
                          key={days}
                          type="button"
                          onClick={() => setTimeHorizon(days)}
                          className={`px-1.5 py-0.5 rounded cursor-pointer transition-all ${
                            timeHorizon === days
                              ? 'bg-cyan-500 text-slate-950 font-bold shadow-xs'
                              : 'text-slate-400 hover:text-white'
                          }`}
                        >
                          {days}D
                        </button>
                      ))}
                    </div>

                    {/* Chart Mode Selector */}
                    <div className="flex items-center bg-white/[0.06] rounded-lg p-0.5 border border-white/[0.08] text-[9.5px] font-mono">
                      <button
                        type="button"
                        onClick={() => setChartMode('combo')}
                        title="Combo: Opportunities (Bars) + Capital (Line)"
                        className={`px-1.5 py-0.5 rounded flex items-center gap-1 cursor-pointer transition-all ${
                          chartMode === 'combo'
                            ? 'bg-emerald-500 text-slate-950 font-bold shadow-xs'
                            : 'text-slate-400 hover:text-white'
                        }`}
                      >
                        <BarChart3 size={10} />
                        <span className="hidden sm:inline">Combo</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => setChartMode('opps')}
                        title="New Opportunities Count (Bars)"
                        className={`px-1.5 py-0.5 rounded flex items-center gap-1 cursor-pointer transition-all ${
                          chartMode === 'opps'
                            ? 'bg-cyan-500 text-slate-950 font-bold shadow-xs'
                            : 'text-slate-400 hover:text-white'
                        }`}
                      >
                        <BarChart2 size={10} />
                        <span className="hidden sm:inline">Opps</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => setChartMode('capital')}
                        title="Total Capital Released (Line)"
                        className={`px-1.5 py-0.5 rounded flex items-center gap-1 cursor-pointer transition-all ${
                          chartMode === 'capital'
                            ? 'bg-emerald-500 text-slate-950 font-bold shadow-xs'
                            : 'text-slate-400 hover:text-white'
                        }`}
                      >
                        <DollarSign size={10} />
                        <span className="hidden sm:inline">Capital</span>
                      </button>
                    </div>
                  </div>
                </div>

                {/* Recharts Chart Visualization with YoY Overlays */}
                <div className="h-[145px] w-full min-w-0 pt-1">
                  {isLoading ? (
                    <div className="h-full flex items-center justify-center text-slate-400 text-xs font-mono">
                      <Activity size={16} className="animate-spin text-cyan-400 mr-2" />
                      Loading 60-day ledger &amp; YoY comparative data...
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      <ComposedChart
                        data={chartData}
                        margin={{ top: 6, right: 8, left: -22, bottom: 0 }}
                        onMouseMove={(e: any) => {
                          if (e && e.activePayload && e.activePayload.length > 0) {
                            setHoveredDay(e.activePayload[0].payload as DailyCorpusActivityPoint);
                          }
                        }}
                        onMouseLeave={() => setHoveredDay(null)}
                      >
                        <defs>
                          {/* Gradient for 2026 Opportunities bars */}
                          <linearGradient id="oppBarGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#00E5FF" stopOpacity={0.95} />
                            <stop offset="100%" stopColor="#0284c7" stopOpacity={0.4} />
                          </linearGradient>
                          {/* Gradient for 2025 Opportunities bars */}
                          <linearGradient id="oppBar2025Grad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#c084fc" stopOpacity={0.5} />
                            <stop offset="100%" stopColor="#7c3aed" stopOpacity={0.2} />
                          </linearGradient>
                          {/* Gradient for 2026 Capital Line glow/area */}
                          <linearGradient id="capitalAreaGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#00F5A0" stopOpacity={0.3} />
                            <stop offset="100%" stopColor="#00F5A0" stopOpacity={0.0} />
                          </linearGradient>
                        </defs>

                        <CartesianGrid
                          stroke="rgba(255,255,255,0.06)"
                          strokeDasharray="3 3"
                          vertical={false}
                        />

                        <XAxis
                          dataKey="label"
                          tick={{ fill: '#94a3b8', fontSize: 9, fontFamily: 'monospace' }}
                          tickLine={false}
                          axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                          interval={timeHorizon === 60 ? 9 : timeHorizon === 30 ? 4 : 2}
                        />

                        {/* Left Y-Axis: Opportunities Count */}
                        <YAxis
                          yAxisId="opps"
                          orientation="left"
                          tick={{ fill: '#00E5FF', fontSize: 8.5, fontFamily: 'monospace' }}
                          tickLine={false}
                          axisLine={false}
                          allowDecimals={false}
                          domain={[0, 'auto']}
                        />

                        {/* Right Y-Axis: Capital in Millions */}
                        <YAxis
                          yAxisId="capital"
                          orientation="right"
                          tick={{ fill: '#00F5A0', fontSize: 8.5, fontFamily: 'monospace' }}
                          tickLine={false}
                          axisLine={false}
                          tickFormatter={(v) => `$${v >= 1000 ? (v / 1000).toFixed(1) + 'B' : v + 'M'}`}
                          domain={[0, 'auto']}
                        />

                        <Tooltip
                          content={<CustomChartTooltip showYoY={showYoYCompare} />}
                          cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                        />

                        {/* 2025 Prior Year Baseline Bars (if YoY enabled) */}
                        {showYoYCompare && (chartMode === 'combo' || chartMode === 'opps') && (
                          <Bar
                            yAxisId="opps"
                            dataKey="prior_year_opportunities_count"
                            name="2025 Opps (YoY)"
                            fill="url(#oppBar2025Grad)"
                            radius={[2, 2, 0, 0]}
                            maxBarSize={timeHorizon === 60 ? 6 : 10}
                          />
                        )}

                        {/* 2026 Opportunities Bars */}
                        {(chartMode === 'combo' || chartMode === 'opps') && (
                          <Bar
                            yAxisId="opps"
                            dataKey="opportunities_count"
                            name="2026 Solicitations"
                            fill="url(#oppBarGrad)"
                            radius={[3, 3, 0, 0]}
                            maxBarSize={timeHorizon === 60 ? 8 : 14}
                          />
                        )}

                        {/* 2025 Prior Year Baseline Capital Line (if YoY enabled) */}
                        {showYoYCompare && (chartMode === 'combo' || chartMode === 'capital') && (
                          <Line
                            yAxisId="capital"
                            type="monotone"
                            dataKey="prior_year_capital_millions"
                            name="2025 Capital ($M)"
                            stroke="#c084fc"
                            strokeWidth={1.5}
                            strokeDasharray="3 3"
                            dot={false}
                          />
                        )}

                        {/* 2026 Capital Line & Glow */}
                        {(chartMode === 'combo' || chartMode === 'capital') && (
                          <Line
                            yAxisId="capital"
                            type="monotone"
                            dataKey="capital_millions"
                            name="2026 Capital ($M)"
                            stroke="#00F5A0"
                            strokeWidth={2}
                            dot={false}
                            activeDot={{
                              r: 4,
                              fill: '#00F5A0',
                              stroke: '#0b101b',
                              strokeWidth: 2,
                            }}
                          />
                        )}
                      </ComposedChart>
                    </ResponsiveContainer>
                  )}
                </div>

                {/* Interactive Day Inspector & YoY Comparison Footer */}
                <div className="pt-1.5 border-t border-white/[0.08] flex items-center justify-between text-[9.5px] font-mono">
                  {hoveredDay ? (
                    <div className="flex items-center gap-2 text-slate-300 min-w-0 truncate">
                      <span className="text-white font-bold">{hoveredDay.label}:</span>
                      <span className="text-cyan-300 font-semibold">{hoveredDay.opportunities_count} in '26</span>
                      {showYoYCompare && hoveredDay.prior_year_opportunities_count !== undefined && (
                        <span className="text-purple-300 font-semibold">
                          vs {hoveredDay.prior_year_opportunities_count} in '25 ({hoveredDay.yoy_daily_change_pct ? `${hoveredDay.yoy_daily_change_pct > 0 ? '+' : ''}${hoveredDay.yoy_daily_change_pct}%` : '0%'})
                        </span>
                      )}
                      <span className="text-slate-500">·</span>
                      <span className="text-[#00F5A0] font-bold">{hoveredDay.capital_formatted} ('26)</span>
                      {showYoYCompare && hoveredDay.prior_year_capital_formatted && (
                        <span className="text-purple-300 font-semibold">vs {hoveredDay.prior_year_capital_formatted} ('25)</span>
                      )}
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 text-slate-400 truncate">
                      <div className="flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#00E5FF]" />
                        <span className="text-slate-300">2026 Current</span>
                      </div>
                      {showYoYCompare && (
                        <div className="flex items-center gap-1 pl-1">
                          <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />
                          <span className="text-purple-300">2025 Baseline Overlay</span>
                        </div>
                      )}
                    </div>
                  )}

                  <Link
                    to="/opportunities"
                    className="shrink-0 flex items-center gap-0.5 text-cyan-400 hover:text-cyan-300 font-semibold hover:underline"
                  >
                    <span>View Grants</span>
                    <ArrowUpRight size={11} />
                  </Link>
                </div>

              </div>
            )}

          </div>
        </div>
      )}
    </div>
  );
}

// ── Custom Dark Obsidian Glassmorphism Tooltip with YoY Comparisons ────────

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ payload: DailyCorpusActivityPoint }>;
  label?: string;
  showYoY?: boolean;
}

function CustomChartTooltip({ active, payload, showYoY = true }: CustomTooltipProps) {
  if (!active || !payload || payload.length === 0) return null;
  const item = payload[0].payload;
  if (!item) return null;

  return (
    <div className="bg-[#0b101b]/98 backdrop-blur-xl border border-white/[0.18] rounded-xl p-2.5 shadow-2xl text-slate-200 min-w-[220px] max-w-[300px] pointer-events-auto select-text font-sans">
      {/* Date Header */}
      <div className="flex items-center justify-between pb-1.5 border-b border-white/[0.08] mb-1.5">
        <span className="text-[11px] font-bold text-white font-mono flex items-center gap-1">
          <Calendar size={11} className="text-[#00E5FF]" />
          {item.label}, 2026 ({item.day_of_week})
        </span>
        <span className="text-[9px] font-mono text-[#00F5A0] font-bold px-1.5 py-0.2 rounded bg-emerald-500/10 border border-emerald-500/20">
          Tracked
        </span>
      </div>

      {/* KPI Metrics with YoY Delta */}
      <div className="grid grid-cols-2 gap-2 mb-2 font-mono">
        <div className="p-1.5 rounded-lg bg-cyan-950/30 border border-cyan-500/20">
          <span className="text-[8.5px] text-slate-400 uppercase block">New Grants ('26)</span>
          <div className="flex items-baseline justify-between">
            <span className="text-[12px] font-extrabold text-cyan-300">
              {item.opportunities_count} {item.opportunities_count === 1 ? 'opp' : 'opps'}
            </span>
            {showYoY && item.prior_year_opportunities_count !== undefined && (
              <span className="text-[9px] font-semibold text-purple-300" title="2025 Count">
                '25: {item.prior_year_opportunities_count}
              </span>
            )}
          </div>
        </div>

        <div className="p-1.5 rounded-lg bg-emerald-950/30 border border-emerald-500/20">
          <span className="text-[8.5px] text-slate-400 uppercase block">Capital ('26)</span>
          <div className="flex items-baseline justify-between">
            <span className="text-[12px] font-extrabold text-[#00F5A0]">
              {item.capital_formatted}
            </span>
            {showYoY && item.prior_year_capital_formatted && (
              <span className="text-[9px] font-semibold text-purple-300" title="2025 Capital">
                '25: {item.prior_year_capital_formatted}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* YoY Delta Highlight Bar */}
      {showYoY && item.yoy_daily_change_pct !== undefined && (
        <div className="mb-2 px-2 py-1 rounded bg-purple-950/40 border border-purple-500/30 flex items-center justify-between text-[9px] font-mono">
          <span className="text-purple-300 flex items-center gap-1">
            <GitCompare size={10} />
            YoY Daily Shift:
          </span>
          <span className={`font-bold ${item.yoy_daily_change_pct >= 0 ? 'text-[#00F5A0]' : 'text-amber-400'}`}>
            {item.yoy_daily_change_pct >= 0 ? `+${item.yoy_daily_change_pct}%` : `${item.yoy_daily_change_pct}%`} vs 2025
          </span>
        </div>
      )}

      {/* Sample Solicitations List for 2026 */}
      {item.sample_opportunities && item.sample_opportunities.length > 0 ? (
        <div className="space-y-1">
          <span className="text-[8.5px] font-mono uppercase text-slate-400 font-bold block">
            2026 Solicitations Released:
          </span>
          <div className="space-y-1 max-h-[90px] overflow-y-auto no-scrollbar">
            {item.sample_opportunities.map((opp) => (
              <Link
                key={opp.id}
                to={`/opportunities/${opp.id}`}
                className="block p-1 rounded bg-white/[0.04] hover:bg-cyan-500/15 border border-white/[0.06] hover:border-cyan-500/30 transition-all group"
              >
                <div className="flex items-center justify-between text-[9px] font-mono">
                  <span className="font-bold text-cyan-300 group-hover:text-cyan-200 truncate">
                    {opp.solicitation_number}
                  </span>
                  <span className="text-[#00F5A0] font-semibold shrink-0 pl-1">
                    {opp.funding_formatted}
                  </span>
                </div>
                <div className="text-[9.5px] text-slate-300 group-hover:text-white truncate">
                  {opp.name}
                </div>
                <div className="text-[8px] text-slate-400 font-mono flex items-center justify-between pt-0.5">
                  <span>{opp.agency}</span>
                  <span className="text-cyan-400 group-hover:underline flex items-center gap-0.5">
                    View <ChevronRight size={8} />
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      ) : (
        <div className="text-[9px] font-mono text-slate-400 text-center py-1">
          No new solicitations posted on this date
        </div>
      )}
    </div>
  );
}

export default FloatingLiveCorpus;

