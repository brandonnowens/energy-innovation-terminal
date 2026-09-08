import React, { useState, useRef, useEffect } from 'react';
import {
  LogIn, LogOut, Settings, ShieldCheck, ChevronDown, Sparkles, Crown
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export function UserMenu() {
  const {
    user,
    isAuthenticated,
    logout,
    openAuthModal,
    openAccountModal,
    openMembershipModal
  } = useAuth();

  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (!isAuthenticated || !user) {
    return null;
  }

  const initial = user.full_name
    ? user.full_name.charAt(0).toUpperCase()
    : user.email.charAt(0).toUpperCase();

  const displayName = user.full_name || user.email.split('@')[0];

  return (
    <div className="relative" ref={menuRef}>
      <button
        type="button"
        onClick={() => setMenuOpen(!menuOpen)}
        className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-800/70 dark:hover:bg-slate-800 border border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-200 transition-all cursor-pointer group shadow-2xs"
      >
        {/* Subtle Executive Avatar */}
        <div className="w-5 h-5 rounded-md bg-slate-700 text-white font-bold text-[10px] flex items-center justify-center">
          {initial}
        </div>

        {/* User details */}
        <div className="text-left hidden sm:block">
          <div className="text-xs font-semibold text-slate-800 dark:text-slate-200 leading-tight truncate max-w-[120px]">
            {displayName}
          </div>
        </div>

        <ChevronDown size={13} className={`text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-200 transition-transform ${menuOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {menuOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-[#0e1422] rounded-xl shadow-xl border border-slate-200 dark:border-white/10 py-1.5 z-50 animate-in fade-in zoom-in-95 duration-100">
          {/* User Header */}
          <div className="px-3.5 py-2.5 border-b border-slate-100 dark:border-white/5 bg-slate-50/50 dark:bg-black/20">
            <div className="text-xs font-bold text-slate-900 dark:text-white truncate">
              {user.full_name || 'Innovator Account'}
            </div>
            <div className="text-[11px] text-slate-500 dark:text-slate-400 truncate mt-0.5 font-mono">
              {user.email}
            </div>
            <div className="mt-1.5 inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium text-[10px]">
              <ShieldCheck size={11} className="text-emerald-500" />
              <span>Full Access</span>
            </div>
          </div>

          {/* Menu Items */}
          <div className="py-1 px-1">
            <button
              type="button"
              onClick={() => {
                setMenuOpen(false);
                openAccountModal();
              }}
              className="w-full px-3 py-1.5 rounded-lg text-left text-xs font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/5 flex items-center gap-2 transition-colors cursor-pointer"
            >
              <Settings size={13} className="text-slate-400" />
              <span>Account Settings</span>
            </button>

            <button
              type="button"
              onClick={() => {
                setMenuOpen(false);
                openMembershipModal();
              }}
              className="w-full px-3 py-1.5 rounded-lg text-left text-xs font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/5 flex items-center gap-2 transition-colors cursor-pointer"
            >
              <Crown size={13} className="text-slate-400" />
              <span>Licensing Tiers</span>
            </button>
          </div>

          {/* Sign Out */}
          <div className="border-t border-slate-100 dark:border-white/5 pt-1 mt-1 px-1">
            <button
              type="button"
              onClick={() => {
                setMenuOpen(false);
                logout();
              }}
              className="w-full px-3 py-1.5 rounded-lg text-left text-xs font-medium text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/20 flex items-center gap-2 transition-colors cursor-pointer"
            >
              <LogOut size={13} />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}


