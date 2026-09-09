import React, { useState, useEffect, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { api, isOpportunityNew } from '../api/client';
import {
  Search, Loader2, FolderOpen, ChevronLeft, ChevronRight, ArrowUpDown,
  ShieldAlert, X, Calendar, Mail, Phone, FileText, ExternalLink,
  AlertTriangle, Info, Ban, Star, Download, Printer, Share2, CheckCircle2,
  Building2, HeartHandshake, Filter, Trophy, Paperclip, FileDown, Layers, FileSearch, RotateCcw,
  Zap, Landmark, RefreshCw, Radio, Clock
} from 'lucide-react';
import clsx from 'clsx';
import { saveAs } from 'file-saver';
import { OrgLogo } from '../components/OrgLogo';
import { RealTimeAlertsModal } from '../components/RealTimeAlertsModal';
import { IngestionHubModal } from '../components/IngestionHubModal';
import { FoaShredderModal } from '../components/FoaShredderModal';
import { useNyserda } from '../context/NyserdaContext';
import { useSEO } from '../utils/seo';

function formatCurrency(val: number | null | undefined): string {
  if (!val) return 'Varies';
  if (val >= 1_000_000_000) return `$${(val / 1_000_000_000).toFixed(2)}B`;
  if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(1)}M`;
  if (val >= 1_000) return `$${(val / 1_000).toFixed(0)}K`;
  return `$${val.toFixed(0)}`;
}

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return 'N/A';
  try {
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  } catch { return dateStr; }
}

function formatDeadlineBadge(dateStr: string | null | undefined, status?: string) {
  if (!dateStr) {
    return status === 'open' ? (
      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
        Rolling / Open
      </span>
    ) : (
      <span className="text-slate-300 text-xs">—</span>
    );
  }

  const targetDate = new Date(dateStr);
  if (isNaN(targetDate.getTime())) {
    return <span className="text-slate-500 font-mono text-[12px]">{dateStr}</span>;
  }

  const now = new Date();
  const diffTime = targetDate.getTime() - now.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  const dateFormatted = targetDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

  if (diffDays < 0) {
    return (
      <span className="text-slate-400 text-[11px] font-mono" title={`Closed ${dateFormatted}`}>
        {dateFormatted}
      </span>
    );
  }

  if (diffDays === 0) {
    return (
      <span className="inline-flex items-center gap-1 text-[11px] font-bold text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200" title={dateFormatted}>
        <Clock size={11} className="text-rose-600" /> Closes Today
      </span>
    );
  }

  if (diffDays <= 7) {
    return (
      <span className="inline-flex items-center gap-1 text-[11px] font-bold text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200" title={dateFormatted}>
        <Clock size={11} className="text-rose-600" /> {diffDays} {diffDays === 1 ? 'day' : 'days'} left
      </span>
    );
  }

  if (diffDays <= 30) {
    return (
      <span className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200" title={dateFormatted}>
        <Clock size={11} className="text-amber-600" /> {diffDays}d left
      </span>
    );
  }

  return (
    <div className="flex flex-col text-left" title={`${diffDays} days remaining`}>
      <span className="text-slate-700 font-mono text-[12px]">{dateFormatted}</span>
      <span className="text-[10px] text-slate-400 font-sans">{diffDays}d remaining</span>
    </div>
  );
}

export default function Opportunities() {
  useSEO({
    title: '5,700+ Energy Innovation Solicitations & Grants Database 2026',
    description: 'Search and filter active and historical energy innovation grant solicitations, RFPs, PONs, and FOAs across US DOE, CEC, ARPA-E, MassCEC, and 140+ electric utilities.',
    canonicalUrl: 'https://terminal.aixenergy.io/opportunities',
    keywords: ['energy innovation solicitations', 'DOE funding opportunities', 'cleantech RFPs', 'energy grants 2026', 'utility innovation solicitations', 'ARPA-E grants'],
  });

  const { includeNyserda, isNyserda } = useNyserda();
  const [search, setSearch] = useState('');
  const [showAlertsRadar, setShowAlertsRadar] = useState(false);
  const [showIngestionModal, setShowIngestionModal] = useState(false);
  const [selectedShredId, setSelectedShredId] = useState<number | null>(null);
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [agencyFilter, setAgencyFilter] = useState('');
  const [jurisdictionFilter, setJurisdictionFilter] = useState<string>('ALL');
  const [orgTypeFilter, setOrgTypeFilter] = useState('');
  const [isHistorical, setIsHistorical] = useState<string>('false');
  const [hasArtifactsFilter, setHasArtifactsFilter] = useState<boolean | null>(null);
  const [hasProposalsFilter, setHasProposalsFilter] = useState<boolean | null>(null);
  const [activeCategoryTab, setActiveCategoryTab] = useState<'all' | 'recent' | 'federal' | 'state' | 'economic_development' | 'foundation' | 'utility' | 'watchlist'>('all');

  
  const [yearMin, setYearMin] = useState<number | ''>('');
  const [yearMax, setYearMax] = useState<number | ''>('');
  const [amountMin, setAmountMin] = useState<number | ''>('');
  const [amountMax, setAmountMax] = useState<number | ''>('');

  const [sortBy, setSortBy] = useState('recent');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);

  const hasActiveFilters = Boolean(
    search || statusFilter || typeFilter || agencyFilter ||
    jurisdictionFilter !== 'ALL' || orgTypeFilter || isHistorical !== 'false' ||
    hasArtifactsFilter !== null || hasProposalsFilter !== null ||
    yearMin || yearMax || amountMin || amountMax || activeCategoryTab !== 'all'
  );

  const resetFilters = () => {
    setSearch('');
    setStatusFilter('');
    setTypeFilter('');
    setAgencyFilter('');
    setJurisdictionFilter('ALL');
    setOrgTypeFilter('');
    setIsHistorical('false');
    setHasArtifactsFilter(null);
    setHasProposalsFilter(null);
    setYearMin('');
    setYearMax('');
    setAmountMin('');
    setAmountMax('');
    setActiveCategoryTab('all');
    setPage(1);
  };


  const [selectedOpp, setSelectedOpp] = useState<any | null>(null);

  // Watchlist stored in localStorage
  const [starredIds, setStarredIds] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem('navigator_starred_opps');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const toggleStar = (id: string | number, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    const strId = id.toString();
    setStarredIds(prev => {
      const next = prev.includes(strId) ? prev.filter(x => x !== strId) : [...prev, strId];
      try {
        localStorage.setItem('navigator_starred_opps', JSON.stringify(next));
      } catch {}
      return next;
    });
  };

  // Debounce search
  useEffect(() => {
    const t = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 300);
    return () => clearTimeout(t);
  }, [search]);

  // Sync category tab with orgTypeFilter
  const handleCategoryTabChange = (tab: 'all' | 'recent' | 'federal' | 'state' | 'economic_development' | 'foundation' | 'utility' | 'watchlist') => {
    setActiveCategoryTab(tab);
    setPage(1);
    if (tab === 'all') {
      setOrgTypeFilter('');
      setIsHistorical('false');
      setStatusFilter('');
    } else if (tab === 'recent') {
      setOrgTypeFilter('');
      setIsHistorical('false');
      setStatusFilter('open');
      setSortBy('recent');
      setSortDir('desc');
    } else if (tab === 'federal') {

      setOrgTypeFilter('federal');
      setIsHistorical('false');
    } else if (tab === 'state') {
      setOrgTypeFilter('state');
      setIsHistorical('false');
    } else if (tab === 'economic_development') {
      setOrgTypeFilter('economic_development');
      setIsHistorical('false');
    } else if (tab === 'foundation') {
      setOrgTypeFilter('foundation');
      setIsHistorical('false');
    } else if (tab === 'utility') {
      setOrgTypeFilter('utility');
      setIsHistorical('false');
    } else if (tab === 'watchlist') {
      // Handled via displayedItems memo
    }
  };



  const params: Record<string, any> = {
    search: debouncedSearch || undefined,
    status: statusFilter || undefined,
    type: typeFilter || undefined,
    agency: agencyFilter || undefined,
    jurisdiction: jurisdictionFilter !== 'ALL' ? jurisdictionFilter : undefined,
    org_type: orgTypeFilter || undefined,
    has_artifacts: hasArtifactsFilter !== null ? hasArtifactsFilter : undefined,
    has_winning_proposals: hasProposalsFilter !== null ? hasProposalsFilter : undefined,
    is_historical: isHistorical === 'all' ? undefined : isHistorical,
    year_min: yearMin || undefined,
    year_max: yearMax || undefined,
    amount_min: amountMin || undefined,
    amount_max: amountMax || undefined,
    exclude_nyserda: !includeNyserda ? true : undefined,
    sort_by: sortBy,
    sort_dir: sortDir,
    page,
    page_size: pageSize
  };

  const { data, isLoading, isError } = useQuery({
    queryKey: ['opportunities', params, includeNyserda],
    queryFn: () => api.getOpportunities(params)
  });

  const { data: oppDetail, isLoading: detailLoading } = useQuery<any>({
    queryKey: ['opportunity-detail', selectedOpp?.id],
    queryFn: async () => {
      const res = await fetch(`/api/opportunities/${selectedOpp.id}`);
      if (!res.ok) throw new Error('Failed to fetch opportunity');
      return res.json();
    },
    enabled: !!selectedOpp,
  });

  const { data: agenciesData } = useQuery<any>({
    queryKey: ['agencies', includeNyserda],
    queryFn: () => api.getAgencies(),
  });

  const rawAgencies = Array.isArray(agenciesData) ? agenciesData : agenciesData?.items || [];
  const agencies = useMemo(() => {
    if (includeNyserda) return rawAgencies;
    return rawAgencies.filter((a: any) => !isNyserda(a.name) && !isNyserda(a.code));
  }, [rawAgencies, includeNyserda, isNyserda]);

  const groupedAgencies = useMemo(() => {
    const map: Record<string, any[]> = {
      utility: [],
      federal: [],
      state: [],
      foundation: [],
    };
    agencies.forEach((a: any) => {
      const cat = a.category || 'state';
      if (!map[cat]) map[cat] = [];
      map[cat].push(a);
    });
    return map;
  }, [agencies]);

  const getStatusBadge = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'open': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'closed': return 'bg-slate-100 text-slate-600 border-slate-200';
      case 'draft': return 'bg-slate-50 text-slate-500 border-slate-200';
      default: return 'bg-slate-50 text-slate-500 border-slate-200';
    }
  };

  const handleSort = (col: string) => {
    if (sortBy === col) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(col);
      setSortDir('asc');
    }
    setPage(1);
  };

  const SortHeader = ({ col, label, className = '' }: { col: string, label: string, className?: string }) => (
    <th className={`px-4 py-3 uppercase tracking-wider text-[11px] cursor-pointer hover:bg-slate-100 select-none ${className}`} onClick={() => handleSort(col)}>
      <div className="flex items-center gap-1">
        {label}
        {sortBy === col && <ArrowUpDown size={12} className={sortDir === 'desc' ? 'text-indigo-500' : 'text-indigo-300'} />}
      </div>
    </th>
  );

  // Filter items by watchlist if tab is active
  const displayedItems = useMemo(() => {
    let items = data?.items || [];
    if (!includeNyserda) {
      items = items.filter((opp: any) => !isNyserda(opp.agency) && !isNyserda(opp.source_name) && !isNyserda(opp.name));
    }
    if (activeCategoryTab === 'watchlist') {
      return items.filter((opp: any) => starredIds.includes(opp.id.toString()));
    }
    return items;
  }, [data, activeCategoryTab, starredIds, includeNyserda, isNyserda]);

  return (
    <div className="max-w-7xl mx-auto space-y-6 relative pb-12">
      {/* Standard Page Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
              <FileSearch size={12} className="text-slate-500 dark:text-slate-400" />
              <span>Multi-Agency Index</span>
            </span>
            <span className="text-xs text-slate-300 dark:text-slate-700">|</span>
            <span className="text-xs font-medium text-slate-500 dark:text-slate-400">5,741 Active &amp; Historical Solicitations</span>
            <span className="text-xs text-slate-300 dark:text-slate-700">|</span>

            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/60">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span>Last Synced: Sep 1, 2026</span>
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100 flex items-center gap-2.5">
            Funding Opportunities &amp; Solicitations
          </h1>
          <p className="text-[13px] sm:text-sm text-slate-500 dark:text-slate-400 max-w-3xl mt-1 leading-relaxed">
            Search active RFPs, PONs, FOAs, and utility demonstration solicitations across federal, state, and utility programs spanning all energy innovation domains, grid modernization, and industrial decarbonization.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            type="button"
            onClick={() => setShowIngestionModal(true)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-[12px] font-medium text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors shadow-2xs cursor-pointer"
          >
            <RefreshCw size={13} className="text-slate-500 dark:text-slate-400" />
            <span>Ingestion Status</span>
          </button>

          <button
            type="button"
            onClick={() => setShowAlertsRadar(true)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-[12px] font-medium text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors shadow-2xs cursor-pointer"
          >
            <Radio size={13} className="text-slate-500 dark:text-slate-400" />
            <span>Radar Watchlists</span>
          </button>
        </div>
      </div>

      {/* Cockpit Jurisdiction Segmented Bar */}
      <div className="flex items-center gap-1.5 dark:bg-slate-900 bg-white p-1.5 rounded-xl border dark:border-slate-800 border-slate-200 shadow-xs overflow-x-auto no-scrollbar">
        <span className="text-[10px] font-bold uppercase tracking-wider dark:text-slate-400 text-slate-500 px-2 shrink-0 font-mono">Jurisdiction:</span>
        {[
          { id: 'ALL', label: 'All Multi-State & Federal' },
          { id: 'US_FED', label: 'Federal (DOE / NSF / ARPA-E)' },
          { id: 'NY', label: 'New York (State Programs)' },
          { id: 'CA', label: 'California (CEC & GO-Biz)' },
          { id: 'MA', label: 'Massachusetts (MassCEC)' },
          { id: 'OH', label: 'Ohio (JobsOhio)' },
          { id: 'MI', label: 'Michigan (MEDC)' },
          { id: 'PA', label: 'Pennsylvania (BFTP)' },
          { id: 'CT', label: 'Connecticut (CI)' },
          { id: 'MD', label: 'Maryland (TEDCO)' },
          { id: 'VA', label: 'Virginia (VIPC)' },
          { id: 'CO', label: 'Colorado (OEDIT)' },
          { id: 'MN', label: 'Minnesota (DEED)' },
        ].map((j) => (
          <button
            key={j.id}
            onClick={() => {
              setJurisdictionFilter(j.id);
              setPage(1);
            }}
            className={clsx(
              'px-2.5 py-1 rounded-md text-[11.5px] font-medium transition-all shrink-0 cursor-pointer',
              jurisdictionFilter === j.id
                ? 'bg-slate-900 text-white dark:bg-cyan-500/20 dark:text-cyan-300 dark:border dark:border-cyan-500/40 font-semibold shadow-2xs'
                : 'dark:text-slate-300 text-slate-600 hover:dark:bg-slate-800 hover:bg-slate-100 hover:text-slate-900 dark:hover:text-white'
            )}
          >
            <span>{j.label}</span>
          </button>
        ))}
      </div>

      {/* Cockpit Category Tabs */}
      <div className="flex items-center gap-1 border-b dark:border-slate-800 border-slate-200 pb-1.5 overflow-x-auto no-scrollbar">
        {[
          { id: 'all', label: 'All Solicitations', icon: Layers },
          { id: 'recent', label: 'Live & What\'s New', icon: Zap },
          { id: 'federal', label: 'Federal Agencies', icon: Landmark },
          { id: 'state', label: 'State Energy Agencies', icon: Building2 },
          { id: 'economic_development', label: 'Economic Development', icon: Building2 },
          { id: 'foundation', label: 'Philanthropic Foundations', icon: HeartHandshake },
          { id: 'utility', label: 'Electric & Gas Utilities', icon: Zap },
          { id: 'watchlist', label: `Saved Watchlist (${starredIds.length})`, icon: Star },
        ].map(tab => {
          const Icon = tab.icon;
          const isSelected = activeCategoryTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => handleCategoryTabChange(tab.id as any)}
              className={clsx(
                'px-3 py-1.5 rounded-lg text-[12px] font-semibold transition-all shrink-0 flex items-center gap-1.5 cursor-pointer',
                isSelected
                  ? 'bg-cyan-500/20 text-[#00E5FF] border border-cyan-400/40 shadow-glow-cyan-sm'
                  : tab.id === 'recent'
                  ? 'text-[#00F5A0] bg-emerald-500/10 border border-emerald-500/30 hover:bg-emerald-500/20'
                  : 'dark:text-slate-400 text-slate-600 hover:dark:bg-slate-800/60 hover:bg-slate-100 hover:text-slate-900 dark:hover:text-slate-200'
              )}
            >
              <Icon size={13} className={isSelected ? 'text-[#00E5FF]' : tab.id === 'recent' ? 'text-[#00F5A0]' : 'text-slate-400'} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Cockpit Advanced Filters Console */}
      <div className="dark:bg-[#0d1424]/90 bg-white backdrop-blur-xl p-3.5 rounded-xl border dark:border-white/10 border-slate-200/90 shadow-xl space-y-3">
        <div className="flex items-center gap-2.5 flex-wrap">
          <div className="relative min-w-[240px] flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 dark:text-slate-400 text-slate-500" size={14} />
            <input
              type="text"
              placeholder="Search by title, solicitation number, keywords..."
              className="pl-8 pr-3 h-9 w-full dark:bg-[#090e18] bg-white border dark:border-white/10 border-slate-200 rounded-lg shadow-2xs text-[12.5px] focus:border-cyan-400 outline-none dark:text-white text-slate-900 dark:placeholder-slate-500 placeholder-slate-400 font-medium"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <select
            className="px-3 h-9 border dark:border-white/10 border-slate-200 rounded-lg shadow-2xs text-[12px] dark:bg-[#090e18] bg-white focus:border-cyan-400 outline-none dark:text-slate-200 text-slate-800 font-medium"
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
          >
            <option value="">All Status</option>
            <option value="open">Active Open</option>
            <option value="closed">Closed / Concluded</option>
          </select>

          <select
            className="px-3 h-9 border dark:border-white/10 border-slate-200 rounded-lg shadow-2xs text-[12px] dark:bg-[#090e18] bg-white focus:border-cyan-400 outline-none dark:text-slate-200 text-slate-800 max-w-[220px] font-medium"
            value={agencyFilter}
            onChange={(e) => { setAgencyFilter(e.target.value); setPage(1); }}
          >
            <option value="">All Organizations ({agencies.length})</option>
            {groupedAgencies.utility?.length > 0 && (
              <optgroup label="Electric & Gas Utilities">
                {groupedAgencies.utility.map((ag: any) => (
                  <option key={ag.name} value={ag.name}>{ag.name} ({ag.count})</option>
                ))}
              </optgroup>
            )}
            {groupedAgencies.federal?.length > 0 && (
              <optgroup label="Federal Agencies">
                {groupedAgencies.federal.map((ag: any) => (
                  <option key={ag.name} value={ag.name}>{ag.name} ({ag.count})</option>
                ))}
              </optgroup>
            )}
            {groupedAgencies.state?.length > 0 && (
              <optgroup label="State Energy Agencies">
                {groupedAgencies.state.map((ag: any) => (
                  <option key={ag.name} value={ag.name}>{ag.name} ({ag.count})</option>
                ))}
              </optgroup>
            )}
            {groupedAgencies.foundation?.length > 0 && (
              <optgroup label="Philanthropic Foundations">
                {groupedAgencies.foundation.map((ag: any) => (
                  <option key={ag.name} value={ag.name}>{ag.name} ({ag.count})</option>
                ))}
              </optgroup>
            )}
          </select>

          <div className="flex dark:bg-black/40 bg-slate-100 rounded-lg p-0.5 border dark:border-white/10 border-slate-200 text-xs">
            <button
              type="button"
              onClick={() => { setIsHistorical('false'); setPage(1); }}
              className={clsx(
                "px-2.5 py-1 text-[11.5px] font-semibold rounded-md transition-all cursor-pointer",
                isHistorical === 'false'
                  ? 'dark:bg-cyan-500 bg-white shadow-2xs dark:text-slate-950 text-slate-900 font-bold'
                  : 'dark:text-slate-400 text-slate-600 hover:dark:text-white hover:text-slate-900'
              )}
            >
              Active Open
            </button>
            <button
              type="button"
              onClick={() => { setIsHistorical('true'); setPage(1); }}
              className={clsx(
                "px-2.5 py-1 text-[11.5px] font-semibold rounded-md transition-all cursor-pointer",
                isHistorical === 'true'
                  ? 'dark:bg-cyan-500 bg-white shadow-2xs dark:text-slate-950 text-slate-900 font-bold'
                  : 'dark:text-slate-400 text-slate-600 hover:dark:text-white hover:text-slate-900'
              )}
            >
              Historical
            </button>
            <button
              type="button"
              onClick={() => { setIsHistorical('all'); setPage(1); }}
              className={clsx(
                "px-2.5 py-1 text-[11.5px] font-semibold rounded-md transition-all cursor-pointer",
                isHistorical === 'all'
                  ? 'dark:bg-cyan-500 bg-white shadow-2xs dark:text-slate-950 text-slate-900 font-bold'
                  : 'dark:text-slate-400 text-slate-600 hover:dark:text-white hover:text-slate-900'
              )}
            >
              All Corpus
            </button>
          </div>
        </div>

        {/* Cockpit Quick Presets */}
        <div className="flex items-center gap-2 flex-wrap pt-2 border-t dark:border-white/10 border-slate-200 text-xs">
          <span className="text-[10.5px] font-bold uppercase tracking-wider dark:text-slate-400 text-slate-600 flex items-center gap-1 font-mono">
            <Filter size={12} className="text-slate-500" /> Focus Views:
          </span>

          <button
            type="button"
            onClick={() => {
              if (activeCategoryTab === 'recent') {
                handleCategoryTabChange('all');
              } else {
                handleCategoryTabChange('recent');
              }
            }}
            className={clsx(
              "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium transition-all border cursor-pointer",
              activeCategoryTab === 'recent'
                ? "bg-emerald-600 text-white border-emerald-600 font-bold shadow-xs"
                : "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800/60 hover:bg-emerald-100"
            )}
          >
            <Clock size={11} className={activeCategoryTab === 'recent' ? "text-white" : "text-emerald-500"} />
            <span>New (Last 30 Days)</span>
          </button>

          <button
            type="button"
            onClick={() => {
              setHasProposalsFilter(prev => prev === true ? null : true);
              setPage(1);
            }}
            className={clsx(
              "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium transition-all border cursor-pointer",
              hasProposalsFilter === true
                ? "bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 border-slate-900 dark:border-slate-100 font-semibold shadow-2xs"
                : "dark:bg-white/[0.04] bg-slate-50 dark:text-slate-300 text-slate-700 dark:border-white/10 border-slate-200 hover:dark:bg-white/[0.08] hover:bg-slate-100"
            )}
          >
            <Trophy size={11} className={hasProposalsFilter === true ? "text-amber-400 dark:text-amber-600" : "text-amber-500"} />
            <span>Winning Proposals Precedents</span>
          </button>

          <button
            type="button"
            onClick={() => {
              if (statusFilter === 'open' && isHistorical === 'false') {
                setStatusFilter('');
                setIsHistorical('false');
              } else {
                setStatusFilter('open');
                setIsHistorical('false');
                setSortBy('recent');
              }
              setPage(1);
            }}
            className={clsx(
              "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium transition-all border cursor-pointer",
              statusFilter === 'open' && isHistorical === 'false'
                ? "bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 border-slate-900 dark:border-slate-100 font-semibold shadow-2xs"
                : "dark:bg-emerald-500/10 bg-emerald-50 dark:text-emerald-300 text-emerald-800 dark:border-emerald-500/30 border-emerald-200 hover:bg-emerald-100"
            )}
          >
            <Zap size={11} />
            <span>Open Solicitations</span>
          </button>

          <button
            type="button"
            onClick={() => {
              if (amountMin === 10000000) {
                setAmountMin('');
              } else {
                setAmountMin(10000000);
                setIsHistorical('false');
              }
              setPage(1);
            }}
            className={clsx(
              "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium transition-all border cursor-pointer",
              amountMin === 10000000
                ? "bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 border-slate-900 dark:border-slate-100 font-semibold shadow-2xs"
                : "dark:bg-white/[0.04] bg-slate-50 dark:text-slate-300 text-slate-700 dark:border-white/10 border-slate-200 hover:dark:bg-white/[0.08] hover:bg-slate-100"
            )}
          >
            <Landmark size={11} className={amountMin === 10000000 ? "text-white dark:text-slate-900" : "text-slate-500"} />
            <span>Mega-Programs (&gt;$10M)</span>
          </button>

          <button
            type="button"
            onClick={() => {
              if (orgTypeFilter === 'state') {
                setOrgTypeFilter('');
                setActiveCategoryTab('all');
              } else {
                setOrgTypeFilter('state');
                setActiveCategoryTab('state');
                setIsHistorical('false');
              }
              setPage(1);
            }}
            className={clsx(
              "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium transition-all border cursor-pointer",
              orgTypeFilter === 'state'
                ? "bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 border-slate-900 dark:border-slate-100 font-semibold shadow-2xs"
                : "dark:bg-white/[0.04] bg-slate-50 dark:text-slate-300 text-slate-700 dark:border-white/10 border-slate-200 hover:dark:bg-white/[0.08] hover:bg-slate-100"
            )}
          >
            <Building2 size={11} className={orgTypeFilter === 'state' ? "text-white dark:text-slate-900" : "text-slate-500"} />
            <span>State Matching Funds</span>
          </button>

          <button
            type="button"
            onClick={() => {
              setHasArtifactsFilter(prev => prev === true ? null : true);
              setPage(1);
            }}
            className={clsx(
              "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium transition-all border cursor-pointer",
              hasArtifactsFilter === true
                ? "bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 border-slate-900 dark:border-slate-100 font-semibold shadow-2xs"
                : "dark:bg-white/[0.04] bg-slate-50 dark:text-slate-300 text-slate-700 dark:border-white/10 border-slate-200 hover:dark:bg-white/[0.08] hover:bg-slate-100"
            )}
          >
            <Paperclip size={11} className={hasArtifactsFilter === true ? "text-white dark:text-slate-900" : "text-slate-500"} />
            <span>Deliverables &amp; Reports</span>
          </button>
        </div>

        <div className="flex items-center gap-4 flex-wrap text-[11.5px] pt-1 dark:text-slate-400 text-slate-600 border-t dark:border-white/10 border-slate-200">
          <div className="flex items-center gap-1.5">
            <span className="font-medium dark:text-slate-400 text-slate-600">Year:</span>
            <input type="number" placeholder="Min" value={yearMin} onChange={e => { setYearMin(e.target.value ? Number(e.target.value) : ''); setPage(1); }} className="w-16 px-2 py-1 dark:bg-[#090e18] bg-white border dark:border-white/10 border-slate-200 rounded-md text-xs dark:text-white text-slate-900 outline-none" />
            <span className="text-slate-400">-</span>
            <input type="number" placeholder="Max" value={yearMax} onChange={e => { setYearMax(e.target.value ? Number(e.target.value) : ''); setPage(1); }} className="w-16 px-2 py-1 dark:bg-[#090e18] bg-white border dark:border-white/10 border-slate-200 rounded-md text-xs dark:text-white text-slate-900 outline-none" />
          </div>
          <div className="flex items-center gap-1.5">
            <span className="font-medium dark:text-slate-400 text-slate-600">Funding ($):</span>
            <input type="number" placeholder="Min $" value={amountMin} onChange={e => { setAmountMin(e.target.value ? Number(e.target.value) : ''); setPage(1); }} className="w-24 px-2 py-1 dark:bg-[#090e18] bg-white border dark:border-white/10 border-slate-200 rounded-md text-xs dark:text-white text-slate-900 outline-none" />
            <span className="text-slate-400">-</span>
            <input type="number" placeholder="Max $" value={amountMax} onChange={e => { setAmountMax(e.target.value ? Number(e.target.value) : ''); setPage(1); }} className="w-24 px-2 py-1 dark:bg-[#090e18] bg-white border dark:border-white/10 border-slate-200 rounded-md text-xs dark:text-white text-slate-900 outline-none" />
          </div>
          {hasActiveFilters && (
            <button
              type="button"
              onClick={resetFilters}
              className="text-[11px] font-semibold text-cyan-600 hover:text-cyan-700 dark:text-cyan-400 dark:hover:text-cyan-300 ml-auto cursor-pointer"
            >
              Reset Filters
            </button>
          )}
        </div>
      </div>

      {/* Table Container */}
      <div className="dark:bg-[#0d1424]/90 bg-white backdrop-blur-xl rounded-2xl border dark:border-white/10 border-slate-200 shadow-2xl overflow-hidden dark:text-slate-100 text-slate-800">
        {isLoading && (
          <div className="p-16 flex flex-col items-center justify-center text-slate-400 gap-2">
            <Loader2 className="animate-spin text-cyan-500" size={24} />
            <span className="text-xs font-mono">Querying funding opportunities corpus...</span>
          </div>
        )}

        {isError && (
          <div className="p-8 text-center text-[13px] text-rose-500 font-mono">
            Failed to load opportunities. Ensure the API backend is running.
          </div>
        )}

        {data && (
          <div>
            {/* Sort indicator & stats bar */}
            <div className="px-5 py-2.5 dark:bg-black/40 bg-slate-50 border-b dark:border-white/10 border-slate-200 flex flex-wrap items-center justify-between gap-2 text-[11px] dark:text-slate-400 text-slate-500 font-medium font-mono">
              <div className="flex items-center gap-1.5 font-semibold dark:text-slate-300 text-slate-700">
                <ArrowUpDown size={12} className="text-cyan-500" />
                <span>
                  Primary Sort: <strong className="dark:text-cyan-300 text-cyan-800 font-bold">{sortBy === 'recent' || sortBy === 'solicitation_number' ? 'Most Recent to Least Recent' : sortBy === 'days_since_release' ? 'Days Since Release' : sortBy === 'total_funding' ? 'Financial Amount / Award Size' : sortBy}</strong> ({sortDir === 'desc' ? 'Descending' : 'Ascending'}) • Secondary: <span className="dark:text-slate-300 text-slate-600 font-semibold">Award Size ($)</span>
                </span>
              </div>
              <div className="dark:text-slate-400 text-slate-500">
                Showing <strong className="dark:text-white text-slate-900 font-bold">{displayedItems.length}</strong> of <strong className="dark:text-white text-slate-900 font-bold">{data?.total?.toLocaleString() || '5,741'}</strong> opportunities
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-[13px] whitespace-nowrap">
                <thead className="dark:bg-[#070b14]/90 bg-slate-100/90 dark:text-slate-400 text-slate-600 font-semibold border-b dark:border-white/10 border-slate-200">
                  <tr>
                    <th className="px-3 py-3 w-8 text-center"><Star size={13} className="mx-auto text-slate-400" /></th>
                    <SortHeader col="recent" label="Solicitation" />
                    <SortHeader col="agency" label="Agency" />
                    <SortHeader col="name" label="Opportunity Name & Reference Dossiers" className="w-full" />
                    <SortHeader col="days_since_release" label="Days Since Release" />
                    <th className="px-4 py-3 uppercase tracking-wider text-[11px]">Proposals & Deliverables</th>
                    <SortHeader col="solicitation_type" label="Type" />
                    <SortHeader col="status" label="Status" />
                    <SortHeader col="next_deadline" label="Next Deadline" />
                    <SortHeader col="total_funding" label="Funding / Award Size" />
                    <th className="px-4 py-3 uppercase tracking-wider text-[11px]">Restrictions</th>
                  </tr>
                </thead>
                <tbody className="dark:divide-white/5 divide-slate-100">

                {displayedItems.map((opp: any) => {
                  const isStarred = starredIds.includes(opp.id.toString());
                  const hasExamples = (opp.winning_proposals_count > 0) || (opp.artifacts_count > 0);

                  return (
                    <tr 
                      key={opp.id} 
                      className={clsx(
                        "transition-colors group cursor-pointer",
                        hasExamples ? "dark:bg-amber-500/[0.06] bg-amber-50/40 hover:dark:bg-amber-500/[0.12] hover:bg-amber-50/80" : "hover:dark:bg-white/[0.04] hover:bg-slate-50/80"
                      )}
                      onClick={() => setSelectedOpp(opp)}
                    >
                      <td className="px-3 py-3 text-center">
                        <button
                          type="button"
                          onClick={(e) => toggleStar(opp.id, e)}
                          className="text-slate-400 hover:text-amber-500 transition-colors cursor-pointer p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-800"
                        >
                          <Star size={14} className={clsx(isStarred ? 'fill-amber-400 text-amber-500' : 'text-slate-300 dark:text-slate-600')} />
                        </button>
                      </td>
                      <td className="px-4 py-3">
                        <span className="font-mono text-[12px] font-semibold dark:text-cyan-300 text-cyan-800 dark:group-hover:text-cyan-200 group-hover:text-cyan-900">
                          {opp.solicitation_number}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1.5">
                          <OrgLogo org={opp.agency || 'Agency'} size="xs" />
                          <span className="text-[11px] dark:text-slate-200 text-slate-800 font-semibold">{opp.agency || 'Agency'}</span>
                          {opp.org_type === 'utility' && <span title="Utility"><Zap size={11} className="text-amber-500 shrink-0" /></span>}
                        </div>
                      </td>
                      <td className="px-4 py-3 dark:text-slate-100 text-slate-800 font-medium whitespace-normal max-w-md">
                        <div className="flex items-center gap-2 flex-wrap mb-1">
                          <span className="dark:group-hover:text-cyan-300 group-hover:text-cyan-700 font-bold transition-colors">{opp.name}</span>
                          {isOpportunityNew(opp) && (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9.5px] font-extrabold bg-emerald-600 text-white shadow-xs tracking-wide">
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-200" />
                              <span>NEW</span>
                            </span>
                          )}
                          {opp.status === 'open' && (
                            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9.5px] font-semibold dark:bg-emerald-950/40 bg-emerald-50 dark:text-emerald-400 text-emerald-800 dark:border-emerald-800/60 border-emerald-200 border">
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                              <span>LIVE</span>
                            </span>
                          )}
                          {opp.winning_proposals_count > 0 && (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100/80 text-amber-800 border border-amber-300/80 shadow-2xs">
                              <Trophy size={10} />
                              <span>{opp.winning_proposals_count} Won</span>
                            </span>
                          )}
                          {opp.artifacts_count > 0 && (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-100/80 text-indigo-800 border border-indigo-300/80 shadow-2xs">
                              <Paperclip size={10} />
                              <span>{opp.artifacts_count} Deliverable{opp.artifacts_count !== 1 ? 's' : ''}</span>
                            </span>
                          )}
                        </div>

                        {(opp.vendorRegistrationRequired || opp.procurementPortalUrl) && (
                          <div className="flex items-center gap-2 mt-1">
                            {opp.vendorRegistrationRequired && (
                              <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-medium bg-amber-50 text-amber-700 border border-amber-200">
                                <ShieldAlert size={10} /> Vendor Reg. Required
                              </span>
                            )}
                            {opp.procurementPortalUrl && (
                              <a href={opp.procurementPortalUrl} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-medium bg-slate-50 text-slate-600 border border-slate-200 hover:bg-slate-100" onClick={(e) => e.stopPropagation()}>
                                Bid Portal →
                              </a>
                            )}
                          </div>
                        )}
                      </td>

                      {/* Days Since Release Column */}
                      <td className="px-4 py-3 whitespace-nowrap">
                        <div className="flex flex-col">
                          <span className={clsx(
                            "inline-flex items-center gap-1.5 font-mono text-[12px] font-bold",
                            isOpportunityNew(opp) ? "text-emerald-600 dark:text-emerald-400 font-extrabold" :
                            opp.days_since_release === 0 ? "text-emerald-700" :
                            opp.days_since_release !== null && opp.days_since_release <= 7 ? "text-indigo-600" :
                            opp.days_since_release !== null && opp.days_since_release <= 30 ? "text-slate-800" :
                            "text-slate-500"
                          )}>
                            {opp.days_since_release === null || opp.days_since_release === undefined 
                              ? '—' 
                              : opp.days_since_release === 0 
                                ? 'Today (< 1d)' 
                                : `${opp.days_since_release.toLocaleString()}d ago`}
                            {isOpportunityNew(opp) && (
                              <span className="text-[8.5px] font-extrabold uppercase px-1.5 py-0.2 rounded bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700">
                                NEW
                              </span>
                            )}
                          </span>
                          {opp.release_date && (
                            <span className="text-[10px] text-slate-400 font-mono">{opp.release_date}</span>
                          )}
                        </div>
                      </td>

                      {/* Proposals & Deliverables Actions Column */}
                      <td className="px-4 py-3 whitespace-nowrap">
                        {opp.artifacts_count > 0 ? (
                          <a
                            href={`/api/opportunities/${opp.id}/artifacts/download-bundle`}
                            download
                            onClick={(e) => e.stopPropagation()}
                            className="inline-flex items-center gap-1 px-2.5 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-[11px] font-bold rounded-lg border border-indigo-200 transition-colors shadow-2xs"
                          >
                            <Download size={11} />
                            <span>ZIP ({opp.artifacts_count})</span>
                          </a>
                        ) : opp.winning_proposals_count > 0 ? (
                          <Link
                            to={`/opportunities/${opp.id}`}
                            onClick={(e) => e.stopPropagation()}
                            className="inline-flex items-center gap-1 px-2.5 py-1 bg-amber-50 hover:bg-amber-100 text-amber-800 text-[11px] font-bold rounded-lg border border-amber-200 transition-colors shadow-2xs"
                          >
                            <Trophy size={11} />
                            <span>{opp.winning_proposals_count} Won</span>
                          </Link>
                        ) : (
                          <span className="text-slate-300 text-xs">—</span>
                        )}
                      </td>

                      <td className="px-4 py-3 text-slate-500">{opp.type}</td>
                      <td className="px-4 py-3">
                        <span className={clsx('px-1.5 py-0.5 rounded text-[10px] font-semibold border', getStatusBadge(opp.status))}>
                          {opp.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-slate-600 font-mono text-[12px]">{formatDeadlineBadge(opp.next_deadline, opp.status)}</td>
                      <td className="px-4 py-3 text-slate-800 font-semibold font-mono">{formatCurrency(opp.total_funding)}</td>
                      <td className="px-4 py-3">
                        {opp.restrictions && opp.restrictions.length > 0 ? (
                          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-red-50 text-red-600 border border-red-100">
                            <ShieldAlert size={10} />
                            {opp.restrictions.length}
                          </span>
                        ) : (
                          <span className="text-[11px] text-slate-300">—</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
                {displayedItems.length === 0 && (
                  <tr>
                    <td colSpan={11} className="px-4 py-16 text-center text-slate-400 text-[13px]">
                      <FolderOpen size={36} className="mx-auto mb-2 opacity-40 text-slate-400" />
                      <p className="font-semibold text-slate-700 mb-1">
                        {activeCategoryTab === 'watchlist' 
                          ? 'No opportunities in your saved watchlist'
                          : 'No funding opportunities match your active filters'}
                      </p>
                      <p className="text-xs text-slate-400 max-w-sm mx-auto mb-4">
                        {activeCategoryTab === 'watchlist'
                          ? 'Star solicitations in the directory to bookmark and track them in your private workspace.'
                          : 'Try broadening your search query or reset your filters to inspect the full multi-agency database.'}
                      </p>
                      {activeCategoryTab !== 'watchlist' && (
                        <button
                          type="button"
                          onClick={() => {
                            setSearch('');
                            setAgencyFilter('');
                            setJurisdictionFilter('ALL');
                            setActiveCategoryTab('all');
                            setIsHistorical('false');
                            setPage(1);
                          }}
                          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-bold rounded-xl border border-indigo-200 transition-colors cursor-pointer shadow-2xs"
                        >
                          <RotateCcw size={13} />
                          <span>Reset All Filters</span>
                        </button>
                      )}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
        )}


        
        {/* Pagination */}
        {data && data.total_pages > 1 && (
          <div className="px-4 py-3 border-t border-slate-200/80 flex items-center justify-between">
            <div className="flex items-center gap-2 text-[13px] text-slate-500">
              <span>Page size:</span>
              <select value={pageSize} onChange={e => { setPageSize(Number(e.target.value)); setPage(1); }} className="border rounded px-1.5 py-0.5 text-xs bg-white">
                <option value={20}>20</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <button 
                type="button"
                onClick={() => setPage(p => Math.max(1, p - 1))} 
                disabled={page === 1}
                className="p-1 rounded text-slate-500 hover:bg-slate-100 disabled:opacity-50"
              ><ChevronLeft size={16} /></button>
              <span className="text-[13px] text-slate-600 font-medium">Page {page} of {data.total_pages} ({data.total} total)</span>
              <button 
                type="button"
                onClick={() => setPage(p => Math.min(data.total_pages, p + 1))} 
                disabled={page === data.total_pages}
                className="p-1 rounded text-slate-500 hover:bg-slate-100 disabled:opacity-50"
              ><ChevronRight size={16} /></button>
            </div>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {selectedOpp && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-8 overflow-y-auto bg-black/50 backdrop-blur-xs" onClick={() => setSelectedOpp(null)}>
          <div className="relative w-full max-w-3xl mx-4 mb-8 bg-white rounded-2xl shadow-2xl flex flex-col animate-in fade-in zoom-in-95 duration-150" onClick={e => e.stopPropagation()}>
            
            {/* Header */}
            <div className="px-6 py-5 border-b border-slate-100 flex items-start justify-between bg-slate-50/70 rounded-t-2xl">
              <div className="pr-8">
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <span className="font-mono text-[13px] font-bold text-indigo-600">{selectedOpp.solicitation_number}</span>
                  {isOpportunityNew(selectedOpp) && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-extrabold bg-emerald-600 text-white shadow-2xs">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-200" />
                      <span>NEW · Last 30 Days</span>
                    </span>
                  )}
                  <span className="w-1 h-1 rounded-full bg-slate-300" />
                  <div className="flex items-center gap-1.5">
                    <OrgLogo org={selectedOpp.agency || 'Agency'} size="xs" />
                    <span className="text-[11px] font-bold text-slate-800">{selectedOpp.agency || 'Agency'}</span>
                  </div>
                  <span className={clsx('px-2 py-0.5 rounded text-[10px] font-bold border', getStatusBadge(selectedOpp.status))}>
                    {selectedOpp.status}
                  </span>
                  {selectedOpp.is_historical && (
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-medium border bg-slate-100 text-slate-600 border-slate-200">Historical</span>
                  )}
                </div>
                <h2 className="text-xl font-bold text-slate-900 leading-tight">{selectedOpp.name}</h2>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => toggleStar(selectedOpp.id)}
                  title={starredIds.includes(selectedOpp.id.toString()) ? 'Remove from Watchlist' : 'Add to Watchlist'}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-amber-500 bg-white border border-slate-200 shadow-2xs transition-colors"
                >
                  <Star size={16} className={starredIds.includes(selectedOpp.id.toString()) ? 'fill-amber-400 text-amber-400' : ''} />
                </button>
                <button 
                  type="button"
                  onClick={() => setSelectedOpp(null)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 bg-white border border-slate-200 shadow-2xs transition-colors"
                >
                  <X size={16} />
                </button>
              </div>
            </div>

            {/* Body */}
            <div className="flex-1 p-6 space-y-6 max-h-[70vh] overflow-y-auto">
              {detailLoading ? (
                <div className="flex justify-center items-center py-12"><Loader2 className="animate-spin text-indigo-600" size={24} /></div>
              ) : !oppDetail ? (
                <div className="text-center py-12 text-slate-500">Failed to load details.</div>
              ) : (
                <>
                  {/* Description */}
                  {(oppDetail.overview || oppDetail.description) && (
                    <section>
                      <h3 className="text-[12px] font-bold text-slate-900 mb-2 uppercase tracking-wider">Opportunity Overview</h3>
                      <p className="text-[13.5px] text-slate-600 leading-relaxed whitespace-pre-wrap">
                        {oppDetail.overview || oppDetail.description}
                      </p>
                    </section>
                  )}

                  {/* Key Facts Grid */}
                  <section>
                    <h3 className="text-[12px] font-bold text-slate-900 mb-3 uppercase tracking-wider">Solicitation Parameters</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-y-3.5 gap-x-6 bg-slate-50 p-4 rounded-xl border border-slate-100 text-[13px]">
                      {oppDetail.type && <div><span className="block font-medium text-slate-500 text-[11px] mb-0.5">Type</span><span className="text-slate-800 font-semibold">{oppDetail.type}</span></div>}
                      {oppDetail.days_since_release !== undefined && oppDetail.days_since_release !== null && (
                        <div>
                          <span className="block font-medium text-slate-500 text-[11px] mb-0.5">Days Since Release</span>
                          <span className="text-indigo-700 font-bold">
                            {oppDetail.days_since_release === 0 ? 'Today (< 1 day)' : `${oppDetail.days_since_release.toLocaleString()}d ago`}
                            {oppDetail.release_date && <span className="text-slate-500 font-normal text-xs ml-1">({oppDetail.release_date})</span>}
                          </span>
                        </div>
                      )}
                      {oppDetail.enrollment_type && <div><span className="block font-medium text-slate-500 text-[11px] mb-0.5">Enrollment</span><span className="text-slate-800 font-semibold">{oppDetail.enrollment_type}</span></div>}
                      {oppDetail.year && <div><span className="block font-medium text-slate-500 text-[11px] mb-0.5">Fiscal Year</span><span className="text-slate-800 font-semibold">{oppDetail.year}</span></div>}
                      {oppDetail.total_funding && <div><span className="block font-medium text-slate-500 text-[11px] mb-0.5">Total Allocation</span><span className="text-emerald-700 font-bold">{formatCurrency(oppDetail.total_funding)}</span></div>}
                      {oppDetail.max_award && <div><span className="block font-medium text-slate-500 text-[11px] mb-0.5">Max Award Ceiling</span><span className="text-slate-800 font-semibold">{formatCurrency(oppDetail.max_award)}</span></div>}
                      {oppDetail.cost_share_pct !== undefined && oppDetail.cost_share_pct !== null && <div><span className="block font-medium text-slate-500 text-[11px] mb-0.5">Required Cost-Share</span><span className="text-amber-700 font-semibold">{oppDetail.cost_share_pct}%</span></div>}
                      {oppDetail.performance_period && <div><span className="block font-medium text-slate-500 text-[11px] mb-0.5">Period of Performance</span><span className="text-slate-700">{oppDetail.performance_period}</span></div>}
                      {oppDetail.geographic_scope && <div><span className="block font-medium text-slate-500 text-[11px] mb-0.5">Geographic Scope</span><span className="text-slate-700 capitalize">{oppDetail.geographic_scope}</span></div>}
                      {(oppDetail.trl_min || oppDetail.trl_max) && <div><span className="block font-medium text-slate-500 text-[11px] mb-0.5">Target TRL</span><span className="text-indigo-700 font-bold">TRL {oppDetail.trl_min || '1'} – {oppDetail.trl_max || '9'}</span></div>}
                    </div>
                  </section>


                  {/* Actions & Links */}
                  <div className="flex items-center gap-3 pt-3 border-t border-slate-100 flex-wrap">
                    <Link
                      to={`/opportunities/${selectedOpp.id}`}
                      className="inline-flex items-center gap-1.5 px-4 py-2 bg-indigo-600 text-white rounded-lg text-[13px] font-semibold hover:bg-indigo-700 transition-colors shadow-sm"
                    >
                      <FileText size={14} /> Open Full Solicitation Dossier
                    </Link>
                    <a
                      href={`/api/opportunities/${selectedOpp.id}/artifacts/download-bundle`}
                      download
                      className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-indigo-50 border border-indigo-200 rounded-lg text-[13px] font-semibold text-indigo-700 hover:bg-indigo-100 transition-colors shadow-2xs"
                    >
                      <Download size={14} /> Download Artifacts (.ZIP)
                    </a>
                    {oppDetail.detail_url && (
                      <a href={oppDetail.detail_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-white border border-slate-200 rounded-lg text-[13px] font-medium text-slate-700 hover:bg-slate-50 transition-colors shadow-2xs">
                        <ExternalLink size={14} /> Agency Portal
                      </a>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    
      {/* Real-Time Alerts Radar Modal */}
      <RealTimeAlertsModal
        isOpen={showAlertsRadar}
        onClose={() => setShowAlertsRadar(false)}
      />

      {/* FOA Shredder Modal */}
      {selectedShredId && (
        <FoaShredderModal
          opportunityId={selectedShredId}
          isOpen={!!selectedShredId}
          onClose={() => setSelectedShredId(null)}
        />
      )}
    
      {/* Ingestion Hub Modal */}
      <IngestionHubModal
        isOpen={showIngestionModal}
        onClose={() => setShowIngestionModal(false)}
      />
    </div>
  );
}