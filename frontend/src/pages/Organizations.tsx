import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import {
  Building2, Search, Globe, MapPin, ExternalLink, FileSearch,
  Trophy, Layers, ChevronRight, X, Loader2, Calendar, DollarSign,
  Zap, Landmark, Sparkles, Filter, CheckCircle2
} from 'lucide-react';
import clsx from 'clsx';
import { OrgLogo } from '../components/OrgLogo';
import { useNyserda } from '../context/NyserdaContext';
import { useSEO } from '../utils/seo';

function fmt(v?: number | null): string {
  if (!v) return '—';
  if (v >= 1e9) return `$${(v / 1e9).toFixed(2)}B`;
  if (v >= 1e6) return `$${(v / 1e6).toFixed(1)}M`;
  if (v >= 1e3) return `$${(v / 1e3).toFixed(0)}K`;
  return `$${v.toLocaleString()}`;
}

export default function Organizations() {
  useSEO({
    title: 'Directory of 140+ Clean Energy Funding Organizations & Utilities',
    description: 'Explore the complete index of US federal grant agencies, state energy offices, investor-owned electric utilities, and climate foundations.',
    canonicalUrl: 'https://terminal.aixenergy.io/organizations',
    keywords: ['clean energy funding organizations', 'utility innovation programs', 'state energy agencies directory', 'DOE offices', 'clean energy foundations'],
  });

  const { includeNyserda, isNyserda } = useNyserda();
  const [search, setSearch] = useState('');
  const [selectedOrg, setSelectedOrg] = useState<any | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<'all' | 'utility' | 'federal' | 'state' | 'economic_development' | 'funder' | 'foundation'>('all');

  const { data: orgsData, isLoading } = useQuery({
    queryKey: ['organizations'],
    queryFn: () => api.getOrganizations(),
  });

  const { data: agenciesData } = useQuery({
    queryKey: ['agencies'],
    queryFn: () => api.getAgencies(),
  });

  const orgs = useMemo(() => {
    const list = Array.isArray(orgsData) ? orgsData : orgsData?.items || [];
    return list.filter((o: any) => {
      if (!includeNyserda && (isNyserda(o.name) || isNyserda(o.acronym) || isNyserda(o.id))) return false;
      if (categoryFilter !== 'all') {
        const cat = o.org_type || o.category || 'funder';
        if (categoryFilter === 'utility' && cat !== 'utility') return false;
        if (categoryFilter === 'federal' && cat !== 'federal') return false;
        if (categoryFilter === 'state' && cat !== 'state' && cat !== 'state_agency') return false;
        if (categoryFilter === 'economic_development' && cat !== 'economic_development') return false;
        if (categoryFilter === 'funder' && cat !== 'funder' && cat !== 'venture_capital') return false;
        if (categoryFilter === 'foundation' && cat !== 'foundation') return false;
      }
      if (!search.trim()) return true;
      const s = search.toLowerCase();
      return (
        o.name?.toLowerCase().includes(s) ||
        o.org_type?.toLowerCase().includes(s) ||
        o.state?.toLowerCase().includes(s) ||
        o.description?.toLowerCase().includes(s)
      );
    });
  }, [orgsData, categoryFilter, search]);

  const { data: orgDetail, isLoading: detailLoading } = useQuery({
    queryKey: ['org-detail-network', selectedOrg?.id],
    queryFn: () => api.getNodeDetail('organization', selectedOrg.id),
    enabled: !!selectedOrg?.id,
  });

  const detail = orgDetail || {};

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Standard Page Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
              <Building2 size={12} className="text-indigo-600" />
              <span>Institutional Directory</span>
            </span>
            <span className="text-xs text-slate-300">|</span>
            <span className="text-xs font-semibold text-slate-500">200+ Innovation Entities</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2.5">
            Funding Organizations &amp; Utilities
          </h1>
          <p className="text-[13px] sm:text-sm text-slate-500 max-w-3xl mt-1 leading-relaxed">
            Authoritative registry of federal funding agencies, state economic development &amp; energy authorities, electric &amp; gas utilities, and institutional climate VC funds.
          </p>
        </div>

        <div className="relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search organizations, acronyms, states..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="pl-8 pr-3 py-1.5 bg-white border border-slate-200 rounded-lg text-[13px] w-64 focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 outline-none shadow-2xs placeholder-slate-400"
          />
        </div>
      </div>

      {/* Cockpit Category Tabs */}
      <div className="flex items-center gap-1.5 border-b border-slate-200/80 pb-2 overflow-x-auto no-scrollbar">
        {[
          { id: 'all', label: 'All Organizations', icon: Globe },
          { id: 'utility', label: 'Electric & Gas Utilities', icon: Zap },
          { id: 'federal', label: 'Federal Agencies', icon: Landmark },
          { id: 'state', label: 'State Energy Agencies', icon: Building2 },
          { id: 'economic_development', label: 'Economic Development', icon: Building2 },
          { id: 'funder', label: 'Climate VC & Funders', icon: DollarSign },
          { id: 'foundation', label: 'Philanthropic Foundations', icon: Sparkles },
        ].map(tab => {
          const Icon = tab.icon;
          const isSelected = categoryFilter === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => setCategoryFilter(tab.id as any)}
              className={clsx(
                'px-3 py-1.5 rounded-lg text-[12px] font-semibold transition-all shrink-0 flex items-center gap-1.5 cursor-pointer',
                isSelected
                  ? 'bg-slate-900 text-white shadow-2xs'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              )}
            >
              <Icon size={12} className={isSelected ? 'text-cyan-300' : 'text-slate-400'} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {isLoading ? (
        <div className="h-64 flex items-center justify-center">
          <Loader2 className="animate-spin text-indigo-600" size={28} />
        </div>
      ) : (
        <div className="flex gap-5 min-h-0 items-start">
          {/* Org Grid */}
          <div className={clsx("flex-1 grid gap-3.5 auto-rows-min transition-all", selectedOrg ? "grid-cols-1 lg:grid-cols-2" : "grid-cols-1 md:grid-cols-2 lg:grid-cols-3")}>
            {orgs.map((org: any) => (
              <button
                key={org.id}
                type="button"
                onClick={() => setSelectedOrg(org)}
                className={clsx(
                  "text-left bg-white rounded-xl border p-4 hover:shadow-md transition-all group shadow-2xs",
                  selectedOrg?.id === org.id
                    ? "border-indigo-400 ring-2 ring-indigo-100 shadow-md"
                    : "border-slate-200/80 hover:border-indigo-300"
                )}
              >
                <div className="flex items-start gap-3">
                  <OrgLogo org={org.name} domain={org.domain || org.website} size="md" />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-1">
                      <h3 className="text-[13.5px] font-bold text-slate-900 group-hover:text-indigo-700 transition-colors truncate">
                        {org.name}
                      </h3>
                      <ChevronRight size={14} className="text-slate-300 group-hover:text-indigo-500 shrink-0" />
                    </div>
                    <div className="flex items-center gap-2 mt-1 flex-wrap">
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 uppercase tracking-wider">
                        {org.org_type || 'Funder'}
                      </span>
                      {org.state && (
                        <span className="text-[10px] text-slate-500 font-medium flex items-center gap-0.5">
                          <MapPin size={10} className="text-slate-400" />
                          {org.state}
                        </span>
                      )}
                    </div>
                    {org.description && (
                      <p className="text-[11.5px] text-slate-500 mt-2 line-clamp-2 leading-relaxed">
                        {org.description}
                      </p>
                    )}
                  </div>
                </div>
              </button>
            ))}
            {orgs.length === 0 && (
              <div className="text-sm text-slate-500 col-span-full text-center py-16">
                No organizations match &ldquo;{search}&rdquo;.
              </div>
            )}
          </div>

          {/* Detail Panel */}
          {selectedOrg && (
            <div className="w-96 bg-white rounded-2xl border border-slate-200 shadow-xl flex flex-col max-h-[calc(100vh-12rem)] overflow-hidden shrink-0 sticky top-4 animate-in slide-in-from-right-2 duration-150">
              <div className="px-5 py-4 border-b border-slate-100 bg-slate-50 flex items-start justify-between rounded-t-2xl">
                <div className="flex items-start gap-3">
                  <OrgLogo org={selectedOrg.name} domain={selectedOrg.domain || selectedOrg.website} size="md" />
                  <div>
                    <h2 className="text-[14px] font-bold text-slate-900 leading-snug">{selectedOrg.name}</h2>
                    <div className="flex items-center gap-2 mt-1 flex-wrap">
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-800 uppercase tracking-wider">
                        {selectedOrg.org_type || 'Funder'}
                      </span>
                      {selectedOrg.state && (
                        <span className="text-[11px] text-slate-500 font-medium">
                          {selectedOrg.city ? `${selectedOrg.city}, ` : ''}{selectedOrg.state}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedOrg(null)}
                  className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-200/60"
                >
                  <X size={16} />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto p-5 space-y-4">
                {detailLoading && (
                  <div className="flex justify-center py-8">
                    <Loader2 className="animate-spin text-indigo-600" size={20} />
                  </div>
                )}

                {selectedOrg.description && (
                  <p className="text-[12.5px] text-slate-600 leading-relaxed">
                    {selectedOrg.description}
                  </p>
                )}

                {selectedOrg.website && (
                  <a
                    href={selectedOrg.website.startsWith('http') ? selectedOrg.website : `https://${selectedOrg.website}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[12px] font-semibold text-indigo-600 hover:underline flex items-center gap-1"
                  >
                    <ExternalLink size={12} />
                    <span>Official Portal ({selectedOrg.website})</span>
                  </a>
                )}

                {/* Stats */}
                {(detail.direct_award_stats || detail.opportunities) && (
                  <div className="grid grid-cols-2 gap-2 bg-indigo-50/50 p-3 rounded-xl border border-indigo-100">
                    {detail.opportunities?.length > 0 && (
                      <div>
                        <span className="block text-[9px] font-bold text-slate-500 uppercase">Opportunities</span>
                        <span className="text-base font-bold text-indigo-700">{detail.opportunities.length}</span>
                      </div>
                    )}
                    {detail.direct_award_stats?.count > 0 && (
                      <div>
                        <span className="block text-[9px] font-bold text-slate-500 uppercase">Awards</span>
                        <span className="text-base font-bold text-slate-800 font-mono">{detail.direct_award_stats.count.toLocaleString()}</span>
                      </div>
                    )}
                    {detail.direct_award_stats?.total_funding > 0 && (
                      <div>
                        <span className="block text-[9px] font-bold text-slate-500 uppercase">Total Deployed</span>
                        <span className="text-base font-bold text-emerald-700 font-mono">{fmt(detail.direct_award_stats.total_funding)}</span>
                      </div>
                    )}
                    {detail.direct_award_stats?.unique_recipients > 0 && (
                      <div>
                        <span className="block text-[9px] font-bold text-slate-500 uppercase">Recipients</span>
                        <span className="text-base font-bold text-slate-700 font-mono">{detail.direct_award_stats.unique_recipients.toLocaleString()}</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Direct Link to Filtered Opportunities */}
                <Link
                  to={`/opportunities?agency=${encodeURIComponent(selectedOrg.name)}`}
                  className="w-full inline-flex items-center justify-center gap-1.5 px-3 py-2 bg-slate-900 text-white rounded-lg text-[12px] font-semibold hover:bg-slate-800 transition-colors shadow-2xs"
                >
                  <FileSearch size={13} />
                  <span>View All {selectedOrg.name} Opportunities</span>
                </Link>

                {/* Programs */}
                {detail.programs?.length > 0 && (
                  <div>
                    <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                      <Layers size={12} /> Innovation Portfolios ({detail.programs.length})
                    </h3>
                    <div className="space-y-1.5">
                      {detail.programs.map((p: any) => (
                        <div key={p.id} className="p-2.5 bg-slate-50 rounded-lg border border-slate-100">
                          <div className="flex items-center justify-between">
                            <span className="text-[12px] font-bold text-slate-800">{p.name}</span>
                            <span className={clsx("text-[9px] px-1.5 py-0.2 rounded-full font-bold", p.active ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : "bg-slate-100 text-slate-500")}>
                              {p.active ? 'Active' : 'Inactive'}
                            </span>
                          </div>
                          {p.description && <p className="text-[10px] text-slate-500 mt-1 line-clamp-2">{p.description}</p>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
