import { apiFetch } from '../api/client';
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Bell, X, Plus, Trash2, CheckCircle2, Search, Sliders, Mail, Radio, ExternalLink 
} from 'lucide-react';

interface RealTimeAlertsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const RealTimeAlertsModal: React.FC<RealTimeAlertsModalProps> = ({ isOpen, onClose }) => {
  const queryClient = useQueryClient();
  const [name, setName] = useState('');
  const [keywords, setKeywords] = useState('');
  const [selectedAgencies, setSelectedAgencies] = useState<string[]>(['DOE', 'ARPA-E', 'CEC']);
  const [minFunding, setMinFunding] = useState<number>(1000000);
  const [successMsg, setSuccessMsg] = useState('');

  const { data: triggers = [], isLoading } = useQuery({
    queryKey: ['alert-triggers'],
    queryFn: async () => {
      const res = await apiFetch('/api/alerts/triggers');
      if (!res.ok) throw new Error('Failed to load alert triggers');
      return res.json();
    },
    enabled: isOpen
  });

  const { data: liveMatches = [] } = useQuery({
    queryKey: ['live-radar-matches', keywords, minFunding],
    queryFn: async () => {
      const res = await apiFetch(`/api/alerts/live-matches?keywords=${encodeURIComponent(keywords)}&min_funding=${minFunding}`);
      if (!res.ok) return [];
      return res.json();
    },
    enabled: isOpen
  });

  const createTriggerMutation = useMutation({
    mutationFn: async (payload: any) => {
      const res = await apiFetch('/api/alerts/triggers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error('Failed to create trigger');
      return res.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['alert-triggers'] });
      setSuccessMsg(data.message);
      setName('');
      setTimeout(() => setSuccessMsg(''), 4000);
    }
  });

  const deleteTriggerMutation = useMutation({
    mutationFn: async (id: number) => {
      const res = await apiFetch(`/api/alerts/triggers/${id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Failed to delete trigger');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alert-triggers'] });
    }
  });

  if (!isOpen) return null;

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name) return;
    createTriggerMutation.mutate({
      name,
      keywords,
      target_agencies: selectedAgencies,
      min_funding: minFunding,
      email_destination: "In-Terminal Daily Feed",
      frequency: "in_terminal_daily"
    });
  };

  const agenciesList = ['DOE', 'ARPA-E', 'CEC', 'MassCEC', 'State Energy Authorities', 'NSF', 'EPA'];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-4xl max-h-[90vh] flex flex-col rounded-2xl border dark:border-white/10 border-slate-200 dark:bg-[#0b1329] bg-white shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b dark:border-white/10 border-slate-200 dark:bg-[#070d1e] bg-slate-50">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-500">
              <Radio className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20">
                  In-Terminal Opportunity Radar
                </span>
                <span className="text-xs dark:text-slate-400 text-slate-500 font-medium">
                  Active In-App Surveillance (Zero Inbox Spam)
                </span>
              </div>
              <h2 className="text-lg font-bold dark:text-white text-slate-900 mt-0.5">
                Smart Radar Watchlists & Custom Triggers
              </h2>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-slate-200 dark:hover:bg-white/10 text-slate-400 hover:text-slate-600 dark:hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {successMsg && (
            <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 text-xs font-semibold flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          {/* Trigger Builder Form */}
          <form onSubmit={handleCreate} className="p-5 rounded-xl border dark:border-white/10 border-slate-200 dark:bg-[#0e1626] bg-slate-50 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider dark:text-slate-300 text-slate-700 flex items-center gap-2">
                <Plus className="w-4 h-4 text-cyan-500" />
                Configure New In-Terminal Watchlist Trigger
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-xs font-semibold dark:text-slate-300 text-slate-700">Trigger Name</label>
                <input 
                  type="text"
                  placeholder="e.g. Clean Hydrogen & Storage > $2M"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg dark:bg-[#070d1e] bg-white border dark:border-white/10 border-slate-200 dark:text-white text-slate-900 outline-none"
                  required
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold dark:text-slate-300 text-slate-700">Keywords to Track</label>
                <input 
                  type="text"
                  placeholder="e.g. hydrogen, PEM, electrolyzer, storage"
                  value={keywords}
                  onChange={e => setKeywords(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-lg dark:bg-[#070d1e] bg-white border dark:border-white/10 border-slate-200 dark:text-white text-slate-900 outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold dark:text-slate-300 text-slate-700">Minimum Total Funding</label>
                <select 
                  value={minFunding}
                  onChange={e => setMinFunding(Number(e.target.value))}
                  className="w-full px-3 py-2 text-xs rounded-lg dark:bg-[#070d1e] bg-white border dark:border-white/10 border-slate-200 dark:text-white text-slate-900 outline-none"
                >
                  <option value="0">Any Funding Amount</option>
                  <option value="1000000">$1,000,000+</option>
                  <option value="5000000">$5,000,000+</option>
                  <option value="10000000">$10,000,000+</option>
                  <option value="25000000">$25,000,000+</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold dark:text-slate-300 text-slate-700">Delivery Channel</label>
                <div className="w-full px-3 py-2 text-xs rounded-lg dark:bg-[#070d1e] bg-white border dark:border-white/10 border-slate-200 dark:text-cyan-400 text-cyan-600 font-semibold flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                  In-Terminal Daily Cockpit Feed (No Email Spam)
                </div>
              </div>
            </div>

            {/* Target Agencies Multi-Select */}
            <div className="space-y-1.5 pt-1">
              <label className="text-xs font-semibold dark:text-slate-300 text-slate-700">Target Agencies</label>
              <div className="flex flex-wrap gap-2">
                {agenciesList.map(ag => {
                  const selected = selectedAgencies.includes(ag);
                  return (
                    <button
                      type="button"
                      key={ag}
                      onClick={() => {
                        setSelectedAgencies(prev => 
                          selected ? prev.filter(x => x !== ag) : [...prev, ag]
                        );
                      }}
                      className={`px-3 py-1 rounded-lg text-xs font-semibold transition cursor-pointer ${
                        selected 
                          ? 'bg-cyan-500/20 text-cyan-500 border border-cyan-500/40' 
                          : 'dark:bg-white/5 bg-slate-200 text-slate-600 dark:text-slate-400'
                      }`}
                    >
                      {selected ? '✓ ' : '+ '}{ag}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                type="submit"
                disabled={createTriggerMutation.isPending}
                className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition flex items-center gap-2"
              >
                <Radio className="w-3.5 h-3.5" />
                {createTriggerMutation.isPending ? 'Activating...' : 'Save In-Terminal Radar Watchlist'}
              </button>
            </div>
          </form>

          {/* Active Triggers List */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider dark:text-slate-400 text-slate-600">
              Active In-Terminal Radar Watchlists ({triggers.length})
            </h3>

            {triggers.length === 0 ? (
              <div className="p-6 text-center rounded-xl border border-dashed dark:border-white/10 border-slate-200 text-xs text-slate-500">
                No custom watchlist triggers configured yet. Create one above to track solicitations on your cockpit!
              </div>
            ) : (
              <div className="grid gap-3">
                {triggers.map((t: any) => (
                  <div key={t.id} className="p-4 rounded-xl border dark:border-white/10 border-slate-200 dark:bg-[#0e1626] bg-slate-50 flex items-center justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                        <span className="font-bold text-sm dark:text-white text-slate-900">{t.name}</span>
                        <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-500 border border-cyan-500/20">
                          {t.matches_count} matching solicitations
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-xs dark:text-slate-400 text-slate-500">
                        <span>Keywords: {t.keywords || 'All'}</span>
                        <span>Min Funding: ${Number(t.min_funding).toLocaleString()}</span>
                        <span className="text-cyan-500 font-medium">Channel: In-Terminal Daily Cockpit</span>
                      </div>
                    </div>

                    <button
                      onClick={() => deleteTriggerMutation.mutate(t.id)}
                      className="p-2 rounded-lg hover:bg-red-500/10 text-slate-400 hover:text-red-500 transition"
                      title="Delete Trigger"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Live Radar Matches Preview */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider dark:text-slate-400 text-slate-600 flex items-center gap-2">
              <Radio className="w-4 h-4 text-emerald-500" />
              Live Matched Opportunities ({liveMatches.length})
            </h3>

            <div className="border dark:border-white/10 border-slate-200 rounded-xl overflow-hidden divide-y dark:divide-white/10 divide-slate-200">
              {liveMatches.slice(0, 5).map((m: any) => (
                <div key={m.id} className="p-3 dark:bg-[#070d1e] bg-white flex items-center justify-between gap-3 text-xs">
                  <div>
                    <div className="font-bold dark:text-white text-slate-900 line-clamp-1">{m.name}</div>
                    <div className="text-[11px] dark:text-slate-400 text-slate-500">
                      {m.agency} | {m.solicitation_number} | Due: {m.due_date_display || 'Open'}
                    </div>
                  </div>
                  <div className="font-bold text-emerald-500 shrink-0">
                    ${Number(m.total_funding || 0).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Footer */}
        <div className="p-4 border-t dark:border-white/10 border-slate-200 dark:bg-[#070d1e] bg-slate-50 flex items-center justify-end text-xs">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg dark:bg-white/10 bg-slate-200 dark:text-white text-slate-800 font-semibold transition"
          >
            Done
          </button>
        </div>

      </div>
    </div>
  );
};
