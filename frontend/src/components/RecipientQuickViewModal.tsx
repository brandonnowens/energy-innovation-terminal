import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  Building2,
  Award,
  DollarSign,
  Globe,
  MapPin,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
  FileText,
  TrendingUp,
  Zap,
  Lightbulb,
  Download,
  Loader2,
  Users,
  X,
  Calendar,
  Layers,
  ArrowUpRight,
  Share2,
  Check,
  FileDown
} from 'lucide-react';
import { api, apiFetch, RecipientCapitalContinuumResponse } from '../api/client';
import { OrgLogo } from './OrgLogo';
import { CapitalContinuumTimeline } from './CapitalContinuumTimeline';

export interface RecipientQuickViewModalProps {
  isOpen: boolean;
  onClose: () => void;
  recipientId?: number | string | null;
  recipientName?: string | null;
}

function fmt(val: number | null | undefined): string {
  if (!val) return '$0';
  if (val >= 1_000_000_000) return `$${(val / 1_000_000_000).toFixed(2)}B`;
  if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(1)}M`;
  if (val >= 1_000) return `$${(val / 1_000).toFixed(0)}K`;
  return `$${val.toLocaleString()}`;
}

export function RecipientQuickViewModal({
  isOpen,
  onClose,
  recipientId,
  recipientName,
}: RecipientQuickViewModalProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'grants' | 'patents' | 'vc' | 'timeline'>('overview');
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [copiedLink, setCopiedLink] = useState(false);

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Lock body scroll when open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const queryKeyParam = recipientId || recipientName;

  // 1. Fetch deep continuum data (Grants, SEC filings, VC rounds, Patents, Contacts)
  const { data: continuum, isLoading: continuumLoading } = useQuery<RecipientCapitalContinuumResponse>({
    queryKey: ['recipient-continuum-modal', queryKeyParam],
    queryFn: async () => {
      if (recipientId && !isNaN(Number(recipientId))) {
        return api.getRecipientCapitalContinuum(Number(recipientId));
      }
      if (recipientName) {
        const res = await apiFetch(`/api/recipients/by-name/${encodeURIComponent(recipientName)}/capital-continuum`);
        if (res.ok) return res.json();
      }
      if (recipientId) {
        const res = await apiFetch(`/api/recipients/by-name/${encodeURIComponent(String(recipientId))}/capital-continuum`);
        if (res.ok) return res.json();
      }
      throw new Error('Recipient not found');
    },
    enabled: isOpen && !!queryKeyParam,
    staleTime: 5 * 60 * 1000,
  });

  // 2. Fetch awardee dossier detail for enriched description, technology tags, and metadata
  const { data: detail, isLoading: detailLoading } = useQuery<any>({
    queryKey: ['recipient-detail-modal', queryKeyParam],
    queryFn: async () => {
      const targetParam = recipientId || recipientName;
      if (!targetParam) throw new Error('No recipient identifier provided');
      const res = await apiFetch(`/api/awards/recipient/${encodeURIComponent(String(targetParam))}`);
      if (res.ok) return res.json();
      return null;
    },
    enabled: isOpen && !!queryKeyParam,
    staleTime: 5 * 60 * 1000,
  });

  if (!isOpen || !queryKeyParam) return null;

  const isLoading = continuumLoading && detailLoading;

  // Derive consolidated company profile
  const resolvedName = continuum?.name || detail?.name || recipientName || (typeof recipientId === 'string' ? recipientId : 'Company Profile');
  const resolvedId = continuum?.recipient_id || detail?.id || (typeof recipientId === 'number' ? recipientId : undefined);
  const primaryTech = continuum?.primary_technology || detail?.primary_technology || 'Energy Innovation';
  const city = continuum?.headquarters_city || detail?.city || '';
  const state = continuum?.headquarters_state || detail?.state || '';
  const locationStr = [city, state].filter(Boolean).join(', ') || 'United States';
  const websiteUrl = detail?.website_url || '';
  const description = detail?.description || '';
  const stage = detail?.commercialization_stage || 'Applied R&D (TRL 5–7)';
  const employeeRange = detail?.employee_range || '11–50 employees';
  const fundedAgencies = detail?.funded_agencies || [];
  const keyInnovations = detail?.key_innovations || '';
  const climateImpact = detail?.climate_impact || '';

  // Financial aggregates
  const aggregates = continuum?.financial_aggregates;
  const totalPublicGrants = aggregates?.total_public_grants_usd || detail?.total_funding_received || 0;
  const totalSecD = aggregates?.total_sec_form_d_usd || 0;
  const totalVc = aggregates?.total_vc_investments_usd || 0;
  const grandTotalCapital = aggregates?.grand_total_capital_usd || (totalPublicGrants + totalSecD + totalVc);

  const grants = continuum?.grants || (detail?.awards?.map((a: any) => ({
    id: a.id,
    agency: a.agency,
    award_amount: a.amount,
    award_date: a.date,
    project_title: a.title,
    solicitation_number: a.program
  })) || []);

  const patents = continuum?.patents || [];
  const vcRounds = continuum?.vc_rounds || [];
  const secFilings = continuum?.sec_form_d_filings || [];
  const contacts = continuum?.contacts || [];

  const handleDownloadPdf = async () => {
    if (isExportingPdf) return;
    try {
      setIsExportingPdf(true);
      const targetUrl = resolvedId
        ? `/api/recipients/${resolvedId}/export-pdf`
        : `/api/recipients/by-name/${encodeURIComponent(resolvedName)}/export-pdf`;
      const res = await apiFetch(targetUrl);
      if (!res.ok) throw new Error('Failed to generate PDF briefing');
      const blob = await res.blob();
      const safeName = resolvedName.replace(/[^a-zA-Z0-9]/g, '_');
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${safeName}_Executive_Brief_EnergyInnovation.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download PDF error:', err);
      alert('Failed to generate executive brief PDF. Please try again.');
    } finally {
      setIsExportingPdf(false);
    }
  };

  const handleCopyLink = () => {
    const url = resolvedId
      ? `${window.location.origin}/recipients/${resolvedId}`
      : `${window.location.origin}/awards?search=${encodeURIComponent(resolvedName)}`;
    navigator.clipboard.writeText(url);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2500);
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-950/70 backdrop-blur-sm flex justify-center p-2 sm:p-4 md:p-6 animate-in fade-in duration-200">
      <div 
        className="relative w-full max-w-5xl bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 flex flex-col max-h-[92vh] overflow-hidden my-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Top Header Bar */}
        <div className="p-5 sm:p-6 border-b border-slate-200 dark:border-slate-800 bg-gradient-to-r from-slate-50 via-white to-slate-50 dark:from-slate-900 dark:via-slate-900/90 dark:to-slate-900 shrink-0">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3.5 min-w-0">
              <div className="p-2.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm shrink-0 mt-0.5">
                <OrgLogo org={resolvedName} domain={websiteUrl} size="md" />
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <h2 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white tracking-tight truncate">
                    {resolvedName}
                  </h2>
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 text-xs font-bold border border-emerald-200 dark:border-emerald-800 shrink-0">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>Tracked Awardee</span>
                  </span>
                  {state && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-cyan-50 dark:bg-cyan-950/40 text-cyan-700 dark:text-cyan-400 text-xs font-bold border border-cyan-200 dark:border-cyan-800 shrink-0">
                      <MapPin className="w-3 h-3" />
                      <span>{locationStr}</span>
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-3 mt-1.5 text-xs text-slate-600 dark:text-slate-400 flex-wrap">
                  <span className="font-semibold text-slate-800 dark:text-slate-200 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">
                    {primaryTech}
                  </span>
                  <span>•</span>
                  <span>{stage}</span>
                  {websiteUrl && (
                    <>
                      <span>•</span>
                      <a
                        href={websiteUrl.startsWith('http') ? websiteUrl : `https://${websiteUrl}`}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-cyan-600 dark:text-cyan-400 hover:underline font-medium"
                      >
                        <Globe className="w-3.5 h-3.5" />
                        <span>{websiteUrl.replace(/^https?:\/\//, '').replace(/\/$/, '')}</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* Header Actions */}
            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={handleDownloadPdf}
                disabled={isExportingPdf}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white rounded-xl text-xs font-bold shadow-md hover:shadow-lg transition-all disabled:opacity-50"
                title="Download publication-grade executive brief PDF"
              >
                {isExportingPdf ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <FileDown className="w-4 h-4" />
                )}
                <span className="hidden sm:inline">Download Executive Brief (PDF)</span>
                <span className="sm:hidden">PDF</span>
              </button>

              {resolvedId && (
                <Link
                  to={`/recipients/${resolvedId}`}
                  target="_blank"
                  className="hidden md:inline-flex items-center gap-1 px-3 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-semibold transition"
                  title="Open full dossier page in new tab"
                >
                  <span>Full Dossier</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </Link>
              )}

              <button
                onClick={handleCopyLink}
                className="p-2 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition"
                title="Copy share link"
              >
                {copiedLink ? <Check className="w-4 h-4 text-emerald-500" /> : <Share2 className="w-4 h-4" />}
              </button>

              <button
                onClick={onClose}
                className="p-2 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition"
                aria-label="Close modal"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 mt-4 pt-4 border-t border-slate-200/80 dark:border-slate-800/80">
            <div className="p-2.5 rounded-xl bg-emerald-50/60 dark:bg-emerald-950/20 border border-emerald-200/60 dark:border-emerald-900/30">
              <div className="text-[10px] uppercase font-bold text-emerald-700 dark:text-emerald-400 tracking-wider">Public Grants Won</div>
              <div className="text-base sm:text-lg font-black text-emerald-900 dark:text-emerald-200 font-mono mt-0.5">
                {fmt(totalPublicGrants)}
              </div>
              <div className="text-[10px] text-emerald-600 dark:text-emerald-400/80 font-medium">
                {grants.length} competitive awards
              </div>
            </div>

            <div className="p-2.5 rounded-xl bg-cyan-50/60 dark:bg-cyan-950/20 border border-cyan-200/60 dark:border-cyan-900/30">
              <div className="text-[10px] uppercase font-bold text-cyan-700 dark:text-cyan-400 tracking-wider">Private Capital & VC</div>
              <div className="text-base sm:text-lg font-black text-cyan-900 dark:text-cyan-200 font-mono mt-0.5">
                {fmt(totalVc + totalSecD)}
              </div>
              <div className="text-[10px] text-cyan-600 dark:text-cyan-400/80 font-medium">
                {vcRounds.length + secFilings.length} funding rounds / filings
              </div>
            </div>

            <div className="p-2.5 rounded-xl bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200/60 dark:border-amber-900/30">
              <div className="text-[10px] uppercase font-bold text-amber-700 dark:text-amber-400 tracking-wider">Commercial Patents</div>
              <div className="text-base sm:text-lg font-black text-amber-900 dark:text-amber-200 font-mono mt-0.5">
                {patents.length}
              </div>
              <div className="text-[10px] text-amber-600 dark:text-amber-400/80 font-medium">
                USPTO & Bayh-Dole IP
              </div>
            </div>

            <div className="p-2.5 rounded-xl bg-indigo-50/60 dark:bg-indigo-950/20 border border-indigo-200/60 dark:border-indigo-900/30">
              <div className="text-[10px] uppercase font-bold text-indigo-700 dark:text-indigo-400 tracking-wider">Total Tracked Capital</div>
              <div className="text-base sm:text-lg font-black text-indigo-900 dark:text-indigo-200 font-mono mt-0.5">
                {fmt(grandTotalCapital)}
              </div>
              <div className="text-[10px] text-indigo-600 dark:text-indigo-400/80 font-medium">
                Public-private continuum
              </div>
            </div>
          </div>
        </div>

        {/* Modal Navigation Tabs */}
        <div className="flex items-center gap-1 px-5 border-b border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-900/60 overflow-x-auto shrink-0">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-3.5 py-2.5 text-xs font-bold border-b-2 transition-colors whitespace-nowrap flex items-center gap-1.5 ${
              activeTab === 'overview'
                ? 'border-cyan-600 text-cyan-600 dark:border-cyan-400 dark:text-cyan-400'
                : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Building2 className="w-3.5 h-3.5" />
            <span>Overview &amp; Tech</span>
          </button>

          <button
            onClick={() => setActiveTab('grants')}
            className={`px-3.5 py-2.5 text-xs font-bold border-b-2 transition-colors whitespace-nowrap flex items-center gap-1.5 ${
              activeTab === 'grants'
                ? 'border-cyan-600 text-cyan-600 dark:border-cyan-400 dark:text-cyan-400'
                : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Award className="w-3.5 h-3.5" />
            <span>Grant Awards ({grants.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('patents')}
            className={`px-3.5 py-2.5 text-xs font-bold border-b-2 transition-colors whitespace-nowrap flex items-center gap-1.5 ${
              activeTab === 'patents'
                ? 'border-cyan-600 text-cyan-600 dark:border-cyan-400 dark:text-cyan-400'
                : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Lightbulb className="w-3.5 h-3.5" />
            <span>Patents &amp; IP ({patents.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('vc')}
            className={`px-3.5 py-2.5 text-xs font-bold border-b-2 transition-colors whitespace-nowrap flex items-center gap-1.5 ${
              activeTab === 'vc'
                ? 'border-cyan-600 text-cyan-600 dark:border-cyan-400 dark:text-cyan-400'
                : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <TrendingUp className="w-3.5 h-3.5" />
            <span>Private Capital ({vcRounds.length + secFilings.length})</span>
          </button>

          {continuum && (
            <button
              onClick={() => setActiveTab('timeline')}
              className={`px-3.5 py-2.5 text-xs font-bold border-b-2 transition-colors whitespace-nowrap flex items-center gap-1.5 ${
                activeTab === 'timeline'
                  ? 'border-cyan-600 text-cyan-600 dark:border-cyan-400 dark:text-cyan-400'
                : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Capital Continuum Timeline</span>
          </button>
        )}
        </div>

        {/* Scrollable Body Content */}
        <div className="p-5 sm:p-6 overflow-y-auto flex-1 space-y-6">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-16 space-y-3">
              <Loader2 className="w-8 h-8 animate-spin text-cyan-600" />
              <p className="text-sm font-medium text-slate-500">Compiling recipient intelligence dossier &amp; capital records...</p>
            </div>
          ) : (
            <>
              {/* === TAB 1: OVERVIEW & TECH === */}
              {activeTab === 'overview' && (
                <div className="space-y-6">
                  {/* Executive Summary */}
                  <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2 flex items-center gap-1.5">
                      <FileText className="w-3.5 h-3.5 text-cyan-600" />
                      <span>Executive Summary &amp; Scope</span>
                    </h3>
                    <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                      {description || `${resolvedName} is an active energy innovation enterprise operating in ${primaryTech}, focused on advancing scalable clean technologies from demonstration to commercial deployment.`}
                    </p>
                  </div>

                  {/* Innovations & Climate Impact */}
                  {(keyInnovations || climateImpact) && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {keyInnovations && (
                        <div className="p-4 rounded-xl bg-cyan-50/40 dark:bg-cyan-950/20 border border-cyan-200/60 dark:border-cyan-800/40">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-800 dark:text-cyan-300 mb-1.5 flex items-center gap-1.5">
                            <Zap className="w-3.5 h-3.5 text-cyan-600" />
                            <span>Core Engineering Innovations</span>
                          </h4>
                          <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
                            {keyInnovations}
                          </p>
                        </div>
                      )}

                      {climateImpact && (
                        <div className="p-4 rounded-xl bg-emerald-50/40 dark:bg-emerald-950/20 border border-emerald-200/60 dark:border-emerald-800/40">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-800 dark:text-emerald-300 mb-1.5 flex items-center gap-1.5">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                            <span>Climate &amp; Environmental Impact</span>
                          </h4>
                          <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
                            {climateImpact}
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Key Contacts & Principal Investigators */}
                  {contacts.length > 0 && (
                    <div className="space-y-3">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                        <Users className="w-3.5 h-3.5 text-indigo-600" />
                        <span>Key Contacts &amp; Principal Investigators ({contacts.length})</span>
                      </h3>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {contacts.slice(0, 6).map((c: any, idx: number) => (
                          <div key={idx} className="p-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm flex items-start gap-3">
                            <div className="w-8 h-8 rounded-full bg-indigo-50 dark:bg-indigo-950/50 text-indigo-700 dark:text-indigo-400 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                              {c.name_display ? c.name_display.charAt(0).toUpperCase() : 'P'}
                            </div>
                            <div className="min-w-0 flex-1">
                              <div className="font-bold text-xs text-slate-900 dark:text-white truncate">
                                {c.name_display}
                              </div>
                              <div className="text-[11px] text-slate-500 dark:text-slate-400 truncate">
                                {c.title || 'Principal Investigator'}
                              </div>
                              {c.email && (
                                <div className="text-[10px] text-emerald-600 dark:text-emerald-400 font-mono mt-0.5 truncate">
                                  {c.email}
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* === TAB 2: GRANT AWARDS LEDGER === */}
              {activeTab === 'grants' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>Showing all historical public grant awards and solicitations won.</span>
                    <span className="font-mono font-bold text-slate-700 dark:text-slate-300">
                      Total: {fmt(totalPublicGrants)}
                    </span>
                  </div>

                  {grants.length === 0 ? (
                    <div className="text-center py-12 border border-dashed border-slate-200 dark:border-slate-800 rounded-xl">
                      <Award className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                      <p className="text-xs text-slate-500">No public grant awards indexed for this entity.</p>
                    </div>
                  ) : (
                    <div className="divide-y divide-slate-200 dark:divide-slate-800 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden">
                      {grants.map((g: any, idx: number) => (
                        <div key={idx} className="p-4 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition">
                          <div className="flex items-start justify-between gap-4">
                            <div className="space-y-1 min-w-0">
                              <div className="flex items-center gap-2 flex-wrap">
                                <span className="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-[11px] font-bold">
                                  {g.agency || 'Federal / State Funder'}
                                </span>
                                {g.solicitation_number && (
                                  <span className="text-[11px] font-mono text-slate-500">
                                    {g.solicitation_number}
                                  </span>
                                )}
                                {g.award_date && (
                                  <span className="text-[11px] text-slate-400 flex items-center gap-1">
                                    <Calendar className="w-3 h-3" />
                                    {g.award_date}
                                  </span>
                                )}
                              </div>
                              <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                                {g.project_title || 'Clean Energy Demonstration & Deployment'}
                              </h4>
                            </div>

                            <div className="text-right shrink-0">
                              <div className="text-sm sm:text-base font-black font-mono text-emerald-600 dark:text-emerald-400">
                                {fmt(g.award_amount)}
                              </div>
                              <div className="text-[10px] text-slate-400">
                                Non-Dilutive Grant
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* === TAB 3: PATENTS & IP === */}
              {activeTab === 'patents' && (
                <div className="space-y-4">
                  <div className="text-xs text-slate-500">
                    Tracked Bayh-Dole inventions and USPTO intellectual property patents.
                  </div>

                  {patents.length === 0 ? (
                    <div className="text-center py-12 border border-dashed border-slate-200 dark:border-slate-800 rounded-xl">
                      <Lightbulb className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                      <p className="text-xs text-slate-500">No commercial patent filings recorded in current active ledger.</p>
                    </div>
                  ) : (
                    <div className="divide-y divide-slate-200 dark:divide-slate-800 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden">
                      {patents.map((p: any, idx: number) => (
                        <div key={idx} className="p-4 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition">
                          <div className="flex items-start justify-between gap-4">
                            <div className="space-y-1">
                              <div className="flex items-center gap-2">
                                <span className="font-mono font-bold text-xs text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/40 px-2 py-0.5 rounded border border-amber-200 dark:border-amber-800">
                                  US #{p.patent_number}
                                </span>
                                {p.grant_date && (
                                  <span className="text-[11px] text-slate-400">
                                    Granted: {p.grant_date}
                                  </span>
                                )}
                              </div>
                              <h4 className="text-xs sm:text-sm font-bold text-slate-900 dark:text-white">
                                {p.title}
                              </h4>
                              {p.bayh_dole_citation && (
                                <div className="text-[11px] text-slate-500 dark:text-slate-400">
                                  <span className="font-semibold">Bayh-Dole Gov Interest:</span> {p.bayh_dole_citation}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* === TAB 4: PRIVATE CAPITAL & VC === */}
              {activeTab === 'vc' && (
                <div className="space-y-6">
                  {/* VC Rounds */}
                  <div>
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-3 flex items-center gap-1.5">
                      <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Venture Capital &amp; Equity Rounds ({vcRounds.length})</span>
                    </h3>

                    {vcRounds.length === 0 ? (
                      <p className="text-xs text-slate-400 italic">No private venture rounds indexed.</p>
                    ) : (
                      <div className="divide-y divide-slate-200 dark:divide-slate-800 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden">
                        {vcRounds.map((v: any, idx: number) => (
                          <div key={idx} className="p-3.5 bg-white dark:bg-slate-900 flex items-center justify-between gap-4">
                            <div>
                              <div className="font-bold text-xs text-slate-900 dark:text-white">
                                {v.round_type || 'Equity Financing'}
                              </div>
                              <div className="text-[11px] text-slate-500">
                                Lead: <span className="font-semibold text-slate-700 dark:text-slate-300">{v.lead_investor || 'Syndicate Co-Investors'}</span>
                                {v.round_date && ` • ${v.round_date}`}
                              </div>
                            </div>
                            <div className="text-right font-mono font-bold text-emerald-600 dark:text-emerald-400 text-sm">
                              {fmt(v.amount_usd)}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* SEC Form D Offerings */}
                  {secFilings.length > 0 && (
                    <div>
                      <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-3 flex items-center gap-1.5">
                        <DollarSign className="w-3.5 h-3.5 text-amber-600" />
                        <span>SEC Form D Reg D Offerings ({secFilings.length})</span>
                      </h3>
                      <div className="divide-y divide-slate-200 dark:divide-slate-800 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden">
                        {secFilings.map((s: any, idx: number) => (
                          <div key={idx} className="p-3.5 bg-white dark:bg-slate-900 flex items-center justify-between gap-4">
                            <div>
                              <div className="font-mono text-xs font-bold text-slate-900 dark:text-white">
                                CIK #{s.cik} • SEC Reg D
                              </div>
                              <div className="text-[11px] text-slate-500">
                                Filing Date: {s.filing_date} • {s.is_equity ? 'Equity' : 'Debt'}
                              </div>
                            </div>
                            <div className="text-right font-mono font-bold text-amber-600 dark:text-amber-400 text-sm">
                              {fmt(s.amount_sold_usd)}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* === TAB 5: CAPITAL CONTINUUM TIMELINE === */}
              {activeTab === 'timeline' && continuum && (
                <div className="space-y-3">
                  <div className="text-xs text-slate-500">
                    Chronological capital stack progression across non-dilutive grants, SEC Form D, VC rounds, and scale-up allocations.
                  </div>
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 overflow-x-auto">
                    <CapitalContinuumTimeline continuum={continuum} recipientName={resolvedName} />
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer Bar */}
        <div className="p-3.5 sm:p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/80 flex items-center justify-between text-xs text-slate-500 shrink-0">
          <div className="flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Energy Innovation Terminal Due Diligence Archive</span>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleDownloadPdf}
              disabled={isExportingPdf}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold shadow-sm transition disabled:opacity-50"
            >
              {isExportingPdf ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
              <span>Download PDF</span>
            </button>

            <button
              onClick={onClose}
              className="px-3 py-1.5 bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-semibold transition"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
