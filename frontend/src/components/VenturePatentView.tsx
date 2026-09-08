import React, { useState, useMemo, useRef, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  api,
  AttributionRecipientItem,
  RecipientAttributionDossier,
  AttributionsGraphResponse,
  AttributionsGraphNode
} from '../api/client';
import {
  Sparkles, Trophy, Building2, Lightbulb, TrendingUp, ExternalLink,
  Search, Filter, ChevronRight, X, ArrowUpRight, ShieldCheck,
  Zap, Compass, Layers, GitFork, Users, Network, DollarSign, Award,
  ArrowUpDown, ZoomIn, ZoomOut, RefreshCw, Maximize2, Minimize2,
  Download, Eye, EyeOff, Info, Check, Sliders
} from 'lucide-react';
import clsx from 'clsx';
import { saveAs } from 'file-saver';
import { OrgLogo } from './OrgLogo';
import { InteractiveEgoGraph } from './InteractiveEgoGraph';
import { ProvenanceRibbon } from './ProvenanceRibbon';
import { LineageMatrixExplorer } from './LineageMatrixExplorer';

function formatCurrency(val: number | null | undefined): string {
  if (!val) return '$0';
  if (val >= 1_000_000_000) return `$${(val / 1_000_000_000).toFixed(2)}B`;
  if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(1)}M`;
  if (val >= 1_000) return `$${(val / 1_000).toFixed(0)}K`;
  return `$${val.toFixed(0)}`;
}

export function VenturePatentView() {
  const [subTab, setSubTab] = useState<'table' | 'graph' | 'syndicates' | 'matrix' | 'sec-filings'>('table');
  const [search, setSearch] = useState('');
  const [techFilter, setTechFilter] = useState('ALL');
  const [sortBy, setSortBy] = useState('leverage_ratio');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const [selectedRecipientId, setSelectedRecipientId] = useState<number | null>(null);

  // Fetch overview stats
  const { data: overview, isLoading: overviewLoading } = useQuery({
    queryKey: ['attributions-overview'],
    queryFn: () => api.getAttributionsOverview(),
  });

  // Fetch recipients list
  const { data: recData, isLoading: recsLoading } = useQuery({
    queryKey: ['attributions-recipients', techFilter, search, sortBy, sortDir],
    queryFn: () => api.getAttributionRecipients({
      technology_area: techFilter !== 'ALL' ? techFilter : undefined,
      search: search || undefined,
      sort_by: sortBy,
      sort_dir: sortDir,
      page_size: 50
    }),
  });

  // Fetch graph data
  const { data: graphData, isLoading: graphLoading } = useQuery({
    queryKey: ['attributions-graph'],
    queryFn: () => api.getAttributionsGraph(),
    enabled: subTab === 'graph',
  });

  // Fetch syndicates data
  const { data: syndicatesData, isLoading: syndLoading } = useQuery({
    queryKey: ['attributions-syndicates'],
    queryFn: () => api.getAttributionSyndicates(),
    enabled: subTab === 'syndicates',
  });

  // Fetch SEC Form D Filings
  const { data: secData, isLoading: secLoading } = useQuery({
    queryKey: ['sec-form-d-filings', search],
    queryFn: () => api.getSecFormDFilings({
      search: search || undefined,
      page_size: 50,
    }),
    enabled: subTab === 'sec-filings',
  });

  // Fetch individual company dossier
  const { data: dossier, isLoading: dossierLoading } = useQuery({
    queryKey: ['attributions-dossier', selectedRecipientId],
    queryFn: () => api.getRecipientAttributionDossier(selectedRecipientId!),
    enabled: !!selectedRecipientId,
  });

  // Fetch individual company capital continuum ledger
  const { data: continuum } = useQuery({
    queryKey: ['recipient-capital-continuum', selectedRecipientId],
    queryFn: () => api.getRecipientCapitalContinuum(selectedRecipientId!),
    enabled: !!selectedRecipientId,
  });

  const recipients = recData?.items || [];

  return (
    <div className="space-y-6">
      {/* Overview Stat Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Bayh-Dole Patents</span>
            <span className="p-1.5 rounded-lg bg-amber-50 text-amber-600 border border-amber-200">
              <Lightbulb size={16} />
            </span>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-slate-900">
              {overview?.total_patents ? overview.total_patents.toLocaleString() : '0'}
            </span>
            <span className="text-xs font-medium text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded">
              USPTO Assigned
            </span>
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">Directly citing public grant awards</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Follow-On VC Raised</span>
            <span className="p-1.5 rounded-lg bg-emerald-50 text-emerald-600 border border-emerald-200">
              <TrendingUp size={16} />
            </span>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-slate-900">
              {formatCurrency(overview?.total_vc_raised_usd)}
            </span>
            <span className="text-xs font-medium text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded">
              Private Capital
            </span>
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">Across Series Seed through Growth equity</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Catalytic Leverage</span>
            <span className="p-1.5 rounded-lg bg-indigo-50 text-indigo-600 border border-indigo-200">
              <Sparkles size={16} />
            </span>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-indigo-600">
              {overview?.leverage_multiplier ? `${overview.leverage_multiplier.toFixed(1)}x` : '0x'}
            </span>
            <span className="text-xs font-medium text-indigo-700 bg-indigo-50 px-1.5 py-0.5 rounded">
              VC / Grant $
            </span>
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">Private capital per $1 of public grant funding</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-semibold uppercase tracking-wider">Commercial Pioneers</span>
            <span className="p-1.5 rounded-lg bg-sky-50 text-sky-600 border border-sky-200">
              <ShieldCheck size={16} />
            </span>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-slate-900">
              {overview?.total_backed_companies ? overview.total_backed_companies.toLocaleString() : '0'}
            </span>
            <span className="text-xs font-medium text-sky-700 bg-sky-50 px-1.5 py-0.5 rounded">
              Enterprises
            </span>
          </div>
          <div className="text-[11px] text-slate-500 mt-0.5">Scale-ups with grant + IP + VC backing</div>
        </div>
      </div>

      {/* Sub-view Switcher & Filters */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-3 rounded-xl border border-slate-200 shadow-2xs">
        <div className="flex items-center bg-slate-100 p-1 rounded-lg border border-slate-200 flex-wrap gap-1">
          <button
            onClick={() => setSubTab('table')}
            className={clsx(
              'flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-md transition-all',
              subTab === 'table' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
            )}
          >
            <span>📋 Venture & Patent Table</span>
          </button>

          <button
            onClick={() => setSubTab('matrix')}
            className={clsx(
              'flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-md transition-all',
              subTab === 'matrix' ? 'bg-white text-indigo-700 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
            )}
          >
            <Sparkles size={13} />
            <span>🧬 9-D Innovation Matrix & Trace</span>
          </button>

          <button
            onClick={() => setSubTab('graph')}
            className={clsx(
              'flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-md transition-all',
              subTab === 'graph' ? 'bg-white text-indigo-700 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
            )}
          >
            <Network size={13} />
            <span>🕸️ Lineage Graph</span>
          </button>

          <button
            onClick={() => setSubTab('syndicates')}
            className={clsx(
              'flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-md transition-all',
              subTab === 'syndicates' ? 'bg-white text-emerald-700 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
            )}
          >
            <Users size={13} />
            <span>🏆 Investor Syndicates</span>
          </button>

          <button
            onClick={() => setSubTab('sec-filings')}
            className={clsx(
              'flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-md transition-all',
              subTab === 'sec-filings' ? 'bg-white text-cyan-700 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
            )}
          >
            <DollarSign size={13} />
            <span>📑 SEC Form D Private Offerings</span>
          </button>
        </div>

        {(subTab === 'table' || subTab === 'sec-filings') && (
          <div className="flex items-center gap-2 flex-wrap">
            <div className="relative">
              <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder={subTab === 'sec-filings' ? 'Search CIK, issuer...' : 'Search company, tech...'}
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="pl-7 pr-3 py-1 bg-slate-50 border border-slate-200 rounded-lg text-xs w-48 focus:ring-1 focus:ring-indigo-500 outline-none"
              />
            </div>

            <select
              value={techFilter}
              onChange={e => setTechFilter(e.target.value)}
              className="bg-slate-50 border border-slate-200 rounded-lg px-2 py-1 text-xs text-slate-700 font-medium outline-none"
            >
              <option value="ALL">All Technology Sectors</option>
              <option value="Energy Storage & Advanced Batteries">Energy Storage</option>
              <option value="Industrial Decarbonization & Clean Heat">Industrial Decarb</option>
              <option value="Hydrogen & Clean Fuel Cells">Hydrogen & Fuel Cells</option>
              <option value="Clean Energy Innovation & Advanced Tech">Fusion & Advanced Tech</option>
              <option value="Critical Minerals & Supply Chain">Critical Minerals</option>
              <option value="Solar Photovoltaics & Systems">Solar PV</option>
              <option value="Grid Modernization & Smart Power">Grid Power</option>
            </select>

            <select
              value={sortBy}
              onChange={e => setSortBy(e.target.value)}
              className="bg-slate-50 border border-slate-200 rounded-lg px-2 py-1 text-xs text-slate-700 font-medium outline-none"
            >
              <option value="leverage_ratio">Sort: Leverage Multiplier</option>
              <option value="vc_raised">Sort: Total VC Raised</option>
              <option value="patents">Sort: Patent Count</option>
              <option value="grants">Sort: Grant Capital</option>
            </select>
          </div>
        )}
      </div>

      {/* ───────────────────────────────────────────────────────── */}
      {/* SUB-VIEW 1: VENTURE & PATENT TABLE                        */}
      {/* ───────────────────────────────────────────────────────── */}
      {subTab === 'table' && (
        <div className="bg-white rounded-xl border border-slate-200/90 shadow-2xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50/80 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider text-[10px]">
                  <th className="py-3 px-4">Awardee Organization</th>
                  <th className="py-3 px-3">Primary Clean Tech</th>
                  <th className="py-3 px-3 text-right">Public Grant Total</th>
                  <th className="py-3 px-3 text-right">Follow-On VC Raised</th>
                  <th className="py-3 px-3 text-center">Bayh-Dole Patents</th>
                  <th className="py-3 px-3 text-right">Leverage Multiplier</th>
                  <th className="py-3 px-3">Lead Investors</th>
                  <th className="py-3 px-3 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {recipients.map((r) => (
                  <tr
                    key={r.id}
                    onClick={() => setSelectedRecipientId(r.id)}
                    className={clsx(
                      'hover:bg-indigo-50/40 cursor-pointer transition-colors',
                      selectedRecipientId === r.id && 'bg-indigo-50/70'
                    )}
                  >
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2.5">
                        <OrgLogo org={r.name} size="sm" />
                        <div>
                          <div className="font-bold text-slate-900 text-[12.5px]">{r.name}</div>
                          <div className="text-[10.5px] text-slate-500 flex items-center gap-1.5 mt-0.5">
                            <span className="capitalize">{r.recipient_type || 'Company'}</span>
                            {r.state && <span>· {r.state}</span>}
                            {r.latest_round && (
                              <span className="px-1.5 py-0.2 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold text-[9px]">
                                {r.latest_round}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </td>

                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-100 text-slate-700">
                        {r.primary_technology || 'Clean Innovation'}
                      </span>
                    </td>

                    <td className="py-3 px-3 text-right font-mono font-semibold text-slate-700">
                      {formatCurrency(r.total_public_grants_usd)}
                    </td>

                    <td className="py-3 px-3 text-right font-mono font-bold text-emerald-700">
                      {formatCurrency(r.total_vc_raised_usd)}
                    </td>

                    <td className="py-3 px-3 text-center">
                      {r.patent_count > 0 ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-amber-50 text-amber-800 font-bold text-[11px] border border-amber-200">
                          <Lightbulb size={11} className="text-amber-600" />
                          <span>{r.patent_count} USPTO</span>
                        </span>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>

                    <td className="py-3 px-3 text-right">
                      <span className="font-mono font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200 text-[11px]">
                        {r.leverage_ratio}x
                      </span>
                    </td>

                    <td className="py-3 px-3">
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {r.lead_investors.slice(0, 2).map((inv, idx) => (
                          <span key={idx} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-medium flex items-center gap-1">
                            <OrgLogo org={inv} size="xs" />
                            <span>{inv}</span>
                          </span>
                        ))}
                        {r.lead_investors.length > 2 && (
                          <span className="text-[9.5px] text-slate-400 font-medium">+{r.lead_investors.length - 2}</span>
                        )}
                      </div>
                    </td>

                    <td className="py-3 px-3 text-center">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedRecipientId(r.id);
                        }}
                        className="inline-flex items-center gap-1 text-[11px] font-bold text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 px-2.5 py-1 rounded-md transition-colors"
                      >
                        <Network size={11} />
                        <span>Ego Graph</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────── */}
      {/* SUB-VIEW 2: FULLY INTERACTIVE & CUSTOMIZABLE GRAPH STUDIO */}
      {/* ───────────────────────────────────────────────────────── */}
      {subTab === 'graph' && (
        <InteractiveGraphStudio
          graphData={graphData}
          onSelectCompany={(name) => {
            const found = recipients.find(r => r.name.toLowerCase() === name.toLowerCase());
            if (found) setSelectedRecipientId(found.id);
          }}
        />
      )}

      {/* ───────────────────────────────────────────────────────── */}
      {/* SUB-VIEW 3: INVESTOR SYNDICATE LEADERBOARD                */}
      {/* ───────────────────────────────────────────────────────── */}
      {subTab === 'syndicates' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {syndicatesData?.syndicates.map((s, idx) => (
            <div key={idx} className="bg-white rounded-xl border border-slate-200 p-4 shadow-2xs flex flex-col justify-between hover:border-indigo-300 transition-all">
              <div className="space-y-2">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <OrgLogo org={s.name} size="sm" />
                    <div className="font-bold text-sm text-slate-900">{s.name}</div>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 font-mono font-bold text-xs border border-emerald-200">
                    {formatCurrency(s.total_capital_deployed_usd)}
                  </span>
                </div>

                <div className="text-[11px] text-slate-500">
                  <span className="font-semibold text-slate-700">{s.rounds_count}</span> rounds led in grant-backed clean tech
                </div>

                <div className="pt-2 border-t border-slate-100">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">Portfolio Companies</div>
                  <div className="flex flex-wrap gap-1">
                    {s.portfolio_companies.map((co, cidx) => (
                      <span key={cidx} className="px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 font-medium text-[10.5px] flex items-center gap-1">
                        <OrgLogo org={co} size="xs" />
                        <span>{co}</span>
                      </span>
                    ))}
                  </div>
                </div>

                {s.co_investors.length > 0 && (
                  <div className="pt-2">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">Syndicate Co-Investors</div>
                    <div className="flex flex-wrap gap-1">
                      {s.co_investors.map((co, cidx) => (
                        <span key={cidx} className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 text-[10px] flex items-center gap-1">
                          <OrgLogo org={co} size="xs" />
                          <span>{co}</span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ───────────────────────────────────────────────────────── */}
      {/* SUB-VIEW 4: 9-D INNOVATION MATRIX & TRACE EXPLORER         */}
      {/* ───────────────────────────────────────────────────────── */}
      {subTab === 'matrix' && (
        <LineageMatrixExplorer />
      )}

      {/* ───────────────────────────────────────────────────────── */}
      {/* SUB-VIEW 5: SEC FORM D PRIVATE OFFERINGS & EXEMPTIONS     */}
      {/* ───────────────────────────────────────────────────────── */}
      {subTab === 'sec-filings' && (
        <div className="space-y-4">
          <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-xl p-4 border border-slate-700/80 shadow-md flex flex-wrap items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded-full text-[10.5px] font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                  SEC EDGAR Reg D
                </span>
                <span className="text-xs text-slate-300">Rule 506(b) &amp; 506(c) Private Capital Intelligence</span>
              </div>
              <p className="text-xs text-slate-400">
                Tracked non-public offering notices, private placement sizes, and executive officer signers for venture-scale innovators.
              </p>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-xl font-bold font-mono text-emerald-400">
                  {formatCurrency(secData?.total_capital_raised_usd)}
                </div>
                <div className="text-[11px] text-slate-400">Total Capital Sold</div>
              </div>
              <div className="text-right pl-4 border-l border-slate-700">
                <div className="text-xl font-bold font-mono text-white">
                  {secData?.total || 0}
                </div>
                <div className="text-[11px] text-slate-400">Filings Tracked</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200/90 shadow-2xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-50/80 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider text-[10px]">
                    <th className="py-3 px-4">Issuer / Entity Legal Name</th>
                    <th className="py-3 px-3 font-mono">CIK Number</th>
                    <th className="py-3 px-3">Industry / State</th>
                    <th className="py-3 px-3 text-right">Total Offering</th>
                    <th className="py-3 px-3 text-right">Amount Sold</th>
                    <th className="py-3 px-3 text-center">Investors</th>
                    <th className="py-3 px-3">Executive Officers / Signers</th>
                    <th className="py-3 px-3">Filing Date</th>
                    <th className="py-3 px-3 text-center">SEC EDGAR</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {secData?.items?.map((filing) => (
                    <tr
                      key={filing.id}
                      onClick={() => filing.recipient_id && setSelectedRecipientId(filing.recipient_id)}
                      className={clsx(
                        'hover:bg-cyan-50/40 transition-colors',
                        filing.recipient_id && 'cursor-pointer'
                      )}
                    >
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <OrgLogo org={filing.entity_legal_name} size="xs" />
                          <div>
                            <div className="font-bold text-slate-900 text-[12px]">{filing.entity_legal_name}</div>
                            <div className="text-[10px] text-slate-400 font-mono mt-0.5">Acc: {filing.accession_number}</div>
                          </div>
                        </div>
                      </td>

                      <td className="py-3 px-3 font-mono text-[11px] text-slate-700 font-semibold">
                        {filing.cik_number}
                      </td>

                      <td className="py-3 px-3">
                        <div className="text-slate-800 font-medium text-[11px]">{filing.primary_industry || 'Energy / Tech'}</div>
                        <div className="text-[10px] text-slate-400">{filing.jurisdiction_state || 'US'}</div>
                      </td>

                      <td className="py-3 px-3 text-right font-mono text-slate-700 font-semibold">
                        {formatCurrency(filing.total_offering_amount_usd)}
                      </td>

                      <td className="py-3 px-3 text-right font-mono font-bold text-emerald-700">
                        {formatCurrency(filing.total_amount_sold_usd)}
                      </td>

                      <td className="py-3 px-3 text-center">
                        <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-mono text-[10.5px]">
                          {filing.num_investors ?? '—'}
                        </span>
                      </td>

                      <td className="py-3 px-3">
                        <div className="flex flex-wrap gap-1 max-w-xs">
                          {filing.executive_officers?.slice(0, 2).map((officer, oidx) => (
                            <span key={oidx} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-700">
                              <span className="font-semibold">{officer.name}</span> ({officer.title})
                            </span>
                          ))}
                          {(filing.executive_officers?.length || 0) > 2 && (
                            <span className="text-[9.5px] text-slate-400">+{filing.executive_officers.length - 2}</span>
                          )}
                        </div>
                      </td>

                      <td className="py-3 px-3 text-slate-600 font-mono text-[11px]">
                        {filing.filing_date}
                      </td>

                      <td className="py-3 px-3 text-center">
                        {filing.sec_html_url ? (
                          <a
                            href={filing.sec_html_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="inline-flex items-center gap-1 text-[11px] text-cyan-700 hover:text-cyan-900 font-bold bg-cyan-50 hover:bg-cyan-100 px-2 py-1 rounded transition-colors"
                          >
                            <span>EDGAR</span>
                            <ExternalLink size={10} />
                          </a>
                        ) : (
                          <span className="text-slate-400">—</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────── */}
      {/* RIGHT-SIDE EGO NETWORK DRAWER                             */}
      {/* ───────────────────────────────────────────────────────── */}
      {selectedRecipientId && dossier && (
        <div className="fixed inset-y-0 right-0 w-full max-w-2xl bg-white shadow-2xl border-l border-slate-200 z-50 flex flex-col animate-in slide-in-from-right duration-200">
          <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
            <div className="flex items-center gap-3">
              <OrgLogo org={dossier.recipient.name} domain={dossier.recipient.website} size="md" />
              <div>
                <div className="text-xs font-bold uppercase tracking-wider text-indigo-600">Company Commercialization Dossier</div>
                <h2 className="text-base font-bold text-slate-900 mt-0.5">{dossier.recipient.name}</h2>
              </div>
            </div>
            <button
              onClick={() => setSelectedRecipientId(null)}
              className="p-1 rounded-lg hover:bg-slate-200 text-slate-500 transition-colors"
            >
              <X size={18} />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            {/* 9-Dimensional Lineage Provenance HUD */}
            <ProvenanceRibbon
              entityType="recipient"
              entityId={dossier.recipient.id}
            />

            {/* ── CAPITAL CONTINUUM GAUGE ── */}
            {continuum && (
              <div className="bg-slate-900 text-white rounded-xl p-4 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1.5">
                    <TrendingUp size={13} /> Multi-Stage Capital Continuum
                  </div>
                  <span className="font-mono font-bold text-emerald-400 text-xs">
                    Grand Total: {formatCurrency(continuum.financial_aggregates.grand_total_capital_usd)}
                  </span>
                </div>

                {/* Continuum Progress Bar */}
                <div className="grid grid-cols-5 gap-1.5 pt-1">
                  <div className={clsx("p-2 rounded-lg text-center border", continuum.financial_aggregates.total_public_grants_usd > 0 ? "bg-cyan-500/20 border-cyan-500/40 text-cyan-300" : "bg-white/5 border-white/10 text-slate-500")}>
                    <div className="text-[9px] uppercase font-bold">1. Grants</div>
                    <div className="font-mono font-bold text-[11px] mt-0.5">{formatCurrency(continuum.financial_aggregates.total_public_grants_usd)}</div>
                  </div>

                  <div className={clsx("p-2 rounded-lg text-center border", continuum.financial_aggregates.total_sec_form_d_usd > 0 ? "bg-amber-500/20 border-amber-500/40 text-amber-300" : "bg-white/5 border-white/10 text-slate-500")}>
                    <div className="text-[9px] uppercase font-bold">2. Form D</div>
                    <div className="font-mono font-bold text-[11px] mt-0.5">{formatCurrency(continuum.financial_aggregates.total_sec_form_d_usd)}</div>
                  </div>

                  <div className={clsx("p-2 rounded-lg text-center border", continuum.financial_aggregates.total_vc_investments_usd > 0 ? "bg-emerald-500/20 border-emerald-500/40 text-emerald-300" : "bg-white/5 border-white/10 text-slate-500")}>
                    <div className="text-[9px] uppercase font-bold">3. VC Equity</div>
                    <div className="font-mono font-bold text-[11px] mt-0.5">{formatCurrency(continuum.financial_aggregates.total_vc_investments_usd)}</div>
                  </div>

                  <div className={clsx("p-2 rounded-lg text-center border", continuum.financial_aggregates.total_scaleup_allocations_usd > 0 ? "bg-purple-500/20 border-purple-500/40 text-purple-300" : "bg-white/5 border-white/10 text-slate-500")}>
                    <div className="text-[9px] uppercase font-bold">4. LPO / 48C</div>
                    <div className="font-mono font-bold text-[11px] mt-0.5">{formatCurrency(continuum.financial_aggregates.total_scaleup_allocations_usd)}</div>
                  </div>

                  <div className={clsx("p-2 rounded-lg text-center border", continuum.financial_aggregates.total_procurement_offtake_usd > 0 ? "bg-indigo-500/20 border-indigo-500/40 text-indigo-300" : "bg-white/5 border-white/10 text-slate-500")}>
                    <div className="text-[9px] uppercase font-bold">5. Offtake</div>
                    <div className="font-mono font-bold text-[11px] mt-0.5">{formatCurrency(continuum.financial_aggregates.total_procurement_offtake_usd)}</div>
                  </div>
                </div>
              </div>
            )}

            {/* Interactive Ego Network Studio Canvas */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                  <Network size={14} className="text-indigo-600" /> Interactive Ego Network Studio
                </span>
                <span className="text-[10.5px] text-slate-500 font-medium">Draggable Physics · Orbits · Live HUD</span>
              </div>
              <InteractiveEgoGraph
                egoGraph={dossier.ego_graph}
                companyName={dossier.recipient.name}
                height={320}
              />
            </div>

            {/* SEC Form D Offerings if present */}
            {continuum?.sec_form_d_filings && continuum.sec_form_d_filings.length > 0 && (
              <div className="space-y-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                  <DollarSign size={13} className="text-cyan-600" /> SEC Form D Exempt Offerings
                </h3>
                <div className="space-y-2">
                  {continuum.sec_form_d_filings.map((filing) => (
                    <div key={filing.id} className="p-3 bg-cyan-50/50 rounded-lg border border-cyan-200 text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-900 font-mono">CIK: {filing.cik}</span>
                        <span className="font-mono font-bold text-cyan-800">{formatCurrency(filing.amount_sold_usd)} Sold</span>
                      </div>
                      <div className="text-slate-600 text-[11px] flex items-center justify-between">
                        <span>Filing Date: {filing.filing_date || 'N/A'}</span>
                        {filing.sec_url && (
                          <a href={filing.sec_url} target="_blank" rel="noopener noreferrer" className="text-cyan-700 hover:underline flex items-center gap-1 font-bold">
                            <span>EDGAR Link</span>
                            <ExternalLink size={10} />
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Federal Scale-up Allocations if present */}
            {continuum?.scaleup_allocations && continuum.scaleup_allocations.length > 0 && (
              <div className="space-y-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                  <Zap size={13} className="text-purple-600" /> Scale-Up Facilities (DOE LPO / 48C)
                </h3>
                <div className="space-y-2">
                  {continuum.scaleup_allocations.map((alloc) => (
                    <div key={alloc.id} className="p-3 bg-purple-50/50 rounded-lg border border-purple-200 text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-purple-900">{alloc.facility_name}</span>
                        <span className="font-mono font-bold text-purple-800">{formatCurrency(alloc.allocation_amount_usd)}</span>
                      </div>
                      <div className="text-slate-600 text-[11px] flex items-center justify-between">
                        <span className="font-semibold">{alloc.program_category}</span>
                        <span className="px-1.5 py-0.5 rounded bg-purple-100 text-purple-800 font-bold text-[9.5px]">{alloc.status}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Federal Procurement Contracts if present */}
            {continuum?.procurement_contracts && continuum.procurement_contracts.length > 0 && (
              <div className="space-y-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                  <ShieldCheck size={13} className="text-indigo-600" /> Federal Procurement &amp; Offtake Contracts
                </h3>
                <div className="space-y-2">
                  {continuum.procurement_contracts.map((contract) => (
                    <div key={contract.id} className="p-3 bg-indigo-50/50 rounded-lg border border-indigo-200 text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-mono font-bold text-indigo-900">{contract.contract_number}</span>
                        <span className="font-mono font-bold text-indigo-800">{formatCurrency(contract.obligated_amount_usd)}</span>
                      </div>
                      <div className="text-slate-600 text-[11px] flex items-center justify-between">
                        <span>Agency: {contract.agency}</span>
                        {contract.is_sbir_phase_3 && (
                          <span className="px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 font-bold text-[9.5px]">SBIR Phase III</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ISO Interconnection Queue Positions if present */}
            {continuum?.interconnection_queues && continuum.interconnection_queues.length > 0 && (
              <div className="space-y-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                  <Zap size={13} className="text-amber-600" /> ISO/RTO Interconnection Queue Positions
                </h3>
                <div className="space-y-2">
                  {continuum.interconnection_queues.map((q) => (
                    <div key={q.id} className="p-3 bg-amber-50/50 rounded-lg border border-amber-200 text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-amber-950">{q.project_name}</span>
                        <span className="font-mono font-bold text-amber-800">{q.capacity_mw} MW</span>
                      </div>
                      <div className="text-slate-600 text-[11px] flex items-center justify-between">
                        <span>ISO: {q.iso_rto} · Queue #{q.queue_id}</span>
                        <span className="px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 font-bold text-[9.5px]">{q.study_phase || q.status}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Private Venture Funding History */}
            <div className="space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <DollarSign size={13} className="text-emerald-600" /> Venture Capital Financing Rounds
              </h3>
              <div className="space-y-2">
                {dossier.investments.map((inv) => (
                  <div key={inv.id} className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900">{inv.round_type}</span>
                      <span className="font-mono font-bold text-emerald-700">{formatCurrency(inv.amount_usd)}</span>
                    </div>
                    <div className="text-slate-600 text-[11px]">
                      Lead Investor: <span className="font-semibold text-slate-800">{inv.lead_investor || 'Undisclosed'}</span>
                      {inv.round_date && <span> · {inv.round_date}</span>}
                    </div>
                    {inv.participating_investors.length > 0 && (
                      <div className="text-[10px] text-slate-500">
                        Syndicate: {inv.participating_investors.join(', ')}
                      </div>
                    )}
                    {inv.notes && <div className="text-[10.5px] text-slate-600 italic mt-1">{inv.notes}</div>}
                  </div>
                ))}
              </div>
            </div>

            {/* USPTO Bayh-Dole Patents */}
            <div className="space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <Lightbulb size={13} className="text-amber-600" /> Assigned Bayh-Dole Patents
              </h3>
              <div className="space-y-2">
                {dossier.patents.map((pat) => (
                  <div key={pat.id} className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1">
                    <div className="flex items-start justify-between gap-2">
                      <span className="font-bold text-slate-900 leading-snug">{pat.title}</span>
                      {pat.patent_url && (
                        <a
                          href={pat.patent_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="shrink-0 text-indigo-600 hover:text-indigo-800 inline-flex items-center gap-1 font-bold text-[10.5px]"
                        >
                          <span>{pat.patent_number}</span>
                          <ExternalLink size={10} />
                        </a>
                      )}
                    </div>
                    {pat.bayh_dole_citation && (
                      <div className="p-2 rounded bg-amber-50/70 border border-amber-200/60 text-[10px] text-amber-900 font-mono leading-relaxed">
                        {pat.bayh_dole_citation}
                      </div>
                    )}
                    <div className="text-[10.5px] text-slate-500 flex items-center justify-between pt-1">
                      <span>Inventors: {pat.inventors || 'Assignee'}</span>
                      <span className="font-semibold">{pat.cited_by_count} Citations</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// FULLY INTERACTIVE & CUSTOMIZABLE GRAPH STUDIO
// ─────────────────────────────────────────────────────────────
function InteractiveGraphStudio({
  graphData,
  onSelectCompany
}: {
  graphData?: AttributionsGraphResponse;
  onSelectCompany: (name: string) => void;
}) {
  const [layoutMode, setLayoutMode] = useState<'orbit' | 'bipartite' | 'cluster'>('orbit');
  const [nodeSearch, setNodeSearch] = useState('');
  const [zoomLevel, setZoomLevel] = useState(1);
  const [selectedNode, setSelectedNode] = useState<AttributionsGraphNode | null>(null);
  const [hoveredNode, setHoveredNode] = useState<AttributionsGraphNode | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  // Visibility toggles
  const [showAgencies, setShowAgencies] = useState(true);
  const [showCompanies, setShowCompanies] = useState(true);
  const [showPatents, setShowPatents] = useState(true);
  const [showInvestors, setShowInvestors] = useState(true);

  const containerRef = useRef<HTMLDivElement>(null);

  const rawNodes = graphData?.nodes || [];
  const rawEdges = graphData?.edges || [];

  // Filter nodes based on toggles and search
  const visibleNodes = useMemo(() => {
    return rawNodes.filter(n => {
      if (n.type === 'agency' && !showAgencies) return false;
      if (n.type === 'company' && !showCompanies) return false;
      if (n.type === 'patent' && !showPatents) return false;
      if (n.type === 'investor' && !showInvestors) return false;
      if (nodeSearch && !n.name.toLowerCase().includes(nodeSearch.toLowerCase())) return false;
      return true;
    });
  }, [rawNodes, showAgencies, showCompanies, showPatents, showInvestors, nodeSearch]);

  const visibleNodeIds = useMemo(() => new Set(visibleNodes.map(n => n.id)), [visibleNodes]);

  const visibleEdges = useMemo(() => {
    return rawEdges.filter(e => visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target));
  }, [rawEdges, visibleNodeIds]);

  // Compute Layout Coordinates based on layoutMode
  const width = 960;
  const height = 560;
  const centerX = width / 2;
  const centerY = height / 2;

  const positions = useMemo(() => {
    const coords: Record<string, { x: number; y: number }> = {};
    const agencies = visibleNodes.filter(n => n.type === 'agency');
    const companies = visibleNodes.filter(n => n.type === 'company');
    const patents = visibleNodes.filter(n => n.type === 'patent');
    const investors = visibleNodes.filter(n => n.type === 'investor');

    if (layoutMode === 'orbit') {
      // Inner Core: Agencies
      agencies.forEach((ag, idx) => {
        const angle = (idx / Math.max(agencies.length, 1)) * 2 * Math.PI - Math.PI / 2;
        coords[ag.id] = { x: centerX + Math.cos(angle) * 100, y: centerY + Math.sin(angle) * 75 };
      });
      // Middle Orbit: Companies
      companies.forEach((co, idx) => {
        const angle = (idx / Math.max(companies.length, 1)) * 2 * Math.PI - Math.PI / 2;
        coords[co.id] = { x: centerX + Math.cos(angle) * 220, y: centerY + Math.sin(angle) * 165 };
      });
      // Outer Left Orbit: Investors
      investors.forEach((inv, idx) => {
        const angle = Math.PI * 0.55 + (idx / Math.max(investors.length, 1)) * Math.PI * 0.9;
        coords[inv.id] = { x: centerX + Math.cos(angle) * 360, y: centerY + Math.sin(angle) * 230 };
      });
      // Outer Right Orbit: Patents
      patents.forEach((pat, idx) => {
        const angle = -Math.PI * 0.45 + (idx / Math.max(patents.length, 1)) * Math.PI * 0.9;
        coords[pat.id] = { x: centerX + Math.cos(angle) * 360, y: centerY + Math.sin(angle) * 230 };
      });
    } else if (layoutMode === 'bipartite') {
      // Left Column: Agencies
      agencies.forEach((ag, idx) => {
        coords[ag.id] = { x: 100, y: 80 + (idx / Math.max(agencies.length - 1, 1)) * (height - 160) };
      });
      // Center Column: Companies
      companies.forEach((co, idx) => {
        coords[co.id] = { x: 380, y: 60 + (idx / Math.max(companies.length - 1, 1)) * (height - 120) };
      });
      // Right Column 1: Patents
      patents.forEach((pat, idx) => {
        coords[pat.id] = { x: 680, y: 50 + (idx / Math.max(patents.length - 1, 1)) * (height - 100) };
      });
      // Right Column 2: Investors
      investors.forEach((inv, idx) => {
        coords[inv.id] = { x: 880, y: 50 + (idx / Math.max(investors.length - 1, 1)) * (height - 100) };
      });
    } else {
      // Clustered
      const clusterCenters: Record<string, { cx: number; cy: number }> = {
        agency: { cx: 200, cy: 160 },
        company: { cx: 500, cy: 280 },
        patent: { cx: 780, cy: 160 },
        investor: { cx: 780, cy: 400 }
      };
      [...agencies, ...companies, ...patents, ...investors].forEach((n, idx) => {
        const center = clusterCenters[n.type] || { cx: centerX, cy: centerY };
        const angle = (idx % 12) * (2 * Math.PI / 12);
        const radius = 40 + Math.floor(idx / 12) * 35;
        coords[n.id] = { x: center.cx + Math.cos(angle) * radius, y: center.cy + Math.sin(angle) * radius };
      });
    }

    return coords;
  }, [visibleNodes, layoutMode, centerX, centerY, height]);

  if (!graphData || !graphData.nodes.length) {
    return (
      <div className="h-96 flex items-center justify-center bg-slate-950 border border-slate-800 rounded-xl text-slate-400 text-xs">
        Loading interactive capital network...
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={clsx(
        'bg-slate-950 rounded-xl border border-slate-800 shadow-2xl overflow-hidden flex flex-col',
        isFullscreen ? 'fixed inset-0 z-50 rounded-none' : 'relative min-h-[620px]'
      )}
    >
      {/* Studio Top Control Bar */}
      <div className="p-3 border-b border-slate-800/90 bg-slate-900/90 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-slate-400 font-bold uppercase tracking-wider text-[10.5px] flex items-center gap-1.5">
            <Sliders size={13} className="text-indigo-400" /> Layout:
          </span>
          <div className="flex items-center bg-slate-800 p-0.5 rounded-lg border border-slate-700">
            {(['orbit', 'bipartite', 'cluster'] as const).map(mode => (
              <button
                key={mode}
                onClick={() => setLayoutMode(mode)}
                className={clsx(
                  'px-2.5 py-1 rounded text-[11px] font-bold capitalize transition-all',
                  layoutMode === mode ? 'bg-indigo-600 text-white shadow-2xs' : 'text-slate-400 hover:text-white'
                )}
              >
                {mode === 'orbit' ? '🪐 Multi-Orbit' : (mode === 'bipartite' ? '⚡ Flow Stream' : '🌌 Clusters')}
              </button>
            ))}
          </div>

          {/* Node Filter Toggles */}
          <div className="flex items-center gap-1 ml-2">
            <button
              onClick={() => setShowAgencies(!showAgencies)}
              className={clsx(
                'px-2 py-0.5 rounded text-[10.5px] font-bold border transition-colors flex items-center gap-1',
                showAgencies ? 'bg-indigo-950/80 text-indigo-300 border-indigo-700/80' : 'bg-slate-800 text-slate-500 border-slate-700'
              )}
            >
              <span className="w-2 h-2 rounded-full bg-indigo-500" />
              <span>Agencies</span>
            </button>

            <button
              onClick={() => setShowCompanies(!showCompanies)}
              className={clsx(
                'px-2 py-0.5 rounded text-[10.5px] font-bold border transition-colors flex items-center gap-1',
                showCompanies ? 'bg-sky-950/80 text-sky-300 border-sky-700/80' : 'bg-slate-800 text-slate-500 border-slate-700'
              )}
            >
              <span className="w-2 h-2 rounded-full bg-sky-400" />
              <span>Startups</span>
            </button>

            <button
              onClick={() => setShowPatents(!showPatents)}
              className={clsx(
                'px-2 py-0.5 rounded text-[10.5px] font-bold border transition-colors flex items-center gap-1',
                showPatents ? 'bg-amber-950/80 text-amber-300 border-amber-700/80' : 'bg-slate-800 text-slate-500 border-slate-700'
              )}
            >
              <span className="w-2 h-2 rounded-full bg-amber-400" />
              <span>Patents ({visibleNodes.filter(n => n.type === 'patent').length})</span>
            </button>

            <button
              onClick={() => setShowInvestors(!showInvestors)}
              className={clsx(
                'px-2 py-0.5 rounded text-[10.5px] font-bold border transition-colors flex items-center gap-1',
                showInvestors ? 'bg-emerald-950/80 text-emerald-300 border-emerald-700/80' : 'bg-slate-800 text-slate-500 border-slate-700'
              )}
            >
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              <span>VC Investors</span>
            </button>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Quick Search */}
          <div className="relative">
            <Search size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search graph..."
              value={nodeSearch}
              onChange={e => setNodeSearch(e.target.value)}
              className="pl-7 pr-3 py-1 bg-slate-800/90 border border-slate-700 rounded-lg text-slate-200 text-xs w-36 focus:w-48 transition-all focus:ring-1 focus:ring-indigo-500 outline-none placeholder-slate-500"
            />
          </div>

          {/* Zoom controls */}
          <div className="flex items-center bg-slate-800 rounded-lg border border-slate-700 p-0.5 text-slate-300">
            <button
              onClick={() => setZoomLevel(z => Math.max(0.6, z - 0.15))}
              className="p-1 hover:text-white hover:bg-slate-700 rounded transition-colors"
              title="Zoom out"
            >
              <ZoomOut size={13} />
            </button>
            <button
              onClick={() => setZoomLevel(1)}
              className="px-1.5 py-0.5 text-[10px] font-mono hover:text-white"
              title="Reset Zoom"
            >
              {Math.round(zoomLevel * 100)}%
            </button>
            <button
              onClick={() => setZoomLevel(z => Math.min(2.0, z + 0.15))}
              className="p-1 hover:text-white hover:bg-slate-700 rounded transition-colors"
              title="Zoom in"
            >
              <ZoomIn size={13} />
            </button>
          </div>

          {/* Fullscreen Toggle */}
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition-colors"
            title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen Studio'}
          >
            {isFullscreen ? <Minimize2 size={13} /> : <Maximize2 size={13} />}
          </button>
        </div>
      </div>

      {/* SVG Canvas Area */}
      <div className="relative flex-1 bg-slate-950 overflow-hidden select-none">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-full"
          style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'center center', transition: 'transform 0.2s ease-out' }}
        >
          <defs>
            <radialGradient id="nodeGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#6366f1" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#6366f1" stopOpacity="0" />
            </radialGradient>
          </defs>

          {/* Draw Edges */}
          {visibleEdges.map((e, idx) => {
            const src = positions[e.source];
            const tgt = positions[e.target];
            if (!src || !tgt) return null;
            const isHighlighted = selectedNode && (selectedNode.id === e.source || selectedNode.id === e.target);
            return (
              <line
                key={idx}
                x1={src.x}
                y1={src.y}
                x2={tgt.x}
                y2={tgt.y}
                stroke={isHighlighted ? '#ffffff' : (e.color || '#334155')}
                strokeWidth={isHighlighted ? 2.5 : 1.2}
                strokeOpacity={isHighlighted ? 0.9 : 0.4}
              />
            );
          })}

          {/* Draw Nodes */}
          {visibleNodes.map((node) => {
            const pos = positions[node.id];
            if (!pos) return null;
            const isSelected = selectedNode?.id === node.id;
            const isHovered = hoveredNode?.id === node.id;
            const isCompany = node.type === 'company';
            const isPatent = node.type === 'patent';
            const isInvestor = node.type === 'investor';
            
            const nodeColor = isPatent ? '#f59e0b' : (isInvestor ? '#10b981' : (isCompany ? '#38bdf8' : '#6366f1'));

            return (
              <g
                key={node.id}
                transform={`translate(${pos.x}, ${pos.y})`}
                className="cursor-pointer"
                onMouseEnter={() => setHoveredNode(node)}
                onMouseLeave={() => setHoveredNode(null)}
                onClick={() => {
                  setSelectedNode(node);
                  if (isCompany) onSelectCompany(node.name);
                }}
              >
                {(isSelected || isHovered) && (
                  <circle r={(node.size || 16) + 8} fill="url(#nodeGlow)" />
                )}
                <circle
                  r={node.size || 16}
                  fill={nodeColor}
                  stroke={isSelected ? '#ffffff' : (isHovered ? '#cbd5e1' : '#0f172a')}
                  strokeWidth={isSelected ? 3 : (isCompany ? 2.5 : 1.5)}
                  className="transition-transform duration-200"
                />
                <text
                  dy={node.size ? node.size + 11 : 20}
                  textAnchor="middle"
                  fill={isSelected ? '#ffffff' : '#94a3b8'}
                  fontSize={isCompany ? '9.5px' : '8px'}
                  fontWeight={isCompany || isSelected ? 'bold' : 'normal'}
                  className="pointer-events-none drop-shadow"
                >
                  {node.name.length > 18 ? `${node.name.slice(0, 16)}...` : node.name}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Hover Tooltip */}
        {hoveredNode && !selectedNode && (
          <div className="absolute bottom-4 left-4 bg-slate-900/95 border border-slate-700 text-white p-2.5 rounded-lg shadow-xl text-xs max-w-sm pointer-events-none animate-in fade-in duration-150">
            <div className="flex items-center gap-1.5 mb-1">
              <span className={clsx(
                'px-1.5 py-0.2 rounded text-[9.5px] font-bold uppercase',
                hoveredNode.type === 'patent' ? 'bg-amber-500/20 text-amber-300' :
                hoveredNode.type === 'investor' ? 'bg-emerald-500/20 text-emerald-300' :
                hoveredNode.type === 'company' ? 'bg-sky-500/20 text-sky-300' : 'bg-indigo-500/20 text-indigo-300'
              )}>
                {hoveredNode.type}
              </span>
              <span className="font-bold text-slate-100">{hoveredNode.name}</span>
            </div>
            <div className="text-[11px] text-slate-400">Click node to open complete intelligence dossier.</div>
          </div>
        )}

        {/* Clicked Node Inspector HUD Popup */}
        {selectedNode && (
          <div className="absolute top-4 right-4 w-80 bg-slate-900/95 border border-slate-700 text-white p-4 rounded-xl shadow-2xl text-xs space-y-3 animate-in slide-in-from-right duration-200">
            <div className="flex items-start justify-between">
              <div>
                <span className={clsx(
                  'px-2 py-0.5 rounded text-[9.5px] font-bold uppercase tracking-wider',
                  selectedNode.type === 'patent' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                  selectedNode.type === 'investor' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                  selectedNode.type === 'company' ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30' : 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                )}>
                  {selectedNode.type === 'patent' ? '💡 USPTO Bayh-Dole Patent' : (selectedNode.type === 'investor' ? '💰 Climate VC Fund' : (selectedNode.type === 'company' ? '🏢 Awardee Startup' : '🏛️ Funding Agency'))}
                </span>
                <h3 className="font-bold text-sm text-slate-100 mt-1.5 leading-snug">{selectedNode.name}</h3>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="p-1 text-slate-400 hover:text-white rounded-lg transition-colors"
              >
                <X size={15} />
              </button>
            </div>

            {selectedNode.type === 'patent' && (
              <div className="space-y-2 pt-2 border-t border-slate-800 text-[11px]">
                <div className="text-slate-300 leading-relaxed">
                  Verified Bayh-Dole patent citing federal & state clean energy grant awards.
                </div>
                <a
                  href={`https://patents.google.com/patent/${selectedNode.name.replace(/[^A-Za-z0-9]/g, '')}/en`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-amber-400 hover:text-amber-300 font-bold"
                >
                  <span>Open on Google Patents</span>
                  <ExternalLink size={11} />
                </a>
              </div>
            )}

            {selectedNode.type === 'company' && (
              <div className="space-y-2 pt-2 border-t border-slate-800 text-[11px]">
                <div className="text-slate-300 leading-relaxed">
                  Pioneering scale-up with grant-funded innovations and follow-on private capital.
                </div>
                <button
                  onClick={() => onSelectCompany(selectedNode.name)}
                  className="w-full py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-lg transition-colors flex items-center justify-center gap-1.5"
                >
                  <Network size={12} />
                  <span>Inspect Company Dossier</span>
                </button>
              </div>
            )}

            {selectedNode.type === 'investor' && (
              <div className="space-y-2 pt-2 border-t border-slate-800 text-[11px]">
                <div className="text-slate-300 leading-relaxed">
                  Institutional climate syndicate investor participating in grant-backed clean tech financing.
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
