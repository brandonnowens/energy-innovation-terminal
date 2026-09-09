import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { Loader2, ExternalLink, Beaker, Rocket, GraduationCap, Wrench, Building2, Search, X, ChevronDown, Check, Building, FileSearch, Network, ShieldCheck, Layers, DollarSign, Calendar, Trophy, Clock } from 'lucide-react';
import clsx from 'clsx';
import { Link } from 'react-router-dom';
import { OrgLogo } from '../components/OrgLogo';
import { OrgSelect, OrgOption } from '../components/OrgSelect';
import { useNyserda } from '../context/NyserdaContext';

const typeConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  innovation: { label: 'Innovation R&D', color: 'bg-indigo-50 border-indigo-200 text-indigo-700', icon: <Beaker size={16} className="text-indigo-600" /> },
  commercialization: { label: 'Commercialization', color: 'bg-purple-50 border-purple-200 text-purple-700', icon: <Rocket size={16} className="text-purple-600" /> },
  technical_assistance: { label: 'Technical Assistance', color: 'bg-blue-50 border-blue-200 text-blue-700', icon: <Wrench size={16} className="text-blue-600" /> },
  deployment: { label: 'Deployment', color: 'bg-amber-50 border-amber-200 text-amber-700', icon: <Building2 size={16} className="text-amber-600" /> },
  workforce: { label: 'Workforce', color: 'bg-teal-50 border-teal-200 text-teal-700', icon: <GraduationCap size={16} className="text-teal-600" /> },
  inferred: { label: 'Inferred', color: 'bg-slate-50 border-slate-200 text-slate-600', icon: <Layers size={16} className="text-slate-500" /> },
};

function formatCurrency(value?: number | null) {
  if (!value) return null;
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);
}

export default function Programs() {
  const { includeNyserda, isNyserda } = useNyserda();
  const [selectedOrgId, setSelectedOrgId] = useState<string>('');
  const [selectedProgram, setSelectedProgram] = useState<any | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');

  // Agencies list for org selector
  const { data: agenciesData, isLoading: orgsLoading } = useQuery<any>({
    queryKey: ['agencies'],
    queryFn: () => api.getAgencies(),
  });

  const agencies: OrgOption[] = useMemo(() => {
    let list: OrgOption[] = [];
    if (Array.isArray(agenciesData)) list = agenciesData;
    else if (agenciesData && Array.isArray(agenciesData.items)) list = agenciesData.items;
    return list.filter(a => includeNyserda || (!isNyserda(a.name) && !isNyserda(a.code)));
  }, [agenciesData, includeNyserda, isNyserda]);

  // Default to ALL for full multi-agency program portfolio overview
  React.useEffect(() => {
    if (!selectedOrgId || (!includeNyserda && isNyserda(selectedOrgId))) {
      setSelectedOrgId('ALL');
    }
  }, [selectedOrgId, includeNyserda, isNyserda]);

  const categories = useMemo(() => {
    const cats = agenciesData?.categories || [];
    if (includeNyserda) return cats;
    return cats.map((cat: any) => ({
      ...cat,
      items: (cat.items || []).filter((item: any) => !isNyserda(item.name) && !isNyserda(item.code))
    })).filter((cat: any) => cat.items.length > 0);
  }, [agenciesData, includeNyserda, isNyserda]);

  const currentOrg = useMemo(() => {
    if (!selectedOrgId || selectedOrgId === 'ALL') {
      return { name: 'All Organizations', code: 'ALL', count: agencies.reduce((s, a) => s + (a.count || 0), 0) };
    }
    return agencies.find(o => o.name === selectedOrgId || o.code === selectedOrgId) || { name: selectedOrgId, count: 0 };
  }, [agencies, selectedOrgId]);

  // Programs filtered by selected org
  const { data: programsData, isLoading: progsLoading, isError: progsError } = useQuery({
    queryKey: ['programs', selectedOrgId],
    queryFn: () => api.getPrograms(selectedOrgId && selectedOrgId !== 'ALL' ? { organization: selectedOrgId } : {}),
  });

  const rawPrograms = useMemo(() => {
    const list = (programsData as any[]) || [];
    if (includeNyserda) return list;
    return list.filter((p: any) => !isNyserda(p.organization) && !isNyserda(p.agency) && !isNyserda(p.name));
  }, [programsData, includeNyserda, isNyserda]);

  // Filter by search query
  const programs = useMemo(() => {
    if (!searchTerm.trim()) return rawPrograms;
    const q = searchTerm.toLowerCase();
    return rawPrograms.filter((p: any) => {
      if (p.name?.toLowerCase().includes(q)) return true;
      if (p.description?.toLowerCase().includes(q)) return true;
      if (p.target_stage?.toLowerCase().includes(q)) return true;
      if (p.focus_areas?.some((fa: any) => (typeof fa === 'string' ? fa : fa.name)?.toLowerCase().includes(q))) return true;
      return false;
    });
  }, [rawPrograms, searchTerm]);

  // Program opportunities (fetched when modal opens)
  const { data: programOpps, isLoading: oppsLoading } = useQuery({
    queryKey: ['program-opportunities', selectedProgram?.id, selectedOrgId],
    queryFn: () => api.getProgramOpportunities(selectedProgram!.id, selectedOrgId && selectedOrgId !== 'ALL' ? selectedOrgId : undefined),
    enabled: !!selectedProgram,
  });

  // Group by type
  const grouped: Record<string, any[]> = {};
  programs.forEach((p: any) => {
    const type = p.program_type || 'other';
    if (!grouped[type]) grouped[type] = [];
    grouped[type].push(p);
  });

  // Stats
  const totalPrograms = rawPrograms.length;
  const totalOpps = rawPrograms.reduce((s: number, p: any) => s + (p.opportunities_count || 0), 0);
  const activeOpps = rawPrograms.reduce((s: number, p: any) => s + (p.active_opportunities_count || 0), 0);
  const totalFunding = rawPrograms.reduce((s: number, p: any) => s + (p.total_funding || 0), 0);
  const totalAwards = rawPrograms.reduce((s: number, p: any) => s + (p.award_count || 0), 0);
  const totalAwarded = rawPrograms.reduce((s: number, p: any) => s + (p.total_awarded || 0), 0);

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Standard Page Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md text-[11px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
              <Layers size={12} className="text-indigo-600" />
              <span>Program Portfolios</span>
            </span>
            <span className="text-xs text-slate-300">|</span>
            <span className="text-xs font-semibold text-slate-500">{totalPrograms} Structured Initiatives</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2.5">
            Programs &amp; Portfolios
          </h1>
          <p className="text-[13px] sm:text-sm text-slate-500 max-w-3xl mt-1 leading-relaxed">
            Browse structured energy innovation programs, non-wires solutions, and research portfolios across utilities and government agencies.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 w-full md:w-auto">
          <div className="relative w-full sm:w-64">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Filter programs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-8 pr-8 py-2 bg-white border border-slate-200 rounded-lg text-xs outline-none focus:ring-2 focus:ring-indigo-500 shadow-2xs"
            />
            {searchTerm && (
              <button onClick={() => setSearchTerm('')} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                <X size={12} />
              </button>
            )}
          </div>

          <div className="w-full sm:w-72 shrink-0">
            <OrgSelect
              label="Select Organization"
              value={selectedOrgId}
              onChange={(val) => {
                setSelectedOrgId(val);
                setSelectedProgram(null);
              }}
              options={agencies}
              categories={categories}
            />
          </div>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 relative z-10">
        {[
          { label: 'Programs', value: totalPrograms, icon: <Layers size={16} className="text-indigo-500" /> },
          { label: 'Total Opportunities', value: totalOpps.toLocaleString(), icon: <FileSearch size={16} className="text-sky-500" /> },
          { label: 'Currently Open', value: activeOpps.toLocaleString(), icon: <Clock size={16} className="text-emerald-500" /> },
          { label: 'Tracked Awards', value: totalAwards.toLocaleString(), icon: <Trophy size={16} className="text-amber-500" /> },
          { label: 'Total Program Funding', value: totalFunding > 0 ? formatCurrency(totalFunding) : (totalAwarded > 0 ? formatCurrency(totalAwarded) : 'N/A'), icon: <DollarSign size={16} className="text-emerald-500" /> },
        ].map((stat, i) => (
          <div key={i} className="bg-white rounded-xl border border-slate-200/80 p-3.5 shadow-2xs">
            <div className="flex items-center gap-1.5 mb-1">
              {stat.icon}
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{stat.label}</span>
            </div>
            <div className="text-xl font-bold text-slate-900 font-mono">{stat.value}</div>
          </div>
        ))}
      </div>

      {/* Programs Grid */}
      <div className="relative z-10">
        {progsLoading ? (
          <div className="flex justify-center items-center h-64"><Loader2 className="animate-spin text-slate-300" size={24} /></div>
        ) : progsError ? (
          <div className="text-center p-8 bg-red-50 border border-red-100 rounded-lg text-[13px] text-red-600">
            Failed to load programs. <button onClick={() => window.location.reload()} className="underline font-medium">Retry</button>
          </div>
        ) : programs.length === 0 ? (
          <div className="text-center p-12 bg-white border border-slate-200/80 rounded-lg shadow-[var(--shadow-xs)]">
            <div className="w-12 h-12 rounded-full bg-slate-50 flex items-center justify-center mx-auto mb-4 border border-slate-100">
              <Layers size={20} className="text-slate-400" />
            </div>
            <h3 className="text-base font-semibold text-slate-900 mb-1">No programs found</h3>
            <p className="text-[13px] text-slate-500 max-w-sm mx-auto mb-4">
              Programs for {currentOrg.name} have not yet been cataloged. {currentOrg.count} opportunities are available.
            </p>
            <Link 
              to={`/opportunities?agency=${encodeURIComponent(currentOrg.name)}`}
              className="inline-flex items-center gap-1.5 px-4 py-2 text-[13px] font-medium text-white bg-indigo-600 border border-transparent rounded-md shadow-sm hover:bg-indigo-700 transition-colors"
            >
              <FileSearch size={14} /> View Opportunities
            </Link>
          </div>
        ) : (
          <div className="space-y-8">
            {Object.entries(grouped).map(([type, progs]) => {
              const cfg = typeConfig[type] || { label: type, color: 'bg-slate-50 border-slate-200 text-slate-700', icon: <Beaker size={16} /> };
              return (
                <div key={type}>
                  <h3 className="text-[13px] font-medium text-slate-900 mb-3 flex items-center gap-2 uppercase tracking-wide">
                    {cfg.icon} {cfg.label} <span className="text-slate-400 font-normal">({progs.length})</span>
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {progs.map((prog: any) => (
                      <div 
                        key={prog.id} 
                        className="bg-white rounded-lg border border-slate-200/80 p-4 shadow-[var(--shadow-xs)] flex flex-col hover:border-indigo-300 hover:shadow-md transition-all cursor-pointer group relative"
                        onClick={() => setSelectedProgram(prog)}
                      >
                        <div className="flex items-start justify-between gap-2 mb-2">
                          <h4 className="font-medium text-[13px] text-slate-900 leading-snug group-hover:text-indigo-700 transition-colors">{prog.name}</h4>
                          <div className="shrink-0 flex items-center gap-1.5 mt-0.5">
                            {prog.active_opportunities_count > 0 ? (
                              <div className="w-2 h-2 rounded-full bg-green-500" title="Has open opportunities" />
                            ) : (
                              <div className="w-2 h-2 rounded-full bg-slate-300" title="No open opportunities" />
                            )}
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-2 mb-3">
                          <OrgLogo org={currentOrg.name} size="xs" />
                          <span className={clsx('px-1.5 py-0.5 rounded text-[10px] font-medium border', cfg.color)}>
                            {cfg.label}
                          </span>
                        </div>

                        <p className="text-[12px] text-slate-500 mb-3 line-clamp-2 leading-relaxed">{prog.description}</p>

                        {/* Opportunity & Award counts */}
                        <div className="mt-auto pt-3 border-t border-slate-100 grid grid-cols-3 gap-2 text-center">
                          <div>
                            <div className="text-[15px] font-bold text-slate-900">{prog.opportunities_count || 0}</div>
                            <div className="text-[10px] text-slate-500 uppercase">Opps</div>
                          </div>
                          <div>
                            <div className="text-[15px] font-bold text-emerald-700">{prog.active_opportunities_count || 0}</div>
                            <div className="text-[10px] text-slate-500 uppercase">Open</div>
                          </div>
                          <div>
                            <div className="text-[15px] font-bold text-amber-700">{prog.award_count || 0}</div>
                            <div className="text-[10px] text-slate-500 uppercase">Awards</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Program Detail Modal */}
      {selectedProgram && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
          <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" onClick={() => setSelectedProgram(null)}></div>
          <div className="relative w-full max-w-4xl max-h-[90vh] bg-white rounded-xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            
            {/* Header */}
            <div className="px-6 py-5 border-b border-slate-100 flex items-start justify-between bg-slate-50/50">
              <div className="pr-8">
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <OrgLogo org={currentOrg.name} size="xs" />
                  <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">{currentOrg.name}</span>
                  <span className="w-1 h-1 rounded-full bg-slate-300"></span>
                  <span className={clsx('px-1.5 py-0.5 rounded text-[10px] font-medium border', (typeConfig[selectedProgram.program_type || 'other'] || typeConfig.inferred).color)}>
                    {(typeConfig[selectedProgram.program_type || 'other'] || {label: selectedProgram.program_type}).label}
                  </span>
                  {selectedProgram.active_opportunities_count > 0 ? (
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-medium border bg-emerald-50 text-emerald-700 border-emerald-200">{selectedProgram.active_opportunities_count} Open</span>
                  ) : (
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-medium border bg-slate-100 text-slate-600 border-slate-200">No Open Opps</span>
                  )}
                </div>
                <h2 className="text-xl font-bold text-slate-900 leading-tight">{selectedProgram.name}</h2>
              </div>
              <button onClick={() => setSelectedProgram(null)} className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer">
                <X size={20} />
              </button>
            </div>

            {/* Body */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              
              {/* Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="bg-slate-50 rounded-lg p-3 border border-slate-100 text-center">
                  <div className="text-lg font-bold text-slate-900 font-mono">{selectedProgram.opportunities_count || 0}</div>
                  <div className="text-[10px] text-slate-500 uppercase font-medium">Total Opportunities</div>
                </div>
                <div className="bg-emerald-50 rounded-lg p-3 border border-emerald-100 text-center">
                  <div className="text-lg font-bold text-emerald-700 font-mono">{selectedProgram.active_opportunities_count || 0}</div>
                  <div className="text-[10px] text-emerald-600 uppercase font-medium">Currently Open</div>
                </div>
                <div className="bg-amber-50 rounded-lg p-3 border border-amber-100 text-center">
                  <div className="text-lg font-bold text-amber-700">{selectedProgram.award_count || 0}</div>
                  <div className="text-[10px] text-amber-600 uppercase font-medium">Awards</div>
                </div>
                <div className="bg-emerald-50 rounded-lg p-3 border border-emerald-100 text-center">
                  <div className="text-lg font-bold text-emerald-700">{formatCurrency(selectedProgram.total_awarded) || 'N/A'}</div>
                  <div className="text-[10px] text-emerald-600 uppercase font-medium">Total Awarded</div>
                </div>
              </div>

              {/* Description */}
              {selectedProgram.description && (
                <section>
                  <h3 className="text-[13px] font-semibold text-slate-900 mb-2 uppercase tracking-wide">Description</h3>
                  <p className="text-[14px] text-slate-600 leading-relaxed whitespace-pre-wrap">{selectedProgram.description}</p>
                </section>
              )}

              {/* Focus Areas + Eligibility */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {selectedProgram.focus_areas && selectedProgram.focus_areas.length > 0 && (
                  <section>
                    <h3 className="text-[13px] font-semibold text-slate-900 mb-2 uppercase tracking-wide">Technologies & Focus Areas</h3>
                    <div className="flex flex-wrap gap-1.5">
                      {selectedProgram.focus_areas.map((fa: any, i: number) => (
                        <span key={i} className="text-[11px] px-2 py-0.5 rounded bg-pink-50 text-pink-700 border border-pink-200">
                          {typeof fa === 'string' ? fa : fa.name}
                        </span>
                      ))}
                    </div>
                  </section>
                )}
                {(selectedProgram.target_stage || selectedProgram.target_applicant) && (
                  <section>
                    <h3 className="text-[13px] font-semibold text-slate-900 mb-2 uppercase tracking-wide">Eligibility</h3>
                    <div className="space-y-2 text-[13px]">
                      {selectedProgram.target_stage && (
                        <div><span className="font-medium text-slate-700">Stage:</span> <span className="text-slate-600">{selectedProgram.target_stage}</span></div>
                      )}
                      {selectedProgram.target_applicant && (
                        <div><span className="font-medium text-slate-700">Target:</span> <span className="text-slate-600">{selectedProgram.target_applicant}</span></div>
                      )}
                    </div>
                  </section>
                )}
              </div>

              {/* Opportunities List */}
              <section>
                <h3 className="text-[13px] font-semibold text-slate-900 mb-3 uppercase tracking-wide flex items-center gap-2">
                  <FileSearch size={14} className="text-slate-400" />
                  Funding Opportunities — Current & Historical ({(programOpps || []).length})
                </h3>
                {oppsLoading ? (
                  <div className="flex justify-center py-8"><Loader2 className="animate-spin text-slate-300" size={20} /></div>
                ) : !programOpps || programOpps.length === 0 ? (
                  <div className="text-center py-6 text-[12px] text-slate-400 bg-slate-50 rounded-lg border border-slate-100">
                    No opportunities found for this program.
                  </div>
                ) : (
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {programOpps.map((opp: any) => (
                      <Link
                        key={opp.id}
                        to={`/opportunities`}
                        onClick={() => setSelectedProgram(null)}
                        className="flex items-start gap-3 p-3 bg-white border border-slate-200 rounded-lg hover:border-indigo-300 hover:bg-indigo-50/30 transition-colors group block"
                      >
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1 flex-wrap">
                            <span className={clsx('px-1.5 py-0.5 rounded text-[10px] font-medium border',
                              opp.status === 'open' ? 'bg-green-50 text-green-700 border-green-200' :
                              opp.status === 'closed' ? 'bg-red-50 text-red-700 border-red-200' :
                              'bg-slate-50 text-slate-600 border-slate-200'
                            )}>
                              {opp.status || 'Unknown'}
                            </span>
                            {opp.year && <span className="text-[10px] text-slate-500">{opp.year}</span>}
                            {opp.solicitation_number && <span className="text-[10px] font-mono text-slate-400">{opp.solicitation_number}</span>}
                          </div>
                          <h4 className="text-[13px] font-medium text-slate-800 group-hover:text-indigo-700 truncate">{opp.name}</h4>
                          <div className="flex items-center gap-3 mt-1.5 text-[11px] text-slate-500">
                            {opp.total_funding ? (
                              <span className="flex items-center gap-0.5"><DollarSign size={10} />{formatCurrency(opp.total_funding)}</span>
                            ) : null}
                            {opp.award_count > 0 && (
                              <span className="flex items-center gap-0.5"><Trophy size={10} className="text-amber-500" />{opp.award_count} awards</span>
                            )}
                            {opp.total_awarded > 0 && (
                              <span className="text-emerald-600 font-medium">{formatCurrency(opp.total_awarded)} awarded</span>
                            )}
                            {opp.funding_type && (
                              <span className="capitalize">{opp.funding_type}</span>
                            )}
                          </div>
                        </div>
                        <ExternalLink size={14} className="text-slate-300 group-hover:text-indigo-400 shrink-0 mt-1" />
                      </Link>
                    ))}
                  </div>
                )}
              </section>

              {/* Source */}
              {(selectedProgram.url || selectedProgram.contact_email) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {selectedProgram.contact_email && (
                    <section>
                      <h3 className="text-[13px] font-semibold text-slate-900 mb-2 uppercase tracking-wide">Contact</h3>
                      <a href={`mailto:${selectedProgram.contact_email}`} className="text-[13px] text-indigo-600 hover:underline">
                        {selectedProgram.contact_email}
                      </a>
                    </section>
                  )}
                  {selectedProgram.url && (
                    <section>
                      <h3 className="text-[13px] font-semibold text-slate-900 mb-2 uppercase tracking-wide flex items-center gap-1.5">
                        <ShieldCheck size={14} className="text-slate-400" /> Source
                      </h3>
                      <a href={selectedProgram.url} target="_blank" rel="noopener noreferrer" className="text-[13px] text-indigo-600 hover:underline flex items-center gap-1.5">
                        <ExternalLink size={12} /> Official Program Page
                      </a>
                    </section>
                  )}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="px-6 py-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between">
              <button 
                onClick={() => setSelectedProgram(null)}
                className="px-4 py-2 text-[13px] font-medium text-slate-700 bg-white border border-slate-300 rounded-md shadow-sm hover:bg-slate-50"
              >
                Close
              </button>
              <Link 
                to={`/opportunities?agency=${encodeURIComponent(currentOrg.name)}`}
                onClick={() => setSelectedProgram(null)}
                className="flex items-center gap-1.5 px-4 py-2 text-[13px] font-medium text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-md hover:bg-indigo-100 transition-colors"
              >
                <FileSearch size={14} />
                All {currentOrg.name} Opportunities
              </Link>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}
