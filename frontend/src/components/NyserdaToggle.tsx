import React from 'react';
import clsx from 'clsx';
import { Layers } from 'lucide-react';
import { useNyserda } from '../context/NyserdaContext';
import { useTheme } from '../context/ThemeContext';

interface NyserdaToggleProps {
  variant?: 'header' | 'sidebar' | 'compact';
  className?: string;
}

export function NyserdaToggle({ variant = 'header', className }: NyserdaToggleProps) {
  const { includeNyserda, toggleNyserda } = useNyserda();
  const { isDark } = useTheme();

  if (variant === 'sidebar') {
    return (
      <div
        className={clsx(
          'px-2.5 py-2 rounded-lg border transition-all select-none',
          isDark
            ? 'bg-white/[0.03] border-white/[0.08] hover:border-cyan-500/30'
            : 'bg-slate-50 border-slate-200 hover:border-slate-300',
          className
        )}
      >
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            <div
              className={clsx(
                'w-6 h-6 rounded-md flex items-center justify-center shrink-0 transition-colors',
                includeNyserda
                  ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30'
                  : 'bg-slate-700/50 text-slate-400 border border-slate-600/40'
              )}
            >
              <Layers size={13} />
            </div>
            <div className="min-w-0">
              <div className="text-[11px] font-semibold text-slate-200 truncate flex items-center gap-1.5">
                <span>NYSERDA Scope</span>
              </div>
              <div className="text-[9.5px] text-slate-400 truncate font-mono">
                {includeNyserda ? 'Included in database' : 'Excluded from views'}
              </div>
            </div>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={includeNyserda}
            onClick={toggleNyserda}
            className={clsx(
              'relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-hidden',
              includeNyserda ? 'bg-cyan-500' : 'bg-slate-700'
            )}
            title={includeNyserda ? 'Click to exclude NYSERDA datasets' : 'Click to include NYSERDA datasets'}
          >
            <span
              aria-hidden="true"
              className={clsx(
                'pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out',
                includeNyserda ? 'translate-x-4' : 'translate-x-0'
              )}
            />
          </button>
        </div>
      </div>
    );
  }

  if (variant === 'compact') {
    return (
      <button
        type="button"
        onClick={toggleNyserda}
        className={clsx(
          'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-semibold transition-all border cursor-pointer select-none',
          includeNyserda
            ? isDark
              ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30 hover:bg-cyan-500/20'
              : 'bg-cyan-50 text-cyan-800 border-cyan-200 hover:bg-cyan-100'
            : isDark
              ? 'bg-slate-800/80 text-slate-400 border-slate-700 hover:text-slate-300'
              : 'bg-slate-100 text-slate-500 border-slate-200 hover:bg-slate-200',
          className
        )}
        title={includeNyserda ? 'NYSERDA included (Click to toggle)' : 'NYSERDA excluded (Click to toggle)'}
      >
        <span
          className={clsx(
            'w-1.5 h-1.5 rounded-full',
            includeNyserda ? 'bg-cyan-400 shadow-[0_0_6px_#06b6d4]' : 'bg-slate-500'
          )}
        />
        <span>NYSERDA</span>
        <span className="text-[9.5px] opacity-75 font-mono uppercase">
          {includeNyserda ? 'ON' : 'OFF'}
        </span>
      </button>
    );
  }

  // Default 'header' variant: Premium interactive pill switch
  return (
    <button
      type="button"
      onClick={toggleNyserda}
      className={clsx(
        'group inline-flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all border shadow-2xs cursor-pointer select-none',
        includeNyserda
          ? isDark
            ? 'bg-gradient-to-r from-cyan-950/40 to-slate-900 text-cyan-300 border-cyan-500/40 hover:border-cyan-400 shadow-[0_0_12px_rgba(6,182,212,0.12)]'
            : 'bg-gradient-to-r from-cyan-50 to-white text-cyan-900 border-cyan-200 hover:border-cyan-300'
          : isDark
            ? 'bg-slate-900/60 text-slate-400 border-white/10 hover:border-slate-700 hover:text-slate-300'
            : 'bg-slate-100/80 text-slate-500 border-slate-200 hover:bg-slate-100 hover:text-slate-700',
        className
      )}
      title={
        includeNyserda
          ? 'NYSERDA dataset active in terminal. Click to exclude NYSERDA.'
          : 'NYSERDA dataset excluded. Click to include NYSERDA in all modules.'
      }
    >
      <div className="flex items-center gap-1.5">
        <span
          className={clsx(
            'w-2 h-2 rounded-full transition-all duration-300',
            includeNyserda
              ? 'bg-cyan-400 shadow-[0_0_8px_#06b6d4] ring-2 ring-cyan-400/20'
              : 'bg-slate-500 ring-1 ring-slate-600/30'
          )}
        />
        <span className="font-bold tracking-tight text-[11.5px]">NYSERDA</span>
      </div>

      <div
        className={clsx(
          'relative inline-flex h-4 w-7 shrink-0 items-center rounded-full transition-colors duration-200 ease-in-out',
          includeNyserda
            ? 'bg-cyan-500'
            : isDark ? 'bg-slate-700' : 'bg-slate-300'
        )}
      >
        <span
          className={clsx(
            'inline-block h-3 w-3 transform rounded-full bg-white shadow-xs transition duration-200 ease-in-out',
            includeNyserda ? 'translate-x-3.5' : 'translate-x-0.5'
          )}
        />
      </div>
    </button>
  );
}
