import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { Loader2, ArrowRight, Plus, RefreshCw, Edit, AlertTriangle } from 'lucide-react';
import clsx from 'clsx';
import { OrgLogo } from '../components/OrgLogo';

const changeTypeConfig: Record<string, { icon: React.ReactNode; color: string; label: string }> = {
  new: { icon: <Plus size={14} />, color: 'text-indigo-600 bg-indigo-50 border-indigo-200', label: 'New' },
  status_change: { icon: <RefreshCw size={14} />, color: 'text-blue-600 bg-blue-50 border-blue-200', label: 'Status Change' },
  revision: { icon: <Edit size={14} />, color: 'text-amber-600 bg-amber-50 border-amber-200', label: 'Revision' },
  field_change: { icon: <Edit size={14} />, color: 'text-purple-600 bg-purple-50 border-purple-200', label: 'Field Change' },
};

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '';
  try {
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' });
  } catch { return dateStr; }
}

export default function Updates() {
  const [filter, setFilter] = useState('');
  const { data: updates, isLoading, isError } = useQuery({
    queryKey: ['updates'],
    queryFn: () => api.getUpdates()
  });

  const items = (updates as any[])?.filter((u: any) => !filter || u.change_type === filter) || [];

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Standard Page Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
              <RefreshCw size={12} className="text-blue-600" />
              <span>Real-Time Feed Audit</span>
            </span>
            <span className="text-xs text-slate-300">|</span>
            <span className="text-xs font-semibold text-slate-500">Live Ingestion Telemetry</span>
            <span className="text-xs text-slate-300">|</span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span>Database Synced: Sep 1, 2026</span>
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2.5">
            Updates &amp; Live Ingestion Feed
          </h1>
          <p className="text-[13px] sm:text-sm text-slate-500 max-w-3xl mt-1 leading-relaxed">
            Chronological audit feed of changes, amendments, and additions across indexed funding agency datasets.
          </p>
        </div>
        <select
          className="px-3 h-9 border border-slate-200 rounded-lg shadow-2xs text-[13px] bg-white focus:ring-1 focus:ring-indigo-500 outline-none text-slate-700 font-medium"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="">All Changes</option>
          <option value="new">New Opportunities</option>
          <option value="status_change">Status Changes</option>
          <option value="revision">Revisions</option>
          <option value="field_change">Field Changes</option>
        </select>
      </div>

      <div className="bg-white rounded-lg border border-slate-200/80 shadow-[var(--shadow-xs)] overflow-hidden">
        {isLoading && (
          <div className="p-12 flex justify-center text-slate-300"><Loader2 className="animate-spin" size={24} /></div>
        )}
        {isError && (
          <div className="p-8 text-center text-[13px] text-red-500">Failed to load updates.</div>
        )}
        {items.length === 0 && !isLoading && (
          <div className="p-8 text-center text-[13px] text-slate-400">No changes detected yet. Run ingestion to detect updates.</div>
        )}
        <div className="divide-y divide-slate-100">
          {items.map((u: any) => {
            const cfg = changeTypeConfig[u.change_type] || changeTypeConfig.field_change;
            return (
              <div key={u.id} className="p-4 hover:bg-slate-50/50 transition-colors">
                <div className="flex items-start gap-3">
                  <div className={clsx('p-1.5 rounded border shrink-0', cfg.color)}>
                    {cfg.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className="text-[10px] font-medium px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">{u.entity_type}</span>
                      {u.agency && <OrgLogo org={u.agency} size="xs" />}
                      <span className="font-medium text-[13px] text-slate-900">{u.entity_name || u.entity_id}</span>
                    </div>
                    {u.field_name && (
                      <div className="text-[12px] text-slate-600">
                        <span className="font-medium">{u.field_name}</span>
                        {u.old_value && u.new_value && (
                          <span>: <span className="text-slate-400 line-through">{u.old_value}</span> <ArrowRight size={12} className="inline text-slate-400 mx-1" /> <span className="text-indigo-600">{u.new_value}</span></span>
                        )}
                      </div>
                    )}
                    {!u.field_name && u.change_type === 'new' && (
                      <div className="text-[12px] text-indigo-600">New opportunity detected</div>
                    )}
                  </div>
                  <div className="text-[11px] text-slate-400 shrink-0">{formatDate(u.detected_at)}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
