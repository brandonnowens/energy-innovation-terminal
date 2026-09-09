import React, { useState, useEffect, useMemo } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import {
  FileSearch, Layers, Building2, Trophy, Network,
  TrendingUp, Database, GitMerge, FileText, Search, ShieldCheck,
  Zap, Command, FileEdit, Scale, Lightbulb, Clock, Activity, BookUser, BookOpen,
  ChevronDown, ChevronRight, ChevronsUpDown, Mail, Compass, Radio, Menu, X, Newspaper, Terminal,
  Sliders, MessageSquare, Target
} from 'lucide-react';

import clsx from 'clsx';
import { EnergyInnovationTerminalLogo } from './EnergyInnovationTerminalLogo';
import { CommandPalette } from './CommandPalette';
import { UserMenu } from './UserMenu';
import { AuthModal } from './AuthModal';
import { MembershipModal } from './MembershipModal';
import { AccountModal } from './AccountModal';
import { ThemeToggle } from './ThemeToggle';
import { NyserdaToggle } from './NyserdaToggle';
import { BrandonSignatureModal } from './BrandonSignatureModal';
import { LegalComplianceModal } from './LegalComplianceModal';
import { ApiDocsModal } from './ApiDocsModal';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { useNyserda } from '../context/NyserdaContext';

export default function Layout() {
  const { user } = useAuth();
  const { theme } = useTheme();
  const { includeNyserda } = useNyserda();
  const isDark = theme === 'dark';
  const isAdmin = Boolean(user && (user.role === 'admin' || user.email?.toLowerCase() === 'bowens@aixenergy.io'));
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [signatureModalOpen, setSignatureModalOpen] = useState(false);
  const [legalModalOpen, setLegalModalOpen] = useState(false);
  const [apiModalOpen, setApiModalOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  // Persona Front Door Selection: 'investor' | 'innovator' | 'all'
  const [persona, setPersona] = useState<'investor' | 'innovator' | 'all'>(() => {
    try {
      const saved = localStorage.getItem('energy_terminal_persona_v1');
      if (saved === 'investor' || saved === 'innovator' || saved === 'all') return saved;
    } catch {}
    return 'investor';
  });

  const handlePersonaChange = (newPersona: 'investor' | 'innovator' | 'all') => {
    setPersona(newPersona);
    try {
      localStorage.setItem('energy_terminal_persona_v1', newPersona);
    } catch {}
    window.dispatchEvent(new CustomEvent('persona-changed', { detail: newPersona }));

    // Contextual front door routing: if switching persona while on a primary landing page
    if (newPersona === 'innovator' && (location.pathname === '/' || location.pathname === '/digest' || location.pathname === '/daily-digest')) {
      navigate('/analyze');
    } else if (newPersona === 'investor' && (location.pathname === '/analyze' || location.pathname === '/match')) {
      navigate('/digest');
    }
  };

  // Dynamic home destination matching active persona
  const homeRoute = persona === 'innovator' ? '/analyze' : '/';

  // Comprehensive active route matcher ensuring zero de-synchronization across aliases & deep links
  const isItemActive = (itemTo: string): boolean => {
    if (itemTo === '__api_modal__') return apiModalOpen;
    const p = location.pathname;
    if (itemTo === '/' || itemTo === '/digest') {
      return p === '/' || p === '/digest' || p.startsWith('/digest') || p.startsWith('/daily-digest');
    }
    if (itemTo === '/analyze') {
      return p === '/analyze' || p.startsWith('/analyze') || p === '/match' || p.startsWith('/match');
    }
    if (itemTo === '/radar') {
      return p === '/radar' || p.startsWith('/radar') || p.startsWith('/forecasting');
    }
    if (itemTo === '/opportunities') {
      return p === '/opportunities' || p.startsWith('/opportunities');
    }
    if (itemTo === '/proposals') {
      return p === '/proposals' || p.startsWith('/proposals');
    }
    if (itemTo === '/awards') {
      return p === '/awards' || p.startsWith('/awards') || p.startsWith('/recipients');
    }
    if (itemTo === '/venture-patents') {
      return p === '/venture-patents' || p.startsWith('/venture-patents');
    }
    if (itemTo === '/results') {
      return p === '/results' || p.startsWith('/results');
    }
    if (itemTo === '/organizations') {
      return p === '/organizations' || p.startsWith('/organizations') || p.startsWith('/agencies');
    }
    if (itemTo === '/programs') {
      return p === '/programs' || p.startsWith('/programs');
    }
    if (itemTo === '/contacts') {
      return p === '/contacts' || p.startsWith('/contacts');
    }
    if (itemTo === '/network') {
      return p === '/network' || p.startsWith('/network');
    }
    if (itemTo === '/strategy') {
      return p === '/strategy' || p.startsWith('/strategy');
    }
    if (itemTo === '/sankey') {
      return p === '/sankey' || p.startsWith('/sankey');
    }
    if (itemTo === '/trends') {
      return p === '/trends' || p.startsWith('/trends');
    }
    if (itemTo === '/reports') {
      return p === '/reports' || p.startsWith('/reports');
    }
    if (itemTo === '/technologies') {
      return p === '/technologies' || p.startsWith('/technologies') || p.startsWith('/tech-reference') || p.startsWith('/tech-hub');
    }
    if (itemTo === '/policies') {
      return p === '/policies' || p.startsWith('/policies') || p.startsWith('/policy-reference');
    }
    if (itemTo === '/dockets') {
      return p === '/dockets' || p.startsWith('/dockets');
    }
    if (itemTo === '/updates') {
      return p === '/updates' || p.startsWith('/updates');
    }
    if (itemTo === '/sources') {
      return p === '/sources' || p.startsWith('/sources');
    }
    if (itemTo === '/chat') {
      return p === '/chat' || p.startsWith('/chat');
    }
    return p === itemTo || p.startsWith(itemTo);
  };

  // Close mobile drawer upon navigation
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  // Listen for persona changes from Command Palette or other components
  useEffect(() => {
    const onSwitchPersona = (e: CustomEvent) => {
      if (e.detail && ['investor', 'innovator', 'all'].includes(e.detail)) {
        handlePersonaChange(e.detail);
      }
    };
    window.addEventListener('switch-persona' as any, onSwitchPersona);
    return () => window.removeEventListener('switch-persona' as any, onSwitchPersona);
  }, []);

  // Collapsed state for navigation sections
  const [collapsedSections, setCollapsedSections] = useState<Record<string, boolean>>(() => {
    try {
      const saved = localStorage.getItem('energy_terminal_nav_collapsed_v6');
      if (saved) return JSON.parse(saved);
    } catch {
      // ignore
    }
    return {
      'Opportunities & Studio': false,
      'Awards & Precedents': false,
      'Directories & Ecosystem': true,
      'Market Intelligence': false,
      'Regulatory & References': true,
      'Data & Audit': true,
      'Grant Seeking Suite': false,
      'Ecosystem & Partners': false,
      'Intelligence & Reference': true,
      'Due Diligence & Benchmarks': false,
      'Project & Deal Sourcing': false,
      'Data & Developer API': true,
    };
  });

  const toggleSection = (sectionTitle: string) => {
    setCollapsedSections(prev => {
      const updated = { ...prev, [sectionTitle]: !prev[sectionTitle] };
      try {
        localStorage.setItem('energy_terminal_nav_collapsed_v6', JSON.stringify(updated));
      } catch (e) {
        // ignore
      }
      return updated;
    });
  };

  const toggleAll = (collapse: boolean) => {
    const updated: Record<string, boolean> = {};
    navSections.forEach(s => {
      updated[s.title] = collapse;
    });
    setCollapsedSections(updated);
    try {
      localStorage.setItem('energy_terminal_nav_collapsed_v6', JSON.stringify(updated));
    } catch (e) {
      // ignore
    }
  };

  // Global key listener for Ctrl+K, Cmd+K, or /
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setCommandPaletteOpen(prev => !prev);
      } else if (e.key === '/' && !['INPUT', 'TEXTAREA', 'SELECT'].includes((e.target as HTMLElement)?.tagName)) {
        e.preventDefault();
        setCommandPaletteOpen(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    const handleOpenApiDocs = () => setApiModalOpen(true);
    window.addEventListener('open-api-docs-modal', handleOpenApiDocs);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('open-api-docs-modal', handleOpenApiDocs);
    };
  }, []);

  interface NavItem {
    to: string;
    icon: React.ComponentType<{ size?: number; className?: string; strokeWidth?: number }>;
    label: string;
    badge?: string;
  }

  interface NavSection {
    title: string;
    items: NavItem[];
  }

  const navSections: NavSection[] = useMemo(() => {
    if (persona === 'innovator') {
      return [
        {
          title: 'Grant Seeking Suite',
          items: [
            { to: '/analyze', icon: Sliders, label: 'Match & Sponsoring' },
            { to: '/opportunities', icon: FileSearch, label: 'Solicitations (5,757)' },
            { to: '/proposals', icon: FileEdit, label: 'Application Studio' },
            { to: '/radar', icon: Radio, label: 'Predictive Radar' },
          ]
        },
        {
          title: 'Ecosystem & Partners',
          items: [
            { to: '/contacts', icon: BookUser, label: 'Key Contacts & PIs' },
            { to: '/organizations', icon: Building2, label: 'Funding Organizations' },
            { to: '/network', icon: Network, label: 'Teaming & Network' },
            { to: '/programs', icon: Layers, label: 'Programs (143)' },
          ]
        },
        {
          title: 'Intelligence & Reference',
          items: [
            { to: '/digest', icon: Newspaper, label: 'Daily Digest' },
            { to: '/policies', icon: ShieldCheck, label: 'IRA §45/§48 Credits' },
            { to: '/technologies', icon: BookOpen, label: 'Technology Reference' },
            { to: '/awards', icon: Trophy, label: 'Award Precedents' },
          ]
        },
        {
          title: 'Data & Developer API',
          items: [
            { to: '/updates', icon: Activity, label: 'Feeds & Telemetry' },
            { to: '__api_modal__', icon: Terminal, label: 'Developers & API' },
          ]
        }
      ];
    }

    if (persona === 'investor') {
      return [
        {
          title: 'Market Intelligence',
          items: [
            { to: '/digest', icon: Newspaper, label: 'Daily Digest' },
            { to: '/sankey', icon: GitMerge, label: 'Capital Flows (Sankey)' },
            { to: '/venture-patents', icon: Lightbulb, label: 'Venture & Bayh-Dole IP' },
            { to: '/reports', icon: FileText, label: 'Reports & Blueprints' },
            { to: '/trends', icon: TrendingUp, label: 'Capital Velocity & Trends' },
            { to: '/strategy', icon: Compass, label: 'Portfolio Strategy' },
          ]
        },
        {
          title: 'Due Diligence & Benchmarks',
          items: [
            { to: '/awards', icon: Trophy, label: 'Awards Ledger ($104B)' },
            { to: '/results', icon: Scale, label: 'Outcomes & Benchmarks' },
            { to: '/dockets', icon: Scale, label: 'Utility Dockets & Tariffs' },
            { to: '/organizations', icon: Building2, label: 'Agencies & Utilities' },
            { to: '/programs', icon: Layers, label: 'Programs & Initiatives' },
          ]
        },
        {
          title: 'Project & Deal Sourcing',
          items: [
            { to: '/analyze', icon: Sliders, label: 'Project Bankability (TBR)' },
            { to: '/opportunities', icon: FileSearch, label: 'Active Solicitations' },
            { to: '/technologies', icon: BookOpen, label: 'Frontier Tech Taxonomy' },
            { to: '/network', icon: Network, label: 'Ecosystem & Syndicates' },
          ]
        },
        {
          title: 'Data & Developer API',
          items: [
            { to: '/sources', icon: Database, label: 'Data Provenance' },
            { to: '/updates', icon: Activity, label: 'Feeds & Telemetry' },
            { to: '__api_modal__', icon: Terminal, label: 'Developers & API' },
          ]
        }
      ];
    }

    // Master / All Modules View
    return [
      {
        title: 'Opportunities & Studio',
        items: [
          { to: '/digest', icon: Newspaper, label: 'Daily Digest' },
          { to: '/analyze', icon: Sliders, label: 'Match Engine' },
          { to: '/radar', icon: Radio, label: 'Predictive Radar' },
          { to: '/opportunities', icon: FileSearch, label: 'Solicitations (5,757)' },
          { to: '/proposals', icon: FileEdit, label: 'Application Studio' },
        ]
      },
      {
        title: 'Awards & Precedents',
        items: [
          { to: '/awards', icon: Trophy, label: 'Awards Ledger ($104B)' },
          { to: '/venture-patents', icon: Lightbulb, label: 'Venture & Bayh-Dole IP' },
          { to: '/results', icon: Scale, label: 'Outcomes & Benchmarks' },
        ]
      },
      {
        title: 'Directories & Ecosystem',
        items: [
          { to: '/organizations', icon: Building2, label: 'Organizations & Utilities' },
          { to: '/programs', icon: Layers, label: 'Programs (143)' },
          { to: '/contacts', icon: BookUser, label: 'Key Contacts & PIs' },
          { to: '/network', icon: Network, label: 'Teaming & Syndicates' },
        ]
      },
      {
        title: 'Market Intelligence',
        items: [
          { to: '/strategy', icon: Compass, label: 'Portfolio Strategy' },
          { to: '/sankey', icon: GitMerge, label: 'Capital Flows (Sankey)' },
          { to: '/trends', icon: TrendingUp, label: 'Capital Velocity & Trends' },
          { to: '/reports', icon: FileText, label: 'Reports & Blueprints' },
        ]
      },
      {
        title: 'Regulatory & References',
        items: [
          { to: '/technologies', icon: BookOpen, label: 'Technology Reference' },
          { to: '/policies', icon: ShieldCheck, label: 'IRA §45/§48 Tax Credits' },
          { to: '/dockets', icon: Scale, label: 'Utility Dockets & Tariffs' },
        ]
      },
      {
        title: 'Data & Developer API',
        items: [
          { to: '/updates', icon: Activity, label: 'Feeds & Telemetry' },
          { to: '/sources', icon: Database, label: 'Data Provenance' },
          { to: '__api_modal__', icon: Terminal, label: 'Developers & API' },
        ]
      }
    ];
  }, [persona]);

  // Ensure active category is always expanded so current menu item is never hidden
  useEffect(() => {
    for (const section of navSections) {
      if (section.items.some(item => isItemActive(item.to))) {
        setCollapsedSections(prev => {
          if (prev[section.title]) {
            const updated = { ...prev, [section.title]: false };
            try {
              localStorage.setItem('energy_terminal_nav_collapsed_v6', JSON.stringify(updated));
            } catch {}
            return updated;
          }
          return prev;
        });
        break;
      }
    }
  }, [location.pathname, persona, navSections]);

  const allCollapsed = useMemo(() => {
    return navSections.every(s => collapsedSections[s.title]);
  }, [navSections, collapsedSections]);

  const renderSidebar = (isMobile = false) => {
    const isChatActive = isItemActive('/chat');

    return (
      <>
        {/* Brand Header */}
        <div className="px-5 py-4 border-b border-white/[0.06] flex items-center justify-between">
          <NavLink to={homeRoute} onClick={() => isMobile && setMobileMenuOpen(false)} className="cursor-pointer" title="Energy Innovation Terminal Home">
            <EnergyInnovationTerminalLogo size="md" showText={true} />
          </NavLink>
          {isMobile && (
            <button
              type="button"
              onClick={() => setMobileMenuOpen(false)}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
              aria-label="Close navigation"
            >
              <X size={18} />
            </button>
          )}
        </div>

        {/* Persona Front Door Selector */}
        <div className="px-3 pt-3 pb-2 border-b border-white/[0.06] space-y-1.5">
          <div className="flex items-center justify-between text-[10px] font-semibold text-slate-400 px-0.5">
            <span className="uppercase tracking-wider text-[9px] text-slate-400">Front Door Mode</span>
            {persona !== 'all' ? (
              <button
                type="button"
                onClick={() => handlePersonaChange('all')}
                className="text-[9.5px] text-slate-400 hover:text-[#00E5FF] transition-colors cursor-pointer"
              >
                All Modules
              </button>
            ) : (
              <span className="text-[9px] text-[#00E5FF] font-mono">Master</span>
            )}
          </div>
          <div className="grid grid-cols-2 p-0.5 bg-white/[0.03] border border-white/[0.06] rounded-lg gap-0.5">
            <button
              type="button"
              onClick={() => handlePersonaChange('investor')}
              className={clsx(
                "px-1.5 py-1 rounded-md text-[10.5px] font-bold transition-all flex items-center justify-center gap-1 cursor-pointer",
                persona === 'investor'
                  ? "bg-cyan-500/20 text-[#00E5FF] border border-cyan-500/40 shadow-2xs"
                  : "text-slate-400 hover:text-slate-200"
              )}
              title="Spotlight: Daily Digest, Capital Flows (Sankey), Venture & IP, Reports, Trends"
            >
              <TrendingUp size={11} className={persona === 'investor' ? "text-[#00E5FF]" : "text-slate-400"} />
              <span className="truncate">Investors</span>
            </button>
            <button
              type="button"
              onClick={() => handlePersonaChange('innovator')}
              className={clsx(
                "px-1.5 py-1 rounded-md text-[10.5px] font-bold transition-all flex items-center justify-center gap-1 cursor-pointer",
                persona === 'innovator'
                  ? "bg-indigo-500/25 text-indigo-300 border border-indigo-500/40 shadow-2xs"
                  : "text-slate-400 hover:text-slate-200"
              )}
              title="Spotlight: Project Match, Solicitations, Winning Proposals Studio, Key Contacts"
            >
              <Lightbulb size={11} className={persona === 'innovator' ? "text-indigo-400" : "text-slate-400"} />
              <span className="truncate">Innovators</span>
            </button>
          </div>
        </div>

        {/* Navigation Area */}
        <nav className="flex-1 px-3 py-3 space-y-2 overflow-y-auto no-scrollbar">
          {/* Top Primary Item: Strategic Advisory */}
          <div className="space-y-1 mb-2">
            <NavLink
              to="/chat"
              onClick={() => isMobile && setMobileMenuOpen(false)}
              className={clsx(
                'flex items-center justify-between gap-2 px-3 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer border',
                isChatActive
                  ? 'bg-cyan-500/15 text-white border-l-2 border-[#00E5FF] font-bold shadow-2xs'
                  : 'bg-white/[0.03] hover:bg-white/[0.06] text-slate-300 border-white/[0.06] hover:text-white'
              )}
            >
              <div className="flex items-center gap-2.5 min-w-0">
                <MessageSquare
                  size={15}
                  strokeWidth={1.8}
                  className={clsx(
                    'shrink-0 transition-colors',
                    isChatActive ? 'text-[#00E5FF]' : 'text-slate-400'
                  )}
                />
                <span className="truncate">Strategic Advisory</span>
              </div>
              <span className={clsx(
                "text-[9.5px] font-bold px-1.5 py-0.2 rounded font-mono",
                isChatActive ? "bg-cyan-500/20 text-[#00E5FF] border border-cyan-400/30" : "bg-white/[0.05] text-slate-400 border border-white/10"
              )}>
                LIVE
              </span>
            </NavLink>
          </div>

          {/* Sidebar Nav Category Header / Collapse Toggle */}
          <div className="pt-2 pb-1 flex items-center justify-between text-[10px] text-slate-400 px-1 border-t border-white/[0.06]">
            <span className="font-semibold uppercase tracking-wider text-[9px] text-slate-400">Navigation</span>
            <button
              type="button"
              onClick={() => toggleAll(!allCollapsed)}
              className="flex items-center gap-1 hover:text-slate-200 transition-colors text-[10px] font-medium cursor-pointer"
              title={allCollapsed ? "Expand all categories" : "Collapse all categories"}
            >
              <ChevronsUpDown size={11} className="text-slate-400" />
              <span>{allCollapsed ? 'Expand All' : 'Collapse All'}</span>
            </button>
          </div>

          {/* Collapsible Accordion Sections */}
          <div className="space-y-2">
            {navSections.map((section) => {
              const isCollapsed = !!collapsedSections[section.title];
              const hasActiveChild = section.items.some(item => isItemActive(item.to));

              return (
                <div key={section.title} className="space-y-0.5">
                  <button
                    type="button"
                    onClick={() => toggleSection(section.title)}
                    className="w-full px-2.5 py-1 rounded-md hover:bg-white/[0.04] text-[9.5px] font-bold uppercase tracking-[0.14em] text-slate-400 flex items-center justify-between group cursor-pointer transition-colors"
                  >
                    <span className="group-hover:text-slate-200 transition-colors text-left truncate">{section.title}</span>
                    <div className="flex items-center gap-1.5 shrink-0">
                      {hasActiveChild && isCollapsed && (
                        <span className="w-1.5 h-1.5 rounded-full bg-[#00E5FF] shadow-[0_0_6px_#00E5FF]" />
                      )}
                      <span className="text-[9px] font-mono text-slate-400 font-normal">
                        {section.items.length}
                      </span>
                      {isCollapsed ? (
                        <ChevronRight size={12} className="text-slate-400 group-hover:text-slate-200 transition-transform" />
                      ) : (
                        <ChevronDown size={12} className="text-slate-400 group-hover:text-slate-200 transition-transform" />
                      )}
                    </div>
                  </button>

                  {!isCollapsed && (
                    <div className="space-y-0.5 pl-0.5 animate-in fade-in-50 duration-100">
                      {section.items.map((item) => {
                        const active = isItemActive(item.to);
                        return item.to === '__api_modal__' ? (
                          <button
                            key={item.label}
                            type="button"
                            onClick={() => {
                              if (isMobile) setMobileMenuOpen(false);
                              setApiModalOpen(true);
                            }}
                            className={clsx(
                              "w-full relative flex items-center justify-between gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer group text-left",
                              apiModalOpen
                                ? "bg-cyan-500/15 text-white font-semibold border-l-2 border-[#00E5FF] shadow-2xs"
                                : "text-slate-400 hover:bg-white/[0.04] hover:text-slate-200"
                            )}
                          >
                            <div className="flex items-center gap-2.5 min-w-0">
                              <item.icon
                                size={14}
                                strokeWidth={1.8}
                                className={clsx(
                                  "shrink-0 transition-colors",
                                  apiModalOpen ? "text-[#00E5FF]" : "text-slate-400 group-hover:text-[#00E5FF]"
                                )}
                              />
                              <span className="truncate">{item.label}</span>
                            </div>
                            {item.badge && (
                              <span className="text-[9px] font-semibold px-1.5 py-0.2 rounded bg-cyan-950/60 text-[#00E5FF] border border-cyan-500/30 shrink-0 font-mono">
                                {item.badge}
                              </span>
                            )}
                          </button>
                        ) : (
                          <NavLink
                            key={`${section.title}-${item.to}-${item.label}`}
                            to={item.to}
                            onClick={() => isMobile && setMobileMenuOpen(false)}
                            className={clsx(
                              'relative flex items-center justify-between gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer',
                              active
                                ? 'bg-cyan-500/15 text-white font-semibold border-l-2 border-[#00E5FF] shadow-2xs'
                                : 'text-slate-400 hover:bg-white/[0.04] hover:text-slate-200'
                            )}
                          >
                            <div className="flex items-center gap-2.5 min-w-0">
                              <item.icon
                                size={14}
                                strokeWidth={1.8}
                                className={clsx(
                                  'shrink-0 transition-colors',
                                  active ? 'text-[#00E5FF]' : 'text-slate-400'
                                )}
                              />
                              <span className={clsx("truncate", active && "text-white font-semibold")}>{item.label}</span>
                            </div>
                            {item.badge && (
                              <span className={clsx(
                                "text-[9px] font-semibold px-1.5 py-0.2 rounded border shrink-0 font-mono",
                                active ? "bg-cyan-950/80 text-[#00E5FF] border-cyan-500/40" : "bg-slate-800 text-slate-300 border-white/10"
                              )}>
                                {item.badge}
                              </span>
                            )}
                          </NavLink>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </nav>

      {/* Sidebar Footer */}
      <div className="px-4 py-3 border-t border-white/[0.06] flex items-center justify-between text-[10px] text-slate-400">
        <button
          type="button"
          onClick={() => {
            if (isMobile) setMobileMenuOpen(false);
            setSignatureModalOpen(true);
          }}
          className="flex items-center gap-1.5 hover:text-cyan-300 transition-colors cursor-pointer group text-left min-w-0"
          title="View Executive Provenance & Author Briefing"
        >
          <ShieldCheck size={13} className="text-cyan-400 group-hover:scale-110 transition-transform shrink-0" />
          <span className="text-slate-300 font-medium tracking-wide group-hover:text-white truncate">Energy Terminal</span>
        </button>
        <button
          type="button"
          onClick={() => {
            if (isMobile) setMobileMenuOpen(false);
            setSignatureModalOpen(true);
          }}
          className="font-mono text-slate-400 text-[9.5px] hover:text-cyan-300 transition-colors cursor-pointer px-1.5 py-0.5 rounded bg-white/[0.04] border border-white/[0.08] shrink-0"
          title="Version 3.5.0 - Click for Author Dossier"
        >
          v3.5
        </button>
      </div>
    </>
  );
};

  return (
    <div className="flex h-screen bg-[#f8fafc] text-slate-800 antialiased selection:bg-blue-500/20 selection:text-blue-900 overflow-hidden">
      {/* Global Command Palette */}
      <CommandPalette
        isOpen={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
      />

      {/* Mobile Drawer Backdrop */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/75 backdrop-blur-xs z-40 md:hidden transition-opacity animate-in fade-in"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Mobile Slide-Over Drawer */}
      <div
        className={clsx(
          "fixed inset-y-0 left-0 z-50 w-72 max-w-[85vw] bg-[#090d16] text-slate-300 flex flex-col border-r border-white/[0.08] shadow-2xl transition-transform duration-200 md:hidden select-none",
          mobileMenuOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {renderSidebar(true)}
      </div>

      {/* Desktop Executive Sidebar */}
      <aside className="hidden md:flex md:w-64 bg-[#090d16] text-slate-300 flex-col border-r border-white/[0.08] z-20 shrink-0 select-none">
        {renderSidebar(false)}
      </aside>

      {/* Main Content Area */}
      <div className={clsx(
        "flex-1 flex flex-col overflow-hidden min-w-0 transition-colors duration-150",
        isDark ? "bg-[#090e17] text-slate-100" : "bg-[#f8fafc] text-slate-900"
      )}>
        {/* Top Header Bar */}
        <header className={clsx(
          "h-13 px-3 sm:px-6 flex items-center justify-between shrink-0 z-10 transition-colors duration-150 border-b gap-2",
          isDark
            ? "bg-[#0b101c] border-white/[0.08] text-slate-100"
            : "bg-white border-slate-200 text-slate-900 shadow-2xs"
        )}>
          <div className="flex items-center gap-2 sm:gap-3 min-w-0">
            {/* Mobile Hamburger Toggle */}
            <button
              type="button"
              onClick={() => setMobileMenuOpen(true)}
              className={clsx(
                "p-1.5 -ml-1 rounded-lg md:hidden cursor-pointer transition-colors",
                isDark ? "text-slate-300 hover:text-white hover:bg-white/10" : "text-slate-700 hover:text-slate-900 hover:bg-slate-100"
              )}
              aria-label="Open navigation menu"
            >
              <Menu size={20} />
            </button>

            {/* Mobile Logo Icon */}
            <NavLink to={homeRoute} className="md:hidden flex items-center shrink-0 cursor-pointer">
              <EnergyInnovationTerminalLogo size="sm" showText={false} />
            </NavLink>


            <div className="flex items-center gap-2.5 text-xs font-medium min-w-0">
              <span className={clsx(
                "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md font-semibold text-[11px] font-mono shrink-0",
                isDark
                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/25"
                  : "bg-emerald-50 text-emerald-800 border border-emerald-200"
              )}>
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0" />
                <span className="hidden sm:inline">56,413 Awards · $104.16B Capital Tracked</span>
                <span className="sm:hidden">56k+ Awards · $104B+</span>
              </span>
            </div>
          </div>

          <div className="flex items-center gap-1.5 sm:gap-2.5 shrink-0">
            {/* Front Door Quick Switcher in Header */}
            <div className={clsx(
              "hidden md:flex items-center p-0.5 rounded-lg border text-xs font-semibold select-none shrink-0",
              isDark ? "bg-white/[0.04] border-white/[0.08]" : "bg-slate-100 border-slate-200"
            )}>
              <button
                type="button"
                onClick={() => handlePersonaChange('investor')}
                className={clsx(
                  "px-2 py-0.5 rounded-md text-[10.5px] font-bold transition-all flex items-center gap-1 cursor-pointer",
                  persona === 'investor'
                    ? (isDark ? "bg-cyan-500/25 text-[#00E5FF] border border-cyan-500/40 shadow-2xs" : "bg-white text-cyan-700 shadow-2xs border border-cyan-200")
                    : (isDark ? "text-slate-400 hover:text-slate-200" : "text-slate-600 hover:text-slate-900")
                )}
                title="Investor & Strategist Front Door: Daily Digest, Capital Flows, Venture & IP, Reports"
              >
                <TrendingUp size={11} className={persona === 'investor' ? (isDark ? "text-[#00E5FF]" : "text-cyan-600") : "opacity-60"} />
                <span>Investors</span>
              </button>
              <button
                type="button"
                onClick={() => handlePersonaChange('innovator')}
                className={clsx(
                  "px-2 py-0.5 rounded-md text-[10.5px] font-bold transition-all flex items-center gap-1 cursor-pointer",
                  persona === 'innovator'
                    ? (isDark ? "bg-indigo-500/25 text-indigo-300 border border-indigo-500/40 shadow-2xs" : "bg-white text-indigo-700 shadow-2xs border border-indigo-200")
                    : (isDark ? "text-slate-400 hover:text-slate-200" : "text-slate-600 hover:text-slate-900")
                )}
                title="Innovator & Grant Seeker Front Door: Match Engine, Solicitations, Application Studio"
              >
                <Lightbulb size={11} className={persona === 'innovator' ? "text-indigo-400" : "text-indigo-600"} />
                <span>Innovators</span>
              </button>
              <button
                type="button"
                onClick={() => handlePersonaChange('all')}
                className={clsx(
                  "px-1.5 py-0.5 rounded-md text-[10px] font-semibold transition-all cursor-pointer font-mono",
                  persona === 'all'
                    ? (isDark ? "bg-white/10 text-white shadow-2xs" : "bg-white text-slate-900 shadow-2xs border border-slate-300")
                    : (isDark ? "text-slate-500 hover:text-slate-300" : "text-slate-400 hover:text-slate-700")
                )}
                title="All Modules (Master Navigation)"
              >
                All
              </button>
            </div>

            <ThemeToggle />
            <button
              type="button"
              onClick={() => setCommandPaletteOpen(true)}
              className={clsx(
                "inline-flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1.5 rounded-lg text-xs font-medium transition-all border shadow-2xs cursor-pointer",
                isDark
                  ? "bg-slate-800/70 hover:bg-slate-800 text-slate-200 border-white/10 hover:border-slate-600"
                  : "bg-slate-100 hover:bg-slate-200 text-slate-800 border-slate-200 hover:border-slate-300"
              )}
            >
              <Search size={13} className={isDark ? "text-slate-400" : "text-slate-600"} />
              <span className="hidden sm:inline">Search Database</span>
              <kbd className={clsx(
                "text-[9px] sm:text-[10px] font-mono font-semibold px-1 sm:px-1.5 py-0.2 rounded border",
                isDark ? "bg-slate-900 text-slate-300 border-slate-700" : "bg-white text-slate-700 border-slate-200"
              )}>⌘K</kbd>
            </button>
            <UserMenu />
          </div>
        </header>

        {/* Auth, Membership, Account, Brandon Signature & Legal Compliance Modals */}
        <AuthModal />
        <MembershipModal />
        <AccountModal />
        <BrandonSignatureModal isOpen={signatureModalOpen} onClose={() => setSignatureModalOpen(false)} />
        <LegalComplianceModal isOpen={legalModalOpen} onClose={() => setLegalModalOpen(false)} />
        <ApiDocsModal isOpen={apiModalOpen} onClose={() => setApiModalOpen(false)} />


        {/* Page Content */}
        <main className="flex-1 overflow-auto px-3 sm:px-6 py-4 sm:py-6 min-w-0">
          <Outlet />
        </main>

        {/* Global Executive Footer */}
        <footer className={clsx(
          "border-t px-6 py-2.5 text-[11px] flex flex-col sm:flex-row items-center justify-between gap-2.5 shrink-0 transition-colors duration-150 select-none",
          isDark
            ? "bg-[#0b101c] border-white/[0.06] text-slate-400"
            : "bg-white border-slate-200 text-slate-600 shadow-2xs"
        )}>
          <div className="flex items-center gap-3 flex-wrap">
            <button
              type="button"
              onClick={() => setSignatureModalOpen(true)}
              className={clsx(
                "inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium transition-all border cursor-pointer group",
                isDark
                  ? "bg-white/[0.02] hover:bg-white/[0.06] text-slate-300 border-white/[0.08]"
                  : "bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-200"
              )}
              title="Curated & Engineered by Brandon N. Owens (Click to view verified provenance & citation)"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span>Curated &amp; Engineered by <strong className="text-cyan-400 group-hover:underline">Brandon N. Owens</strong></span>
            </button>

            <button
              type="button"
              onClick={() => setLegalModalOpen(true)}
              className={clsx(
                "inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10.5px] font-medium transition-all border cursor-pointer",
                isDark
                  ? "bg-white/[0.02] hover:bg-white/[0.06] text-slate-400 hover:text-slate-300 border-white/[0.06]"
                  : "bg-slate-100 hover:bg-slate-200 text-slate-600 border-slate-200"
              )}
              title="Public Records Provenance, Ethics, and Non-Affiliation Notice"
            >
              <Scale size={11} className="text-slate-400" />
              <span>Legal &amp; Compliance</span>
            </button>

            <span className={clsx(isDark ? "text-white/10" : "text-slate-300", "hidden sm:inline")}>|</span>

            <span className="hidden lg:inline text-[10.5px] font-mono text-slate-400">
              56,413 Awards · $104.16B Capital · 140+ Authorities · Open Public Records
            </span>
          </div>

          <div className="flex items-center gap-2 font-mono text-[10px] text-slate-400">
            <span>Energy Innovation Intelligence Terminal</span>
            <span>·</span>
            <span>v3.5</span>
          </div>
        </footer>
      </div>
    </div>
  );
}

