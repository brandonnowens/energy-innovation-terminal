import React from 'react';
import { User, LogIn } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { ghostSignIn } from '../lib/ghostSignIn';
import clsx from 'clsx';

export function UserMenu() {
  const { ghostStatus, ghostMemberName, ghostMemberEmail } = useAuth();
  
  if (ghostStatus === 'authenticated') {
    const displayName = ghostMemberName || ghostMemberEmail?.split('@')[0] || 'User';
    const initial = displayName.charAt(0).toUpperCase();

    return (
      <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800/70 border border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-200 shadow-2xs">
        <div className="w-5 h-5 rounded-md bg-cyan-600 text-white font-bold text-[10px] flex items-center justify-center">
          {initial}
        </div>
        <div className="text-left hidden sm:block">
          <div className="text-xs font-semibold text-slate-800 dark:text-slate-200 leading-tight truncate max-w-[120px]">
            {displayName}
          </div>
        </div>
      </div>
    );
  }

  // Guest / Logged out state
  return (
    <button
      type="button"
      onClick={ghostSignIn}
      className={clsx(
        "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all border shadow-2xs cursor-pointer",
        "bg-cyan-600 hover:bg-cyan-500 text-white border-cyan-500 hover:border-cyan-400"
      )}
    >
      <LogIn size={13} className="text-white" />
      <span>Log In</span>
    </button>
  );
}
