import React, { useState, useEffect } from 'react';
import {
  X, ShieldCheck, Check, Zap, Building2,
  Crown, ArrowUpRight, CheckCircle2, Loader2, Info
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api, MembershipManifest, TierInfo } from '../api/client';

export function MembershipModal() {
  const { membershipModalOpen, closeMembershipModal, user, refreshUser } = useAuth();
  const [manifest, setManifest] = useState<MembershipManifest | null>(null);
  const [loading, setLoading] = useState(false);
  const [upgrading, setUpgrading] = useState(false);
  const [successNotice, setSuccessNotice] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    if (membershipModalOpen) {
      setLoading(true);
      api.getMembership()
        .then(res => {
          if (isMounted) setManifest(res.membership_manifest);
        })
        .catch(err => console.error(err))
        .finally(() => {
          if (isMounted) setLoading(false);
        });
    }
    return () => {
      isMounted = false;
    };
  }, [membershipModalOpen]);

  if (!membershipModalOpen) return null;

  const handleMockUpgrade = async (tierId: string) => {
    setUpgrading(true);
    try {
      const res = await api.mockUpgradeTier(tierId);
      setSuccessNotice(res.message);
      await refreshUser();
      setTimeout(() => setSuccessNotice(null), 3000);
    } catch (e) {
      console.error(e);
    } finally {
      setUpgrading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-4xl max-h-[90vh] bg-white rounded-2xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden">
        {/* Modal Header */}
        <div className="bg-slate-900 text-white px-6 py-5 flex items-center justify-between shrink-0 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center shadow-md text-slate-200">
              <Crown size={18} />
            </div>
            <div>
              <h2 className="text-base font-bold tracking-tight text-white flex items-center gap-2">
                <span>Enterprise Sovereign Licensing &amp; Capacity Tiers</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                  Institutional Grade
                </span>
              </h2>
              <p className="text-xs text-slate-300">
                Bloomberg-grade intelligence terminal indexing $104.16B in non-dilutive energy transition capital &amp; $58.22B in private venture rounds
              </p>
            </div>
          </div>
          <button
            onClick={closeMembershipModal}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-white/10 transition-colors cursor-pointer"
          >
            <X size={18} />
          </button>
        </div>

        {/* Institutional Edition Callout Banner */}
        <div className="bg-slate-900 text-white px-6 py-3.5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shrink-0 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0 text-emerald-400">
              <ShieldCheck size={16} />
            </div>
            <div>
              <div className="text-xs font-semibold uppercase tracking-wider flex items-center gap-2">
                <span>Institutional Sovereign Edition</span>
                <span className="bg-emerald-950/60 text-emerald-400 border border-emerald-800/60 px-2 py-0.2 rounded text-[10px] font-mono font-semibold">ACTIVE LICENSE</span>
              </div>
              <div className="text-xs text-slate-300 mt-0.5">
                Complete multi-agency index (56,413 awards, 5,757 solicitations, 10,250 grid queues), 9-D lineage tracing &amp; capital stacking engines.
              </div>
            </div>
          </div>
          <div className="text-right shrink-0">
            <span className="text-xs font-semibold bg-slate-800 text-slate-200 px-3 py-1 rounded-lg font-mono border border-slate-700">
              Sovereign Enterprise Seat
            </span>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {successNotice && (
            <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2">
              <CheckCircle2 size={16} className="text-emerald-600" />
              <span>{successNotice}</span>
            </div>
          )}

          <div className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-200 flex items-start gap-3">
            <Info size={18} className="text-indigo-600 shrink-0 mt-0.5" />
            <div>
              <strong className="text-slate-800 font-semibold">Institutional Due Diligence Warrant:</strong>
              <span className="block mt-0.5">
                Every dataset, patent linkage, recipient dossier, and financial metric in the Energy Innovation Terminal is grounded against authoritative public records (USAspending, US DOE, CEC, MassCEC, NYSERDA, USPTO, and FERC). All intelligence briefs are cleared for Board of Directors presentations and Investment Committee memos.
              </span>
            </div>
          </div>

          {/* Tiers Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {manifest?.tiers.map((tier: TierInfo) => {
              const isCurrent = user?.tier === tier.id || (tier.id === 'free_public_benefit' && (!user || user.tier === 'free_public_benefit'));
              const isEnterprise = tier.id === 'enterprise';
              const isPro = tier.id === 'pro';

              return (
                <div
                  key={tier.id}
                  className={`rounded-2xl border flex flex-col p-5 transition-all ${
                    isEnterprise
                      ? 'border-cyan-400 bg-gradient-to-b from-cyan-50/30 to-white shadow-lg ring-2 ring-cyan-400/30'
                      : isCurrent
                        ? 'border-indigo-500 bg-indigo-50/20 shadow-md ring-2 ring-indigo-500/20'
                        : 'border-slate-200 bg-white hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                      {isEnterprise ? 'Institutional Master' : isPro ? 'Deal Team' : 'Research'}
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      isEnterprise
                        ? 'bg-cyan-100 text-cyan-900 border border-cyan-300 font-extrabold'
                        : isCurrent
                          ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                          : 'bg-slate-100 text-slate-600'
                    }`}>
                      {tier.badge}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-slate-900">{tier.name}</h3>
                  <p className="text-xs text-slate-500 mt-1 min-h-[32px] leading-relaxed">{tier.tagline}</p>

                  <div className="my-4 pt-3 border-t border-slate-100">
                    <div className="text-xl font-bold text-slate-900 font-mono">
                      {tier.price}
                    </div>
                    <span className="text-[10px] text-slate-400">
                      {isEnterprise ? 'Institutional SLA & Concierge Included' : isPro ? 'Per Active Analyst Seat' : 'Academic Non-Commercial'}
                    </span>
                  </div>

                  {/* Feature list */}
                  <div className="flex-1 space-y-2 mb-5">
                    <div className="text-[11px] font-semibold text-slate-700 uppercase tracking-wider">
                      Included Capabilities:
                    </div>
                    {tier.features.map((feat, idx) => (
                      <div key={idx} className="flex items-start gap-2 text-xs text-slate-600">
                        <Check size={14} className="text-emerald-600 shrink-0 mt-0.5" />
                        <span>{feat}</span>
                      </div>
                    ))}
                  </div>

                  {/* Action / Upgrade Button */}
                  <div className="pt-2">
                    {isCurrent ? (
                      <div className="w-full py-2 px-3 text-center bg-emerald-100/70 text-emerald-800 text-xs font-bold rounded-xl border border-emerald-200 flex items-center justify-center gap-1.5">
                        <Check size={13} /> Currently Active (Full Access)
                      </div>
                    ) : (
                      <button
                        type="button"
                        disabled={upgrading || !user}
                        onClick={() => handleMockUpgrade(tier.id)}
                        className={`w-full py-2 px-3 text-center text-xs font-bold rounded-xl transition-all flex items-center justify-center gap-1 cursor-pointer disabled:opacity-50 ${
                          isEnterprise
                            ? 'bg-slate-900 hover:bg-slate-800 text-white shadow-md'
                            : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200'
                        }`}
                      >
                        <span>{isEnterprise ? 'Activate Sovereign Tier' : 'Select Deal Team Plan'}</span>
                        <ArrowUpRight size={13} />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="bg-slate-50 border-t border-slate-200 px-6 py-3 flex items-center justify-between text-xs text-slate-500 shrink-0">
          <div className="font-mono text-[11px]">
            Energy Innovation Terminal · U.S. Energy Innovation Database by Brandon N. Owens
          </div>
          <button
            onClick={closeMembershipModal}
            className="px-4 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-800 font-semibold rounded-lg transition-colors text-xs cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
