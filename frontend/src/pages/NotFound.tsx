import React from 'react';
import { Link } from 'react-router-dom';
import { Compass, Search, Map, Home, ArrowRight } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-[70hv] flex flex-col items-center justify-center text-center px-4 py-16">
      <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 mb-6 shadow-lg shadow-cyan-500/5">
        <Compass size={32} className="animate-pulse" />
      </div>

      <span className="px-3 py-1 rounded-full text-xs font-mono font-semibold bg-slate-800 text-cyan-400 border border-slate-700/60 mb-3">
        404 : TERMINAL ROUTE NOT FOUND
      </span>

      <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight max-w-lg mb-3">
        Requested Intelligence Module Not Located
      </h1>

      <p className="text-slate-500 dark:text-slate-400 text-sm sm:text-base max-w-md mb-8 leading-relaxed">
       The requested resource path does not exist or has been relocated within the Energy Innovation Terminal registry.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full max-w-xl mb-8">
        <Link
          to="/"
          className="flex items-center gap-2.5 p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-cyan-500/40 text-left transition-all group"
        >
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-500 group-hover:bg-cyan-500 group-hover:text-white transition-colors">
            <Home size={18} />
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-900 dark:text-slate-200">Grant Matcher</div>
            <div className="text-[11p] text-slate-500">Return to home</div>
          </div>
        </Link>

        <Link
          to="/opportunities"
          className="flex items-center gap-2.5 p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-cyan-500/40 text-left transition-all group"
        >
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-500 group-hover:bg-emerald-500 group-hover:text-white transition-colors">
            <Search size={18} />
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-900 dark:text-slate-200">Opportunities</div>
            <div className="text-[11px] text-slate-500">Explore solicitations</div>
          </div>
        </Link>

        <Link
          to="/awards"
          className="flex items-center gap-2.5 p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-cyan-500/40 text-left transition-all group"
        >
          <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-500 group-hover:bg-indigo-500 group-hover:text-white transition-colors">
            <Map size={18} />
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-900 dark:text-slate-200">Award Map</div>
            <div className="text-[11px] text-slate-500">54k+ grant awards</div>
          </div>
        </Link>
      </div>

      <Link
        to="/"
        className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-900 dark:bg-cyan-500 text-white dark:text-slate-950 text-xs font-bold shadow-md hover:opacity-90 transition-opacity"
      >
        <span>Back to Terminal Dashboard</span>
        <ArrowRight size={14} />
      </Link>
    </div>
  );
}
