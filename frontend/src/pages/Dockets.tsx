import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  Scale, FileText, Building2, Zap, Search, ExternalLink,
  ShieldCheck, AlertTriangle, TrendingUp, Clock, ChevronRight,
  Filter, Sparkles, Layers, Activity, CheckCircle2, Calendar,
  ArrowUpRight, X, Grid, List, Compass, Info, FileSpreadsheet
} from 'lucide-react';
import { api, RegulatoryProceeding, ProceedingDossier, ProceedingMacroStats } from '../api/client';
import clsx from 'clsx';

const TOPIC_LABELS: Record<string, { label: string; color: string }> = {
  large_load_interconnection: {
    label: 'Large Load & AI Data Centers',
    color: 'bg-purple-50 text-purple-700 border-purple-200'
  },
  storage_procurement: {
    label: 'Storage & LDES Mandates',
    color: 'bg-cyan-50 text-cyan-700 border-cyan-200'
  },
  thermal_networks: {
    label: 'Utility Thermal Networks (TENs)',
    color: 'bg-emerald-50 text-emerald-700 border-emerald-200'
  },
  interconnection_reform: {
    label: 'Interconnection Reform & Queue',
    color: 'bg-blue-50 text-blue-700 border-blue-200'
  },
  vpp_rate_design: {
    label: 'VPP & Dynamic Rate Design',
    color: 'bg-amber-50 text-amber-700 border-amber-200'
  },
  transmission_planning: {
    label: '20-Yr Regional Transmission',
    color: 'bg-indigo-50 text-indigo-700 border-indigo-200'
  },
  clean_firm_procurement: {
    label: 'Clean Firm & Geothermal',
    color: 'bg-teal-50 text-teal-700 border-teal-200'
  }
};

const COMMISSION_BADGES: Record<string, string> = {
  NYPSC: 'bg-blue-500/10 text-blue-800 border-blue-200',
  CPUC: 'bg-orange-500/10 text-orange-800 border-orange-200',
  PUCT: 'bg-red-500/10 text-red-800 border-red-200',
  FERC: 'bg-emerald-500/10 text-emerald-800 border-emerald-200',
  'FERC / PJM': 'bg-teal-500/10 text-teal-800 border-teal-200',
  'Mass DPU': 'bg-indigo-500/10 text-indigo-800 border-indigo-200',
  ICC: 'bg-purple-500/10 text-purple-800 border-purple-200'
};

const STATUS_BADGES: Record<string, { label: string; color: string }> = {
  active: { label: 'Active Proceeding', color: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  public_comment: { label: 'Public Comment Open', color: 'bg-amber-50 text-amber-700 border-amber-200' },
  staff_whitepaper: { label: 'Staff Whitepaper Issued', color: 'bg-cyan-50 text-cyan-700 border-cyan-200' },
  order_issued: { label: 'Commission Order Issued', color: 'bg-blue-50 text-blue-700 border-blue-200' },
  implementation: { label: 'Utility Implementation', color: 'bg-purple-50 text-purple-700 border-purple-200' }
};

export default function Dockets() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCommission, setSelectedCommission] = useState<string>('all');
  const [selectedTopic, setSelectedTopic] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'cards' | 'table'>('cards');
  const [selectedProceedingId, setSelectedProceedingId] = useState<string | null>(null);

  // 1. Fetch Stats
  const { data: stats } = useQuery<ProceedingMacroStats>({
    queryKey: ['proceeding-stats'],
    queryFn: () => api.getProceedingStats(),
    staleTime: 10 * 60 * 1000
  });

  // 2. Fetch Proceedings List
  const { data: proceedingsData, isLoading } = useQuery({
    queryKey: ['regulatory-proceedings', selectedCommission, selectedTopic, selectedStatus, searchQuery],
    queryFn: () => api.getRegulatoryProceedings({
      commission: selectedCommission !== 'all' ? selectedCommission : undefined,
      topic_category: selectedTopic !== 'all' ? selectedTopic : undefined,
      status: selectedStatus !== 'all' ? selectedStatus : undefined,
      search: searchQuery || undefined,
      limit: 100
    }),
    staleTime: 5 * 60 * 1000
  });

  // 3. Fetch Selected Proceeding Detail (for drawer)
  const { data: selectedDossier, isLoading: isLoadingDossier } = useQuery<ProceedingDossier>({
    queryKey: ['proceeding-detail', selectedProceedingId],
    queryFn: () => api.getRegulatoryProceedingDetail(selectedProceedingId!),
    enabled: Boolean(selectedProceedingId),
    staleTime: 5 * 60 * 1000
  });

  const proceedings = proceedingsData?.proceedings || [];

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Standard Page Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 shadow-2xs">
              <Scale size={12} className="text-indigo-600" />
              <span>Regulatory Reference</span>
            </span>
            <span className="text-xs text-slate-300">|</span>
            <span className="text-xs font-semibold text-slate-500 font-mono">NYPSC · CPUC · PUCT · FERC · Mass DPU · ICC</span>
            <span className="text-xs text-slate-300">|</span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 shadow-2xs">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span>Active Proceedings &amp; Orders</span>
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2.5">
            Regulatory Reference &amp; Energy Dockets
          </h1>
          <p className="text-[13px] sm:text-sm text-slate-500 max-w-3xl mt-1 leading-relaxed">
            Public Utility Commission orders, active interconnection dockets, large load &amp; AI data center inquiries, Virtual Power Plant rate reforms, and utility filings shaping energy innovation commercialization.
          </p>
        </div>
      </div>

      {/* Stats KPI Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs">
          <span className="text-[11px] uppercase font-bold text-slate-400 block tracking-wider">Tracked Dockets</span>
          <span className="text-2xl font-bold text-slate-900 font-mono mt-0.5 block">{stats?.total_proceedings || 15}</span>
          <span className="text-[11px] text-slate-500 mt-0.5 block">Active State &amp; Federal Dockets</span>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs">
          <span className="text-[11px] uppercase font-bold text-slate-400 block tracking-wider">Commissions</span>
          <span className="text-2xl font-bold text-slate-900 font-mono mt-0.5 block">{stats?.active_commissions_count || 7}</span>
          <span className="text-[11px] text-slate-500 mt-0.5 block">NYPSC, CPUC, PUCT, FERC, Mass DPU, ICC</span>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs">
          <span className="text-[11px] uppercase font-bold text-slate-400 block tracking-wider">Tech Linkages</span>
          <span className="text-2xl font-bold text-slate-900 font-mono mt-0.5 block">{stats?.total_technology_linkages || 45}</span>
          <span className="text-[11px] text-slate-500 mt-0.5 block">Direct clean tech cross-references</span>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs">
          <span className="text-[11px] uppercase font-bold text-slate-400 block tracking-wider">Utility Linkages</span>
          <span className="text-2xl font-bold text-slate-900 font-mono mt-0.5 block">{stats?.total_organization_linkages || 12}</span>
          <span className="text-[11px] text-slate-500 mt-0.5 block">Regulated IOU &amp; POU filings</span>
        </div>
      </div>

      {/* ── FILTER & SEARCH TOOLBAR ────────────────────────────────────────── */}
      <div className="w-full flex flex-col gap-4">
        <div className="bg-white rounded-2xl border border-slate-200/90 p-4 shadow-2xs flex flex-col md:flex-row gap-4 items-center justify-between">
          {/* Search Bar */}
          <div className="relative flex-1 w-full">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search docket number, case title, commission, large loads, data centers, tariffs..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-hidden focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500 transition-all font-medium"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-1"
              >
                <X size={14} />
              </button>
            )}
          </div>

          {/* View Mode Toggle & Result Count */}
          <div className="flex items-center gap-3 shrink-0 w-full md:w-auto justify-between md:justify-end">
            <span className="text-xs font-semibold text-slate-500">
              Showing <span className="text-slate-900 font-bold">{proceedings.length}</span> Dockets
            </span>

            <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200">
              <button
                type="button"
                onClick={() => setViewMode('cards')}
                className={`p-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                  viewMode === 'cards' ? 'bg-white text-cyan-700 shadow-2xs' : 'text-slate-500 hover:text-slate-800'
                }`}
                title="Card View"
              >
                <Grid size={15} />
                <span className="hidden sm:inline">Cards</span>
              </button>
              <button
                type="button"
                onClick={() => setViewMode('table')}
                className={`p-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                  viewMode === 'table' ? 'bg-white text-cyan-700 shadow-2xs' : 'text-slate-500 hover:text-slate-800'
                }`}
                title="Table View"
              >
                <List size={15} />
                <span className="hidden sm:inline">Table</span>
              </button>
            </div>
          </div>
        </div>

        {/* Multi-Attribute Filter Chips */}
        <div className="flex flex-col gap-2.5">
          {/* Commission Filter */}
          <div className="flex items-center gap-2 overflow-x-auto no-scrollbar pb-1">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 shrink-0 flex items-center gap-1">
              <Building2 size={12} className="text-cyan-600" /> Commission:
            </span>
            {[
              { id: 'all', label: 'All Commissions' },
              { id: 'NYPSC', label: 'NY PSC (New York)' },
              { id: 'CPUC', label: 'CPUC (California)' },
              { id: 'PUCT', label: 'PUCT (Texas / ERCOT)' },
              { id: 'FERC', label: 'FERC (Federal)' },
              { id: 'Mass DPU', label: 'Mass DPU (Massachusetts)' },
              { id: 'ICC', label: 'ICC (Illinois)' }
            ].map(com => (
              <button
                key={com.id}
                onClick={() => setSelectedCommission(com.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all shrink-0 cursor-pointer ${
                  selectedCommission === com.id
                    ? 'bg-slate-900 text-white shadow-xs'
                    : 'bg-white text-slate-600 border border-slate-200/80 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                {com.label}
              </button>
            ))}
          </div>

          {/* Topic Category Filter */}
          <div className="flex items-center gap-2 overflow-x-auto no-scrollbar pb-1">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 shrink-0 flex items-center gap-1">
              <Zap size={12} className="text-purple-600" /> Topic Area:
            </span>
            {[
              { id: 'all', label: 'All Topics' },
              { id: 'large_load_interconnection', label: 'Large Loads & AI Data Centers' },
              { id: 'storage_procurement', label: 'Energy Storage (6 GW Roadmap)' },
              { id: 'thermal_networks', label: 'Utility Thermal Networks (TENs)' },
              { id: 'interconnection_reform', label: 'Interconnection & Queue Reform' },
              { id: 'vpp_rate_design', label: 'VPPs & Demand Flexibility' },
              { id: 'clean_firm_procurement', label: 'Clean Firm & Geothermal' },
              { id: 'transmission_planning', label: '20-Year Transmission' }
            ].map(top => (
              <button
                key={top.id}
                onClick={() => setSelectedTopic(top.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all shrink-0 cursor-pointer ${
                  selectedTopic === top.id
                    ? 'bg-cyan-700 text-white shadow-xs'
                    : 'bg-white text-slate-600 border border-slate-200/80 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                {top.label}
              </button>
            ))}
          </div>
        </div>

        {/* ── PROCEEDINGS CONTENT ────────────────────────────────────────── */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 py-8">
            {[1, 2, 3, 4].map(n => (
              <div key={n} className="h-48 rounded-2xl bg-slate-100 animate-pulse border border-slate-200" />
            ))}
          </div>
        ) : proceedings.length === 0 ? (
          <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center my-6">
            <Scale size={40} className="mx-auto text-slate-300 mb-3" />
            <h3 className="text-base font-bold text-slate-800">No regulatory proceedings match your criteria</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
              Try adjusting your commission, topic, or search term to discover active public utility commission dockets.
            </p>
            <button
              onClick={() => {
                setSearchQuery('');
                setSelectedCommission('all');
                setSelectedTopic('all');
                setSelectedStatus('all');
              }}
              className="mt-4 px-4 py-2 rounded-xl bg-cyan-50 text-cyan-800 text-xs font-bold hover:bg-cyan-100 transition-colors"
            >
              Reset All Filters
            </button>
          </div>
        ) : viewMode === 'cards' ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {proceedings.map((proc) => {
              const topicMeta = TOPIC_LABELS[proc.topic_category] || { label: proc.topic_category, color: 'bg-slate-50 text-slate-700 border-slate-200' };
              const statusMeta = STATUS_BADGES[proc.status] || { label: proc.status, color: 'bg-slate-50 text-slate-700 border-slate-200' };
              const comBadgeColor = COMMISSION_BADGES[proc.commission] || 'bg-slate-100 text-slate-700 border-slate-200';

              return (
                <div
                  key={proc.id}
                  onClick={() => setSelectedProceedingId(proc.id)}
                  className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-2xs hover:shadow-md hover:border-cyan-500/50 transition-all cursor-pointer flex flex-col justify-between group relative overflow-hidden"
                >
                  <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-500 opacity-0 group-hover:opacity-100 transition-opacity" />

                  <div>
                    {/* Header Badges */}
                    <div className="flex items-center justify-between gap-2 flex-wrap mb-3">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className={`px-2.5 py-0.5 rounded-lg text-[10px] font-black font-mono border uppercase tracking-wider ${comBadgeColor}`}>
                          {proc.commission}
                        </span>
                        <span className="text-xs font-mono font-bold text-slate-800 bg-slate-100 px-2 py-0.5 rounded-md border border-slate-200">
                          {proc.docket_number}
                        </span>
                        <span className={`px-2.5 py-0.5 rounded-lg text-[10px] font-bold border ${topicMeta.color}`}>
                          {topicMeta.label}
                        </span>
                      </div>
                      <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold border ${statusMeta.color}`}>
                        {statusMeta.label}
                      </span>
                    </div>

                    {/* Title */}
                    <h3 className="text-sm sm:text-base font-extrabold text-slate-900 group-hover:text-cyan-700 transition-colors leading-snug">
                      {proc.short_title || proc.title}
                    </h3>

                    {/* Executive Summary */}
                    <p className="text-xs text-slate-600 mt-2 line-clamp-3 leading-relaxed">
                      {proc.executive_summary}
                    </p>

                    {/* Innovation Impact Highlight */}
                    <div className="mt-3.5 p-3 rounded-xl bg-cyan-50/50 border border-cyan-100 text-xs">
                      <span className="font-bold text-cyan-900 block text-[11px] uppercase tracking-wider mb-1 flex items-center gap-1.5">
                        <Sparkles size={12} className="text-cyan-600" />
                        Why This Matters for Clean Tech Innovation:
                      </span>
                      <p className="text-slate-700 text-[11.5px] line-clamp-2 leading-relaxed">
                        {proc.innovation_impact}
                      </p>
                    </div>
                  </div>

                  {/* Card Footer */}
                  <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                    <div className="flex items-center gap-3">
                      {proc.linked_technologies_count !== undefined && (
                        <span className="flex items-center gap-1 text-[11px] font-medium text-slate-600">
                          <Zap size={13} className="text-purple-600" />
                          <strong className="text-slate-900">{proc.linked_technologies_count}</strong> Linked Techs
                        </span>
                      )}
                      {proc.jurisdiction_state && (
                        <span className="text-[11px] font-mono text-slate-400">
                          State: <strong className="text-slate-700">{proc.jurisdiction_state}</strong>
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-1 text-cyan-700 font-bold group-hover:translate-x-0.5 transition-transform text-xs">
                      <span>View Dossier</span>
                      <ChevronRight size={14} />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          /* Tabular View */
          <div className="bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200 text-[11px] uppercase font-bold text-slate-500 tracking-wider">
                    <th className="py-3 px-4">Commission & Docket</th>
                    <th className="py-3 px-4">Proceeding Name</th>
                    <th className="py-3 px-4">Topic Area</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4">Impacted Technologies</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                  {proceedings.map((proc) => {
                    const topicMeta = TOPIC_LABELS[proc.topic_category] || { label: proc.topic_category, color: 'bg-slate-50 text-slate-700 border-slate-200' };
                    const statusMeta = STATUS_BADGES[proc.status] || { label: proc.status, color: 'bg-slate-50 text-slate-700 border-slate-200' };

                    return (
                      <tr
                        key={proc.id}
                        onClick={() => setSelectedProceedingId(proc.id)}
                        className="hover:bg-cyan-50/40 cursor-pointer transition-colors"
                      >
                        <td className="py-3 px-4 whitespace-nowrap">
                          <span className="font-extrabold text-slate-900 block font-mono">{proc.docket_number}</span>
                          <span className="text-[10px] text-slate-500 font-bold uppercase">{proc.commission} ({proc.jurisdiction_state || 'US'})</span>
                        </td>
                        <td className="py-3 px-4">
                          <span className="font-bold text-slate-900 hover:text-cyan-700 block line-clamp-1">
                            {proc.short_title || proc.title}
                          </span>
                          <span className="text-[11px] text-slate-500 line-clamp-1">{proc.executive_summary}</span>
                        </td>
                        <td className="py-3 px-4 whitespace-nowrap">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${topicMeta.color}`}>
                            {topicMeta.label}
                          </span>
                        </td>
                        <td className="py-3 px-4 whitespace-nowrap">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${statusMeta.color}`}>
                            {statusMeta.label}
                          </span>
                        </td>
                        <td className="py-3 px-4 whitespace-nowrap">
                          <span className="font-bold text-slate-800 font-mono">
                            {proc.linked_technologies_count || 0} Tech Verticals
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right whitespace-nowrap">
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedProceedingId(proc.id);
                            }}
                            className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-cyan-100 text-slate-800 hover:text-cyan-900 font-bold text-xs transition-colors cursor-pointer"
                          >
                            Details
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* ── SLIDE-OVER DETAIL DRAWER ────────────────────────────────────────── */}
      {selectedProceedingId && (
        <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/60 backdrop-blur-xs flex justify-end animate-fadeIn">
          <div
            className="w-full max-w-2xl bg-white h-full shadow-2xl flex flex-col border-l border-slate-200 overflow-hidden animate-slideInRight"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Drawer Header */}
            <div className="p-6 bg-gradient-to-r from-slate-900 to-[#0c1833] text-white border-b border-slate-800 shrink-0">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 flex-wrap mb-2">
                    <span className="px-2.5 py-0.5 rounded-md text-[10px] font-black uppercase font-mono bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                      {selectedDossier?.commission || 'PUC'}
                    </span>
                    <span className="text-xs font-mono font-bold text-slate-300 bg-white/10 px-2 py-0.5 rounded">
                      {selectedDossier?.docket_number}
                    </span>
                    {selectedDossier?.jurisdiction_state && (
                      <span className="text-xs font-mono text-slate-400">
                        Jurisdiction: {selectedDossier.jurisdiction_state}
                      </span>
                    )}
                  </div>
                  <h2 className="text-lg sm:text-xl font-black text-white leading-snug">
                    {selectedDossier?.short_title || selectedDossier?.title}
                  </h2>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedProceedingId(null)}
                  className="p-2 rounded-xl bg-white/10 hover:bg-white/20 text-slate-300 hover:text-white transition-colors cursor-pointer"
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            {/* Drawer Body Content */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {isLoadingDossier ? (
                <div className="space-y-4 py-8">
                  <div className="h-20 bg-slate-100 rounded-xl animate-pulse" />
                  <div className="h-32 bg-slate-100 rounded-xl animate-pulse" />
                  <div className="h-32 bg-slate-100 rounded-xl animate-pulse" />
                </div>
              ) : selectedDossier ? (
                <>
                  {/* Full Official Title */}
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Official Proceeding Caption</span>
                    <p className="text-xs font-semibold text-slate-800 leading-relaxed">
                      {selectedDossier.title}
                    </p>
                  </div>

                  {/* Executive Summary */}
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
                      <FileText size={14} className="text-blue-600" />
                      Executive Docket Summary
                    </h4>
                    <p className="text-xs text-slate-700 leading-relaxed whitespace-pre-line bg-white p-4 rounded-xl border border-slate-200/90 shadow-2xs">
                      {selectedDossier.executive_summary}
                    </p>
                  </div>

                  {/* Innovation Impact Synthesis */}
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
                      <Sparkles size={14} className="text-cyan-600" />
                      Implications for Energy Startups & Clean Tech
                    </h4>
                    <div className="p-4 rounded-xl bg-cyan-50/60 border border-cyan-200/80 text-xs text-slate-800 leading-relaxed shadow-2xs">
                      {selectedDossier.innovation_impact}
                    </div>
                  </div>

                  {/* Tailwinds vs Friction Points Grid */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl bg-emerald-50/50 border border-emerald-200 text-xs">
                      <span className="font-bold text-emerald-900 block text-[11px] uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                        <TrendingUp size={13} className="text-emerald-600" />
                        Commercial Tailwinds
                      </span>
                      <p className="text-slate-700 text-xs leading-relaxed">
                        {selectedDossier.commercial_tailwinds || 'Expands market access and establishes statutory procurement basis.'}
                      </p>
                    </div>

                    <div className="p-4 rounded-xl bg-amber-50/50 border border-amber-200 text-xs">
                      <span className="font-bold text-amber-900 block text-[11px] uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                        <AlertTriangle size={13} className="text-amber-600" />
                        Risks & Friction Points
                      </span>
                      <p className="text-slate-700 text-xs leading-relaxed">
                        {selectedDossier.commercial_friction_points || 'Study deposits, interconnection queue backlogs, and utility tariff adjustments.'}
                      </p>
                    </div>
                  </div>

                  {/* Impacted Technologies Links */}
                  {selectedDossier.linked_technologies && selectedDossier.linked_technologies.length > 0 && (
                    <div>
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2.5 flex items-center gap-1.5">
                        <Zap size={14} className="text-purple-600" />
                        Impacted Clean Technologies ({selectedDossier.linked_technologies.length})
                      </h4>
                      <div className="space-y-2.5">
                        {selectedDossier.linked_technologies.map((tlink, idx) => (
                          <div
                            key={idx}
                            className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-col gap-1.5 hover:bg-slate-100/80 transition-colors"
                          >
                            <div className="flex items-center justify-between">
                              <Link
                                to={`/technologies/${tlink.technology_id}`}
                                className="text-xs font-extrabold text-slate-900 hover:text-cyan-700 flex items-center gap-1"
                              >
                                {tlink.technology_name}
                                <ArrowUpRight size={13} className="text-cyan-600" />
                              </Link>
                              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-purple-100 text-purple-800 uppercase">
                                {tlink.impact_level.replace('_', ' ')}
                              </span>
                            </div>
                            {tlink.impact_summary && (
                              <p className="text-[11.5px] text-slate-600 leading-relaxed">
                                {tlink.impact_summary}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Affected Utilities & Organizations */}
                  {selectedDossier.linked_organizations && selectedDossier.linked_organizations.length > 0 && (
                    <div>
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
                        <Building2 size={14} className="text-slate-600" />
                        Regulated Utilities & Intervenors
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedDossier.linked_organizations.map((org, idx) => (
                          <span
                            key={idx}
                            className="px-3 py-1.5 rounded-lg bg-slate-100 border border-slate-200 text-xs font-semibold text-slate-800"
                          >
                            {org.organization_name}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Key Filings Summary */}
                  {selectedDossier.key_filings_summary && (
                    <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs">
                      <span className="font-bold text-slate-800 block text-[11px] uppercase tracking-wider mb-1">
                        Key Intervenor & Staff Filings
                      </span>
                      <p className="text-slate-600 leading-relaxed">
                        {selectedDossier.key_filings_summary}
                      </p>
                    </div>
                  )}
                </>
              ) : null}
            </div>

            {/* Drawer Footer with Official Docket Link */}
            {selectedDossier?.official_docket_url && (
              <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between shrink-0">
                <span className="text-[11px] text-slate-500 font-medium">
                  Authoritative State & Federal Docket Record
                </span>
                <a
                  href={selectedDossier.official_docket_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-cyan-700 text-white text-xs font-bold transition-colors flex items-center gap-1.5 shadow-xs"
                >
                  <span>Open Official Docket</span>
                  <ExternalLink size={13} />
                </a>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
