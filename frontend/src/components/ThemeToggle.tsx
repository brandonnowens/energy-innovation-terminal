import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import clsx from 'clsx';

export const ThemeToggle: React.FC<{ className?: string }> = ({ className }) => {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className={clsx(
        "inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer border shadow-2xs",
        isDark
          ? "bg-slate-800/70 hover:bg-slate-800 text-slate-200 border-white/10 hover:border-slate-600"
          : "bg-slate-100 hover:bg-slate-200 text-slate-800 border-slate-200 hover:border-slate-300",
        className
      )}
      title={`Switch to ${isDark ? 'Light' : 'Dark'} Mode`}
      aria-label="Toggle Theme"
    >
      <div className="relative w-3.5 h-3.5 flex items-center justify-center">
        {isDark ? (
          <Moon size={13} className="text-slate-300" />
        ) : (
          <Sun size={13} className="text-slate-600" />
        )}
      </div>
      <span className="text-xs font-medium hidden sm:inline">
        {isDark ? 'Dark' : 'Light'}
      </span>
    </button>
  );
};

