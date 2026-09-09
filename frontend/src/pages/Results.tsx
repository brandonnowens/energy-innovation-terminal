import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { api, OrganizationResultDossier, ResultArtifact } from '../api/client';
import {
  Scale, ShieldCheck, FileText, ExternalLink, Search,
  CheckCircle2, ChevronDown, ChevronRight, Building2,
  Award, Quote, FileCheck, ArrowUpDown, ArrowUpRight, RotateCcw,
  Layers, Target
} from 'lucide-react';
import clsx from 'clsx';
import { OrgLogo } from '../components/OrgLogo';
import { VenturePatentView } from '../components/VenturePatentView';
import { useNyserda } from '../context/NyserdaContext';

function formatCurrency(val: number | null | undefined): string {
  if (!val) return '$0';
  if (val >= 1_000_000_000) return `$${(val / 1_000_000_000).toFixed(2)}B`;
  if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(1)}M`;
  if (val >= 1_000) return `$${(val / 1_000).toFixed(0)}K`;
  return `$${val.toFixed(0)}`;
}

function formatNumber(val: number | null | undefined): string {
  if (!val) return '0';
  if (val >= 1_000_000) return `${(val / 1_000_000).toFixed(2)}M`;
  if (val >= 1_000) return `${(val / 1_000).toFixed(1)}K`;
  return val.toLocaleString();
}

export default function Results() {
  const { includeNyserda, isNyserda, isNyserdaAgency } = useNyserda();
  const [viewMode, setViewMode] = useState<'organizations' | 'benchmarks' | 'artifacts' | 'venture_patents'>('organizations');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAgency, setSelectedAgency] = useState<string>('ALL');
  const [selectedTech, setSelectedTech] = useState<string>('ALL');
  const [expandedOrg, setExpandedOrg] = useState<string | null>(null);

  // Benchmarks sorting
  const [bmSortBy, setBmSortBy] = useState('leverage_ratio');
  const [bmSortDir, setBmSortDir] = useState<'asc' | 'desc'>('desc');

  // Reset selected agency if NYSERDA is excluded
  React.useEffect(() => {
    if (!includeNyserda && (selectedAgency === 'NYSERDA' || isNyserdaAgency(selectedAgency))) {
      setSelectedAgency('ALL');
    }
  }, [includeNyserda, selectedAgency, isNyserdaAgency]);

  // Fetch summary KPIs
  const { data: summary } = useQuery({
    queryKey: ['results-summary'],
    queryFn: () => api.getResultsSummary(),
    staleTime: 5 * 60 * 1000,
  });

  // Fetch organizations with verified results
  const { data: orgData, isLoading: orgsLoading } = useQuery({
    queryKey: ['results-organizations'],
    queryFn: () => api.getOrganizationResults(),
    staleTime: 5 * 60 * 1000,
  });

  // Fetch benchmarked opportunities
  const { data: benchmarksData, isLoading: bmLoading } = useQuery({
    queryKey: ['results-benchmarks', bmSortBy, bmSortDir],
    queryFn: () => api.getBenchmarks({
      page: 1,
      page_size: 30,
      sort_by: bmSortBy,
      sort_dir: bmSortDir,
    }),
    enabled: viewMode === 'benchmarks',
    staleTime: 5 * 60 * 1000,
  });

  // Fetch verified artifacts
  const { data: artifactsData, isLoading: artsLoading } = useQuery({
    queryKey: ['results-artifacts'],
    queryFn: () => api.getResultArtifacts(),
    enabled: viewMode === 'artifacts',
    staleTime: 5 * 60 * 1000,
  });

  const allOrganizations = useMemo(() => {
    const orgs = orgData?.organizations || [];
    if (includeNyserda) return orgs;
    return orgs.filter(o => !isNyserda(o.recipient_name) && !isNyserdaAgency(o.agency));
  }, [orgData, includeNyserda, isNyserda, isNyserdaAgency]);

  const benchmarksList = useMemo(() => {
    const items = benchmarksData?.items || [];
    return items.filter(b => 
      (b.leverage_ratio > 0 || b.ghg_abatement_per_10k_usd > 0) &&
      (includeNyserda || (!isNyserdaAgency(b.agency) && !isNyserda(b.opportunity_name)))
    );
  }, [benchmarksData, includeNyserda, isNyserda, isNyserdaAgency]);

  const artifactsList = useMemo(() => {
    const arts: ResultArtifact[] = Array.isArray(artifactsData) ? artifactsData : (artifactsData as any)?.artifacts || [];
    if (includeNyserda) return arts;
    return arts.filter((a: ResultArtifact) => !isNyserdaAgency(a.agency) && !isNyserda(a.title));
  }, [artifactsData, includeNyserda, isNyserda, isNyserdaAgency]);

  // Derive active agencies dynamically from available data (never show empty agency buttons)
  const availableAgencies = useMemo(() => {
    const set = new Set<string>();
    allOrganizations.forEach(o => {
      if (o.agency && (includeNyserda || !isNyserdaAgency(o.agency))) set.add(o.agency);
    });
    return ['ALL', ...Array.from(set)];
  }, [allOrganizations, includeNyserda, isNyserdaAgency]);

  // Derive active tech areas dynamically from available data
  const availableTechAreas = useMemo(() => {
    const set = new Set<string>();
    allOrganizations.forEach(o => {
      if (o.technology_area) set.add(o.technology_area);
    });
    return Array.from(set);
  }, [allOrganizations]);

  // Client-side filtering to guarantee instant, responsive filtering
  const filteredOrganizations = useMemo(() => {
    return allOrganizations.filter(org => {
      if (selectedAgency !== 'ALL' && org.agency !== selectedAgency) {
        return false;
      }
      if (selectedTech !== 'ALL' && org.technology_area !== selectedTech) {
        return false;
      }
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesName = org.recipient_name.toLowerCase().includes(q);
        const matchesTech = org.technology_area.toLowerCase().includes(q);
        const matchesStory = org.success_story?.summary?.toLowerCase().includes(q) || false;
        const matchesArtifact = org.artifacts.some(a => a.title.toLowerCase().includes(q));
        if (!matchesName && !matchesTech && !matchesStory && !matchesArtifact) {
          return false;
        }
      }
      return true;
    });
  }, [allOrganizations, selectedAgency, selectedTech, searchQuery]);

  const resetFilters = () => {
    setSearchQuery('');
    setSelectedAgency('ALL');
    setSelectedTech('ALL');
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Standard Page Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <ShieldCheck size={12} />
              <span>Public Evidence &amp; Impact Audits</span>
            </span>
            <span className="text-xs text-slate-300">|</span>
            <span className="text-xs font-semibold text-slate-500">Verified Results Only</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2.5">
            Results &amp; Outcomes Intelligence
          </h1>
          <p className="text-[13px] sm:text-sm text-slate-500 max-w-3xl mt-1 leading-relaxed">
            Curated public regulatory filings, OSTI deliverables, and return-on-grant metrics for funded energy innovation and clean technology organizations.
          </p>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 shrink-0">
          <button
            onClick={() => setViewMode('organizations')}
            className={clsx(
              'flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg transition-all',
              viewMode === 'organizations'
                ? 'bg-white text-slate-900 shadow-2xs'
                : 'text-slate-600 hover:text-slate-900'
            )}
          >
            <Building2 size={13} />
            <span>Organizations ({allOrganizations.length})</span>
          </button>

          <button
            onClick={() => setViewMode('venture_patents')}
            className={clsx(
              'flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg transition-all',
              viewMode === 'venture_patents'
                ? 'bg-white text-slate-900 shadow-2xs'
                : 'text-slate-600 hover:text-slate-900'
            )}
          >
            <Layers size={13} className="text-amber-500" />
            <span>Venture &amp; Patents</span>
            <span className="px-1.5 py-0.2 rounded-full text-[9px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
              NEW
            </span>
          </button>

          <button
            onClick={() => setViewMode('benchmarks')}
            className={clsx(
              'flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg transition-all',
              viewMode === 'benchmarks'
                ? 'bg-white text-slate-900 shadow-2xs'
                : 'text-slate-600 hover:text-slate-900'
            )}
          >
            <Scale size={13} />
            <span>Benchmarks</span>
          </button>

          <button
            onClick={() => setViewMode('artifacts')}
            className={clsx(
              'flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg transition-all',
              viewMode === 'artifacts'
                ? 'bg-white text-slate-900 shadow-2xs'
                : 'text-slate-600 hover:text-slate-900'
            )}
          >
            <FileCheck size={13} />
            <span>Evidence Vault</span>
          </button>
        </div>
      </div>

      {/* Macro Metrics Strip */}
      {summary?.kpis && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="bg-white p-3.5 rounded-xl border border-slate-200/80 shadow-2xs">
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Total Capital Leveraged</div>
            <div className="text-lg font-bold font-mono text-indigo-700 mt-0.5">
              {formatCurrency(summary.kpis.total_leveraged_capital_usd)}
            </div>
          </div>

          <div className="bg-white p-3.5 rounded-xl border border-slate-200/80 shadow-2xs">
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Annual GHG Abated</div>
            <div className="text-lg font-bold font-mono text-emerald-700 mt-0.5">
              {formatNumber(summary.kpis.total_ghg_avoided_annual_mt)} MT CO2e
            </div>
          </div>

          <div className="bg-white p-3.5 rounded-xl border border-slate-200/80 shadow-2xs">
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Direct Clean Tech Jobs</div>
            <div className="text-lg font-bold font-mono text-blue-700 mt-0.5">
              {formatNumber(summary.kpis.total_jobs_created)} FTEs
            </div>
          </div>

          <div className="bg-white p-3.5 rounded-xl border border-slate-200/80 shadow-2xs">
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Patents &amp; Products</div>
            <div className="text-lg font-bold font-mono text-amber-700 mt-0.5">
              {(summary.kpis.total_patents_issued || 0) + (summary.kpis.total_commercial_products || 0)} Innovations
            </div>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="space-y-6">

        {/* ------------------------------------------------------------- */}
        {/* VIEW 0: VENTURE & PATENT COMMERCIALIZATION ATTRIBUTIONS       */}
        {/* ------------------------------------------------------------- */}
        {viewMode === 'venture_patents' && (
          <VenturePatentView />
        )}

        {/* ------------------------------------------------------------- */}
        {/* VIEW 1: ORGANIZATIONS WITH VERIFIED RESULTS (MINIMIZED)       */}
        {/* ------------------------------------------------------------- */}
        {viewMode === 'organizations' && (
          <div className="space-y-4">
            {/* Filters Bar */}
            <div className="bg-white p-3.5 rounded-xl border border-slate-200/80 shadow-2xs flex flex-col md:flex-row items-center justify-between gap-3">
              <div className="relative w-full md:w-80">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={14} />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Filter organizations..."
                  className="w-full pl-8 pr-4 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all placeholder:text-slate-400"
                />
              </div>

              <div className="flex items-center gap-2 w-full md:w-auto overflow-x-auto">
                {/* Dynamically derived agencies only */}
                <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg">
                  {availableAgencies.map((agency) => (
                    <button
                      key={agency}
                      onClick={() => setSelectedAgency(agency)}
                      className={clsx(
                        'px-2.5 py-1 text-[11px] font-bold rounded-md transition-all',
                        selectedAgency === agency
                          ? 'bg-white text-indigo-700 shadow-2xs'
                          : 'text-slate-600 hover:text-slate-900'
                      )}
                    >
                      {agency}
                    </button>
                  ))}
                </div>

                {/* Dynamically derived tech areas only */}
                {availableTechAreas.length > 0 && (
                  <select
                    value={selectedTech}
                    onChange={(e) => setSelectedTech(e.target.value)}
                    className="px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-semibold text-slate-700 focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20"
                  >
                    <option value="ALL">All Sectors</option>
                    {availableTechAreas.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                )}
              </div>
            </div>

            {/* Organizations Grid / Dossier Cards */}
            {orgsLoading ? (
              <div className="p-10 text-center bg-white rounded-xl border border-slate-200/80">
                <div className="inline-block animate-spin rounded-full h-7 w-7 border-3 border-indigo-600 border-t-transparent mb-2" />
                <div className="text-xs font-semibold text-slate-600">Loading dossiers...</div>
              </div>
            ) : filteredOrganizations.length === 0 ? (
              <div className="p-8 text-center bg-white rounded-xl border border-slate-200/80 space-y-2">
                <ShieldCheck size={28} className="mx-auto text-slate-300" />
                <div className="text-xs font-bold text-slate-700">No organizations match current filter</div>
                <button
                  onClick={resetFilters}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-indigo-50 text-indigo-700 text-xs font-bold hover:bg-indigo-100"
                >
                  <RotateCcw size={12} />
                  <span>Reset Filters</span>
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredOrganizations.map((org: OrganizationResultDossier, idx: number) => {
                  const isExpanded = expandedOrg === org.recipient_name;
                  const metrics = org.summary_metrics;

                  return (
                    <div
                      key={idx}
                      className="bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:border-indigo-200 transition-all overflow-hidden"
                    >
                      {/* Organization Header */}
                      <div className="p-4 sm:p-5 border-b border-slate-100 flex flex-col md:flex-row md:items-start md:justify-between gap-3">
                        <div className="space-y-1 max-w-3xl">
                          <div className="flex items-center gap-2.5 flex-wrap">
                            <OrgLogo org={org.recipient_name} size="sm" />
                            <span className="font-bold text-base sm:text-lg text-slate-900">
                              {org.recipient_name}
                            </span>
                            <span className={clsx(
                              'inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider',
                              org.agency === 'NYSERDA' ? 'bg-amber-100 text-amber-900' :
                              org.agency === 'CEC' ? 'bg-cyan-100 text-cyan-900' :
                              org.agency === 'DOE' ? 'bg-emerald-100 text-emerald-900' :
                              org.agency === 'ARPA-E' ? 'bg-purple-100 text-purple-900' :
                              'bg-blue-100 text-blue-900'
                            )}>
                              <OrgLogo org={org.agency} size="xs" />
                              <span>{org.agency} Verified</span>
                            </span>
                            <span className="text-[11px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                              {org.technology_area}
                            </span>
                          </div>

                          {org.success_story?.summary && (
                            <p className="text-[12px] text-slate-600 leading-relaxed">
                              {org.success_story.summary}
                            </p>
                          )}
                        </div>

                        {/* Actions */}
                        <div className="flex items-center gap-2 shrink-0">
                          {org.artifacts.length > 0 && (
                            <a
                              href={org.artifacts[0].source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 text-xs font-bold transition-all border border-indigo-200/70"
                            >
                              <FileText size={12} />
                              <span>Source PDF Report</span>
                              <ExternalLink size={10} />
                            </a>
                          )}

                          <button
                            onClick={() => setExpandedOrg(isExpanded ? null : org.recipient_name)}
                            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 text-xs font-bold transition-all"
                          >
                            <span>{isExpanded ? 'Hide' : 'Audit'}</span>
                            <ChevronDown size={12} className={clsx('transition-transform', isExpanded && 'rotate-180')} />
                          </button>
                        </div>
                      </div>

                      {/* Non-Empty Quantitative Highlights Only */}
                      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 p-3.5 bg-slate-50/40 border-b border-slate-100 text-xs">
                        {metrics.total_leveraged_capital_usd > 0 && (
                          <div className="p-2.5 bg-white rounded-lg border border-slate-200/70">
                            <div className="text-[9.5px] font-bold text-slate-400 uppercase tracking-wider">Follow-On Capital</div>
                            <div className="text-sm font-bold font-mono text-indigo-700 mt-0.5">
                              {formatCurrency(metrics.total_leveraged_capital_usd)}
                            </div>
                          </div>
                        )}

                        {metrics.total_ghg_avoided_annual_mt > 0 && (
                          <div className="p-2.5 bg-white rounded-lg border border-slate-200/70">
                            <div className="text-[9.5px] font-bold text-slate-400 uppercase tracking-wider">Annual GHG Abated</div>
                            <div className="text-sm font-bold font-mono text-emerald-700 mt-0.5">
                              {formatNumber(metrics.total_ghg_avoided_annual_mt)} MT
                            </div>
                          </div>
                        )}

                        {metrics.total_clean_energy_mwh_yr > 0 && (
                          <div className="p-2.5 bg-white rounded-lg border border-slate-200/70">
                            <div className="text-[9.5px] font-bold text-slate-400 uppercase tracking-wider">Energy Innovation</div>
                            <div className="text-sm font-bold font-mono text-cyan-700 mt-0.5">
                              {formatNumber(metrics.total_clean_energy_mwh_yr)} MWh
                            </div>
                          </div>
                        )}

                        {metrics.total_jobs_created > 0 && (
                          <div className="p-2.5 bg-white rounded-lg border border-slate-200/70">
                            <div className="text-[9.5px] font-bold text-slate-400 uppercase tracking-wider">Clean Tech Jobs</div>
                            <div className="text-sm font-bold font-mono text-blue-700 mt-0.5">
                              {metrics.total_jobs_created} FTEs
                            </div>
                          </div>
                        )}

                        {metrics.total_patents_issued > 0 && (
                          <div className="p-2.5 bg-white rounded-lg border border-slate-200/70">
                            <div className="text-[9.5px] font-bold text-slate-400 uppercase tracking-wider">Patents Granted</div>
                            <div className="text-sm font-bold font-mono text-amber-700 mt-0.5">
                              {metrics.total_patents_issued} Patents
                            </div>
                          </div>
                        )}

                        {metrics.avg_trl_advancement > 0 && (
                          <div className="p-2.5 bg-white rounded-lg border border-slate-200/70">
                            <div className="text-[9.5px] font-bold text-slate-400 uppercase tracking-wider">TRL Jump</div>
                            <div className="text-sm font-bold font-mono text-purple-700 mt-0.5">
                              +{metrics.avg_trl_advancement} TRL
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Direct Evidence Artifacts (Rendered directly with findings) */}
                      {org.artifacts.length > 0 && (
                        <div className="p-3.5 bg-indigo-50/20 border-b border-slate-100 space-y-2">
                          <div className="flex items-center gap-1.5 text-[10.5px] font-bold text-slate-500 uppercase tracking-wider">
                            <FileCheck size={12} className="text-indigo-600" />
                            <span>Audit Source Artifacts</span>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                            {org.artifacts.map((art: ResultArtifact, artIdx: number) => (
                              <div
                                key={artIdx}
                                className="p-3 bg-white rounded-lg border border-indigo-100 shadow-2xs flex flex-col justify-between"
                              >
                                <div className="space-y-1">
                                  <div className="flex items-start justify-between gap-2">
                                    <span className="font-bold text-[11.5px] text-slate-900 leading-snug">
                                      {art.title}
                                    </span>
                                    <span className="text-[9.5px] font-bold px-1.5 py-0.2 bg-slate-100 text-slate-700 rounded uppercase shrink-0">
                                      {art.artifact_type.replace(/_/g, ' ')}
                                    </span>
                                  </div>

                                  {art.summary && (
                                    <p className="text-[11px] text-slate-600 line-clamp-2">
                                      {art.summary}
                                    </p>
                                  )}

                                  {(() => {
                                    let findings: any = art.key_findings;
                                    if (typeof findings === 'string') {
                                      try { findings = JSON.parse(findings); } catch { findings = [findings]; }
                                    }
                                    if (!Array.isArray(findings) || findings.length === 0) return null;
                                    return (
                                      <div className="mt-1.5 space-y-0.5 bg-slate-50 p-2 rounded text-[10.5px] text-slate-600">
                                        {findings.slice(0, 2).map((f: string, fi: number) => (
                                          <div key={fi} className="flex items-center gap-1">
                                            <span className="text-indigo-500 font-bold">•</span>
                                            <span>{f}</span>
                                          </div>
                                        ))}
                                      </div>
                                    );
                                  })()}
                                </div>

                                <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between text-[11px]">
                                  <span className="text-slate-400 font-mono text-[10px]">
                                    {art.doi ? `DOI: ${art.doi}` : (art.page_count ? `${art.page_count} Pages` : 'Public Record')}
                                  </span>
                                  <a
                                    href={art.source_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center gap-1 font-bold text-indigo-600 hover:text-indigo-800"
                                  >
                                    <span>Access PDF / Record</span>
                                    <ExternalLink size={10} />
                                  </a>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Expandable Audit Details */}
                      {isExpanded && (
                        <div className="p-4 space-y-4 bg-white border-t border-slate-100">
                          {org.success_story?.quote_text && (
                            <div className="p-3.5 bg-gradient-to-r from-indigo-50/60 to-purple-50/40 rounded-lg border border-indigo-100/80">
                              <div className="flex items-start gap-2">
                                <Quote size={15} className="text-indigo-400 shrink-0 mt-0.5" />
                                <div>
                                  <p className="text-[12px] italic font-medium text-indigo-950">
                                    "{org.success_story.quote_text}"
                                  </p>
                                  {org.success_story.quote_author && (
                                    <div className="text-[10.5px] font-bold text-indigo-700 mt-0.5">
                                      — {org.success_story.quote_author}
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          )}

                          {/* Linked Solicitations */}
                          {org.linked_opportunities.length > 0 && (
                            <div>
                              <div className="text-[10.5px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                                Linked Solicitations
                              </div>
                              <div className="flex flex-wrap gap-2">
                                {org.linked_opportunities.map((opp, oppIdx) => (
                                  <Link
                                    key={oppIdx}
                                    to={`/opportunities/${opp.id}`}
                                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 text-[11px] font-semibold text-slate-700 border border-slate-200 transition-all"
                                  >
                                    <Award size={11} className="text-indigo-600" />
                                    <span>{opp.solicitation_number}: {opp.name}</span>
                                    <ChevronRight size={10} className="text-slate-400" />
                                  </Link>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Granular Audit Ledger */}
                          {org.metrics.length > 0 && (
                            <div>
                              <div className="text-[10.5px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                                Verified Metrics Ledger
                              </div>
                              <div className="overflow-x-auto border border-slate-200 rounded-lg">
                                <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
                                  <thead className="bg-slate-50 text-[10.5px] font-bold text-slate-500 uppercase">
                                    <tr>
                                      <th className="px-3 py-2">Metric</th>
                                      <th className="px-3 py-2">Canonical Value</th>
                                      <th className="px-3 py-2">Reported Raw String</th>
                                      <th className="px-3 py-2">Provenance</th>
                                    </tr>
                                  </thead>
                                  <tbody className="divide-y divide-slate-100">
                                    {org.metrics.map((m, mIdx) => (
                                      <tr key={mIdx} className="hover:bg-slate-50/60">
                                        <td className="px-3 py-2 font-semibold text-slate-800">
                                          {m.reported_metric_name || m.canonical_metric_name}
                                        </td>
                                        <td className="px-3 py-2 font-mono font-bold text-indigo-700">
                                          {m.canonical_unit === 'USD' ? formatCurrency(m.canonical_value) : `${m.canonical_value.toLocaleString()} ${m.canonical_unit}`}
                                        </td>
                                        <td className="px-3 py-2 font-mono text-slate-600">
                                          {m.raw_metric_value_str || '—'}
                                        </td>
                                        <td className="px-3 py-2">
                                          <span className="inline-flex items-center gap-1 text-[10.5px] text-emerald-700 font-semibold">
                                            <CheckCircle2 size={10} />
                                            <span>{m.data_provenance.replace(/_/g, ' ')}</span>
                                          </span>
                                        </td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* ------------------------------------------------------------- */}
        {/* VIEW 2: OPPORTUNITY BENCHMARKS (SORTABLE, NON-EMPTY)          */}
        {/* ------------------------------------------------------------- */}
        {viewMode === 'benchmarks' && (
          <div className="bg-white rounded-xl border border-slate-200/80 shadow-2xs overflow-hidden">
            <div className="p-4 border-b border-slate-100 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-bold text-slate-900">Apples-to-Apples Opportunity Benchmarking Index</h2>
                <p className="text-[11px] text-slate-500">
                  Normalized return-on-grant ratios across funding solicitations.
                </p>
              </div>
            </div>

            {bmLoading ? (
              <div className="p-10 text-center">
                <div className="inline-block animate-spin rounded-full h-7 w-7 border-3 border-indigo-600 border-t-transparent mb-2" />
                <div className="text-xs font-semibold text-slate-600">Loading benchmark rankings...</div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
                  <thead className="bg-slate-50 text-[10.5px] font-bold text-slate-500 uppercase tracking-wider">
                    <tr>
                      <th className="px-3.5 py-2.5">Solicitation</th>
                      <th className="px-3.5 py-2.5">Agency</th>
                      <th
                        className="px-3.5 py-2.5 cursor-pointer hover:bg-slate-100"
                        onClick={() => {
                          setBmSortBy('leverage_ratio');
                          setBmSortDir(bmSortDir === 'desc' ? 'asc' : 'desc');
                        }}
                      >
                        <div className="flex items-center gap-1">
                          <span>Leverage Multiplier</span>
                          <ArrowUpDown size={10} />
                        </div>
                      </th>
                      <th
                        className="px-3.5 py-2.5 cursor-pointer hover:bg-slate-100"
                        onClick={() => {
                          setBmSortBy('ghg_abatement_per_10k_usd');
                          setBmSortDir(bmSortDir === 'desc' ? 'asc' : 'desc');
                        }}
                      >
                        <div className="flex items-center gap-1">
                          <span>GHG / $10k Awarded</span>
                          <ArrowUpDown size={10} />
                        </div>
                      </th>
                      <th className="px-3.5 py-2.5">Awards Tracked</th>
                      <th className="px-3.5 py-2.5 text-right">Dossier</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {benchmarksList.map((b) => (
                      <tr key={b.id} className="hover:bg-slate-50/70 transition-colors">
                        <td className="px-3.5 py-2.5">
                          <Link to={`/opportunities/${b.opportunity_id}`} className="font-semibold text-slate-900 hover:text-indigo-600">
                            {b.solicitation_number}
                          </Link>
                          <div className="text-[11px] text-slate-500 line-clamp-1">{b.opportunity_name}</div>
                        </td>
                        <td className="px-3.5 py-2.5">
                          <div className="flex items-center gap-1.5">
                            <OrgLogo org={b.agency} size="xs" />
                            <span className="font-semibold text-slate-700">{b.agency}</span>
                          </div>
                        </td>
                        <td className="px-3.5 py-2.5 font-mono font-bold text-indigo-700">
                          {b.leverage_ratio.toFixed(2)}x
                        </td>
                        <td className="px-3.5 py-2.5 font-mono font-semibold text-emerald-700">
                          {b.ghg_abatement_per_10k_usd > 0 ? `${b.ghg_abatement_per_10k_usd.toFixed(2)} MT` : '—'}
                        </td>
                        <td className="px-3.5 py-2.5 text-slate-600 font-mono">
                          {b.total_awards_tracked} awards
                        </td>
                        <td className="px-3.5 py-2.5 text-right">
                          <Link
                            to={`/opportunities/${b.opportunity_id}`}
                            className="inline-flex items-center gap-1 text-[11px] font-bold text-indigo-600 hover:text-indigo-800"
                          >
                            <span>View</span>
                            <ArrowUpRight size={11} />
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* ------------------------------------------------------------- */}
        {/* VIEW 3: EVIDENCE VAULT (ALL CATALOGED PDF REPORTS)            */}
        {/* ------------------------------------------------------------- */}
        {viewMode === 'artifacts' && (
          <div className="space-y-3">
            <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs">
              <h2 className="text-sm font-bold text-slate-900">Scraped Public Reports & Regulatory Filings</h2>
              <p className="text-[11px] text-slate-500">
                Official documents supporting all verified claims in the Results Database.
              </p>
            </div>

            {artsLoading ? (
              <div className="p-10 text-center bg-white rounded-xl border border-slate-200/80">
                <div className="inline-block animate-spin rounded-full h-7 w-7 border-3 border-indigo-600 border-t-transparent mb-2" />
                <div className="text-xs font-semibold text-slate-600">Loading artifacts...</div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {artifactsList.map((art: ResultArtifact) => (
                  <div
                    key={art.id}
                    className="p-3.5 bg-white rounded-xl border border-slate-200/90 shadow-2xs hover:border-indigo-300 transition-all flex flex-col justify-between"
                  >
                    <div className="space-y-1.5">
                      <div className="flex items-start justify-between gap-2">
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[9.5px] font-bold uppercase bg-slate-100 text-slate-700">
                          <OrgLogo org={art.agency || 'Public Filer'} size="xs" />
                          <span>{art.agency || 'Public Filer'}</span>
                        </span>
                        <span className="text-[9.5px] font-semibold text-slate-400">
                          {art.publication_date || '2024'}
                        </span>
                      </div>

                      <h3 className="font-bold text-[12px] text-slate-900 leading-snug">
                        {art.title}
                      </h3>

                      {art.summary && (
                        <p className="text-[11px] text-slate-600 leading-relaxed line-clamp-3">
                          {art.summary}
                        </p>
                      )}
                    </div>

                    <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
                      <span className="text-slate-400 text-[10px] font-mono">
                        {art.doi ? `DOI: ${art.doi}` : (art.page_count ? `${art.page_count} Pages` : 'Public Record')}
                      </span>
                      <a
                        href={art.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 font-bold text-indigo-600 hover:text-indigo-800 text-[11px]"
                      >
                        <span>Open Document</span>
                        <ExternalLink size={10} />
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
