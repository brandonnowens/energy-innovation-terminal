import React, { useState, useEffect, useCallback } from 'react';
import { EnergyInnovationTerminalLogo } from './EnergyInnovationTerminalLogo';
import { ShieldCheck, Database, Layers, ArrowRight, Zap } from 'lucide-react';
import clsx from 'clsx';

interface SplashScreenProps {
  onComplete?: () => void;
  forceShow?: boolean;
}

export function SplashScreen({ onComplete, forceShow = false }: SplashScreenProps) {
  const [phase, setPhase] = useState<'intro' | 'loading' | 'indexing' | 'ready' | 'exit'>('intro');
  const [progress, setProgress] = useState(12);
  const [statusText, setStatusText] = useState('INITIALIZING NEURAL TELEMETRY ENGINE...');
  const [visible, setVisible] = useState(true);
  const [canSkip, setCanSkip] = useState(false);

  const finishSplash = useCallback(() => {
    setPhase('exit');
    setTimeout(() => {
      setVisible(false);
      if (onComplete) onComplete();
    }, 450);
  }, [onComplete]);

  // Listen for custom replay event
  useEffect(() => {
    const handleReplay = () => {
      setVisible(true);
      setPhase('intro');
      setProgress(12);
      setStatusText('INITIALIZING NEURAL TELEMETRY ENGINE...');
    };
    window.addEventListener('replay-splash-screen', handleReplay);
    return () => window.removeEventListener('replay-splash-screen', handleReplay);
  }, []);

  // Keyboard shortcut listener (Space, Enter, Esc to enter immediately)
  useEffect(() => {
    if (!visible) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === ' ' || e.key === 'Enter' || e.key === 'Escape') {
        e.preventDefault();
        finishSplash();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [visible, finishSplash]);

  useEffect(() => {
    if (!visible) return;

    // Enable skip after brief moment
    const skipTimer = setTimeout(() => setCanSkip(true), 300);

    // Stage 1: Initializing
    const t1 = setTimeout(() => {
      setProgress(38);
      setStatusText('CONNECTING TO MULTI-AGENCY CORPUS (140+ FUNDERS & AGENCIES)...');
      setPhase('loading');
    }, 350);

    // Stage 2: Indexing
    const t2 = setTimeout(() => {
      setProgress(76);
      setStatusText('INDEXING 56,413 AWARDS · $104.16B CAPITAL FLOWS · 10,250 GRID PROJECTS...');
      setPhase('indexing');
    }, 850);

    // Stage 3: Verification & Ready
    const t3 = setTimeout(() => {
      setProgress(100);
      setStatusText('TERMINAL READY · VERIFIED CROSS-AGENCY CORPUS ACTIVE');
      setPhase('ready');
    }, 1400);

    // Stage 4: Automatic exit
    const t4 = setTimeout(() => {
      finishSplash();
    }, 1900);

    return () => {
      clearTimeout(skipTimer);
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
      clearTimeout(t4);
    };
  }, [visible, finishSplash]);

  if (!visible) return null;

  return (
    <div
      onClick={finishSplash}
      className={clsx(
        "fixed inset-0 z-[99999] flex flex-col items-center justify-center bg-[#050813] text-white select-none cursor-pointer transition-all duration-500 ease-out backdrop-blur-3xl",
        phase === 'exit'
          ? "opacity-0 scale-105 pointer-events-none"
          : "opacity-100 scale-100"
      )}
    >
      {/* Dynamic Ambient Luxury Lighting */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-[550px] h-[550px] rounded-full bg-cyan-500/15 blur-[120px] animate-pulse" />
        <div className="absolute -bottom-40 -right-40 w-[550px] h-[550px] rounded-full bg-emerald-500/15 blur-[120px] animate-pulse" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] rounded-full bg-cyan-500/5 blur-[140px]" />
        {/* Subtle grid mesh */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)] opacity-40" />
      </div>

      {/* Center Branding & Telemetry */}
      <div className="relative z-10 flex flex-col items-center max-w-xl px-6 text-center">
        {/* Pulsing Breathing Brand Seal */}
        <div className="relative mb-6 group">
          <div className="absolute -inset-6 rounded-3xl bg-gradient-to-r from-cyan-400/30 via-emerald-400/20 to-blue-500/30 blur-2xl animate-pulse" />
          <div className="relative p-3.5 rounded-3xl bg-gradient-to-b from-[#0c1322] to-[#060a14] border border-cyan-500/30 shadow-[0_0_40px_rgba(0,210,255,0.25)] backdrop-blur-xl transition-transform duration-300 group-hover:scale-105">
            <EnergyInnovationTerminalLogo size="2xl" showText={false} />
          </div>
        </div>

        {/* Title */}
        <div className="flex items-center tracking-tight font-black text-2xl sm:text-3xl md:text-4xl mb-1.5 drop-shadow-[0_2px_10px_rgba(0,0,0,0.5)]">
          <span className="text-white">Energy</span>
          <span className="bg-gradient-to-r from-[#00D2FF] via-[#00F5A0] to-[#00F5D4] bg-clip-text text-transparent ml-2 drop-shadow-[0_0_20px_rgba(0,210,255,0.5)]">
            Innovation Terminal
          </span>
        </div>

        {/* Subtitle */}
        <div className="text-[10.5px] sm:text-xs font-mono tracking-[0.22em] text-slate-400 uppercase font-semibold mb-7">
          Upstream Energy Innovation &amp; Capital Intelligence Terminal
        </div>

        {/* Multi-Segment High-Tech Progress Bar */}
        <div className="w-72 sm:w-96 h-2 bg-slate-900/90 rounded-full overflow-hidden mb-3.5 p-[1px] border border-white/15 shadow-[inset_0_1px_3px_rgba(0,0,0,0.8)]">
          <div
            className="h-full rounded-full bg-gradient-to-r from-cyan-400 via-emerald-400 to-cyan-300 shadow-[0_0_16px_rgba(0,245,160,0.8)] transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Live Telemetry Ticker Text */}
        <div className="flex items-center gap-2.5 text-[10.5px] font-mono text-cyan-300/95 font-bold tracking-wider h-6 px-3 py-1 rounded-full bg-cyan-950/40 border border-cyan-500/20 shadow-inner">
          <span className="relative flex h-2 w-2 shrink-0">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00F5A0] opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[#00F5A0]" />
          </span>
          <span className="truncate">{statusText}</span>
        </div>

        {/* Live Data Telemetry Pills */}
        <div className="mt-6 flex items-center justify-center gap-2 flex-wrap text-[10px] font-mono text-slate-400">
          <span className="px-2.5 py-1 rounded-md bg-white/[0.04] border border-white/[0.08] flex items-center gap-1.5">
            <Database size={11} className="text-cyan-400" />
            56,413 Awards
          </span>
          <span className="px-2.5 py-1 rounded-md bg-white/[0.04] border border-white/[0.08] flex items-center gap-1.5">
            <Zap size={11} className="text-emerald-400" />
            $104.16B Capital
          </span>
          <span className="px-2.5 py-1 rounded-md bg-white/[0.04] border border-white/[0.08] flex items-center gap-1.5">
            <Layers size={11} className="text-cyan-400" />
            140+ Agencies &amp; Utilities
          </span>
        </div>

        {/* Signature Creator Attribution & Skip CTA */}
        <div className="mt-8 flex flex-col items-center gap-2">
          <div className="text-[10px] font-mono text-slate-400 flex items-center gap-1.5">
            <ShieldCheck size={12} className="text-emerald-400" />
            <span>Curated &amp; Engineered by <strong className="text-slate-200">Brandon N. Owens</strong></span>
          </div>

          {canSkip && (
            <div className="mt-1 text-[9.5px] font-mono text-slate-500 flex items-center gap-1 hover:text-cyan-400 transition-colors">
              <span>Click anywhere or press <kbd className="px-1 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">Space</kbd> to enter</span>
              <ArrowRight size={10} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
