import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  X, Zap, ShieldAlert, CheckCircle2, FileText, 
  Award, AlertTriangle, Scale, Clock, Copy, Check, Download, Layers
} from 'lucide-react';

interface FoaShredderModalProps {
  opportunityId: number;
  isOpen: boolean;
  onClose: () => void;
}

export const FoaShredderModal: React.FC<FoaShredderModalProps> = ({ opportunityId, isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'rubric' | 'compliance' | 'checklist' | 'strategy'>('rubric');
  const [copied, setCopied] = useState(false);

  const { data: shred, isLoading } = useQuery({
    queryKey: ['foa-shred', opportunityId],
    queryFn: async () => {
      const res = await fetch(`/api/foa-shredder/${opportunityId}`);
      if (!res.ok) throw new Error('Failed to load shredded FOA blueprint');
      return res.json();
    },
    enabled: isOpen && !!opportunityId
  });

  if (!isOpen) return null;

  const handleCopy = () => {
    if (!shred) return;
    const text = `FOA BLUEPRINT: ${shred.title}\nSolicitation: ${shred.solicitation_number} (${shred.agency})\nCost-Share Required: ${shred.cost_share_required_pct}%\n\nEVALUATION RUBRIC:\n${shred.scoring_rubric?.map((r: any) => `- ${r.criterion} (${r.weight_pct}%): ${r.description}`).join('\n')}\n\nREQUIRED VOLUMES:\n${shred.submission_checklist?.map((v: any) => `- ${v.title} (Max ${v.page_limit || 'No'} pages)`).join('\n')}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-4xl max-h-[90vh] flex flex-col rounded-2xl border dark:border-white/10 border-slate-200 dark:bg-[#0b1329] bg-white shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b dark:border-white/10 border-slate-200 dark:bg-[#070d1e] bg-slate-50">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-500">
              <Zap className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
                  AI FOA Shredder Blueprint
                </span>
                <span className="text-xs font-mono dark:text-slate-400 text-slate-500">
                  {shred?.solicitation_number || `Opp #${opportunityId}`}
                </span>
              </div>
              <h2 className="text-lg font-bold dark:text-white text-slate-900 line-clamp-1 mt-1">
                {shred?.title || 'Loading Solicitation Blueprint...'}
              </h2>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg dark:bg-white/5 bg-slate-100 hover:dark:bg-white/10 hover:bg-slate-200 dark:text-slate-300 text-slate-700 transition"
              title="Copy Summary"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? 'Copied' : 'Copy'}
            </button>
            <button 
              onClick={onClose}
              className="p-1.5 rounded-lg hover:bg-slate-200 dark:hover:bg-white/10 text-slate-400 hover:text-slate-600 dark:hover:text-white transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex border-b dark:border-white/10 border-slate-200 px-6 dark:bg-[#090e1a] bg-slate-100/50">
          {[
            { id: 'rubric', label: 'Evaluation Rubric', icon: Scale },
            { id: 'compliance', label: 'Compliance Gates', icon: ShieldAlert },
            { id: 'checklist', label: 'Volume Checklist', icon: FileText },
            { id: 'strategy', label: 'Red-Team Win Strategy', icon: Award },
          ].map(tab => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 py-3 px-4 border-b-2 font-semibold text-xs transition cursor-pointer ${
                  active 
                    ? 'border-amber-500 text-amber-600 dark:text-amber-400 dark:bg-white/5 bg-white' 
                    : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-16 space-y-3">
              <Zap className="w-8 h-8 animate-spin text-amber-500" />
              <p className="text-sm dark:text-slate-400 text-slate-600">AI Engine is parsing FOA text, scoring weights, and compliance rules...</p>
            </div>
          ) : shred ? (
            <>
              {/* TAB 1: SCORING RUBRIC */}
              {activeTab === 'rubric' && (
                <div className="space-y-4">
                  <div className="p-4 rounded-xl dark:bg-amber-500/5 bg-amber-50 border border-amber-500/20 text-xs dark:text-amber-200 text-amber-900">
                    <span className="font-bold">Official Reviewer Evaluation Weights:</span> Proposals are scored mathematically against these exact criteria. Focus your narrative heavily on Criterion 1 and 2 to pass the technical cutoff.
                  </div>

                  <div className="grid gap-4">
                    {shred.scoring_rubric?.map((criterion: any, idx: number) => (
                      <div key={idx} className="p-4 rounded-xl border dark:border-white/10 border-slate-200 dark:bg-[#0e1626] bg-slate-50 space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-sm dark:text-white text-slate-900">{criterion.criterion}</span>
                          <span className="px-2.5 py-1 rounded-full text-xs font-extrabold bg-amber-500/20 text-amber-600 dark:text-amber-400 border border-amber-500/30">
                            {criterion.weight_pct}% of Score
                          </span>
                        </div>
                        <p className="text-xs dark:text-slate-300 text-slate-700 leading-relaxed">{criterion.description}</p>
                        <div className="flex items-center gap-2 pt-1 text-[11px] dark:text-cyan-400 text-cyan-700 font-medium">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Core Deliverable Focus: {criterion.key_focus}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* TAB 2: COMPLIANCE GATES */}
              {activeTab === 'compliance' && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl border dark:border-white/10 border-slate-200 dark:bg-[#0e1626] bg-slate-50 space-y-1.5">
                      <div className="text-xs font-semibold dark:text-slate-400 text-slate-500">Mandatory Non-Federal Cost Share</div>
                      <div className="text-2xl font-bold text-amber-500">{shred.cost_share_required_pct}%</div>
                      <p className="text-xs dark:text-slate-300 text-slate-600">{shred.cost_share_rule_explanation}</p>
                    </div>

                    <div className="p-4 rounded-xl border dark:border-white/10 border-slate-200 dark:bg-[#0e1626] bg-slate-50 space-y-1.5">
                      <div className="text-xs font-semibold dark:text-slate-400 text-slate-500">Technology Readiness Level (TRL)</div>
                      <div className="text-2xl font-bold text-cyan-500">TRL {shred.trl_min} ➔ {shred.trl_max}</div>
                      <p className="text-xs dark:text-slate-300 text-slate-600">Projects below TRL {shred.trl_min} (basic science) or above TRL {shred.trl_max} (commercial off-the-shelf) will be disqualified.</p>
                    </div>
                  </div>

                  <div className="p-4 rounded-xl border dark:border-white/10 border-slate-200 dark:bg-[#0e1626] bg-slate-50 space-y-3">
                    <h3 className="text-xs font-bold uppercase tracking-wider dark:text-slate-400 text-slate-600">Eligible Prime Entities</h3>
                    <div className="flex flex-wrap gap-2">
                      {shred.eligible_applicant_types?.map((item: string, i: number) => (
                        <span key={i} className="px-3 py-1 rounded-lg text-xs font-semibold dark:bg-emerald-500/10 bg-emerald-50 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20">
                          ✓ {item}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex items-center gap-3 p-3.5 rounded-xl border dark:border-white/10 border-slate-200 dark:bg-[#0e1626] bg-slate-50">
                      <CheckCircle2 className={`w-5 h-5 ${shred.justice40_cbp_required ? 'text-indigo-500' : 'text-slate-400'}`} />
                      <div>
                        <div className="text-xs font-bold dark:text-white text-slate-900">Justice40 Community Benefits Plan</div>
                        <div className="text-[11px] dark:text-slate-400 text-slate-600">{shred.justice40_cbp_required ? 'Mandatory stand-alone 8-page narrative' : 'Not required'}</div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 p-3.5 rounded-xl border dark:border-white/10 border-slate-200 dark:bg-[#0e1626] bg-slate-50">
                      <CheckCircle2 className={`w-5 h-5 ${shred.domestic_manufacturing_clause ? 'text-amber-500' : 'text-slate-400'}`} />
                      <div>
                        <div className="text-xs font-bold dark:text-white text-slate-900">U.S. Manufacturing Commitment</div>
                        <div className="text-[11px] dark:text-slate-400 text-slate-600">{shred.domestic_manufacturing_clause ? 'Enforceable US build commitment required' : 'Standard'}</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 3: VOLUME CHECKLIST */}
              {activeTab === 'checklist' && (
                <div className="space-y-3">
                  <div className="text-xs dark:text-slate-400 text-slate-600 mb-2">
                    Prepare and attach these mandatory volumes in the exact prescribed format:
                  </div>

                  {shred.submission_checklist?.map((vol: any, i: number) => (
                    <div key={i} className="p-4 rounded-xl border dark:border-white/10 border-slate-200 dark:bg-[#0e1626] bg-slate-50 flex flex-col md:flex-row md:items-center justify-between gap-3">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                            {vol.section_code}
                          </span>
                          <span className="text-sm font-bold dark:text-white text-slate-900">{vol.title}</span>
                        </div>
                        <p className="text-xs dark:text-slate-300 text-slate-600">{vol.description}</p>
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        {vol.page_limit && (
                          <span className="px-2.5 py-1 rounded text-xs font-semibold bg-amber-500/10 text-amber-500 border border-amber-500/20">
                            Max {vol.page_limit} Pages
                          </span>
                        )}
                        <span className="px-2.5 py-1 rounded text-xs font-semibold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                          {vol.font_rules}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* TAB 4: RED-TEAM STRATEGY */}
              {activeTab === 'strategy' && (
                <div className="space-y-4">
                  <div className="p-4 rounded-xl border dark:border-emerald-500/20 border-emerald-200 dark:bg-emerald-500/5 bg-emerald-50 space-y-2">
                    <div className="flex items-center gap-2 font-bold text-sm text-emerald-600 dark:text-emerald-400">
                      <Award className="w-4 h-4" />
                      Key Winning Themes to Feature
                    </div>
                    <ul className="space-y-1.5 text-xs dark:text-slate-300 text-slate-700">
                      {shred.key_win_themes?.map((theme: string, i: number) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-emerald-500 font-bold">✓</span>
                          <span>{theme}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="p-4 rounded-xl border dark:border-red-500/20 border-red-200 dark:bg-red-500/5 bg-red-50 space-y-2">
                    <div className="flex items-center gap-2 font-bold text-sm text-red-600 dark:text-red-400">
                      <AlertTriangle className="w-4 h-4" />
                      Red-Team Fatal Flaws to Avoid (Disqualification Traps)
                    </div>
                    <ul className="space-y-1.5 text-xs dark:text-slate-300 text-slate-700">
                      {shred.red_team_fatal_flaws_to_avoid?.map((flaw: string, i: number) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-red-500 font-bold">✗</span>
                          <span>{flaw}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </>
          ) : null}
        </div>

        {/* Footer */}
        <div className="p-4 border-t dark:border-white/10 border-slate-200 dark:bg-[#070d1e] bg-slate-50 flex items-center justify-between text-xs text-slate-500">
          <span>Engine: {shred?.shredded_by || 'AI FOA Synthesizer'}</span>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-semibold transition"
          >
            Close Blueprint
          </button>
        </div>

      </div>
    </div>
  );
};
