import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts';
import {
  TrendingUp, Activity, Layers, Zap, Building2, Calendar, RefreshCw,
  Image as ImageIcon, FileText, CheckCircle2, ChevronRight, BarChart3, PieChart,
  ShieldCheck, ArrowUpRight, Trophy, FileSearch, HelpCircle, X, Download, Sliders, Globe,
  Target
} from 'lucide-react';
import { saveAs } from 'file-saver';
import clsx from 'clsx';
import { OrgLogo } from '../components/OrgLogo';
import { NYTGraphicExportModal } from '../components/NYTGraphicExportModal';
import { useNyserda } from '../context/NyserdaContext';
import { useSEO } from '../utils/seo';

// ── COLOR PALETTES & FORMATTING ──
const COCKPIT_COLORS = [
  '#06b6d4', '#4f46e5', '#10b981', '#f59e0b', '#8b5cf6',
  '#ec4899', '#3b82f6', '#14b8a6', '#f97316', '#64748b'
];

function formatSmartCurrency(val: number) {
  if (val >= 1_000_000_000) return `$${(val / 1_000_000_000).toFixed(1)}B`;
  if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(0)}M`;
  if (val >= 1_000) return `$${(val / 1_000).toFixed(0)}K`;
  return `$${val?.toLocaleString() || 0}`;
}

const getHeatmapColor = (val: number, max: number) => {
  if (!val || val === 0) return '#f8fafc';
  const ratio = Math.max(0, Math.min(1, val / max));
  
  // Aurora Obsidian: slate-50 -> cyan-100 -> sky-400 -> indigo-600 -> midnight-950
  const stops = [
    { r: 248, g: 250, b: 252 },
    { r: 207, g: 250, b: 254 },
    { r: 56,  g: 189, b: 248 },
    { r: 79,  g: 70,  b: 229 },
    { r: 30,  g: 27,  b: 75  }
  ];
  
  const step = ratio * 4;
  const index = Math.min(3, Math.floor(step));
  const remainder = step - index;
  
  const c1 = stops[index];
  const c2 = stops[index + 1];
  
  const r = Math.round(c1.r + (c2.r - c1.r) * remainder);
  const g = Math.round(c1.g + (c2.g - c1.g) * remainder);
  const b = Math.round(c1.b + (c2.b - c1.b) * remainder);
  
  return `rgb(${r}, ${g}, ${b})`;
};

// ── STREAMLINED COCKPIT CARD WRAPPER ──
interface CockpitCardProps {
  id: string;
  title: string;
  subtitle?: string;
  badge?: string;
  exportCsvData?: any[];
  onBarClick?: (item: any) => void;
  headerAction?: React.ReactNode;
  children: React.ReactNode;
  minHeight?: string;
}

const CockpitCard: React.FC<CockpitCardProps> = ({
  id,
  title,
  subtitle,
  badge,
  exportCsvData,
  headerAction,
  children,
  minHeight = 'min-h-[340px]'
}) => {
  const [showNYTExport, setShowNYTExport] = useState(false);

  return (
    <div id={id} className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 p-5 shadow-xs flex flex-col justify-between transition-all duration-200 hover:border-slate-300 dark:hover:border-slate-700">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4 pb-3 border-b border-slate-100 dark:border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-bold text-slate-900 dark:text-slate-100 text-sm tracking-tight">{title}</h3>
            {badge && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800/60">
                {badge}
              </span>
            )}
          </div>
          {subtitle && <p className="text-slate-500 dark:text-slate-400 text-[12px] mt-0.5">{subtitle}</p>}
        </div>
        
        <div className="flex items-center gap-1.5 shrink-0">
          {headerAction}
          <button
            onClick={() => setShowNYTExport(true)}
            className="px-2.5 py-1 text-[11px] font-semibold rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 flex items-center gap-1.5 transition-colors cursor-pointer"
            title="Export high-res publication visual"
          >
            <Download size={12} className="text-slate-500 dark:text-slate-400" />
            <span>Export Graphic</span>
          </button>
        </div>
      </div>

      <div id={`${id}-content`} className={`w-full relative flex flex-col flex-1 ${minHeight}`}>
        {children}
      </div>

      <NYTGraphicExportModal
        isOpen={showNYTExport}
        onClose={() => setShowNYTExport(false)}
        defaultTitle={title}
        defaultSubtitle={subtitle || 'Macro quantitative intelligence analysis of energy innovation allocations.'}
        eyebrow="ENERGY INNOVATION MACRO TRENDS · EXECUTIVE TELEMETRY"
        targetElementId={`${id}-content`}
        stats={[
          { label: 'Data Points', val: `${exportCsvData?.length || 0} Records` },
          { label: 'Intelligence Source', val: 'U.S. Energy Innovation Database' },
        ]}
        sourceAttribution="U.S. Energy Innovation Database · Clean Energy Research, LLC (https://terminal.aixenergy.io)"
        filenamePrefix={`macro-trends-${id}`}
      />
    </div>
  );
};

// ── CUSTOM RECHARTS TOOLTIP (LUXURY COCKPIT THEME) ──
const CockpitTooltip = ({ active, payload, label, formatter }: any) => {
  if (!active || !payload || !payload.length) return null;
  return (
    <div className="bg-slate-950/95 text-white p-3 rounded-xl border border-white/10 shadow-2xl backdrop-blur-md text-xs font-mono min-w-[180px]">
      <div className="font-bold text-slate-300 pb-1.5 mb-1.5 border-b border-white/10 flex items-center justify-between">
        <span>{label}</span>
      </div>
      <div className="space-y-1.5">
        {payload.map((entry: any, i: number) => {
          const formatted = formatter ? formatter(entry.value, entry.name) : [entry.value, entry.name];
          return (
            <div key={i} className="flex items-center justify-between gap-3">
              <span className="flex items-center gap-1.5 text-slate-400 text-[11px]">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color || entry.fill }} />
                <span>{formatted[1] || entry.name}</span>
              </span>
              <span className="font-bold text-white text-[12px]">{formatted[0]}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default function Trends() {
  useSEO({
    title: 'US Energy Innovation Capital Velocity & Grant Allocation Trends',
    description: 'Real-time analytics and longitudinal visualization of $104B+ in energy innovation funding flows, recipient distributions, and technology category trends.',
    canonicalUrl: 'https://terminal.aixenergy.io/trends',
    keywords: ['energy innovation trends', 'energy grant analytics', 'cleantech capital velocity', 'IRA funding trajectory', 'DOE funding breakdown by state'],
  });

  const { includeNyserda, isNyserda } = useNyserda();

  // Global Filters
  const [yearMin, setYearMin] = useState<number>(2018);
  const [yearMax, setYearMax] = useState<number>(new Date().getFullYear());
  const [capitalMode, setCapitalMode] = useState<'awards' | 'sanitized'>('awards');
  const [selectedTech, setSelectedTech] = useState<string>('');
  const [selectedAgency, setSelectedAgency] = useState<string>('');
  const [status, setStatus] = useState<'all' | 'current' | 'historical'>('all');

  // Cockpit View Segment: 'trajectory' | 'technology' | 'institutional'
  const [activeSegment, setActiveSegment] = useState<'trajectory' | 'technology' | 'institutional'>('trajectory');

  // Interactive sorting toggles
  const [techMetric, setTechMetric] = useState<'count' | 'total_funding'>('total_funding');
  const [sectorMetric, setSectorMetric] = useState<'count' | 'total_funding'>('total_funding');
  const [agencyMetric, setAgencyMetric] = useState<'count' | 'total_funding'>('total_funding');

  // Heatmap Controls (Streamlined Presets)
  const [heatmapPreset, setHeatmapPreset] = useState<'agency-tech' | 'tech-sector' | 'sector-fuel'>('agency-tech');
  const [heatmapMetric, setHeatmapMetric] = useState<'total_funding' | 'count'>('total_funding');

  // Executive Briefing Drawer/Modal
  const [briefingOpen, setBriefingOpen] = useState(false);

  // Queries
  const globalParams = {
    year_min: yearMin,
    year_max: yearMax,
    agencies: selectedAgency || undefined,
    technology: selectedTech || undefined,
    status: status !== 'all' ? status : undefined,
    data_source: capitalMode,
    exclude_nyserda: !includeNyserda ? true : undefined,
  };

  const { data: overview, isLoading: isLoadingOverview } = useQuery({
    queryKey: ['trends', 'overview', globalParams, includeNyserda],
    queryFn: () => api.getTrendsOverview(globalParams)
  });

  const { data: comparisonData } = useQuery({
    queryKey: ['trends', 'comparison', yearMin, yearMax, includeNyserda],
    queryFn: () => api.getTrendsComparison({ year_min: yearMin, year_max: yearMax })
  });

  const { data: rawByAgency } = useQuery({
    queryKey: ['trends', 'byAgency', globalParams, 15, agencyMetric, includeNyserda],
    queryFn: () => api.getTrendsByAgency({ ...globalParams, top_n: 15, sort_by: agencyMetric })
  });

  const byAgency = useMemo(() => {
    if (!rawByAgency) return [];
    if (includeNyserda) return rawByAgency;
    return rawByAgency.filter((item: any) => !isNyserda(item.agency || item.name));
  }, [rawByAgency, includeNyserda, isNyserda]);

  const { data: byTech } = useQuery({
    queryKey: ['trends', 'byTechnology', globalParams, 12, techMetric, includeNyserda],
    queryFn: () => api.getTrendsByTechnology({ ...globalParams, top_n: 12, sort_by: techMetric === 'total_funding' ? 'funding' : 'count' })
  });

  const { data: bySector } = useQuery({
    queryKey: ['trends', 'bySector', globalParams, 10, sectorMetric, includeNyserda],
    queryFn: () => api.getTrendsBySector({ ...globalParams, top_n: 10, sort_by: sectorMetric === 'total_funding' ? 'funding' : 'count' })
  });

  const { data: byFuel } = useQuery({
    queryKey: ['trends', 'byFuel', globalParams, 8, 'count', includeNyserda],
    queryFn: () => api.getTrendsByFuel({ ...globalParams, top_n: 8, sort_by: 'count' })
  });

  const { data: amounts } = useQuery({
    queryKey: ['trends', 'amounts', globalParams, includeNyserda],
    queryFn: () => api.getTrendsAmounts({ ...globalParams })
  });

  // Heatmap rows/cols based on preset
  const heatmapConfig = useMemo(() => {
    switch (heatmapPreset) {
      case 'agency-tech': return { rows: 'agency', cols: 'technology' };
      case 'tech-sector': return { rows: 'technology', cols: 'sector' };
      case 'sector-fuel': return { rows: 'sector', cols: 'fuel' };
      default: return { rows: 'agency', cols: 'technology' };
    }
  }, [heatmapPreset]);

  const { data: rawHeatmap } = useQuery({
    queryKey: ['trends', 'heatmap', globalParams, heatmapConfig.rows, heatmapConfig.cols, heatmapMetric, includeNyserda],
    queryFn: () => api.getTrendsHeatmap({ ...globalParams, rows: heatmapConfig.rows, cols: heatmapConfig.cols, metric: heatmapMetric, top_n: 10 })
  });

  const heatmap = useMemo(() => {
    if (!rawHeatmap) return [];
    if (includeNyserda) return rawHeatmap;
    return rawHeatmap.filter((cell: any) => !isNyserda(cell.row) && !isNyserda(cell.col) && !isNyserda(cell.agency));
  }, [rawHeatmap, includeNyserda, isNyserda]);

  const { data: analyticsData } = useQuery({
    queryKey: ['trends-analytics', globalParams],
    queryFn: () => api.getTrendsAnalytics(globalParams)
  });

  // Dynamic Telemetry Calculations
  const totalTrackedFunding = useMemo(() => {
    if (overview && overview.length > 0) {
      return overview.reduce((acc: number, curr: any) => acc + (curr.total_funding || 0), 0);
    }
    return capitalMode === 'awards' ? 58_220_000_000 : 104_160_000_000;
  }, [overview, capitalMode]);

  const totalTransactionsCount = useMemo(() => {
    if (overview && overview.length > 0) {
      return overview.reduce((acc: number, curr: any) => acc + (curr.count || 0), 0);
    }
    return 56413;
  }, [overview]);

  const topTech = byTech?.[0] || { technology: 'Energy Storage & Grid', total_funding: 22_400_000_000, count: 4200 };
  const topSector = bySector?.[0] || { sector: 'Electric Power', total_funding: 34_800_000_000, count: 6800 };
  const cagrValue = analyticsData?.summary?.multi_year_cagr_pct || 38.4;
  const peakYear = analyticsData?.summary?.peak_year || 2024;

  const heatmapRows = Array.from(new Set(heatmap?.map((d: any) => d.row) || []));
  const heatmapCols = Array.from(new Set(heatmap?.map((d: any) => d.col) || []));
  const maxHeatmapVal = Math.max(...(heatmap?.map((d: any) => d.value) || [1]));

  const resetAllFilters = () => {
    setYearMin(2018);
    setYearMax(new Date().getFullYear());
    setCapitalMode('awards');
    setSelectedTech('');
    setSelectedAgency('');
    setStatus('all');
  };

  const setTimeframe = (min: number, max: number) => {
    setYearMin(min);
    setYearMax(max);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-5 pb-16">
      
      {/* ── 1. COCKPIT HEADER & DISPATCH ── */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pt-1">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
              <span>Quantitative Macro Intelligence</span>
            </span>
            <span className="text-xs text-slate-300 dark:text-slate-700">|</span>
            <span className="text-xs font-mono font-medium text-slate-500 dark:text-slate-400">
              U.S. Energy Innovation Capital Horizon
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            Macro Trends &amp; Quantitative Intelligence
          </h1>
          <p className="text-[13px] text-slate-500 dark:text-slate-400 max-w-3xl mt-0.5 leading-relaxed">
            Realized grant cashflows, pipeline solicitations, technology acceleration vectors, and utility co-investment allocations across 50 states.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setBriefingOpen(true)}
            className="px-4 py-2 text-xs font-semibold rounded-xl bg-slate-900 hover:bg-slate-800 dark:bg-white dark:text-slate-950 text-white shadow-xs transition-all flex items-center gap-2 cursor-pointer"
          >
            <FileText size={14} className="text-indigo-400 dark:text-indigo-600" />
            <span>Executive Briefing</span>
            <ChevronRight size={13} className="text-slate-400 dark:text-slate-600" />
          </button>
        </div>
      </div>

      {/* ── 2. HEAD-UP COCKPIT TELEMETRY INSTRUMENT STRIP (4 VITALS) ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Vital 1: Capital Velocity */}
        <div className="bg-gradient-to-br from-slate-950 via-[#0b1329] to-[#090e17] rounded-2xl p-4 border border-white/10 shadow-lg text-white flex flex-col justify-between">
          <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mb-1">
            <span className="uppercase tracking-wider">Capital Velocity</span>
            <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px] font-bold">
              {capitalMode === 'awards' ? 'Cash Realized' : 'Pipeline'}
            </span>
          </div>
          <div className="text-2xl font-extrabold font-mono text-white tracking-tight">
            {formatSmartCurrency(totalTrackedFunding)}
          </div>
          <div className="text-[11px] font-mono text-slate-400 mt-1 flex items-center justify-between">
            <span>{totalTransactionsCount.toLocaleString()} Transactions</span>
            <span className="text-emerald-400 font-semibold">{yearMin}–{yearMax}</span>
          </div>
        </div>

        {/* Vital 2: Trajectory & Growth */}
        <div className="bg-gradient-to-br from-slate-950 via-[#0b1329] to-[#090e17] rounded-2xl p-4 border border-white/10 shadow-lg text-white flex flex-col justify-between">
          <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mb-1">
            <span className="uppercase tracking-wider">Trajectory CAGR</span>
            <span className="px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-[10px] font-bold">
              YoY Growth
            </span>
          </div>
          <div className="text-2xl font-extrabold font-mono text-cyan-400 tracking-tight">
            +{cagrValue}%
          </div>
          <div className="text-[11px] font-mono text-slate-400 mt-1 flex items-center justify-between">
            <span>Peak Inflection: {peakYear}</span>
            <span className="text-cyan-300 font-semibold">Accelerating</span>
          </div>
        </div>

        {/* Vital 3: Leading Vector */}
        <div className="bg-gradient-to-br from-slate-950 via-[#0b1329] to-[#090e17] rounded-2xl p-4 border border-white/10 shadow-lg text-white flex flex-col justify-between">
          <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mb-1">
            <span className="uppercase tracking-wider">Lead Tech Vector</span>
            <span className="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[10px] font-bold">
              Dominant
            </span>
          </div>
          <div className="text-lg font-bold text-amber-300 truncate mt-0.5" title={topTech.technology}>
            {topTech.technology}
          </div>
          <div className="text-[11px] font-mono text-slate-400 mt-1 flex items-center justify-between">
            <span>{formatSmartCurrency(topTech.total_funding)} Allocations</span>
            <span className="text-amber-400 font-semibold">{topTech.count} Opps</span>
          </div>
        </div>

        {/* Vital 4: Institutional Breadth */}
        <div className="bg-gradient-to-br from-slate-950 via-[#0b1329] to-[#090e17] rounded-2xl p-4 border border-white/10 shadow-lg text-white flex flex-col justify-between">
          <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mb-1">
            <span className="uppercase tracking-wider">Funding Issuers</span>
            <span className="px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-[10px] font-bold">
              Federal &middot; Utility
            </span>
          </div>
          <div className="text-2xl font-extrabold font-mono text-indigo-300 tracking-tight">
            {byAgency?.length ? `${byAgency.length}+ Agencies` : '18+ Active'}
          </div>
          <div className="text-[11px] font-mono text-slate-400 mt-1 flex items-center justify-between">
            <span>Federal, State, 70+ Utilities</span>
            <span className="text-indigo-300 font-semibold">3.8x Match</span>
          </div>
        </div>
      </div>

      {/* ── 3. ZERO-EFFORT EXECUTIVE SYNTHESIS (DIRECTLY VISIBLE TAKEAWAYS) ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="p-4 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10.5px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                Direct Capital Realization
              </span>
              <span className="text-xs font-mono font-bold text-emerald-600 dark:text-emerald-400">$58.1B Real Cash</span>
            </div>
            <h4 className="text-xs font-bold text-slate-900 dark:text-white leading-snug">
              $39.8B Peak Realization (2024) &middot; $12.95B (2025)
            </h4>
            <p className="text-[11.5px] text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">
              Historical BIL/IRA funding achieved peak cashflow execution in 2024 across 2,320 grants, transitioning to focused scale-up capital in 2025.
            </p>
          </div>
        </div>

        <div className="p-4 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10.5px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-cyan-50 dark:bg-cyan-950/60 text-cyan-700 dark:text-cyan-300 border border-cyan-200 dark:border-cyan-800">
                Utility Decentralization
              </span>
              <span className="text-xs font-mono font-bold text-cyan-600 dark:text-cyan-400">70+ Utilities</span>
            </div>
            <h4 className="text-xs font-bold text-slate-900 dark:text-white leading-snug">
              1,398 Project-Level Solicitations Active
            </h4>
            <p className="text-[11.5px] text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">
              Capital deployment has decentralized from central federal hubs into regional utility programs (LADWP, TVA, Con Edison, Rocky Mountain Power).
            </p>
          </div>
        </div>

        <div className="p-4 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10.5px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                Technology Acceleration
              </span>
              <span className="text-xs font-mono font-bold text-indigo-600 dark:text-indigo-400">3.8x Multiplier</span>
            </div>
            <h4 className="text-xs font-bold text-slate-900 dark:text-white leading-snug">
              Storage, Hydrogen &amp; Nuclear Surging
            </h4>
            <p className="text-[11.5px] text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">
              Energy storage and grid modernizations dominate national capital share, followed by high-expansion hydrogen and SMR demonstrations.
            </p>
          </div>
        </div>
      </div>

      {/* ── 4. STREAMLINED COCKPIT CONTROLS & SEGMENT SWITCHER ── */}
      <div className="bg-slate-950 text-white rounded-2xl p-3 sm:p-4 border border-white/10 shadow-xl flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
        
        {/* Left: View Segment Switcher */}
        <div className="flex bg-slate-900/90 p-1 rounded-xl border border-white/10 gap-1 w-full sm:w-auto">
          <button
            onClick={() => setActiveSegment('trajectory')}
            className={clsx(
              "px-3.5 py-2 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-2 cursor-pointer flex-1 sm:flex-initial",
              activeSegment === 'trajectory'
                ? "bg-cyan-400 text-slate-950 font-bold shadow-sm"
                : "text-slate-400 hover:text-white hover:bg-white/5"
            )}
          >
            <TrendingUp size={14} />
            <span>Capital Trajectory &amp; Horizon</span>
          </button>
          <button
            onClick={() => setActiveSegment('technology')}
            className={clsx(
              "px-3.5 py-2 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-2 cursor-pointer flex-1 sm:flex-initial",
              activeSegment === 'technology'
                ? "bg-cyan-400 text-slate-950 font-bold shadow-sm"
                : "text-slate-400 hover:text-white hover:bg-white/5"
            )}
          >
            <Zap size={14} />
            <span>Tech &amp; Sector Radar</span>
          </button>
          <button
            onClick={() => setActiveSegment('institutional')}
            className={clsx(
              "px-3.5 py-2 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-2 cursor-pointer flex-1 sm:flex-initial",
              activeSegment === 'institutional'
                ? "bg-cyan-400 text-slate-950 font-bold shadow-sm"
                : "text-slate-400 hover:text-white hover:bg-white/5"
            )}
          >
            <Building2 size={14} />
            <span>Institutional Matrix</span>
          </button>
        </div>

        {/* Right: Data Mode & Timeframe Presets */}
        <div className="flex flex-wrap items-center gap-2.5 w-full lg:w-auto justify-end">
          
          {/* Data Mode Switcher */}
          <div className="flex bg-slate-900/90 p-1 rounded-xl border border-white/10 gap-1">
            <button
              onClick={() => setCapitalMode('awards')}
              className={clsx(
                "px-2.5 py-1.5 text-[11px] font-semibold rounded-lg transition-all flex items-center gap-1.5 cursor-pointer font-mono",
                capitalMode === 'awards'
                  ? "bg-emerald-500 text-slate-950 font-bold"
                  : "text-slate-400 hover:text-white"
              )}
              title="Verified direct cash grant and contract disbursements"
            >
              <Trophy size={12} className={capitalMode === 'awards' ? "text-slate-950" : "text-emerald-400"} />
              <span>Real Awards ($58.1B)</span>
            </button>
            <button
              onClick={() => setCapitalMode('sanitized')}
              className={clsx(
                "px-2.5 py-1.5 text-[11px] font-semibold rounded-lg transition-all flex items-center gap-1.5 cursor-pointer font-mono",
                capitalMode === 'sanitized'
                  ? "bg-emerald-500 text-slate-950 font-bold"
                  : "text-slate-400 hover:text-white"
              )}
              title="Programmatic solicitation pipeline"
            >
              <FileSearch size={12} className={capitalMode === 'sanitized' ? "text-slate-950" : "text-cyan-400"} />
              <span>Pipeline ($98.9B)</span>
            </button>
          </div>

          {/* Time Horizon Pills */}
          <div className="flex bg-slate-900/90 p-1 rounded-xl border border-white/10 gap-1 text-[11px] font-mono">
            <button
              onClick={() => setTimeframe(2018, 2026)}
              className={clsx(
                "px-2.5 py-1.5 rounded-lg transition-colors cursor-pointer",
                yearMin === 2018 && yearMax === 2026
                  ? "bg-white/20 text-white font-bold"
                  : "text-slate-400 hover:text-white"
              )}
            >
              2018–2026
            </button>
            <button
              onClick={() => setTimeframe(2022, 2026)}
              className={clsx(
                "px-2.5 py-1.5 rounded-lg transition-colors cursor-pointer",
                yearMin === 2022 && yearMax === 2026
                  ? "bg-white/20 text-white font-bold"
                  : "text-slate-400 hover:text-white"
              )}
            >
              IRA Era
            </button>
            <button
              onClick={() => setTimeframe(2024, 2026)}
              className={clsx(
                "px-2.5 py-1.5 rounded-lg transition-colors cursor-pointer",
                yearMin === 2024 && yearMax === 2026
                  ? "bg-white/20 text-white font-bold"
                  : "text-slate-400 hover:text-white"
              )}
            >
              Recent
            </button>
          </div>

          {/* Reset Action */}
          {(selectedTech || selectedAgency || yearMin !== 2018 || yearMax !== 2026 || status !== 'all') && (
            <button
              onClick={resetAllFilters}
              className="px-2.5 py-1.5 text-[11px] font-semibold text-slate-400 hover:text-white bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl transition-colors flex items-center gap-1 cursor-pointer"
              title="Reset to default cockpit view"
            >
              <RefreshCw size={12} className="text-cyan-400" />
              <span>Reset</span>
            </button>
          )}
        </div>
      </div>

      {/* Filter Active Notice Tag */}
      {(selectedTech || selectedAgency) && (
        <div className="flex items-center gap-2 p-2.5 bg-indigo-50 dark:bg-indigo-950/40 rounded-xl border border-indigo-200 dark:border-indigo-800/80 text-xs text-indigo-900 dark:text-indigo-200">
          <span className="font-semibold">Active Filter:</span>
          {selectedTech && (
            <span className="px-2 py-0.5 rounded-md bg-white dark:bg-slate-900 border border-indigo-200 dark:border-indigo-700 flex items-center gap-1">
              Tech: {selectedTech}
              <button onClick={() => setSelectedTech('')} className="hover:text-red-500 cursor-pointer"><X size={12}/></button>
            </span>
          )}
          {selectedAgency && (
            <span className="px-2 py-0.5 rounded-md bg-white dark:bg-slate-900 border border-indigo-200 dark:border-indigo-700 flex items-center gap-1">
              Org: {selectedAgency}
              <button onClick={() => setSelectedAgency('')} className="hover:text-red-500 cursor-pointer"><X size={12}/></button>
            </span>
          )}
        </div>
      )}

      {/* ── 5. COCKPIT INSTRUMENTS: VIEW SEGMENTS ── */}
      
      {/* ── SEGMENT 1: CAPITAL TRAJECTORY & HORIZON ── */}
      {activeSegment === 'trajectory' && (
        <div className="space-y-5 animate-in fade-in duration-200">
          
          {/* Main Instrument: Longitudinal Capital Trajectory Area Chart */}
          <CockpitCard
            id="cockpit-trajectory"
            title={capitalMode === 'awards' ? "Longitudinal Award Disbursements Over Time" : "Longitudinal Solicitation Pipeline Trajectory"}
            subtitle={`Tracking total capital volume ($) and transaction counts (#) across ${yearMin} - ${yearMax}`}
            badge={capitalMode === 'awards' ? "Direct Cashflow" : "Programmatic Pipeline"}
            exportCsvData={overview || []}
            minHeight="min-h-[350px]"
          >
            {!overview || overview.length === 0 ? (
              <div className="absolute inset-0 flex items-center justify-center text-slate-400 text-xs">No telemetry data available for selected horizon</div>
            ) : (
              <ResponsiveContainer width="100%" height={340}>
                <AreaChart data={overview} margin={{ top: 15, right: 35, left: 60, bottom: 20 }}>
                  <defs>
                    <linearGradient id="cockpitFundingGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={capitalMode === 'awards' ? '#10b981' : '#06b6d4'} stopOpacity={0.45}/>
                      <stop offset="50%" stopColor="#4f46e5" stopOpacity={0.15}/>
                      <stop offset="95%" stopColor="#4f46e5" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="cockpitCountGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.35}/>
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" opacity={0.6} />
                  <XAxis dataKey="year" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} dy={10} />
                  <YAxis yAxisId="left" tickFormatter={(val) => formatSmartCurrency(val)} axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} dx={-10} />
                  <YAxis yAxisId="right" orientation="right" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} dx={10} />
                  <Tooltip
                    content={<CockpitTooltip formatter={(val: any, name: any) => [
                      name === 'total_funding' ? formatSmartCurrency(val) : val?.toLocaleString(),
                      name === 'total_funding' ? (capitalMode === 'awards' ? 'Executed Realized Funding' : 'Program Pipeline Budget') : (capitalMode === 'awards' ? 'Executed Awards Count' : 'Opportunities Count')
                    ]} />}
                  />
                  <Area
                    yAxisId="left"
                    type="monotone"
                    dataKey="total_funding"
                    name="total_funding"
                    stroke={capitalMode === 'awards' ? '#10b981' : '#06b6d4'}
                    strokeWidth={2.5}
                    fillOpacity={1}
                    fill="url(#cockpitFundingGrad)"
                    activeDot={{ r: 6, fill: capitalMode === 'awards' ? '#10b981' : '#06b6d4', stroke: '#ffffff', strokeWidth: 2 }}
                  />
                  <Area
                    yAxisId="right"
                    type="monotone"
                    dataKey="count"
                    name="count"
                    stroke="#8b5cf6"
                    strokeWidth={2}
                    fill="url(#cockpitCountGrad)"
                    activeDot={{ r: 5, fill: '#8b5cf6', stroke: '#ffffff', strokeWidth: 2 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </CockpitCard>

          {/* Sub-Instruments: Comparative Matrix + Ticket Size Scale */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {/* Comparative Matrix */}
            <CockpitCard
              id="cockpit-comparison"
              title="Realized Cash Awards vs. Pipeline Budget"
              subtitle="Conversion ratio of realized cash vs. solicitation target"
              badge="Realization Ratio"
              exportCsvData={comparisonData || []}
              minHeight="min-h-[300px]"
            >
              {!comparisonData || comparisonData.length === 0 ? (
                <div className="absolute inset-0 flex items-center justify-center text-slate-400 text-xs">No comparative data</div>
              ) : (
                <ResponsiveContainer width="100%" height={290}>
                  <BarChart data={comparisonData} margin={{ top: 15, right: 20, left: 60, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" opacity={0.6} />
                    <XAxis dataKey="year" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} dy={10} />
                    <YAxis tickFormatter={(val) => formatSmartCurrency(val)} axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} dx={-10} />
                    <Tooltip
                      content={<CockpitTooltip formatter={(val: any, name: any) => [
                        formatSmartCurrency(val),
                        name === 'award_funding' ? 'Executed Awards ($)' : 'Pipeline Solicitations ($)'
                      ]} />}
                    />
                    <Bar dataKey="award_funding" name="award_funding" fill="#10b981" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="pipeline_funding" name="pipeline_funding" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </CockpitCard>

            {/* Ticket Size Bracket Breakdown */}
            <CockpitCard
              id="cockpit-amounts"
              title="Capital Scale &amp; Award Ticket Size Distribution"
              subtitle="Dispersion across seed, scale-up, and infrastructure mega-grants"
              badge="Ticket Sizes"
              exportCsvData={amounts || []}
              minHeight="min-h-[300px]"
            >
              {!amounts || amounts.length === 0 ? (
                <div className="absolute inset-0 flex items-center justify-center text-slate-400 text-xs">No ticket distribution data</div>
              ) : (
                <ResponsiveContainer width="100%" height={290}>
                  <BarChart data={amounts} margin={{ top: 15, right: 20, left: 20, bottom: 40 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" opacity={0.6} />
                    <XAxis dataKey="bucket" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} angle={-35} textAnchor="end" dy={8} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} dx={-10} />
                    <Tooltip
                      content={<CockpitTooltip formatter={(val: any) => [val?.toLocaleString(), 'Opportunities']} />}
                    />
                    <Bar dataKey="count" name="count" fill="#8b5cf6" radius={[6, 6, 0, 0]}>
                      {amounts.map((_, index) => (
                        <Cell key={`cell-amt-${index}`} fill={COCKPIT_COLORS[index % COCKPIT_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </CockpitCard>
          </div>
        </div>
      )}

      {/* ── SEGMENT 2: TECHNOLOGY & SECTOR RADAR ── */}
      {activeSegment === 'technology' && (
        <div className="space-y-5 animate-in fade-in duration-200">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            
            {/* Tech Breakdown */}
            <CockpitCard
              id="cockpit-tech"
              title="Clean Technology Portfolio Distribution"
              subtitle="Click any technology vector to filter entire telemetry"
              badge="Top 12 Technologies"
              exportCsvData={byTech || []}
              headerAction={
                <div className="flex bg-slate-100 dark:bg-slate-800 p-0.5 rounded-md text-[10px] font-semibold">
                  <button
                    onClick={() => setTechMetric('total_funding')}
                    className={clsx("px-2 py-0.5 rounded cursor-pointer", techMetric === 'total_funding' ? "bg-white dark:bg-slate-700 text-indigo-700 dark:text-indigo-300 font-bold shadow-2xs" : "text-slate-500")}
                  >
                    Funding ($)
                  </button>
                  <button
                    onClick={() => setTechMetric('count')}
                    className={clsx("px-2 py-0.5 rounded cursor-pointer", techMetric === 'count' ? "bg-white dark:bg-slate-700 text-indigo-700 dark:text-indigo-300 font-bold shadow-2xs" : "text-slate-500")}
                  >
                    Count (#)
                  </button>
                </div>
              }
              minHeight="min-h-[360px]"
            >
              {!byTech || byTech.length === 0 ? (
                <div className="absolute inset-0 flex items-center justify-center text-slate-400 text-xs">No tech portfolio data</div>
              ) : (
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={byTech} layout="vertical" margin={{ left: 110, right: 25, top: 10, bottom: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#e2e8f0" opacity={0.6} />
                    <XAxis type="number" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} tickFormatter={(val) => techMetric === 'total_funding' ? formatSmartCurrency(val) : val} />
                    <YAxis dataKey="technology" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#334155', fontWeight: 600 }} width={105} />
                    <Tooltip
                      content={<CockpitTooltip formatter={(val: any) => [techMetric === 'total_funding' ? formatSmartCurrency(val) : val?.toLocaleString(), techMetric === 'total_funding' ? 'Total Funding' : 'Opportunities']} />}
                    />
                    <Bar
                      dataKey={techMetric}
                      radius={[0, 6, 6, 0]}
                      onClick={(data: any) => data?.technology && setSelectedTech(data.technology === selectedTech ? '' : data.technology)}
                      className="cursor-pointer hover:opacity-85 transition-opacity"
                    >
                      {byTech.map((entry: any, index: number) => (
                        <Cell
                          key={`cell-tech-${index}`}
                          fill={selectedTech === entry.technology ? '#06b6d4' : COCKPIT_COLORS[(index + 1) % COCKPIT_COLORS.length]}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </CockpitCard>

            {/* Sector Breakdown */}
            <CockpitCard
              id="cockpit-sector"
              title="Industry &amp; Infrastructure Sectors"
              subtitle="Capital allocations across cross-cutting end-use sectors"
              badge="Sector Shares"
              exportCsvData={bySector || []}
              headerAction={
                <div className="flex bg-slate-100 dark:bg-slate-800 p-0.5 rounded-md text-[10px] font-semibold">
                  <button
                    onClick={() => setSectorMetric('total_funding')}
                    className={clsx("px-2 py-0.5 rounded cursor-pointer", sectorMetric === 'total_funding' ? "bg-white dark:bg-slate-700 text-indigo-700 dark:text-indigo-300 font-bold shadow-2xs" : "text-slate-500")}
                  >
                    Funding ($)
                  </button>
                  <button
                    onClick={() => setSectorMetric('count')}
                    className={clsx("px-2 py-0.5 rounded cursor-pointer", sectorMetric === 'count' ? "bg-white dark:bg-slate-700 text-indigo-700 dark:text-indigo-300 font-bold shadow-2xs" : "text-slate-500")}
                  >
                    Count (#)
                  </button>
                </div>
              }
              minHeight="min-h-[360px]"
            >
              {!bySector || bySector.length === 0 ? (
                <div className="absolute inset-0 flex items-center justify-center text-slate-400 text-xs">No sector allocation data</div>
              ) : (
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={bySector} layout="vertical" margin={{ left: 110, right: 25, top: 10, bottom: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#e2e8f0" opacity={0.6} />
                    <XAxis type="number" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} tickFormatter={(val) => sectorMetric === 'total_funding' ? formatSmartCurrency(val) : val} />
                    <YAxis dataKey="sector" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#334155', fontWeight: 600 }} width={105} />
                    <Tooltip
                      content={<CockpitTooltip formatter={(val: any) => [sectorMetric === 'total_funding' ? formatSmartCurrency(val) : val?.toLocaleString(), sectorMetric === 'total_funding' ? 'Total Funding' : 'Opportunities']} />}
                    />
                    <Bar dataKey={sectorMetric} radius={[0, 6, 6, 0]} className="cursor-pointer hover:opacity-85 transition-opacity">
                      {bySector.map((_, index) => (
                        <Cell key={`cell-sec-${index}`} fill={COCKPIT_COLORS[(index + 3) % COCKPIT_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </CockpitCard>

          </div>

          {/* Clean Fuel & Energy Resource Allocations */}
          <CockpitCard
            id="cockpit-fuel"
            title="Clean Fuel &amp; Energy Carrier Trajectory"
            subtitle="Distribution across primary energy innovation carriers (Hydrogen, Electricity, Biofuels, Nuclear)"
            badge="Carrier Allocations"
            exportCsvData={byFuel || []}
            minHeight="min-h-[260px]"
          >
            {!byFuel || byFuel.length === 0 ? (
              <div className="absolute inset-0 flex items-center justify-center text-slate-400 text-xs">No fuel carrier data</div>
            ) : (
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={byFuel} margin={{ top: 15, right: 25, left: 60, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" opacity={0.6} />
                  <XAxis dataKey="fuel" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} dy={10} />
                  <YAxis tickFormatter={(val) => formatSmartCurrency(val)} axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} dx={-10} />
                  <Tooltip
                    content={<CockpitTooltip formatter={(val: any, name: any) => [formatSmartCurrency(val), 'Capital Deployed']} />}
                  />
                  <Bar dataKey="total_funding" name="total_funding" fill="#10b981" radius={[6, 6, 0, 0]}>
                    {byFuel.map((_, index) => (
                      <Cell key={`cell-fuel-${index}`} fill={COCKPIT_COLORS[(index + 4) % COCKPIT_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </CockpitCard>
        </div>
      )}

      {/* ── SEGMENT 3: INSTITUTIONAL & CORRELATION MATRIX ── */}
      {activeSegment === 'institutional' && (
        <div className="space-y-5 animate-in fade-in duration-200">
          
          {/* Funding Organization Leaderboard */}
          <CockpitCard
            id="cockpit-agency"
            title="Funding Organization Leaderboard"
            subtitle="Federal agencies, state energy authorities, utilities &amp; philanthropic institutions"
            badge="Top 15 Issuers"
            exportCsvData={byAgency || []}
            headerAction={
              <div className="flex bg-slate-100 dark:bg-slate-800 p-0.5 rounded-md text-[10px] font-semibold">
                <button
                  onClick={() => setAgencyMetric('total_funding')}
                  className={clsx("px-2 py-0.5 rounded cursor-pointer", agencyMetric === 'total_funding' ? "bg-white dark:bg-slate-700 text-indigo-700 dark:text-indigo-300 font-bold shadow-2xs" : "text-slate-500")}
                >
                  Funding ($)
                </button>
                <button
                  onClick={() => setAgencyMetric('count')}
                  className={clsx("px-2 py-0.5 rounded cursor-pointer", agencyMetric === 'count' ? "bg-white dark:bg-slate-700 text-indigo-700 dark:text-indigo-300 font-bold shadow-2xs" : "text-slate-500")}
                >
                  Count (#)
                </button>
              </div>
            }
            minHeight="min-h-[360px]"
          >
            {!byAgency || byAgency.length === 0 ? (
              <div className="absolute inset-0 flex items-center justify-center text-slate-400 text-xs">No organization data</div>
            ) : (
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={byAgency} layout="vertical" margin={{ left: 110, right: 25, top: 10, bottom: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#e2e8f0" opacity={0.6} />
                  <XAxis type="number" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} tickFormatter={(val) => agencyMetric === 'total_funding' ? formatSmartCurrency(val) : val} />
                  <YAxis
                    dataKey="agency"
                    type="category"
                    axisLine={false}
                    tickLine={false}
                    width={105}
                    tick={({ x, y, payload }: any) => (
                      <g transform={`translate(${x},${y})`}>
                        <foreignObject x={-105} y={-10} width={100} height={20}>
                          <div className="flex items-center justify-end gap-1 w-full h-full text-[11px] font-semibold text-slate-700 dark:text-slate-300 pr-1">
                            <span className="truncate">{payload.value}</span>
                            <OrgLogo org={payload.value} size="xs" showTooltip={false} />
                          </div>
                        </foreignObject>
                      </g>
                    )}
                  />
                  <Tooltip
                    content={<CockpitTooltip formatter={(val: any) => [agencyMetric === 'total_funding' ? formatSmartCurrency(val) : val?.toLocaleString(), agencyMetric === 'total_funding' ? 'Total Capital' : 'Opportunities']} />}
                  />
                  <Bar
                    dataKey={agencyMetric}
                    radius={[0, 6, 6, 0]}
                    onClick={(data: any) => data?.agency && setSelectedAgency(data.agency === selectedAgency ? '' : data.agency)}
                    className="cursor-pointer hover:opacity-85 transition-opacity"
                  >
                    {byAgency.map((entry: any, index: number) => (
                      <Cell
                        key={`cell-org-${index}`}
                        fill={selectedAgency === entry.agency ? '#10b981' : COCKPIT_COLORS[index % COCKPIT_COLORS.length]}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </CockpitCard>

          {/* 2D Intensity Correlation Matrix */}
          <CockpitCard
            id="cockpit-heatmap"
            title="2D Cross-Dimensional Intensity Matrix"
            subtitle="Cross-variable capital concentration and co-occurrence patterns"
            badge="Intensity Matrix"
            exportCsvData={heatmap || []}
            headerAction={
              <div className="flex items-center gap-2">
                <div className="flex bg-slate-100 dark:bg-slate-800 p-0.5 rounded-md text-[10px] font-semibold">
                  <button
                    onClick={() => setHeatmapPreset('agency-tech')}
                    className={clsx("px-2 py-0.5 rounded cursor-pointer", heatmapPreset === 'agency-tech' ? "bg-white dark:bg-slate-700 text-indigo-700 dark:text-indigo-300 font-bold shadow-2xs" : "text-slate-500")}
                  >
                    Org &times; Tech
                  </button>
                  <button
                    onClick={() => setHeatmapPreset('tech-sector')}
                    className={clsx("px-2 py-0.5 rounded cursor-pointer", heatmapPreset === 'tech-sector' ? "bg-white dark:bg-slate-700 text-indigo-700 dark:text-indigo-300 font-bold shadow-2xs" : "text-slate-500")}
                  >
                    Tech &times; Sector
                  </button>
                  <button
                    onClick={() => setHeatmapPreset('sector-fuel')}
                    className={clsx("px-2 py-0.5 rounded cursor-pointer", heatmapPreset === 'sector-fuel' ? "bg-white dark:bg-slate-700 text-indigo-700 dark:text-indigo-300 font-bold shadow-2xs" : "text-slate-500")}
                  >
                    Sector &times; Fuel
                  </button>
                </div>

                <div className="flex bg-slate-100 dark:bg-slate-800 p-0.5 rounded-md text-[10px] font-semibold">
                  <button
                    onClick={() => setHeatmapMetric('total_funding')}
                    className={clsx("px-2 py-0.5 rounded cursor-pointer", heatmapMetric === 'total_funding' ? "bg-white dark:bg-slate-700 text-indigo-700 dark:text-indigo-300 font-bold shadow-2xs" : "text-slate-500")}
                  >
                    $ Funding
                  </button>
                  <button
                    onClick={() => setHeatmapMetric('count')}
                    className={clsx("px-2 py-0.5 rounded cursor-pointer", heatmapMetric === 'count' ? "bg-white dark:bg-slate-700 text-indigo-700 dark:text-indigo-300 font-bold shadow-2xs" : "text-slate-500")}
                  >
                    # Count
                  </button>
                </div>
              </div>
            }
            minHeight="min-h-[300px]"
          >
            <div className="overflow-x-auto pb-3">
              <div className="min-w-[620px]">
                {/* Heatmap Column Headers */}
                <div className="flex">
                  <div className="w-28 shrink-0"></div>
                  {heatmapCols.map((col: string) => (
                    <div key={col} className="flex-1 flex items-center justify-center gap-1 text-center truncate px-1 text-[11px] font-semibold text-slate-700 dark:text-slate-300 pb-2 border-b border-slate-200 dark:border-slate-800" title={col}>
                      {heatmapConfig.cols === 'agency' && <OrgLogo org={col} size="xs" showTooltip={false} />}
                      <span className="truncate">{col.length > 14 ? col.substring(0, 14) + '...' : col}</span>
                    </div>
                  ))}
                </div>
                
                {/* Heatmap Rows */}
                {heatmapRows.map((row: string) => (
                  <div key={row} className="flex items-center mt-1 border-b border-slate-100 dark:border-slate-800/60">
                    <div className="w-28 shrink-0 text-[11px] font-semibold text-slate-800 dark:text-slate-200 truncate pr-3 text-right flex items-center justify-end gap-1" title={row}>
                      <span className="truncate">{row}</span>
                      {heatmapConfig.rows === 'agency' && <OrgLogo org={row} size="xs" showTooltip={false} />}
                    </div>
                    {heatmapCols.map((col: string) => {
                      const match = heatmap?.find((d: any) => d.row === row && d.col === col);
                      const val = match?.value || 0;
                      return (
                        <div
                          key={`${row}-${col}`}
                          className="flex-1 h-10 border border-white/60 dark:border-slate-900/60 flex items-center justify-center rounded-md transition-all hover:scale-105 hover:z-20 hover:ring-2 hover:ring-cyan-500 cursor-pointer group relative m-[1px] shadow-2xs"
                          style={{ backgroundColor: getHeatmapColor(val, maxHeatmapVal) }}
                        >
                          {val > 0 && (
                            <span className={clsx(
                              "text-[10px] font-mono font-bold",
                              val > (maxHeatmapVal / 2) ? "text-white" : "text-slate-900 dark:text-slate-950"
                            )}>
                              {heatmapMetric === 'total_funding' ? formatSmartCurrency(val) : val.toLocaleString()}
                            </span>
                          )}
                          <div className="absolute hidden group-hover:block bottom-full left-1/2 -translate-x-1/2 mb-1 z-30 bg-slate-950 text-white text-[11px] font-mono px-3 py-1.5 rounded-lg shadow-xl whitespace-nowrap pointer-events-none border border-white/10 backdrop-blur-sm">
                            <span className="font-bold text-amber-300">{row}</span> &times; <span className="font-bold text-cyan-300">{col}</span>: {heatmapMetric === 'total_funding' ? formatSmartCurrency(val) : `${val.toLocaleString()} Opps`}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>

            {/* Heatmap Legend */}
            <div className="flex items-center justify-end gap-2 mt-3 text-[11px] font-mono text-slate-500">
              <span>Low</span>
              <div className="w-28 h-2.5 rounded-full bg-gradient-to-r from-slate-100 via-sky-400 to-[#1e1b4b] border border-slate-200 dark:border-slate-700 shadow-2xs"></div>
              <span className="font-bold text-slate-700 dark:text-slate-300">Peak ({heatmapMetric === 'total_funding' ? formatSmartCurrency(maxHeatmapVal) : maxHeatmapVal})</span>
            </div>
          </CockpitCard>
        </div>
      )}

      {/* ── 6. EXECUTIVE DOSSIER BRIEFING MODAL ── */}
      {briefingOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-2xl w-full max-w-3xl max-h-[85vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            
            <div className="p-4 sm:p-5 bg-gradient-to-r from-slate-950 via-[#0b1329] to-[#090e17] text-white flex items-center justify-between border-b border-white/10">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-amber-400/20 rounded-xl border border-amber-400/30">
                  <TrendingUp size={20} className="text-amber-300" />
                </div>
                <div>
                  <h2 className="text-base font-bold tracking-tight">Macro Trend Executive Intelligence Dossier</h2>
                  <p className="text-[12px] text-indigo-200">Longitudinal capital realization, sector distribution &amp; innovation drivers</p>
                </div>
              </div>
              <button
                onClick={() => setBriefingOpen(false)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
              >
                <X size={18} />
              </button>
            </div>

            <div className="p-5 overflow-y-auto space-y-5 text-xs leading-relaxed text-slate-700 dark:text-slate-300">
              
              {/* Summary Stats Strip */}
              <div className="grid grid-cols-3 gap-3 p-3 bg-slate-50 dark:bg-slate-950/50 rounded-xl border border-slate-200 dark:border-slate-800 text-center font-mono">
                <div>
                  <div className="text-[10px] text-slate-400 uppercase">Realized Capital</div>
                  <div className="text-sm font-bold text-emerald-600 dark:text-emerald-400 font-mono mt-0.5">$58.1B Real Cash</div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-400 uppercase">Multi-Year CAGR</div>
                  <div className="text-sm font-bold text-cyan-600 dark:text-cyan-400 font-mono mt-0.5">+{cagrValue}% YoY</div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-400 uppercase">Peak Execution</div>
                  <div className="text-sm font-bold text-amber-600 dark:text-amber-400 font-mono mt-0.5">Year {peakYear}</div>
                </div>
              </div>

              {/* Discoveries List */}
              <div className="space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white flex items-center gap-1.5">
                  <Activity size={14} className="text-indigo-600" />
                  Key Structural Discoveries
                </h3>

                {analyticsData?.insights?.map((ins: any, idx: number) => (
                  <div key={idx} className="p-3.5 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700/80 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-indigo-100 dark:bg-indigo-950 text-indigo-800 dark:text-indigo-300">
                        {ins.category}
                      </span>
                      {ins.metric && (
                        <span className="text-[10px] font-bold font-mono px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">
                          {ins.metric}
                        </span>
                      )}
                    </div>
                    <div className="font-bold text-slate-900 dark:text-white text-xs">{ins.title}</div>
                    <p className="text-slate-600 dark:text-slate-400 text-[11.5px] leading-relaxed">{ins.description}</p>
                  </div>
                ))}
              </div>

            </div>

            <div className="p-3 bg-slate-50 dark:bg-slate-950/80 border-t border-slate-200 dark:border-slate-800 flex justify-end">
              <button
                onClick={() => setBriefingOpen(false)}
                className="px-4 py-1.5 text-xs font-semibold rounded-lg bg-slate-900 text-white dark:bg-white dark:text-slate-950 hover:bg-slate-800 cursor-pointer"
              >
                Close Briefing
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}
