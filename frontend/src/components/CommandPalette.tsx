import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import {
  Search, FileSearch, Layers, Trophy, Network, GitMerge, TrendingUp,
  FileText, Database, Building2, Sparkles, ArrowRight, X, Loader2,
  ExternalLink, Globe, MapPin, Zap, ChevronRight, FileEdit, Scale, Lightbulb, BookUser, BookOpen, Bot, ShieldCheck, Compass
} from 'lucide-react';
import clsx from 'clsx';
import { OrgLogo } from './OrgLogo';
import { useNyserda } from '../context/NyserdaContext';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

const STATIC_ACTIONS = [
  { id: 'nav-chat', label: 'AI Advisor', sub: 'Grounded RAG AI expert copilot with direct access to all 56k+ awards & 5.7k+ opportunities', to: '/chat', icon: Bot, category: 'AI Advisor' },
  { id: 'nav-match', label: 'Match', sub: 'Deterministic eligibility and funding architecture engine', to: '/', icon: Sparkles, category: 'Opportunities' },
  { id: 'nav-opps', label: 'Solicitations', sub: '5,757 active and historical funding opportunities', to: '/opportunities', icon: FileSearch, category: 'Opportunities' },
  { id: 'nav-awards', label: 'Awards', sub: '56,413 awards representing $104.16B tracked capital & 10k+ grid queues', to: '/awards', icon: Trophy, category: 'Awards' },
  { id: 'nav-venture-patents', label: 'Venture & IP', sub: 'USPTO Bayh-Dole patent citations, $58.22B private VC syndicates & lineage graph', to: '/venture-patents', icon: Lightbulb, category: 'Awards' },
  { id: 'nav-results', label: 'Outcomes', sub: 'Apples-to-apples benchmarks, ROI ratios, and verified success stories', to: '/results', icon: Scale, category: 'Awards' },
  { id: 'nav-orgs', label: 'Organizations', sub: 'Directory of 140+ federal, state, and utility entities', to: '/organizations', icon: Building2, category: 'Directories' },
  { id: 'nav-programs', label: 'Programs', sub: '143 federal, state, and utility programs', to: '/programs', icon: Layers, category: 'Directories' },
  { id: 'nav-contacts', label: 'Contacts', sub: 'Directory of 3,090+ energy innovation domain experts, PIs & agency officers', to: '/contacts', icon: BookUser, category: 'Directories' },
  { id: 'nav-network', label: 'Network', sub: 'Ecosystem clustering, bridge entities, and co-investment', to: '/network', icon: Network, category: 'Directories' },
  { id: 'nav-strategy', label: 'Strategy', sub: 'Interactive capital allocation, positioning, and portfolio strategy workspace', to: '/strategy', icon: Compass, category: 'Intelligence' },
  { id: 'nav-sankey', label: 'Capital Flows', sub: 'Trace funds from agencies through sectors to energy & deep tech verticals', to: '/sankey', icon: GitMerge, category: 'Intelligence' },
  { id: 'nav-trends', label: 'Trends', sub: 'Longitudinal analytics & capital velocity', to: '/trends', icon: TrendingUp, category: 'Intelligence' },
  { id: 'nav-reports', label: 'Reports', sub: 'Macro & policy strategy blueprints, technology domain briefs, and commercialization reports', to: '/reports', icon: FileText, category: 'Intelligence' },
  { id: 'nav-technologies', label: 'Technologies', sub: 'Engineering mechanics, fuel pathways, 2026-2035 frontier targets, and database capital evidence', to: '/technologies', icon: BookOpen, category: 'References' },
  { id: 'nav-policies', label: 'Policies', sub: 'Federal IRA §45/§48 tax credits, elective direct pay cash monetization, NFPA/UL safety codes, and state climate statutes', to: '/policies', icon: ShieldCheck, category: 'References' },
  { id: 'nav-dockets', label: 'Dockets', sub: 'Public Utility Commission dockets, large load interconnection & VPP tariffs', to: '/dockets', icon: Scale, category: 'References' },
  { id: 'nav-updates', label: 'Feeds', sub: 'Real-time telemetry and audit feed of detected dataset updates', to: '/updates', icon: Sparkles, category: 'Data & Audit' },
  { id: 'nav-sources', label: 'Provenance', sub: 'Source authority ranking, audit metrics, and database status', to: '/sources', icon: Database, category: 'Data & Audit' },
  { id: 'nav-splash', label: 'Replay Splash', sub: 'Interactive launch sequence and telemetry indexing animation', to: '__splash__', icon: Sparkles, category: 'System' },
];

export function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const { includeNyserda, isNyserda, isNyserdaAgency } = useNyserda();

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQuery(query.trim());
    }, 200);
    return () => clearTimeout(handler);
  }, [query]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
      setSelectedIndex(0);
    } else {
      setQuery('');
      setDebouncedQuery('');
    }
  }, [isOpen]);

  // Quick query for live opportunities matching search
  const { data: oppsData, isLoading: oppsLoading } = useQuery({
    queryKey: ['cmd-palette-opps', debouncedQuery, includeNyserda],
    queryFn: () => api.getOpportunities({ search: debouncedQuery, page_size: 5, exclude_nyserda: !includeNyserda }),
    enabled: isOpen && debouncedQuery.length >= 2,
    staleTime: 60 * 1000,
  });

  // Quick query for live awards matching search
  const { data: awardsData, isLoading: awardsLoading } = useQuery({
    queryKey: ['cmd-palette-awards', debouncedQuery, includeNyserda],
    queryFn: () => api.getAwards({ search: debouncedQuery, page_size: 5, exclude_nyserda: !includeNyserda }),
    enabled: isOpen && debouncedQuery.length >= 2,
    staleTime: 60 * 1000,
  });

  // Quick query for live programs matching search
  const { data: programsData } = useQuery({
    queryKey: ['cmd-palette-programs'],
    queryFn: () => api.getPrograms(),
    enabled: isOpen,
    staleTime: 5 * 60 * 1000,
  });

  const matchingPrograms = useMemo(() => {
    if (!debouncedQuery || debouncedQuery.length < 2) return [];
    const list = Array.isArray(programsData) ? programsData : (programsData as any)?.items || [];
    const q = debouncedQuery.toLowerCase();
    return list.filter((p: any) => {
      if (!includeNyserda && (isNyserdaAgency(p.agency) || isNyserda(p.name))) return false;
      return p.name?.toLowerCase().includes(q) || 
        p.description?.toLowerCase().includes(q) ||
        p.type?.toLowerCase().includes(q);
    }).slice(0, 4);
  }, [programsData, debouncedQuery, includeNyserda, isNyserda, isNyserdaAgency]);

  // Combine items into a unified list
  const results = useMemo(() => {
    if (!debouncedQuery) {
      return STATIC_ACTIONS.map(action => ({
        type: 'action' as const,
        id: action.id,
        title: action.label,
        subtitle: action.sub,
        category: action.category,
        badge: undefined as string | undefined,
        icon: action.icon,
        to: action.to,
      }));
    }

    const items: Array<{
      type: 'action' | 'opp' | 'award' | 'program';
      id: string;
      title: string;
      subtitle: string;
      category: string;
      badge?: string;
      to: string;
      icon?: any;
    }> = [];

    // Filter static actions
    const q = debouncedQuery.toLowerCase();
    STATIC_ACTIONS.forEach(a => {
      if (a.label.toLowerCase().includes(q) || a.sub.toLowerCase().includes(q)) {
        items.push({
          type: 'action',
          id: a.id,
          title: a.label,
          subtitle: a.sub,
          category: 'Quick Actions',
          icon: a.icon,
          to: a.to,
        });
      }
    });

    // Opportunities
    const oppList = (oppsData as any)?.items || [];
    oppList.forEach((opp: any) => {
      if (!includeNyserda && (isNyserdaAgency(opp.agency) || isNyserda(opp.name))) return;
      items.push({
        type: 'opp',
        id: `opp-${opp.id}`,
        title: `${opp.solicitation_number || 'SOL'} · ${opp.name}`,
        subtitle: `${opp.agency || 'Funder'} · ${opp.status || 'Active'} · ${opp.total_funding ? `$${(opp.total_funding / 1e6).toFixed(1)}M` : 'Funding varies'}`,
        category: 'Funding Solicitations',
        badge: opp.agency,
        to: `/opportunities/${opp.id}`,
      });
    });

    // Programs
    matchingPrograms.forEach((prog: any) => {
      items.push({
        type: 'program',
        id: `prog-${prog.id}`,
        title: prog.name,
        subtitle: `${prog.agency || 'Program'} · ${prog.type || 'Innovation Initiative'}`,
        category: 'Programs & Portfolios',
        to: `/programs`,
      });
    });

    // Awards
    const awardList = (awardsData as any)?.items || [];
    awardList.forEach((aw: any) => {
      if (!includeNyserda && (isNyserdaAgency(aw.agency) || isNyserda(aw.recipient_name) || isNyserda(aw.project_title))) return;
      items.push({
        type: 'award',
        id: `award-${aw.id}`,
        title: `${aw.recipient_name || 'Recipient'} · ${aw.project_title || 'Clean Energy Project'}`,
        subtitle: `${aw.agency || 'Agency'} · ${aw.award_amount ? `$${(aw.award_amount / 1e6).toFixed(2)}M` : '$0'} · ${aw.state || 'US'}`,
        category: 'Awards & Precedents',
        badge: aw.agency,
        to: `/awards`,
      });
    });

    return items;
  }, [debouncedQuery, oppsData, awardsData, matchingPrograms, includeNyserda, isNyserda, isNyserdaAgency]);

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => (prev + 1) % Math.max(1, results.length));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => (prev - 1 + results.length) % Math.max(1, results.length));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const item = results[selectedIndex];
      if (item) {
        if (item.to === '__splash__') {
          onClose();
          window.dispatchEvent(new CustomEvent('replay-splash-screen'));
        } else {
          navigate(item.to);
          onClose();
        }
      }
    } else if (e.key === 'Escape') {
      onClose();
    }
  };

  // Scroll active item into view
  useEffect(() => {
    if (listRef.current) {
      const activeEl = listRef.current.querySelector(`[data-index="${selectedIndex}"]`);
      if (activeEl) {
        activeEl.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [selectedIndex]);

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-start justify-center pt-16 sm:pt-20 px-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-150"
      onClick={onClose}
    >
      <div 
        className="w-full max-w-2xl bg-white dark:bg-slate-900 rounded-xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col max-h-[75vh] animate-in zoom-in-95 duration-150"
        onClick={e => e.stopPropagation()}
      >
        {/* Header Search Input */}
        <div className="flex items-center gap-3.5 px-4 py-3.5 border-b border-slate-200 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-900/90">
          <Search size={18} className="text-[#00E5FF] shrink-0 drop-shadow-[0_0_6px_rgba(0,229,255,0.4)]" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={e => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            onKeyDown={handleKeyDown}
            placeholder="Search solicitations, awardees, programs, technologies, reports, or modules..."
            className="w-full text-[13.5px] bg-transparent text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 outline-none font-medium"
          />
          {(oppsLoading || awardsLoading) && (
            <Loader2 size={16} className="animate-spin text-[#00E5FF] shrink-0" />
          )}
          {query && (
            <button 
              onClick={() => { setQuery(''); setDebouncedQuery(''); }} 
              className="p-1 rounded-md text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-200/60 dark:hover:bg-slate-800 transition-colors"
            >
              <X size={14} />
            </button>
          )}
          <button 
            onClick={onClose} 
            className="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-slate-200/70 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-300 dark:border-slate-700 hover:bg-slate-300/80 transition-colors"
          >
            ESC
          </button>
        </div>

        {/* Results Container */}
        <div ref={listRef} className="flex-1 overflow-y-auto p-2 space-y-1">
          {results.length === 0 ? (
            <div className="py-12 text-center text-slate-400 dark:text-slate-500 text-sm">
              No results found for &ldquo;<span className="font-medium text-slate-700 dark:text-slate-300">{query}</span>&rdquo;
            </div>
          ) : (
            results.map((item, idx) => {
              const isSelected = idx === selectedIndex;
              const Icon = item.icon || (
                item.type === 'opp' ? FileSearch :
                item.type === 'award' ? Trophy :
                item.type === 'program' ? Layers : ArrowRight
              );

              return (
                <div
                  key={item.id}
                  data-index={idx}
                  onClick={() => {
                    if (item.to === '__splash__') {
                      onClose();
                      window.dispatchEvent(new CustomEvent('replay-splash-screen'));
                    } else {
                      navigate(item.to);
                      onClose();
                    }
                  }}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={clsx(
                    'flex items-center justify-between gap-3 px-3 py-2 rounded-lg cursor-pointer transition-all border',
                    isSelected 
                      ? 'bg-slate-900 text-white border-cyan-400/50 shadow-glow-cyan-sm' 
                      : 'text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/40 border-transparent'
                  )}
                >
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    <div className={clsx(
                      'w-7 h-7 rounded-md flex items-center justify-center shrink-0 transition-colors',
                      isSelected ? 'bg-cyan-500/20 text-[#00E5FF]' : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400'
                    )}>
                      <Icon size={14} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <span className={clsx(
                          'text-[13px] font-semibold truncate',
                          isSelected ? 'text-white' : 'text-slate-800 dark:text-slate-200'
                        )}>
                          {item.title}
                        </span>
                        {item.badge && (
                          <span className={clsx(
                            'text-[9.5px] font-mono px-1.5 py-0.2 rounded shrink-0 border',
                            isSelected 
                              ? 'bg-cyan-400/20 text-cyan-300 border-cyan-400/40' 
                              : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700'
                          )}>
                            {item.badge}
                          </span>
                        )}
                      </div>
                      <div className={clsx(
                        'text-[11px] truncate mt-0.5',
                        isSelected ? 'text-slate-300' : 'text-slate-500 dark:text-slate-400'
                      )}>
                        {item.subtitle}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <span className={clsx(
                      "text-[9.5px] font-mono uppercase tracking-wider",
                      isSelected ? "text-[#00F5A0] font-bold" : "text-slate-400 dark:text-slate-500"
                    )}>
                      {item.category}
                    </span>
                    <ChevronRight size={13} className={isSelected ? 'text-[#00E5FF]' : 'text-slate-300 dark:text-slate-600'} />
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer Shortcut Guide */}
        <div className="px-4 py-2.5 bg-slate-50 dark:bg-slate-900/90 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 rounded bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 font-mono text-[9.5px]">↑</kbd>
              <kbd className="px-1.5 py-0.5 rounded bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 font-mono text-[9.5px]">↓</kbd>
              <span>Navigate</span>
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 rounded bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 font-mono text-[9.5px]">↵</kbd>
              <span>Select</span>
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 rounded bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 font-mono text-[9.5px]">ESC</kbd>
              <span>Close</span>
            </span>
          </div>
          <div className="font-mono text-slate-500 dark:text-slate-400 text-[10.5px] hidden sm:flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block" />
            <span>56,413 Awards · $104.16B Tracked</span>
          </div>
        </div>
      </div>
    </div>
  );
}
