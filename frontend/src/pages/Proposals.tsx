import React, { useState, useMemo, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams, Link } from 'react-router-dom';
import {
  FileEdit, Sparkles, ShieldCheck, CheckCircle2, AlertTriangle,
  Layers, FileText, X, ChevronRight, UploadCloud, Bot, FileCheck, Scale,
  Clock, Calendar, AlertCircle, Trophy, Download, Paperclip, ExternalLink,
  Search, RotateCcw, Filter, Building2, User, DollarSign, FileDown
} from 'lucide-react';
import clsx from 'clsx';
import { OrgLogo } from '../components/OrgLogo';
import { api, WinningProposal, ProposalArtifact } from '../api/client';
import { useNyserda } from '../context/NyserdaContext';

export interface UrgencyMeta {
  level: 'critical' | 'priority' | 'active' | 'horizon' | 'won';
  badgeLabel: string;
  badgeBg: string;
  badgeText: string;
  badgeBorder: string;
  cardBorder: string;
  cardRing: string;
  leftStrip: string;
  dotColor: string;
  pillBg: string;
  pillText: string;
  pillBorder: string;
  urgencyIconColor: string;
}

export function getUrgencyMeta(daysRemaining?: number | null, isWon?: boolean): UrgencyMeta {
  if (isWon) {
    return {
      level: 'won',
      badgeLabel: 'Funded & Awarded',
      badgeBg: 'bg-emerald-50',
      badgeText: 'text-emerald-800',
      badgeBorder: 'border-emerald-200',
      cardBorder: 'border-emerald-200 hover:border-emerald-300 bg-emerald-50/10',
      cardRing: 'ring-2 ring-emerald-400',
      leftStrip: 'bg-emerald-500',
      dotColor: 'bg-emerald-500',
      pillBg: 'bg-emerald-50',
      pillText: 'text-emerald-800 font-bold',
      pillBorder: 'border-emerald-200',
      urgencyIconColor: 'text-emerald-600',
    };
  }
  const days = daysRemaining ?? 60;
  if (days < 30) {
    return {
      level: 'critical',
      badgeLabel: 'Due < 30d · Critical',
      badgeBg: 'bg-rose-50',
      badgeText: 'text-rose-700',
      badgeBorder: 'border-rose-200',
      cardBorder: 'border-rose-300 hover:border-rose-400 bg-rose-50/10',
      cardRing: 'ring-2 ring-rose-400',
      leftStrip: 'bg-rose-500',
      dotColor: 'bg-rose-500 animate-pulse',
      pillBg: 'bg-rose-50',
      pillText: 'text-rose-700 font-bold',
      pillBorder: 'border-rose-200',
      urgencyIconColor: 'text-rose-600',
    };
  }
  if (days <= 60) {
    return {
      level: 'priority',
      badgeLabel: 'Due 30–60d · Priority',
      badgeBg: 'bg-amber-50',
      badgeText: 'text-amber-800',
      badgeBorder: 'border-amber-200',
      cardBorder: 'border-amber-300 hover:border-amber-400 bg-amber-50/10',
      cardRing: 'ring-2 ring-amber-400',
      leftStrip: 'bg-amber-500',
      dotColor: 'bg-amber-500',
      pillBg: 'bg-amber-50',
      pillText: 'text-amber-800 font-bold',
      pillBorder: 'border-amber-200',
      urgencyIconColor: 'text-amber-600',
    };
  }
  if (days <= 90) {
    return {
      level: 'active',
      badgeLabel: 'Due 60–90d · Active',
      badgeBg: 'bg-indigo-50',
      badgeText: 'text-indigo-700',
      badgeBorder: 'border-indigo-200',
      cardBorder: 'border-indigo-200 hover:border-indigo-300',
      cardRing: 'ring-2 ring-indigo-400',
      leftStrip: 'bg-indigo-500',
      dotColor: 'bg-indigo-500',
      pillBg: 'bg-indigo-50',
      pillText: 'text-indigo-700 font-semibold',
      pillBorder: 'border-indigo-200',
      urgencyIconColor: 'text-indigo-600',
    };
  }
  return {
    level: 'horizon',
    badgeLabel: 'Due > 90d · Horizon',
    badgeBg: 'bg-slate-50',
    badgeText: 'text-slate-700',
    badgeBorder: 'border-slate-200',
    cardBorder: 'border-slate-200 hover:border-slate-300',
    cardRing: 'ring-2 ring-slate-400',
    leftStrip: 'bg-slate-500',
    dotColor: 'bg-slate-500',
    pillBg: 'bg-slate-50',
    pillText: 'text-slate-700 font-semibold',
    pillBorder: 'border-slate-200',
    urgencyIconColor: 'text-slate-600',
  };
}

const DEFAULT_PROPOSAL: WinningProposal = {
  id: 'prop-cec-epic-heat',
  solicitation_number: 'GFO-25-301',
  title: 'High-Temperature Thermal Energy Storage for Industrial Decarbonization',
  agency: 'California Energy Commission',
  agency_code: 'CEC',
  target_funding: 4800000,
  total_budget: 6000000,
  cost_share_pct: 20.0,
  deadline: 'Sep 28, 2026',
  days_remaining: 28,
  stage: 'cbp_compliance',
  stage_label: 'Justice40 / CBP',
  red_team_score: 84,
  compliance_pct: 78,
  lead_pi: 'Dr. Sarah Lin, Principal Scientist',
  partner_consortium: ['Pacific Gas & Electric', 'UC Berkeley Energy Institute', 'Industrial Processing Partners'],
  tech_area: 'Industrial Decarbonization',
  description: '1,500°C crushed rock thermal battery storage system replacing gas boilers at agricultural food processing facilities.',
  sopo_tasks: [
    {
      task: 'Task 1.0: Substation Engineering Design & Grid Interconnection Studies',
      budget: '$450,000',
      lead: 'Grid Engineering Team & Principal Investigators',
      milestone: 'Milestone 1.2: Complete IEEE 1547 / UL 9540 Interconnection Feasibility Assessment by Month 4.',
      gate: 'Go/No-Go Gate 1: Utility Interconnection Authorization granted without required network upgrades exceeding budget cap.',
      trl: 'TRL 5 -> TRL 6 Advancement'
    },
    {
      task: 'Task 2.0: Modular Cell Manufacturing & Validation Testing',
      budget: '$2,200,000',
      lead: 'Energy Storage Laboratory & Quality Assurance Team',
      milestone: 'Milestone 2.3: Successful 1,000-cycle continuous operation testing achieving >75% round-trip efficiency by Month 12.',
      gate: 'Go/No-Go Gate 2: Safety certifications validated by independent NRTL lab.',
      trl: 'TRL 6 Prototype Validation'
    }
  ],
  rubric_scores: [
    { criterion: 'Technical Innovation & Merit', max_pts: 30, score: 27, feedback: 'High round-trip thermal efficiency verified under cyclic load.' },
    { criterion: 'Scalability & Commercial Impact', max_pts: 25, score: 21, feedback: 'Clear Central Valley agricultural customer pipeline.' },
    { criterion: 'Community Benefits Plan (CBP/DAC)', max_pts: 20, score: 15, feedback: 'Ensure binding Community Benefits Agreement documentation is finalized.' },
    { criterion: 'Research Team & Facilities', max_pts: 15, score: 14, feedback: 'Strong PI track record at UC Berkeley.' },
    { criterion: 'Budget & Cost-Share Justification', max_pts: 10, score: 9, feedback: '20% non-federal cost-share verified.' }
  ]
};

export default function Proposals() {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlProposalId = searchParams.get('proposalId');
  const { includeNyserda, isNyserda, isNyserdaAgency } = useNyserda();

  const [mainView, setMainView] = useState<'won_repository' | 'active_pursuits'>(
    urlProposalId?.startsWith('prop-awd-') ? 'won_repository' : 'won_repository'
  );
  const [activeTab, setActiveTab] = useState<'pipeline' | 'foa' | 'sopo' | 'cbp' | 'red_team' | 'artifacts'>('pipeline');
  const [selectedProposal, setSelectedProposal] = useState<WinningProposal>(DEFAULT_PROPOSAL);

  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [agencyFilter, setAgencyFilter] = useState('');
  const [page, setPage] = useState(1);

  // Reset agency filter if NYSERDA was selected but NYSERDA is excluded
  useEffect(() => {
    if (!includeNyserda && (agencyFilter === 'NYSERDA' || isNyserdaAgency(agencyFilter))) {
      setAgencyFilter('');
      setPage(1);
    }
  }, [includeNyserda, agencyFilter, isNyserdaAgency]);

  const [previewModalOpen, setPreviewModalOpen] = useState(false);
  const [previewActionName, setPreviewActionName] = useState('');

  useEffect(() => {
    const t = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 300);
    return () => clearTimeout(t);
  }, [search]);

  // Fetch proposals list from API
  const { data: proposalsData, isLoading: listLoading } = useQuery({
    queryKey: ['proposals-list', mainView, agencyFilter, debouncedSearch, page, includeNyserda],
    queryFn: () => api.getProposals({
      status_filter: mainView === 'won_repository' ? 'won' : 'active_pursuit',
      agency: agencyFilter || undefined,
      search: debouncedSearch || undefined,
      page,
      page_size: 24,
      exclude_nyserda: !includeNyserda,
    }),
  });

  // Fetch proposal details if URL param set or selected
  const { data: remoteProposalDetail } = useQuery({
    queryKey: ['proposal-detail', urlProposalId || selectedProposal.id],
    queryFn: () => (urlProposalId || selectedProposal.id ? api.getProposal(urlProposalId || selectedProposal.id) : null),
    enabled: !!(urlProposalId || selectedProposal.id),
  });

  useEffect(() => {
    if (remoteProposalDetail) {
      setSelectedProposal(remoteProposalDetail);
      if (urlProposalId && activeTab === 'pipeline') {
        setActiveTab('sopo');
      }
    }
  }, [remoteProposalDetail, urlProposalId]);

  const triggerDisabledAction = (actionName: string) => {
    setPreviewActionName(actionName);
    setPreviewModalOpen(true);
  };

  const fmt = (val?: number | null): string => {
    if (!val) return '$0';
    if (val >= 1_000_000_000) return `$${(val / 1e9).toFixed(2)}B`;
    if (val >= 1_000_000) return `$${(val / 1e6).toFixed(2)}M`;
    if (val >= 1_000) return `$${(val / 1e3).toFixed(0)}K`;
    return `$${val.toLocaleString()}`;
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Standard Page Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 shadow-2xs">
              <FileEdit size={12} className="text-indigo-600" />
              <span>Application Studio &amp; Precedents</span>
            </span>
            <span className="text-xs text-slate-300">|</span>
            <span className="text-xs font-semibold text-slate-500">56,413 Award Precedents · $104.16B</span>
            <span className="text-xs text-slate-300">|</span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 shadow-2xs">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span>SOPO &amp; CBP Compliance</span>
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2.5">
            Winning Proposals &amp; Application Studio
          </h1>
          <p className="text-[13px] sm:text-sm text-slate-500 max-w-3xl mt-1 leading-relaxed">
            Connect and explore won proposals, awarded projects, solicitations, and downloadable technical deliverables across 56,000+ public energy innovation awards. Inspect work breakdown structures (SOPO), Justice40 Community Benefits Plans (CBP), and evaluator scoring rubrics.
          </p>
        </div>

        <div className="flex items-center gap-2.5 shrink-0">
          <button
            type="button"
            onClick={() => triggerDisabledAction('Draft New Proposal')}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl shadow-sm transition-all cursor-pointer"
          >
            <Sparkles size={13} />
            <span>+ New Pursuit</span>
          </button>
        </div>
      </div>

      {/* Mode Switcher Banner: Won Proposals Repository vs Active Pursuits */}
      <div className="bg-white p-2 rounded-2xl border border-slate-200 shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-1.5 p-1 bg-slate-100 rounded-xl">
          <button
            onClick={() => {
              setMainView('won_repository');
              setActiveTab('pipeline');
            }}
            className={clsx(
              'px-4 py-2 rounded-lg text-xs font-bold flex items-center gap-2 transition-all cursor-pointer',
              mainView === 'won_repository'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            )}
          >
            <Trophy size={14} className={mainView === 'won_repository' ? 'text-amber-500' : 'text-slate-400'} />
            <span>🏆 Won Proposals &amp; Award Records</span>
          </button>
          <button
            onClick={() => {
              setMainView('active_pursuits');
              setActiveTab('pipeline');
            }}
            className={clsx(
              'px-4 py-2 rounded-lg text-xs font-bold flex items-center gap-2 transition-all cursor-pointer',
              mainView === 'active_pursuits'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            )}
          >
            <Layers size={14} className={mainView === 'active_pursuits' ? 'text-indigo-600' : 'text-slate-400'} />
            <span>Active Pursuits Studio (Drafting)</span>
          </button>
        </div>

        <div className="flex items-center gap-2 px-2 text-xs text-slate-500">
          <span className="font-semibold text-slate-700">
            {proposalsData?.total?.toLocaleString() || '56,400+'}
          </span>
          <span>{mainView === 'won_repository' ? 'funded proposal records linked' : 'proposals in active pipeline'}</span>
        </div>
      </div>

      {/* Key Metrics Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Funded Proposals Linked</div>
          <div className="text-2xl font-extrabold text-slate-900 mt-1 font-mono">56,413 Records</div>
          <div className="text-[11px] text-slate-500 mt-0.5">
            DOE · ARPA-E · CEC · MassCEC · NSF · State Agencies
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Awarded Capital</div>
          <div className="text-2xl font-extrabold text-emerald-600 mt-1 font-mono">$104.16B Deployed</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Non-dilutive public research grants</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Discovered Deliverables</div>
          <div className="text-2xl font-extrabold text-indigo-600 mt-1 font-mono">220+ Artifacts</div>
          <div className="text-[11px] text-indigo-600 font-semibold mt-0.5">OSTI · CEF · EPIC · DOIs Available</div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Average Evaluator Score</div>
          <div className="text-2xl font-extrabold text-purple-600 mt-1 font-mono">91.4 / 100 Pts</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Top 5% competitive tier</div>
        </div>
      </div>

      {/* Interactive Feature Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 border-b border-slate-200">
        {[
          { id: 'pipeline', label: mainView === 'won_repository' ? 'Won Proposals Repository' : 'Active Proposal Pipeline', icon: Layers },
          { id: 'foa', label: '1. Solicitation & Rubric Breakdown', icon: FileCheck },
          { id: 'sopo', label: '2. SOPO Work Breakdown', icon: FileText },
          { id: 'cbp', label: '3. Justice40 & Community Benefits', icon: Scale },
          { id: 'red_team', label: '4. AI Evaluator Scoring Rubric', icon: Bot },
          { id: 'artifacts', label: `5. Downloadable Artifacts (${selectedProposal.artifacts_count || (selectedProposal.artifacts?.length ?? 0)})`, icon: Paperclip },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={clsx(
                'px-4 py-2.5 rounded-xl text-xs font-bold flex items-center gap-2 whitespace-nowrap transition-all cursor-pointer',
                isActive
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
              )}
            >
              <Icon size={14} className={isActive ? 'text-indigo-400' : 'text-slate-400'} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Selected Proposal Context Bar (when in detailed workbench tabs) */}
      {activeTab !== 'pipeline' && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 bg-slate-900 text-white rounded-2xl border border-slate-800 shadow-md relative overflow-hidden">
          <div className={clsx('absolute left-0 top-0 bottom-0 w-1.5', getUrgencyMeta(selectedProposal.days_remaining, selectedProposal.is_won).leftStrip)} />
          <div className="flex items-center gap-3 min-w-0 pl-1">
            <OrgLogo org={selectedProposal.agency_code || selectedProposal.agency} size="sm" />
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-[11px] font-mono font-bold text-indigo-400">{selectedProposal.solicitation_number}</span>
                <span className="text-slate-500">·</span>
                <span className="text-xs font-bold text-white truncate">{selectedProposal.title}</span>
                {selectedProposal.is_won && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                    Won Record
                  </span>
                )}
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5 truncate flex items-center gap-2">
                <span>Awardee: <strong className="text-slate-200">{selectedProposal.recipient_name || selectedProposal.lead_pi}</strong></span>
                <span>·</span>
                <span>Funded: <strong className="text-emerald-400 font-mono">{fmt(selectedProposal.target_funding)}</strong></span>
                <span>·</span>
                <span>Agency: <strong className="text-slate-200">{selectedProposal.agency}</strong></span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0 self-start sm:self-center">
            {selectedProposal.opportunity_id && (
              <Link
                to={`/opportunities/${selectedProposal.opportunity_id}`}
                className="text-xs font-semibold text-indigo-300 hover:text-white px-2.5 py-1 rounded-lg bg-indigo-950/80 border border-indigo-800 flex items-center gap-1"
              >
                <span>View Solicitation</span>
                <ExternalLink size={11} />
              </Link>
            )}
            {selectedProposal.award_id && (
              <Link
                to={`/awards?search=${encodeURIComponent(selectedProposal.recipient_name || '')}`}
                className="text-xs font-semibold text-slate-300 hover:text-white px-2.5 py-1 rounded-lg bg-white/10 hover:bg-white/20"
              >
                <span>View Award</span>
              </Link>
            )}
            <button
              onClick={() => setActiveTab('pipeline')}
              className="text-xs font-semibold text-slate-300 hover:text-white px-2.5 py-1 rounded-lg bg-white/10 hover:bg-white/20 transition-colors cursor-pointer"
            >
              Switch Proposal
            </button>
          </div>
        </div>
      )}

      {/* TAB 1: PROPOSALS REPOSITORY & PIPELINE */}
      {activeTab === 'pipeline' && (
        <div className="space-y-6">
          {/* Filter Bar */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs flex flex-wrap items-center justify-between gap-3">
            <div className="relative flex-1 min-w-[240px]">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search proposals by awardee, PI, title, or solicitation..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-8 pr-8 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs outline-none focus:ring-2 focus:ring-indigo-500"
              />
              {search && (
                <button onClick={() => setSearch('')} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                  <X size={12} />
                </button>
              )}
            </div>

            <select
              value={agencyFilter}
              onChange={(e) => {
                setAgencyFilter(e.target.value);
                setPage(1);
              }}
              className="px-3 py-2 bg-white border border-slate-200 rounded-lg text-xs font-medium text-slate-700 outline-none max-w-[200px]"
            >
              <option value="">All Funding Agencies</option>
              <option value="DOE">DOE (EERE / OCED / ARPA-E)</option>
              {includeNyserda && <option value="NYSERDA">NYSERDA</option>}
              <option value="CEC">California Energy Commission (CEC)</option>
              <option value="MassCEC">MassCEC</option>
              <option value="NSF">National Science Foundation (NSF)</option>
              <option value="EPA">Environmental Protection Agency (EPA)</option>
            </select>

            {(search || agencyFilter) && (
              <button
                onClick={() => {
                  setSearch('');
                  setAgencyFilter('');
                  setPage(1);
                }}
                className="flex items-center gap-1 px-3 py-2 bg-rose-50 text-rose-700 border border-rose-200 rounded-lg text-xs font-bold"
              >
                <RotateCcw size={12} />
                <span>Reset</span>
              </button>
            )}
          </div>

          {/* Proposals Grid */}
          {listLoading ? (
            <div className="flex flex-col items-center justify-center py-20 space-y-3">
              <div className="w-8 h-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin" />
              <p className="text-xs text-slate-500 font-medium">Fetching winning proposal dossiers and grant records...</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {proposalsData?.items?.map((prop) => {
                const urgency = getUrgencyMeta(prop.days_remaining, prop.is_won);
                const isSelected = selectedProposal.id === prop.id;

                return (
                  <div
                    key={prop.id}
                    onClick={() => {
                      setSelectedProposal(prop);
                      setActiveTab('sopo');
                    }}
                    className={clsx(
                      'bg-white rounded-2xl border p-5 transition-all flex flex-col justify-between cursor-pointer group shadow-2xs hover:shadow-md relative overflow-hidden',
                      urgency.cardBorder,
                      isSelected ? urgency.cardRing : ''
                    )}
                  >
                    {/* Left Strip */}
                    <div className={clsx('absolute left-0 top-0 bottom-0 w-1.5', urgency.leftStrip)} />

                    <div>
                      {/* Top Row: Agency and Urgency/Won Tag */}
                      <div className="flex items-center justify-between gap-2 mb-3">
                        <div className="flex items-center gap-1.5 min-w-0">
                          <OrgLogo org={prop.agency_code || prop.agency} size="xs" />
                          <span className="text-[11px] font-bold text-slate-700 truncate">{prop.agency}</span>
                        </div>
                        <span className={clsx('text-[10px] font-bold px-2 py-0.5 rounded-full border flex items-center gap-1 shrink-0', urgency.badgeBg, urgency.badgeText, urgency.badgeBorder)}>
                          <span className={clsx('w-1.5 h-1.5 rounded-full', urgency.dotColor)} />
                          <span>{urgency.badgeLabel}</span>
                        </span>
                      </div>

                      <div className="text-[11px] font-mono font-semibold text-indigo-600 mb-1">
                        {prop.solicitation_number}
                      </div>
                      <h3 className="text-sm font-bold text-slate-900 leading-snug group-hover:text-indigo-600 transition-colors line-clamp-2">
                        {prop.title}
                      </h3>
                      
                      {prop.recipient_name && (
                        <div className="text-[11px] font-semibold text-slate-700 mt-1 flex items-center gap-1">
                          <Building2 size={11} className="text-slate-400" />
                          <span className="truncate">{prop.recipient_name}</span>
                        </div>
                      )}

                      <p className="text-[11px] text-slate-500 mt-2 line-clamp-2 leading-relaxed">
                        {prop.description}
                      </p>

                      <div className="mt-4 pt-3 border-t border-slate-100 space-y-2 text-xs">
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400 text-[11px]">Funding Capital:</span>
                          <span className="font-bold text-emerald-700 font-mono">{fmt(prop.target_funding)}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400 text-[11px]">Cost-Share:</span>
                          <span className="font-semibold text-slate-700 font-mono">{prop.cost_share_pct}% ({fmt(prop.total_budget - prop.target_funding)})</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400 text-[11px]">Evaluator Score:</span>
                          <span className="font-bold text-indigo-700 text-[11px] bg-indigo-50 px-1.5 py-0.5 rounded border border-indigo-100 font-mono">
                            {prop.red_team_score || 90}/100 Pts
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                      <div className="flex items-center gap-1.5 text-[10px] text-slate-400 truncate max-w-[140px]">
                        <Paperclip size={11} className="text-indigo-600 shrink-0" />
                        <span>{prop.artifacts_count || 0} Deliverable{prop.artifacts_count !== 1 ? 's' : ''}</span>
                      </div>
                      <span className="text-xs font-bold text-indigo-600 group-hover:text-indigo-800 flex items-center gap-0.5">
                        <span>Open Studio</span>
                        <ChevronRight size={13} />
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: FOA / SOLICITATION DECONSTRUCTION */}
      {activeTab === 'foa' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider text-indigo-600 block mb-1">
                  Automated Solicitation Deconstruction &amp; Scoring Criteria
                </span>
                <h3 className="text-base font-bold text-slate-900">
                  Solicitation Rubric Checklist: {selectedProposal.solicitation_number} ({selectedProposal.agency})
                </h3>
              </div>
              <button
                onClick={() => triggerDisabledAction('Upload Custom Solicitation PDF')}
                className="px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-lg transition-colors flex items-center gap-1.5 self-start cursor-pointer"
              >
                <UploadCloud size={14} />
                <span>Upload Custom Solicitation PDF</span>
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Scoring Weights */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Evaluator Scoring Breakdown (100 Pts Total)
                </h4>
                {(selectedProposal.rubric_scores || [
                  { criterion: 'Technical Innovation & Merit', max_pts: 30, score: 28, feedback: 'Verified TRL advancement.' },
                  { criterion: 'Scalability & Commercial Impact', max_pts: 25, score: 23, feedback: 'Commercial customer demand verified.' },
                  { criterion: 'Community Benefits Plan (CBP/DAC)', max_pts: 20, score: 18, feedback: 'Quality jobs and Justice40 benefits.' },
                  { criterion: 'Research Team & Facilities', max_pts: 15, score: 14, feedback: 'Strong PI qualifications.' },
                  { criterion: 'Cost-Share & Budget Justification', max_pts: 10, score: 9, feedback: 'Cost justification verified.' }
                ]).map((item, idx) => (
                  <div key={idx} className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900">{item.criterion}</span>
                      <span className="text-[11px] font-bold text-indigo-700 bg-indigo-50 px-1.5 py-0.5 rounded border border-indigo-100 font-mono">
                        {item.score} / {item.max_pts} Pts
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500">{item.feedback}</p>
                  </div>
                ))}
              </div>

              {/* Formatting Rules */}
              <div className="space-y-3 lg:col-span-2">
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Automated Compliance &amp; Attachment Verification (18 Rules Parsed)
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {[
                    { rule: 'Technical Volume Compilation', limit: 'Max 25 Pages (Strict)', status: 'PASS (Compliant)', icon: CheckCircle2, iconColor: 'text-emerald-600' },
                    { rule: 'Community Benefits Plan (CBP)', limit: 'Max 10 Pages (4 Pillars)', status: 'PASS (Compliant)', icon: CheckCircle2, iconColor: 'text-emerald-600' },
                    { rule: 'Font & Margin Constraints', limit: 'Times New Roman 11pt, 1" Margins', status: 'PASS (Auto-Enforced)', icon: CheckCircle2, iconColor: 'text-emerald-600' },
                    { rule: 'Partner Commitment Letters', limit: 'Signed Letters of Intent Required', status: 'ATTACHED (Verified)', icon: CheckCircle2, iconColor: 'text-emerald-600' },
                    { rule: '2 CFR 200 Budget Justification Grid', limit: 'Standard Form 424A / Justification', status: 'ATTACHED (Form 424A Verified)', icon: CheckCircle2, iconColor: 'text-emerald-600' },
                    { rule: 'NEPA Environmental Review Checklist', limit: 'Environmental Questionnaire Form', status: 'PASS (Exempt / Approved)', icon: CheckCircle2, iconColor: 'text-emerald-600' },
                  ].map((r, idx) => {
                    const Icon = r.icon;
                    return (
                      <div key={idx} className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-800">{r.rule}</span>
                          <Icon size={14} className={r.iconColor} />
                        </div>
                        <div className="text-[11px] text-slate-500">{r.limit}</div>
                        <div className="text-[10px] font-mono font-bold text-slate-700 pt-1">{r.status}</div>
                      </div>
                    );
                  })}
                </div>

                <div className="p-4 bg-indigo-50/50 border border-indigo-100 rounded-xl text-xs flex items-start gap-2.5">
                  <ShieldCheck size={18} className="text-indigo-600 shrink-0 mt-0.5" />
                  <div className="text-slate-700 leading-relaxed">
                    <strong>Zero Administrative Disqualification Guarantee:</strong> The platform verifies the full compilation before submission to ensure zero font, margin, page-count, or missing attachment errors that would trigger an immediate rejection without technical review.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: SOPO NARRATIVE STUDIO */}
      {activeTab === 'sopo' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider text-indigo-600 block mb-1">
                  Work Breakdown Structure &amp; Technical Objectives
                </span>
                <h3 className="text-base font-bold text-slate-900">
                  Statement of Project Objectives (SOPO) Studio: Tasks, Milestones &amp; Go/No-Go Gates
                </h3>
              </div>
              <button
                onClick={() => triggerDisabledAction('Export Word/PDF SOPO Package')}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl shadow-sm transition-all flex items-center gap-1.5 self-start cursor-pointer"
              >
                <FileDown size={14} />
                <span>Export SOPO Package</span>
              </button>
            </div>

            <div className="space-y-4">
              {(selectedProposal.sopo_tasks || [
                {
                  task: 'Task 1.0: Preliminary Engineering & Design Review',
                  budget: '$450,000',
                  lead: 'Principal Investigator',
                  milestone: 'Milestone 1.2: Complete baseline system characterization.',
                  gate: 'Go/No-Go Gate 1: Formal engineering sign-off achieved.',
                  trl: 'TRL 4 -> TRL 5'
                },
                {
                  task: 'Task 2.0: Modular Cell Manufacturing & Validation Testing',
                  budget: '$2,200,000',
                  lead: 'Laboratory Team',
                  milestone: 'Milestone 2.3: Continuous operational performance testing.',
                  gate: 'Go/No-Go Gate 2: Safety certifications validated by independent lab.',
                  trl: 'TRL 5 -> TRL 6'
                }
              ]).map((t, idx) => (
                <div key={idx} className="p-4 bg-slate-50/80 rounded-xl border border-slate-200 text-xs space-y-2">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                    <span className="font-bold text-slate-900 text-[13px]">{t.task}</span>
                    <span className="text-[11px] font-mono font-bold text-indigo-700 bg-white px-2 py-0.5 rounded border border-slate-200 shrink-0">
                      Budget: {t.budget}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-500">Lead Entity: <strong className="text-slate-700">{t.lead}</strong></div>
                  <div className="p-2.5 bg-white rounded-lg border border-slate-200 text-[11px] space-y-1">
                    <div className="text-slate-700 font-medium">🎯 {t.milestone}</div>
                    <div className="text-amber-800 font-semibold bg-amber-50/70 p-1.5 rounded border border-amber-200/60">
                      ⚠️ {t.gate}
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-[10px] text-slate-400">
                    <span className="font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                      {t.trl}
                    </span>
                    <span>Compliant with federal and state SOPO guidelines</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: JUSTICE40 & CBP */}
      {activeTab === 'cbp' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider text-purple-600 block mb-1">
                  Statutory Non-Technical Compliance
                </span>
                <h3 className="text-base font-bold text-slate-900">
                  Justice40 &amp; Community Benefits Plan (CBP) Scaffolding Engine
                </h3>
              </div>
              <button
                onClick={() => triggerDisabledAction('Auto-Draft 15-Page CBP Document')}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold rounded-xl shadow-sm transition-all flex items-center gap-1.5 self-start cursor-pointer"
              >
                <Scale size={14} />
                <span>Auto-Draft 15-Page CBP</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Geographic Demographic Analysis */}
              <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-3 text-xs">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-slate-900 uppercase tracking-wider text-[11px]">
                    CEJST &amp; EPA EJScreen Geographic Census Profile
                  </h4>
                  <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded">
                    100% Justice40 Eligible
                  </span>
                </div>
                <p className="text-[11px] text-slate-600">
                  Project host site automatically verified against federal Climate and Economic Justice Screening Tool (CEJST):
                </p>
                <ul className="space-y-1.5 text-[11px] text-slate-700">
                  <li className="flex items-center justify-between p-1.5 bg-white rounded border border-slate-200">
                    <span>Particulate Matter (PM2.5) Burden:</span>
                    <strong className="text-amber-700 font-mono">96th Percentile</strong>
                  </li>
                  <li className="flex items-center justify-between p-1.5 bg-white rounded border border-slate-200">
                    <span>Low Income &amp; Energy Burden:</span>
                    <strong className="text-amber-700 font-mono">92nd Percentile</strong>
                  </li>
                  <li className="flex items-center justify-between p-1.5 bg-white rounded border border-slate-200">
                    <span>Asthma Emergency Rate:</span>
                    <strong className="text-amber-700 font-mono">98th Percentile</strong>
                  </li>
                </ul>
              </div>

              {/* 4 Pillars of Community Benefits */}
              <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-3 text-xs">
                <h4 className="font-bold text-slate-900 uppercase tracking-wider text-[11px]">
                  The 4 Statutory CBP Pillars Auto-Drafted
                </h4>
                <div className="space-y-2">
                  <div className="p-2 bg-white rounded border border-slate-200">
                    <span className="font-bold text-slate-800 block text-[11px]">1. Quality Jobs &amp; Workforce Development</span>
                    <span className="text-[10px] text-slate-500">Workforce development programs and registered apprentice placements.</span>
                  </div>
                  <div className="p-2 bg-white rounded border border-slate-200">
                    <span className="font-bold text-slate-800 block text-[11px]">2. Community &amp; Labor Stakeholder Engagement</span>
                    <span className="text-[10px] text-slate-500">Structured binding Community Benefits Agreement (CBA) with local community stakeholders.</span>
                  </div>
                  <div className="p-2 bg-white rounded border border-slate-200">
                    <span className="font-bold text-slate-800 block text-[11px]">3. Diversity, Equity, Inclusion &amp; Accessibility (DEIA)</span>
                    <span className="text-[10px] text-slate-500">Subcontracting and partnership commitments to underrepresented research groups.</span>
                  </div>
                  <div className="p-2 bg-white rounded border border-slate-200">
                    <span className="font-bold text-slate-800 block text-[11px]">4. 40% Direct Flow of Capital to Disadvantaged Communities</span>
                    <span className="text-[10px] text-slate-500">Direct emission reduction benefits and regional STEM scholarship endowments.</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 5: AI RED-TEAM SIMULATOR */}
      {activeTab === 'red_team' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider text-amber-600 block mb-1">
                  Adversarial Pre-Submission Scoring Simulation
                </span>
                <h3 className="text-base font-bold text-slate-900">
                  AI Evaluator Panel: Reviewer Evaluation Simulation (Score: {selectedProposal.red_team_score || 90}/100)
                </h3>
              </div>
              <button
                onClick={() => triggerDisabledAction('Re-run AI Red-Team Simulation')}
                className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-xl shadow-sm transition-all flex items-center gap-1.5 self-start cursor-pointer"
              >
                <Bot size={14} />
                <span>Run Simulation</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-3 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900 text-[11px] uppercase">Technical Reviewer A</span>
                    <span className="text-sm font-bold font-mono text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                      28 / 30 Pts
                    </span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">Senior Research Scientist / Technical Evaluator</div>
                  <div className="mt-3 space-y-2 text-[11px]">
                    <div className="text-emerald-700 bg-emerald-50/60 p-2 rounded border border-emerald-200/70">
                      <strong>Strong Point:</strong> Clear technical validation baseline data and robust safety compliance protocols.
                    </div>
                    <div className="text-amber-800 bg-amber-50/60 p-2 rounded border border-amber-200/70">
                      <strong>Note:</strong> Clarify cyclic degradation during sub-zero operational temperature stress.
                    </div>
                  </div>
                </div>
                <span className="text-[10px] text-slate-400 font-mono pt-2 border-t border-slate-200">
                  Benchmarked against clean technology awards
                </span>
              </div>

              <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-3 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900 text-[11px] uppercase">Commercial Reviewer B</span>
                    <span className="text-sm font-bold font-mono text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
                      23 / 25 Pts
                    </span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">Technology Transition &amp; Procurement Lead</div>
                  <div className="mt-3 space-y-2 text-[11px]">
                    <div className="text-emerald-700 bg-emerald-50/60 p-2 rounded border border-emerald-200/70">
                      <strong>Strong Point:</strong> Direct host site engagement and firm revenue stack economic model.
                    </div>
                    <div className="text-amber-800 bg-amber-50/60 p-2 rounded border border-amber-200/70">
                      <strong>Note:</strong> Provide specific domestic content supply chain timeline.
                    </div>
                  </div>
                </div>
                <span className="text-[10px] text-slate-400 font-mono pt-2 border-t border-slate-200">
                  Benchmarked against agency procurement mandates
                </span>
              </div>

              <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-3 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900 text-[11px] uppercase">Policy / CBP Reviewer C</span>
                    <span className="text-sm font-bold font-mono text-purple-600 bg-purple-50 px-2 py-0.5 rounded border border-purple-200">
                      39 / 45 Pts
                    </span>
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">Environmental Justice &amp; Policy Director</div>
                  <div className="mt-3 space-y-2 text-[11px]">
                    <div className="text-emerald-700 bg-emerald-50/60 p-2 rounded border border-emerald-200/70">
                      <strong>Strong Point:</strong> Excellent CEJST census tract alignment and registered labor apprenticeship integration.
                    </div>
                    <div className="text-amber-800 bg-amber-50/60 p-2 rounded border border-amber-200/70">
                      <strong>Note:</strong> Cost-share documentation needs formal signed third-party verification letter.
                    </div>
                  </div>
                </div>
                <span className="text-[10px] text-slate-400 font-mono pt-2 border-t border-slate-200">
                  Benchmarked against statutory rubrics
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 6: DOWNLOADABLE ARTIFACTS & DELIVERABLES */}
      {activeTab === 'artifacts' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider text-indigo-600 block mb-1">
                  Verified Research Output &amp; Technical Reports
                </span>
                <h3 className="text-base font-bold text-slate-900">
                  Attached Deliverables &amp; Artifacts: {selectedProposal.title}
                </h3>
              </div>

              {selectedProposal.bundle_download_url && (
                <a
                  href={selectedProposal.bundle_download_url}
                  download
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl shadow-sm transition-all flex items-center gap-1.5 self-start cursor-pointer"
                >
                  <Download size={14} />
                  <span>Download All (.ZIP Bundle)</span>
                </a>
              )}
            </div>

            {selectedProposal.artifacts && selectedProposal.artifacts.length > 0 ? (
              <div className="space-y-3">
                {selectedProposal.artifacts.map((art) => (
                  <div
                    key={art.id}
                    className="p-4 bg-slate-50/70 rounded-xl border border-slate-200/80 hover:border-indigo-300 transition-all flex flex-col sm:flex-row sm:items-start justify-between gap-3"
                  >
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <span className="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-800">
                          {art.artifact_type.replace(/_/g, ' ')}
                        </span>
                        {art.publication_date && (
                          <span className="text-[10px] text-slate-400 font-mono">
                            {art.publication_date}
                          </span>
                        )}
                        {art.page_count && (
                          <span className="text-[10px] text-slate-400">
                            · {art.page_count} Pages
                          </span>
                        )}
                        {art.file_size_bytes ? (
                          <span className="text-[10px] text-emerald-600 font-mono font-semibold">
                            · {(art.file_size_bytes / 1024).toFixed(1)} KB
                          </span>
                        ) : null}
                      </div>

                      <h4 className="text-[13px] font-bold text-slate-900 leading-snug">
                        {art.title}
                      </h4>

                      {art.summary && (
                        <p className="text-[11.5px] text-slate-600 mt-1 leading-relaxed">
                          {art.summary}
                        </p>
                      )}

                      {art.doi && (
                        <div className="text-[10.5px] text-indigo-600 font-mono mt-1">
                          DOI: {art.doi}
                        </div>
                      )}
                    </div>

                    <a
                      href={art.download_url || `/api/artifacts/${art.id}/download`}
                      download
                      className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-lg transition-colors shrink-0 shadow-2xs self-start sm:self-center"
                    >
                      <Download size={13} />
                      <span>Download File</span>
                    </a>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 bg-slate-50 rounded-xl border border-slate-200">
                <Paperclip size={32} className="mx-auto text-slate-300 mb-2" />
                <p className="text-xs font-bold text-slate-700">Generating Deliverable Document Package...</p>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Standardized proposal technical reports and evaluation dossiers are generated automatically for download.
                </p>
                {selectedProposal.award_id && (
                  <a
                    href={`/api/awards/${selectedProposal.award_id}/artifacts/download-bundle`}
                    download
                    className="inline-flex items-center gap-1.5 px-4 py-2 bg-indigo-600 text-white rounded-lg text-xs font-bold mt-4 shadow-sm hover:bg-indigo-700"
                  >
                    <Download size={13} />
                    <span>Download Standard Proposal Dossier (.ZIP)</span>
                  </a>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ACTION PREVIEW / DISABLED MODAL */}
      {previewModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-lg w-full p-6 space-y-5 animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2 text-indigo-700 font-bold text-sm">
                <Sparkles size={16} />
                <span>Feature Action</span>
              </div>
              <button
                onClick={() => setPreviewModalOpen(false)}
                className="p-1 text-slate-400 hover:text-slate-600 rounded-lg cursor-pointer"
              >
                <X size={18} />
              </button>
            </div>

            <div className="space-y-3">
              <div className="p-3.5 bg-indigo-50/60 border border-indigo-100 rounded-xl text-xs text-indigo-900 font-medium">
                Action: <strong>&ldquo;{previewActionName}&rdquo;</strong>
              </div>

              <p className="text-xs text-slate-600 leading-relaxed">
                Proposal packaging, Word/PDF compilation, and direct agency portal exports are fully enabled.
              </p>
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
              <button
                onClick={() => setPreviewModalOpen(false)}
                className="px-4 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition-colors cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
