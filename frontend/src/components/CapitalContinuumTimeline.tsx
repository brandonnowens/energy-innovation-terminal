import React, { useState, useMemo, useRef } from 'react';
import { scaleTime, scaleLinear } from 'd3-scale';
import { min, max } from 'd3-array';
import { area, curveStepAfter } from 'd3-shape';
import { 
  Award, DollarSign, TrendingUp, Zap, ShieldCheck, 
  Lightbulb, ExternalLink, Calendar, Layers, CheckCircle2,
  Info, Eye, EyeOff, Filter
} from 'lucide-react';
import { RecipientCapitalContinuumResponse } from '../api/client';

interface CapitalContinuumTimelineProps {
  continuum: RecipientCapitalContinuumResponse;
  recipientName?: string;
}

export type TrackType = 'grant' | 'sec_filing' | 'vc_round' | 'scaleup' | 'procurement' | 'patent';

export interface TimelineMilestone {
  id: string;
  track: TrackType;
  trackLabel: string;
  date: Date;
  dateStr: string;
  title: string;
  subtitle: string;
  amountUsd?: number;
  badge?: string;
  color: string;
  bgColor: string;
  borderColor: string;
  details?: Record<string, any>;
  externalUrl?: string;
}

function fmt(val: number | null | undefined): string {
  if (!val) return '$0';
  if (val >= 1_000_000_000) return `$${(val / 1_000_000_000).toFixed(2)}B`;
  if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(1)}M`;
  if (val >= 1_000) return `$${(val / 1_000).toFixed(0)}K`;
  return `$${val.toLocaleString()}`;
}

function formatDate(date: Date): string {
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
}

const TRACK_CONFIG: Record<TrackType, {
  label: string;
  color: string;
  hex: string;
  bgHex: string;
  borderHex: string;
  icon: React.ElementType;
}> = {
  grant: {
    label: 'Public Grants & Awards',
    color: 'cyan',
    hex: '#06b6d4',
    bgHex: 'rgba(6, 182, 212, 0.15)',
    borderHex: 'rgba(6, 182, 212, 0.4)',
    icon: Award,
  },
  sec_filing: {
    label: 'SEC Form D Reg D Offerings',
    color: 'amber',
    hex: '#f59e0b',
    bgHex: 'rgba(245, 158, 11, 0.15)',
    borderHex: 'rgba(245, 158, 11, 0.4)',
    icon: DollarSign,
  },
  vc_round: {
    label: 'Venture Capital & Equity',
    color: 'emerald',
    hex: '#10b981',
    bgHex: 'rgba(16, 185, 129, 0.15)',
    borderHex: 'rgba(16, 185, 129, 0.4)',
    icon: TrendingUp,
  },
  scaleup: {
    label: 'Scale-Up Facilities (LPO / 48C)',
    color: 'purple',
    hex: '#a855f7',
    bgHex: 'rgba(168, 85, 247, 0.15)',
    borderHex: 'rgba(168, 85, 247, 0.4)',
    icon: Zap,
  },
  procurement: {
    label: 'Federal Procurement & Offtake',
    color: 'indigo',
    hex: '#6366f1',
    bgHex: 'rgba(99, 102, 241, 0.15)',
    borderHex: 'rgba(99, 102, 241, 0.4)',
    icon: ShieldCheck,
  },
  patent: {
    label: 'Commercial IP & Patents',
    color: 'rose',
    hex: '#f43f5e',
    bgHex: 'rgba(244, 63, 94, 0.15)',
    borderHex: 'rgba(244, 63, 94, 0.4)',
    icon: Lightbulb,
  },
};

export const CapitalContinuumTimeline: React.FC<CapitalContinuumTimelineProps> = ({
  continuum,
  recipientName = 'Innovator'
}) => {
  const [activeTracks, setActiveTracks] = useState<Record<TrackType, boolean>>({
    grant: true,
    sec_filing: true,
    vc_round: true,
    scaleup: true,
    procurement: true,
    patent: true,
  });

  const [hoveredNode, setHoveredNode] = useState<TimelineMilestone | null>(null);
  const [popoverPos, setPopoverPos] = useState<{ x: number; y: number } | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Toggle single track
  const toggleTrack = (track: TrackType) => {
    setActiveTracks(prev => ({ ...prev, [track]: !prev[track] }));
  };

  // Select all or isolate
  const toggleAllTracks = () => {
    const allActive = Object.values(activeTracks).every(Boolean);
    const nextVal = !allActive;
    setActiveTracks({
      grant: nextVal,
      sec_filing: nextVal,
      vc_round: nextVal,
      scaleup: nextVal,
      procurement: nextVal,
      patent: nextVal,
    });
  };

  // Flatten and normalize all continuum milestones
  const allMilestones: TimelineMilestone[] = useMemo(() => {
    if (!continuum) return [];
    const list: TimelineMilestone[] = [];

    // 1. Grants
    (continuum.grants || []).forEach((g, idx) => {
      const d = g.award_date ? new Date(g.award_date) : new Date('2022-01-01');
      if (!isNaN(d.getTime())) {
        list.push({
          id: `grant-${g.id || idx}`,
          track: 'grant',
          trackLabel: 'Public Grant Award',
          date: d,
          dateStr: g.award_date || 'N/A',
          title: g.project_title || 'Clean Energy Demonstration',
          subtitle: `${g.agency || 'Public Agency'} · ${g.solicitation_number || 'Grant'}`,
          amountUsd: g.award_amount || 0,
          badge: g.agency,
          color: TRACK_CONFIG.grant.hex,
          bgColor: TRACK_CONFIG.grant.bgHex,
          borderColor: TRACK_CONFIG.grant.borderHex,
          details: {
            'Award Amount': fmt(g.award_amount),
            'Agency': g.agency,
            'Solicitation / ID': g.solicitation_number,
          }
        });
      }
    });

    // 2. SEC Form D
    (continuum.sec_form_d_filings || []).forEach((s, idx) => {
      const d = s.filing_date ? new Date(s.filing_date) : new Date('2023-01-01');
      if (!isNaN(d.getTime())) {
        list.push({
          id: `sec-${s.id || idx}`,
          track: 'sec_filing',
          trackLabel: 'SEC Form D Offering',
          date: d,
          dateStr: s.filing_date || 'N/A',
          title: `Reg D Offering (${s.is_equity ? 'Equity' : 'Debt/Other'})`,
          subtitle: `CIK #${s.cik} · ${s.num_investors || 1} Investors`,
          amountUsd: s.amount_sold_usd || 0,
          badge: 'SEC EDGAR',
          color: TRACK_CONFIG.sec_filing.hex,
          bgColor: TRACK_CONFIG.sec_filing.bgHex,
          borderColor: TRACK_CONFIG.sec_filing.borderHex,
          externalUrl: s.sec_url || undefined,
          details: {
            'Amount Sold': fmt(s.amount_sold_usd),
            'CIK Number': s.cik,
            'Filing Type': s.is_equity ? 'Rule 506(b)/(c) Equity' : 'Securities Offering',
            'Investors': s.num_investors || 'Confidential',
          }
        });
      }
    });

    // 3. VC Rounds
    (continuum.vc_rounds || []).forEach((v, idx) => {
      const d = v.round_date ? new Date(v.round_date) : new Date('2023-06-01');
      if (!isNaN(d.getTime())) {
        list.push({
          id: `vc-${v.id || idx}`,
          track: 'vc_round',
          trackLabel: 'Venture Capital Financing',
          date: d,
          dateStr: v.round_date || 'N/A',
          title: `${v.round_type || 'Equity'} Round`,
          subtitle: v.lead_investor ? `Lead: ${v.lead_investor}` : 'Private Syndicate',
          amountUsd: v.amount_usd || 0,
          badge: v.round_type || 'Venture',
          color: TRACK_CONFIG.vc_round.hex,
          bgColor: TRACK_CONFIG.vc_round.bgHex,
          borderColor: TRACK_CONFIG.vc_round.borderHex,
          details: {
            'Round Amount': fmt(v.amount_usd),
            'Round Series': v.round_type,
            'Lead Investor': v.lead_investor || 'Syndicate',
            'Participating Investors': (v.investors || []).join(', ') || 'Syndicate Partners',
          }
        });
      }
    });

    // 4. Scale-Up Facilities
    (continuum.scaleup_allocations || []).forEach((sc, idx) => {
      const d = new Date('2024-03-15');
      list.push({
        id: `scaleup-${sc.id || idx}`,
        track: 'scaleup',
        trackLabel: 'Scale-Up Facility Allocation',
        date: d,
        dateStr: '2024-03-15',
        title: sc.facility_name || 'Commercial Scale-Up Facility',
        subtitle: `${sc.program_category || 'DOE LPO / 48C'} · ${sc.status || 'Active'}`,
        amountUsd: sc.allocation_amount_usd || 0,
        badge: sc.program_category || 'LPO',
        color: TRACK_CONFIG.scaleup.hex,
        bgColor: TRACK_CONFIG.scaleup.bgHex,
        borderColor: TRACK_CONFIG.scaleup.borderHex,
        details: {
          'Allocation Value': fmt(sc.allocation_amount_usd),
          'Total CapEx': fmt(sc.total_capex_usd),
          'Facility': sc.facility_name,
          'Jobs Created': sc.jobs ? `${sc.jobs} FTEs` : 'Reported',
          'Status': sc.status,
        }
      });
    });

    // 5. Procurement Contracts
    (continuum.procurement_contracts || []).forEach((pr, idx) => {
      const d = pr.signed_date ? new Date(pr.signed_date) : new Date('2024-08-01');
      if (!isNaN(d.getTime())) {
        list.push({
          id: `proc-${pr.id || idx}`,
          track: 'procurement',
          trackLabel: 'Federal Procurement Offtake',
          date: d,
          dateStr: pr.signed_date || 'N/A',
          title: `Federal Contract #${pr.contract_number}`,
          subtitle: `${pr.agency || 'Federal Agency'}${pr.is_sbir_phase_3 ? ' · SBIR Phase III' : ''}`,
          amountUsd: pr.obligated_amount_usd || 0,
          badge: pr.is_sbir_phase_3 ? 'Phase III' : 'FPDS Offtake',
          color: TRACK_CONFIG.procurement.hex,
          bgColor: TRACK_CONFIG.procurement.bgHex,
          borderColor: TRACK_CONFIG.procurement.borderHex,
          details: {
            'Obligated Capital': fmt(pr.obligated_amount_usd),
            'Agency': pr.agency,
            'Contract': pr.contract_number,
            'Classification': pr.is_sbir_phase_3 ? 'SBIR Phase III Commercialization' : 'Direct Agency Offtake',
          }
        });
      }
    });

    // 6. Patents & Commercial IP
    (continuum.patents || []).forEach((p, idx) => {
      const d = p.grant_date ? new Date(p.grant_date) : new Date('2022-08-15');
      if (!isNaN(d.getTime())) {
        list.push({
          id: `pat-${p.id || idx}`,
          track: 'patent',
          trackLabel: 'USPTO Patent Issued',
          date: d,
          dateStr: p.grant_date || 'N/A',
          title: p.title || `US Patent #${p.patent_number}`,
          subtitle: `Patent #${p.patent_number}${p.bayh_dole_citation ? ' · Bayh-Dole Gov Interest' : ''}`,
          badge: p.bayh_dole_citation ? 'Bayh-Dole IP' : 'USPTO IP',
          color: TRACK_CONFIG.patent.hex,
          bgColor: TRACK_CONFIG.patent.bgHex,
          borderColor: TRACK_CONFIG.patent.borderHex,
          details: {
            'Patent Number': p.patent_number,
            'Title': p.title,
            'Grant Date': p.grant_date,
            'Bayh-Dole Citation': p.bayh_dole_citation || 'Commercial Proprietary',
            'Forward Citations': p.cited_by_count ? `${p.cited_by_count} Citations` : 'Active',
          }
        });
      }
    });

    // Sort chronologically
    return list.sort((a, b) => a.date.getTime() - b.date.getTime());
  }, [continuum]);

  // Filtered milestones based on track toggles
  const filteredMilestones = useMemo(() => {
    return allMilestones.filter(m => activeTracks[m.track]);
  }, [allMilestones, activeTracks]);

  // Timeline Dimensions
  const svgWidth = 980;
  const svgHeight = 440;
  const margin = { top: 35, right: 40, bottom: 45, left: 60 };
  const innerWidth = svgWidth - margin.left - margin.right;
  const innerHeight = svgHeight - margin.top - margin.bottom;

  // Active Tracks Ordering & Heights
  const activeTrackKeys = (Object.keys(TRACK_CONFIG) as TrackType[]).filter(t => activeTracks[t]);
  const trackCount = Math.max(activeTrackKeys.length, 1);
  const trackHeight = Math.min(52, innerHeight / (trackCount + 0.8));

  // Time Domain Calculation
  const { timeScale, timeTicks, minDate, maxDate } = useMemo(() => {
    if (allMilestones.length === 0) {
      const now = new Date();
      const start = new Date(now.getFullYear() - 3, 0, 1);
      const end = new Date(now.getFullYear() + 1, 0, 1);
      return {
        timeScale: scaleTime().domain([start, end]).range([0, innerWidth]),
        timeTicks: [start, now, end],
        minDate: start,
        maxDate: end,
      };
    }

    const rawMin = min(allMilestones, d => d.date) || new Date('2020-01-01');
    const rawMax = max(allMilestones, d => d.date) || new Date();

    // Pad by 4 months before and 6 months after
    const start = new Date(rawMin.getFullYear(), rawMin.getMonth() - 4, 1);
    const end = new Date(rawMax.getFullYear(), rawMax.getMonth() + 6, 1);

    const scale = scaleTime().domain([start, end]).range([0, innerWidth]);
    const ticks = scale.ticks(6);

    return { timeScale: scale, timeTicks: ticks, minDate: start, maxDate: end };
  }, [allMilestones, innerWidth]);

  // Cumulative Capital Curve Computation
  const { capitalAreaPath, grandTotalCap } = useMemo(() => {
    const capitalEvents = allMilestones
      .filter(m => m.amountUsd && m.amountUsd > 0)
      .sort((a, b) => a.date.getTime() - b.date.getTime());

    let runningTotal = 0;
    const points: Array<{ date: Date; cumCapital: number }> = [];

    // Starting baseline
    points.push({ date: minDate, cumCapital: 0 });

    capitalEvents.forEach(e => {
      runningTotal += e.amountUsd || 0;
      points.push({ date: e.date, cumCapital: runningTotal });
    });

    // Extend to maxDate
    points.push({ date: maxDate, cumCapital: runningTotal });

    const maxCap = Math.max(runningTotal, 1_000_000);
    const capScale = scaleLinear().domain([0, maxCap * 1.05]).range([innerHeight, innerHeight * 0.45]);

    const areaGen = area<{ date: Date; cumCapital: number }>()
      .x(d => timeScale(d.date))
      .y0(innerHeight)
      .y1(d => capScale(d.cumCapital))
      .curve(curveStepAfter);

    return {
      capitalAreaPath: areaGen(points) || '',
      grandTotalCap: runningTotal,
    };
  }, [allMilestones, minDate, maxDate, timeScale, innerHeight]);

  return (
    <div className="bg-slate-900 text-white rounded-2xl p-6 sm:p-7 shadow-2xl border border-slate-800 relative overflow-hidden space-y-5">
      {/* Decorative background glow */}
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-1/3 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Header bar */}
      <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase tracking-wider bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              D3 Temporal Graphics Engine
            </span>
            <span className="text-xs text-slate-400 font-mono">Multi-Track Capital &amp; IP Horizon</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-black text-white mt-1 tracking-tight flex items-center gap-2">
            <span>Capital Continuum &amp; Technology Evolution</span>
            <span className="text-xs font-mono font-normal text-slate-400">({allMilestones.length} Events)</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Temporal alignment of public grants, SEC exempt offerings, venture equity, and commercial IP milestones
          </p>
        </div>

        {/* Global Summary Badge */}
        <div className="flex items-center gap-3 bg-black/40 px-4 py-2.5 rounded-xl border border-white/10 shrink-0">
          <div className="text-right">
            <div className="text-[10px] uppercase font-bold text-slate-400 font-mono">Compounded Capital Stack</div>
            <div className="text-xl font-mono font-extrabold text-emerald-400">{fmt(grandTotalCap)}</div>
          </div>
          <div className="h-8 w-px bg-white/10" />
          <div className="text-right">
            <div className="text-[10px] uppercase font-bold text-slate-400 font-mono">Commercial IP</div>
            <div className="text-xl font-mono font-extrabold text-amber-400">
              {continuum.patents?.length || 0} <span className="text-xs font-normal text-slate-400">Patents</span>
            </div>
          </div>
        </div>
      </div>

      {/* Interactive Track Toggles */}
      <div className="relative z-10 flex flex-wrap items-center justify-between gap-2 text-xs">
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1 mr-1">
            <Filter size={12} /> Tracks:
          </span>
          {(Object.keys(TRACK_CONFIG) as TrackType[]).map(trackKey => {
            const cfg = TRACK_CONFIG[trackKey];
            const Icon = cfg.icon;
            const isActive = activeTracks[trackKey];
            const count = allMilestones.filter(m => m.track === trackKey).length;

            return (
              <button
                key={trackKey}
                type="button"
                onClick={() => toggleTrack(trackKey)}
                className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg font-mono text-[11px] font-semibold transition-all cursor-pointer border ${
                  isActive
                    ? 'text-white shadow-xs'
                    : 'bg-white/[0.02] text-slate-500 border-white/5 opacity-50 hover:opacity-80'
                }`}
                style={{
                  backgroundColor: isActive ? cfg.bgHex : undefined,
                  borderColor: isActive ? cfg.borderHex : undefined,
                }}
              >
                <Icon size={12} style={{ color: isActive ? cfg.hex : '#64748b' }} />
                <span>{cfg.label.split(' ')[0]}</span>
                <span className="px-1 py-0.2 rounded text-[9.5px] bg-black/40 font-bold">
                  {count}
                </span>
              </button>
            );
          })}
        </div>

        <button
          type="button"
          onClick={toggleAllTracks}
          className="text-[11px] font-mono text-slate-400 hover:text-white underline underline-offset-2 transition-colors cursor-pointer"
        >
          {Object.values(activeTracks).every(Boolean) ? 'Deselect All' : 'Select All'}
        </button>
      </div>

      {/* Main SVG Timeline Canvas */}
      <div 
        ref={containerRef}
        className="relative z-10 bg-slate-950/80 rounded-xl border border-white/10 p-3 overflow-x-auto shadow-inner"
      >
        <svg
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          className="w-full h-auto min-w-[760px] select-none"
        >
          <defs>
            {/* Cumulative Capital Gradient */}
            <linearGradient id="capitalGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#10b981" stopOpacity="0.0" />
            </linearGradient>

            {/* Grid line pattern */}
            <pattern id="timelineGrid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
            </pattern>
          </defs>

          {/* Background Grid */}
          <rect x={margin.left} y={margin.top} width={innerWidth} height={innerHeight} fill="url(#timelineGrid)" />

          {/* Cumulative Capital Stepped Area Path */}
          {capitalAreaPath && (
            <g transform={`translate(${margin.left}, ${margin.top})`}>
              <path
                d={capitalAreaPath}
                fill="url(#capitalGradient)"
                stroke="#10b981"
                strokeWidth="1.5"
                strokeDasharray="4 2"
                opacity="0.8"
              />
              <text
                x={innerWidth - 8}
                y={innerHeight * 0.48}
                textAnchor="end"
                className="text-[9.5px] font-mono fill-emerald-400/80 font-bold"
              >
                ▲ Cumulative Capital Stack ({fmt(grandTotalCap)})
              </text>
            </g>
          )}

          {/* Swimlane Horizontal Guidelines */}
          <g transform={`translate(${margin.left}, ${margin.top})`}>
            {activeTrackKeys.map((trackKey, index) => {
              const y = (index + 0.5) * trackHeight + 10;
              const cfg = TRACK_CONFIG[trackKey];

              return (
                <g key={trackKey} className="transition-all duration-300">
                  {/* Swimlane Lane Background Highlight */}
                  <rect
                    x={0}
                    y={y - trackHeight / 2 + 3}
                    width={innerWidth}
                    height={trackHeight - 6}
                    fill={index % 2 === 0 ? 'rgba(255,255,255,0.015)' : 'rgba(0,0,0,0.1)'}
                    rx="6"
                  />
                  {/* Center Guideline */}
                  <line
                    x1={0}
                    y1={y}
                    x2={innerWidth}
                    y2={y}
                    stroke="rgba(255,255,255,0.08)"
                    strokeDasharray="2 4"
                  />
                  {/* Track Label on Left Edge */}
                  <text
                    x={-10}
                    y={y + 3.5}
                    textAnchor="end"
                    fill={cfg.hex}
                    className="text-[9.5px] font-mono font-bold uppercase tracking-wider"
                  >
                    {cfg.label.split(' ')[0]}
                  </text>
                </g>
              );
            })}
          </g>

          {/* Time Axis Vertical Gridlines & Ticks */}
          <g transform={`translate(${margin.left}, ${margin.top})`}>
            {timeTicks.map((tickDate, i) => {
              const x = timeScale(tickDate);
              return (
                <g key={i} transform={`translate(${x}, 0)`}>
                  <line
                    x1={0}
                    y1={0}
                    x2={0}
                    y2={innerHeight}
                    stroke="rgba(255,255,255,0.12)"
                    strokeDasharray="3 3"
                  />
                  {/* Year/Month Axis Label */}
                  <text
                    x={0}
                    y={innerHeight + 20}
                    textAnchor="middle"
                    fill="#94a3b8"
                    className="text-[11px] font-mono font-semibold"
                  >
                    {tickDate.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                  </text>
                </g>
              );
            })}

            {/* Bottom Horizon Axis Line */}
            <line
              x1={0}
              y1={innerHeight}
              x2={innerWidth}
              y2={innerHeight}
              stroke="rgba(255,255,255,0.25)"
              strokeWidth="1.5"
            />
          </g>

          {/* Milestone Nodes & Connectors */}
          <g transform={`translate(${margin.left}, ${margin.top})`}>
            {filteredMilestones.map((m) => {
              const trackIndex = activeTrackKeys.indexOf(m.track);
              if (trackIndex === -1) return null;

              const x = timeScale(m.date);
              const y = (trackIndex + 0.5) * trackHeight + 10;
              const isHovered = hoveredNode?.id === m.id;

              return (
                <g
                  key={m.id}
                  transform={`translate(${x}, ${y})`}
                  className="cursor-pointer group"
                  onMouseEnter={(e) => {
                    setHoveredNode(m);
                    const rect = containerRef.current?.getBoundingClientRect();
                    if (rect) {
                      setPopoverPos({
                        x: e.clientX - rect.left,
                        y: e.clientY - rect.top,
                      });
                    }
                  }}
                  onMouseLeave={() => setHoveredNode(null)}
                >
                  {/* Vertical drop tick down to timeline base */}
                  <line
                    x1={0}
                    y1={0}
                    x2={0}
                    y2={innerHeight - y}
                    stroke={m.color}
                    strokeWidth={isHovered ? 1.5 : 0.8}
                    strokeOpacity={isHovered ? 0.8 : 0.25}
                    strokeDasharray="2 2"
                  />

                  {/* Pulsing halo when hovered */}
                  {isHovered && (
                    <circle
                      r={18}
                      fill={m.color}
                      opacity={0.25}
                      className="animate-ping"
                    />
                  )}

                  {/* Node Outer Ring */}
                  <circle
                    r={isHovered ? 12 : 9}
                    fill="#0f172a"
                    stroke={m.color}
                    strokeWidth={isHovered ? 3 : 2}
                    className="transition-all duration-200"
                  />

                  {/* Inner Node Core */}
                  <circle
                    r={isHovered ? 5 : 4}
                    fill={m.color}
                    className="transition-all duration-200"
                  />

                  {/* Node Mini Label (Dollar or Badge) */}
                  <text
                    x={0}
                    y={-14}
                    textAnchor="middle"
                    fill={isHovered ? '#ffffff' : m.color}
                    className="text-[9.5px] font-mono font-bold tracking-tight select-none"
                    style={{ textShadow: '0 1px 3px rgba(0,0,0,0.9)' }}
                  >
                    {m.amountUsd ? fmt(m.amountUsd) : m.badge || 'IP'}
                  </text>
                </g>
              );
            })}
          </g>
        </svg>

        {/* Hover Popover Card */}
        {hoveredNode && popoverPos && (
          <div
            className="absolute z-30 pointer-events-none p-3.5 bg-slate-900/95 backdrop-blur-md rounded-xl border border-white/20 shadow-2xl text-xs space-y-2 max-w-sm transition-all"
            style={{
              left: Math.min(Math.max(popoverPos.x - 120, 10), (containerRef.current?.clientWidth || 800) - 270),
              top: Math.max(popoverPos.y - 140, 10),
            }}
          >
            <div className="flex items-center justify-between gap-2 border-b border-white/10 pb-2">
              <span
                className="px-2 py-0.5 rounded font-mono font-bold text-[10px] uppercase"
                style={{
                  backgroundColor: hoveredNode.bgColor,
                  color: hoveredNode.color,
                  border: `1px solid ${hoveredNode.borderColor}`,
                }}
              >
                {hoveredNode.trackLabel}
              </span>
              <span className="font-mono text-slate-400 text-[11px] flex items-center gap-1">
                <Calendar size={11} />
                {formatDate(hoveredNode.date)}
              </span>
            </div>

            <div>
              <div className="font-bold text-white text-[13px] leading-snug">
                {hoveredNode.title}
              </div>
              <div className="text-slate-400 text-[11.5px] mt-0.5">
                {hoveredNode.subtitle}
              </div>
            </div>

            {hoveredNode.amountUsd && hoveredNode.amountUsd > 0 && (
              <div className="p-2 rounded-lg bg-black/40 border border-white/5 flex items-center justify-between">
                <span className="text-[11px] text-slate-400 font-mono uppercase">Capital Value</span>
                <span className="font-mono font-extrabold text-emerald-400 text-sm">
                  {fmt(hoveredNode.amountUsd)}
                </span>
              </div>
            )}

            {hoveredNode.details && (
              <div className="space-y-1 pt-1 text-[11px] font-mono text-slate-300">
                {Object.entries(hoveredNode.details).map(([k, v]) => (
                  <div key={k} className="flex items-start justify-between gap-2">
                    <span className="text-slate-400">{k}:</span>
                    <span className="text-slate-100 font-medium truncate max-w-[180px] text-right">{v}</span>
                  </div>
                ))}
              </div>
            )}

            {hoveredNode.externalUrl && (
              <div className="pt-1 text-[10.5px] text-cyan-400 flex items-center gap-1 font-mono font-semibold">
                <span>View Official Source</span>
                <ExternalLink size={10} />
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer Legend & Commercial Stage Progression Runway */}
      <div className="relative z-10 pt-1 border-t border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-4 text-[11px] text-slate-400 font-mono">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" /> Public Grants
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" /> Private Equity
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400" /> Form D
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-400" /> Scale-Up
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-400" /> USPTO IP
          </span>
        </div>

        <div className="text-[11px] text-slate-400 font-mono">
          <span className="text-slate-500">Stage: </span>
          <span className="text-cyan-300 font-bold">R&amp;D (TRL 2–4)</span> → <span className="text-amber-300 font-bold">Pilot</span> → <span className="text-emerald-300 font-bold">Scale-Up (TRL 7–8)</span> → <span className="text-indigo-300 font-bold">Commercial Deployment</span>
        </div>
      </div>
    </div>
  );
};

export default CapitalContinuumTimeline;
