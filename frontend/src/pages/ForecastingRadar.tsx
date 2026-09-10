import React, { useState, useEffect, useMemo } from 'react';
import {
  Radio,
  Calendar,
  Clock,
  DollarSign,
  Building2,
  CheckCircle2,
  Layers,
  Search,
  Filter,
  ArrowRight,
  TrendingUp,
  ShieldCheck,
  Zap,
  Target,
  FileCheck,
  AlertCircle,
  ExternalLink,
  ChevronRight,
  ChevronLeft,
  RefreshCw,
  Compass,
  Landmark,
  X,
  MapPin,
  Activity,
  Award,
  BookOpen,
  Info,
  FileText
} from 'lucide-react';
import clsx from 'clsx';
import { API_BASE_URL } from '../api/client';
import { OrgLogo } from '../components/OrgLogo';
import { WinningAngleModal } from '../components/WinningAngleModal';

export interface CadenceStats {
  mean_interval_months: number;
  std_dev_months: number;
  regularity_score: number;
  peak_quarter: string;
  sample_size: number;
  historical_years?: number[];
  quarter_distribution?: Record<string, number>;
}

export interface ForecastOrganization {
  organization_id: number;
  organization_code: string;
  organization_name: string;
  full_name: string;
  category: 'state' | 'federal' | 'utility' | 'foundation' | 'university' | 'economic_development' | string;
  category_label: string;
  state: string;
  jurisdiction: string;
  total_pipeline_funding: number;
  upcoming_opportunities_count: number;
  next_release_horizon: string;
  min_days_until_release: number;
  primary_mandate: string;
  technologies_funded: string[];
  historical_opportunity_count?: number;
  cadence_regularity_score?: number;
  cadence_stats?: CadenceStats;
  disclaimer?: string;
}

export interface ForecastItem {
  id: string;
  predicted_title: string;
  agency: string;
  agency_code: string;
  organization_name: string;
  organization_category: string;
  organization_category_label: string;
  organization_state: string;
  organization_jurisdiction: string;
  program_division: string;
  forecasted_release_window: string;
  days_until_release: number;
  confidence_score: number;
  confidence_tier: string;
  cadence_regularity_score?: number;
  historical_predecessor: string;
  recurrence_cadence: string;
  projected_funding_envelope: string;
  projected_funding_range?: { min: number; expected: number; max: number };
  projected_max_award: number;
  projected_typical_award?: number;
  expected_cost_share_pct?: number;
  statutory_driver: string;
  targeted_technologies: string[];
  targeted_sectors: string[];
  eligible_applicants: string[];
  pre_positioning_playbook: string[];
  strategic_rationale: string;
  cadence_stats?: CadenceStats;
  disclaimer?: string;
}

export interface BriefingData {
  status: string;
  organization_code: string;
  organization_name: string;
  category: string;
  jurisdiction: string;
  forecasted_release_window: string;
  days_until_release: number;
  cadence_regularity_score: number;
  projected_total_pipeline: number;
  briefing: string;
  pre_positioning_playbook: string[];
  disclaimer: string;
}

function fmtMoney(n: number): string {
  if (n >= 1_000_000_000) return `$${(n / 1_000_000_000).toFixed(2)}B`;
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(0)}M`;
  if (n >= 1_000) return `$${(n / 1_000).toFixed(0)}k`;
  return `$${n.toLocaleString()}`;
}

export function ForecastingRadar() {
  const [organizations, setOrganizations] = useState<ForecastOrganization[]>([]);
  const [forecasts, setForecasts] = useState<ForecastItem[]>([]);
  const [loadingOrgs, setLoadingOrgs] = useState(true);
  const [loadingForecasts, setLoadingForecasts] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [selectedOrgCode, setSelectedOrgCode] = useState<string>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedLocation, setSelectedLocation] = useState<string>('all');
  const [selectedHorizon, setSelectedHorizon] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [completedSteps, setCompletedSteps] = useState<Record<string, boolean>>({});

  // Org Picker Pagination
  const [orgPage, setOrgPage] = useState(1);
  const orgsPerPage = 12;

  // Winning Angle modal state
  const [selectedAngleOpp, setSelectedAngleOpp] = useState<ForecastItem | null>(null);

  // AI Strategic Briefing Modal State
  const [briefingModalOpen, setBriefingModalOpen] = useState(false);
  const [briefingLoading, setBriefingLoading] = useState(false);
  const [briefingData, setBriefingData] = useState<BriefingData | null>(null);

  useEffect(() => {
    fetchOrganizations();
  }, []);

  useEffect(() => {
    fetchRadar();
    setOrgPage(1);
  }, [selectedOrgCode, selectedCategory, selectedLocation, selectedHorizon, searchQuery]);

  const fetchOrganizations = async () => {
    setLoadingOrgs(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/forecasting/organizations`);
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const data = await res.json();
      setOrganizations(data.organizations || []);
    } catch (err: any) {
      console.error('Error fetching organizations directory:', err);
    } finally {
      setLoadingOrgs(false);
    }
  };

  const fetchRadar = async () => {
    setLoadingForecasts(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (selectedOrgCode !== 'all') params.append('organization', selectedOrgCode);
      if (selectedCategory !== 'all') params.append('category', selectedCategory);
      if (selectedLocation !== 'all') params.append('location', selectedLocation);
      if (selectedHorizon !== 'all') params.append('horizon', selectedHorizon);
      if (searchQuery.trim()) params.append('search', searchQuery.trim());
      params.append('limit', '100');

      const res = await fetch(`${API_BASE_URL}/api/forecasting/radar?${params.toString()}`);
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const data = await res.json();
      setForecasts(data.forecasts || []);
    } catch (err: any) {
      console.error('Error fetching forecasting radar:', err);
      setError('Unable to load solicitation release forecasts.');
    } finally {
      setLoadingForecasts(false);
    }
  };

  const openBriefingModal = async (orgCode: string) => {
    setBriefingModalOpen(true);
    setBriefingLoading(true);
    setBriefingData(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/forecasting/briefing/${encodeURIComponent(orgCode)}`);
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const data = await res.json();
      setBriefingData(data);
    } catch (err) {
      console.error('Error fetching briefing:', err);
    } finally {
      setBriefingLoading(false);
    }
  };

  const toggleStep = (key: string) => {
    setCompletedSteps((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  // Selected Organization Object
  const activeOrg = useMemo(() => {
    if (selectedOrgCode === 'all') return null;
    return (
      organizations.find(
        (o) =>
          o.organization_code.toLowerCase() === selectedOrgCode.toLowerCase() ||
          o.organization_name.toLowerCase() === selectedOrgCode.toLowerCase()
      ) || null
    );
  }, [selectedOrgCode, organizations]);

  // Filtered organizations for the picker carousel
  const filteredOrganizations = useMemo(() => {
    return organizations.filter((org) => {
      if (selectedCategory !== 'all' && org.category !== selectedCategory) return false;
      if (selectedLocation !== 'all') {
        const loc = selectedLocation.toLowerCase();
        if (!org.state?.toLowerCase().includes(loc) && !org.jurisdiction?.toLowerCase().includes(loc)) {
          return false;
        }
      }
      if (!searchQuery.trim()) return true;
      const q = searchQuery.toLowerCase();
      return (
        org.organization_name.toLowerCase().includes(q) ||
        org.full_name.toLowerCase().includes(q) ||
        org.organization_code.toLowerCase().includes(q) ||
        org.jurisdiction.toLowerCase().includes(q) ||
        org.primary_mandate.toLowerCase().includes(q) ||
        org.technologies_funded.some((t) => t.toLowerCase().includes(q))
      );
    });
  }, [organizations, selectedCategory, selectedLocation, searchQuery]);

  // Paginated organizations for the picker grid
  const paginatedOrganizations = useMemo(() => {
    const start = (orgPage - 1) * orgsPerPage;
    return filteredOrganizations.slice(start, start + orgsPerPage);
  }, [filteredOrganizations, orgPage]);

  const totalOrgPages = Math.ceil(filteredOrganizations.length / orgsPerPage);

  const categories = [
    { id: 'all', label: 'All Organizations' },
    { id: 'state', label: 'State Energy Agencies' },
    { id: 'federal', label: 'Federal Funding Agencies' },
    { id: 'utility', label: 'Electric & Gas Utilities' },
    { id: 'foundation', label: 'Philanthropic Foundations' },
    { id: 'university', label: 'Universities & Research' },
    { id: 'economic_development', label: 'Economic Development' },
  ];

  const locations = [
    { id: 'all', label: 'All Jurisdictions' },
    { id: 'NY', label: 'New York' },
    { id: 'CA', label: 'California' },
    { id: 'MA', label: 'Massachusetts' },
    { id: 'US', label: 'Federal / Nationwide' },
  ];

  const horizons = [
    { id: 'all', label: 'All Horizons' },
    { id: '30_days', label: 'Next 30 Days' },
    { id: '90_days', label: 'Next 90 Days' },
    { id: '2026', label: '2026 Releases' },
    { id: '2027', label: '2027 Releases' },
  ];

  const totalTrackedPipeline = useMemo(() => {
    return organizations.reduce((acc, o) => acc + (o.total_pipeline_funding || 0), 0);
  }, [organizations]);

  return (
    <div className="space-y-6 pb-16">
      {/* Flagship Header Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-indigo-950 to-[#0c1220] border border-white/10 p-6 sm:p-8 text-white shadow-2xl">
        <div className="relative z-10 max-w-4xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-400/30 text-indigo-300 text-xs font-mono font-bold tracking-wide uppercase">
            <Radio size={14} className="animate-pulse text-indigo-400" />
            <span>The Early-Warning Radar</span>
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
            <span>All 250 Database Organizations Analyzed</span>
          </div>

          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
            Upcoming Solicitations by Target Organization
          </h1>

          <p className="text-slate-300 text-xs sm:text-sm leading-relaxed max-w-3xl">
            Statistical release cadences and opportunity release projections across all {organizations.length || 250} tracked funding agencies, state authorities, utilities, and research anchors. Modeled from historical PostgreSQL transaction ledgers, statutory appropriations (IRA, BIL, CLCPA, CEF, EPIC), and regulatory dockets.
          </p>

          {/* Metric Stats Banner */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3">
            <div className="p-3 rounded-2xl bg-white/5 border border-white/10">
              <div className="text-[11px] font-mono text-slate-400">Database Organizations</div>
              <div className="text-lg sm:text-xl font-bold font-mono text-white">
                {organizations.length > 0 ? `${organizations.length} Entities` : '250 Entities'}
              </div>
            </div>
            <div className="p-3 rounded-2xl bg-white/5 border border-white/10">
              <div className="text-[11px] font-mono text-slate-400">Total Tracked Pipeline</div>
              <div className="text-lg sm:text-xl font-bold font-mono text-emerald-400">
                {fmtMoney(totalTrackedPipeline || 1220000000)}
              </div>
            </div>
            <div className="p-3 rounded-2xl bg-white/5 border border-white/10">
              <div className="text-[11px] font-mono text-slate-400">Forecast Lead Time</div>
              <div className="text-lg sm:text-xl font-bold font-mono text-indigo-300">30 Days – 18 Mo.</div>
            </div>
            <div className="p-3 rounded-2xl bg-white/5 border border-white/10">
              <div className="text-[11px] font-mono text-slate-400">Cadence Regularity</div>
              <div className="text-lg sm:text-xl font-bold font-mono text-amber-300">80% – 96% Empirical</div>
            </div>
          </div>
        </div>
      </div>

      {/* ─── PROBABILISTIC FORECAST & PUBLIC INFORMATION DISCLAIMER BANNER ─────────── */}
      <div className="p-4 sm:p-5 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-900 dark:text-amber-200 text-xs shadow-xs space-y-1.5">
        <div className="flex items-center gap-2 font-bold font-mono tracking-wide uppercase text-amber-700 dark:text-amber-300">
          <AlertCircle size={16} className="text-amber-500 shrink-0" />
          <span>Probabilistic Forecast &amp; Public Information Integrity Notice</span>
          <span className="ml-auto hidden sm:inline-block px-2 py-0.5 rounded-full text-[10px] bg-amber-500/20 text-amber-800 dark:text-amber-200 font-mono font-bold">
            Statistical Models &bull; Not Guarantees
          </span>
        </div>
        <p className="text-[11.5px] text-slate-700 dark:text-slate-300 leading-relaxed">
          All solicitation release projections, timing horizons, and funding envelopes displayed on the Early-Warning Radar are <strong>probabilistic statistical estimates and heuristic models</strong> calculated from publicly available historical filings, statutory appropriations (IRA, BIL, CLCPA, CEF, EPIC), and regulatory dockets. They are <strong>NOT guarantees, commitments, or official announcements</strong> by funding entities, and contain zero non-public or confidential information.
        </p>
      </div>

      {/* ─── THE ORGANIZATION PICKER HUB ───────────────────────────────────────── */}
      <div className="rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-[#0d1424] p-5 shadow-2xs space-y-4">
        {/* Top Controls: Search, Category & Location */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/20">
              <Building2 size={18} />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <span>Select Target Organization</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/30">
                  {filteredOrganizations.length} of {organizations.length} Entities
                </span>
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Filter and click any organization to explore upcoming grant programs, statutory releases, and cadence metrics.
              </p>
            </div>
          </div>

          {/* Search Box */}
          <div className="relative w-full md:w-80">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search 250 organizations, utilities & topics..."
              className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-50 dark:bg-black/20 border border-slate-200 dark:border-white/10 text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery('')}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-white cursor-pointer"
              >
                <X size={13} />
              </button>
            )}
          </div>
        </div>

        {/* Filter Badges: Category & Jurisdiction */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1 border-t border-slate-100 dark:border-white/5">
          {/* Category Tabs */}
          <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs font-semibold overflow-x-auto">
            {categories.map((c) => (
              <button
                key={c.id}
                type="button"
                onClick={() => setSelectedCategory(c.id)}
                className={clsx(
                  'px-3 py-1.5 rounded-lg transition-colors whitespace-nowrap cursor-pointer',
                  selectedCategory === c.id
                    ? 'bg-white dark:bg-[#11192e] text-indigo-600 dark:text-indigo-400 shadow-2xs font-bold'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                )}
              >
                {c.label}
              </button>
            ))}
          </div>

          {/* Location / Jurisdiction Selector */}
          <div className="flex items-center gap-1.5 overflow-x-auto">
            <span className="text-[11px] font-mono text-slate-400 shrink-0 flex items-center gap-1">
              <MapPin size={12} /> Region:
            </span>
            {locations.map((loc) => (
              <button
                key={loc.id}
                type="button"
                onClick={() => setSelectedLocation(loc.id)}
                className={clsx(
                  'px-2.5 py-1 rounded-lg text-xs font-medium transition-colors cursor-pointer whitespace-nowrap',
                  selectedLocation === loc.id
                    ? 'bg-indigo-600 text-white font-bold'
                    : 'bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-white/10'
                )}
              >
                {loc.label}
              </button>
            ))}
          </div>
        </div>

        {/* Organization Selection Grid / Cards */}
        {loadingOrgs ? (
          <div className="py-12 text-center text-xs text-slate-400 flex flex-col items-center justify-center gap-2">
            <RefreshCw size={24} className="animate-spin text-indigo-500" />
            <span>Loading complete database organization taxonomy (250 entities)...</span>
          </div>
        ) : filteredOrganizations.length === 0 ? (
          <div className="py-8 text-center text-xs text-slate-400">
            No organizations match the selected filters. Try broadening your search.
          </div>
        ) : (
          <div className="space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 pt-2">
              {/* "All Organizations" Option Card */}
              {orgPage === 1 && (
                <div
                  onClick={() => setSelectedOrgCode('all')}
                  className={clsx(
                    'p-3.5 rounded-xl border text-xs cursor-pointer transition-all flex items-center justify-between gap-3',
                    selectedOrgCode === 'all'
                      ? 'bg-indigo-50/90 dark:bg-indigo-950/40 border-indigo-500 ring-2 ring-indigo-500/20 shadow-sm'
                      : 'bg-slate-50/60 dark:bg-[#0c1220] border-slate-200 dark:border-white/10 hover:border-slate-300 dark:hover:border-white/20'
                  )}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold font-mono text-xs shrink-0">
                      ALL
                    </div>
                    <div className="min-w-0">
                      <div className="font-bold text-slate-900 dark:text-white truncate">
                        All Organizations
                      </div>
                      <div className="text-[11px] text-slate-500 dark:text-slate-400">
                        {forecasts.length} Total Releases
                      </div>
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400 text-xs">
                      {fmtMoney(totalTrackedPipeline)}
                    </span>
                  </div>
                </div>
              )}

              {/* Individual Organization Cards */}
              {paginatedOrganizations.map((org) => {
                const isSelected =
                  selectedOrgCode.toLowerCase() === org.organization_code.toLowerCase() ||
                  selectedOrgCode.toLowerCase() === org.organization_name.toLowerCase();

                return (
                  <div
                    key={org.organization_id || org.organization_code}
                    onClick={() => setSelectedOrgCode(org.organization_code)}
                    className={clsx(
                      'p-3.5 rounded-xl border text-xs cursor-pointer transition-all flex items-center justify-between gap-3',
                      isSelected
                        ? 'bg-indigo-50/90 dark:bg-indigo-950/40 border-indigo-500 ring-2 ring-indigo-500/20 shadow-sm'
                        : 'bg-slate-50/60 dark:bg-[#0c1220] border-slate-200 dark:border-white/10 hover:border-slate-300 dark:hover:border-white/20'
                    )}
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <OrgLogo org={org.organization_code} size="sm" showTooltip={false} />
                      <div className="min-w-0">
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <span className="font-bold text-slate-900 dark:text-white truncate" title={org.full_name}>
                            {org.organization_name}
                          </span>
                          <span className="text-[9.5px] px-1.5 py-0.2 rounded font-mono font-bold bg-slate-200/80 text-slate-700 dark:bg-white/10 dark:text-slate-300">
                            {org.state || 'US'}
                          </span>
                        </div>
                        <div className="text-[10.5px] text-slate-500 dark:text-slate-400 truncate flex items-center gap-1 mt-0.5">
                          <span>{org.upcoming_opportunities_count} Upcoming</span>
                          {org.cadence_regularity_score && (
                            <span className="text-[9.5px] font-mono text-indigo-600 dark:text-indigo-400 font-bold">
                              &bull; {org.cadence_regularity_score}% Reg.
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="text-right shrink-0">
                      <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400 text-xs block">
                        {fmtMoney(org.total_pipeline_funding)}
                      </span>
                      <span className="text-[9.5px] text-slate-400 font-mono">
                        {org.next_release_horizon?.split(' ')[0] || '2026/2027'}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Pagination Controls */}
            {totalOrgPages > 1 && (
              <div className="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-white/5 text-xs">
                <span className="text-slate-500 dark:text-slate-400 font-mono text-[11px]">
                  Showing {(orgPage - 1) * orgsPerPage + 1}–{Math.min(orgPage * orgsPerPage, filteredOrganizations.length)} of {filteredOrganizations.length} organizations
                </span>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    disabled={orgPage <= 1}
                    onClick={() => setOrgPage((p) => Math.max(1, p - 1))}
                    className="p-1.5 rounded-lg border border-slate-200 dark:border-white/10 text-slate-600 dark:text-slate-300 disabled:opacity-40 hover:bg-slate-100 dark:hover:bg-white/5 cursor-pointer disabled:cursor-not-allowed"
                  >
                    <ChevronLeft size={14} />
                  </button>
                  <span className="font-mono text-xs text-slate-700 dark:text-slate-300">
                    Page {orgPage} / {totalOrgPages}
                  </span>
                  <button
                    type="button"
                    disabled={orgPage >= totalOrgPages}
                    onClick={() => setOrgPage((p) => Math.min(totalOrgPages, p + 1))}
                    className="p-1.5 rounded-lg border border-slate-200 dark:border-white/10 text-slate-600 dark:text-slate-300 disabled:opacity-40 hover:bg-slate-100 dark:hover:bg-white/5 cursor-pointer disabled:cursor-not-allowed"
                  >
                    <ChevronRight size={14} />
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Selected Organization Dossier Callout (if specific org selected) */}
      {activeOrg && (
        <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-br from-indigo-500/10 via-purple-500/5 to-slate-900/10 border border-indigo-500/30 text-xs shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3.5 min-w-0">
            <OrgLogo org={activeOrg.organization_code} size="md" showTooltip={false} />
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider font-mono">
                  {activeOrg.category_label}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-indigo-100 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/30">
                  {activeOrg.jurisdiction}
                </span>
                {activeOrg.cadence_stats && (
                  <span className="text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-slate-100 dark:bg-white/10 text-slate-700 dark:text-slate-300">
                    {activeOrg.cadence_stats.mean_interval_months} mo. Cadence &bull; {activeOrg.cadence_stats.regularity_score}% Regularity
                  </span>
                )}
              </div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white mt-0.5">
                {activeOrg.full_name}
              </h3>
              <p className="text-slate-600 dark:text-slate-300 text-[11px] mt-0.5 line-clamp-2">
                <strong className="text-slate-900 dark:text-white">Statutory Driver: </strong>
                {activeOrg.primary_mandate}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 shrink-0 flex-wrap">
            <div className="text-right">
              <div className="text-[10.5px] text-slate-500 dark:text-slate-400 font-mono">Total Forecasted Capital</div>
              <div className="text-base font-bold font-mono text-emerald-600 dark:text-emerald-400">
                {fmtMoney(activeOrg.total_pipeline_funding)}
              </div>
            </div>

            <button
              type="button"
              onClick={() => openBriefingModal(activeOrg.organization_code)}
              className="px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold flex items-center gap-1.5 transition-colors cursor-pointer shadow-xs"
            >
              <FileText size={13} />
              <span>Strategic Forecast Briefing</span>
            </button>

            <button
              type="button"
              onClick={() => setSelectedOrgCode('all')}
              className="px-3 py-1.5 rounded-xl bg-white dark:bg-[#0c1220] hover:bg-slate-100 dark:hover:bg-white/10 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-white/10 text-xs font-semibold transition-colors cursor-pointer"
            >
              Clear Filter
            </button>
          </div>
        </div>
      )}

      {/* Release Horizon Filter Bar */}
      <div className="flex items-center justify-between gap-3 pt-1">
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs font-semibold overflow-x-auto">
          <span className="text-[11px] text-slate-400 px-2 font-mono flex items-center gap-1">
            <Clock size={12} /> Horizon:
          </span>
          {horizons.map((h) => (
            <button
              key={h.id}
              type="button"
              onClick={() => setSelectedHorizon(h.id)}
              className={clsx(
                'px-3 py-1.5 rounded-lg transition-colors whitespace-nowrap cursor-pointer',
                selectedHorizon === h.id
                  ? 'bg-white dark:bg-[#11192e] text-indigo-600 dark:text-indigo-400 shadow-2xs font-bold'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              )}
            >
              {h.label}
            </button>
          ))}
        </div>

        <div className="text-xs text-slate-500 dark:text-slate-400 font-mono">
          Showing <strong>{forecasts.length}</strong> upcoming {forecasts.length === 1 ? 'solicitation' : 'solicitations'}
        </div>
      </div>

      {/* Forecast Radar Cards Grid */}
      {loadingForecasts ? (
        <div className="py-24 flex flex-col items-center justify-center space-y-3 text-slate-500 dark:text-slate-400">
          <RefreshCw size={32} className="animate-spin text-indigo-500" />
          <p className="text-xs font-mono">Scanning statutory cadence models across all 250 database organizations...</p>
        </div>
      ) : forecasts.length === 0 ? (
        <div className="py-16 text-center p-8 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-dashed border-slate-300 dark:border-white/10 text-slate-500 dark:text-slate-400 text-xs">
          No upcoming solicitations found matching the selected organization or horizon filters.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-5">
          {forecasts.map((fc, idx) => {
            const isImminent = fc.days_until_release <= 90;

            return (
              <div
                key={fc.id || idx}
                className={clsx(
                  'rounded-2xl border transition-all p-5 sm:p-6 bg-white dark:bg-[#0d1424] shadow-xs space-y-4',
                  isImminent
                    ? 'border-amber-500/40 dark:border-amber-500/30 ring-1 ring-amber-500/20'
                    : 'border-slate-200 dark:border-white/10'
                )}
              >
                {/* Top Meta Bar */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100 dark:border-white/5">
                  <div className="flex items-center gap-3 min-w-0">
                    <OrgLogo org={fc.agency_code || fc.agency} size="sm" showTooltip={false} />
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-bold text-xs text-slate-900 dark:text-white">{fc.agency}</span>
                        <span className="text-[10.5px] font-mono text-slate-500 dark:text-slate-400">
                          &bull; {fc.program_division}
                        </span>
                        <span className="text-[10px] px-2 py-0.2 rounded-md font-mono font-bold bg-slate-100 text-slate-600 dark:bg-white/5 dark:text-slate-300">
                          {fc.recurrence_cadence}
                        </span>
                        <span className="text-[9.5px] px-2 py-0.2 rounded-full font-mono font-bold bg-amber-500/10 text-amber-700 dark:text-amber-300 border border-amber-500/20">
                          Probabilistic Forecast
                        </span>
                      </div>
                      <h3 className="text-sm sm:text-base font-bold text-slate-900 dark:text-white mt-0.5">
                        {fc.predicted_title}
                      </h3>
                    </div>
                  </div>

                  {/* Horizon & Conviction Badges */}
                  <div className="flex items-center gap-2 shrink-0 flex-wrap">
                    <span
                      className={clsx(
                        'px-2.5 py-1 rounded-xl text-xs font-mono font-bold flex items-center gap-1.5',
                        isImminent
                          ? 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-500/30'
                          : 'bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/30'
                      )}
                    >
                      <Clock size={12} />
                      <span>{fc.days_until_release} Days &bull; {fc.forecasted_release_window}</span>
                    </span>

                    <span className="px-2 py-1 rounded-xl bg-slate-100 dark:bg-white/5 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-white/10 text-xs font-mono font-bold">
                      {fc.confidence_score}% Conviction ({fc.confidence_tier})
                    </span>
                  </div>
                </div>

                {/* Core Parameters Row */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs bg-slate-50/60 dark:bg-black/20 p-3.5 rounded-xl border border-slate-200/60 dark:border-white/5">
                  <div>
                    <span className="text-[10.5px] uppercase font-bold text-slate-400 block mb-0.5">
                      Funding Envelope Range
                    </span>
                    <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400 text-xs">
                      {fc.projected_funding_envelope}
                    </span>
                    {fc.expected_cost_share_pct !== undefined && fc.expected_cost_share_pct > 0 && (
                      <span className="text-[10px] text-slate-400 block font-mono">
                        Expected Cost-Share: ~{fc.expected_cost_share_pct}%
                      </span>
                    )}
                  </div>

                  <div>
                    <span className="text-[10.5px] uppercase font-bold text-slate-400 block mb-0.5">
                      Statutory Driver &amp; Mandate
                    </span>
                    <span className="font-medium text-slate-700 dark:text-slate-300 line-clamp-2">
                      {fc.statutory_driver}
                    </span>
                  </div>

                  <div>
                    <span className="text-[10.5px] uppercase font-bold text-slate-400 block mb-0.5">
                      Historical Predecessor &amp; Cadence
                    </span>
                    <span className="font-mono text-slate-600 dark:text-slate-400 block truncate">
                      {fc.historical_predecessor}
                    </span>
                    {fc.cadence_stats && (
                      <span className="text-[10px] text-slate-400 font-mono block">
                        Cadence: ~{fc.cadence_stats.mean_interval_months} mo. &bull; Peak: {fc.cadence_stats.peak_quarter}
                      </span>
                    )}
                  </div>
                </div>

                {/* Pre-Positioning Playbook Checklist */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-slate-900 dark:text-white uppercase tracking-wider font-mono flex items-center gap-1.5">
                      <Zap size={13} className="text-amber-500" />
                      <span>Early Pre-Positioning Playbook (Actions to Prepare Before Release)</span>
                    </span>
                    <span className="text-[11px] text-slate-400 font-mono">
                      Execute 60–120 days ahead
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {fc.pre_positioning_playbook.map((step, sIdx) => {
                      const stepKey = `${fc.id}-step-${sIdx}`;
                      const isDone = completedSteps[stepKey] === true;

                      return (
                        <div
                          key={sIdx}
                          onClick={() => toggleStep(stepKey)}
                          className={clsx(
                            'p-3 rounded-xl border text-xs flex items-start gap-2.5 cursor-pointer transition-all',
                            isDone
                              ? 'bg-emerald-50/50 dark:bg-emerald-950/20 border-emerald-300 dark:border-emerald-500/30 text-slate-500 dark:text-slate-400 line-through'
                              : 'bg-white dark:bg-[#0c1220] border-slate-200 dark:border-white/10 hover:border-indigo-300 dark:hover:border-indigo-500 text-slate-800 dark:text-slate-200'
                          )}
                        >
                          <div
                            className={clsx(
                              'w-4 h-4 rounded mt-0.5 flex items-center justify-center shrink-0 transition-colors',
                              isDone
                                ? 'bg-emerald-600 text-white'
                                : 'border border-slate-300 dark:border-white/20 text-transparent'
                            )}
                          >
                            <CheckCircle2 size={12} />
                          </div>
                          <span className="leading-snug text-[11.5px]">{step}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Targeted Technologies & Action Bar */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2 text-xs">
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <span className="text-[10.5px] font-mono text-slate-400">Target Tech:</span>
                    {fc.targeted_technologies.map((t, tIdx) => (
                      <span
                        key={tIdx}
                        className="text-[10.5px] px-2 py-0.5 rounded-md bg-slate-100 dark:bg-white/5 text-slate-700 dark:text-slate-300 font-medium"
                      >
                        {t}
                      </span>
                    ))}
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      type="button"
                      onClick={() => openBriefingModal(fc.agency_code || fc.agency)}
                      className="px-3 py-1.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/50 hover:bg-indigo-100 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/30 font-bold text-xs flex items-center gap-1.5 transition-colors cursor-pointer"
                    >
                      <FileText size={13} />
                      <span>Forecast Briefing</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => setSelectedAngleOpp(fc)}
                      className="px-3.5 py-1.5 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-amber-600 dark:text-amber-400 border border-amber-500/30 font-bold text-xs flex items-center gap-1.5 transition-colors cursor-pointer"
                    >
                      <Zap size={13} className="fill-amber-500" />
                      <span>Positioning Analysis</span>
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Strategic Briefing Modal */}
      {briefingModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
          <div className="relative w-full max-w-2xl bg-white dark:bg-[#0c1220] rounded-2xl border border-slate-200 dark:border-white/10 shadow-2xl p-6 space-y-4 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-white/5">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
                  <FileText size={20} />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    Strategic Opportunity Forecast Briefing
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Probabilistic Cadence &amp; Pre-Positioning Dossier
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setBriefingModalOpen(false)}
                className="p-1.5 rounded-xl text-slate-400 hover:text-slate-600 dark:hover:text-white cursor-pointer"
              >
                <X size={18} />
              </button>
            </div>

            {briefingLoading ? (
              <div className="py-16 text-center text-xs text-slate-400 flex flex-col items-center justify-center gap-2">
                <RefreshCw size={24} className="animate-spin text-indigo-500" />
                <span>Synthesizing database cadence analytics and strategic posture...</span>
              </div>
            ) : briefingData ? (
              <div className="space-y-4 text-xs">
                {/* Header Metrics Row */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 bg-slate-50 dark:bg-black/30 p-3 rounded-xl border border-slate-200 dark:border-white/5">
                  <div>
                    <span className="text-[10px] uppercase font-mono text-slate-400 block">Organization</span>
                    <span className="font-bold text-slate-900 dark:text-white truncate block">
                      {briefingData.organization_name}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-mono text-slate-400 block">Next Release</span>
                    <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400 block">
                      {briefingData.forecasted_release_window}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-mono text-slate-400 block">Cadence Regularity</span>
                    <span className="font-mono font-bold text-amber-600 dark:text-amber-400 block">
                      {briefingData.cadence_regularity_score}% Score
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-mono text-slate-400 block">Projected Pipeline</span>
                    <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400 block">
                      {fmtMoney(briefingData.projected_total_pipeline)}
                    </span>
                  </div>
                </div>

                {/* Briefing Text */}
                <div
                  className="prose dark:prose-invert prose-xs max-w-none text-slate-700 dark:text-slate-300 leading-relaxed space-y-2"
                  dangerouslySetInnerHTML={{ __html: briefingData.briefing.replace(/\n\n/g, '<br/><br/>') }}
                />

                {/* Pre-Positioning Actions */}
                <div className="space-y-2 pt-2 border-t border-slate-100 dark:border-white/5">
                  <h4 className="font-bold text-slate-900 dark:text-white uppercase tracking-wider font-mono text-xs flex items-center gap-1.5">
                    <Zap size={13} className="text-amber-500" />
                    <span>Recommended Pre-Positioning Actions</span>
                  </h4>
                  <ul className="space-y-1.5 pl-2">
                    {briefingData.pre_positioning_playbook.map((step, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-[11.5px] text-slate-600 dark:text-slate-300">
                        <span className="w-4 h-4 rounded-full bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 font-bold font-mono text-[10px] flex items-center justify-center shrink-0 mt-0.5">
                          {idx + 1}
                        </span>
                        <span>{step}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Disclaimer Callout inside modal */}
                <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-800 dark:text-amber-300 text-[10.5px]">
                  <strong>Probabilistic Forecast Notice:</strong> {briefingData.disclaimer}
                </div>
              </div>
            ) : (
              <div className="py-8 text-center text-xs text-red-500">
                Unable to synthesize briefing for this organization.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Winning Angle Modal for Forecasted Solicitations */}
      {selectedAngleOpp && (
        <WinningAngleModal
          isOpen={!!selectedAngleOpp}
          onClose={() => setSelectedAngleOpp(null)}
          opportunityId={selectedAngleOpp.id}
          opportunityName={selectedAngleOpp.predicted_title}
          solicitationNumber={selectedAngleOpp.historical_predecessor}
          agency={selectedAngleOpp.agency}
          projectProfile={{
            title: selectedAngleOpp.predicted_title,
            summary: `Proposed commercial demonstration aligned with ${selectedAngleOpp.agency} ${selectedAngleOpp.program_division} priorities.`,
            technology_areas: selectedAngleOpp.targeted_technologies,
            location: selectedAngleOpp.organization_state === 'NY' ? 'New York' : selectedAngleOpp.organization_state === 'CA' ? 'California' : 'United States',
          }}
          matchScore={0.92}
        />
      )}
    </div>
  );
}
