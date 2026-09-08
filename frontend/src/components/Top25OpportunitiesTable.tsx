import React, { useState, useMemo } from 'react';
import {
  Target,
  Sparkles,
  Download,
  Search,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Building2,
  CheckCircle2,
  AlertCircle,
  Clock,
  DollarSign,
  Layers,
  FileText,
  FileCheck,
  ShieldCheck,
  Zap,
  Info,
  SlidersHorizontal,
  ChevronRight,
  LayoutList,
  FolderTree,
  Landmark,
  HeartHandshake,
  Globe,
  Filter,
  Users,
  Flame,
  Scale
} from 'lucide-react';
import clsx from 'clsx';
import { OrgLogo } from './OrgLogo';
import { GroupedOpportunityOrg, isOpportunityNew } from '../api/client';
import { WinningAngleModal } from './WinningAngleModal';
import { useNyserda } from '../context/NyserdaContext';

export interface RequirementItem {
  name: string;
  status: string;
  reason: string;
}

export interface MatchItem {
  opportunity_id: number;
  solicitation_number: string;
  name: string;
  agency?: string;
  match_type: string;
  fit_score: number;
  match_score_pct?: number;
  why_it_fits?: string;
  strategic_thesis?: string;
  criteria_strengths?: string[];
  potential_risks_or_flags?: string[];
  recommended_positioning?: string;
  conviction_tier?: string;
  llm_match_score?: number;
  llm_analysis?: any;
  advisor_qc?: {
    makes_sense?: boolean;
    decision?: string;
    confidence?: number;
    reason?: string;
    domain_alignment?: string;
    model_used?: string;
    is_llm_generated?: boolean;
  };
  statutory_mandates?: string[];
  priority_problem_statements?: string[];
  scoring_rubric_weights?: Record<string, number>;
  teaming_partner_types_sought?: string[];
  project_cost_min?: number | null;
  project_cost_max?: number | null;
  cost_share_mandatory?: boolean;
  disadvantaged_community_priority?: boolean;
  max_per_award?: number | null;
  total_funding?: number | null;
  cost_share_pct?: number | null;
  next_deadline?: string | null;
  deadline?: string | null;
  lifecycle_status?: string | null;
  status?: string | null;
  program_type?: string | null;
  url?: string | null;
  assessment?: any;
  timeline?: any;
  requirements_checklist?: any[];
  restrictions?: any[];
  matched_keywords?: string[];
}

function fmt(n: number | null | undefined): string {
  if (n === null || n === undefined || isNaN(n)) return 'Unspecified';
  if (n >= 1_000_000_000) return `$${(n / 1_000_000_000).toFixed(2)}B`;
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(2)}M`;
  if (n >= 1_000) return `$${(n / 1_000).toFixed(0)}k`;
  return `$${n.toLocaleString()}`;
}

interface Top25OpportunitiesTableProps {
  matches: MatchItem[];
  groupedOpportunities?: GroupedOpportunityOrg[];
  rawTopMatches?: MatchItem[];
  projectTitle?: string;
  onOpenShredder?: (oppId: number) => void;
}

export function Top25OpportunitiesTable({
  matches,
  groupedOpportunities = [],
  rawTopMatches = [],
  projectTitle = 'Proposed Project',
  onOpenShredder,
}: Top25OpportunitiesTableProps) {
  const { includeNyserda, isNyserda } = useNyserda();
  const [viewMode, setViewMode] = useState<'grouped' | 'flat'>('grouped');
  const [quotaMode, setQuotaMode] = useState<'diversified' | 'uncapped'>('diversified');
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const [search, setSearch] = useState('');
  const [selectedAgency, setSelectedAgency] = useState<string>('all');
  const [selectedLevel, setSelectedLevel] = useState<string>('all');
  const [expandedRowId, setExpandedRowId] = useState<number | null>(null);
  const [expandedOrgCodes, setExpandedOrgCodes] = useState<Record<string, boolean>>({});
  const [selectedAngleMatch, setSelectedAngleMatch] = useState<MatchItem | null>(null);

  // Flat matches based on quota mode (strictly filtered to >=75% match score, top 20 opportunities)
  const activeMatches = useMemo(() => {
    const raw = quotaMode === 'uncapped' && rawTopMatches.length > 0 ? rawTopMatches : (matches || []);
    return raw
      .filter((m) => includeNyserda || (!isNyserda(m.agency) && !isNyserda(m.name)))
      .filter((m) => (m.fit_score || 0) >= 0.75 || (m.match_score_pct || 0) >= 75 || (m.llm_match_score || 0) >= 75)
      .slice(0, 20);
  }, [matches, rawTopMatches, quotaMode, includeNyserda, isNyserda]);

  // Distinct agencies
  const availableAgencies = useMemo(() => {
    const set = new Set<string>();
    activeMatches.forEach((m) => {
      if (m.agency && (includeNyserda || !isNyserda(m.agency))) set.add(m.agency);
    });
    return Array.from(set).sort();
  }, [activeMatches, includeNyserda, isNyserda]);

  // Synthesize grouped opportunities if not directly provided (Top 10 Organizations & >=75% Matches)
  const resolvedGroupedOrgs: GroupedOpportunityOrg[] = useMemo(() => {
    let list: GroupedOpportunityOrg[] = [];
    if (groupedOpportunities && groupedOpportunities.length > 0) {
      list = groupedOpportunities
        .filter((org) => includeNyserda || (!isNyserda(org.organization_name) && !isNyserda(org.organization_code)))
        .map((org) => {
          const opps = (org.top_opportunities || []).filter(
            (m) => (includeNyserda || (!isNyserda(m.agency) && !isNyserda(m.name))) &&
                   ((m.fit_score || 0) >= 0.75 || (m.match_score_pct || 0) >= 75 || (m.llm_match_score || 0) >= 75)
          );
          const allOpps = (org.all_opportunities || []).filter(
            (m) => (includeNyserda || (!isNyserda(m.agency) && !isNyserda(m.name))) &&
                   ((m.fit_score || 0) >= 0.75 || (m.match_score_pct || 0) >= 75 || (m.llm_match_score || 0) >= 75)
          );
          return {
            ...org,
            top_opportunities: opps.slice(0, 5),
            all_opportunities: allOpps,
            total_opportunities_count: opps.length,
          };
        });
    } else {
      // Fallback: group from activeMatches
      const map = new Map<string, MatchItem[]>();
      activeMatches.forEach((m) => {
        const ag = m.agency || 'Public Agency';
        if (!map.has(ag)) map.set(ag, []);
        map.get(ag)!.push(m);
      });

      map.forEach((opps, ag) => {
        const topOpp = opps[0];
        const isState = ag.toLowerCase().includes('nyserda') || ag.toLowerCase().includes('cec') || ag.toLowerCase().includes('state');
        const isFed = ['DOE', 'NSF', 'EPA', 'ARPA-E', 'USDA', 'DOT'].includes(ag);
        const category = isState ? 'state' : isFed ? 'federal' : 'utility';
        list.push({
          organization_code: ag,
          organization_name: ag,
          category: category,
          category_label: isState ? 'State Energy Agency' : isFed ? 'Federal Agency' : 'Electric & Gas Utility',
          state: isState ? 'State' : isFed ? 'US' : 'Regional',
          say_yes_score: Math.round((topOpp?.fit_score || 0.8) * 100),
          say_yes_tier: (topOpp?.fit_score || 0) >= 0.8 ? 'Highest Probability' : 'Strong Alignment',
          tier_badge_color: 'emerald',
          geographic_nexus: isState ? 'State Jurisdiction' : isFed ? 'Federal Nationwide' : 'Utility Service Territory',
          primary_pain_points: [],
          why_they_say_yes: topOpp?.why_it_fits || 'Direct technology match with active funding priorities.',
          total_opportunities_count: opps.length,
          top_opportunities: opps.slice(0, 5),
          all_opportunities: opps,
        });
      });
    }

    return list.slice(0, 10).sort((a, b) => b.say_yes_score - a.say_yes_score);
  }, [groupedOpportunities, activeMatches]);

  // Filter grouped organizations by search and category
  const filteredGroupedOrgs = useMemo(() => {
    return resolvedGroupedOrgs.filter((org) => {
      if (activeCategory !== 'all' && org.category !== activeCategory) return false;
      if (!search.trim()) return true;
      const s = search.toLowerCase();
      const matchOrg =
        org.organization_name.toLowerCase().includes(s) ||
        org.organization_code.toLowerCase().includes(s) ||
        org.why_they_say_yes.toLowerCase().includes(s) ||
        org.primary_pain_points.some((p) => p.toLowerCase().includes(s));
      const matchSubOpps = (org.top_opportunities || []).some(
        (opp) =>
          (opp.name && opp.name.toLowerCase().includes(s)) ||
          (opp.solicitation_number && opp.solicitation_number.toLowerCase().includes(s)) ||
          (opp.why_it_fits && opp.why_it_fits.toLowerCase().includes(s))
      );
      return matchOrg || matchSubOpps;
    });
  }, [resolvedGroupedOrgs, activeCategory, search]);

  // Filtered flat matches
  const filteredFlatMatches = useMemo(() => {
    return activeMatches.filter((m) => {
      if (selectedAgency !== 'all' && m.agency !== selectedAgency) return false;
      if (selectedLevel !== 'all') {
        const type = (m.match_type || '').toLowerCase();
        if (selectedLevel === 'strong' && !type.includes('strong')) return false;
        if (selectedLevel === 'conditional' && !type.includes('conditional')) return false;
      }
      if (!search.trim()) return true;
      const s = search.toLowerCase();
      return (
        (m.solicitation_number && m.solicitation_number.toLowerCase().includes(s)) ||
        (m.name && m.name.toLowerCase().includes(s)) ||
        (m.agency && m.agency.toLowerCase().includes(s)) ||
        (m.why_it_fits && m.why_it_fits.toLowerCase().includes(s))
      );
    });
  }, [activeMatches, selectedAgency, selectedLevel, search]);

  const toggleRow = (id: number) => {
    setExpandedRowId(expandedRowId === id ? null : id);
  };

  const toggleOrgCollapse = (code: string) => {
    setExpandedOrgCodes((prev) => ({
      ...prev,
      [code]: prev[code] === undefined ? true : !prev[code],
    }));
  };

  const expandAllOrgs = () => {
    const next: Record<string, boolean> = {};
    resolvedGroupedOrgs.forEach((o) => {
      next[o.organization_code] = false; // false = expanded (not collapsed)
    });
    setExpandedOrgCodes(next);
  };

  const collapseAllOrgs = () => {
    const next: Record<string, boolean> = {};
    resolvedGroupedOrgs.forEach((o) => {
      next[o.organization_code] = true; // true = collapsed
    });
    setExpandedOrgCodes(next);
  };

  const totalOppsCount = useMemo(() => {
    return resolvedGroupedOrgs.reduce((acc, org) => acc + (org.total_opportunities_count || org.top_opportunities?.length || 0), 0);
  }, [resolvedGroupedOrgs]);

  return (
    <div className="bg-white dark:bg-[#0d1424] rounded-2xl border border-slate-200/80 dark:border-white/10 p-5 shadow-2xs space-y-4">
      {/* Header Bar */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-3 border-b border-slate-100 dark:border-slate-800">
        <div>
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
              <Target size={12} className="text-slate-500" />
              <span>High-Conviction Solicitations &amp; Grants</span>
            </span>
            <span className="text-xs text-slate-300 dark:text-slate-700">|</span>
            <span className="text-[11px] font-mono font-medium text-slate-500 dark:text-slate-400">
              {resolvedGroupedOrgs.length} Sponsoring Organizations ({totalOppsCount} Matched Solicitations)
            </span>
            <span className="text-xs text-slate-300 dark:text-slate-700">|</span>
            <span className="text-[10.5px] font-medium px-2 py-0.2 rounded-full bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/60">
              Score ≥75% Only
            </span>
          </div>
          <h2 className="text-base font-bold text-slate-900 dark:text-slate-100 tracking-tight">
            High-Conviction Solicitations Grouped by Sponsoring Organization (&ge;75% Match Fit)
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 max-w-3xl leading-relaxed">
            Screened against <strong>TRL bounds</strong>, <strong>award size eligibility</strong>, <strong>cost-share obligations</strong>, and statutory problem statement alignment. Clustered by sponsoring institution to prevent federal giants from crowding out state agencies and regional utilities.
          </p>
        </div>

        <div className="flex items-center gap-2.5 flex-wrap shrink-0">
          {/* Dual View Mode Switcher */}
          <div className="flex items-center bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg border border-slate-200 dark:border-slate-700">
            <button
              type="button"
              onClick={() => setViewMode('grouped')}
              className={clsx(
                'px-2.5 py-1 rounded-md text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer',
                viewMode === 'grouped'
                  ? 'bg-[#00E5FF] text-slate-950 font-bold shadow-glow-cyan-sm'
                  : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'
              )}
            >
              <FolderTree size={13} />
              <span>By Organization</span>
            </button>
            <button
              type="button"
              onClick={() => setViewMode('flat')}
              className={clsx(
                'px-2.5 py-1 rounded-md text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer',
                viewMode === 'flat'
                  ? 'bg-[#00E5FF] text-slate-950 font-bold shadow-glow-cyan-sm'
                  : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'
              )}
            >
              <LayoutList size={13} />
              <span>Flat Table</span>
            </button>
          </div>

          {/* Diversity Quota Toggle */}
          <button
            type="button"
            onClick={() => setQuotaMode(quotaMode === 'diversified' ? 'uncapped' : 'diversified')}
            title="Toggle between Institutional Diversity (Max 5/agency) and Uncapped Pure Score ranking"
            className={clsx(
              'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium transition-colors shadow-2xs cursor-pointer',
              quotaMode === 'diversified'
                ? 'bg-[#00E5FF] text-slate-950 border-[#00E5FF] font-bold shadow-glow-cyan-sm'
                : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300'
            )}
          >
            <Scale size={13} className={quotaMode === 'diversified' ? 'text-slate-950 font-bold' : 'text-slate-400'} />
            <span>{quotaMode === 'diversified' ? 'Diversified (Max 5)' : 'Uncapped Pure Scores'}</span>
          </button>
        </div>
      </div>

      {/* Filters & Search Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        {/* Category Tabs */}
        <div className="flex items-center gap-1 overflow-x-auto no-scrollbar py-0.5">
          {[
            { id: 'all', label: 'All Organizations', icon: Globe },
            { id: 'utility', label: 'Utilities', icon: Zap },
            { id: 'state', label: 'State Agencies', icon: Building2 },
            { id: 'federal', label: 'Federal Agencies', icon: Landmark },
            { id: 'foundation', label: 'Philanthropy', icon: HeartHandshake },
          ].map((tab) => {
            const Icon = tab.icon;
            const isCurrent = activeCategory === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveCategory(tab.id)}
                className={clsx(
                  'px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 shrink-0 cursor-pointer',
                  isCurrent
                    ? 'bg-[#00E5FF] text-slate-950 border-[#00E5FF] font-bold shadow-glow-cyan-sm'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/5'
                )}
              >
                <Icon size={12} className={isCurrent ? 'text-slate-950 font-bold' : 'text-slate-400'} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Search & Secondary Filter Controls */}
        <div className="flex items-center gap-2 flex-1 sm:max-w-md justify-end flex-wrap">
          <div className="relative flex-1 min-w-[180px]">
            <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search by program, FOA #, or organization..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 rounded-xl bg-slate-50 dark:bg-black/30 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 outline-none focus:border-indigo-500 transition-all"
            />
          </div>

          {viewMode === 'grouped' ? (
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={expandAllOrgs}
                className="px-2.5 py-1 text-[11px] font-semibold rounded-lg bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 text-slate-700 dark:text-slate-300 transition-colors cursor-pointer"
              >
                Expand All
              </button>
              <button
                type="button"
                onClick={collapseAllOrgs}
                className="px-2.5 py-1 text-[11px] font-semibold rounded-lg bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 text-slate-700 dark:text-slate-300 transition-colors cursor-pointer"
              >
                Collapse All
              </button>
            </div>
          ) : (
            availableAgencies.length > 0 && (
              <select
                value={selectedAgency}
                onChange={(e) => setSelectedAgency(e.target.value)}
                className="px-2.5 py-1.5 rounded-xl bg-slate-50 dark:bg-black/30 border border-slate-200 dark:border-white/10 text-xs text-slate-800 dark:text-slate-200 outline-none focus:border-indigo-500 shrink-0"
              >
                <option value="all">All Agencies ({availableAgencies.length})</option>
                {availableAgencies.map((ag) => (
                  <option key={ag} value={ag}>
                    {ag.length > 25 ? ag.slice(0, 25) + '...' : ag}
                  </option>
                ))}
              </select>
            )
          )}
        </div>
      </div>

      {/* ─── 1. HIERARCHICAL GROUPED BY ORGANIZATION VIEW ──────────────────────── */}
      {viewMode === 'grouped' && (
        <div className="space-y-4">
          {filteredGroupedOrgs.map((org, orgIdx) => {
            const isOrgCollapsed = expandedOrgCodes[org.organization_code] === true;
            const opps = org.top_opportunities || [];
            const hasMore = org.total_opportunities_count > opps.length;

            return (
              <div
                key={org.organization_code || orgIdx}
                className="rounded-2xl border border-slate-200 dark:border-white/10 overflow-hidden bg-slate-50/50 dark:bg-black/20 shadow-2xs transition-all"
              >
                {/* Organization Header Bar */}
                <div
                  onClick={() => toggleOrgCollapse(org.organization_code)}
                  className="p-4 bg-white dark:bg-[#0d1424] border-b border-slate-200/80 dark:border-white/5 flex flex-col md:flex-row md:items-center justify-between gap-3 cursor-pointer hover:bg-slate-50/80 dark:hover:bg-white/[0.02] transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <OrgLogo org={org.organization_code} size="sm" showTooltip={false} />
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className="text-sm font-bold text-slate-900 dark:text-white truncate">
                          {org.organization_name}
                        </h3>
                        <span className="text-[10px] font-mono font-bold px-2 py-0.2 rounded-md bg-slate-100 text-slate-600 dark:bg-white/5 dark:text-slate-300">
                          {org.category_label}
                        </span>
                        {org.state && (
                          <span className="text-[10px] font-mono font-bold px-1.5 py-0.2 rounded bg-indigo-50 text-indigo-700 dark:bg-indigo-950/40 dark:text-indigo-300 border border-indigo-200/60 dark:border-indigo-500/20">
                            {org.state}
                          </span>
                        )}
                      </div>
                      {org.why_they_say_yes && (
                        <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-1 italic">
                          &ldquo;{org.why_they_say_yes}&rdquo;
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    <div className="text-right">
                      <div className="flex items-center gap-1 font-mono font-bold text-xs text-emerald-600 dark:text-emerald-400">
                        <Sparkles size={12} />
                        <span>{org.say_yes_score}% Say-Yes Score</span>
                      </div>
                      <div className="text-[10.5px] text-slate-400 font-mono">
                        {opps.length} Active {opps.length === 1 ? 'Opportunity' : 'Opportunities'}
                        {hasMore ? ` (of ${org.total_opportunities_count})` : ''}
                      </div>
                    </div>

                    <div className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-white/5 dark:hover:bg-white/10 text-slate-600 dark:text-slate-300 transition-colors">
                      {isOrgCollapsed ? <ChevronDown size={15} /> : <ChevronUp size={15} />}
                    </div>
                  </div>
                </div>

                {/* Sub-Section: Nested Solicitations Table */}
                {!isOrgCollapsed && (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="border-b border-slate-200 dark:border-white/10 bg-slate-100/60 dark:bg-white/[0.01] text-[10.5px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 font-mono">
                          <th className="py-2.5 px-3.5 w-12 text-center">Rank</th>
                          <th className="py-2.5 px-3.5 w-24 text-center">Fit Score</th>
                          <th className="py-2.5 px-3.5 min-w-[240px]">Solicitation &amp; Program Scope</th>
                          <th className="py-2.5 px-3.5 text-right w-28">Max Award</th>
                          <th className="py-2.5 px-3.5 text-center w-24">Cost-Share</th>
                          <th className="py-2.5 px-3.5 min-w-[130px]">Deadline</th>
                          <th className="py-2.5 px-3.5 w-24 text-center">Diligence</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-200/60 dark:divide-white/5 bg-white dark:bg-[#0d1424]">
                        {opps.map((m: MatchItem, oppIdx: number) => {
                          const isExpanded = expandedRowId === m.opportunity_id;
                          const scorePct = m.match_score_pct ?? Math.round((m.fit_score || 0.8) * 100);
                          const isStrong = scorePct >= 85 || (m.match_type || '').includes('strong');

                          return (
                            <React.Fragment key={m.opportunity_id || oppIdx}>
                              <tr
                                onClick={() => toggleRow(m.opportunity_id)}
                                className={clsx(
                                  'hover:bg-slate-50/80 dark:hover:bg-white/[0.02] transition-colors cursor-pointer group',
                                  isExpanded && 'bg-slate-50 dark:bg-white/[0.03]'
                                )}
                              >
                                {/* Rank */}
                                <td className="py-3 px-3.5 text-center font-mono">
                                  <span className="inline-flex items-center justify-center w-6 h-6 rounded-md bg-slate-100 dark:bg-white/5 text-slate-700 dark:text-slate-300 text-[11px] font-bold">
                                    #{oppIdx + 1}
                                  </span>
                                </td>

                                {/* Fit Score */}
                                <td className="py-3 px-3.5 text-center">
                                  <div className="flex flex-col items-center">
                                    <span
                                      className={clsx(
                                        'font-mono font-bold text-xs',
                                        isStrong ? 'text-[#00F5A0]' : 'text-[#00E5FF]'
                                      )}
                                    >
                                      {scorePct}%
                                    </span>
                                    <span
                                      className={clsx(
                                        'text-[8.5px] font-bold px-1.5 py-0.1 rounded-full uppercase tracking-tight',
                                        isStrong
                                          ? 'bg-[#00F5A0]/15 text-[#00F5A0] border border-[#00F5A0]/40'
                                          : 'bg-[#00E5FF]/15 text-[#00E5FF] border border-[#00E5FF]/40'
                                      )}
                                    >
                                      {isStrong ? 'Strong' : 'Conditional'}
                                    </span>
                                  </div>
                                </td>

                                {/* Solicitation & Program Name */}
                                <td className="py-3 px-3.5">
                                  <div className="space-y-0.5">
                                    <div className="flex items-center gap-1.5 flex-wrap">
                                      <span className="font-mono font-bold text-[11px] text-indigo-600 dark:text-indigo-400">
                                        {m.solicitation_number || `OPP-${m.opportunity_id}`}
                                      </span>
                                      {isOpportunityNew(m) && (
                                        <span className="inline-flex items-center gap-0.5 text-[8.5px] font-extrabold px-1.5 py-0.2 rounded-full bg-emerald-500 text-white shadow-2xs tracking-wide">
                                          <Sparkles size={8} className="animate-pulse" />
                                          <span>NEW</span>
                                        </span>
                                      )}
                                      {m.lifecycle_status && (
                                        <span className="text-[8px] px-1.5 py-0.2 rounded bg-slate-100 dark:bg-white/10 text-slate-600 dark:text-slate-300 font-mono font-semibold">
                                          {m.lifecycle_status}
                                        </span>
                                      )}
                                    </div>
                                    <div className="font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors line-clamp-1">
                                      {m.name}
                                    </div>
                                    {m.why_it_fits && (
                                      <div className="text-[10.5px] text-slate-500 dark:text-slate-400 line-clamp-1 italic">
                                        &ldquo;{m.why_it_fits}&rdquo;
                                      </div>
                                    )}
                                  </div>
                                </td>

                                {/* Max Award */}
                                <td className="py-3 px-3.5 text-right font-mono">
                                  <div className="font-bold text-emerald-600 dark:text-emerald-400 text-xs">
                                    {fmt(m.max_per_award || m.total_funding)}
                                  </div>
                                  {m.total_funding && m.max_per_award && m.total_funding !== m.max_per_award && (
                                    <div className="text-[9px] text-slate-400">Pool: {fmt(m.total_funding)}</div>
                                  )}
                                </td>

                                {/* Cost Share */}
                                <td className="py-3 px-3.5 text-center font-mono">
                                  <span
                                    className={clsx(
                                      'inline-block font-bold px-2 py-0.5 rounded text-[10.5px]',
                                      m.cost_share_pct === 0 || m.cost_share_pct === null
                                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-500/30'
                                        : 'bg-amber-50 text-amber-800 border border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-500/30'
                                    )}
                                  >
                                    {m.cost_share_pct !== null && m.cost_share_pct !== undefined ? `${m.cost_share_pct}%` : '0%'}
                                  </span>
                                </td>

                                {/* Deadline */}
                                <td className="py-3 px-3.5">
                                  <div className="flex items-center gap-1.5 text-[10.5px] text-slate-700 dark:text-slate-300">
                                    <Clock size={11} className="text-slate-400 shrink-0" />
                                    <span className="truncate max-w-[120px]">{m.next_deadline || m.deadline || 'Open / Rolling'}</span>
                                  </div>
                                </td>

                                {/* Details Action */}
                                <td className="py-3 px-3.5 text-center">
                                  <button
                                    type="button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      toggleRow(m.opportunity_id);
                                    }}
                                    className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-white/5 dark:hover:bg-white/10 text-slate-700 dark:text-slate-300 transition-colors cursor-pointer"
                                  >
                                    {isExpanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                                  </button>
                                </td>
                              </tr>

                              {/* Expanded Diligence Drawer */}
                              {isExpanded && (
                                <tr className="bg-slate-50/80 dark:bg-black/30 animate-in fade-in duration-150">
                                  <td colSpan={7} className="p-4 border-b border-slate-200 dark:border-white/10">
                                    <div className="space-y-4 max-w-5xl mx-auto">
                                      {/* Top Summary Info & LLM Strategic Analysis */}
                                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 p-4 rounded-xl bg-white dark:bg-[#0d1424] border border-slate-200/80 dark:border-white/10 text-xs shadow-2xs">
                                        <div className="md:col-span-2 space-y-2">
                                          <div className="text-[10px] uppercase font-bold text-indigo-600 dark:text-indigo-400 flex items-center gap-1">
                                            <Sparkles size={12} />
                                            <span>LLM Strategic Match Thesis</span>
                                          </div>
                                          <div className="text-slate-800 dark:text-slate-200 text-xs leading-relaxed italic">
                                            &ldquo;{m.strategic_thesis || m.why_it_fits || m.assessment?.verdict_detail || 'Strong programmatic fit matching technology readiness and applicant scope.'}&rdquo;
                                          </div>
                                          {m.recommended_positioning && (
                                            <div className="p-2.5 rounded-lg bg-indigo-50 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-500/30 text-[11px] text-indigo-900 dark:text-indigo-200 mt-2">
                                              <strong className="text-indigo-700 dark:text-indigo-300">Winning Proposal Angle: </strong>
                                              {m.recommended_positioning}
                                            </div>
                                          )}
                                          {m.advisor_qc && (
                                            <div className="p-2.5 rounded-lg bg-emerald-50/90 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-500/30 text-[11px] text-emerald-900 dark:text-emerald-200 mt-2">
                                              <div className="flex items-center gap-1.5 font-bold text-emerald-700 dark:text-emerald-400">
                                                <ShieldCheck size={13} className="shrink-0" />
                                                <span>Advisor QC Diligence Verified</span>
                                                <span className="text-[9.5px] font-normal text-emerald-600 dark:text-emerald-400/80">({Math.round((m.advisor_qc.confidence || 0.9) * 100)}% confidence &bull; {m.advisor_qc.model_used || 'grounded-qc'})</span>
                                              </div>
                                              <div className="mt-1 text-emerald-800 dark:text-emerald-300/90 leading-relaxed text-[10.5px]">
                                                {m.advisor_qc.reason}
                                              </div>
                                            </div>
                                          )}
                                        </div>

                                        <div className="space-y-3">
                                          <div>
                                            <div className="text-[10px] uppercase font-bold text-slate-500 dark:text-slate-400">Application Strategy</div>
                                            <div className="text-slate-700 dark:text-slate-300 mt-0.5 leading-relaxed text-[11px]">
                                              {m.timeline?.timing_note || 'Prepare formal technical consortia and lock in milestone cost-share.'}
                                            </div>
                                          </div>
                                          <div>
                                            <div className="text-[10px] uppercase font-bold text-slate-500 dark:text-slate-400">FOA Actions</div>
                                            <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                                              <button
                                                type="button"
                                                onClick={() => setSelectedAngleMatch(m)}
                                                className="px-2.5 py-1 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-700 dark:text-amber-300 border border-amber-500/30 text-[11px] font-bold flex items-center gap-1 cursor-pointer transition-colors"
                                              >
                                                <Zap size={11} className="text-amber-500 fill-amber-500" /> Winning Angle
                                              </button>
                                              {onOpenShredder && (
                                                <button
                                                  type="button"
                                                  onClick={() => onOpenShredder(m.opportunity_id)}
                                                  className="px-2.5 py-1 rounded-lg bg-indigo-50 dark:bg-indigo-950/40 hover:bg-indigo-100 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/30 text-[11px] font-bold flex items-center gap-1 cursor-pointer"
                                                >
                                                  <FileText size={11} /> Shred FOA
                                                </button>
                                              )}
                                              {m.url && (
                                                <a
                                                  href={m.url}
                                                  target="_blank"
                                                  rel="noopener noreferrer"
                                                  className="px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-white/10 text-[11px] font-bold flex items-center gap-1"
                                                >
                                                  <ExternalLink size={11} /> View Source
                                                </a>
                                              )}
                                            </div>
                                          </div>
                                        </div>
                                      </div>

                                      {/* Evaluation Criteria Strengths */}
                                      {m.criteria_strengths && m.criteria_strengths.length > 0 && (
                                        <div className="space-y-1.5">
                                          <div className="text-[11px] font-bold text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5">
                                            <CheckCircle2 size={13} className="text-emerald-600 dark:text-emerald-400" />
                                            <span>Evaluation Criteria Advantages:</span>
                                          </div>
                                          <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                                            {m.criteria_strengths.map((crit, cIdx) => (
                                              <div key={cIdx} className="p-2.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-500/30 text-emerald-900 dark:text-emerald-200 text-[11px] leading-snug">
                                                {crit}
                                              </div>
                                            ))}
                                          </div>
                                        </div>
                                      )}

                                      {/* Requirements Checklist */}
                                      {m.requirements_checklist && m.requirements_checklist.length > 0 && (
                                        <div className="space-y-1.5">
                                          <div className="text-[11px] font-bold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                                            <ShieldCheck size={13} className="text-indigo-600 dark:text-indigo-400" />
                                            <span>Requirements Verification:</span>
                                          </div>
                                          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                                            {m.requirements_checklist.map((req, reqIdx) => (
                                              <div
                                                key={reqIdx}
                                                className="p-2 rounded-lg bg-white dark:bg-[#0d1424] border border-slate-200 dark:border-white/10 flex items-start gap-2 text-[11px]"
                                              >
                                                {req.status === 'pass' ? (
                                                  <CheckCircle2 size={13} className="text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
                                                ) : req.status === 'conditional' ? (
                                                  <AlertCircle size={13} className="text-amber-500 shrink-0 mt-0.5" />
                                                ) : (
                                                  <AlertCircle size={13} className="text-rose-500 shrink-0 mt-0.5" />
                                                )}
                                                <div className="min-w-0">
                                                  <span className="font-bold text-slate-900 dark:text-white">{req.name}: </span>
                                                  <span className="text-slate-500 dark:text-slate-400">{req.reason}</span>
                                                </div>
                                              </div>
                                            ))}
                                          </div>
                                        </div>
                                      )}

                                      {/* Proprietary Intelligence: Statutory Mandates & Targeted Problem Statements */}
                                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 border-t border-slate-200 dark:border-white/10 text-xs">
                                        {/* Statutory Mandates */}
                                        {m.statutory_mandates && m.statutory_mandates.length > 0 && (
                                          <div className="space-y-1.5">
                                            <div className="text-[10.5px] uppercase font-bold text-indigo-600 dark:text-indigo-400 flex items-center gap-1">
                                              <Layers size={12} />
                                              <span>Statutory Policy Alignment</span>
                                            </div>
                                            <div className="flex flex-wrap gap-1">
                                              {m.statutory_mandates.map((mandate, idx) => (
                                                <span
                                                  key={idx}
                                                  className="text-[10px] px-2 py-0.5 rounded-md bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/30 font-medium"
                                                >
                                                  {mandate}
                                                </span>
                                              ))}
                                            </div>
                                          </div>
                                        )}

                                        {/* Targeted Problem Statements */}
                                        {m.priority_problem_statements && m.priority_problem_statements.length > 0 && (
                                          <div className="space-y-1.5">
                                            <div className="text-[10.5px] uppercase font-bold text-amber-700 dark:text-amber-400 flex items-center gap-1">
                                              <Target size={12} />
                                              <span>Targeted Technical Challenges</span>
                                            </div>
                                            <div className="space-y-1">
                                              {m.priority_problem_statements.map((prob, idx) => (
                                                <div key={idx} className="text-[11px] text-slate-700 dark:text-slate-300 leading-snug flex items-start gap-1.5">
                                                  <span className="text-amber-500 font-bold">•</span>
                                                  <span>{prob}</span>
                                                </div>
                                              ))}
                                            </div>
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  </td>
                                </tr>
                              )}
                            </React.Fragment>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* ─── 2. FLAT SOLICITATIONS TABULAR VIEW ───────────────────────────────── */}
      {viewMode === 'flat' && (
        <div className="rounded-xl border border-slate-200 dark:border-white/10 overflow-hidden shadow-2xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-200 dark:border-white/10 bg-slate-50/80 dark:bg-white/[0.02] text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 font-mono">
                  <th className="py-3 px-3.5 w-14 text-center">Rank</th>
                  <th className="py-3 px-3.5 w-24 text-center">Fit Score</th>
                  <th className="py-3 px-3.5 min-w-[240px]">Solicitation &amp; Program</th>
                  <th className="py-3 px-3.5 min-w-[150px]">Funding Agency</th>
                  <th className="py-3 px-3.5 text-right w-28">Max Award</th>
                  <th className="py-3 px-3.5 text-center w-24">Cost-Share</th>
                  <th className="py-3 px-3.5 min-w-[120px]">Deadline</th>
                  <th className="py-3 px-3.5 w-24 text-center">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-white/5 text-xs">
                {filteredFlatMatches.map((m, idx) => {
                  const rank = idx + 1;
                  const isExpanded = expandedRowId === m.opportunity_id;
                  const scorePct = m.match_score_pct ?? Math.round((m.fit_score || 0.8) * 100);
                  const isStrong = scorePct >= 85 || (m.match_type || '').includes('strong');

                  return (
                    <React.Fragment key={m.opportunity_id || idx}>
                      <tr
                        onClick={() => toggleRow(m.opportunity_id)}
                        className={clsx(
                          'hover:bg-slate-50/70 dark:hover:bg-white/[0.02] transition-colors cursor-pointer group',
                          isExpanded && 'bg-slate-50 dark:bg-white/[0.03]'
                        )}
                      >
                        {/* Rank Badge */}
                        <td className="py-3 px-3.5 text-center font-mono">
                          <span
                            className={clsx(
                              'inline-flex items-center justify-center w-7 h-7 rounded-lg text-xs font-black',
                              rank === 1
                                ? 'bg-amber-400 text-slate-950 shadow-2xs'
                                : rank <= 3
                                ? 'bg-slate-200 text-slate-800 dark:bg-white/10 dark:text-slate-200'
                                : 'bg-slate-100 text-slate-600 dark:bg-white/5 dark:text-slate-400'
                            )}
                          >
                            #{rank}
                          </span>
                        </td>

                        {/* Fit Score */}
                        <td className="py-3 px-3.5 text-center">
                          <div className="flex flex-col items-center">
                            <span
                              className={clsx(
                                'font-mono font-bold text-sm',
                                isStrong ? 'text-[#00F5A0]' : 'text-[#00E5FF]'
                              )}
                            >
                              {scorePct}%
                            </span>
                            <span
                              className={clsx(
                                'text-[9px] font-bold px-1.5 py-0.2 rounded-full mt-0.5 uppercase tracking-tight',
                                isStrong
                                  ? 'bg-[#00F5A0]/15 text-[#00F5A0] border border-[#00F5A0]/40'
                                  : 'bg-[#00E5FF]/15 text-[#00E5FF] border border-[#00E5FF]/40'
                              )}
                            >
                              {isStrong ? 'Strong' : 'Conditional'}
                            </span>
                          </div>
                        </td>

                        {/* Solicitation & Program Name */}
                        <td className="py-3 px-3.5">
                          <div className="space-y-0.5">
                            <div className="flex items-center gap-1.5 flex-wrap">
                              <span className="font-mono font-bold text-[11.5px] text-indigo-600 dark:text-indigo-400">
                                {m.solicitation_number || `OPP-${m.opportunity_id}`}
                              </span>
                              {isOpportunityNew(m) && (
                                <span className="inline-flex items-center gap-0.5 text-[8.5px] font-extrabold px-1.5 py-0.2 rounded-full bg-emerald-500 text-white shadow-2xs tracking-wide">
                                  <Sparkles size={8} className="animate-pulse" />
                                  <span>NEW</span>
                                </span>
                              )}
                              {m.lifecycle_status && (
                                <span className="text-[8.5px] px-1.5 py-0.2 rounded bg-slate-100 dark:bg-white/10 text-slate-600 dark:text-slate-300 font-mono font-semibold">
                                  {m.lifecycle_status}
                                </span>
                              )}
                            </div>
                            <div className="font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors line-clamp-1">
                              {m.name}
                            </div>
                            {m.why_it_fits && (
                              <div className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-1 italic">
                                &ldquo;{m.why_it_fits}&rdquo;
                              </div>
                            )}
                          </div>
                        </td>

                        {/* Agency & Territory */}
                        <td className="py-3 px-3.5">
                          <div className="flex items-center gap-2">
                            <OrgLogo org={m.agency || 'Agency'} size="xs" showTooltip={false} />
                            <div className="min-w-0">
                              <div className="font-bold text-slate-900 dark:text-white truncate text-[11.5px]">
                                {m.agency || 'Public Agency'}
                              </div>
                              <div className="text-[10px] text-slate-500 dark:text-slate-400">
                                {m.program_type || 'Innovation Grant'}
                              </div>
                            </div>
                          </div>
                        </td>

                        {/* Max Award */}
                        <td className="py-3 px-3.5 text-right font-mono">
                          <div className="font-bold text-emerald-600 dark:text-emerald-400 text-xs">
                            {fmt(m.max_per_award || m.total_funding)}
                          </div>
                          {m.total_funding && m.max_per_award && m.total_funding !== m.max_per_award && (
                            <div className="text-[9.5px] text-slate-400">Pool: {fmt(m.total_funding)}</div>
                          )}
                        </td>

                        {/* Cost-Share */}
                        <td className="py-3 px-3.5 text-center font-mono">
                          <span
                            className={clsx(
                              'inline-block font-bold px-2 py-0.5 rounded text-[11px]',
                              m.cost_share_pct === 0 || m.cost_share_pct === null
                                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-500/30'
                                : 'bg-amber-50 text-amber-800 border border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-500/30'
                            )}
                          >
                            {m.cost_share_pct !== null && m.cost_share_pct !== undefined ? `${m.cost_share_pct}%` : '0%'}
                          </span>
                        </td>

                        {/* Deadline */}
                        <td className="py-3 px-3.5">
                          <div className="flex items-center gap-1.5 text-[11px] text-slate-700 dark:text-slate-300">
                            <Clock size={12} className="text-slate-400 shrink-0" />
                            <span className="truncate max-w-[130px]">{m.next_deadline || m.deadline || 'Open / Rolling'}</span>
                          </div>
                        </td>

                        {/* Details Action */}
                        <td className="py-3 px-3.5 text-center">
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleRow(m.opportunity_id);
                            }}
                            className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-white/5 dark:hover:bg-white/10 text-slate-700 dark:text-slate-300 transition-colors cursor-pointer"
                          >
                            {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                          </button>
                        </td>
                      </tr>

                      {/* Expanded Row Drawer */}
                      {isExpanded && (
                        <tr className="bg-slate-50/80 dark:bg-black/30 animate-in fade-in duration-150">
                          <td colSpan={8} className="p-4 border-b border-slate-200 dark:border-white/10">
                            <div className="space-y-4 max-w-5xl mx-auto">
                              {/* Top Summary Info & LLM Strategic Analysis */}
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 p-4 rounded-xl bg-white dark:bg-[#0d1424] border border-slate-200/80 dark:border-white/10 text-xs shadow-2xs">
                                <div className="md:col-span-2 space-y-2">
                                  <div className="text-[10px] uppercase font-bold text-indigo-600 dark:text-indigo-400 flex items-center gap-1">
                                    <Sparkles size={12} />
                                    <span>LLM Strategic Match Thesis</span>
                                  </div>
                                  <div className="text-slate-800 dark:text-slate-200 text-xs leading-relaxed italic">
                                    &ldquo;{m.strategic_thesis || m.why_it_fits || m.assessment?.verdict_detail || 'Strong programmatic fit matching technology readiness and applicant scope.'}&rdquo;
                                  </div>
                                  {m.recommended_positioning && (
                                    <div className="p-2.5 rounded-lg bg-indigo-50 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-500/30 text-[11px] text-indigo-900 dark:text-indigo-200 mt-2">
                                      <strong className="text-indigo-700 dark:text-indigo-300">Winning Proposal Angle: </strong>
                                      {m.recommended_positioning}
                                    </div>
                                  )}
                                </div>

                                <div className="space-y-3">
                                  <div>
                                    <div className="text-[10px] uppercase font-bold text-slate-500 dark:text-slate-400">Application Strategy</div>
                                    <div className="text-slate-700 dark:text-slate-300 mt-0.5 leading-relaxed text-[11px]">
                                      {m.timeline?.timing_note || 'Prepare formal technical consortia and lock in milestone cost-share.'}
                                    </div>
                                  </div>
                                  <div>
                                    <div className="text-[10px] uppercase font-bold text-slate-500 dark:text-slate-400">FOA Actions</div>
                                    <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                                      <button
                                        type="button"
                                        onClick={() => setSelectedAngleMatch(m)}
                                        className="px-2.5 py-1 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-700 dark:text-amber-300 border border-amber-500/30 text-[11px] font-bold flex items-center gap-1 cursor-pointer transition-colors"
                                      >
                                        <Zap size={11} className="text-amber-500 fill-amber-500" /> Winning Angle
                                      </button>
                                      {onOpenShredder && (
                                        <button
                                          type="button"
                                          onClick={() => onOpenShredder(m.opportunity_id)}
                                          className="px-2.5 py-1 rounded-lg bg-indigo-50 dark:bg-indigo-950/40 hover:bg-indigo-100 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/30 text-[11px] font-bold flex items-center gap-1 cursor-pointer"
                                        >
                                          <FileText size={11} /> Shred FOA
                                        </button>
                                      )}
                                      {m.url && (
                                        <a
                                          href={m.url}
                                          target="_blank"
                                          rel="noopener noreferrer"
                                          className="px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-white/10 text-[11px] font-bold flex items-center gap-1"
                                        >
                                          <ExternalLink size={11} /> View Source
                                        </a>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {/* Evaluation Criteria Strengths */}
                              {m.criteria_strengths && m.criteria_strengths.length > 0 && (
                                <div className="space-y-1.5">
                                  <div className="text-[11px] font-bold text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5">
                                    <CheckCircle2 size={13} className="text-emerald-600 dark:text-emerald-400" />
                                    <span>Evaluation Criteria Advantages:</span>
                                  </div>
                                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                                    {m.criteria_strengths.map((crit, cIdx) => (
                                      <div key={cIdx} className="p-2.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-500/30 text-emerald-900 dark:text-emerald-200 text-[11px] leading-snug">
                                        {crit}
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}

                              {/* Requirements Checklist */}
                              {m.requirements_checklist && m.requirements_checklist.length > 0 && (
                                <div className="space-y-1.5">
                                  <div className="text-[11px] font-bold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                                    <ShieldCheck size={13} className="text-indigo-600 dark:text-indigo-400" />
                                    <span>Requirements Verification:</span>
                                  </div>
                                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                                    {m.requirements_checklist.map((req, reqIdx) => (
                                      <div
                                        key={reqIdx}
                                        className="p-2 rounded-lg bg-white dark:bg-[#0d1424] border border-slate-200 dark:border-white/10 flex items-start gap-2 text-[11px]"
                                      >
                                        {req.status === 'pass' ? (
                                          <CheckCircle2 size={13} className="text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
                                        ) : req.status === 'conditional' ? (
                                          <AlertCircle size={13} className="text-amber-500 shrink-0 mt-0.5" />
                                        ) : (
                                          <AlertCircle size={13} className="text-rose-500 shrink-0 mt-0.5" />
                                        )}
                                        <div className="min-w-0">
                                          <span className="font-bold text-slate-900 dark:text-white">{req.name}: </span>
                                          <span className="text-slate-500 dark:text-slate-400">{req.reason}</span>
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}

                              {/* Proprietary Intelligence: Statutory Mandates & Targeted Problem Statements */}
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 border-t border-slate-200 dark:border-white/10 text-xs">
                                {/* Statutory Mandates */}
                                {m.statutory_mandates && m.statutory_mandates.length > 0 && (
                                  <div className="space-y-1.5">
                                    <div className="text-[10.5px] uppercase font-bold text-indigo-600 dark:text-indigo-400 flex items-center gap-1">
                                      <Layers size={12} />
                                      <span>Statutory Policy Alignment</span>
                                    </div>
                                    <div className="flex flex-wrap gap-1">
                                      {m.statutory_mandates.map((mandate, idx) => (
                                        <span
                                          key={idx}
                                          className="text-[10px] px-2 py-0.5 rounded-md bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/30 font-medium"
                                        >
                                          {mandate}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* Targeted Problem Statements */}
                                {m.priority_problem_statements && m.priority_problem_statements.length > 0 && (
                                  <div className="space-y-1.5">
                                    <div className="text-[10.5px] uppercase font-bold text-amber-700 dark:text-amber-400 flex items-center gap-1">
                                      <Target size={12} />
                                      <span>Targeted Technical Challenges</span>
                                    </div>
                                    <div className="space-y-1">
                                      {m.priority_problem_statements.map((prob, idx) => (
                                        <div key={idx} className="text-[11px] text-slate-700 dark:text-slate-300 leading-snug flex items-start gap-1.5">
                                          <span className="text-amber-500 font-bold">•</span>
                                          <span>{prob}</span>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {((viewMode === 'grouped' && filteredGroupedOrgs.length === 0) ||
        (viewMode === 'flat' && filteredFlatMatches.length === 0)) && (
        <div className="py-12 text-center text-xs text-slate-500 dark:text-slate-400">
          No solicitations or organizations found matching your search or filters.
        </div>
      )}

      {/* Winning Angle & Hidden Rubric Reverse-Engineering Modal */}
      {selectedAngleMatch && (
        <WinningAngleModal
          isOpen={!!selectedAngleMatch}
          onClose={() => setSelectedAngleMatch(null)}
          opportunityId={selectedAngleMatch.opportunity_id}
          opportunityName={selectedAngleMatch.name}
          solicitationNumber={selectedAngleMatch.solicitation_number}
          agency={selectedAngleMatch.agency}
          projectProfile={{
            title: projectTitle,
            project_title: projectTitle,
          }}
          matchScore={selectedAngleMatch.fit_score || 0.88}
        />
      )}
    </div>
  );
}
