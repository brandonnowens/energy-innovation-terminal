import React, { useState, useMemo } from 'react';
import {
  Sparkles, ShieldCheck, Mail, MapPin, Target, CheckCircle2,
  ExternalLink, Copy, Check, ChevronDown, ChevronUp, Search,
  Filter, Building2, Zap, Landmark, HeartHandshake, Download,
  Users, Flame, ArrowUpRight, Compass, Layers, Globe, X,
  LayoutList, LayoutGrid, FileText, ChevronRight
} from 'lucide-react';
import clsx from 'clsx';
import { SayYesOrganization, SayYesDecisionMaker } from '../api/client';
import { OrgLogo } from './OrgLogo';
import { useNyserda } from '../context/NyserdaContext';

interface SayYesDecisionMakerMatrixProps {
  organizations: SayYesOrganization[];
  projectTitle?: string;
  projectLocation?: string;
  onSelectOpportunity?: (oppId: number) => void;
}

export function SayYesDecisionMakerMatrix({
  organizations,
  projectTitle,
  projectLocation,
  onSelectOpportunity,
}: SayYesDecisionMakerMatrixProps) {
  const { includeNyserda, isNyserda } = useNyserda();
  const [viewLimit, setViewLimit] = useState<'10' | '15' | '25' | 'all'>('15');
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const [search, setSearch] = useState('');
  const [copiedEmail, setCopiedEmail] = useState<string | null>(null);
  const [viewLayout, setViewLayout] = useState<'table' | 'cards'>('table');
  const [selectedOrg, setSelectedOrg] = useState<SayYesOrganization | null>(null);

  // Active pool of organizations based on selected viewLimit and NYSERDA inclusion
  const activeOrgs = useMemo(() => {
    const raw = (organizations || []).filter(
      (org) => includeNyserda || (!isNyserda(org.organization_name) && !isNyserda(org.organization_code))
    );
    if (viewLimit === '10') return raw.slice(0, 10);
    if (viewLimit === '15') return raw.slice(0, 15);
    if (viewLimit === '25') return raw.slice(0, 25);
    return raw;
  }, [organizations, viewLimit, includeNyserda, isNyserda]);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedEmail(id);
    setTimeout(() => setCopiedEmail(null), 2000);
  };

  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = { all: activeOrgs.length, utility: 0, state: 0, federal: 0, foundation: 0 };
    activeOrgs.forEach(org => {
      const cat = org.category || 'utility';
      counts[cat] = (counts[cat] || 0) + 1;
    });
    return counts;
  }, [activeOrgs]);

  const filteredOrgs = useMemo(() => {
    return activeOrgs.filter(org => {
      if (activeCategory !== 'all' && org.category !== activeCategory) return false;
      if (!search.trim()) return true;
      const s = search.toLowerCase();
      const matchName = org.organization_name.toLowerCase().includes(s) || org.organization_code.toLowerCase().includes(s);
      const matchState = org.state.toLowerCase().includes(s) || (org.territory_desc && org.territory_desc.toLowerCase().includes(s));
      const matchPain = org.primary_pain_points.some(p => p.toLowerCase().includes(s));
      const matchContact = org.decision_maker_contacts.some(c => c.name.toLowerCase().includes(s) || c.title.toLowerCase().includes(s));
      return matchName || matchState || matchPain || matchContact;
    });
  }, [activeOrgs, activeCategory, search]);

  if (!organizations || organizations.length === 0) {
    return (
      <div className="p-8 text-center bg-white dark:bg-[#0d1424] rounded-2xl border border-slate-200/80 dark:border-white/10 shadow-2xs">
        <Sparkles className="mx-auto mb-2 text-indigo-600 dark:text-indigo-400 opacity-60" size={28} />
        <p className="text-sm font-bold text-slate-800 dark:text-slate-200">No organization match rankings available yet.</p>
        <p className="text-xs text-slate-500 mt-1">Run project matching to generate the ranked outreach matrix.</p>
      </div>
    );
  }

  const limitLabel = viewLimit === '10' ? 'Top 10' : viewLimit === '15' ? 'Top 15' : viewLimit === '25' ? 'Top 25' : `All (${organizations.length})`;

  return (
    <div className="bg-white dark:bg-[#0d1424] rounded-2xl border border-slate-200/80 dark:border-white/10 p-5 shadow-2xs space-y-4">
      {/* Header Bar */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-3 border-b border-slate-100 dark:border-slate-800">
        <div>
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
              <Building2 size={12} className="text-slate-500" />
              <span>Sponsoring Organizations &amp; Decision-Makers</span>
            </span>
            <span className="text-xs text-slate-300 dark:text-slate-700">|</span>
            <span className="text-[11px] font-mono font-medium text-slate-500 dark:text-slate-400">
              {activeOrgs.length} Ranked Entities
            </span>
          </div>
          <h2 className="text-base font-bold text-slate-900 dark:text-slate-100 tracking-tight">
            {limitLabel} Sponsoring Organizations Most Likely to Say &ldquo;YES&rdquo;
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 max-w-3xl leading-relaxed">
            Screened against <strong>utility service territories</strong>, <strong>state jurisdiction boundaries</strong>, and institutional <strong>mandate fit</strong>. Click any row to inspect decision-maker contacts, pain points, and active solicitations.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2 shrink-0">
          {/* View Limit Selector */}
          <div className="flex items-center bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg border border-slate-200 dark:border-slate-700">
            <button
              type="button"
              onClick={() => setViewLimit('10')}
              className={clsx(
                'px-2 py-1 rounded-md text-xs font-semibold transition-all cursor-pointer',
                viewLimit === '10' ? 'bg-[#00E5FF] text-slate-950 font-bold shadow-glow-cyan-sm' : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'
              )}
            >
              Top 10
            </button>
            <button
              type="button"
              onClick={() => setViewLimit('15')}
              className={clsx(
                'px-2 py-1 rounded-md text-xs font-semibold transition-all cursor-pointer',
                viewLimit === '15' ? 'bg-[#00E5FF] text-slate-950 font-bold shadow-glow-cyan-sm' : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'
              )}
            >
              Top 15
            </button>
            <button
              type="button"
              onClick={() => setViewLimit('25')}
              className={clsx(
                'px-2 py-1 rounded-md text-xs font-semibold transition-all cursor-pointer',
                viewLimit === '25' ? 'bg-[#00E5FF] text-slate-950 font-bold shadow-glow-cyan-sm' : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'
              )}
            >
              Top 25
            </button>
            <button
              type="button"
              onClick={() => setViewLimit('all')}
              className={clsx(
                'px-2 py-1 rounded-md text-xs font-semibold transition-all cursor-pointer',
                viewLimit === 'all' ? 'bg-[#00E5FF] text-slate-950 font-bold shadow-glow-cyan-sm' : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'
              )}
            >
              All ({organizations.length})
            </button>
          </div>

          <div className="flex items-center bg-slate-100 dark:bg-black/30 p-1 rounded-xl border border-slate-200 dark:border-white/10">
            <button
              type="button"
              onClick={() => setViewLayout('table')}
              className={clsx(
                'px-2.5 py-1 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer',
                viewLayout === 'table' ? 'bg-[#00E5FF] text-slate-950 font-bold shadow-glow-cyan-sm' : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
              )}
            >
              <LayoutList size={13} />
              <span>Table</span>
            </button>
            <button
              type="button"
              onClick={() => setViewLayout('cards')}
              className={clsx(
                'px-2.5 py-1 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer',
                viewLayout === 'cards' ? 'bg-[#00E5FF] text-slate-950 font-bold shadow-glow-cyan-sm' : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
              )}
            >
              <LayoutGrid size={13} />
              <span>Cards</span>
            </button>
          </div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        {/* Category Tabs */}
        <div className="flex items-center gap-1 overflow-x-auto no-scrollbar py-0.5">
          {[
            { id: 'all', label: 'All Organizations', icon: Globe },
            { id: 'utility', label: 'Electric & Gas Utilities', icon: Zap },
            { id: 'state', label: 'State Energy Agencies', icon: Building2 },
            { id: 'federal', label: 'Federal Innovation', icon: Landmark },
            { id: 'foundation', label: 'Philanthropic Funds', icon: HeartHandshake },
          ].map(tab => {
            const Icon = tab.icon;
            const isCurrent = activeCategory === tab.id;
            const count = categoryCounts[tab.id] || 0;
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
                <span className={clsx('text-[10px] px-1.5 py-0.2 rounded-full font-mono font-bold', isCurrent ? 'bg-slate-950/20 text-slate-950' : 'bg-slate-200 dark:bg-white/10 text-slate-600 dark:text-slate-400')}>
                  {count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Search Input */}
        <div className="relative flex-1 sm:w-64 max-w-xs">
          <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Filter by organization, pain point, contact..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 text-xs rounded-xl bg-slate-50 dark:bg-black/30 border border-slate-200 dark:border-white/10 outline-none focus:border-indigo-500 text-slate-900 dark:text-white placeholder:text-slate-400"
          />
        </div>
      </div>

      {/* ─── TABULAR MATRIX VIEW (DEFAULT) ────────────────────────────────── */}
      {viewLayout === 'table' && (
        <div className="rounded-xl border border-slate-200 dark:border-white/10 overflow-hidden shadow-2xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-200 dark:border-white/10 bg-slate-50/80 dark:bg-white/[0.02] text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 font-mono">
                  <th className="py-3 px-3.5 w-12 text-center">Rank</th>
                  <th className="py-3 px-3.5 min-w-[200px]">Organization &amp; Category</th>
                  <th className="py-3 px-3.5 min-w-[150px]">Jurisdiction &amp; Territory</th>
                  <th className="py-3 px-3.5 w-36 text-center">Say Yes Propensity</th>
                  <th className="py-3 px-3.5 min-w-[240px]">Strategic Alignment &amp; Pain Points</th>
                  <th className="py-3 px-3.5 min-w-[170px]">Lead Contact</th>
                  <th className="py-3 px-3.5 w-24 text-center">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-white/5 text-xs">
                {filteredOrgs.map((org) => {
                  const leadContact = org.decision_maker_contacts[0];
                  return (
                    <tr
                      key={org.rank}
                      onClick={() => setSelectedOrg(org)}
                      className={clsx(
                        'hover:bg-slate-50/70 dark:hover:bg-white/[0.02] transition-colors cursor-pointer group',
                        org.rank === 1 && 'bg-amber-50/30 dark:bg-amber-950/10'
                      )}
                    >
                      {/* Rank */}
                      <td className="py-3 px-3.5 text-center font-mono">
                        <span
                          className={clsx(
                            'inline-flex items-center justify-center w-7 h-7 rounded-lg text-xs font-black',
                            org.rank === 1
                              ? 'bg-amber-400 text-slate-950 shadow-2xs'
                              : org.rank <= 3
                              ? 'bg-slate-200 text-slate-800 dark:bg-white/10 dark:text-slate-200'
                              : 'bg-slate-100 text-slate-600 dark:bg-white/5 dark:text-slate-400'
                          )}
                        >
                          #{org.rank}
                        </span>
                      </td>

                      {/* Organization & Category */}
                      <td className="py-3 px-3.5">
                        <div className="flex items-center gap-2.5">
                          <OrgLogo org={org.organization_code} size="xs" showTooltip={false} />
                          <div className="min-w-0">
                            <div className="font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors truncate">
                              {org.organization_code}
                            </div>
                            <div className="text-[11px] text-slate-500 dark:text-slate-400 truncate max-w-[200px]" title={org.organization_name}>
                              {org.organization_name}
                            </div>
                            <span className="inline-block mt-0.5 text-[9.5px] font-semibold px-2 py-0.2 rounded-md bg-slate-100 text-slate-600 dark:bg-white/5 dark:text-slate-400">
                              {org.category_label}
                            </span>
                          </div>
                        </div>
                      </td>

                      {/* Territory & Jurisdiction */}
                      <td className="py-3 px-3.5">
                        <div className="flex items-start gap-1.5 text-[11px]">
                          <MapPin size={12} className="text-slate-400 shrink-0 mt-0.5" />
                          <div>
                            <div className="font-bold text-slate-800 dark:text-slate-200">{org.geographic_nexus}</div>
                            {org.territory_desc && (
                              <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2" title={org.territory_desc}>
                                {org.territory_desc}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>

                      {/* Say Yes Propensity Gauge */}
                      <td className="py-3 px-3.5 text-center">
                        <div className="inline-flex flex-col items-center">
                          <div className="flex items-center gap-1 font-mono font-bold text-sm text-emerald-600 dark:text-emerald-400">
                            <Sparkles size={12} className="text-emerald-500" />
                            <span>{org.say_yes_score}%</span>
                          </div>
                          <div className="w-20 bg-slate-200 dark:bg-white/10 h-1.5 rounded-full overflow-hidden mt-1">
                            <div
                              className="h-full bg-emerald-500 rounded-full"
                              style={{ width: `${Math.min(100, org.say_yes_score)}%` }}
                            />
                          </div>
                          <span className="text-[9.5px] font-bold text-slate-400 mt-0.5 uppercase tracking-wider">
                            {org.say_yes_tier}
                          </span>
                        </div>
                      </td>

                      {/* Strategic Alignment & Pain Points */}
                      <td className="py-3 px-3.5">
                        <div className="space-y-1">
                          <div className="text-[11px] text-slate-700 dark:text-slate-300 italic line-clamp-2">
                            &ldquo;{org.why_they_say_yes}&rdquo;
                          </div>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {org.primary_pain_points.slice(0, 2).map((p, i) => (
                              <span key={i} className="text-[10px] px-1.5 py-0.2 rounded bg-amber-50 text-amber-800 border border-amber-200 dark:bg-amber-950/30 dark:text-amber-300 dark:border-amber-500/30 font-medium">
                                {p}
                              </span>
                            ))}
                          </div>
                        </div>
                      </td>

                      {/* Lead Contact */}
                      <td className="py-3 px-3.5">
                        {leadContact ? (
                          <div className="space-y-0.5">
                            <div className="font-bold text-slate-900 dark:text-white text-[11.5px] truncate">{leadContact.name}</div>
                            <div className="text-[10.5px] text-slate-500 dark:text-slate-400 truncate">{leadContact.title}</div>
                            <button
                              type="button"
                              onClick={(e) => {
                                e.stopPropagation();
                                copyToClipboard(leadContact.email, `table-${org.rank}`);
                              }}
                              className="inline-flex items-center gap-1 text-[10.5px] font-mono text-indigo-600 dark:text-indigo-400 hover:underline mt-0.5 cursor-pointer"
                            >
                              {copiedEmail === `table-${org.rank}` ? (
                                <>
                                  <Check size={11} className="text-emerald-500" />
                                  <span>Copied</span>
                                </>
                              ) : (
                                <>
                                  <Mail size={11} />
                                  <span>{leadContact.email}</span>
                                </>
                              )}
                            </button>
                          </div>
                        ) : (
                          <span className="text-slate-400 text-[11px]">Program Office</span>
                        )}
                      </td>

                      {/* Details button */}
                      <td className="py-3 px-3.5 text-center">
                        <button
                          type="button"
                          className="px-2 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-white/5 dark:hover:bg-white/10 text-slate-700 dark:text-slate-300 text-xs font-semibold flex items-center justify-center gap-1 mx-auto transition-colors cursor-pointer"
                        >
                          <span>Dossier</span>
                          <ChevronRight size={12} />
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

      {/* ─── CARD VIEW ────────────────────────────────────────────────────── */}
      {viewLayout === 'cards' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {filteredOrgs.map((org) => (
            <div
              key={org.rank}
              onClick={() => setSelectedOrg(org)}
              className="bg-slate-50 dark:bg-black/30 rounded-xl border border-slate-200/80 dark:border-white/5 p-4 space-y-3 hover:border-indigo-400 dark:hover:border-indigo-500/40 transition-all cursor-pointer shadow-2xs flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded-md bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 font-bold font-mono text-xs flex items-center justify-center">
                      #{org.rank}
                    </span>
                    <span className="font-bold text-sm text-slate-900 dark:text-white">{org.organization_code}</span>
                  </div>
                  <span className="font-mono font-bold text-xs text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-500/30">
                    {org.say_yes_score}%
                  </span>
                </div>

                <div className="text-xs text-slate-500 dark:text-slate-400 font-medium truncate">{org.organization_name}</div>
                <div className="text-[11px] text-slate-600 dark:text-slate-300 mt-2 italic line-clamp-2">
                  &ldquo;{org.why_they_say_yes}&rdquo;
                </div>

                <div className="flex flex-wrap gap-1 mt-2.5">
                  {org.primary_pain_points.slice(0, 2).map((p, i) => (
                    <span key={i} className="text-[10px] px-1.5 py-0.2 rounded bg-amber-50 text-amber-800 border border-amber-200 dark:bg-amber-950/30 dark:text-amber-300 dark:border-amber-500/30 font-medium">
                      {p}
                    </span>
                  ))}
                </div>
              </div>

              <div className="pt-2 border-t border-slate-200/60 dark:border-white/5 flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
                <span>{org.geographic_nexus}</span>
                <span className="text-indigo-600 dark:text-indigo-400 font-semibold flex items-center gap-0.5">
                  View Dossier <ChevronRight size={11} />
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ─── INTERACTIVE ORGANIZATION DOSSIER SLIDE-OVER DRAWER ───────────── */}
      {selectedOrg && (
        <div className="fixed inset-0 z-50 flex items-center justify-end bg-black/60 backdrop-blur-xs animate-in fade-in duration-150 p-0 sm:p-4">
          <div className="w-full sm:max-w-2xl h-full sm:h-[94vh] bg-white dark:bg-[#0d1424] border-l sm:border sm:rounded-2xl border-slate-200 dark:border-white/15 shadow-2xl flex flex-col overflow-hidden animate-in slide-in-from-right duration-200">
            {/* Drawer Header */}
            <div className="p-5 border-b border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-black/30 flex items-start justify-between gap-4 shrink-0">
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 font-black font-mono text-base flex items-center justify-center shrink-0 border border-indigo-200 dark:border-indigo-500/30">
                  #{selectedOrg.rank}
                </div>
                <div className="min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <OrgLogo org={selectedOrg.organization_code} size="xs" showTooltip={false} />
                    <h2 className="text-base font-bold text-slate-900 dark:text-white truncate">{selectedOrg.organization_name}</h2>
                  </div>
                  <div className="flex items-center gap-2 mt-1 text-xs text-slate-500 dark:text-slate-400 flex-wrap">
                    <span className="px-2 py-0.5 rounded-full bg-slate-200 dark:bg-white/10 text-slate-700 dark:text-slate-300 font-semibold text-[10px]">
                      {selectedOrg.category_label}
                    </span>
                    <span>·</span>
                    <span>{selectedOrg.state}</span>
                    <span>·</span>
                    <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400">{selectedOrg.say_yes_score}% Propensity</span>
                  </div>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setSelectedOrg(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-200 dark:hover:bg-white/10 transition-colors cursor-pointer shrink-0"
              >
                <X size={16} />
              </button>
            </div>

            {/* Drawer Scrollable Body */}
            <div className="p-5 overflow-y-auto space-y-5 flex-1 text-xs leading-relaxed">
              {/* Strategic Pitch Thesis */}
              <div className="p-4 rounded-xl bg-indigo-50/70 dark:bg-indigo-950/30 border border-indigo-200/80 dark:border-indigo-500/30 space-y-1.5">
                <div className="text-xs font-bold uppercase tracking-wider text-indigo-900 dark:text-indigo-300 flex items-center gap-1.5">
                  <ShieldCheck size={14} className="text-indigo-600 dark:text-indigo-400" />
                  <span>Strategic Match Thesis (&ldquo;Why They Say YES&rdquo;)</span>
                </div>
                <p className="text-xs text-slate-800 dark:text-slate-200 leading-relaxed italic">
                  &ldquo;{selectedOrg.why_they_say_yes}&rdquo;
                </p>
              </div>

              {/* Geographic Territory & Grid Nexus */}
              <div className="space-y-1.5">
                <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                  <MapPin size={13} className="text-slate-400" />
                  <span>Jurisdiction &amp; Territory</span>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-black/30 border border-slate-200/80 dark:border-white/5 space-y-1">
                  <div className="font-bold text-slate-900 dark:text-white text-xs">{selectedOrg.geographic_nexus}</div>
                  {selectedOrg.territory_desc && (
                    <p className="text-slate-500 dark:text-slate-400 text-[11.5px]">{selectedOrg.territory_desc}</p>
                  )}
                </div>
              </div>

              {/* Targeted Pain Points */}
              <div className="space-y-1.5">
                <div className="text-[11px] font-bold uppercase tracking-wider text-amber-700 dark:text-amber-400 flex items-center gap-1.5">
                  <Target size={13} className="text-amber-600" />
                  <span>Targeted Institutional Mandates ({selectedOrg.primary_pain_points.length})</span>
                </div>
                <div className="space-y-1.5">
                  {selectedOrg.primary_pain_points.map((pain, idx) => (
                    <div key={idx} className="p-2.5 rounded-xl bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-500/30 text-amber-900 dark:text-amber-100 flex items-start gap-2">
                      <Flame size={13} className="text-amber-600 shrink-0 mt-0.5" />
                      <span className="text-xs font-medium leading-snug">{pain}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Decision-Maker Contacts Roster */}
              <div className="space-y-1.5">
                <div className="text-[11px] font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Users size={13} className="text-indigo-600 dark:text-indigo-400" />
                    <span>Decision-Maker Contacts ({selectedOrg.decision_maker_contacts.length})</span>
                  </span>
                </div>
                <div className="space-y-2">
                  {selectedOrg.decision_maker_contacts.map((contact, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-slate-50 dark:bg-black/30 border border-slate-200/80 dark:border-white/5 flex items-center justify-between gap-3"
                    >
                      <div className="min-w-0">
                        <div className="font-bold text-xs text-slate-900 dark:text-white truncate">{contact.name}</div>
                        <div className="text-[11px] text-slate-500 dark:text-slate-400 truncate">{contact.title}</div>
                        {contact.department && (
                          <div className="text-[10px] text-indigo-600 dark:text-indigo-400 font-mono mt-0.5">{contact.department}</div>
                        )}
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        <button
                          type="button"
                          onClick={() => copyToClipboard(contact.email, `drawer-${idx}`)}
                          className="px-2 py-1 rounded-lg bg-white dark:bg-white/10 hover:bg-slate-100 dark:hover:bg-white/20 text-slate-700 dark:text-slate-200 text-xs font-semibold flex items-center gap-1 transition-colors border border-slate-200 dark:border-white/10 cursor-pointer"
                        >
                          {copiedEmail === `drawer-${idx}` ? (
                            <>
                              <Check size={11} className="text-emerald-500" />
                              <span>Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy size={11} />
                              <span>Copy</span>
                            </>
                          )}
                        </button>
                        <a
                          href={`mailto:${contact.email}?subject=${encodeURIComponent(`Project Diligence & Sponsoring Alignment: ${projectTitle || 'Clean Energy Innovation'}`)}`}
                          className="px-2.5 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold flex items-center gap-1 transition-colors shadow-2xs"
                        >
                          <Mail size={11} />
                          <span>Email</span>
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Active Opportunities Under this Organization */}
              <div className="space-y-1.5">
                <div className="text-[11px] font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                  <FileText size={13} className="text-slate-400" />
                  <span>Active Solicitations Under {selectedOrg.organization_code} ({selectedOrg.active_opportunities.length})</span>
                </div>
                {selectedOrg.active_opportunities.length > 0 ? (
                  <div className="space-y-1.5">
                    {selectedOrg.active_opportunities.map((opp) => (
                      <div
                        key={opp.id}
                        onClick={() => {
                          if (onSelectOpportunity) {
                            onSelectOpportunity(opp.id);
                            setSelectedOrg(null);
                          }
                        }}
                        className="p-3 rounded-xl bg-slate-50 dark:bg-black/30 border border-slate-200/80 dark:border-white/5 hover:border-indigo-400 dark:hover:border-indigo-500/40 transition-all flex items-center justify-between gap-3 cursor-pointer group"
                      >
                        <div className="min-w-0">
                          <div className="font-mono text-xs font-bold text-indigo-600 dark:text-indigo-400">{opp.solicitation_number}</div>
                          <div className="text-xs font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors truncate">
                            {opp.name}
                          </div>
                        </div>
                        <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400 flex items-center gap-1 shrink-0 group-hover:translate-x-0.5 transition-transform">
                          <span>View Match</span>
                          <ChevronRight size={12} />
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-500 dark:text-slate-400 text-xs p-3 rounded-xl bg-slate-50 dark:bg-black/20 border border-slate-200/60 dark:border-white/5">
                    No active open solicitations listed for this specific cycle; outreach is focused on discretionary programs and direct partnership.
                  </p>
                )}
              </div>
            </div>

            {/* Drawer Footer */}
            <div className="p-3.5 border-t border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-black/40 flex items-center justify-between gap-3 shrink-0">
              <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">
                Rank #{selectedOrg.rank} in Match Diligence
              </span>
              <button
                type="button"
                onClick={() => setSelectedOrg(null)}
                className="px-3 py-1.5 rounded-xl bg-slate-200 dark:bg-white/10 hover:bg-slate-300 dark:hover:bg-white/20 text-slate-800 dark:text-white font-bold text-xs cursor-pointer transition-colors"
              >
                Close Dossier
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

