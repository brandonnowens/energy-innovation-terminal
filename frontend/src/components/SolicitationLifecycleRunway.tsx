import React, { useState, useMemo } from 'react';
import { 
  Calendar, Clock, CheckCircle2, AlertCircle, 
  HelpCircle, ChevronRight, Layers, FileText, 
  Check, ArrowRight, Sparkles, Target, Zap
} from 'lucide-react';
import clsx from 'clsx';

interface SolicitationLifecycleRunwayProps {
  opportunity: {
    id: number | string;
    name: string;
    solicitation_number?: string;
    status?: string;
    open_date?: string | null;
    close_date?: string | null;
    deadline?: string | null;
    award_date?: string | null;
    concept_paper_required?: boolean;
    concept_paper_due_date?: string | null;
    questions_due_date?: string | null;
    rounds?: Array<{
      round_number?: number;
      status?: string;
      due_date?: string | null;
      concept_paper_due_date?: string | null;
      questions_due_date?: string | null;
      award_date?: string | null;
    }>;
  };
  className?: string;
}

interface StageGate {
  id: string;
  name: string;
  shortName: string;
  date: Date | null;
  dateStr: string;
  status: 'completed' | 'current' | 'upcoming';
  isMandatory: boolean;
  isTodayMarker?: boolean;
  description: string;
  requirements: string[];
  daysDiff: number; // Difference from today in days
}

function formatDateDisplay(d: Date | null, fallback: string = 'Rolling'): string {
  if (!d || isNaN(d.getTime())) return fallback;
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
}

export const SolicitationLifecycleRunway: React.FC<SolicitationLifecycleRunwayProps> = ({
  opportunity,
  className
}) => {
  const [selectedRoundIndex, setSelectedRoundIndex] = useState<number>(0);
  const [activeGateId, setActiveGateId] = useState<string | null>(null);

  const rounds = opportunity.rounds || [];
  const currentRound = rounds.length > 0 ? rounds[selectedRoundIndex] : null;

  // Compute Stage Gates
  const { stageGates, todayProgressPct, daysUntilDeadline, isClosed } = useMemo(() => {
    const now = new Date();
    const nowTime = now.getTime();

    // 1. Open Date
    const openDateStr = opportunity.open_date;
    const openDate = openDateStr ? new Date(openDateStr) : new Date(nowTime - 45 * 86400000);

    // 2. Questions Due Date
    const questionsDateStr = currentRound?.questions_due_date || opportunity.questions_due_date;
    const questionsDate = questionsDateStr ? new Date(questionsDateStr) : new Date(openDate.getTime() + 14 * 86400000);

    // 3. Concept Paper Due Date
    const conceptRequired = opportunity.concept_paper_required || !!currentRound?.concept_paper_due_date;
    const conceptDateStr = currentRound?.concept_paper_due_date || opportunity.concept_paper_due_date;
    const conceptDate = conceptDateStr 
      ? new Date(conceptDateStr) 
      : (conceptRequired ? new Date(openDate.getTime() + 28 * 86400000) : null);

    // 4. Full Proposal Due Date / Deadline
    const closeDateStr = currentRound?.due_date || opportunity.close_date || opportunity.deadline;
    const closeDate = closeDateStr ? new Date(closeDateStr) : new Date(openDate.getTime() + 60 * 86400000);

    // 5. Merit Review & Technical Scoring Window
    const reviewDate = new Date(closeDate.getTime() + 30 * 86400000);

    // 6. Anticipated Award / Selection
    const awardDateStr = currentRound?.award_date || opportunity.award_date;
    const awardDate = awardDateStr ? new Date(awardDateStr) : new Date(closeDate.getTime() + 60 * 86400000);

    // 7. Contracting & Project Kickoff
    const kickoffDate = new Date(awardDate.getTime() + 45 * 86400000);

    // Build Gates Array
    const gates: StageGate[] = [
      {
        id: 'issuance',
        name: 'FOA Issuance & Open Window',
        shortName: 'FOA Open',
        date: openDate,
        dateStr: formatDateDisplay(openDate, 'Open'),
        status: nowTime >= openDate.getTime() ? 'completed' : 'upcoming',
        isMandatory: true,
        description: 'Solicitation officially issued by program authority with complete technical scope.',
        requirements: ['Download official solicitation packet', 'Review TRL eligibility requirements', 'SAM.gov & Cage Code verification'],
        daysDiff: Math.round((openDate.getTime() - nowTime) / 86400000),
      },
      {
        id: 'questions',
        name: 'Technical Questions & Webinar',
        shortName: 'Questions Due',
        date: questionsDate,
        dateStr: formatDateDisplay(questionsDate, 'TBD'),
        status: nowTime > questionsDate.getTime() ? 'completed' : (nowTime >= openDate.getTime() && nowTime <= questionsDate.getTime() ? 'current' : 'upcoming'),
        isMandatory: false,
        description: 'Deadline to submit formal clarification inquiries and attend applicant webinars.',
        requirements: ['Submit FOA clarification inquiries', 'Access official FAQ addenda', 'Verify cost-share rules'],
        daysDiff: Math.round((questionsDate.getTime() - nowTime) / 86400000),
      },
    ];

    if (conceptRequired && conceptDate) {
      gates.push({
        id: 'concept',
        name: 'Mandatory Concept Paper / LOI',
        shortName: 'Concept Paper',
        date: conceptDate,
        dateStr: formatDateDisplay(conceptDate, 'Required'),
        status: nowTime > conceptDate.getTime() ? 'completed' : (nowTime >= questionsDate.getTime() && nowTime <= conceptDate.getTime() ? 'current' : 'upcoming'),
        isMandatory: true,
        description: 'Binding go/no-go stage gate determining eligibility for full proposal invitation.',
        requirements: ['3–5 Page Concept Brief', 'High-level CapEx and GHG abatement metrics', 'Encouraged/Discouraged determination notification'],
        daysDiff: Math.round((conceptDate.getTime() - nowTime) / 86400000),
      });
    }

    const prevConceptTime = conceptDate ? conceptDate.getTime() : questionsDate.getTime();

    gates.push({
      id: 'submission',
      name: 'Full Application Submission Deadline',
      shortName: 'Proposal Deadline',
      date: closeDate,
      dateStr: formatDateDisplay(closeDate, 'Open Rolling'),
      status: nowTime > closeDate.getTime() ? 'completed' : (nowTime >= prevConceptTime && nowTime <= closeDate.getTime() ? 'current' : 'upcoming'),
      isMandatory: true,
      description: 'Hard electronic submission cutoff. Strict statutory compliance required.',
      requirements: ['Full Technical Volume (Workplan & SOPO)', 'Detailed 5-Year Budget & Cost Share Commitments', 'Letters of Support & Subcontractor Teaming Agreements'],
      daysDiff: Math.round((closeDate.getTime() - nowTime) / 86400000),
    });

    gates.push({
      id: 'scoring',
      name: 'Merit Review & Technical Scoring',
      shortName: 'Merit Review',
      date: reviewDate,
      dateStr: formatDateDisplay(reviewDate, 'Estimated'),
      status: nowTime > reviewDate.getTime() ? 'completed' : (nowTime > closeDate.getTime() && nowTime <= reviewDate.getTime() ? 'current' : 'upcoming'),
      isMandatory: true,
      description: 'Independent peer review panel scoring against criteria weighting matrix.',
      requirements: ['Technical Innovation & Soundness (40%)', 'Commercialization & Market Viability (30%)', 'Team Qualifications & Management Plan (30%)'],
      daysDiff: Math.round((reviewDate.getTime() - nowTime) / 86400000),
    });

    gates.push({
      id: 'selection',
      name: 'Selection & Award Notification',
      shortName: 'Award Selection',
      date: awardDate,
      dateStr: formatDateDisplay(awardDate, 'Projected'),
      status: nowTime >= awardDate.getTime() ? 'completed' : 'upcoming',
      isMandatory: true,
      description: 'Formal announcement of selected awardees and public debrief notifications.',
      requirements: ['Notice of Selection issuance', 'Debrief review request window (if unselected)', 'Draft Statement of Project Objectives negotiation'],
      daysDiff: Math.round((awardDate.getTime() - nowTime) / 86400000),
    });

    gates.push({
      id: 'kickoff',
      name: 'Contracting & Execution Kickoff',
      shortName: 'Project Kickoff',
      date: kickoffDate,
      dateStr: formatDateDisplay(kickoffDate, 'Projected'),
      status: nowTime >= kickoffDate.getTime() ? 'completed' : 'upcoming',
      isMandatory: true,
      description: 'Final execution of grant agreement and first milestone fund disbursement.',
      requirements: ['Finalized subcontract agreements', 'NEPA environmental compliance signoff', 'First invoice milestone baseline approval'],
      daysDiff: Math.round((kickoffDate.getTime() - nowTime) / 86400000),
    });

    // Compute progress % between openDate and closeDate
    const totalSpan = Math.max(closeDate.getTime() - openDate.getTime(), 1);
    const elapsed = Math.min(Math.max(nowTime - openDate.getTime(), 0), totalSpan);
    const pct = Math.min(Math.max((elapsed / totalSpan) * 100, 0), 100);

    const daysRemaining = Math.round((closeDate.getTime() - nowTime) / 86400000);
    const closed = daysRemaining < 0 || opportunity.status === 'closed';

    return {
      stageGates: gates,
      todayProgressPct: pct,
      daysUntilDeadline: daysRemaining,
      isClosed: closed,
    };
  }, [opportunity, currentRound]);

  const activeGate = stageGates.find(g => g.id === activeGateId) || stageGates.find(g => g.status === 'current') || stageGates[0];

  return (
    <div className={clsx("bg-white rounded-2xl p-5 sm:p-6 border border-slate-200/90 shadow-xs space-y-4", className)}>
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider bg-indigo-50 text-indigo-700 border border-indigo-200/60">
              Stage-Gate Runway
            </span>
            <span className="text-xs text-slate-500 font-mono">Solicitation Lifecycle &amp; Submission Gates</span>
          </div>
          <h2 className="text-[15px] font-bold text-slate-900 mt-1 flex items-center gap-2">
            <span>Milestone Timeline &amp; Decision Horizon</span>
          </h2>
        </div>

        {/* Right side: Round Selector or Countdown Badge */}
        <div className="flex items-center gap-2">
          {rounds.length > 1 && (
            <div className="flex items-center p-0.5 rounded-lg bg-slate-100 border border-slate-200 text-xs font-mono">
              {rounds.map((r, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setSelectedRoundIndex(i)}
                  className={clsx(
                    "px-2.5 py-1 rounded-md text-[11px] font-bold transition-all cursor-pointer",
                    selectedRoundIndex === i 
                      ? "bg-white text-indigo-700 shadow-2xs" 
                      : "text-slate-500 hover:text-slate-800"
                  )}
                >
                  Round {r.round_number || i + 1}
                </button>
              ))}
            </div>
          )}

          {/* Submission Countdown Pill */}
          <div className={clsx(
            "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold font-mono border shadow-2xs shrink-0",
            isClosed
              ? "bg-slate-100 text-slate-600 border-slate-200"
              : daysUntilDeadline <= 14
              ? "bg-rose-50 text-rose-700 border-rose-200 animate-pulse"
              : "bg-emerald-50 text-emerald-800 border-emerald-200"
          )}>
            <Clock size={13} className={isClosed ? "text-slate-400" : daysUntilDeadline <= 14 ? "text-rose-600" : "text-emerald-600"} />
            <span>
              {isClosed 
                ? 'Submission Window Closed' 
                : daysUntilDeadline === 0 
                ? 'Due Today!' 
                : `${daysUntilDeadline} Days to Full Proposal`}
            </span>
          </div>
        </div>
      </div>

      {/* Horizontal Runway Visual Track */}
      <div className="relative pt-3 pb-2">
        {/* Continuous track bar */}
        <div className="absolute top-[26px] left-6 right-6 h-1.5 bg-slate-100 rounded-full overflow-hidden">
          {/* Completed progress fill */}
          <div 
            className="h-full bg-gradient-to-r from-indigo-500 via-indigo-600 to-cyan-500 transition-all duration-500 rounded-full"
            style={{ width: `${todayProgressPct}%` }}
          />
        </div>

        {/* Stage Nodes Grid */}
        <div className="relative grid grid-cols-3 sm:grid-cols-7 gap-2">
          {stageGates.map((gate, idx) => {
            const isCompleted = gate.status === 'completed';
            const isCurrent = gate.status === 'current';
            const isSelected = activeGate?.id === gate.id;

            return (
              <div
                key={gate.id}
                onClick={() => setActiveGateId(gate.id)}
                className={clsx(
                  "flex flex-col items-center text-center cursor-pointer p-2 rounded-xl transition-all group",
                  isSelected ? "bg-indigo-50/60 ring-1 ring-indigo-300" : "hover:bg-slate-50"
                )}
              >
                {/* Node Glyph */}
                <div className={clsx(
                  "relative z-10 w-8 h-8 rounded-full flex items-center justify-center border-2 transition-all shadow-xs",
                  isCompleted 
                    ? "bg-emerald-500 border-emerald-600 text-white" 
                    : isCurrent 
                    ? "bg-indigo-600 border-indigo-400 text-white ring-4 ring-indigo-100" 
                    : "bg-white border-slate-300 text-slate-400 group-hover:border-slate-400"
                )}>
                  {isCompleted ? (
                    <Check size={14} strokeWidth={3} />
                  ) : isCurrent ? (
                    <span className="relative flex h-2.5 w-2.5">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-300 opacity-75" />
                      <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-white" />
                    </span>
                  ) : (
                    <span className="text-[11px] font-mono font-bold">{idx + 1}</span>
                  )}
                </div>

                {/* Node Title & Date */}
                <div className="mt-2 space-y-0.5">
                  <div className={clsx(
                    "text-[11.5px] font-bold leading-tight line-clamp-1",
                    isCurrent ? "text-indigo-900" : isCompleted ? "text-slate-800" : "text-slate-600"
                  )}>
                    {gate.shortName}
                  </div>
                  <div className="text-[10px] font-mono text-slate-400 font-semibold">
                    {gate.dateStr}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Selected Gate Inspection Detail Panel */}
      {activeGate && (
        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200/80 space-y-2 text-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200/60 pb-2">
            <div className="flex items-center gap-2">
              <span className={clsx(
                "px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase",
                activeGate.status === 'completed' 
                  ? "bg-emerald-100 text-emerald-800 border border-emerald-200" 
                  : activeGate.status === 'current'
                  ? "bg-indigo-100 text-indigo-800 border border-indigo-200"
                  : "bg-slate-200 text-slate-700"
              )}>
                {activeGate.status === 'completed' ? 'Gate Completed' : activeGate.status === 'current' ? 'Active Stage Gate' : 'Future Milestone'}
              </span>
              <h3 className="font-bold text-slate-900 text-[13px]">{activeGate.name}</h3>
            </div>

            <div className="font-mono text-[11px] text-slate-600 font-semibold flex items-center gap-1">
              <Calendar size={12} className="text-slate-400" />
              <span>Target: {activeGate.dateStr}</span>
              {activeGate.daysDiff !== 0 && (
                <span className="text-slate-400">({activeGate.daysDiff > 0 ? `${activeGate.daysDiff} days away` : `${Math.abs(activeGate.daysDiff)} days ago`})</span>
              )}
            </div>
          </div>

          <p className="text-slate-600 leading-relaxed text-[12px]">
            {activeGate.description}
          </p>

          <div className="pt-1">
            <div className="text-[10.5px] font-bold uppercase text-slate-500 tracking-wider mb-1 flex items-center gap-1">
              <CheckCircle2 size={11} className="text-indigo-600" /> Key Gate Deliverables &amp; Requirements:
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-1.5">
              {activeGate.requirements.map((req, i) => (
                <div key={i} className="p-2 bg-white rounded-lg border border-slate-200/70 text-[11px] text-slate-700 flex items-start gap-1.5 font-medium">
                  <span className="text-indigo-600 font-bold">›</span>
                  <span>{req}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SolicitationLifecycleRunway;
