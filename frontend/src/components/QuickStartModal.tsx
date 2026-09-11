import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Compass, MessageSquare, Newspaper, Sliders, Radio,
  Trophy, Building2, FileEdit, ArrowRight, CheckCircle2, Sparkles,
  X, BookOpen, Search, Zap, Lightbulb, ShieldCheck
} from 'lucide-react';
import clsx from 'clsx';
import { useTheme } from '../context/ThemeContext';
import { EnergyInnovationTerminalLogo } from './EnergyInnovationTerminalLogo';

interface QuickStartModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function QuickStartModal({ isOpen, onClose }: QuickStartModalProps) {
  const { isDark } = useTheme();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'tour' | 'workflows' | 'shortcuts'>('tour');

  if (!isOpen) return null;

  const handleNavigate = (path: string, persona?: 'investor' | 'innovator' | 'all') => {
    if (persona) {
      window.dispatchEvent(new CustomEvent('switch-persona', { detail: persona }));
    }
    navigate(path);
    onClose();
  };

  const corePillars = [
    {
      id: 'advisory',
      title: '1. Strategic AI Advisory',
      badge: 'Interactive Hub',
      path: '/',
      icon: MessageSquare,
      color: 'cyan',
      description: 'Consult a domain-trained AI advisor tailored to your operational perspective (Founder, Investor, Researcher, Utility, or Policy Lead), grounded in 56,413 historical awards and 5,757 active solicitations.',
      actionText: 'Open Chat Advisor',
      samplePrompt: 'How can our deep tech startup stack SBIR Phase I/II with state matching funds?'
    },
    {
      id: 'digest',
      title: '2. Daily Intelligence Digest',
      badge: 'Morning Briefing',
      path: '/digest',
      icon: Newspaper,
      color: 'emerald',
      description: 'Read the automated morning intelligence briefing summarizing new funding programs, closing deadlines, venture investments, and regulatory dockets across federal and state agencies.',
      actionText: "View Today's Digest",
      samplePrompt: 'Review new solicitations released in the last 7 days.'
    },
    {
      id: 'match',
      title: '3. AI Grant Match Screener',
      badge: 'Project Screener',
      path: '/analyze',
      icon: Sliders,
      color: 'indigo',
      description: 'Screen any clean tech project against 140+ federal, state, and utility funding organizations. Receive instant eligibility scoring, bankability metrics (TBR), and winning proposal angles.',
      actionText: 'Launch Match Screener',
      samplePrompt: 'Test a 10 MW iron-air battery storage demonstration project.'
    },
    {
      id: 'radar',
      title: '4. Forecasting Radar & Capital Flows',
      badge: 'Market Radar',
      path: '/forecasting',
      icon: Radio,
      color: 'amber',
      description: 'Anticipate upcoming funding releases 30 days to 18 months ahead based on statutory cadence models and trace multi-stage capital flows from R&D to commercial deployment.',
      actionText: 'Explore Release Radar',
      samplePrompt: 'Forecast upcoming clean hydrogen and grid modernization releases.'
    }
  ];

  const userWorkflows = [
    {
      title: 'Innovators & Startups',
      icon: Lightbulb,
      persona: 'innovator' as const,
      color: 'indigo',
      summary: 'Find non-dilutive capital, assess grant eligibility, and draft winning proposals.',
      steps: [
        'Open Match & Sponsoring (/analyze) to screen your technology profile.',
        'Filter 5,757 active solicitations (/opportunities) by cost-share and deadline.',
        'Use Proposal Studio (/proposals) to draft compliant statements of objectives.',
        'Connect with potential PIs and partner organizations (/network).'
      ]
    },
    {
      title: 'Investors & Strategists',
      icon: Trophy,
      persona: 'investor' as const,
      color: 'cyan',
      summary: 'Conduct technical due diligence, track public capital flows, and benchmark performers.',
      steps: [
        'Check the Daily Digest (/digest) for daily macro and venture capital wire.',
        'Trace multi-billion dollar capital flows with Sankey diagrams (/sankey).',
        'Verify startup grant track records and Bayh-Dole patent linkages (/venture-patents).',
        'Analyze historical award precedents across $104B+ in public grants (/awards).'
      ]
    },
    {
      title: 'Researchers & Academic PIs',
      icon: BookOpen,
      persona: 'innovator' as const,
      color: 'purple',
      summary: 'Form multi-institutional consortia, target center grants, and protect IP.',
      steps: [
        'Ask Strategic Advisory (/) about structuring $50M+ regional hub consortia.',
        'Search verified Principal Investigator directories and award momentum (/contacts).',
        'Review agency scoring rubrics and FOA shredder compliance checks (/shredder).'
      ]
    }
  ];

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-3 sm:p-6 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/80 backdrop-blur-md transition-opacity animate-in fade-in"
        onClick={onClose}
      />

      {/* Modal Card */}
      <div
        className={clsx(
          "relative w-full max-w-4xl rounded-2xl shadow-2xl overflow-hidden border transition-all duration-200 z-10 my-auto",
          isDark
            ? "bg-[#090e1a] border-cyan-500/30 text-slate-100 shadow-[0_0_50px_rgba(0,210,255,0.15)]"
            : "bg-white border-slate-200 text-slate-900 shadow-2xl"
        )}
      >
        {/* Header */}
        <div className="relative px-6 py-5 bg-gradient-to-r from-[#04101e] via-[#08182b] to-[#04101e] border-b border-cyan-500/30 overflow-hidden">
          <div className="relative z-10 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-cyan-950/70 border border-cyan-500/40 shadow-[0_0_20px_rgba(0,210,255,0.3)]">
                <Compass className="text-cyan-400" size={22} />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold tracking-widest text-cyan-400 uppercase">
                    Platform Quick Start Guide
                  </span>
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    v3.5.0
                  </span>
                </div>
                <h3 className="text-lg font-black tracking-tight text-white flex items-center gap-1.5 mt-0.5">
                  Welcome to Energy Innovation Intelligence Terminal
                </h3>
              </div>
            </div>

            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
              aria-label="Close guide"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className={clsx(
          "flex items-center gap-2 px-6 py-2.5 border-b text-xs font-semibold select-none",
          isDark ? "bg-[#060a14] border-white/[0.08]" : "bg-slate-50 border-slate-200"
        )}>
          <button
            type="button"
            onClick={() => setActiveTab('tour')}
            className={clsx(
              "px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer",
              activeTab === 'tour'
                ? "bg-cyan-500/20 text-[#00E5FF] border border-cyan-400/40 font-bold shadow-2xs"
                : "text-slate-400 hover:text-slate-200"
            )}
          >
            <Sparkles size={13} />
            <span>Core Capabilities Tour</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('workflows')}
            className={clsx(
              "px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer",
              activeTab === 'workflows'
                ? "bg-cyan-500/20 text-[#00E5FF] border border-cyan-400/40 font-bold shadow-2xs"
                : "text-slate-400 hover:text-slate-200"
            )}
          >
            <Zap size={13} />
            <span>Recommended Workflows</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('shortcuts')}
            className={clsx(
              "px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer",
              activeTab === 'shortcuts'
                ? "bg-cyan-500/20 text-[#00E5FF] border border-cyan-400/40 font-bold shadow-2xs"
                : "text-slate-400 hover:text-slate-200"
            )}
          >
            <Search size={13} />
            <span>Search &amp; Keyboard Shortcuts</span>
          </button>
        </div>

        {/* Modal Content Body */}
        <div className="p-6 max-h-[68vh] overflow-y-auto space-y-6">
          {activeTab === 'tour' && (
            <div className="space-y-4">
              <div className={clsx(
                "p-3.5 rounded-xl border flex items-start gap-2.5 text-xs leading-relaxed",
                isDark ? "bg-cyan-950/20 border-cyan-500/30 text-cyan-200" : "bg-cyan-50 border-cyan-200 text-cyan-950"
              )}>
                <ShieldCheck size={16} className="shrink-0 mt-0.5 text-cyan-400" />
                <p>
                  <strong>Zero-Friction Access:</strong> You are browsing as an authorized research visitor. All modules, real-time queries, search indices, and interactive tools are fully unlocked and grounded in <strong>56,413 public awards ($104.16B capital tracked)</strong> and <strong>5,757 open solicitations</strong>.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {corePillars.map((p) => {
                  const Icon = p.icon;
                  return (
                    <div
                      key={p.id}
                      className={clsx(
                        "p-4 rounded-xl border flex flex-col justify-between transition-all group",
                        isDark ? "bg-white/[0.02] border-white/[0.08] hover:border-cyan-500/40" : "bg-slate-50 border-slate-200 hover:border-cyan-500"
                      )}
                    >
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <div className={clsx(
                            "p-2 rounded-lg",
                            p.color === 'cyan' ? "bg-cyan-500/20 text-[#00E5FF]" :
                            p.color === 'emerald' ? "bg-emerald-500/20 text-emerald-400" :
                            p.color === 'indigo' ? "bg-indigo-500/20 text-indigo-400" :
                            "bg-amber-500/20 text-amber-400"
                          )}>
                            <Icon size={16} />
                          </div>
                          <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-white/[0.06] text-slate-300 border border-white/10">
                            {p.badge}
                          </span>
                        </div>
                        <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                          {p.title}
                        </h4>
                        <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                          {p.description}
                        </p>
                      </div>

                      <div className="pt-4 mt-2 border-t border-white/[0.06] flex items-center justify-between gap-2">
                        <span className="text-[10.5px] text-slate-400 italic truncate max-w-[200px]" title={p.samplePrompt}>
                          &ldquo;{p.samplePrompt}&rdquo;
                        </span>
                        <button
                          type="button"
                          onClick={() => handleNavigate(p.path)}
                          className="inline-flex items-center gap-1 text-xs font-bold text-[#00E5FF] hover:underline cursor-pointer shrink-0"
                        >
                          <span>{p.actionText}</span>
                          <ArrowRight size={12} />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {activeTab === 'workflows' && (
            <div className="space-y-4">
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Choose your primary objective to follow a curated step-by-step workflow:
              </p>

              <div className="space-y-4">
                {userWorkflows.map((wf, idx) => {
                  const Icon = wf.icon;
                  return (
                    <div
                      key={idx}
                      className={clsx(
                        "p-4 rounded-xl border space-y-3",
                        isDark ? "bg-white/[0.02] border-white/[0.08]" : "bg-slate-50 border-slate-200"
                      )}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2.5">
                          <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
                            <Icon size={16} />
                          </div>
                          <div>
                            <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                              {wf.title}
                            </h4>
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                              {wf.summary}
                            </p>
                          </div>
                        </div>

                        <button
                          type="button"
                          onClick={() => handleNavigate(wf.persona === 'investor' ? '/digest' : '/analyze', wf.persona)}
                          className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-colors cursor-pointer shadow-2xs"
                        >
                          Activate {wf.title.split(' ')[0]} View
                        </button>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2 border-t border-white/[0.06]">
                        {wf.steps.map((st, sIdx) => (
                          <div key={sIdx} className="flex items-start gap-2 text-xs text-slate-700 dark:text-slate-300">
                            <CheckCircle2 size={13} className="text-emerald-500 shrink-0 mt-0.5" />
                            <span>{st}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {activeTab === 'shortcuts' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className={clsx(
                  "p-4 rounded-xl border space-y-2",
                  isDark ? "bg-white/[0.02] border-white/[0.08]" : "bg-slate-50 border-slate-200"
                )}>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-900 dark:text-white">Global Command Palette</span>
                    <kbd className="px-2 py-0.5 rounded bg-slate-800 text-cyan-400 font-mono text-xs border border-slate-700">⌘K or /</kbd>
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                    Instantly search across all 13 database domains, including awardee companies (e.g. Ecolectro), solicitations, patents, contacts, and regulatory dockets.
                  </p>
                </div>

                <div className={clsx(
                  "p-4 rounded-xl border space-y-2",
                  isDark ? "bg-white/[0.02] border-white/[0.08]" : "bg-slate-50 border-slate-200"
                )}>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-900 dark:text-white">Switch Operational Perspective</span>
                    <span className="text-xs font-mono text-indigo-400">Advisory Top Bar</span>
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                    Toggle between Founder, Investor, Researcher, Utility Grid Lead, and Policy Maker to adapt the AI's analytical depth and citation context.
                  </p>
                </div>

                <div className={clsx(
                  "p-4 rounded-xl border space-y-2",
                  isDark ? "bg-white/[0.02] border-white/[0.08]" : "bg-slate-50 border-slate-200"
                )}>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-900 dark:text-white">Export Executive Briefing PDF</span>
                    <span className="text-xs font-mono text-emerald-400">Daily Digest</span>
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                    Click &ldquo;Export PDF Briefing&rdquo; on the Daily Digest to download a publication-grade, printable multi-page briefing for board meetings.
                  </p>
                </div>

                <div className={clsx(
                  "p-4 rounded-xl border space-y-2",
                  isDark ? "bg-white/[0.02] border-white/[0.08]" : "bg-slate-50 border-slate-200"
                )}>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-900 dark:text-white">Developer API Documentation</span>
                    <span className="text-xs font-mono text-purple-400">API Modal</span>
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                    Access standard REST endpoints, OpenAPI schemas, and Python SDK code snippets to integrate terminal data into your own applications.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className={clsx(
          "px-6 py-3.5 border-t flex flex-col sm:flex-row items-center justify-between gap-3 text-xs",
          isDark ? "bg-[#060a14] border-white/[0.08]" : "bg-slate-50 border-slate-200"
        )}>
          <div className="text-[11px] text-slate-400 flex items-center gap-1.5">
            <EnergyInnovationTerminalLogo size="sm" showText={false} />
            <span>Energy Innovation Terminal · Public Open Records</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => handleNavigate('/')}
              className="px-4 py-1.5 rounded-lg text-xs font-bold bg-[#00E5FF] hover:bg-cyan-400 text-slate-950 transition-colors shadow-glow-cyan-sm cursor-pointer"
            >
              Get Started with Strategic Advisory &rarr;
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
