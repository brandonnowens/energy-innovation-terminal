import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  Building2, Award, DollarSign, Globe, MapPin, Tag, 
  ExternalLink, Share2, Code, ArrowLeft, ShieldCheck, CheckCircle2,
  Sparkles, FileText, TrendingUp, Layers, Zap, Lightbulb
} from 'lucide-react';
import { api, RecipientCapitalContinuumResponse } from '../api/client';
import { updatePageMeta } from '../utils/seo';

interface RecipientDossierData {
  recipient: {
    id: number;
    name: string;
    recipient_type?: string;
    headquarters_city?: string;
    headquarters_state?: string;
    primary_technology?: string;
    sector?: string;
    description?: string;
    website_url?: string;
    commercialization_stage?: string;
    employee_range?: string;
    total_funding_received?: number;
    total_awards_count?: number;
    climate_impact_focus?: string;
    key_innovations?: string;
  };
  awards?: Array<{
    id: number;
    project_title: string;
    award_amount: number;
    agency: string;
    program_name: string;
    year: number;
    award_date?: string;
  }>;
  patents?: Array<{
    id: number;
    patent_number: string;
    title: string;
    filing_date: string;
  }>;
  investments?: Array<{
    id: number;
    round_type: string;
    amount_usd: number;
    lead_investor: string;
    deal_date: string;
  }>;
}

function fmt(val: number | null | undefined): string {
  if (!val) return '$0';
  if (val >= 1_000_000_000) return `$${(val / 1_000_000_000).toFixed(2)}B`;
  if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(1)}M`;
  if (val >= 1_000) return `$${(val / 1_000).toFixed(0)}K`;
  return `$${val.toLocaleString()}`;
}

export default function RecipientDossier() {
  const { id } = useParams<{ id: string }>();
  const [copiedBadge, setCopiedBadge] = useState(false);
  const [copiedLink, setCopiedLink] = useState(false);

  const { data, isLoading, error } = useQuery<RecipientDossierData>({
    queryKey: ['recipient-dossier', id],
    queryFn: async () => {
      const res = await fetch(`/api/attributions/recipients/${id}`);
      if (!res.ok) {
        // Fallback to direct recipient query if attributions not found
        const recRes = await fetch(`/api/awards/recipients/${id}`);
        if (recRes.ok) return recRes.json();
        throw new Error('Recipient not found');
      }
      return res.json();
    },
    enabled: !!id,
  });

  const { data: continuum } = useQuery<RecipientCapitalContinuumResponse>({
    queryKey: ['recipient-continuum-dossier', id],
    queryFn: () => api.getRecipientCapitalContinuum(Number(id!)),
    enabled: !!id,
  });

  const recipient = data?.recipient;

  useEffect(() => {
    if (recipient) {
      const tech = recipient.primary_technology || 'Energy Innovation';
      const funding = recipient.total_funding_received 
        ? `$${(recipient.total_funding_received / 1_000_000).toFixed(1)}M` 
        : '$0';
      
      updatePageMeta({
        title: `${recipient.name} - Energy Innovation Funding Dossier & Grants`,
        description: `Tracked with ${funding} in public grant funding across ${recipient.total_awards_count || 0} awards in ${tech}. Explore DOE awards, patent linkages, and venture attributions.`,
        canonicalUrl: `https://energyinnovation.terminal/recipients/${recipient.id}`,
        ogImage: `https://energyinnovation.terminal/api/seo/badge/${recipient.id}.svg`,
        keywords: [recipient.name, tech, recipient.sector || 'Clean Tech', 'DOE Grants', 'Energy Innovation Awards', 'Public Funding'],
        jsonLd: {
          '@context': 'https://schema.org',
          '@type': 'Organization',
          name: recipient.name,
          description: recipient.description,
          url: recipient.website_url,
          knowsAbout: [tech, recipient.sector || 'Energy Innovation'],
        },
      });
    }
  }, [recipient]);

  const copyBadgeSnippet = () => {
    if (!recipient) return;
    const snippet = `<a href="https://energyinnovation.terminal/recipients/${recipient.id}"><img src="https://energyinnovation.terminal/api/seo/badge/${recipient.id}.svg" alt="${recipient.name} Energy Innovation Funding" /></a>`;
    navigator.clipboard.writeText(snippet);
    setCopiedBadge(true);
    setTimeout(() => setCopiedBadge(false), 3000);
  };

  const copyShareLink = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 3000);
  };

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-cyan-500"></div>
      </div>
    );
  }

  if (error || !recipient) {
    return (
      <div className="p-8 text-center max-w-lg mx-auto">
        <Building2 className="h-12 w-12 text-slate-400 mx-auto mb-3" />
        <h2 className="text-xl font-bold text-slate-900">Recipient Not Found</h2>
        <p className="text-sm text-slate-600 mt-1 mb-4">The requested recipient record could not be loaded.</p>
        <Link to="/awards" className="inline-flex items-center gap-2 text-cyan-600 font-medium hover:underline">
          <ArrowLeft className="h-4 w-4" /> Back to Awards &amp; Recipients
        </Link>
      </div>
    );
  }

  const fundingTotal = recipient.total_funding_received || continuum?.financial_aggregates?.total_public_grants_usd || 0;
  const totalVcAmount = continuum?.financial_aggregates?.total_vc_investments_usd || 
    (data?.investments || []).reduce((s, inv) => s + (inv.amount_usd || 0), 0);
  const totalVcRounds = continuum?.vc_rounds?.length || (data?.investments || []).length;
  const grandTotalCapital = continuum?.financial_aggregates?.grand_total_capital_usd || (fundingTotal + totalVcAmount);
  const totalPatentsCount = continuum?.patents?.length || (data?.patents || []).length;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      {/* Breadcrumb & Navigation */}
      <div className="flex items-center justify-between">
        <Link to="/awards" className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-slate-800 transition-colors">
          <ArrowLeft className="h-4 w-4" /> Back to Awards Database
        </Link>
        <div className="flex items-center gap-2">
          <button 
            onClick={copyShareLink}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 shadow-sm transition-all"
          >
            {copiedLink ? <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" /> : <Share2 className="h-3.5 w-3.5" />}
            {copiedLink ? 'Link Copied!' : 'Share Dossier'}
          </button>
          <button 
            onClick={copyBadgeSnippet}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-cyan-50 border border-cyan-200 text-cyan-800 hover:bg-cyan-100 shadow-sm transition-all"
          >
            {copiedBadge ? <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" /> : <Code className="h-3.5 w-3.5" />}
            {copiedBadge ? 'Badge Snippet Copied!' : 'Embed Web Badge'}
          </button>
        </div>
      </div>

      {/* Hero Header Card */}
      <div className="bg-slate-900 text-white rounded-2xl p-6 sm:p-8 shadow-xl border border-slate-800 relative overflow-hidden">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="relative z-10 flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
          <div className="space-y-3 max-w-2xl">
            <div className="flex flex-wrap items-center gap-2.5">
              <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                {recipient.recipient_type || 'Innovator'}
              </span>
              {recipient.commercialization_stage && (
                <span className="px-3 py-1 rounded-full text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
                  {recipient.commercialization_stage}
                </span>
              )}
              {recipient.primary_technology && (
                <span className="px-3 py-1 rounded-full text-xs font-medium bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  {recipient.primary_technology}
                </span>
              )}
            </div>

            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
              {recipient.name}
            </h1>

            <div className="flex flex-wrap items-center gap-4 text-sm text-slate-400">
              {(recipient.headquarters_city || recipient.headquarters_state) && (
                <div className="flex items-center gap-1.5">
                  <MapPin className="h-4 w-4 text-slate-500" />
                  <span>{[recipient.headquarters_city, recipient.headquarters_state].filter(Boolean).join(', ')}</span>
                </div>
              )}
              {recipient.employee_range && (
                <div className="flex items-center gap-1.5">
                  <Building2 className="h-4 w-4 text-slate-500" />
                  <span>{recipient.employee_range} Employees</span>
                </div>
              )}
              {recipient.website_url && (
                <a 
                  href={recipient.website_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 text-cyan-400 hover:text-cyan-300 font-medium transition-colors"
                >
                  <Globe className="h-4 w-4" />
                  <span>Official Website</span>
                  <ExternalLink className="h-3 w-3" />
                </a>
              )}
            </div>

            <p className="text-slate-300 text-base leading-relaxed pt-2">
              {recipient.description}
            </p>
          </div>

          {/* Quick Stats Highlights - Unified Hybrid Capital Stack */}
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-2 gap-3 w-full lg:w-auto shrink-0">
            <div className="bg-slate-800/80 rounded-xl p-3.5 border border-slate-700/60 backdrop-blur-sm">
              <div className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider">1. Public Grants</div>
              <div className="text-xl sm:text-2xl font-extrabold text-white mt-1">
                {fmt(fundingTotal)}
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">{recipient.total_awards_count || 0} Tracked Wins</div>
            </div>

            <div className="bg-slate-800/80 rounded-xl p-3.5 border border-slate-700/60 backdrop-blur-sm">
              <div className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">2. Private VC / Equity</div>
              <div className="text-xl sm:text-2xl font-extrabold text-white mt-1">
                {fmt(totalVcAmount)}
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">{totalVcRounds} Rounds Raised</div>
            </div>

            <div className="bg-slate-800/80 rounded-xl p-3.5 border border-emerald-500/30 bg-emerald-950/20 backdrop-blur-sm">
              <div className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">Grand Total Capital</div>
              <div className="text-xl sm:text-2xl font-extrabold text-emerald-300 mt-1 font-mono">
                {fmt(grandTotalCapital)}
              </div>
              <div className="text-[11px] text-emerald-400/80 mt-0.5">Hybrid Capital Stack</div>
            </div>

            <div className="bg-slate-800/80 rounded-xl p-3.5 border border-slate-700/60 backdrop-blur-sm">
              <div className="text-[10px] font-bold text-amber-400 uppercase tracking-wider">Commercial IP</div>
              <div className="text-xl sm:text-2xl font-extrabold text-white mt-1">
                {totalPatentsCount}
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">Patents &amp; Filings</div>
            </div>
          </div>
        </div>
      </div>

      {/* ── MULTI-STAGE CAPITAL CONTINUUM DASHBOARD ── */}
      {continuum && (
        <div className="bg-slate-900 text-white rounded-2xl p-6 sm:p-8 shadow-xl border border-slate-800 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-white/10">
            <div>
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  Full Capital Continuum Ledger
                </span>
                <span className="text-xs text-slate-400 font-mono">Grants → Reg D → Equity → Scale-Up → Offtake</span>
              </div>
              <h2 className="text-xl font-bold text-white mt-1">Multi-Stage Capital Stack &amp; Tracked Ledger</h2>
            </div>
            <div className="text-right">
              <div className="text-xs text-slate-400 font-mono uppercase">Grand Total Capital Tracked</div>
              <div className="text-2xl sm:text-3xl font-extrabold font-mono text-emerald-400">
                {fmt(continuum.financial_aggregates.grand_total_capital_usd)}
              </div>
            </div>
          </div>

          {/* 5-Stage Continuum Stage Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            <div className="p-3.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 space-y-1">
              <div className="text-[10px] uppercase font-bold text-cyan-300 font-mono">1. Public Grants</div>
              <div className="text-lg font-bold font-mono text-white">{fmt(continuum.financial_aggregates.total_public_grants_usd)}</div>
              <div className="text-[10.5px] text-slate-400">{continuum.grants?.length || 0} Awards Tracked</div>
            </div>

            <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 space-y-1">
              <div className="text-[10px] uppercase font-bold text-amber-300 font-mono">2. SEC Form D</div>
              <div className="text-lg font-bold font-mono text-white">{fmt(continuum.financial_aggregates.total_sec_form_d_usd)}</div>
              <div className="text-[10.5px] text-slate-400">{continuum.sec_form_d_filings?.length || 0} Reg D Filings</div>
            </div>

            <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 space-y-1">
              <div className="text-[10px] uppercase font-bold text-emerald-300 font-mono">3. VC Equity</div>
              <div className="text-lg font-bold font-mono text-white">{fmt(continuum.financial_aggregates.total_vc_investments_usd)}</div>
              <div className="text-[10.5px] text-slate-400">{continuum.vc_rounds?.length || 0} Rounds Led</div>
            </div>

            <div className="p-3.5 rounded-xl bg-purple-500/10 border border-purple-500/30 space-y-1">
              <div className="text-[10px] uppercase font-bold text-purple-300 font-mono">4. Scale-Up (LPO/48C)</div>
              <div className="text-lg font-bold font-mono text-white">{fmt(continuum.financial_aggregates.total_scaleup_allocations_usd)}</div>
              <div className="text-[10.5px] text-slate-400">{continuum.scaleup_allocations?.length || 0} Facilities</div>
            </div>

            <div className="p-3.5 rounded-xl bg-indigo-500/10 border border-indigo-500/30 space-y-1">
              <div className="text-[10px] uppercase font-bold text-indigo-300 font-mono">5. Offtake / Contracts</div>
              <div className="text-lg font-bold font-mono text-white">{fmt(continuum.financial_aggregates.total_procurement_offtake_usd)}</div>
              <div className="text-[10.5px] text-slate-400">{continuum.procurement_contracts?.length || 0} FPDS Contracts</div>
            </div>
          </div>

          {/* Detailed Continuum Accordions / Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 pt-2">
            {/* SEC Form D Filings Card */}
            {continuum.sec_form_d_filings && continuum.sec_form_d_filings.length > 0 && (
              <div className="p-4 rounded-xl bg-white/[0.03] border border-white/10 space-y-2.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-amber-300 uppercase font-mono flex items-center gap-1.5">
                    <DollarSign size={13} /> SEC Form D Exempt Offerings
                  </span>
                  <span className="text-slate-400 font-mono">{continuum.sec_form_d_filings.length} Filings</span>
                </div>
                <div className="space-y-2">
                  {continuum.sec_form_d_filings.map((f) => (
                    <div key={f.id} className="p-3 rounded-lg bg-black/40 border border-white/5 text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold font-mono text-slate-200">CIK #{f.cik}</span>
                        <span className="font-mono font-bold text-emerald-400">{fmt(f.amount_sold_usd)} Sold</span>
                      </div>
                      <div className="text-slate-400 text-[11px] flex items-center justify-between">
                        <span>Filing Date: {f.filing_date || 'N/A'}</span>
                        {f.sec_url && (
                          <a href={f.sec_url} target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:underline flex items-center gap-1 font-bold font-mono">
                            <span>EDGAR</span>
                            <ExternalLink size={10} />
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Federal Scale-Up (LPO/48C) Card */}
            {continuum.scaleup_allocations && continuum.scaleup_allocations.length > 0 && (
              <div className="p-4 rounded-xl bg-white/[0.03] border border-white/10 space-y-2.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-purple-300 uppercase font-mono flex items-center gap-1.5">
                    <Zap size={13} /> Scale-Up Facilities (DOE LPO / 48C)
                  </span>
                  <span className="text-slate-400 font-mono">{continuum.scaleup_allocations.length} Allocations</span>
                </div>
                <div className="space-y-2">
                  {continuum.scaleup_allocations.map((alloc) => (
                    <div key={alloc.id} className="p-3 rounded-lg bg-black/40 border border-white/5 text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-white">{alloc.facility_name}</span>
                        <span className="font-mono font-bold text-purple-400">{fmt(alloc.allocation_amount_usd)}</span>
                      </div>
                      <div className="text-slate-400 text-[11px] flex items-center justify-between">
                        <span>{alloc.program_category}</span>
                        <span className="px-1.5 py-0.2 rounded bg-purple-500/20 text-purple-300 font-bold font-mono text-[9.5px]">{alloc.status}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Federal Procurement Contracts */}
            {continuum.procurement_contracts && continuum.procurement_contracts.length > 0 && (
              <div className="p-4 rounded-xl bg-white/[0.03] border border-white/10 space-y-2.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-indigo-300 uppercase font-mono flex items-center gap-1.5">
                    <ShieldCheck size={13} /> Federal Procurement &amp; Offtake
                  </span>
                  <span className="text-slate-400 font-mono">{continuum.procurement_contracts.length} Contracts</span>
                </div>
                <div className="space-y-2">
                  {continuum.procurement_contracts.map((c) => (
                    <div key={c.id} className="p-3 rounded-lg bg-black/40 border border-white/5 text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-mono font-bold text-slate-200">{c.contract_number}</span>
                        <span className="font-mono font-bold text-indigo-400">{fmt(c.obligated_amount_usd)}</span>
                      </div>
                      <div className="text-slate-400 text-[11px] flex items-center justify-between">
                        <span>Agency: {c.agency}</span>
                        {c.is_sbir_phase_3 && (
                          <span className="px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 font-bold font-mono text-[9.5px]">SBIR Phase III</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ISO Interconnection Positions */}
            {continuum.interconnection_queues && continuum.interconnection_queues.length > 0 && (
              <div className="p-4 rounded-xl bg-white/[0.03] border border-white/10 space-y-2.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-cyan-300 uppercase font-mono flex items-center gap-1.5">
                    <Zap size={13} /> Grid Interconnection Queue Positions
                  </span>
                  <span className="text-slate-400 font-mono">{continuum.interconnection_queues.length} Positions</span>
                </div>
                <div className="space-y-2">
                  {continuum.interconnection_queues.map((q) => (
                    <div key={q.id} className="p-3 rounded-lg bg-black/40 border border-white/5 text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-white">{q.project_name}</span>
                        <span className="font-mono font-bold text-cyan-400">{q.capacity_mw} MW</span>
                      </div>
                      <div className="text-slate-400 text-[11px] flex items-center justify-between">
                        <span>{q.iso_rto} · Queue #{q.queue_id}</span>
                        <span className="px-1.5 py-0.2 rounded bg-cyan-500/20 text-cyan-300 font-bold font-mono text-[9.5px]">{q.study_phase || q.status}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Climate Impact & Key Innovations Focus */}
      {(recipient.climate_impact_focus || recipient.key_innovations) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {recipient.climate_impact_focus && (
            <div className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-sm">
              <div className="flex items-center gap-2 text-emerald-700 font-bold text-sm mb-2">
                <Sparkles className="h-4 w-4" /> Climate Impact &amp; Decarbonization Mandate
              </div>
              <p className="text-sm text-slate-700 leading-relaxed">
                {recipient.climate_impact_focus}
              </p>
            </div>
          )}

          {recipient.key_innovations && (
            <div className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-sm">
              <div className="flex items-center gap-2 text-indigo-700 font-bold text-sm mb-2">
                <Layers className="h-4 w-4" /> Core Innovations &amp; Project Domains
              </div>
              <p className="text-sm text-slate-700 leading-relaxed">
                {recipient.key_innovations}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Awards Ledger Section */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Award className="h-5 w-5 text-cyan-600" /> Competitive Public Grant Awards Ledger
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">Historical non-dilutive awards across DOE, NSF, ARPA-E, and state programs</p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-100 text-slate-700">
            {data?.awards?.length || recipient.total_awards_count || 0} Records
          </span>
        </div>

        {data?.awards && data.awards.length > 0 ? (
          <div className="divide-y divide-slate-100">
            {data.awards.map((aw) => (
              <div key={aw.id} className="p-5 hover:bg-slate-50/80 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="space-y-1 max-w-3xl">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold px-2 py-0.5 rounded bg-cyan-100 text-cyan-800">
                      {aw.agency || 'Public Agency'}
                    </span>
                    {aw.program_name && (
                      <span className="text-xs font-medium text-slate-500">
                        {aw.program_name}
                      </span>
                    )}
                    <span className="text-xs text-slate-400">| Year {aw.year}</span>
                  </div>
                  <h3 className="text-sm font-semibold text-slate-900 leading-snug">
                    {aw.project_title}
                  </h3>
                </div>

                <div className="text-right whitespace-nowrap">
                  <div className="text-base font-bold text-slate-900">
                    ${aw.award_amount ? aw.award_amount.toLocaleString() : 'N/A'}
                  </div>
                  <div className="text-xs text-slate-400">Awarded Amount</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-sm text-slate-500">
            Detailed project ledger records are being indexed for this recipient.
          </div>
        )}
      </div>

      {/* Embed Badge Promotion Footer */}
      <div className="bg-slate-50 rounded-xl p-6 border border-slate-200/80 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="space-y-1 text-center sm:text-left">
          <div className="text-sm font-bold text-slate-900 flex items-center justify-center sm:justify-start gap-1.5">
            <ShieldCheck className="h-4 w-4 text-cyan-600" /> Embed Verified Public Funding Badge on Your Website
          </div>
          <p className="text-xs text-slate-500">
            Showcase your tracked federal and state energy innovation grant validation to investors, partners, and customers.
          </p>
        </div>
        <button
          onClick={copyBadgeSnippet}
          className="px-4 py-2 text-xs font-bold rounded-lg bg-slate-900 text-white hover:bg-slate-800 shadow-sm transition-all whitespace-nowrap"
        >
          {copiedBadge ? 'Badge Snippet Copied!' : 'Get Embed Code'}
        </button>
      </div>
    </div>
  );
}
