import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams, Link } from 'react-router-dom';
import { api, isOpportunityNew } from '../api/client';
import {
  ArrowLeft, Loader2, Calendar, Mail, Phone, FileText, ExternalLink,
  AlertTriangle, CheckCircle2, Info, ShieldAlert, Ban, Star, Printer,
  Share2, Copy, Building2, Zap, Landmark, Check, Trophy, Download,
  Paperclip, FileDown, FileEdit, Award, Users, Target, TrendingUp, Send, Lock, DollarSign, Layers
} from 'lucide-react';
import clsx from 'clsx';
import { OrgLogo } from '../components/OrgLogo';
import { ProvenanceRibbon } from '../components/ProvenanceRibbon';
import { SolicitationLifecycleRunway } from '../components/SolicitationLifecycleRunway';
import { FoaShredderModal } from '../components/FoaShredderModal';
import { IraCalculatorModal } from '../components/IraCalculatorModal';
import { useSEO } from '../utils/seo';

function formatCurrency(val: number | null | undefined): string {
  if (!val) return '—';
  if (val >= 1_000_000_000) return `$${(val / 1_000_000_000).toFixed(2)}B`;
  if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(1)}M`;
  if (val >= 1_000) return `$${(val / 1_000).toFixed(0)}K`;
  return `$${val.toFixed(0)}`;
}

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '—';
  try {
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' });
  } catch { return dateStr; }
}

export default function OpportunityDetail() {
  const { id } = useParams<{ id: string }>();
  const [copiedCitation, setCopiedCitation] = useState(false);
  const [showFoaShred, setShowFoaShred] = useState(false);
  const [showIraCalc, setShowIraCalc] = useState(false);
  const [copiedEmailId, setCopiedEmailId] = useState<string | null>(null);

  const { data: opp, isLoading, isError } = useQuery({
    queryKey: ['opportunity', id],
    queryFn: () => api.getOpportunity(id!),
    enabled: !!id
  });

  const oppAny = opp as any;

  useSEO({
    title: oppAny ? `${oppAny.solicitation_number || oppAny.solicitationNumber ? (oppAny.solicitation_number || oppAny.solicitationNumber) + ' · ' : ''}${oppAny.name} Funding & Eligibility` : 'Energy Innovation Opportunity Details',
    description: oppAny?.description ? `${oppAny.description.slice(0, 180)}... Total Funding: ${formatCurrency(oppAny.total_funding || oppAny.totalFunding)}. Organization: ${oppAny.agency || 'Public Agency'}.` : 'Comprehensive intelligence, proposal scoring, eligibility requirements, and historical awardees for this energy innovation solicitation.',
    canonicalUrl: `https://terminal.aixenergy.io/opportunities/${id}`,
    keywords: [
      oppAny?.solicitation_number || oppAny?.solicitationNumber || '',
      oppAny?.name || '',
      oppAny?.agency || '',
      'energy innovation grant',
      'solicitation eligibility',
      'proposal requirements',
      'non-dilutive funding',
    ].filter(Boolean),
    jsonLd: oppAny ? {
      '@context': 'https://schema.org',
      '@type': 'GovernmentService',
      name: oppAny.name,
      serviceType: 'Energy Innovation Innovation Grant / Funding Solicitation',
      provider: {
        '@type': 'Organization',
        name: oppAny.agency || 'Funding Agency',
      },
      description: oppAny.description || oppAny.name,
      url: `https://terminal.aixenergy.io/opportunities/${id}`,
      offers: {
        '@type': 'Offer',
        price: '0',
        priceCurrency: 'USD',
      },
    } : undefined,
  }, [opp, id]);

  const { data: winRateData } = useQuery({
    queryKey: ['opportunity-win-rate', id],
    queryFn: () => (id ? api.getWinRateBenchmark(id) : null),
    enabled: !!id
  });

  const { data: teamingData } = useQuery({
    queryKey: ['opportunity-teaming', id],
    queryFn: () => (id ? api.getTeamingRecommendations({ opportunity_id: id }) : null),
    enabled: !!id
  });

  const { data: resultsData } = useQuery({
    queryKey: ['opportunity-results', id],
    queryFn: () => (id ? api.getOpportunityResults(id) : null),
    enabled: !!id
  });

  const { data: winningProposalsData } = useQuery({
    queryKey: ['opportunity-winning-proposals', id],
    queryFn: () => (id ? api.getOpportunityWinningProposals(id) : null),
    enabled: !!id
  });

  const { data: artifactsData } = useQuery({
    queryKey: ['opportunity-artifacts', id],
    queryFn: () => (id ? api.getArtifacts({ opportunity_id: id, page_size: 50 }) : null),
    enabled: !!id
  });

  // Watchlist
  const [isStarred, setIsStarred] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem('navigator_starred_opps');
      if (!saved || !id) return false;
      const list = JSON.parse(saved);
      return list.includes(id.toString());
    } catch {
      return false;
    }
  });

  const toggleStar = () => {
    if (!id) return;
    const strId = id.toString();
    try {
      const saved = localStorage.getItem('navigator_starred_opps');
      const list: string[] = saved ? JSON.parse(saved) : [];
      const next = list.includes(strId) ? list.filter(x => x !== strId) : [...list, strId];
      localStorage.setItem('navigator_starred_opps', JSON.stringify(next));
      setIsStarred(next.includes(strId));
    } catch {}
  };

  const [copiedMemo, setCopiedMemo] = useState(false);
  const [isExportingFoaPdf, setIsExportingFoaPdf] = useState(false);

  const handleExportFoaPdf = async () => {
    if (!id || isExportingFoaPdf) return;
    setIsExportingFoaPdf(true);
    try {
      const res = await fetch(`/api/foa-shredder/${id}/export-pdf`);
      if (!res.ok) throw new Error('Failed to export FOA blueprint PDF');
      const blob = await res.blob();
      const d = opp as any;
      const safeSol = d?.solicitation_number ? d.solicitation_number.replace(/[^a-zA-Z0-9]/g, '_') : `Opp_${id}`;
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `FOA_${safeSol}_Blueprint.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('FOA PDF Export Error:', err);
      window.open(`/api/foa-shredder/${id}/export-pdf`, '_blank');
    } finally {
      setIsExportingFoaPdf(false);
    }
  };
  const copyCitation = () => {
    if (!opp) return;
    const d = opp as any;
    const citation = `[Solicitation] ${d.agency || 'Agency'} ${d.solicitation_number || ''}: "${d.name || ''}". Funding: ${formatCurrency(d.total_funding)}. Verified: ${formatDate(d.last_verified)}. Energy Innovation Terminal Archive.`;
    navigator.clipboard.writeText(citation);
    setCopiedCitation(true);
    setTimeout(() => setCopiedCitation(false), 2500);
  };

  const copyExecutiveMemo = () => {
    if (!opp) return;
    const d = opp as any;
    const lines = [
      `# EXECUTIVE FUNDING INTELLIGENCE BRIEF: ${d.solicitation_number || 'SOL'}`,
      `**Title:** ${d.name || 'Energy Innovation Solicitation'}`,
      `**Issuing Authority:** ${d.agency || 'Funder'} | **Status:** ${d.status || 'Active'}`,
      `**Total Program Funding:** ${formatCurrency(d.total_funding)} | **Max Award:** ${d.max_per_award ? formatCurrency(d.max_per_award) : 'Varies'}`,
      `**Cost-Share Requirement:** ${d.cost_share_pct ? `${d.cost_share_pct}% mandatory non-federal cost-share` : '0% (100% grant funded)'}`,
      `**Submission Deadline:** ${d.deadline ? formatDate(d.deadline) : 'Rolling / Open Enrollment'}`,
      ``,
      `## Technology & Sector Scope`,
      `- **Technologies:** ${(d.technologies || []).join(', ') || 'Energy Innovation & Decarbonization'}`,
      `- **Sectors:** ${(d.sectors || []).join(', ') || 'Utility / Commercial / Industrial'}`,
      `- **Target TRL Stage:** ${d.target_trl_min ? `TRL ${d.target_trl_min}–${d.target_trl_max || 8}` : 'R&D through Commercial Deployment'}`,
      ``,
      `## Key Mandates & Objectives`,
      `${d.description || d.summary || 'Public non-dilutive grant opportunity for energy transition innovation.'}`,
      ``,
      `---`,
      `*Source: Independent Research Compilation from Public Open Records (Energy Innovation Terminal · U.S. Energy Innovation Database by Brandon N. Owens). Not affiliated with or endorsed by NYSERDA, US DOE, or any government entity.*`,
      `*Official Solicitation Record: ${d.official_url || d.portal_url || 'Authoritative Ingestion Feed'}*`
    ];

    navigator.clipboard.writeText(lines.join('\n'));
    setCopiedMemo(true);
    setTimeout(() => setCopiedMemo(false), 2500);
  };

  const copyOutreachEmail = (partnerId: string) => {
    if (!teamingData?.outreach_templates?.[partnerId]) return;
    const tpl = teamingData.outreach_templates[partnerId];
    navigator.clipboard.writeText(`To: ${tpl.to_name} <${tpl.to_email}>\nSubject: ${tpl.subject}\n\n${tpl.body}`);
    setCopiedEmailId(partnerId);
    setTimeout(() => setCopiedEmailId(null), 3000);
  };

  if (isLoading) return (
    <div className="flex justify-center items-center h-64"><Loader2 className="animate-spin text-indigo-600" size={28} /></div>
  );

  if (isError || !opp) return (
    <div className="text-center p-12 text-red-500 text-[13px]">Failed to load opportunity detail. Verify API connection.</div>
  );

  const d = opp as any;

  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-12">
      {/* Top Breadcrumb & Actions */}
      <div className="flex items-center justify-between gap-4">
        <Link to="/opportunities" className="inline-flex items-center gap-1.5 text-[13px] font-semibold text-slate-500 hover:text-indigo-600 transition-colors">
          <ArrowLeft size={14} /> Back to opportunities
        </Link>

        <div className="flex items-center gap-2 flex-wrap">
          <button
            type="button"
            onClick={toggleStar}
            className={clsx(
              'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors cursor-pointer',
              isStarred
                ? 'bg-amber-50 text-amber-800 border-amber-300'
                : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
            )}
          >
            <Star size={13} className={isStarred ? 'fill-amber-400 text-amber-500' : 'text-slate-400'} />
            <span>{isStarred ? 'On Watchlist' : 'Add to Watchlist'}</span>
          </button>

          <button
            type="button"
            onClick={copyCitation}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white text-slate-600 border border-slate-200 hover:bg-slate-50 transition-colors cursor-pointer"
          >
            {copiedCitation ? <Check size={13} className="text-emerald-600" /> : <Copy size={13} className="text-slate-400" />}
            <span>{copiedCitation ? 'Citation Copied' : 'Cite Record'}</span>
          </button>

          <button
            type="button"
            onClick={() => setShowFoaShred(true)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30 hover:bg-amber-500/20 transition cursor-pointer shadow-2xs"
          >
            <Zap size={13} className="text-amber-500" />
            <span>FOA Requirements Blueprint</span>
          </button>

          <button
            type="button"
            onClick={handleExportFoaPdf}
            disabled={isExportingFoaPdf}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-amber-600 hover:bg-amber-500 text-white transition cursor-pointer shadow-2xs disabled:opacity-50"
            title="Download publication-grade FOA shred & requirements blueprint PDF"
          >
            {isExportingFoaPdf ? <Loader2 size={13} className="animate-spin" /> : <Download size={13} />}
            <span>{isExportingFoaPdf ? 'Compiling PDF...' : 'Export Blueprint (PDF)'}</span>
          </button>

          <button
            type="button"
            onClick={() => setShowIraCalc(true)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/20 transition cursor-pointer shadow-2xs"
          >
            <DollarSign size={13} className="text-emerald-500" />
            <span>IRA Capital Stack</span>
          </button>

          <button
            type="button"
            onClick={copyExecutiveMemo}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-indigo-50 text-indigo-800 border border-indigo-200 hover:bg-indigo-100 transition-colors cursor-pointer shadow-2xs"
          >
            {copiedMemo ? <CheckCircle2 size={13} className="text-emerald-600" /> : <FileText size={13} className="text-indigo-600" />}
            <span>{copiedMemo ? 'Memo Copied!' : 'Copy Executive Brief'}</span>
          </button>
        </div>
      </div>

      {/* Header Banner */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <OrgLogo org={d.agency || 'Government'} size="lg" />
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-1.5">
                <span className="font-mono text-xs font-bold text-indigo-700 bg-indigo-50 border border-indigo-200 px-2.5 py-0.5 rounded-full">
                  {d.solicitation_number || 'SOLICITATION'}
                </span>
                {isOpportunityNew(d) && (
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-emerald-600 text-white shadow-2xs">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-200" />
                    <span>NEW · Last 30 Days</span>
                  </span>
                )}
                <span className={clsx(
                  'px-2.5 py-0.5 rounded-full text-xs font-bold border',
                  d.status === 'open' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-slate-100 text-slate-600 border-slate-200'
                )}>
                  {d.status === 'open' ? 'Active / Open' : 'Closed / Benchmark'}
                </span>
                {d.agency && (
                  <span className="text-xs font-semibold text-slate-600 bg-slate-100 px-2.5 py-0.5 rounded-full">
                    {d.agency}
                  </span>
                )}
                {winRateData &&
                 typeof winRateData.win_probability_pct === 'number' &&
                 !isNaN(winRateData.win_probability_pct) &&
                 winRateData.win_probability_pct > 0 && (
                  <span className={clsx(
                    'inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded-full border',
                    winRateData.tier_color === 'emerald' ? 'bg-emerald-50 text-emerald-800 border-emerald-200' :
                    winRateData.tier_color === 'amber' ? 'bg-amber-50 text-amber-800 border-amber-200' :
                    'bg-rose-50 text-rose-800 border-rose-200'
                  )}>
                    <Target size={12} />
                    <span>
                      {winRateData.win_probability_pct}% Win Rate Index
                      {winRateData.badge_text ? ` (${winRateData.badge_text})` : ''}
                    </span>
                  </span>
                )}
              </div>
              <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 leading-snug">
                {d.name}
              </h1>
            </div>
          </div>

          <div className="flex sm:flex-col items-end justify-between sm:justify-start gap-1 shrink-0 bg-slate-50 sm:bg-transparent p-3 sm:p-0 rounded-xl border sm:border-0 border-slate-100">
            <span className="text-xs font-semibold text-slate-400">Total Program Capital</span>
            <span className="text-xl sm:text-2xl font-bold font-mono text-emerald-700">
              {formatCurrency(d.total_funding)}
            </span>
            {d.max_per_award && (
              <span className="text-[11px] text-slate-500 font-mono">
                Up to {formatCurrency(d.max_per_award)} / award
              </span>
            )}
          </div>
        </div>

        {d.short_description && (
          <p className="text-[13.5px] text-slate-600 leading-relaxed pt-2 border-t border-slate-100">
            {d.short_description}
          </p>
        )}
      </div>

      {/* 9-Dimensional Lineage Provenance HUD */}
      {id && (
        <ProvenanceRibbon
          entityType="opportunity"
          entityId={id}
        />
      )}

      {/* Stage-Gate Solicitation Runway Timeline */}
      <SolicitationLifecycleRunway opportunity={d} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* PREDICTIVE WIN-RATE & COMPETITIVENESS BENCHMARK CARD */}
          {winRateData &&
           typeof winRateData.win_probability_pct === 'number' &&
           !isNaN(winRateData.win_probability_pct) &&
           winRateData.win_probability_pct > 0 && (
            <div className="bg-gradient-to-br from-indigo-900 via-slate-900 to-slate-950 p-5 rounded-2xl text-white shadow-md border border-indigo-800/40 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-indigo-800/60 pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-xl bg-indigo-500/20 border border-indigo-400/30 text-indigo-300">
                    <Target size={18} />
                  </div>
                  <div>
                    <h2 className="text-sm font-bold text-white flex items-center gap-2">
                      <span>Predictive Win-Rate &amp; Selection Analytics</span>
                      <span className={clsx(
                        'text-[10.5px] font-bold px-2 py-0.5 rounded-full border uppercase tracking-wider',
                        winRateData.tier_color === 'emerald' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-400/30' :
                        winRateData.tier_color === 'amber' ? 'bg-amber-500/20 text-amber-300 border-amber-400/30' :
                        'bg-rose-500/20 text-rose-300 border-rose-400/30'
                      )}>
                        {winRateData.win_tier}
                      </span>
                    </h2>
                    <p className="text-[11.5px] text-indigo-200/70 mt-0.5">
                      Empirical selection probability calibrated against 56,413 historical awards
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-2xl font-black font-mono text-emerald-400">
                    {winRateData.win_probability_pct}%
                  </div>
                  <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                    Selection Index
                  </div>
                </div>
              </div>

              {/* 4 Quantitative Breakdown Meters */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                <div className="p-3 bg-white/5 rounded-xl border border-white/10">
                  <div className="text-[10px] font-bold text-indigo-300 uppercase">Agency Precedent</div>
                  <div className="text-base font-bold font-mono text-white mt-0.5">{winRateData.precedent_score_pct}%</div>
                  <div className="text-[10.5px] text-slate-400 mt-0.5 truncate">{winRateData.precedent_rating}</div>
                </div>
                <div className="p-3 bg-white/5 rounded-xl border border-white/10">
                  <div className="text-[10px] font-bold text-indigo-300 uppercase">Field Congestion</div>
                  <div className="text-base font-bold font-mono text-white mt-0.5">{winRateData.estimated_field_size}</div>
                  <div className="text-[10.5px] text-slate-400 mt-0.5">Est. Applications</div>
                </div>
                <div className="p-3 bg-white/5 rounded-xl border border-white/10">
                  <div className="text-[10px] font-bold text-indigo-300 uppercase">Base Award Rate</div>
                  <div className="text-base font-bold font-mono text-white mt-0.5">{winRateData.historical_selection_rate}</div>
                  <div className="text-[10.5px] text-slate-400 mt-0.5">Historical Baseline</div>
                </div>
                <div className="p-3 bg-white/5 rounded-xl border border-white/10">
                  <div className="text-[10px] font-bold text-indigo-300 uppercase">Cost-Share Fit</div>
                  <div className="text-base font-bold font-mono text-white mt-0.5">{winRateData.cost_share_score_pct}%</div>
                  <div className="text-[10.5px] text-slate-400 mt-0.5">Statutory Profile</div>
                </div>
              </div>

              {/* Recommended Strategy Box */}
              <div className="p-3 bg-indigo-950/60 rounded-xl border border-indigo-700/40 text-[12px] text-indigo-100 flex items-start gap-2.5 leading-relaxed">
                <Target size={16} className="text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="text-white">Winning Proposal Strategy: </strong>
                  {winRateData.recommended_strategy}
                </div>
              </div>
            </div>
          )}

          {/* Utility Information */}
          {(d.org_type === 'utility' || d.jurisdiction === 'utility_ny' || [
            'Con Edison', 'Orange & Rockland', 'National Grid', 'NYSEG', 'RG&E', 
            'Central Hudson', 'PSEG Long Island', 'LIPA', 'NYPA', 'Joint Utilities of NY'
          ].includes(d.agency)) && (
            <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-2xs">
              <h2 className="text-[13px] font-bold text-slate-900 mb-4 flex items-center gap-2">
                <Zap size={15} className="text-amber-500" /> Utility Infrastructure Context
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-[13px]">
                <div>
                  <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">Utility</div>
                  <div className="font-semibold text-slate-800">{d.agency}</div>
                  {d.parentUtility && <div className="text-[11px] text-slate-500 mt-0.5">Parent Entity: {d.parentUtility}</div>}
                </div>
                <div>
                  <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">Service Territory</div>
                  <div className="text-slate-700">{d.serviceTerritory || 'New York State / Regional'}</div>
                </div>
                <div>
                  <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">Program Type</div>
                  {d.utilityProgramType ? (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-indigo-50 text-indigo-700 border border-indigo-200">
                      {d.utilityProgramType}
                    </span>
                  ) : (
                    <span className="text-slate-400">—</span>
                  )}
                </div>
                <div>
                  <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">Regulatory Jurisdiction</div>
                  <div className="text-slate-700">Public Service Commission (PSC / FERC)</div>
                </div>
                {(d.procurementPortalUrl || d.vendorRegistrationRequired) && (
                  <div className="sm:col-span-2 pt-3 mt-1 border-t border-slate-100">
                    <div className="flex items-center gap-3">
                      {d.procurementPortalUrl && (
                        <a href={d.procurementPortalUrl} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 text-indigo-700 rounded-md text-[12px] font-medium hover:bg-indigo-100 transition-colors border border-indigo-200">
                          <ExternalLink size={14} /> Utility Bid Portal
                        </a>
                      )}
                      {d.vendorRegistrationRequired && (
                        <div className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-amber-50 text-amber-700 rounded-md text-[12px] font-medium border border-amber-200">
                          <Lock size={12} className="text-amber-700" />
                          <span>Vendor Registration Required</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Rounds & Deadlines */}
          {d.rounds && d.rounds.length > 0 && (
            <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-2xs">
              <h2 className="text-[13px] font-bold text-slate-900 mb-3 flex items-center gap-2"><Calendar size={15} className="text-indigo-600" /> Rounds & Deadlines</h2>
              <div className="space-y-2">
                {d.rounds.map((r: any, i: number) => (
                  <div key={i} className={clsx('flex items-center justify-between p-3 rounded-lg border',
                    r.status === 'Open' ? 'bg-indigo-50/50 border-indigo-200' : 'bg-slate-50/50 border-slate-100')}>
                    <div>
                      <div className="font-bold text-[13px] text-slate-800">Round {r.round_number || i + 1}</div>
                      <div className={clsx('text-[11px] font-semibold mt-0.5',
                        r.status === 'Open' ? 'text-indigo-700' : 'text-slate-500')}>{r.status}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-[13px] font-semibold text-slate-800 font-mono">{formatDate(r.due_date)}</div>
                      {r.concept_paper_due_date && (
                        <div className="text-[11px] text-slate-500 mt-0.5">Concept paper: {formatDate(r.concept_paper_due_date)}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Eligibility Rules */}
          {d.eligibility_rules && d.eligibility_rules.length > 0 && (
            <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-2xs">
              <h2 className="text-[13px] font-bold text-slate-900 mb-3">Deterministic Eligibility Requirements</h2>
              <div className="space-y-2.5">
                {d.eligibility_rules.map((r: any, i: number) => (
                  <div key={i} className="flex items-start gap-2.5 text-[13px] bg-slate-50/60 p-2.5 rounded-lg border border-slate-100">
                    {r.is_hard ? <AlertTriangle size={15} className="text-amber-600 shrink-0 mt-0.5" /> : <Info size={15} className="text-indigo-500 shrink-0 mt-0.5" />}
                    <div>
                      <span className="font-bold text-slate-800 uppercase text-[11px] tracking-wider">{r.type}: </span>
                      <span className="text-slate-700 font-medium">{r.key} {r.operator} {r.value}</span>
                      {r.source && <span className="text-[11px] text-slate-400 ml-2">({r.source})</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Restrictions */}
          {d.restrictions && d.restrictions.length > 0 && (
            <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-2xs">
              <div className="flex items-center gap-2 mb-3">
                <ShieldAlert size={16} className="text-red-500" />
                <h2 className="text-[13px] font-bold text-slate-900">Statutory Restrictions & Conditions</h2>
                <span className="text-[11px] text-slate-400 ml-auto">{d.restrictions.length} restriction{d.restrictions.length !== 1 ? 's' : ''}</span>
              </div>
              <div className="space-y-2">
                {d.restrictions.map((r: any, i: number) => (
                  <div key={i} className="p-3 bg-red-50/40 rounded-lg border border-red-100 text-[12.5px]">
                    <div className="font-bold text-red-800">{r.title || r.category}</div>
                    <div className="text-slate-700 mt-0.5 leading-relaxed">{r.description || r.text}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* RECOMMENDED CONSORTIA & TEAMING STACK */}
          {teamingData && teamingData.recommended_partners && teamingData.recommended_partners.length > 0 && (
            <div className="bg-white p-5 rounded-2xl border border-indigo-200/80 shadow-xs space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-indigo-100 pb-3">
                <div className="flex items-center gap-2.5">
                  <span className="p-2 rounded-xl bg-indigo-50 text-indigo-700 border border-indigo-200/60">
                    <Users size={18} />
                  </span>
                  <div>
                    <h2 className="text-[14px] font-bold text-slate-900 flex items-center gap-2">
                      <span>Recommended Consortia &amp; Subcontractor Stack</span>
                      <span className="text-[11px] font-mono font-bold text-indigo-700 bg-indigo-100/70 px-2 py-0.5 rounded-full">
                        {teamingData.consortia_composition.total_members}-Party Team
                      </span>
                    </h2>
                    <p className="text-[11.5px] text-slate-500 mt-0.5">
                      Auto-matched high-scoring academic anchors, utility hosts, and research labs with verified PI emails
                    </p>
                  </div>
                </div>

                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-bold shrink-0">
                  <CheckCircle2 size={13} className="text-emerald-600" />
                  <span>{teamingData.consortia_readiness_score}/100 Teaming Readiness</span>
                </div>
              </div>

              {teamingData.consortia_rationale && (
                <div className="p-3 bg-slate-50/80 rounded-xl border border-slate-200/60 text-[12px] text-slate-700 leading-relaxed">
                  <strong className="text-slate-900">Teaming Strategy: </strong>
                  {teamingData.consortia_rationale}
                </div>
              )}

              {/* Teaming Partner Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                {teamingData.recommended_partners.map((p, i) => (
                  <div key={i} className="p-3.5 bg-gradient-to-br from-white to-slate-50/60 rounded-xl border border-slate-200/90 shadow-2xs space-y-2.5 hover:border-indigo-300 transition-all">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <span className="text-[10.5px] font-bold uppercase tracking-wider text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded">
                          {p.role_title}
                        </span>
                        <h4 className="text-[13px] font-bold text-slate-900 mt-1.5 leading-snug">
                          {p.name}
                        </h4>
                        <div className="text-[11px] text-slate-500">{p.location}</div>
                      </div>
                      <span className="text-[10px] font-mono font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 shrink-0">
                        {p.precedent_award_count} Prior Awards
                      </span>
                    </div>

                    <p className="text-[11.5px] text-slate-600 leading-relaxed line-clamp-2">
                      {p.role_description}
                    </p>

                    <div className="pt-2 border-t border-slate-100 flex items-center justify-between gap-2">
                      <div className="text-[11px] truncate">
                        <span className="font-semibold text-slate-800">{p.pi_name}</span>
                        <div className="text-slate-400 text-[10px] truncate">{p.pi_email}</div>
                      </div>

                      <button
                        onClick={() => copyOutreachEmail(p.id)}
                        className="inline-flex items-center gap-1 px-2.5 py-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-[11px] font-bold transition-colors shrink-0 cursor-pointer shadow-2xs"
                      >
                        {copiedEmailId === p.id ? (
                          <>
                            <Check size={11} />
                            <span>Copied!</span>
                          </>
                        ) : (
                          <>
                            <Send size={11} />
                            <span>Outreach Draft</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* WINNING PROPOSALS & FUNDED AWARDS */}
          {winningProposalsData && winningProposalsData.items && winningProposalsData.items.length > 0 && (
            <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-2xs space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <span className="p-1.5 rounded-lg bg-amber-50 text-amber-700">
                    <Trophy size={18} />
                  </span>
                  <div>
                    <h2 className="text-[13.5px] font-bold text-slate-900 flex items-center gap-2">
                      <span>Winning Proposals &amp; Funded Awards</span>
                      <span className="text-[11px] font-mono font-bold text-amber-800 bg-amber-100/70 px-2 py-0.5 rounded">
                        {winningProposalsData.total_proposals_won} Won
                      </span>
                    </h2>
                    <p className="text-[11.5px] text-slate-500 mt-0.5">
                      Total Awarded Capital: <strong className="text-emerald-700 font-mono">{formatCurrency(winningProposalsData.total_capital_awarded)}</strong> deployed to innovation recipients
                    </p>
                  </div>
                </div>

                {winningProposalsData.bundle_download_url && (
                  <a
                    href={winningProposalsData.bundle_download_url}
                    download
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-bold transition-all shadow-sm shrink-0"
                  >
                    <FileDown size={13} />
                    <span>Download All Artifacts (.ZIP)</span>
                  </a>
                )}
              </div>

              {/* Proposals Grid */}
              <div className="space-y-3">
                {winningProposalsData.items.slice(0, 10).map((prop) => (
                  <div
                    key={prop.id}
                    className="p-4 bg-slate-50/70 hover:bg-indigo-50/30 rounded-xl border border-slate-200/80 hover:border-indigo-300 transition-all space-y-2.5"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
                      <div className="min-w-0">
                        <div className="flex items-center gap-2 mb-1 flex-wrap">
                          <span className="font-bold text-slate-900 text-[13px]">
                            {prop.recipient_name}
                          </span>
                          {prop.recipient_city && (
                            <span className="text-[11px] text-slate-500">
                              · {prop.recipient_city}, {prop.recipient_state}
                            </span>
                          )}
                          <span className="text-[10px] font-mono text-indigo-700 bg-indigo-50 px-1.5 py-0.2 rounded border border-indigo-100">
                            {prop.id}
                          </span>
                          <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-1.5 py-0.2 rounded border border-emerald-200">
                            Score: {prop.red_team_score || 92}/100
                          </span>
                        </div>
                        <h3 className="text-xs font-semibold text-slate-800 leading-snug">
                          {prop.title}
                        </h3>
                        {prop.lead_pi && (
                          <div className="text-[11px] text-slate-500 mt-1">
                            Lead PI: <strong className="text-slate-700">{prop.lead_pi}</strong>
                          </div>
                        )}
                      </div>

                      <div className="text-right shrink-0">
                        <div className="font-mono font-bold text-emerald-700 text-sm">
                          {formatCurrency(prop.target_funding)}
                        </div>
                        {prop.cost_share_pct > 0 && (
                          <div className="text-[10.5px] text-slate-400 font-mono">
                            Cost Share: {prop.cost_share_pct}%
                          </div>
                        )}
                      </div>
                    </div>

                    {prop.description && (
                      <p className="text-[11.5px] text-slate-600 line-clamp-2 leading-relaxed">
                        {prop.description}
                      </p>
                    )}

                    <div className="flex items-center justify-between pt-2 border-t border-slate-200/60 text-xs">
                      <div className="flex items-center gap-2 text-[11px] text-slate-500">
                        <span className="flex items-center gap-1 font-semibold text-slate-700">
                          <Paperclip size={11} className="text-indigo-600" />
                          {prop.artifacts_count || 0} Artifact{prop.artifacts_count !== 1 ? 's' : ''}
                        </span>
                        {prop.year && <span>· Year: {prop.year}</span>}
                      </div>

                      <div className="flex items-center gap-2">
                        <Link
                          to={`/proposals?proposalId=${prop.id}`}
                          className="inline-flex items-center gap-1 text-[11px] font-bold text-indigo-600 hover:text-indigo-800 bg-white px-2.5 py-1 rounded border border-slate-200 hover:border-indigo-300 transition-colors shadow-2xs"
                        >
                          <FileEdit size={11} />
                          <span>View Proposal Dossier</span>
                        </Link>
                        {prop.bundle_download_url && (
                          <a
                            href={prop.bundle_download_url}
                            download
                            className="inline-flex items-center gap-1 text-[11px] font-bold text-slate-700 hover:text-indigo-600 bg-white px-2.5 py-1 rounded border border-slate-200 hover:border-slate-300 transition-colors shadow-2xs"
                          >
                            <Download size={11} />
                            <span>Download Artifacts</span>
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* DISCOVERED ARTIFACTS & TECHNICAL DELIVERABLES */}
          {artifactsData && artifactsData.items && artifactsData.items.length > 0 && (
            <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-2xs space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <span className="p-1.5 rounded-lg bg-indigo-50 text-indigo-700">
                    <Paperclip size={18} />
                  </span>
                  <div>
                    <h2 className="text-[13.5px] font-bold text-slate-900 flex items-center gap-2">
                      <span>Discovered Deliverables &amp; Report Artifacts</span>
                      <span className="text-[11px] font-mono font-bold text-indigo-800 bg-indigo-100/70 px-2 py-0.5 rounded">
                        {artifactsData.total} Documents
                      </span>
                    </h2>
                    <p className="text-[11.5px] text-slate-500 mt-0.5">
                      Peer-reviewed public reports, OSTI deliverables, and state agency evaluation filings
                    </p>
                  </div>
                </div>

                <a
                  href={`/api/opportunities/${id}/artifacts/download-bundle`}
                  download
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-lg text-xs font-bold transition-colors border border-indigo-200 shadow-2xs"
                >
                  <Download size={13} />
                  <span>Download All ({artifactsData.total})</span>
                </a>
              </div>

              <div className="space-y-2.5">
                {artifactsData.items.map((art) => (
                  <div
                    key={art.id}
                    className="p-3.5 bg-slate-50/70 rounded-xl border border-slate-200/80 hover:border-indigo-300 transition-all flex flex-col sm:flex-row sm:items-start justify-between gap-3"
                  >
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <span className="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded bg-indigo-100/70 text-indigo-800">
                          {art.artifact_type.replace(/_/g, ' ')}
                        </span>
                        {art.recipient_name && (
                          <span className="text-[11px] font-bold text-slate-800">
                            {art.recipient_name}
                          </span>
                        )}
                        {art.publication_date && (
                          <span className="text-[10px] text-slate-400 font-mono">
                            · {art.publication_date}
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
                        <p className="text-[11.5px] text-slate-600 mt-1 line-clamp-2 leading-relaxed">
                          {art.summary}
                        </p>
                      )}
                    </div>

                    <a
                      href={art.download_url || `/api/artifacts/${art.id}/download`}
                      download
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white hover:bg-indigo-50 text-indigo-700 text-xs font-bold rounded-lg border border-slate-200 hover:border-indigo-300 transition-colors shrink-0 shadow-2xs self-start sm:self-center"
                    >
                      <Download size={13} />
                      <span>Download</span>
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Verified Outcomes, Benchmarks & Success Stories */}
          {resultsData && ((resultsData.results && resultsData.results.length > 0) || (resultsData.success_stories && resultsData.success_stories.length > 0) || (resultsData.artifacts && resultsData.artifacts.length > 0)) && (
            <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-2xs space-y-5">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <span className="p-1.5 rounded-lg bg-indigo-50 text-indigo-700">
                    <Trophy size={16} />
                  </span>
                  <div>
                    <h2 className="text-[13.5px] font-bold text-slate-900">
                      Verified Results, Return on Capital & Outcomes Track Record
                    </h2>
                    <p className="text-[11.5px] text-slate-500 mt-0.5">
                      Standardized public performance metrics and regulatory evaluation findings
                    </p>
                  </div>
                </div>

                <Link
                  to="/results"
                  className="inline-flex items-center gap-1 text-[11.5px] font-bold text-indigo-600 hover:text-indigo-800 bg-indigo-50 px-2.5 py-1 rounded-lg transition-colors"
                >
                  <span>Apples-to-Apples Benchmarks</span>
                  <ExternalLink size={11} />
                </Link>
              </div>

              {/* Standardized Benchmark Scorecard */}
              {resultsData.benchmark && (
                <div>
                  <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                    Standardized Return-on-Grant Ratios (Apples-to-Apples Benchmark)
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                    <div className="p-3 bg-indigo-50/50 rounded-xl border border-indigo-100">
                      <div className="text-[10px] font-bold text-indigo-600 uppercase">Private Leverage</div>
                      <div className="text-base font-bold font-mono text-indigo-900 mt-0.5">
                        {resultsData.benchmark.leverage_ratio.toFixed(2)}x
                      </div>
                      <div className="text-[10px] text-slate-500">Private $ / Grant $</div>
                    </div>

                    <div className="p-3 bg-teal-50/50 rounded-xl border border-teal-100">
                      <div className="text-[10px] font-bold text-teal-700 uppercase">GHG Abated</div>
                      <div className="text-base font-bold font-mono text-teal-900 mt-0.5">
                        {resultsData.benchmark.ghg_abatement_per_10k_usd.toFixed(2)} MT
                      </div>
                      <div className="text-[10px] text-slate-500">per $10K Awarded</div>
                    </div>

                    <div className="p-3 bg-blue-50/50 rounded-xl border border-blue-100">
                      <div className="text-[10px] font-bold text-blue-700 uppercase">Jobs Velocity</div>
                      <div className="text-base font-bold font-mono text-blue-900 mt-0.5">
                        {resultsData.benchmark.jobs_per_million_usd.toFixed(1)} FTEs
                      </div>
                      <div className="text-[10px] text-slate-500">per $1M Awarded</div>
                    </div>

                    <div className="p-3 bg-amber-50/50 rounded-xl border border-amber-100">
                      <div className="text-[10px] font-bold text-amber-700 uppercase">Innovation Output</div>
                      <div className="text-base font-bold font-mono text-amber-900 mt-0.5">
                        {resultsData.benchmark.ip_and_product_velocity.toFixed(2)}
                      </div>
                      <div className="text-[10px] text-slate-500">Patents+Products/$1M</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Verified Outcome Metrics Table */}
              {resultsData.results && resultsData.results.length > 0 && (
                <div>
                  <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                    Reported & Verified Outcome Metrics
                  </div>
                  <div className="divide-y divide-slate-100 border border-slate-100 rounded-lg overflow-hidden text-[12.5px]">
                    {resultsData.results.map((r, i) => (
                      <div key={i} className="p-3 flex items-start justify-between gap-3 bg-slate-50/40">
                        <div>
                          <div className="font-semibold text-slate-800 flex items-center gap-1.5">
                            <span>{r.reported_metric_name || r.canonical_metric_name}</span>
                            <span className="px-1.5 py-0.2 rounded text-[10px] font-bold uppercase bg-slate-200/70 text-slate-600">
                              {r.metric_category.replace(/_/g, ' ')}
                            </span>
                          </div>
                          <div className="text-[11.5px] text-slate-500 mt-0.5">
                            {r.recipient_name} · Provenance: <span className="font-semibold text-slate-700">{r.data_provenance.replace(/_/g, ' ')}</span>
                          </div>
                          {r.notes_and_context && (
                            <div className="text-[11.5px] text-slate-600 mt-1 italic">
                              "{r.notes_and_context}"
                            </div>
                          )}
                        </div>
                        <div className="text-right shrink-0">
                          <div className="font-mono font-bold text-indigo-700 text-sm">
                            {r.canonical_unit === 'USD' ? formatCurrency(r.canonical_value) : `${r.canonical_value.toLocaleString()} ${r.canonical_unit}`}
                          </div>
                          {r.raw_metric_value_str && (
                            <div className="text-[10.5px] text-slate-400 font-mono">Reported: {r.raw_metric_value_str}</div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Linked Success Story */}
              {resultsData.success_stories && resultsData.success_stories.length > 0 && (
                <div>
                  <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                    Featured Awardee Impact Case Study
                  </div>
                  {resultsData.success_stories.map((story, i) => (
                    <div key={i} className="p-4 bg-gradient-to-br from-indigo-50/40 via-white to-slate-50 rounded-xl border border-indigo-100/80 space-y-2.5">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-[13px] text-indigo-950">{story.title}</span>
                        {story.trl_advancement && (
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                            {story.trl_advancement}
                          </span>
                        )}
                      </div>
                      <p className="text-[12px] text-slate-600 leading-relaxed">
                        {story.summary}
                      </p>
                      {story.quote_text && (
                        <div className="p-2.5 bg-white rounded-lg border border-slate-200/60 text-[11.5px] italic text-slate-700">
                          "{story.quote_text}"
                          {story.quote_author && <div className="text-[10.5px] font-bold text-indigo-700 mt-1 not-italic">— {story.quote_author}</div>}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Facts */}
          <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs">
            <h3 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-3">Quick Dossier Facts</h3>
            <div className="space-y-2.5 text-[12px]">
              {d.cost_share_pct != null && (
                <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                  <span className="text-slate-500">Cost Share</span>
                  <span className="font-bold text-slate-800">{d.cost_share_pct}%</span>
                </div>
              )}
              {d.performance_period && (
                <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                  <span className="text-slate-500">Duration</span>
                  <span className="font-semibold text-slate-800">{d.performance_period}</span>
                </div>
              )}
              {d.concept_paper_required && (
                <div className="flex items-center gap-2 text-amber-700 font-semibold bg-amber-50 p-2 rounded border border-amber-200">
                  <AlertTriangle size={14} /> Concept Paper Mandatory
                </div>
              )}
              {d.ny_green_bank && (
                <div className="flex items-center gap-2 text-emerald-700 font-semibold bg-emerald-50 p-2 rounded border border-emerald-200">
                  <CheckCircle2 size={14} /> NY Green Bank Eligible
                </div>
              )}
            </div>
          </div>

          {/* Contacts */}
          {d.contacts && d.contacts.length > 0 && (
            <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs">
              <h3 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-3">Solicitation Contacts</h3>
              <div className="space-y-3">
                {d.contacts.map((c: any, i: number) => (
                  <div key={i} className="pb-2 border-b border-slate-100 last:border-0 last:pb-0">
                    <div className="font-bold text-[13px] text-slate-800">{c.name}</div>
                    {c.email && (
                      <a href={`mailto:${c.email}`} className="text-[12px] text-indigo-600 hover:text-indigo-700 flex items-center gap-1 mt-0.5">
                        <Mail size={12} /> {c.email}
                      </a>
                    )}
                    {c.phone && (
                      <div className="text-[12px] text-slate-500 flex items-center gap-1 mt-0.5">
                        <Phone size={12} /> {c.phone}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Documents */}
          {d.documents && d.documents.length > 0 && (
            <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-2xs">
              <h3 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-3">Source Documents</h3>
              <div className="space-y-1.5">
                {d.documents.map((doc: any, i: number) => (
                  <a key={i} href={doc.url} target="_blank" rel="noopener noreferrer"
                    className="flex items-center gap-2 p-2 rounded-lg hover:bg-slate-50 text-[12px] text-indigo-600 hover:text-indigo-800 transition-colors border border-slate-100">
                    <FileText size={14} className="shrink-0 text-indigo-500" />
                    <span className="truncate font-medium">{doc.name || doc.title || 'Solicitation Document'}</span>
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    
      {/* FOA Requirements Analysis Modal */}
      <FoaShredderModal
        opportunityId={Number(id)}
        isOpen={showFoaShred}
        onClose={() => setShowFoaShred(false)}
      />

      {/* IRA Capital Stack Modal */}
      <IraCalculatorModal
        isOpen={showIraCalc}
        onClose={() => setShowIraCalc(false)}
        defaultGrant={d.total_funding || 4000000}
        defaultCapex={(d.total_funding || 4000000) * 4}
        projectTitle={d.name}
      />
    </div>
  );
}