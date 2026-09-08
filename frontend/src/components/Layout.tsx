import React, { useState, useEffect, useMemo } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import {
  Sparkles, FileSearch, Layers, Building2, Trophy, Network,
  TrendingUp, Database, GitMerge, FileText, Search, ShieldCheck,
  Zap, Command, FileEdit, Scale, Lightbulb, Clock, Activity, BookUser, BookOpen, Bot,
  ChevronDown, ChevronRight, ChevronsUpDown, Mail, Compass, Radio
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
  const location = useLocation();

  // Collapsed state for navigation sections
  const [collapsedSections, setCollapsedSections] = useState<Record<string, boolean>>(() => {
    try {
      const saved = localStorage.getItem('energy_terminal_nav_collapsed_v5');
      if (saved) return JSON.parse(saved);
    } catch {
      // ignore
    }
    return {
      'Awards & Outcomes': false,
      'Organizations': true,
      'Strategy & Intelligence': true,
      'References': true,
      'Data & Audit': true,
    };
  });

  const toggleSection = (sectionTitle: string) => {
    setCollapsedSections(prev => {
      const updated = { ...prev, [sectionTitle]: !prev[sectionTitle] };
      try {
        localStorage.setItem('energy_terminal_nav_collapsed_v5', JSON.stringify(updated));
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
      localStorage.setItem('energy_terminal_nav_collapsed_v5', JSON.stringify(updated));
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
    return () => window.removeEventListener('keydown', handleKeyDown);
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

  const navSections: NavSection[] = [
    {
      title: 'Opportunity Matcher',
      items: [
        { to: '/analyze', icon: Sparkles, label: 'Match Opportunities' },
        { to: '/radar', icon: Radio, label: 'Early-Warning Radar' },
        { to: '/opportunities', icon: FileSearch, label: 'Funding Directory' },
      ]
    },
    {
      title: 'Awards & Outcomes',
      items: [
        { to: '/awards', icon: Trophy, label: 'Awards & Deployments' },
        { to: '/venture-patents', icon: Lightbulb, label: 'Venture & Patents' },
        { to: '/results', icon: Scale, label: 'Results & Outcomes' },
      ]
    },
    {
      title: 'Organizations & Programs',
      items: [
        { to: '/organizations', icon: Building2, label: 'Organizations' },
        { to: '/programs', icon: Layers, label: 'Programs' },
        { to: '/contacts', icon: BookUser, label: 'Key Contacts' },
        { to: '/network', icon: Network, label: 'Entity Network' },
      ]
    },
    {
      title: 'Strategy & Intelligence',
      items: [
        { to: '/strategy', icon: Compass, label: 'Strategy' },
        { to: '/sankey', icon: GitMerge, label: 'Funding Flows' },
        { to: '/trends', icon: TrendingUp, label: 'Trends' },
        { to: '/reports', icon: FileText, label: 'Executive Reports' },
      ]
    },
    {
      title: 'References',
      items: [
        { to: '/technologies', icon: BookOpen, label: 'Technology Reference' },
        { to: '/policies', icon: ShieldCheck, label: 'Policy Reference' },
        { to: '/dockets', icon: Scale, label: 'Regulatory Dockets' },
      ]
    },
    {
      title: 'Data & Audit',
      items: [
        { to: '/updates', icon: Activity, label: 'Ingestion Feed' },
        { to: '/sources', icon: Database, label: 'Data Provenance & Audit' },
      ]
    },
    {
      title: 'Administration',
      items: [
        { to: '/admin/email-hub', icon: BookUser, label: 'Contact CRM & Intelligence', badge: 'CRM' },
      ]
    }
  ];

  const allCollapsed = useMemo(() => {
    return navSections.every(s => collapsedSections[s.title]);
  }, [navSections, collapsedSections]);

  return (
    <div className="flex h-screen bg-[#f8fafc] text-slate-800 antialiased selection:bg-blue-500/20 selection:text-blue-900 overflow-hidden">
      {/* Global Command Palette */}
      <CommandPalette
        isOpen={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
      />

      {/* Executive Sidebar */}
      <aside className="w-64 bg-[#090d16] text-slate-300 flex flex-col border-r border-white/[0.08] z-20 shrink-0 select-none">
        {/* Brand Header */}
        <div className="px-5 py-4 border-b border-white/[0.06]">
          <div className="flex items-center justify-between">
            <EnergyInnovationTerminalLogo size="md" showText={true} />
          </div>
        </div>

        {/* Navigation Area */}
        <nav className="flex-1 px-3 py-3 space-y-2 overflow-y-auto no-scrollbar">
          {/* Top Primary Item: Strategic AI Advisor */}
          <div className="space-y-1 mb-2">
            <NavLink
              to="/chat"
              className={({ isActive }) =>
                clsx(
                  'flex items-center justify-between gap-2 px-3 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer border',
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 to-emerald-500/15 text-white border-cyan-400/50 shadow-glow-cyan-sm'
                    : 'bg-white/[0.03] hover:bg-white/[0.06] text-slate-300 border-white/[0.06] hover:text-white'
                )
              }
            >
              {({ isActive }) => (
                <>
                  <div className="flex items-center gap-2.5 min-w-0">
                    <Bot
                      size={15}
                      strokeWidth={1.8}
                      className={clsx(
                        'shrink-0 transition-colors',
                        isActive ? 'text-[#00E5FF]' : 'text-[#00F5A0]'
                      )}
                    />
                    <span className="truncate font-bold">Strategic Advisor</span>
                  </div>
                  <span className={clsx(
                    "text-[9px] font-bold px-1.5 py-0.2 rounded font-mono",
                    isActive ? "bg-cyan-500/30 text-[#00E5FF] border border-cyan-400/40" : "bg-emerald-500/15 text-[#00F5A0] border border-emerald-500/30"
                  )}>
                    AI
                  </span>
                </>
              )}
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
              const hasActiveChild = section.items.some(item => {
                if (item.to === '/') return location.pathname === '/';
                return location.pathname.startsWith(item.to);
              });

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
                      {section.items.map((item) => (
                        <NavLink
                          key={item.to}
                          to={item.to}
                          end={item.to === '/'}
                          className={({ isActive }) =>
                            clsx(
                              'relative flex items-center justify-between gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer',
                              isActive
                                ? 'bg-cyan-500/10 text-white font-semibold border-l-2 border-[#00E5FF] shadow-2xs'
                                : 'text-slate-400 hover:bg-white/[0.04] hover:text-slate-200'
                            )
                          }
                        >
                          {({ isActive }) => (
                            <>
                              <div className="flex items-center gap-2.5 min-w-0">
                                <item.icon
                                  size={14}
                                  strokeWidth={1.8}
                                  className={clsx(
                                    'shrink-0 transition-colors',
                                    isActive ? 'text-[#00E5FF]' : 'text-slate-400'
                                  )}
                                />
                                <span className={clsx("truncate", isActive && "text-white font-semibold")}>{item.label}</span>
                              </div>
                              {item.badge && (
                                <span className="text-[9px] font-semibold px-1.5 py-0.2 rounded bg-slate-800 text-[#00E5FF] border border-cyan-500/30 shrink-0 font-mono">
                                  {item.badge}
                                </span>
                              )}
                            </>
                          )}
                        </NavLink>
                      ))}
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
            onClick={() => setSignatureModalOpen(true)}
            className="flex items-center gap-1.5 hover:text-cyan-300 transition-colors cursor-pointer group text-left"
            title="View Executive Provenance & Author Briefing"
          >
            <ShieldCheck size={13} className="text-cyan-400 group-hover:scale-110 transition-transform" />
            <span className="text-slate-300 font-medium tracking-wide group-hover:text-white">Energy Innovation Terminal</span>
          </button>
          <button
            type="button"
            onClick={() => setSignatureModalOpen(true)}
            className="font-mono text-slate-400 text-[9.5px] hover:text-cyan-300 transition-colors cursor-pointer px-1.5 py-0.5 rounded bg-white/[0.04] border border-white/[0.08]"
            title="Version 3.5.0 - Click for Author Dossier"
          >
            v3.5
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className={clsx(
        "flex-1 flex flex-col overflow-hidden min-w-0 transition-colors duration-150",
        isDark ? "bg-[#090e17] text-slate-100" : "bg-[#f8fafc] text-slate-900"
      )}>
        {/* Top Header Bar */}
        <header className={clsx(
          "h-13 px-6 flex items-center justify-between shrink-0 z-10 transition-colors duration-150 border-b",
          isDark
            ? "bg-[#0b101c] border-white/[0.08] text-slate-100"
            : "bg-white border-slate-200 text-slate-900 shadow-2xs"
        )}>
          <div className="flex items-center gap-3 min-w-0">
            <div className="flex items-center gap-2.5 text-xs font-medium flex-wrap">
              <span className={clsx(
                "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md font-semibold text-[11px] font-mono",
                isDark
                  ? "bg-emerald-500/10 text-[#00F5A0] border border-emerald-500/30 shadow-[0_0_8px_rgba(0,245,160,0.15)]"
                  : "bg-emerald-50 text-emerald-800 border border-emerald-200"
              )}>
                <span className="w-2 h-2 rounded-full bg-[#00F5A0] shadow-[0_0_8px_#00F5A0] animate-pulse" />
                <span>56,413 Awards · $104.16B Tracked · 10,250 Grid Projects</span>
              </span>
              <span className={clsx(isDark ? "text-white/20" : "text-slate-300", "hidden md:inline")}>|</span>
              <span className={clsx(isDark ? "text-slate-400" : "text-slate-600", "hidden md:inline text-[11.5px] font-medium")}>
                DOE · ARPA-E · CEC · MassCEC · NSF · State Agencies · 140+ Utilities
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <ThemeToggle />
            <button
              type="button"
              onClick={() => setCommandPaletteOpen(true)}
              className={clsx(
                "inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all border shadow-2xs cursor-pointer",
                isDark
                  ? "bg-slate-800/70 hover:bg-slate-800 text-slate-200 border-white/10 hover:border-slate-600"
                  : "bg-slate-100 hover:bg-slate-200 text-slate-800 border-slate-200 hover:border-slate-300"
              )}
            >
              <Search size={13} className={isDark ? "text-slate-400" : "text-slate-600"} />
              <span>Search Database</span>
              <kbd className={clsx(
                "text-[10px] font-mono font-semibold px-1.5 py-0.2 rounded border",
                isDark ? "bg-slate-900 text-slate-300 border-slate-700" : "bg-white text-slate-700 border-slate-200"
              )}>⌘K</kbd>
            </button>
            <UserMenu />
          </div>
        </header>

        {/* Auth, Membership, Account & Brandon Signature Modals */}
        <AuthModal />
        <MembershipModal />
        <AccountModal />
        <BrandonSignatureModal isOpen={signatureModalOpen} onClose={() => setSignatureModalOpen(false)} />

        {/* Page Content */}
        <main className="flex-1 overflow-auto px-6 py-6 min-w-0">
          <Outlet />
        </main>

        {/* Global Signature Footer */}
        <footer className={clsx(
          "border-t px-6 py-2 text-[11px] flex flex-col sm:flex-row items-center justify-between gap-2.5 shrink-0 transition-colors duration-150",
          isDark
            ? "bg-[#0b101c] border-white/[0.06] text-slate-400"
            : "bg-white border-slate-200 text-slate-600 shadow-2xs"
        )}>
          <div className="flex items-center gap-3 flex-wrap">
            <button
              type="button"
              onClick={() => setSignatureModalOpen(true)}
              className={clsx(
                "inline-flex items-center gap-2 px-2.5 py-1 rounded-lg text-xs font-medium transition-all border cursor-pointer group select-none",
                isDark
                  ? "bg-white/[0.03] hover:bg-cyan-950/40 text-slate-200 border-white/[0.08] hover:border-cyan-500/40 shadow-xs"
                  : "bg-slate-100 hover:bg-cyan-50 text-slate-800 border-slate-200 hover:border-cyan-300"
              )}
              title="Curated & Engineered by Brandon N. Owens (Click to view verified provenance & citation)"
            >
              <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_6px_#10b981] group-hover:scale-110 transition-transform" />
              <span className="font-semibold text-[11px]">Curated &amp; Engineered by <strong className="text-cyan-400 font-bold group-hover:underline">Brandon N. Owens</strong></span>
              <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">VERIFIED</span>
            </button>

            <span className={clsx(isDark ? "text-white/10" : "text-slate-300", "hidden sm:inline")}>|</span>

            <span className="hidden md:inline text-[10.5px] font-mono text-slate-400">
              56,413 Awards · $104.16B Capital · 140+ Authorities
            </span>
          </div>

          <div className="flex items-center gap-3 font-mono text-[10px] text-slate-400">
            <button
              type="button"
              onClick={() => window.dispatchEvent(new CustomEvent('replay-splash-screen'))}
              className="hover:text-cyan-400 transition-colors flex items-center gap-1 cursor-pointer"
              title="Replay intro splash screen"
            >
              <Sparkles size={11} className="text-cyan-400" />
              <span className="hidden sm:inline">Splash Intro</span>
            </button>
            <span className={isDark ? "text-white/10" : "text-slate-300"}>·</span>
            <span>Upstream Energy Intelligence Terminal v3.5</span>
          </div>
        </footer>
      </div>
    </div>
  );
}

