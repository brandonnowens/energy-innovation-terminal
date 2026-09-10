import React, { useState, useEffect } from 'react';
import {
  ShieldCheck, Award, Check, Copy, ExternalLink,
  Layers, Database, Zap, BookOpen, Activity, Compass,
  Cpu, Lock, FileText, X, RefreshCw
} from 'lucide-react';
import clsx from 'clsx';
import { EnergyInnovationTerminalLogo } from './EnergyInnovationTerminalLogo';
import { useTheme } from '../context/ThemeContext';

interface BrandonSignatureModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function BrandonSignatureModal({ isOpen, onClose }: BrandonSignatureModalProps) {
  const { isDark } = useTheme();
  const [copiedFormat, setCopiedFormat] = useState<string | null>(null);
  const [utcTime, setUtcTime] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setUtcTime(now.toUTCString().replace('GMT', 'UTC'));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  if (!isOpen) return null;

  const citationApa = `Clean Energy Research, LLC. (2026). U.S. Energy Innovation Database (Version 3.5.0) [Data set and software]. Energy Innovation Terminal. https://terminal.aixenergy.io`;
  
  const citationBibtex = `@misc{energyinnovation2026database,
  author = {{Clean Energy Research, LLC}},
  title = {U.S. Energy Innovation Database},
  year = {2026},
  publisher = {Clean Energy Research, LLC},
  url = {https://terminal.aixenergy.io},
  note = {Multi-agency cross-jurisdictional open public records intelligence covering 56,000+ public disbursements and 140+ funding authorities}
};`;

  const citationChicago = `Clean Energy Research, LLC. 2026. "U.S. Energy Innovation Database." Energy Innovation Terminal. https://terminal.aixenergy.io.`;

  const copyToClipboard = (text: string, format: string) => {
    navigator.clipboard.writeText(text);
    setCopiedFormat(format);
    setTimeout(() => setCopiedFormat(null), 2500);
  };

  const triggerReplaySplash = () => {
    onClose();
    window.dispatchEvent(new CustomEvent('replay-splash-screen'));
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/80 backdrop-blur-md transition-opacity animate-in fade-in"
        onClick={onClose}
      />

      {/* Modal Container */}
      <div
        className={clsx(
          "relative w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden border transition-all duration-200 z-10 my-auto",
          isDark
            ? "bg-[#090e1a] border-cyan-500/30 text-slate-100 shadow-xl"
            : "bg-white border-slate-200 text-slate-900 shadow-xl"
        )}
      >
        {/* Header */}
        <div className="relative px-6 py-5 bg-gradient-to-r from-[#04101e] via-[#08182b] to-[#04101e] border-b border-cyan-500/30">
          <div className="relative z-10 flex items-center justify-between">
            <div className="flex items-center gap-3.5">
              <div className="relative p-2 rounded-xl bg-cyan-950/60 border border-cyan-500/40">
                <EnergyInnovationTerminalLogo size="sm" showText={false} />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold tracking-widest text-cyan-400 uppercase">
                    Database Reference &amp; Public Provenance
                  </span>
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    OPEN PUBLIC RECORDS
                  </span>
                </div>
                <h3 className="text-lg font-bold tracking-tight text-white flex items-center gap-1.5 mt-0.5">
                  <span>U.S. Energy Innovation Database · Clean Energy Research, LLC</span>
                </h3>
              </div>
            </div>

            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6 max-h-[75vh] overflow-y-auto no-scrollbar">
          {/* Mission & Architectural Thesis */}
          <div className={clsx(
            "p-4 rounded-xl border",
            isDark ? "bg-white/[0.02] border-white/[0.08]" : "bg-slate-50 border-slate-200"
          )}>
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 shrink-0 mt-0.5 border border-cyan-500/20">
                <Award size={16} />
              </div>
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-1">
                  Public Open Records Compilation
                </h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  The <strong>U.S. Energy Innovation Database</strong> structures and harmonizes publicly available energy innovation funding disclosures across <strong>140+ federal, state, and utility authorities</strong>. Published and maintained by <strong>Clean Energy Research, LLC</strong> to provide capital allocators, project sponsors, and researchers with transparent visibility across the U.S. clean energy innovation ecosystem.
                </p>
              </div>
            </div>
          </div>

          {/* Verified Corpus Metrics Grid */}
          <div>
            <div className="text-[10.5px] font-mono uppercase tracking-wider text-slate-400 font-bold mb-2.5 flex items-center justify-between">
              <span>Public Open Records Telemetry &amp; Coverage</span>
              <span className="text-emerald-400 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Live Node
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
              <div className={clsx("p-3 rounded-xl border text-center", isDark ? "bg-white/[0.03] border-white/[0.06]" : "bg-slate-50 border-slate-200")}>
                <div className="text-lg font-black text-cyan-400 font-mono">56,000+</div>
                <div className="text-[10px] text-slate-400 font-medium mt-0.5">Tracked Awards</div>
              </div>

              <div className={clsx("p-3 rounded-xl border text-center", isDark ? "bg-white/[0.03] border-white/[0.06]" : "bg-slate-50 border-slate-200")}>
                <div className="text-lg font-black text-emerald-400 font-mono">$104B+</div>
                <div className="text-[10px] text-slate-400 font-medium mt-0.5">Public Capital</div>
              </div>

              <div className={clsx("p-3 rounded-xl border text-center", isDark ? "bg-white/[0.03] border-white/[0.06]" : "bg-slate-50 border-slate-200")}>
                <div className="text-lg font-black text-blue-400 font-mono">10,000+</div>
                <div className="text-[10px] text-slate-400 font-medium mt-0.5">Grid Projects</div>
              </div>

              <div className={clsx("p-3 rounded-xl border text-center", isDark ? "bg-white/[0.03] border-white/[0.06]" : "bg-slate-50 border-slate-200")}>
                <div className="text-lg font-black text-purple-400 font-mono">140+</div>
                <div className="text-[10px] text-slate-400 font-medium mt-0.5">Funders Indexed</div>
              </div>
            </div>
          </div>

          {/* Academic & Professional Citation */}
          <div className={clsx(
            "p-4 rounded-xl border",
            isDark ? "bg-white/[0.02] border-white/[0.08]" : "bg-slate-50 border-slate-200"
          )}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <BookOpen size={14} className="text-cyan-400" />
                <span className="text-xs font-bold text-slate-200">Academic &amp; Institutional Citation</span>
              </div>
              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={() => copyToClipboard(citationApa, 'apa')}
                  className={clsx(
                    "px-2 py-1 rounded text-[10px] font-mono font-semibold transition-all border flex items-center gap-1 cursor-pointer",
                    copiedFormat === 'apa'
                      ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                      : isDark ? "bg-slate-800 text-slate-300 border-slate-700 hover:text-white" : "bg-white text-slate-700 border-slate-300"
                  )}
                >
                  {copiedFormat === 'apa' ? <Check size={11} /> : <Copy size={11} />}
                  <span>{copiedFormat === 'apa' ? 'Copied APA' : 'Copy APA'}</span>
                </button>

                <button
                  type="button"
                  onClick={() => copyToClipboard(citationBibtex, 'bibtex')}
                  className={clsx(
                    "px-2 py-1 rounded text-[10px] font-mono font-semibold transition-all border flex items-center gap-1 cursor-pointer",
                    copiedFormat === 'bibtex'
                      ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                      : isDark ? "bg-slate-800 text-slate-300 border-slate-700 hover:text-white" : "bg-white text-slate-700 border-slate-300"
                  )}
                >
                  {copiedFormat === 'bibtex' ? <Check size={11} /> : <Copy size={11} />}
                  <span>{copiedFormat === 'bibtex' ? 'Copied BibTeX' : 'BibTeX'}</span>
                </button>

                <button
                  type="button"
                  onClick={() => copyToClipboard(citationChicago, 'chicago')}
                  className={clsx(
                    "px-2 py-1 rounded text-[10px] font-mono font-semibold transition-all border flex items-center gap-1 cursor-pointer",
                    copiedFormat === 'chicago'
                      ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                      : isDark ? "bg-slate-800 text-slate-300 border-slate-700 hover:text-white" : "bg-white text-slate-700 border-slate-300"
                  )}
                >
                  {copiedFormat === 'chicago' ? <Check size={11} /> : <Copy size={11} />}
                  <span>{copiedFormat === 'chicago' ? 'Copied Chicago' : 'Chicago'}</span>
                </button>
              </div>
            </div>

            <p className="text-[11px] font-mono p-2.5 rounded-lg bg-black/40 border border-white/5 text-slate-300 leading-relaxed break-words select-all">
              {citationApa}
            </p>
          </div>

          {/* Legal Non-Affiliation & Contributor Safe Harbor Notice */}
          <div className={clsx(
            "p-3.5 rounded-xl border text-[11px] leading-relaxed",
            isDark ? "bg-amber-950/20 border-amber-500/30 text-amber-200/90" : "bg-amber-50 border-amber-200 text-amber-900"
          )}>
            <div className="font-bold mb-1 flex items-center gap-1.5 text-amber-400">
              <ShieldCheck size={14} className="text-amber-400 shrink-0" />
              <span className="uppercase tracking-wider text-[10px] font-mono">Independent Public Research Safe Harbor</span>
            </div>
            <p className="text-[11px]">
              This terminal is an independent research, academic, and analytical initiative developed outside of any official government capacity. It is not an official tool, service, or publication of any state or federal governmental entity. All data is sourced exclusively from open public records, official disclosure filings, and public databases. Contributing researchers participate strictly in a personal research capacity without representing any public employer or agency.
            </p>
          </div>

          {/* AIxEnergy Link Card */}
          <div className={clsx(
            "p-3.5 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3",
            isDark ? "bg-white/[0.02] border-cyan-500/25" : "bg-slate-50 border-slate-200"
          )}>
            <div className="flex items-center gap-3 min-w-0">
              <img
                src="/aixenergy-logo.webp"
                alt="AIxEnergy"
                className="w-8 h-8 rounded-full object-cover shrink-0 ring-1 ring-cyan-500/40 shadow-sm"
              />
              <div className="min-w-0">
                <div className="text-xs font-bold text-slate-100 flex items-center gap-1.5">
                  <span>AIxEnergy</span>
                </div>
                <div className="text-[11px] text-slate-400 truncate">
                  AI-driven intelligence for clean energy transition &amp; infrastructure
                </div>
              </div>
            </div>
            <a
              href="https://aixenergy.io"
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-1.5 rounded-lg text-xs font-bold bg-cyan-600 hover:bg-cyan-500 text-white flex items-center justify-center gap-1.5 shrink-0 transition-colors shadow-xs"
            >
              <span>Visit aixenergy.io</span>
              <span>↗</span>
            </a>
          </div>
        </div>

        {/* Modal Footer */}
        <div className={clsx(
          "px-6 py-3.5 border-t flex flex-col sm:flex-row items-center justify-between gap-3 text-xs",
          isDark ? "bg-[#060a14] border-white/[0.08]" : "bg-slate-50 border-slate-200"
        )}>
          <div className="text-[10px] font-mono text-slate-400 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span>Terminal Clock: <strong className="text-slate-300">{utcTime || 'UTC Live'}</strong></span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={triggerReplaySplash}
              className={clsx(
                "px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all border cursor-pointer",
                isDark
                  ? "bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border-cyan-500/30"
                  : "bg-cyan-50 hover:bg-cyan-100 text-cyan-800 border-cyan-200"
              )}
            >
              <RefreshCw size={12} />
              <span>Replay Intro Splash</span>
            </button>

            <button
              type="button"
              onClick={onClose}
              className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-white text-slate-900 hover:bg-slate-200 transition-colors shadow-xs cursor-pointer"
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
