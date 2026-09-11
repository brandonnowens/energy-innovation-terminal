import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import {
  Search, FileSearch, Layers, Trophy, Network, GitMerge, TrendingUp,
  FileText, Database, Building2, ArrowRight, X, Loader2,
  ExternalLink, Globe, MapPin, Zap, ChevronRight, FileEdit, Scale, Lightbulb, BookUser, BookOpen, ShieldCheck, Compass, Newspaper, Terminal,
  Sliders, MessageSquare, Activity
} from 'lucide-react';
import clsx from 'clsx';
import { OrgLogo } from './OrgLogo';
import { useNyserda } from '../context/NyserdaContext';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

const STATIC_ACTIONS = [
  { id: 'persona-investors', label: 'Switch Front Door: Investors & Strategists', sub: 'Curated view spotlighting Daily Digest, Capital Flows (Sankey), Venture & IP, and Strategic Reports', to: '__persona_investor__', icon: TrendingUp, category: 'Front Doors' },
  { id: 'persona-innovators', label: 'Switch Front Door: Innovators & Grant Seekers', sub: 'Curated view spotlighting Match Engine, Solicitations, and Application Studio', to: '__persona_innovator__', icon: Lightbulb, category: 'Front Doors' },
  { id: 'persona-all', label: 'Switch Front Door: All Modules (Master View)', sub: 'Display all modules, directories, intelligence suites, and reference databases', to: '__persona_all__', icon: Layers, category: 'Front Doors' },
  { id: 'nav-digest', label: 'Daily Digest', sub: 'Morning intelligence briefing analyzing new solicitations, deadlines, and venture wire', to: '/digest', icon: Newspaper, category: 'Opportunities' },
  { id: 'nav-chat', label: 'Strategic Advisory', sub: 'Interactive research query tool with direct access to all 56k+ awards & 5.7k+ opportunities', to: '/chat', icon: MessageSquare, category: 'Research' },
  { id: 'nav-match', label: 'Match Engine', sub: 'Eligibility and capital stacking analysis engine', to: '/analyze', icon: Sliders, category: 'Opportunities' },
  { id: 'nav-proposals', label: 'Application Studio', sub: 'Statement of project objectives, scoring review, and proposal builder', to: '/proposals', icon: FileEdit, category: 'Opportunities' },
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
  { id: 'nav-updates', label: 'Feeds', sub: 'Real-time telemetry and audit feed of detected dataset updates', to: '/updates', icon: Activity, category: 'Data & Audit' },
  { id: 'nav-sources', label: 'Provenance', sub: 'Source authority ranking, audit metrics, and database status', to: '/sources', icon: Database, category: 'Data & Audit' },
  { id: 'nav-quick-start', label: 'Platform Quick Start Guide & Tour', sub: 'Interactive guide explaining core pillars, recommended workflows, and shortcuts', to: '__quick_start_guide__', icon: Compass, category: 'System' },
  { id: 'nav-api-docs', label: 'Developers & API Docs', sub: 'Interactive OpenAPI docs, developer tools, and Python/cURL endpoints', to: '__api_modal__', icon: Terminal, category: 'Data & Audit' },
  { id: 'nav-splash', label: 'Replay Splash', sub: 'Interactive launch sequence and telemetry indexing animation', to: '__splash__', icon: Compass, category: 'System' },
];


export function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [activeDomainFilter, setActiveDomainFilter] = useState<string>('all');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const { includeNyserda, isNyserda, isNyserdaAgency } = useNyserda();

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQuery(query.trim());
    }, 180);
    return () => clearTimeout(handler);
  }, [query]);

  // Focus input when opened
  useEffect(() => {
    let timer: any;
    if (isOpen) {
      timer = setTimeout(() => inputRef.current?.focus(), 50);
      setSelectedIndex(0);
      setActiveDomainFilter('all');
    } else {
      setQuery('');
      setDebouncedQuery('');
    }
    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [isOpen]);

  // Universal Database Search Query across all 13 database domains
  const { data: searchData, isLoading: isSearchLoading } = useQuery({
    queryKey: ['cmd-palette-universal-search', debouncedQuery, includeNyserda],
    queryFn: () => api.universalSearch(debouncedQuery, { exclude_nyserda: !includeNyserda, limit_per_domain: 8 }),
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
  const { results, domainCounts, totalMatches } = useMemo(() => {
    if (!debouncedQuery) {
      const items = STATIC_ACTIONS.map(action => ({
        type: 'action' as const,
        id: action.id,
        title: action.label,
        subtitle: action.sub,
        category: action.category,
        domainKey: 'actions',
        badge: undefined as string | undefined,
        badgeColor: undefined as string | undefined,
        icon: action.icon,
        to: action.to,
      }));
      return { results: items, domainCounts: {}, totalMatches: items.length };
    }

    const items: Array<{
      type: 'action' | 'award' | 'recipient' | 'opp' | 'program' | 'org' | 'contact' | 'patent' | 'venture' | 'tech' | 'policy' | 'docket' | 'interconn' | 'lab' | 'news';
      id: string;
      title: string;
      subtitle: string;
      category: string;
      domainKey: string;
      badge?: string;
      badgeColor?: string;
      to: string;
      icon?: any;
    }> = [];

    const q = debouncedQuery.toLowerCase();

    // 1. Static Actions & Modules
    STATIC_ACTIONS.forEach(a => {
      if (a.label.toLowerCase().includes(q) || a.sub.toLowerCase().includes(q)) {
        items.push({
          type: 'action',
          id: a.id,
          title: a.label,
          subtitle: a.sub,
          category: 'Quick Actions',
          domainKey: 'actions',
          icon: a.icon,
          to: a.to,
        });
      }
    });

    // 2. Programs
    matchingPrograms.forEach((prog: any) => {
      items.push({
        type: 'program',
        id: `prog-${prog.id}`,
        title: prog.name,
        subtitle: `${prog.agency || 'Program'} · ${prog.type || 'Innovation Initiative'}`,
        category: 'Programs & Portfolios',
        domainKey: 'programs',
        badge: prog.agency,
        to: `/programs`,
        icon: Layers,
      });
    });

    const sResults = searchData?.results;
    const counts = searchData?.counts || {};

    if (sResults) {
      // 3. Awardee Companies & Startups (Recipients)
      (sResults.recipients || []).forEach(r => {
        items.push({
          type: 'recipient',
          id: `rec-${r.id}`,
          title: r.name,
          subtitle: `${r.recipient_type || 'Company'} · ${r.total_funding_formatted} tracked funding · ${r.city ? `${r.city}, ${r.state || 'US'}` : (r.state || 'US')}`,
          category: 'Companies & Scaleups',
          domainKey: 'recipients',
          badge: r.total_funding_formatted !== '$0' ? r.total_funding_formatted : 'Awardee',
          badgeColor: 'emerald',
          to: r.to || `/awards?search=${encodeURIComponent(r.name)}`,
          icon: Building2,
        });
      });

      // 4. Past Awards & Precedents
      (sResults.awards || []).forEach(aw => {
        items.push({
          type: 'award',
          id: `aw-${aw.id}`,
          title: `${aw.recipient_name} · ${aw.project_title}`,
          subtitle: `${aw.agency} · ${aw.award_amount_formatted} ${aw.year ? `(${aw.year})` : ''} · ${aw.city ? `${aw.city}, ${aw.state}` : (aw.state || 'US')}`,
          category: 'Past Awards',
          domainKey: 'awards',
          badge: aw.agency,
          badgeColor: 'cyan',
          to: aw.to || `/awards?search=${encodeURIComponent(debouncedQuery)}`,
          icon: Trophy,
        });
      });

      // 5. Funding Solicitations & FOAs
      (sResults.opportunities || []).forEach(opp => {
        items.push({
          type: 'opp',
          id: `opp-${opp.id}`,
          title: `${opp.solicitation_number} · ${opp.name}`,
          subtitle: `${opp.agency} · ${opp.status} · ${opp.total_funding_formatted} total · Due ${opp.deadline || 'Open'}`,
          category: 'Funding Solicitations',
          domainKey: 'opportunities',
          badge: opp.agency,
          badgeColor: 'amber',
          to: opp.to || `/opportunities/${opp.id}`,
          icon: FileSearch,
        });
      });

      // 6. Patents & Bayh-Dole IP
      (sResults.patents || []).forEach(pat => {
        items.push({
          type: 'patent',
          id: `pat-${pat.id}`,
          title: `${pat.patent_number}: ${pat.title}`,
          subtitle: `${pat.assignee_name || 'Assignee'} · ${pat.technology_area || 'Energy Tech'}${pat.grant_date ? ` · Granted ${pat.grant_date}` : ''}`,
          category: 'Bayh-Dole Patents',
          domainKey: 'patents',
          badge: 'USPTO Patent',
          badgeColor: 'purple',
          to: pat.to || `/venture-patents`,
          icon: Lightbulb,
        });
      });

      // 7. Key Contacts & PIs
      (sResults.contacts || []).forEach(c => {
        items.push({
          type: 'contact',
          id: `con-${c.id}`,
          title: `${c.name_display}${c.title ? ` · ${c.title}` : ''}`,
          subtitle: `${c.institution_name || 'Organization'} · ${c.technology_area || 'Energy Innovation'}${c.email ? ` · ${c.email}` : ''}`,
          category: 'Contacts & Experts',
          domainKey: 'contacts',
          badge: c.role_type ? c.role_type.replace(/_/g, ' ') : 'Expert',
          badgeColor: 'blue',
          to: c.to || `/contacts?search=${encodeURIComponent(c.name_display)}`,
          icon: BookUser,
        });
      });

      // 8. Organizations & Agencies
      (sResults.organizations || []).forEach(org => {
        items.push({
          type: 'org',
          id: `org-${org.id}`,
          title: org.name,
          subtitle: `${org.org_type || 'Organization'} · ${org.city ? `${org.city}, ` : ''}${org.state || 'US'}${org.domain ? ` · ${org.domain}` : ''}`,
          category: 'Organizations & Agencies',
          domainKey: 'organizations',
          badge: org.org_type || 'Agency',
          badgeColor: 'slate',
          to: org.to || `/organizations`,
          icon: Building2,
        });
      });

      // 9. Technologies Reference
      (sResults.technologies || []).forEach(tech => {
        items.push({
          type: 'tech',
          id: `tech-${tech.id}`,
          title: tech.name,
          subtitle: `${tech.category} · ${tech.description || 'Frontier Clean Energy Architecture'}`,
          category: 'Technology Reference',
          domainKey: 'technologies',
          badge: tech.category,
          badgeColor: 'teal',
          to: tech.to || `/technologies`,
          icon: BookOpen,
        });
      });

      // 10. Venture Deals & SEC Form D
      (sResults.venture || []).forEach(v => {
        items.push({
          type: 'venture',
          id: `ven-${v.id}`,
          title: `${v.company_name} · Private Offering`,
          subtitle: `${v.primary_industry || 'Clean Tech'} · ${v.total_offering_formatted} Offering${v.filing_date ? ` · Filed ${v.filing_date}` : ''}`,
          category: 'Venture & Private Offerings',
          domainKey: 'venture',
          badge: v.total_offering_formatted,
          badgeColor: 'emerald',
          to: v.to || `/venture-patents`,
          icon: TrendingUp,
        });
      });

      // 11. Policies & Tax Credits
      (sResults.policies || []).forEach(pol => {
        items.push({
          type: 'policy',
          id: `pol-${pol.id}`,
          title: `${pol.code_identifier}: ${pol.title}`,
          subtitle: `${pol.category.replace(/_/g, ' ')} · ${pol.jurisdiction_state || 'Federal'} · ${pol.executive_summary?.slice(0, 90)}...`,
          category: 'Policies & Tax Credits',
          domainKey: 'policies',
          badge: pol.code_identifier,
          badgeColor: 'indigo',
          to: pol.to || `/policies`,
          icon: ShieldCheck,
        });
      });

      // 12. PUC Regulatory Dockets
      (sResults.dockets || []).forEach(doc => {
        items.push({
          type: 'docket',
          id: `doc-${doc.id}`,
          title: `${doc.docket_number}: ${doc.title}`,
          subtitle: `${doc.commission} · ${doc.topic_category.replace(/_/g, ' ')} · ${doc.jurisdiction_state || 'State'}`,
          category: 'Regulatory Dockets',
          domainKey: 'dockets',
          badge: doc.commission,
          badgeColor: 'orange',
          to: doc.to || `/dockets`,
          icon: Scale,
        });
      });

      // 13. Interconnection Queues
      (sResults.interconnections || []).forEach(iq => {
        items.push({
          type: 'interconn',
          id: `iq-${iq.id}`,
          title: `${iq.project_name}${iq.capacity_mw ? ` (${iq.capacity_mw} MW)` : ''}`,
          subtitle: `${iq.developer || 'Developer'} · ${iq.fuel_type || 'Grid Project'} · ${iq.iso_rto || 'ISO'} · ${iq.county ? `${iq.county}, ${iq.state}` : (iq.state || '')}`,
          category: 'Grid Interconnections',
          domainKey: 'interconnections',
          badge: iq.iso_rto || 'Grid',
          badgeColor: 'cyan',
          to: iq.to || `/awards`,
          icon: Zap,
        });
      });

      // 14. National Lab Facilities
      (sResults.labs || []).forEach(lab => {
        items.push({
          type: 'lab',
          id: `lab-${lab.id}`,
          title: `${lab.name} (${lab.parent_lab})`,
          subtitle: `${lab.facility_type || 'Testbed'} · ${lab.focus_areas ? lab.focus_areas.slice(0, 90) : ''} · ${lab.city ? `${lab.city}, ${lab.state}` : ''}`,
          category: 'National Lab Testbeds',
          domainKey: 'labs',
          badge: lab.parent_lab,
          badgeColor: 'teal',
          to: lab.to || `/network`,
          icon: Network,
        });
      });

      // 15. News Wire
      (sResults.news || []).forEach(n => {
        items.push({
          type: 'news',
          id: `news-${n.id}`,
          title: n.title,
          subtitle: `${n.source_domain || 'News Wire'}${n.published_at ? ` · ${n.published_at}` : ''} · ${n.summary ? n.summary.slice(0, 90) : ''}`,
          category: 'Clean Tech News',
          domainKey: 'news',
          badge: 'News',
          badgeColor: 'slate',
          to: n.to || `/updates`,
          icon: Newspaper,
        });
      });
    }

    const filteredItems = activeDomainFilter === 'all'
      ? items
      : items.filter(i => i.domainKey === activeDomainFilter || i.type === 'action');

    const totalCount = (searchData?.total_matches ?? items.length);

    return { results: filteredItems, domainCounts: counts, totalMatches: totalCount };
  }, [debouncedQuery, searchData, matchingPrograms, activeDomainFilter]);

  const handleSelectItem = (item: any) => {
    if (!item) return;
    if (item.to === '__quick_start_guide__') {
      onClose();
      window.dispatchEvent(new CustomEvent('open-quick-start-guide'));
    } else if (item.to === '__splash__') {
      onClose();
      window.dispatchEvent(new CustomEvent('replay-splash-screen'));
    } else if (item.to === '__api_modal__') {
      onClose();
      window.dispatchEvent(new CustomEvent('open-api-docs-modal'));
    } else if (item.to === '__persona_investor__') {
      onClose();
      window.dispatchEvent(new CustomEvent('switch-persona', { detail: 'investor' }));
    } else if (item.to === '__persona_innovator__') {
      onClose();
      window.dispatchEvent(new CustomEvent('switch-persona', { detail: 'innovator' }));
    } else if (item.to === '__persona_all__') {
      onClose();
      window.dispatchEvent(new CustomEvent('switch-persona', { detail: 'all' }));
    } else if (item.to.startsWith('http')) {
      window.open(item.to, '_blank');
      onClose();
    } else {
      navigate(item.to);
      onClose();
    }
  };

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
        handleSelectItem(item);
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

  // Domain badge filter list with counts
  const availableFilterTabs = useMemo(() => {
    if (!debouncedQuery || !searchData?.counts) return [];
    const tabs: Array<{ key: string; label: string; count: number }> = [];
    const c = searchData.counts;
    
    if (searchData.total_matches > 0) {
      tabs.push({ key: 'all', label: 'All Domains', count: searchData.total_matches });
    }
    if ((c.awards || 0) > 0) tabs.push({ key: 'awards', label: 'Awards', count: c.awards });
    if ((c.recipients || 0) > 0) tabs.push({ key: 'recipients', label: 'Companies', count: c.recipients });
    if ((c.opportunities || 0) > 0) tabs.push({ key: 'opportunities', label: 'Solicitations', count: c.opportunities });
    if ((c.patents || 0) > 0) tabs.push({ key: 'patents', label: 'Patents', count: c.patents });
    if ((c.contacts || 0) > 0) tabs.push({ key: 'contacts', label: 'Contacts', count: c.contacts });
    if ((c.venture || 0) > 0) tabs.push({ key: 'venture', label: 'Venture & SEC', count: c.venture });
    if ((c.technologies || 0) > 0) tabs.push({ key: 'technologies', label: 'Technologies', count: c.technologies });
    if ((c.policies || 0) > 0) tabs.push({ key: 'policies', label: 'Policies', count: c.policies });
    if ((c.dockets || 0) > 0) tabs.push({ key: 'dockets', label: 'Dockets', count: c.dockets });
    if ((c.organizations || 0) > 0) tabs.push({ key: 'organizations', label: 'Agencies', count: c.organizations });
    if ((c.interconnections || 0) > 0) tabs.push({ key: 'interconnections', label: 'Grid Queues', count: c.interconnections });
    if ((c.labs || 0) > 0) tabs.push({ key: 'labs', label: 'National Labs', count: c.labs });
    if ((c.news || 0) > 0) tabs.push({ key: 'news', label: 'News Wire', count: c.news });

    return tabs;
  }, [debouncedQuery, searchData]);

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-start justify-center pt-14 sm:pt-16 px-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-150"
      onClick={onClose}
    >
      <div 
        className="w-full max-w-3xl bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800/90 overflow-hidden flex flex-col max-h-[82vh] animate-in zoom-in-95 duration-150"
        onClick={e => e.stopPropagation()}
      >
        {/* Header Search Input */}
        <div className="flex items-center gap-3 px-4 py-3.5 border-b border-slate-200 dark:border-slate-800 bg-slate-50/90 dark:bg-slate-900/95">
          <Search size={19} className="text-[#00E5FF] shrink-0 drop-shadow-[0_0_8px_rgba(0,229,255,0.4)]" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={e => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            onKeyDown={handleKeyDown}
            placeholder="Search all 56k+ awards, awardees (e.g. Ecolectro), solicitations, patents, contacts, technologies..."
            className="w-full text-[14px] bg-transparent text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 outline-none font-medium"
          />
          {isSearchLoading && (
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-cyan-500/10 text-[#00E5FF] text-[11px] font-mono shrink-0">
              <Loader2 size={13} className="animate-spin text-[#00E5FF]" />
              <span>Searching...</span>
            </div>
          )}
          {query && !isSearchLoading && (
            <button 
              onClick={() => { setQuery(''); setDebouncedQuery(''); setActiveDomainFilter('all'); }} 
              className="p-1 rounded-md text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-200/60 dark:hover:bg-slate-800 transition-colors"
            >
              <X size={15} />
            </button>
          )}
          <button 
            onClick={onClose} 
            className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-slate-200/70 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-300 dark:border-slate-700 hover:bg-slate-300/80 transition-colors"
          >
            ESC
          </button>
        </div>

        {/* Category Domain Filter Tabs (when active search returns counts) */}
        {availableFilterTabs.length > 1 && (
          <div className="flex items-center gap-1.5 px-3 py-2 border-b border-slate-200/80 dark:border-slate-800/80 bg-slate-100/60 dark:bg-slate-950/40 overflow-x-auto no-scrollbar">
            {availableFilterTabs.map(tab => {
              const isActive = activeDomainFilter === tab.key;
              return (
                <button
                  key={tab.key}
                  onClick={() => {
                    setActiveDomainFilter(tab.key);
                    setSelectedIndex(0);
                  }}
                  className={clsx(
                    'px-2.5 py-1 rounded-lg text-[11.5px] font-medium transition-all shrink-0 flex items-center gap-1.5 border',
                    isActive 
                      ? 'bg-cyan-500/20 text-[#00E5FF] border-cyan-400/40 font-semibold shadow-sm'
                      : 'bg-white/60 dark:bg-slate-900/60 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-800 hover:bg-white dark:hover:bg-slate-850'
                  )}
                >
                  <span>{tab.label}</span>
                  <span className={clsx(
                    'text-[10px] font-mono px-1.5 py-0.2 rounded-full',
                    isActive ? 'bg-[#00E5FF] text-slate-950 font-bold' : 'bg-slate-200 dark:bg-slate-800 text-slate-500 dark:text-slate-400'
                  )}>
                    {tab.count}
                  </span>
                </button>
              );
            })}
          </div>
        )}

        {/* Results Container */}
        <div ref={listRef} className="flex-1 overflow-y-auto p-2.5 space-y-1">
          {results.length === 0 ? (
            <div className="py-14 text-center text-slate-400 dark:text-slate-500 text-sm flex flex-col items-center justify-center gap-2">
              <Search size={28} className="text-slate-300 dark:text-slate-600" />
              <div>
                No matches found across any database domain for &ldquo;<span className="font-semibold text-slate-700 dark:text-slate-300">{query}</span>&rdquo;
              </div>
              <p className="text-[12px] text-slate-400">
                Try searching for company names (e.g. &ldquo;Ecolectro&rdquo;, &ldquo;Form Energy&rdquo;), agencies (&ldquo;DOE&rdquo;, &ldquo;NSF&rdquo;), or technologies (&ldquo;Hydrogen&rdquo;, &ldquo;Battery&rdquo;).
              </p>
            </div>
          ) : (
            results.map((item, idx) => {
              const isSelected = idx === selectedIndex;
              const Icon = item.icon || (
                item.type === 'opp' ? FileSearch :
                item.type === 'award' ? Trophy :
                item.type === 'recipient' ? Building2 :
                item.type === 'patent' ? Lightbulb :
                item.type === 'contact' ? BookUser :
                item.type === 'tech' ? BookOpen :
                item.type === 'program' ? Layers : ArrowRight
              );

              return (
                <div
                  key={item.id}
                  data-index={idx}
                  onClick={() => handleSelectItem(item)}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={clsx(
                    'flex items-center justify-between gap-3 px-3.5 py-2.5 rounded-xl cursor-pointer transition-all border',
                    isSelected 
                      ? 'bg-slate-900 text-white border-cyan-400/60 shadow-[0_0_15px_rgba(0,229,255,0.15)] ring-1 ring-cyan-400/30' 
                      : 'text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/50 border-transparent'
                  )}
                >
                  <div className="flex items-center gap-3.5 min-w-0 flex-1">
                    <div className={clsx(
                      'w-8 h-8 rounded-lg flex items-center justify-center shrink-0 transition-colors border',
                      isSelected 
                        ? 'bg-cyan-500/20 text-[#00E5FF] border-cyan-400/40 shadow-glow-cyan-sm' 
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-700/60'
                    )}>
                      <Icon size={15} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <span className={clsx(
                          'text-[13.5px] font-semibold truncate',
                          isSelected ? 'text-white' : 'text-slate-800 dark:text-slate-200'
                        )}>
                          {item.title}
                        </span>
                        {item.badge && (
                          <span className={clsx(
                            'text-[10px] font-mono font-medium px-2 py-0.5 rounded-md shrink-0 border',
                            isSelected 
                              ? 'bg-cyan-400/20 text-cyan-300 border-cyan-400/40' 
                              : item.badgeColor === 'emerald'
                              ? 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800'
                              : item.badgeColor === 'amber'
                              ? 'bg-amber-50 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800'
                              : item.badgeColor === 'purple'
                              ? 'bg-purple-50 dark:bg-purple-950/50 text-purple-700 dark:text-purple-300 border-purple-200 dark:border-purple-800'
                              : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700'
                          )}>
                            {item.badge}
                          </span>
                        )}
                      </div>
                      <div className={clsx(
                        'text-[11.5px] truncate mt-0.5 leading-relaxed',
                        isSelected ? 'text-slate-300' : 'text-slate-500 dark:text-slate-400'
                      )}>
                        {item.subtitle}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2.5 shrink-0 pl-2">
                    <span className={clsx(
                      "text-[10px] font-mono uppercase tracking-wider hidden sm:inline-block px-2 py-0.5 rounded",
                      isSelected 
                        ? "bg-[#00F5A0]/20 text-[#00F5A0] font-bold border border-[#00F5A0]/30" 
                        : "bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-500"
                    )}>
                      {item.category}
                    </span>
                    <ChevronRight size={14} className={isSelected ? 'text-[#00E5FF]' : 'text-slate-300 dark:text-slate-600'} />
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer Shortcut Guide & Database Telemetry */}
        <div className="px-4 py-2.5 bg-slate-50 dark:bg-slate-900/95 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
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
          <div className="font-mono text-slate-500 dark:text-slate-400 text-[10.5px] hidden sm:flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block animate-pulse" />
            <span>Universal Search: 13 Domains · 56k+ Awards · $104.16B Tracked</span>
          </div>
        </div>
      </div>
    </div>
  );
}
