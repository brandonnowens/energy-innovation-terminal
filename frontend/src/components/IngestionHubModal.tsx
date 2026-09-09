import { apiFetch } from '../api/client';
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  RefreshCw, X, CheckCircle2, AlertTriangle, Play, Clock, 
  Layers, Database, ShieldCheck, Activity, Radio, Cpu 
} from 'lucide-react';

interface IngestionHubModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const IngestionHubModal: React.FC<IngestionHubModalProps> = ({ isOpen, onClose }) => {
  const queryClient = useQueryClient();
  const [syncingWorker, setSyncingWorker] = useState<string | null>(null);
  const [successBanner, setSuccessBanner] = useState<string | null>(null);

  const { data: pipelineStatus, isLoading, refetch } = useQuery({
    queryKey: ['ingestion-status'],
    queryFn: async () => {
      const res = await apiFetch('/api/ingestion/status');
      if (!res.ok) throw new Error('Failed to fetch ingestion status');
      return res.json();
    },
    enabled: isOpen,
    refetchInterval: 15000 // Refresh every 15s when modal is open
  });

  const syncMutation = useMutation({
    mutationFn: async (sourceCode: string) => {
      setSyncingWorker(sourceCode);
      const res = await apiFetch(`/api/ingestion/run/${sourceCode}`, { method: 'POST' });
      if (!res.ok) throw new Error('Sync failed');
      return res.json();
    },
    onSuccess: (data) => {
      setSyncingWorker(null);
      queryClient.invalidateQueries({ queryKey: ['ingestion-status'] });
      queryClient.invalidateQueries({ queryKey: ['opportunities'] });
      setSuccessBanner(`Sync Complete! Ingested ${data.total_new_opportunities_inserted || 0} new solicitations, updated ${data.total_existing_updated || 0} records in ${data.timestamp?.slice(11, 19)} UTC.`);
      setTimeout(() => setSuccessBanner(null), 5000);
    },
    onError: (err) => {
      setSyncingWorker(null);
      alert(`Sync error: ${err.message}`);
    }
  });

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-5xl max-h-[92vh] flex flex-col rounded-2xl border dark:border-white/10 border-slate-200 dark:bg-[#0b1329] bg-white shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b dark:border-white/10 border-slate-200 dark:bg-[#070d1e] bg-slate-50">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-500">
              <Cpu className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  Continuous Ingestion Workers Active (60m Cycle)
                </span>
                <span className="text-xs font-mono dark:text-slate-400 text-slate-500">
                  PostgreSQL 18 Cluster Ingest Sink
                </span>
              </div>
              <h2 className="text-lg font-bold dark:text-white text-slate-900 mt-0.5">
                Automated Grants.gov, State Feeds &amp; Docket Ingestion Hub
              </h2>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => syncMutation.mutate('all')}
              disabled={!!syncingWorker}
              className="flex items-center gap-2 px-3.5 py-1.5 text-xs font-bold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition disabled:opacity-50 cursor-pointer shadow-2xs"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${syncingWorker ? 'animate-spin' : ''}`} />
              {syncingWorker === 'all' ? 'Ingesting All Feeds...' : 'Sync All Feeds Now'}
            </button>
            <button 
              onClick={onClose}
              className="p-1.5 rounded-lg hover:bg-slate-200 dark:hover:bg-white/10 text-slate-400 hover:text-slate-600 dark:hover:text-white transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {successBanner && (
            <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 text-xs font-semibold flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{successBanner}</span>
            </div>
          )}

          {/* Active Ingestion Workers Grid */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider dark:text-slate-400 text-slate-600 flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-500" />
              Surveillance Scrapers &amp; API Pollers
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {pipelineStatus?.workers?.map((w: any) => (
                <div key={w.code} className="p-4 rounded-xl border dark:border-white/10 border-slate-200 dark:bg-[#0e1626] bg-slate-50 flex flex-col justify-between space-y-3">
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                        {w.jurisdiction} · {w.agency}
                      </span>
                      <span className="flex items-center gap-1 text-[11px] font-bold text-emerald-500">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                        {w.status.toUpperCase()}
                      </span>
                    </div>
                    <h4 className="font-bold text-sm dark:text-white text-slate-900 line-clamp-1">{w.name}</h4>
                    <p className="text-[11px] dark:text-slate-400 text-slate-600">
                      Polls every {w.poll_interval_minutes}m · Next check: {w.next_run ? new Date(w.next_run).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Pending'}
                    </p>
                  </div>

                  <div className="pt-2 border-t dark:border-white/5 border-slate-200 flex items-center justify-between">
                    <span className="text-[10px] dark:text-slate-500 text-slate-400">
                      Last sync: {w.last_run ? new Date(w.last_run).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Never'}
                    </span>
                    <button
                      onClick={() => syncMutation.mutate(w.code)}
                      disabled={syncingWorker === w.code}
                      className="px-2.5 py-1 text-[11px] font-bold rounded-md dark:bg-white/10 bg-slate-200 hover:dark:bg-white/20 hover:bg-slate-300 dark:text-white text-slate-900 transition flex items-center gap-1 cursor-pointer"
                    >
                      <Play className="w-3 h-3 text-emerald-500" />
                      {syncingWorker === w.code ? 'Syncing...' : 'Run Sync'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Audit Logs Stream */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider dark:text-slate-400 text-slate-600 flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-500" />
              Recent Ingestion Run Audit Logs
            </h3>

            <div className="border dark:border-white/10 border-slate-200 rounded-xl overflow-hidden divide-y dark:divide-white/10 divide-slate-200 text-xs">
              <div className="p-3 dark:bg-[#070d1e] bg-slate-100 grid grid-cols-12 font-bold dark:text-slate-400 text-slate-600">
                <span className="col-span-4">Source Worker</span>
                <span className="col-span-3">Timestamp</span>
                <span className="col-span-2">New Records</span>
                <span className="col-span-2">Updated</span>
                <span className="col-span-1 text-right">Status</span>
              </div>

              {pipelineStatus?.recent_runs?.map((run: any) => (
                <div key={run.id} className="p-3 dark:bg-[#0e1626] bg-white grid grid-cols-12 items-center dark:text-slate-300 text-slate-700">
                  <span className="col-span-4 font-bold dark:text-white text-slate-900 truncate">{run.source_name}</span>
                  <span className="col-span-3 font-mono text-[11px] dark:text-slate-400 text-slate-500">
                    {run.started_at ? new Date(run.started_at).toLocaleString() : '—'}
                  </span>
                  <span className="col-span-2 font-mono font-bold text-emerald-500">+{run.records_added || 0}</span>
                  <span className="col-span-2 font-mono text-cyan-500">{run.records_updated || 0}</span>
                  <span className="col-span-1 text-right">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${run.status === 'success' ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' : 'bg-red-500/10 text-red-500'}`}>
                      {run.status.toUpperCase()}
                    </span>
                  </span>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Footer */}
        <div className="p-4 border-t dark:border-white/10 border-slate-200 dark:bg-[#070d1e] bg-slate-50 flex items-center justify-between text-xs text-slate-500">
          <span>Continuous Worker Loop: APScheduler / Python 3.12 Daemon</span>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg dark:bg-white/10 bg-slate-200 dark:text-white text-slate-800 font-semibold transition"
          >
            Close Ingestion Hub
          </button>
        </div>

      </div>
    </div>
  );
};
