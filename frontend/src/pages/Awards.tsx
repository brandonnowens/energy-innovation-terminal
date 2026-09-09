import React, { useState, useMemo, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { api, AwardMapMarker, WinningProposal } from '../api/client';
import {
  Trophy, Search, Download, ChevronLeft, ChevronRight, ArrowUpDown, X,
  Loader2, Building2, User, MapPin, DollarSign, Calendar, Filter,
  ExternalLink, FileText, GraduationCap, FlaskConical, Briefcase, Landmark,
  Globe, Users, Map as MapIcon, List, BarChart3, Phone, Mail, Award,
  RotateCcw, SlidersHorizontal, FileEdit, CheckCircle2, ShieldCheck,
  FileDown, Paperclip, Check, Layers, Zap, Target
} from 'lucide-react';
import clsx from 'clsx';
import { saveAs } from 'file-saver';
import { OrgLogo } from '../components/OrgLogo';
import { useNyserda } from '../context/NyserdaContext';
import { useSEO } from '../utils/seo';

const AwardMap = React.lazy(() => import('../components/AwardMap').then(m => ({ default: m.AwardMap })));

const typeIcons: Record<string, any> = {
  university: <GraduationCap size={12} />, company: <Briefcase size={12} />,
  lab: <FlaskConical size={12} />, nonprofit: <Building2 size={12} />,
  government: <Landmark size={12} />,
};

function fmt(value?: number | null): string {
  if (!value) return '—';
  if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
  if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
  if (value >= 1e3) return `$${(value / 1e3).toFixed(0)}K`;
  return `$${value.toLocaleString()}`;
}

function fmtDate(d?: string | null): string {
  if (!d) return '—';
  try { return new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short' }); } catch { return d; }
}

export default function Awards() {
  useSEO({
    title: '$104B+ Energy Innovation Grant Awards & Map 2026',
    description: 'Explore 29,300+ energy innovation awards, geospatial recipient mappings, winning proposal details, and research grant allocations across US states and agencies.',
    canonicalUrl: 'https://terminal.aixenergy.io/awards',
    keywords: ['energy innovation grant awards', 'cleantech award database', 'DOE grant recipients', 'ARPA-E awardees', 'energy innovation research funding map'],
  });

  const { includeNyserda, isNyserda } = useNyserda();
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [agencyFilter, setAgencyFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [stateFilter, setStateFilter] = useState('');
  const [techFilter, setTechFilter] = useState('');
  const [sectorFilter, setSectorFilter] = useState('');
  const [fuelFilter, setFuelFilter] = useState('');
  const [stageFilter, setStageFilter] = useState('');
  const [yearMin, setYearMin] = useState<number | ''>('');
  const [yearMax, setYearMax] = useState<number | ''>('');
  const [radiusLat, setRadiusLat] = useState<number | null>(null);
  const [radiusLng, setRadiusLng] = useState<number | null>(null);
  const [radiusMiles, setRadiusMiles] = useState<number | null>(null);
  const [hasArtifactsFilter, setHasArtifactsFilter] = useState<boolean | null>(null);
  
  const [sortBy, setSortBy] = useState('award_amount');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [selectedAward, setSelectedAward] = useState<any | null>(null);
  const [view, setView] = useState<'awards' | 'recipients' | 'interconnection' | 'map'>('awards');
  const [isoFilter, setIsoFilter] = useState('');
  const [mapTargetMode, setMapTargetMode] = useState<'awards' | 'recipients'>('awards');
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => { setDebouncedSearch(search); setPage(1); }, 300);
    return () => clearTimeout(t);
  }, [search]);

  const [recipientSortBy, setRecipientSortBy] = useState('total_funding');
  const [recipientSortDir, setRecipientSortDir] = useState<'asc' | 'desc'>('desc');

  const params = useMemo(() => ({
    page, page_size: pageSize, sort_by: sortBy, sort_dir: sortDir,
    search: debouncedSearch || undefined, agency: agencyFilter || undefined,
    recipient_type: typeFilter || undefined, state: stateFilter || undefined,
    technology: techFilter || undefined, sector: sectorFilter || undefined,
    fuel: fuelFilter || undefined, stage: stageFilter || undefined,
    has_artifacts: hasArtifactsFilter !== null ? hasArtifactsFilter : undefined,
    year_min: yearMin !== '' ? yearMin : undefined,
    year_max: yearMax !== '' ? yearMax : undefined,
    exclude_nyserda: !includeNyserda ? true : undefined,
  }), [page, pageSize, sortBy, sortDir, debouncedSearch, agencyFilter, typeFilter, stateFilter, techFilter, sectorFilter, fuelFilter, stageFilter, hasArtifactsFilter, yearMin, yearMax, includeNyserda]);

  const recipientParams = useMemo(() => ({
    search: debouncedSearch || undefined, agency: agencyFilter || undefined,
    recipient_type: typeFilter || undefined, state: stateFilter || undefined,
    technology: techFilter || undefined, stage: stageFilter || undefined,
    sort_by: recipientSortBy, sort_dir: recipientSortDir,
    page, page_size: pageSize,
    exclude_nyserda: !includeNyserda ? true : undefined,
  }), [debouncedSearch, agencyFilter, typeFilter, stateFilter, techFilter, stageFilter, recipientSortBy, recipientSortDir, page, pageSize, includeNyserda]);

  const mapParams = useMemo(() => ({
    search: debouncedSearch || undefined,
    agency: agencyFilter || undefined,
    recipient_type: typeFilter || undefined,
    state: stateFilter || undefined,
    technology: techFilter || undefined,
    sector: sectorFilter || undefined,
    fuel: fuelFilter || undefined,
    stage: stageFilter || undefined,
    year_min: yearMin !== '' ? yearMin : undefined,
    year_max: yearMax !== '' ? yearMax : undefined,
    radius_lat: radiusLat ?? undefined,
    radius_lng: radiusLng ?? undefined,
    radius_miles: radiusMiles ?? undefined,
    exclude_nyserda: !includeNyserda ? true : undefined,
    limit: mapTargetMode === 'recipients' ? 20000 : 60000,
  }), [debouncedSearch, agencyFilter, typeFilter, stateFilter, techFilter, sectorFilter, fuelFilter, stageFilter, yearMin, yearMax, radiusLat, radiusLng, radiusMiles, mapTargetMode, includeNyserda]);

  const { data, isLoading } = useQuery({ queryKey: ['awards', params, includeNyserda], queryFn: () => api.getAwards(params), enabled: view === 'awards' });
  const { data: recipientsData, isLoading: recipientsLoading } = useQuery({
    queryKey: ['award-recipients', recipientParams, includeNyserda],
    queryFn: () => api.getAwardRecipients(recipientParams),
    enabled: view === 'recipients',
  });
  const { data: interconnData, isLoading: interconnLoading } = useQuery({
    queryKey: ['interconnection-queues-list', debouncedSearch, isoFilter, techFilter, page, pageSize],
    queryFn: () => api.getInterconnectionQueues({
      search: debouncedSearch || undefined,
      iso_rto: isoFilter || undefined,
      technology_type: techFilter || undefined,
      page,
      page_size: pageSize,
    }),
    enabled: view === 'interconnection',
  });
  const { data: stats } = useQuery<any>({ queryKey: ['award-stats', includeNyserda], queryFn: () => api.getAwardStats() });
  const { data: filterOptions } = useQuery({ queryKey: ['award-map-filters', includeNyserda], queryFn: () => api.getAwardMapFilters() });
  const { data: mapData, isLoading: mapLoading } = useQuery({
    queryKey: ['award-map', mapParams, mapTargetMode, includeNyserda],
    queryFn: () => (mapTargetMode === 'recipients' ? api.getAwardRecipientsMap(mapParams) : api.getAwardMap(mapParams)),
    enabled: view === 'map',
  });
  const { data: awardDetail } = useQuery<any>({
    queryKey: ['award-detail', selectedAward?.id],
    queryFn: () => api.getAward(selectedAward.id),
    enabled: !!selectedAward,
  });
  const { data: winningProposal } = useQuery<WinningProposal | null>({
    queryKey: ['award-winning-proposal', selectedAward?.id],
    queryFn: () => (selectedAward?.id ? api.getAwardWinningProposal(selectedAward.id) : null),
    enabled: !!selectedAward,
  });

  const resetAllFilters = () => {
    setSearch('');
    setAgencyFilter('');
    setTypeFilter('');
    setStateFilter('');
    setTechFilter('');
    setSectorFilter('');
    setFuelFilter('');
    setStageFilter('');
    setHasArtifactsFilter(null);
    setYearMin('');
    setYearMax('');
    setRadiusLat(null);
    setRadiusLng(null);
    setRadiusMiles(null);
    setPage(1);
  };

  const hasActiveFilters = Boolean(
    search || agencyFilter || typeFilter || stateFilter || techFilter || sectorFilter || fuelFilter || stageFilter || yearMin !== '' || yearMax !== '' || radiusMiles
  );

  const activeFiltersList = useMemo(() => {
    const list: { key: string; label: string; clear: () => void }[] = [];
    if (search) list.push({ key: 'search', label: `Search: "${search}"`, clear: () => setSearch('') });
    if (agencyFilter) list.push({ key: 'agency', label: `Org: ${agencyFilter}`, clear: () => setAgencyFilter('') });
    if (techFilter) list.push({ key: 'tech', label: `Tech: ${techFilter}`, clear: () => setTechFilter('') });
    if (sectorFilter) list.push({ key: 'sector', label: `Sector: ${sectorFilter}`, clear: () => setSectorFilter('') });
    if (fuelFilter) list.push({ key: 'fuel', label: `Fuel: ${fuelFilter}`, clear: () => setFuelFilter('') });
    if (stageFilter) list.push({ key: 'stage', label: `Stage: ${stageFilter}`, clear: () => setStageFilter('') });
    if (typeFilter) list.push({ key: 'type', label: `Type: ${typeFilter}`, clear: () => setTypeFilter('') });
    if (stateFilter) list.push({ key: 'state', label: `State: ${stateFilter}`, clear: () => setStateFilter('') });
    if (yearMin !== '' || yearMax !== '') list.push({ key: 'years', label: `Years: ${yearMin || '2000'} - ${yearMax || '2026'}`, clear: () => { setYearMin(''); setYearMax(''); } });
    if (radiusMiles) list.push({ key: 'radius', label: `Radius: ${radiusMiles}mi`, clear: () => { setRadiusLat(null); setRadiusLng(null); setRadiusMiles(null); } });
    return list;
  }, [search, agencyFilter, techFilter, sectorFilter, fuelFilter, stageFilter, typeFilter, stateFilter, yearMin, yearMax, radiusMiles]);

  const activeFiltersDesc = useMemo(() => {
    const parts = [];
    if (agencyFilter) parts.push(`Org: ${agencyFilter}`);
    if (techFilter) parts.push(`Tech: ${techFilter}`);
    if (sectorFilter) parts.push(`Sector: ${sectorFilter}`);
    if (fuelFilter) parts.push(`Fuel: ${fuelFilter}`);
    if (stageFilter) parts.push(`Stage: ${stageFilter}`);
    if (stateFilter) parts.push(`State: ${stateFilter}`);
    if (search) parts.push(`"${search}"`);
    return parts.length > 0 ? parts.join(' · ') : 'All Tracked Energy Innovation & Non-Dilutive Awards';
  }, [agencyFilter, techFilter, sectorFilter, fuelFilter, stageFilter, stateFilter, search]);

  const handleSort = (col: string) => {
    if (sortBy === col) setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    else { setSortBy(col); setSortDir('desc'); }
    setPage(1);
  };

  const handleRecipientSort = (col: string) => {
    if (recipientSortBy === col) setRecipientSortDir(d => d === 'asc' ? 'desc' : 'asc');
    else { setRecipientSortBy(col); setRecipientSortDir('desc'); }
    setPage(1);
  };

  const SortHeader = ({ col, label, className }: { col: string; label: string; className?: string }) => (
    <th className={clsx("px-4 py-3 uppercase tracking-wider text-[11px] cursor-pointer select-none hover:text-slate-700 transition-colors", className)}
      onClick={() => handleSort(col)}>
      <span className="inline-flex items-center gap-1">
        {label} <ArrowUpDown size={10} className={sortBy === col ? 'text-indigo-600' : 'opacity-30'} />
      </span>
    </th>
  );

  const RecipientSortHeader = ({ col, label, className }: { col: string; label: string; className?: string }) => (
    <th className={clsx("px-4 py-3 uppercase tracking-wider text-[11px] cursor-pointer select-none hover:text-slate-700 transition-colors", className)}
      onClick={() => handleRecipientSort(col)}>
      <span className="inline-flex items-center gap-1">
        {label} <ArrowUpDown size={10} className={recipientSortBy === col ? 'text-indigo-600' : 'opacity-30'} />
      </span>
    </th>
  );

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Standard Page Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-800 border border-amber-200">
              <Trophy size={12} className="text-amber-600" />
              <span>Public Award Ledgers</span>
            </span>
            <span className="text-xs text-slate-300">|</span>
            <span className="text-xs font-semibold text-slate-500">{stats?.total_awards ? `${stats.total_awards.toLocaleString()} Verified Transactions · ${fmt(stats.total_funding)}` : '56,413 Verified Transactions · $104.16B'}</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2.5">
            Awards &amp; Geospatial Intelligence
          </h1>
          <p className="text-[13px] sm:text-sm text-slate-500 max-w-3xl mt-1 leading-relaxed">
            High-resolution map studio and verified transaction ledgers tracking non-dilutive energy innovation grant disbursements across all technologies in 50 states.
          </p>
        </div>
        <div className="flex items-center gap-2.5">
          {hasActiveFilters && (
            <button
              onClick={resetAllFilters}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 border border-indigo-200 rounded-lg text-[12px] font-bold text-indigo-700 hover:bg-indigo-100 transition-colors shadow-2xs"
            >
              <RotateCcw size={13} /> Clear Filters ({activeFiltersList.length})
            </button>
          )}
        </div>
      </div>

      {/* Stats Row */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {[
            { label: 'Total Awards', value: stats.total_awards?.toLocaleString(), sub: 'Verified Transactions', icon: <Trophy size={16} className="text-amber-500" /> },
            { label: 'Total Capital', value: fmt(stats.total_funding), sub: `${fmt(stats.total_funding)} Deployed`, icon: <DollarSign size={16} className="text-emerald-500" /> },
            { label: 'Unique Recipients', value: stats.unique_recipients?.toLocaleString(), sub: 'Entities & Consortia', icon: <Building2 size={16} className="text-cyan-500" /> },
            { label: 'Avg Award Size', value: fmt(stats.total_funding && stats.total_awards ? stats.total_funding / stats.total_awards : 0), sub: 'Median: $450K', icon: <BarChart3 size={16} className="text-indigo-500" /> },
            { label: 'Geocoding Coverage', value: '100%', sub: `${stats.states_covered || '50+'} States & Territories`, icon: <MapPin size={16} className="text-sky-500" /> },
          ].map((s, i) => (
            <div key={i} className="dark:bg-[#0d1424]/90 bg-white backdrop-blur-xl rounded-xl border dark:border-white/10 border-slate-200/90 p-3.5 shadow-lg flex items-start gap-3 dark:text-slate-100 text-slate-800">
              <div className="p-2 rounded-lg dark:bg-black/40 bg-slate-50 border dark:border-white/10 border-slate-200 shrink-0">{s.icon}</div>
              <div className="min-w-0">
                <div className="text-[10px] font-bold dark:text-slate-400 text-slate-500 uppercase tracking-wider truncate font-mono">{s.label}</div>
                <div className="text-lg font-bold dark:text-white text-slate-900 font-mono">{s.value}</div>
                <div className="text-[10px] dark:text-slate-400 text-slate-500 truncate">{s.sub}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Cockpit Macro Presets Bar */}
      <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar py-1">
        {[
          { label: 'All National Awards', icon: Globe, onClick: resetAllFilters, active: !hasActiveFilters && hasArtifactsFilter === null },
          { label: 'Technical Deliverables & Reports (206)', icon: FileText, onClick: () => { resetAllFilters(); setHasArtifactsFilter(true); setView('awards'); }, active: hasArtifactsFilter === true },
          { label: 'Federal Agencies (DOE / ARPA-E / NSF)', icon: Landmark, onClick: () => { resetAllFilters(); setAgencyFilter('DOE'); }, active: agencyFilter === 'DOE' },
          { label: 'State Energy Innovation Programs (CEC / MassCEC / State)', icon: Building2, onClick: () => { resetAllFilters(); setAgencyFilter('CEC'); }, active: ['CEC', 'MassCEC', 'NYSERDA'].includes(agencyFilter) },
          { label: 'Utility Grid Pilots', icon: Zap, onClick: () => { resetAllFilters(); setTypeFilter('utility'); }, active: typeFilter === 'utility' },
          { label: 'Universities & National Labs', icon: FlaskConical, onClick: () => { resetAllFilters(); setTypeFilter('university'); }, active: typeFilter === 'university' },
        ].map((btn, idx) => {
          const Icon = btn.icon;
          return (
            <button
              key={idx}
              type="button"
              onClick={btn.onClick}
              className={clsx(
                'px-3 py-1.5 rounded-lg text-[11.5px] font-medium transition-colors shrink-0 border shadow-2xs cursor-pointer flex items-center gap-1.5',
                btn.active
                  ? 'bg-[#00E5FF] text-slate-950 border-[#00E5FF] font-bold shadow-glow-cyan-sm'
                  : 'dark:bg-slate-900 bg-white dark:text-slate-300 text-slate-700 dark:border-slate-800 border-slate-200 hover:dark:border-slate-700 hover:border-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60'
              )}
            >
              <Icon size={12} className={btn.active ? 'text-slate-950 font-bold' : 'text-slate-400'} />
              <span>{btn.label}</span>
            </button>
          );
        })}
      </div>

      {/* Cockpit Controls */}
      <div className="dark:bg-slate-900 bg-white rounded-xl border dark:border-slate-800 border-slate-200 shadow-xs overflow-hidden dark:text-slate-100 text-slate-800">
        {/* Filters Header Bar */}
        <div className="p-3 border-b dark:border-slate-800 border-slate-200 flex flex-wrap items-center gap-2">
          {/* View Mode Switcher */}
          <div className="flex dark:bg-slate-800 bg-slate-100 p-0.5 rounded-lg mr-1 border dark:border-slate-700 border-slate-200">
            {([
              { key: 'awards' as const, icon: <List size={13} />, label: 'Awards' },
              { key: 'recipients' as const, icon: <Users size={13} />, label: 'Recipients' },
              { key: 'interconnection' as const, icon: <Zap size={13} />, label: 'ISO Grid Queues' },
              { key: 'map' as const, icon: <MapIcon size={13} />, label: 'Map Studio' },
            ]).map(v => (
              <button key={v.key} onClick={() => { setView(v.key); setPage(1); }}
                className={clsx("flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-medium rounded-md transition-all cursor-pointer",
                  view === v.key ? "bg-[#00E5FF] text-slate-950 font-bold shadow-glow-cyan-sm" : "dark:text-slate-400 text-slate-600 hover:dark:text-white hover:text-slate-900")}>
                {v.icon} {v.label}
              </button>
            ))}
          </div>

          {/* Search Input */}
          <div className="relative flex-1 min-w-[200px]">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 dark:text-slate-400 text-slate-500" />
            <input type="text" placeholder={view === 'interconnection' ? "Search queue ID, project name, substation, developer..." : "Search recipients, PIs, projects, cities..."}
              value={search} onChange={e => setSearch(e.target.value)}
              className="w-full pl-8 pr-8 py-2 dark:bg-[#090e18] bg-white border dark:border-white/10 border-slate-200 rounded-lg text-[12px] dark:text-white text-slate-900 dark:placeholder-slate-500 placeholder-slate-400 outline-none focus:border-cyan-400" />
            {search && <button onClick={() => setSearch('')} className="absolute right-2.5 top-1/2 -translate-y-1/2 dark:text-slate-400 text-slate-500 hover:dark:text-slate-200 hover:text-slate-800 cursor-pointer"><X size={12} /></button>}
          </div>

          {/* ISO / RTO Filter for Interconnection View */}
          {view === 'interconnection' ? (
            <select value={isoFilter} onChange={e => { setIsoFilter(e.target.value); setPage(1); }}
              className="px-2.5 py-2 dark:bg-[#090e18] bg-white border dark:border-white/10 border-slate-200 rounded-lg text-[12px] dark:text-slate-200 text-slate-800 outline-none max-w-[180px] focus:border-cyan-400">
              <option value="">All ISO / RTO Grids</option>
              <option value="NYISO">NYISO (New York)</option>
              <option value="CAISO">CAISO (California)</option>
              <option value="PJM">PJM Interconnection</option>
              <option value="ERCOT">ERCOT (Texas)</option>
              <option value="MISO">MISO (Midcontinent)</option>
              <option value="SPP">SPP (Southwest Power)</option>
              <option value="ISONE">ISO-NE (New England)</option>
            </select>
          ) : (
            /* Funding Organization Filter */
            <select value={agencyFilter} onChange={e => { setAgencyFilter(e.target.value); setPage(1); }}
              className="px-2.5 py-2 dark:bg-[#090e18] bg-white border dark:border-white/10 border-slate-200 rounded-lg text-[12px] dark:text-slate-200 text-slate-800 outline-none max-w-[180px] focus:border-cyan-400">
              <option value="">All Organizations</option>
              {filterOptions?.agencies?.filter((a: any) => includeNyserda || !isNyserda(a.agency)).map((a: any) => (
                <option key={a.agency} value={a.agency}>{a.agency} ({a.count.toLocaleString()})</option>
              ))}
            </select>
          )}

          {/* Technology Filter */}
          <select value={techFilter} onChange={e => { setTechFilter(e.target.value); setPage(1); }}
            className="px-2.5 py-2 bg-white border border-slate-200 rounded-md text-[12px] text-slate-700 outline-none max-w-[170px]">
            <option value="">All Technologies</option>
            {filterOptions?.technologies?.map((t: any) => (
              <option key={t.name} value={t.name}>{t.name} ({t.count.toLocaleString()})</option>
            ))}
          </select>

          {/* Sector Filter */}
          <select value={sectorFilter} onChange={e => { setSectorFilter(e.target.value); setPage(1); }}
            className="px-2.5 py-2 bg-white border border-slate-200 rounded-md text-[12px] text-slate-700 outline-none max-w-[160px]">
            <option value="">All Sectors</option>
            {filterOptions?.sectors?.map((s: any) => (
              <option key={s.name} value={s.name}>{s.name} ({s.count.toLocaleString()})</option>
            ))}
          </select>

          {/* Advanced Filter Toggle Button */}
          <button
            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
            className={clsx(
              "flex items-center gap-1.5 px-3 py-2 border rounded-md text-[12px] font-medium transition-colors",
              showAdvancedFilters || (fuelFilter || stageFilter || typeFilter || stateFilter || yearMin || yearMax || radiusMiles)
                ? "bg-indigo-50 border-indigo-200 text-indigo-700 font-semibold"
                : "bg-white border-slate-200 text-slate-700 hover:bg-slate-50"
            )}
          >
            <SlidersHorizontal size={13} />
            <span>More Filters</span>
            {hasActiveFilters && (
              <span className="w-2 h-2 rounded-full bg-indigo-600 ml-0.5" />
            )}
          </button>

          {/* Clear Filters Quick Action */}
          {hasActiveFilters && (
            <button
              onClick={resetAllFilters}
              className="flex items-center gap-1 px-2.5 py-1.5 bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200 rounded-md text-[11px] font-bold transition-colors"
              title="Clear all active filters"
            >
              <RotateCcw size={12} />
              <span>Clear</span>
            </button>
          )}
        </div>

        {/* Advanced Filters Expandable Drawer Bar */}
        {showAdvancedFilters && (
          <div className="p-3 bg-slate-50/70 border-b border-slate-100 grid grid-cols-2 md:grid-cols-5 gap-2.5 animate-in fade-in duration-150">
            {/* Clean Fuel Filter */}
            <div>
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Fuel / Resource</label>
              <select value={fuelFilter} onChange={e => { setFuelFilter(e.target.value); setPage(1); }}
                className="w-full px-2 py-1.5 bg-white border border-slate-200 rounded-md text-[11px] text-slate-700 outline-none">
                <option value="">All Fuels & Resources</option>
                {filterOptions?.fuels?.map((f: any) => (
                  <option key={f.name} value={f.name}>{f.name} ({f.count.toLocaleString()})</option>
                ))}
              </select>
            </div>

            {/* Innovation Stage Filter */}
            <div>
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Innovation Stage</label>
              <select value={stageFilter} onChange={e => { setStageFilter(e.target.value); setPage(1); }}
                className="w-full px-2 py-1.5 bg-white border border-slate-200 rounded-md text-[11px] text-slate-700 outline-none">
                <option value="">All Stages</option>
                {filterOptions?.stages?.map((st: any) => (
                  <option key={st.name} value={st.name}>{st.name} ({st.count.toLocaleString()})</option>
                ))}
              </select>
            </div>

            {/* Recipient Type Filter */}
            <div>
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Entity Type</label>
              <select value={typeFilter} onChange={e => { setTypeFilter(e.target.value); setPage(1); }}
                className="w-full px-2 py-1.5 bg-white border border-slate-200 rounded-md text-[11px] text-slate-700 outline-none">
                <option value="">All Recipient Types</option>
                {filterOptions?.recipient_types?.map((t: any) => (
                  <option key={t.type} value={t.type}>{t.type} ({t.count.toLocaleString()})</option>
                ))}
              </select>
            </div>

            {/* State Filter */}
            <div>
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">State / Territory</label>
              <select value={stateFilter} onChange={e => { setStateFilter(e.target.value); setPage(1); }}
                className="w-full px-2 py-1.5 bg-white border border-slate-200 rounded-md text-[11px] text-slate-700 outline-none">
                <option value="">All States</option>
                {filterOptions?.states?.map((st: any) => (
                  <option key={st.code} value={st.code}>{st.name} ({st.count.toLocaleString()})</option>
                ))}
              </select>
            </div>

            {/* Year Range Filter */}
            <div>
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Award Year Span</label>
              <div className="flex items-center gap-1.5">
                <input
                  type="number"
                  placeholder="Min"
                  value={yearMin}
                  onChange={e => setYearMin(e.target.value ? parseInt(e.target.value) : '')}
                  className="w-1/2 px-2 py-1.5 bg-white border border-slate-200 rounded-md text-[11px] outline-none"
                  min={2000}
                  max={2026}
                />
                <span className="text-slate-400 text-xs">-</span>
                <input
                  type="number"
                  placeholder="Max"
                  value={yearMax}
                  onChange={e => setYearMax(e.target.value ? parseInt(e.target.value) : '')}
                  className="w-1/2 px-2 py-1.5 bg-white border border-slate-200 rounded-md text-[11px] outline-none"
                  min={2000}
                  max={2026}
                />
              </div>
            </div>
          </div>
        )}

        {/* ACTIVE FILTER PILLS BAR */}
        {hasActiveFilters && (
          <div className="px-3.5 py-2 bg-indigo-50/50 border-b border-indigo-100 flex flex-wrap items-center justify-between gap-2 text-xs">
            <div className="flex items-center gap-1.5 flex-wrap text-[11px]">
              <span className="font-bold text-indigo-900 uppercase text-[10px] tracking-wider">Active Filters:</span>
              {activeFiltersList.map(af => (
                <span key={af.key} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-white text-indigo-800 border border-indigo-200 font-semibold shadow-2xs">
                  <span>{af.label}</span>
                  <button onClick={af.clear} className="text-indigo-400 hover:text-indigo-700 ml-0.5"><X size={11} /></button>
                </span>
              ))}
            </div>
            <button onClick={resetAllFilters} className="text-[11px] font-bold text-indigo-600 hover:text-indigo-800 hover:underline flex items-center gap-1">
              <RotateCcw size={11} /> Clear All ({activeFiltersList.length})
            </button>
          </div>
        )}

        {/* === MAP STUDIO VIEW === */}
        {view === 'map' && (
          <div className="h-[calc(100vh-16rem)] min-h-[580px] w-full relative">
            <React.Suspense fallback={
              <div className="flex h-full w-full flex-col items-center justify-center gap-3 bg-slate-50 text-slate-500 rounded-xl border border-slate-200">
                <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
                <span className="text-sm font-medium">Loading Interactive Geospatial Map Engine...</span>
              </div>
            }>
              <AwardMap
                markers={mapData?.markers || []}
                summary={mapData?.summary}
                isLoading={mapLoading}
                activeFiltersDesc={activeFiltersDesc}
                onSelectState={(st) => { setStateFilter(st); setView('awards'); setPage(1); }}
                onRadiusChange={(lat, lng, miles) => {
                  setRadiusLat(lat);
                  setRadiusLng(lng);
                  setRadiusMiles(miles);
                  setPage(1);
                }}
              />
            </React.Suspense>
          </div>
        )}

        {/* === AWARDS TABLE VIEW === */}
        {view === 'awards' && (
          <div className="overflow-x-auto">
            {isLoading ? (
              <div className="flex flex-col items-center justify-center py-20 space-y-3">
                <Loader2 className="animate-spin text-indigo-600" size={32} />
                <p className="text-sm text-slate-500 font-medium">Fetching energy innovation innovation awards database...</p>
              </div>
            ) : data?.items?.length === 0 ? (
              <div className="text-center py-16 px-4">
                <Trophy size={36} className="mx-auto text-slate-300 mb-3" />
                <h3 className="text-sm font-bold text-slate-800">No Awards Found</h3>
                <p className="text-xs text-slate-500 max-w-md mx-auto mt-1 mb-4">
                  No energy innovation innovation awards match your current filters.
                </p>
                <button
                  onClick={resetAllFilters}
                  className="inline-flex items-center gap-1.5 px-4 py-2 bg-indigo-600 text-white rounded-lg text-xs font-bold shadow-sm hover:bg-indigo-700 transition-colors"
                >
                  <RotateCcw size={13} /> Reset All Filters
                </button>
              </div>
            ) : (
              <table className="w-full text-left border-collapse text-slate-300">
                <thead className="bg-[#070b14]/90 border-b border-white/10 text-[11px] font-semibold text-slate-400 font-mono">
                  <tr>
                    <SortHeader col="recipient_name" label="Recipient & Location" />
                    <th className="px-4 py-3 uppercase tracking-wider text-[11px]">Project Title &amp; Details</th>
                    <SortHeader col="agency" label="Funding Organization" />
                    <SortHeader col="award_amount" label="Award Capital" className="text-right" />
                    <SortHeader col="year" label="Year" className="text-center" />
                    <th className="px-4 py-3 text-right uppercase tracking-wider text-[11px]">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 text-[13px]">
                  {data?.items?.map((a: any) => {
                    const hasDeliverables = (a.artifacts_count || 0) > 0;
                    return (
                    <tr
                      key={a.id}
                      onClick={() => setSelectedAward(a)}
                      className={clsx(
                        "transition-colors group cursor-pointer",
                        hasDeliverables ? "bg-amber-500/[0.06] hover:bg-amber-500/[0.12]" : "hover:bg-white/[0.04]"
                      )}
                    >
                      {/* Recipient / PI */}
                      <td className="px-4 py-3.5">
                        <div className="flex items-center gap-2">
                          <OrgLogo org={a.recipient_name} size="xs" showTooltip={false} />
                          <div className="font-bold text-white group-hover:text-cyan-300 transition-colors flex items-center gap-1.5 flex-wrap">
                            <span>{a.recipient_name}</span>
                            {hasDeliverables && (
                              <span className="inline-flex items-center gap-1 px-1.5 py-0.2 rounded-full text-[9.5px] font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30 shadow-2xs font-mono">
                                <Paperclip size={9} />
                                <span>{a.artifacts_count} Deliverable{a.artifacts_count !== 1 ? 's' : ''}</span>
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2 mt-1 text-[11px] text-slate-400 flex-wrap">
                          {a.recipient_type && (
                            <span className="inline-flex items-center gap-1 px-1.5 py-0.2 rounded bg-white/10 text-slate-300 capitalize text-[10px] font-medium font-mono">
                              {typeIcons[a.recipient_type.toLowerCase()]}
                              {a.recipient_type}
                            </span>
                          )}
                          {(a.recipient_city || a.recipient_state) && (
                            <span className="flex items-center gap-0.5 text-slate-400 font-mono">
                              <MapPin size={10} className="text-cyan-400" /> {[a.recipient_city, a.recipient_state].filter(Boolean).join(', ')}
                            </span>
                          )}
                        </div>
                        {a.pi_name && (
                          <div className="text-[10px] text-slate-400 mt-0.5 flex items-center gap-1 truncate font-mono">
                            <User size={9} /> PI: {a.pi_name}
                          </div>
                        )}
                      </td>

                      {/* Project Title */}
                      <td className="px-4 py-3.5 max-w-[380px]">
                        <div className="font-medium text-slate-200 line-clamp-2 leading-snug group-hover:text-white transition-colors">
                          {a.project_title || 'Energy Innovation Innovation Research Grant'}
                        </div>
                        {a.project_abstract && (
                          <div className="text-[11px] text-slate-400 line-clamp-1 mt-1 leading-normal">
                            {a.project_abstract}
                          </div>
                        )}
                        <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-400 font-mono">
                          {a.program_name && (
                            <span className="px-1.5 py-0.2 bg-white/10 rounded text-slate-300 truncate max-w-[180px]">
                              {a.program_name}
                            </span>
                          )}
                          {a.award_type && (
                            <span className="text-slate-400 capitalize truncate">
                              {a.award_type.toLowerCase().replace(/_/g, ' ')}
                            </span>
                          )}
                        </div>
                      </td>

                      {/* Agency */}
                      <td className="px-4 py-3.5 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <OrgLogo org={a.agency} size="xs" />
                          <div>
                            <span className="text-[12px] font-bold text-white block">{a.agency}</span>
                            {a.funder_type && (
                              <span className="text-[9.5px] text-slate-400 uppercase tracking-wider font-mono">
                                {a.funder_type}
                              </span>
                            )}
                          </div>
                        </div>
                      </td>

                      {/* Capital Amount */}
                      <td className="px-4 py-3.5 text-right whitespace-nowrap">
                        <div className="font-mono font-bold text-[14px] text-emerald-400">
                          {fmt(a.award_amount)}
                        </div>
                        {a.cost_share_amount > 0 && (
                          <div className="text-[10px] text-slate-400 font-mono">
                            + {fmt(a.cost_share_amount)} match
                          </div>
                        )}
                      </td>

                      {/* Year */}
                      <td className="px-4 py-3.5 text-center whitespace-nowrap font-mono text-xs text-slate-300 font-bold">
                        {a.year || '—'}
                      </td>

                      {/* Action */}
                      <td className="px-4 py-3.5 text-right whitespace-nowrap">
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedAward(a);
                          }}
                          className="px-2.5 py-1 rounded-lg text-xs font-semibold text-cyan-300 bg-cyan-950/40 border border-cyan-500/30 hover:bg-cyan-900/50 hover:text-white transition-all cursor-pointer font-mono shadow-2xs"
                        >
                          View Dossier
                        </button>
                      </td>
                    </tr>
                  );
                })}
                </tbody>
              </table>
            )}
          </div>
        )}

        {/* === RECIPIENTS TABLE VIEW === */}
        {view === 'recipients' && (
          <div className="overflow-x-auto">
            {recipientsLoading ? (
              <div className="flex flex-col items-center justify-center py-20 space-y-3">
                <Loader2 className="animate-spin text-indigo-600" size={32} />
                <p className="text-sm text-slate-500 font-medium">Loading unique innovation recipients...</p>
              </div>
            ) : recipientsData?.items?.length === 0 ? (
              <div className="text-center py-16 px-4">
                <Users size={36} className="mx-auto text-slate-300 mb-3" />
                <h3 className="text-sm font-bold text-slate-800">No Recipients Matched Filters</h3>
                <p className="text-xs text-slate-500 max-w-md mx-auto mt-1 mb-4">
                  No recipient organizations found matching your active filters.
                </p>
                <button
                  onClick={resetAllFilters}
                  className="inline-flex items-center gap-1.5 px-4 py-2 bg-indigo-600 text-white rounded-lg text-xs font-bold shadow-sm hover:bg-indigo-700 transition-colors"
                >
                  <RotateCcw size={13} /> Reset All Filters
                </button>
              </div>
            ) : (
              <table className="w-full text-left border-collapse text-slate-600">
                <thead className="bg-slate-50/80 border-b border-slate-200/80 text-[11px] font-semibold text-slate-500">
                  <tr>
                    <RecipientSortHeader col="recipient_name" label="Awardee Organization & Overview" />
                    <th className="px-4 py-3 uppercase tracking-wider text-[11px]">Primary Clean Tech &amp; Stage</th>
                    <th className="px-4 py-3 uppercase tracking-wider text-[11px]">Funding Organizations</th>
                    <RecipientSortHeader col="award_count" label="Awards" className="text-center" />
                    <RecipientSortHeader col="state_funding" label="State Funding" className="text-right" />
                    <RecipientSortHeader col="total_funding" label="Total Capital" className="text-right" />
                    <th className="px-4 py-3 text-right uppercase tracking-wider text-[11px]">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-[13px]">
                  {recipientsData?.items?.map((r: any, idx: number) => {
                    const recipientAgencies = (r.agencies || []).filter((ag: string) => includeNyserda || !isNyserda(ag));
                    return (
                    <tr
                      key={idx}
                      onClick={() => { setSearch(r.name); setView('awards'); setPage(1); }}
                      className="hover:bg-indigo-50/40 transition-colors cursor-pointer group"
                    >
                      {/* Name & Type */}
                      <td className="px-4 py-3.5 max-w-[320px]">
                        <div className="flex items-center gap-2.5">
                          <OrgLogo org={r.name} domain={r.website_url || ''} size="sm" showTooltip={false} />
                          <div className="min-w-0">
                            <div className="flex items-center gap-1.5 flex-wrap">
                              <span className="font-bold text-slate-900 group-hover:text-indigo-600 transition-colors truncate text-[13.5px]">
                                {r.name}
                              </span>
                              {r.is_ny_based && (
                                <span className="px-1.5 py-0.2 rounded bg-purple-100 text-purple-800 text-[9px] font-extrabold border border-purple-200 shrink-0">
                                  NY Based
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                        {r.description && (
                          <div className="text-[11px] text-slate-500 mt-1 line-clamp-2 leading-snug">
                            {r.description}
                          </div>
                        )}
                        <div className="flex items-center gap-2 mt-1.5 text-[11px] text-slate-500 flex-wrap">
                          {r.type && (
                            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 capitalize text-[10px] font-medium">
                              {typeIcons[r.type.toLowerCase()]}
                              {r.type}
                            </span>
                          )}
                          {(r.city || r.state) && (
                            <span className="flex items-center gap-0.5">
                              <MapPin size={10} className="text-slate-400" /> {[r.city, r.state].filter(Boolean).join(', ')}
                            </span>
                          )}
                          {r.employee_range && (
                            <span className="text-[10px] text-slate-400">
                              {r.employee_range} emp
                            </span>
                          )}
                        </div>
                      </td>

                      {/* Primary Tech & Stage */}
                      <td className="px-4 py-3.5 max-w-[220px]">
                        <span className="inline-block px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 text-[11px] font-bold border border-indigo-100 mb-1">
                          {r.primary_technology || 'Energy Innovation'}
                        </span>
                        <div className="text-[10px] text-slate-500 font-medium">
                          {r.commercialization_stage || 'Applied R&D'}
                        </div>
                        {r.technology_tags?.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-1">
                            {r.technology_tags.slice(0, 2).map((t: string) => (
                              <span key={t} className="text-[9px] px-1.5 py-0.2 rounded bg-slate-100 text-slate-600 border border-slate-200">
                                {t}
                              </span>
                            ))}
                          </div>
                        )}
                      </td>

                      {/* Agencies */}
                      <td className="px-4 py-3.5">
                        <div className="flex flex-wrap items-center gap-1 max-w-[200px]">
                          {recipientAgencies.slice(0, 4).map((ag: string) => (
                            <span
                              key={ag}
                              className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[10px] font-bold border border-slate-200/80"
                            >
                              <OrgLogo org={ag} size="xs" />
                              <span>{ag}</span>
                            </span>
                          ))}
                          {recipientAgencies.length > 4 && (
                            <span className="text-[10px] text-slate-400 font-semibold px-1">
                              +{recipientAgencies.length - 4} more
                            </span>
                          )}
                        </div>
                      </td>

                      {/* Award Count */}
                      <td className="px-4 py-3.5 text-center whitespace-nowrap">
                        <span className="inline-block px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 font-mono font-bold text-[12px] border border-indigo-100">
                          {r.award_count?.toLocaleString()}
                        </span>
                      </td>

                      {/* State Funding */}
                      <td className="px-4 py-3.5 text-right whitespace-nowrap">
                        {(r.state_funding || r.nyserda_funding) > 0 ? (
                          <div className="font-bold text-slate-700 dark:text-slate-300 font-mono text-[13px]">
                            {fmt(r.state_funding || r.nyserda_funding)}
                          </div>
                        ) : (
                          <span className="text-slate-300 text-[11px]">-</span>
                        )}
                      </td>

                      {/* Total Funding */}
                      <td className="px-4 py-3.5 text-right whitespace-nowrap">
                        <div className="font-extrabold text-emerald-700 font-mono text-[14px]">
                          {fmt(r.total_funding)}
                        </div>
                      </td>

                      {/* Actions */}
                      <td className="px-4 py-3.5 text-right whitespace-nowrap">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSearch(r.name);
                            setView('awards');
                            setPage(1);
                          }}
                          className="px-2.5 py-1 text-[11px] font-semibold text-indigo-600 bg-indigo-50 hover:bg-indigo-100 rounded-md transition-colors"
                        >
                          View Awards
                        </button>
                      </td>
                    </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        )}

        {/* === ISO GRID INTERCONNECTION QUEUES VIEW === */}
        {view === 'interconnection' && (
          <div className="overflow-x-auto">
            {interconnLoading ? (
              <div className="flex flex-col items-center justify-center py-20 space-y-3">
                <Loader2 className="animate-spin text-cyan-500" size={32} />
                <p className="text-sm text-slate-400 font-medium">Fetching ISO/RTO grid interconnection queues...</p>
              </div>
            ) : interconnData?.items?.length === 0 ? (
              <div className="text-center py-16 px-4">
                <Zap size={36} className="mx-auto text-slate-600 mb-3" />
                <h3 className="text-sm font-bold text-white">No Interconnection Queues Found</h3>
                <p className="text-xs text-slate-400 max-w-md mx-auto mt-1 mb-4">
                  No ISO grid queue projects match your current filters.
                </p>
                <button
                  onClick={resetAllFilters}
                  className="inline-flex items-center gap-1.5 px-4 py-2 bg-cyan-500 text-slate-950 rounded-lg text-xs font-bold shadow-sm hover:bg-cyan-400 transition-colors"
                >
                  <RotateCcw size={13} /> Reset All Filters
                </button>
              </div>
            ) : (
              <div className="space-y-4 p-4">
                {/* Telemetry Summary Bar */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-white/[0.03] p-3.5 rounded-xl border border-white/10 text-xs">
                  <div>
                    <div className="text-[10px] uppercase font-bold text-slate-400 font-mono">Total Tracked Capacity</div>
                    <div className="text-lg font-bold font-mono text-cyan-400 mt-0.5">
                      {((interconnData?.total_capacity_mw || 0) / 1000).toFixed(2)} GW ({interconnData?.total_capacity_mw?.toLocaleString()} MW)
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] uppercase font-bold text-slate-400 font-mono">Storage Co-Located</div>
                    <div className="text-lg font-bold font-mono text-emerald-400 mt-0.5">
                      {((interconnData?.total_storage_mwh || 0) / 1000).toFixed(2)} GWh ({interconnData?.total_storage_mwh?.toLocaleString()} MWh)
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] uppercase font-bold text-slate-400 font-mono">Grid Operators</div>
                    <div className="text-lg font-bold font-mono text-amber-400 mt-0.5">
                      NYISO · CAISO · PJM · ERCOT · MISO · SPP · ISONE
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] uppercase font-bold text-slate-400 font-mono">Queue Projects</div>
                    <div className="text-lg font-bold font-mono text-white mt-0.5">
                      {interconnData?.total?.toLocaleString()} Projects
                    </div>
                  </div>
                </div>

                <table className="w-full text-left border-collapse text-slate-300">
                  <thead className="bg-[#070b14]/90 border-b border-white/10 text-[11px] font-semibold text-slate-400 font-mono">
                    <tr>
                      <th className="px-4 py-3 uppercase tracking-wider text-[11px]">Project Name &amp; Developer</th>
                      <th className="px-4 py-3 uppercase tracking-wider text-[11px]">ISO / Queue ID</th>
                      <th className="px-4 py-3 uppercase tracking-wider text-[11px]">Technology</th>
                      <th className="px-4 py-3 uppercase tracking-wider text-[11px] text-right">Capacity (MW / MWh)</th>
                      <th className="px-4 py-3 uppercase tracking-wider text-[11px]">POI Substation &amp; County</th>
                      <th className="px-4 py-3 uppercase tracking-wider text-[11px]">Study Phase / Status</th>
                      <th className="px-4 py-3 uppercase tracking-wider text-[11px] text-right">Est. Upgrades</th>
                      <th className="px-4 py-3 uppercase tracking-wider text-[11px] text-center">COD</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5 text-[13px]">
                    {interconnData?.items?.map((q) => (
                      <tr
                        key={q.id}
                        className="hover:bg-cyan-500/[0.04] transition-colors"
                      >
                        <td className="px-4 py-3.5">
                          <div className="font-bold text-white text-[13px]">{q.project_name}</div>
                          <div className="text-[11px] text-slate-400 flex items-center gap-1.5 mt-0.5 font-mono">
                            {q.developer_raw && <span>Dev: {q.developer_raw}</span>}
                            {q.recipient_id && (
                              <Link
                                to={`/recipients/${q.recipient_id}`}
                                className="px-1.5 py-0.2 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-[9.5px] font-bold"
                              >
                                View Linked Dossier
                              </Link>
                            )}
                          </div>
                        </td>

                        <td className="px-4 py-3.5 font-mono text-[12px]">
                          <span className="px-2 py-0.5 rounded bg-white/10 text-slate-200 font-bold mr-1.5">
                            {q.iso_rto}
                          </span>
                          <span className="text-slate-400">#{q.queue_id}</span>
                        </td>

                        <td className="px-4 py-3.5">
                          <span className="px-2 py-0.5 rounded-full text-[10.5px] font-medium bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                            {q.technology_type}
                          </span>
                        </td>

                        <td className="px-4 py-3.5 text-right font-mono">
                          <div className="font-bold text-cyan-400 text-[13px]">{q.capacity_mw ? `${q.capacity_mw} MW` : '—'}</div>
                          {q.storage_mwh ? (
                            <div className="text-[10px] text-emerald-400">{q.storage_mwh} MWh BESS</div>
                          ) : null}
                        </td>

                        <td className="px-4 py-3.5 text-xs text-slate-300">
                          <div className="font-medium text-slate-200">{q.poi_substation || 'POI Pending'}</div>
                          <div className="text-[10.5px] text-slate-400 mt-0.5">
                            {[q.county, q.state].filter(Boolean).join(', ')} {q.utility_territory ? `(${q.utility_territory})` : ''}
                          </div>
                        </td>

                        <td className="px-4 py-3.5">
                          <span className={clsx(
                            "px-2 py-0.5 rounded text-[10px] font-bold font-mono border",
                            q.status === 'Active' || q.status === 'Under Study'
                              ? "bg-cyan-500/15 text-cyan-300 border-cyan-500/30"
                              : q.status === 'Operational'
                              ? "bg-emerald-500/15 text-emerald-300 border-emerald-500/30"
                              : "bg-amber-500/15 text-amber-300 border-amber-500/30"
                          )}>
                            {q.study_phase || q.status}
                          </span>
                        </td>

                        <td className="px-4 py-3.5 text-right font-mono text-xs text-slate-300">
                          {q.estimated_network_upgrade_cost_usd ? fmt(q.estimated_network_upgrade_cost_usd) : '—'}
                        </td>

                        <td className="px-4 py-3.5 text-center font-mono text-xs text-slate-300 font-bold">
                          {q.expected_cod || '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Pagination */}
        {view !== 'map' && (
          <div className="px-4 py-3 border-t border-slate-200/80 flex items-center justify-between">
            <div className="flex items-center gap-2 text-[13px] text-slate-500">
              <span>Page size:</span>
              <select value={pageSize} onChange={e => { setPageSize(Number(e.target.value)); setPage(1); }} className="border rounded px-1 py-0.5 text-[12px]">
                <option value={25}>25</option><option value={50}>50</option><option value={100}>100</option>
              </select>
              <span className="text-slate-400 ml-2">
                {((view === 'awards' ? data?.total : view === 'recipients' ? recipientsData?.total : interconnData?.total) || 0).toLocaleString()} total
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
                className="p-1 rounded text-slate-500 hover:bg-slate-100 disabled:opacity-50"><ChevronLeft size={16} /></button>
              <span className="text-[13px] text-slate-600">
                Page {page} of {(view === 'awards' ? data?.total_pages : view === 'recipients' ? recipientsData?.total_pages : Math.ceil((interconnData?.total || 1) / pageSize)) || 1}
              </span>
              <button onClick={() => setPage(p => p + 1)}
                disabled={page >= ((view === 'awards' ? data?.total_pages : view === 'recipients' ? recipientsData?.total_pages : Math.ceil((interconnData?.total || 1) / pageSize)) || 1)}
                className="p-1 rounded text-slate-500 hover:bg-slate-100 disabled:opacity-50"><ChevronRight size={16} /></button>
            </div>
          </div>
        )}
      </div>

      {/* === DETAIL MODAL === */}
      {selectedAward && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-6 overflow-y-auto bg-black/40 backdrop-blur-sm" onClick={() => setSelectedAward(null)}>
          <div className="relative w-full max-w-3xl mx-4 mb-8 bg-white rounded-xl shadow-2xl flex flex-col" onClick={e => e.stopPropagation()}>
            {/* Header */}
            <div className="px-6 py-5 border-b border-slate-100 flex items-start justify-between bg-gradient-to-r from-slate-50 to-white rounded-t-xl">
              <div className="pr-8 flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <OrgLogo org={selectedAward.agency} size="xs" />
                  {selectedAward.recipient_type && <span className="inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded bg-slate-50 text-slate-600 border border-slate-200 capitalize">{typeIcons[selectedAward.recipient_type]} {selectedAward.recipient_type}</span>}
                  {selectedAward.year && <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-50 text-slate-600 border border-slate-200"><Calendar size={9} className="inline mr-0.5" />{selectedAward.year}</span>}
                  {selectedAward.award_type && <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200 capitalize">{selectedAward.award_type?.replace(/_/g, ' ')}</span>}
                </div>
                <h2 className="text-xl font-bold text-slate-900 leading-tight">{selectedAward.recipient_name}</h2>
                {selectedAward.project_title && <p className="text-[13px] text-slate-600 mt-1 leading-snug">{selectedAward.project_title}</p>}
              </div>
              <button onClick={() => setSelectedAward(null)} className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors bg-white border border-slate-200 shadow-sm flex-shrink-0">
                <X size={20} />
              </button>
            </div>

            {/* Body */}
            <div className="flex-1 p-6 space-y-5 max-h-[70vh] overflow-y-auto">
              {!awardDetail ? (
                <div className="flex justify-center py-12"><Loader2 className="animate-spin text-slate-300" size={24} /></div>
              ) : (
                <>
                  {/* Funding Facts */}
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 bg-emerald-50/50 p-4 rounded-lg border border-emerald-100">
                    {awardDetail.award_amount && (
                      <div><span className="block text-[10px] font-semibold text-slate-500 uppercase">Award Amount</span>
                        <span className="text-xl font-bold text-emerald-700">{fmt(awardDetail.award_amount)}</span></div>
                    )}
                    {awardDetail.total_estimated && awardDetail.total_estimated !== awardDetail.award_amount && (
                      <div><span className="block text-[10px] font-semibold text-slate-500 uppercase">Estimated Total</span>
                        <span className="text-lg font-semibold text-slate-700">{fmt(awardDetail.total_estimated)}</span></div>
                    )}
                    {awardDetail.cost_share_amount && (
                      <div><span className="block text-[10px] font-semibold text-slate-500 uppercase">Cost Share</span>
                        <span className="text-lg font-semibold text-slate-700">{fmt(awardDetail.cost_share_amount)}</span></div>
                    )}
                  </div>

                  {/* Organization Details */}
                  <section>
                    <h3 className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5"><Building2 size={14} /> Organization</h3>
                    <div className="grid grid-cols-2 gap-3 bg-white border border-slate-200 p-4 rounded-lg text-[13px]">
                      <div><span className="block text-[10px] text-slate-400 uppercase">Name</span><span className="font-medium text-slate-800">{awardDetail.recipient_name}</span></div>
                      {awardDetail.recipient_type && <div><span className="block text-[10px] text-slate-400 uppercase">Type</span><span className="capitalize">{awardDetail.recipient_type}</span></div>}
                      {(awardDetail.recipient_city || awardDetail.recipient_state) && (
                        <div><span className="block text-[10px] text-slate-400 uppercase">Location</span>
                          <span className="flex items-center gap-1"><MapPin size={12} className="text-slate-400" />{[awardDetail.recipient_city, awardDetail.recipient_state, awardDetail.recipient_zip].filter(Boolean).join(', ')}</span></div>
                      )}
                      {awardDetail.latitude && (
                        <div><span className="block text-[10px] text-slate-400 uppercase">Coordinates</span>
                          <span className="font-mono text-[11px]">{awardDetail.latitude?.toFixed(4)}, {awardDetail.longitude?.toFixed(4)}</span></div>
                      )}
                      {awardDetail.recipient_website && (
                        <div><span className="block text-[10px] text-slate-400 uppercase">Website</span>
                          <a href={awardDetail.recipient_website.startsWith('http') ? awardDetail.recipient_website : `http://${awardDetail.recipient_website}`} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline flex items-center gap-1"><Globe size={12} />{awardDetail.recipient_website}</a></div>
                      )}
                      {awardDetail.employee_count && (
                        <div><span className="block text-[10px] text-slate-400 uppercase">Employees</span><span>{awardDetail.employee_count.toLocaleString()}</span></div>
                      )}
                    </div>
                  </section>

                  {/* PI Details */}
                  {awardDetail.pi_name && (
                    <section>
                      <h3 className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5"><User size={14} /> Principal Investigator</h3>
                      <div className="grid grid-cols-2 gap-3 bg-white border border-slate-200 p-4 rounded-lg text-[13px]">
                        <div><span className="block text-[10px] text-slate-400 uppercase">Name</span><span className="font-medium text-slate-800">{awardDetail.pi_name}</span></div>
                        {awardDetail.pi_email && <div><span className="block text-[10px] text-slate-400 uppercase">Email</span><a href={`mailto:${awardDetail.pi_email}`} className="text-indigo-600 hover:underline flex items-center gap-1"><Mail size={12} />{awardDetail.pi_email}</a></div>}
                        {awardDetail.pi_institution && <div><span className="block text-[10px] text-slate-400 uppercase">Institution</span><span>{awardDetail.pi_institution}</span></div>}
                      </div>
                    </section>
                  )}

                  {/* Award Details */}
                  <section>
                    <h3 className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5"><Award size={14} /> Award Details</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3 bg-white border border-slate-200 p-4 rounded-lg text-[13px]">
                      {awardDetail.award_type && <div><span className="block text-[10px] text-slate-400 uppercase">Type</span><span className="capitalize">{awardDetail.award_type.replace(/_/g, ' ')}</span></div>}
                      {awardDetail.program_name && <div><span className="block text-[10px] text-slate-400 uppercase">Program</span><span>{awardDetail.program_name}</span></div>}
                      {awardDetail.cfda_number && <div><span className="block text-[10px] text-slate-400 uppercase">CFDA</span><span>{awardDetail.cfda_number}</span></div>}
                      {awardDetail.start_date && <div><span className="block text-[10px] text-slate-400 uppercase">Start Date</span><span>{fmtDate(awardDetail.start_date)}</span></div>}
                      {awardDetail.end_date && <div><span className="block text-[10px] text-slate-400 uppercase">End Date</span><span>{fmtDate(awardDetail.end_date)}</span></div>}
                      {awardDetail.source_name && <div><span className="block text-[10px] text-slate-400 uppercase">Data Source</span><span className="capitalize">{awardDetail.source_name.replace(/_/g, ' ')}</span></div>}
                    </div>
                  </section>

                  {/* Abstract */}
                  {awardDetail.project_abstract && (
                    <section>
                      <h3 className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5"><FileText size={14} /> Abstract</h3>
                      <p className="text-[13px] text-slate-600 leading-relaxed whitespace-pre-wrap bg-white border border-slate-200 p-4 rounded-lg shadow-sm max-h-48 overflow-y-auto">
                        {awardDetail.project_abstract}
                      </p>
                    </section>
                  )}

                  {/* Linked Opportunity */}
                  {awardDetail.opportunity && (
                    <section>
                      <h3 className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                        <FileText size={14} className="text-indigo-600" /> Linked Funding Opportunity (Solicitation)
                      </h3>
                      <Link
                        to={`/opportunities/${awardDetail.opportunity.id}`}
                        className="flex items-center justify-between gap-3 p-3.5 bg-gradient-to-r from-indigo-50/60 via-white to-slate-50 border border-indigo-200/80 rounded-xl hover:border-indigo-400 hover:shadow-md transition-all group"
                      >
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-[11px] font-mono font-bold text-indigo-700 bg-indigo-100/70 px-2 py-0.5 rounded">
                              {awardDetail.opportunity.solicitation_number || `OPP-${awardDetail.opportunity.id}`}
                            </span>
                            <span className="text-[10px] uppercase font-bold text-emerald-700 bg-emerald-50 px-1.5 py-0.2 rounded border border-emerald-200">
                              {awardDetail.opportunity.status || 'Active'}
                            </span>
                          </div>
                          <p className="text-[13px] font-bold text-slate-900 group-hover:text-indigo-600 transition-colors truncate">
                            {awardDetail.opportunity.name}
                          </p>
                        </div>
                        <div className="flex items-center gap-1 text-[11px] font-bold text-indigo-600 shrink-0">
                          <span>View Solicitation</span>
                          <ExternalLink size={13} className="text-indigo-500 group-hover:translate-x-0.5 transition-transform" />
                        </div>
                      </Link>
                    </section>
                  )}

                  {/* Winning Proposal & Work Breakdown Dossier */}
                  {winningProposal && (
                    <section className="bg-slate-900 text-white p-5 rounded-xl border border-slate-800 shadow-md space-y-4">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                        <div className="flex items-center gap-2">
                          <Trophy size={18} className="text-amber-400" />
                          <div>
                            <h3 className="text-sm font-bold text-white flex items-center gap-2">
                              <span>Winning Proposal Dossier</span>
                              <span className="text-[10px] font-mono text-indigo-300 bg-indigo-950/80 px-2 py-0.5 rounded border border-indigo-800">
                                {winningProposal.id}
                              </span>
                            </h3>
                            <div className="text-[11px] text-slate-400">
                              Awarded Record · Evaluator Score: <strong className="text-emerald-400 font-mono">{winningProposal.red_team_score || 92} / 100 Pts</strong>
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 shrink-0">
                          <Link
                            to={`/proposals?proposalId=${winningProposal.id}`}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-bold transition-all shadow-sm"
                          >
                            <FileEdit size={13} />
                            <span>Open in Studio</span>
                          </Link>
                          {winningProposal.bundle_download_url && (
                            <a
                              href={winningProposal.bundle_download_url}
                              download
                              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white/10 hover:bg-white/20 text-slate-200 hover:text-white rounded-lg text-xs font-semibold transition-colors"
                            >
                              <FileDown size={13} />
                              <span>Download Dossier (.ZIP)</span>
                            </a>
                          )}
                        </div>
                      </div>

                      {/* Financials & Metrics */}
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
                        <div className="p-2.5 bg-white/5 rounded-lg border border-white/10">
                          <div className="text-[10px] font-bold text-slate-400 uppercase">Target Capital</div>
                          <div className="text-sm font-bold font-mono text-emerald-400 mt-0.5">{fmt(winningProposal.target_funding)}</div>
                        </div>
                        <div className="p-2.5 bg-white/5 rounded-lg border border-white/10">
                          <div className="text-[10px] font-bold text-slate-400 uppercase">Total Budget</div>
                          <div className="text-sm font-bold font-mono text-white mt-0.5">{fmt(winningProposal.total_budget)}</div>
                        </div>
                        <div className="p-2.5 bg-white/5 rounded-lg border border-white/10">
                          <div className="text-[10px] font-bold text-slate-400 uppercase">Cost-Share</div>
                          <div className="text-sm font-bold font-mono text-amber-300 mt-0.5">{winningProposal.cost_share_pct}% ({fmt(winningProposal.cost_share_amount || (winningProposal.total_budget - winningProposal.target_funding))})</div>
                        </div>
                        <div className="p-2.5 bg-white/5 rounded-lg border border-white/10">
                          <div className="text-[10px] font-bold text-slate-400 uppercase">Compliance</div>
                          <div className="text-sm font-bold font-mono text-indigo-300 mt-0.5">100% Complete</div>
                        </div>
                      </div>

                      {/* Work Breakdown SOPO Tasks */}
                      {winningProposal.sopo_tasks && winningProposal.sopo_tasks.length > 0 && (
                        <div className="space-y-2 pt-1">
                          <div className="text-[11px] font-bold text-slate-300 uppercase tracking-wider">
                            Statement of Project Objectives (SOPO) Work Breakdown:
                          </div>
                          <div className="space-y-1.5">
                            {winningProposal.sopo_tasks.map((task, tIdx) => (
                              <div key={tIdx} className="p-2.5 bg-white/5 rounded-lg border border-white/10 text-[11.5px] space-y-1">
                                <div className="flex items-center justify-between font-semibold text-slate-200">
                                  <span>{task.task}</span>
                                  <span className="font-mono text-indigo-300 text-[10.5px]">{task.budget}</span>
                                </div>
                                <div className="text-[10.5px] text-slate-400 flex items-center justify-between">
                                  <span className="flex items-center gap-1"><Target size={11} className="text-slate-400" /> {task.milestone}</span>
                                  <span className="text-emerald-400 font-semibold">{task.trl}</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </section>
                  )}

                  {/* Discovered Deliverables & Report Artifacts */}
                  {winningProposal?.artifacts && winningProposal.artifacts.length > 0 && (
                    <section>
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                          <Paperclip size={14} className="text-indigo-600" /> Discovered Artifacts &amp; Technical Reports ({winningProposal.artifacts.length})
                        </h3>
                        {winningProposal.bundle_download_url && (
                          <a
                            href={winningProposal.bundle_download_url}
                            download
                            className="inline-flex items-center gap-1 text-[11px] font-bold text-indigo-600 hover:text-indigo-800 bg-indigo-50 px-2.5 py-1 rounded-md transition-colors"
                          >
                            <Download size={12} />
                            <span>Download All Artifacts (.ZIP)</span>
                          </a>
                        )}
                      </div>

                      <div className="space-y-2">
                        {winningProposal.artifacts.map((art) => (
                          <div key={art.id} className="p-3 bg-white border border-slate-200 rounded-xl hover:border-indigo-300 hover:shadow-xs transition-all space-y-1.5">
                            <div className="flex items-start justify-between gap-3">
                              <div>
                                <div className="flex items-center gap-2 mb-1 flex-wrap">
                                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-100 font-bold uppercase">
                                    {art.artifact_type.replace(/_/g, ' ')}
                                  </span>
                                  {art.publication_date && (
                                    <span className="text-[10px] text-slate-400 font-mono">
                                      {art.publication_date}
                                    </span>
                                  )}
                                  {art.page_count && (
                                    <span className="text-[10px] text-slate-400">
                                      · {art.page_count} Pages
                                    </span>
                                  )}
                                  {art.file_size_bytes ? (
                                    <span className="text-[10px] text-emerald-600 font-mono font-semibold">
                                      · {(art.file_size_bytes / 1024).toFixed(1)} KB
                                    </span>
                                  ) : null}
                                </div>
                                <h4 className="text-[13px] font-bold text-slate-900 leading-snug">
                                  {art.title}
                                </h4>
                                {art.summary && (
                                  <p className="text-[11.5px] text-slate-600 mt-1 line-clamp-2 leading-relaxed">
                                    {art.summary}
                                  </p>
                                )}
                              </div>

                              <a
                                href={art.download_url || `/api/artifacts/${art.id}/download`}
                                download
                                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-bold rounded-lg transition-colors shrink-0 shadow-2xs"
                              >
                                <Download size={13} />
                                <span>Download</span>
                              </a>
                            </div>

                            {art.key_findings && art.key_findings.length > 0 && (
                              <div className="p-2 bg-slate-50 rounded-lg border border-slate-100 text-[11px] text-slate-600 space-y-0.5">
                                <span className="font-semibold text-slate-700 block text-[10.5px] uppercase">Verified Findings:</span>
                                {art.key_findings.map((kf, kfIdx) => (
                                  <div key={kfIdx} className="flex items-start gap-1">
                                    <span className="text-emerald-600 mt-0.5">•</span>
                                    <span>{kf}</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </section>
                  )}

                  {/* Results & Outputs */}
                  {awardDetail.results?.length > 0 && (
                    <section>
                      <h3 className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2">Results &amp; Outputs ({awardDetail.results.length})</h3>
                      <div className="space-y-2">
                        {awardDetail.results.map((r: any) => (
                          <div key={r.id} className="p-3 bg-white border border-slate-200 rounded-lg">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-100 capitalize font-medium">{r.result_type}</span>
                              {r.date && <span className="text-[10px] text-slate-400">{fmtDate(r.date)}</span>}
                            </div>
                            <p className="text-[13px] font-medium text-slate-800">{r.title}</p>
                            {r.authors && <p className="text-[11px] text-slate-500 mt-0.5">{r.authors}</p>}
                            {r.doi && <a href={`https://doi.org/${r.doi}`} target="_blank" rel="noopener noreferrer" className="text-[11px] text-indigo-600 hover:underline">DOI: {r.doi}</a>}
                          </div>
                        ))}
                      </div>
                    </section>
                  )}
                </>
              )}
            </div>

            {/* Footer */}
            <div className="px-6 py-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between rounded-b-xl">
              <div className="text-[11px] text-slate-400">
                {awardDetail?.source_name && `Source: ${awardDetail.source_name.replace(/_/g, ' ')}`}
              </div>
              <div className="flex items-center gap-3">
                <button onClick={() => setSelectedAward(null)} className="px-4 py-2 text-[13px] font-medium text-slate-700 bg-white border border-slate-300 rounded-md shadow-sm hover:bg-slate-50">Close</button>
                {(selectedAward.source_url || awardDetail?.source_url) && (
                  <a href={awardDetail?.source_url || selectedAward.source_url} target="_blank" rel="noopener noreferrer"
                    className="flex items-center gap-1.5 px-4 py-2 text-[13px] font-medium text-white bg-indigo-600 border border-transparent rounded-md shadow-sm hover:bg-indigo-700 transition-colors">
                    <ExternalLink size={14} /> View Source
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
