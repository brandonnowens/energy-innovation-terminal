import React, { useState, useEffect } from 'react';
import {
  Zap,
  ShieldAlert,
  Users,
  Key,
  CheckCircle2,
  Copy,
  Check,
  X,
  RefreshCw,
  Award,
  AlertTriangle,
  Scale,
  Compass,
  FileCheck,
  ExternalLink,
  Target
} from 'lucide-react';
import clsx from 'clsx';
import { API_BASE_URL } from '../api/client';

export interface RubricCriterion {
  criterion: string;
  weight_pct: number;
  target_score: string;
  scoring_focus: string;
  reviewer_bias: string;
}

export interface TeamingPartner {
  partner_type: string;
  recommended_profile: string;
  strategic_value: string;
  urgency: string;
}

export interface WinningAngleReportData {
  opportunity_id: number;
  solicitation_number: string;
  opportunity_name: string;
  agency: string;
  program_name: string;
  match_score_pct: number;
  winning_hook: string;
  strategic_framing: string;
  hidden_rubric_breakdown: RubricCriterion[];
  mandatory_reviewer_keywords: string[];
  optimal_teaming_strategy: TeamingPartner[];
  unwritten_evaluation_biases: string[];
  red_flag_landmines: string[];
  competitive_differentiation: string;
  target_score_benchmark: string;
  model_used: string;
  is_llm_generated: boolean;
}

interface WinningAngleModalProps {
  isOpen: boolean;
  onClose: () => void;
  opportunityId?: number | string | null;
  opportunityName?: string;
  solicitationNumber?: string;
  agency?: string;
  projectProfile?: any;
  matchScore?: number;
}

export function WinningAngleModal({
  isOpen,
  onClose,
  opportunityId,
  opportunityName = 'Funding Opportunity',
  solicitationNumber = '',
  agency = '',
  projectProfile,
  matchScore = 0.88,
}: WinningAngleModalProps) {
  const [report, setReport] = useState<WinningAngleReportData | null>(null);
  const [loading, setLoading] = useState(false);
  const [liveRefreshing, setLiveRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copiedHook, setCopiedHook] = useState(false);
  const [activeTab, setActiveTab] = useState<'rubric' | 'keywords' | 'teaming' | 'landmines'>('rubric');

  useEffect(() => {
    if (!isOpen) {
      setReport(null);
      setError(null);
      return;
    }
    fetchWinningAngle(false);
  }, [isOpen, opportunityId, opportunityName]);

  const fetchWinningAngle = async (forceLive: boolean = false) => {
    if (forceLive) setLiveRefreshing(true);
    else setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE_URL}/api/analyze/winning-angle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          opportunity_id: opportunityId,
          solicitation_number: solicitationNumber,
          opportunity_name: opportunityName,
          agency: agency,
          project_profile: projectProfile || {},
          match_score: matchScore,
          force_live: forceLive,
        }),
      });

      if (!res.ok) {
        throw new Error(`Failed to load winning angle (status ${res.status})`);
      }

      const data = await res.json();
      setReport(data);
    } catch (err: any) {
      console.error('Error fetching winning angle:', err);
      setError(err.message || 'Unable to reverse-engineer winning angle.');
    } finally {
      setLoading(false);
      setLiveRefreshing(false);
    }
  };

  const copyHook = () => {
    if (!report?.winning_hook) return;
    navigator.clipboard.writeText(report.winning_hook);
    setCopiedHook(true);
    setTimeout(() => setCopiedHook(false), 2000);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 md:p-6 bg-black/70 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-4xl max-h-[90vh] flex flex-col bg-white dark:bg-[#0c1220] border border-slate-200 dark:border-white/10 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header Bar */}
        <div className="flex items-center justify-between p-4 sm:p-5 border-b border-slate-200 dark:border-white/10 bg-slate-50/80 dark:bg-[#0d1527]">
          <div className="flex items-center gap-3 min-w-0">
            <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-500 border border-amber-500/20 shrink-0">
              <Zap size={20} className="animate-pulse" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-mono text-xs font-bold text-amber-500 uppercase tracking-wider">
                  Winning Angle &amp; Hidden Rubric
                </span>
                {report && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full font-mono font-bold bg-indigo-50 dark:bg-indigo-950/50 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/30">
                    {report.target_score_benchmark}
                  </span>
                )}
                {report?.is_llm_generated && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full font-mono font-bold bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-500/30">
                    Deep Strategic Analysis
                  </span>
                )}
              </div>
              <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white truncate">
                {solicitationNumber ? `${solicitationNumber} — ` : ''}{opportunityName}
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              type="button"
              onClick={() => fetchWinningAngle(true)}
              disabled={loading || liveRefreshing}
              className="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-white/5 dark:hover:bg-white/10 text-slate-700 dark:text-slate-300 text-xs font-semibold flex items-center gap-1.5 border border-slate-200 dark:border-white/10 transition-colors disabled:opacity-50 cursor-pointer"
              title="Re-run in-depth strategic analysis"
            >
              <RefreshCw size={12} className={clsx(liveRefreshing && 'animate-spin')} />
              <span className="hidden sm:inline">Live Deep-Dive</span>
            </button>
            <button
              type="button"
              onClick={onClose}
              className="p-2 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/5 transition-colors cursor-pointer"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5">
          {loading && (
            <div className="py-20 flex flex-col items-center justify-center space-y-3 text-slate-500 dark:text-slate-400">
              <RefreshCw size={28} className="animate-spin text-amber-500" />
              <p className="text-xs font-mono">Reverse-engineering reviewer scoring rubric and evaluation biases...</p>
            </div>
          )}

          {error && (
            <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-500/30 text-rose-700 dark:text-rose-300 text-xs flex items-start gap-2">
              <AlertTriangle size={16} className="shrink-0 mt-0.5" />
              <div>
                <strong className="block font-bold mb-0.5">Error Loading Winning Angle</strong>
                {error}
              </div>
            </div>
          )}

          {report && !loading && (
            <>
              {/* Flagship: The Winning Hook */}
              <div className="relative p-4 sm:p-5 rounded-2xl bg-gradient-to-br from-amber-500/10 via-indigo-500/5 to-purple-500/10 border border-amber-500/30 shadow-sm">
                <div className="flex items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-amber-600 dark:text-amber-400 uppercase tracking-wider font-mono">
                    <Target size={14} />
                    <span>The Winning Proposal Hook (Executive Summary)</span>
                  </div>
                  <button
                    type="button"
                    onClick={copyHook}
                    className="px-2.5 py-1 rounded-lg bg-white/80 dark:bg-black/40 hover:bg-white dark:hover:bg-black/60 text-slate-700 dark:text-slate-200 text-xs font-semibold flex items-center gap-1.5 border border-slate-200 dark:border-white/10 transition-colors shadow-2xs cursor-pointer"
                  >
                    {copiedHook ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
                    <span>{copiedHook ? 'Copied' : 'Copy Hook'}</span>
                  </button>
                </div>
                <blockquote className="text-sm sm:text-base font-semibold text-slate-900 dark:text-white leading-relaxed italic">
                  &ldquo;{report.winning_hook}&rdquo;
                </blockquote>
                <div className="mt-3 text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-white/50 dark:bg-black/20 p-3 rounded-xl border border-slate-200/50 dark:border-white/5">
                  <span className="font-bold text-slate-900 dark:text-white">Strategic Framing: </span>
                  {report.strategic_framing}
                </div>
              </div>

              {/* Navigation Tabs */}
              <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-xs font-semibold overflow-x-auto">
                <button
                  type="button"
                  onClick={() => setActiveTab('rubric')}
                  className={clsx(
                    'px-3.5 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors whitespace-nowrap cursor-pointer',
                    activeTab === 'rubric'
                      ? 'bg-white dark:bg-[#11192e] text-indigo-600 dark:text-indigo-400 shadow-2xs'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                  )}
                >
                  <Scale size={13} />
                  <span>Hidden Rubric ({report.hidden_rubric_breakdown?.length || 0})</span>
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('keywords')}
                  className={clsx(
                    'px-3.5 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors whitespace-nowrap cursor-pointer',
                    activeTab === 'keywords'
                      ? 'bg-white dark:bg-[#11192e] text-indigo-600 dark:text-indigo-400 shadow-2xs'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                  )}
                >
                  <Key size={13} />
                  <span>Mandatory Keywords ({report.mandatory_reviewer_keywords?.length || 0})</span>
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('teaming')}
                  className={clsx(
                    'px-3.5 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors whitespace-nowrap cursor-pointer',
                    activeTab === 'teaming'
                      ? 'bg-white dark:bg-[#11192e] text-indigo-600 dark:text-indigo-400 shadow-2xs'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                  )}
                >
                  <Users size={13} />
                  <span>Teaming Roster ({report.optimal_teaming_strategy?.length || 0})</span>
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('landmines')}
                  className={clsx(
                    'px-3.5 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors whitespace-nowrap cursor-pointer',
                    activeTab === 'landmines'
                      ? 'bg-white dark:bg-[#11192e] text-indigo-600 dark:text-indigo-400 shadow-2xs'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                  )}
                >
                  <ShieldAlert size={13} />
                  <span>Biases &amp; Landmines ({report.red_flag_landmines?.length || 0})</span>
                </button>
              </div>

              {/* Tab 1: Hidden Rubric Breakdown */}
              {activeTab === 'rubric' && (
                <div className="space-y-3">
                  <div className="text-xs text-slate-500 dark:text-slate-400 flex items-center justify-between">
                    <span>Scoring criteria weights reverse-engineered from agency evaluation history:</span>
                    <span className="font-mono font-bold text-slate-700 dark:text-slate-300">Total: 100%</span>
                  </div>
                  <div className="space-y-2.5">
                    {report.hidden_rubric_breakdown?.map((crit, idx) => (
                      <div
                        key={idx}
                        className="p-3.5 rounded-xl bg-slate-50 dark:bg-[#0d1424] border border-slate-200 dark:border-white/10 space-y-2"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <div className="flex items-center gap-2 min-w-0">
                            <span className="font-bold text-xs text-slate-900 dark:text-white">
                              {crit.criterion}
                            </span>
                          </div>
                          <div className="flex items-center gap-2 shrink-0">
                            <span className="font-mono text-xs font-bold text-indigo-600 dark:text-indigo-400">
                              Target: {crit.target_score}
                            </span>
                            <span className="px-2 py-0.5 rounded font-mono text-[10px] font-bold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/20">
                              {crit.weight_pct}% Weight
                            </span>
                          </div>
                        </div>

                        {/* Progress Bar */}
                        <div className="w-full bg-slate-200 dark:bg-white/10 rounded-full h-1.5 overflow-hidden">
                          <div
                            className="bg-indigo-500 h-full rounded-full transition-all"
                            style={{ width: `${crit.weight_pct * 2.5}%` }}
                          />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 pt-1 text-[11px]">
                          <div className="text-slate-700 dark:text-slate-300">
                            <strong className="text-slate-900 dark:text-white">Reviewer Focus: </strong>
                            {crit.scoring_focus}
                          </div>
                          <div className="text-amber-700 dark:text-amber-300/90 bg-amber-50/50 dark:bg-amber-950/20 p-2 rounded-lg border border-amber-200/50 dark:border-amber-500/20">
                            <strong className="text-amber-800 dark:text-amber-200">Unwritten Bias: </strong>
                            {crit.reviewer_bias}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab 2: Mandatory Reviewer Keywords */}
              {activeTab === 'keywords' && (
                <div className="space-y-4">
                  <div className="text-xs text-slate-500 dark:text-slate-400">
                    Reviewers use automated semantic screening and manual keyword scanning. Include these exact terms across your narrative:
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {report.mandatory_reviewer_keywords?.map((kw, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1.5 rounded-xl font-mono text-xs font-bold bg-slate-100 dark:bg-white/5 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-white/10 hover:border-indigo-400 dark:hover:border-indigo-500 transition-colors flex items-center gap-1.5"
                      >
                        <Key size={11} className="text-indigo-500" />
                        <span>{kw}</span>
                      </span>
                    ))}
                  </div>

                  {report.competitive_differentiation && (
                    <div className="p-4 rounded-xl bg-indigo-50/70 dark:bg-indigo-950/20 border border-indigo-200 dark:border-indigo-500/30 text-xs">
                      <div className="font-bold text-indigo-900 dark:text-indigo-300 mb-1 flex items-center gap-1.5">
                        <Award size={14} />
                        <span>Competitive Differentiation Stance</span>
                      </div>
                      <p className="text-indigo-950 dark:text-indigo-200 leading-relaxed">
                        {report.competitive_differentiation}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Tab 3: Teaming Partner Roster */}
              {activeTab === 'teaming' && (
                <div className="space-y-3">
                  <div className="text-xs text-slate-500 dark:text-slate-400">
                    Optimal consortium profiles that eliminate institutional reviewer skepticism and maximize score points:
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {report.optimal_teaming_strategy?.map((team, idx) => (
                      <div
                        key={idx}
                        className="p-3.5 rounded-xl bg-slate-50 dark:bg-[#0d1424] border border-slate-200 dark:border-white/10 space-y-2 text-xs"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <span className="font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                            <Users size={13} className="text-indigo-500" />
                            {team.partner_type}
                          </span>
                          <span className="text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-500/20">
                            {team.urgency}
                          </span>
                        </div>
                        <div className="text-slate-700 dark:text-slate-300 text-[11px]">
                          <strong className="text-slate-900 dark:text-white">Profile: </strong>
                          {team.recommended_profile}
                        </div>
                        <div className="text-slate-600 dark:text-slate-400 text-[11px] bg-white dark:bg-black/20 p-2 rounded-lg border border-slate-200/60 dark:border-white/5">
                          <strong className="text-slate-800 dark:text-slate-200">Strategic Impact: </strong>
                          {team.strategic_value}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tab 4: Reviewer Biases & Landmines */}
              {activeTab === 'landmines' && (
                <div className="space-y-4">
                  {/* Unwritten Biases */}
                  {report.unwritten_evaluation_biases?.length > 0 && (
                    <div className="space-y-2">
                      <div className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider font-mono flex items-center gap-1.5">
                        <Compass size={13} className="text-indigo-500" />
                        <span>Unwritten Agency Evaluation Biases</span>
                      </div>
                      <div className="space-y-1.5">
                        {report.unwritten_evaluation_biases.map((bias, idx) => (
                          <div
                            key={idx}
                            className="p-3 rounded-xl bg-slate-50 dark:bg-[#0d1424] border border-slate-200 dark:border-white/10 text-xs text-slate-700 dark:text-slate-300 flex items-start gap-2"
                          >
                            <CheckCircle2 size={13} className="text-indigo-500 shrink-0 mt-0.5" />
                            <span>{bias}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Red-Flag Landmines */}
                  {report.red_flag_landmines?.length > 0 && (
                    <div className="space-y-2 pt-2">
                      <div className="text-xs font-bold text-rose-600 dark:text-rose-400 uppercase tracking-wider font-mono flex items-center gap-1.5">
                        <ShieldAlert size={14} />
                        <span>Proposal Landmines (Automatic Scoring Deductions)</span>
                      </div>
                      <div className="space-y-1.5">
                        {report.red_flag_landmines.map((mine, idx) => (
                          <div
                            key={idx}
                            className="p-3 rounded-xl bg-rose-50/60 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-500/30 text-xs text-rose-900 dark:text-rose-200 flex items-start gap-2"
                          >
                            <AlertTriangle size={13} className="text-rose-500 shrink-0 mt-0.5" />
                            <span>{mine}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-200 dark:border-white/10 bg-slate-50/80 dark:bg-[#0d1527] flex items-center justify-between text-xs">
          <div className="text-slate-500 dark:text-slate-400 font-mono text-[11px]">
            Targeting Upper Quartile Reviewer Scores (≥90/100)
          </div>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 dark:bg-white dark:hover:bg-slate-100 text-white dark:text-slate-900 font-bold transition-colors cursor-pointer"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
