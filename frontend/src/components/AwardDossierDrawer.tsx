import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api, AwardMapMarker } from '../api/client';
import {
  X, Building2, User, MapPin, DollarSign, Calendar, ExternalLink,
  FileText, Award, Globe, Mail, Phone, Loader2, Layers,
  ChevronRight, BookmarkCheck, Atom, Zap, Lightbulb, TrendingUp
} from 'lucide-react';
import { OrgLogo } from './OrgLogo';
import { InteractiveEgoGraph } from './InteractiveEgoGraph';
import { ProvenanceRibbon } from './ProvenanceRibbon';

interface AwardDossierDrawerProps {
  award: AwardMapMarker | null;
  onClose: () => void;
  onSelectRelatedAward?: (awardId: number) => void;
}

function fmt(value?: number | null): string {
  if (!value) return '—';
  if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
  if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
  if (value >= 1e3) return `$${(value / 1e3).toFixed(1)}K`;
  return `$${value.toLocaleString()}`;
}

function fmtDate(d?: string | null): string {
  if (!d) return '—';
  try {
    return new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  } catch {
    return d;
  }
}

export const AwardDossierDrawer: React.FC<AwardDossierDrawerProps> = ({
  award,
  onClose,
  onSelectRelatedAward,
}) => {
  const awardId = award?.id;

  const { data: detail, isLoading } = useQuery({
    queryKey: ['award-detail', awardId],
    queryFn: () => (awardId ? api.getAward(awardId) : null),
    enabled: !!awardId,
  });

  // Query related awards for the same recipient
  const { data: relatedAwards } = useQuery({
    queryKey: ['award-related', award?.name],
    queryFn: () => (award?.name ? api.getAwards({ recipient: award.name, page_size: 5 }) : null),
    enabled: !!award?.name,
  });

  // Query enriched recipient profile intelligence
  const { data: recipientDetail } = useQuery({
    queryKey: ['recipient-detail', award?.name],
    queryFn: () => (award?.name ? api.getRecipientDetail(award.name) : null),
    enabled: !!award?.name,
  });

  // Query attribution dossier (patents and venture funding)
  const { data: attributionDossier } = useQuery({
    queryKey: ['award-attributions', award?.name],
    queryFn: async () => {
      if (!award?.name) return null;
      try {
        const res = await api.getAttributionRecipients({ search: award.name });
        if (res?.items?.[0]) {
          return api.getRecipientAttributionDossier(res.items[0].id);
        }
      } catch {}
      return null;
    },
    enabled: !!award?.name,
  });

  if (!award) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden pointer-events-none">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-slate-900/40 backdrop-blur-[2px] transition-opacity duration-300 pointer-events-auto"
        onClick={onClose}
      />

      {/* Slide-over Drawer Panel */}
      <div className="absolute inset-y-0 right-0 max-w-full flex pl-10 pointer-events-auto">
        <div className="w-screen max-w-xl bg-white shadow-2xl border-l border-slate-200 flex flex-col transform transition-transform duration-300 ease-in-out">
          {/* Drawer Header */}
          <div className="p-5 border-b border-slate-100 bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white relative">
            <div className="flex items-center justify-between gap-3 mb-3">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider bg-white/10 text-white border border-white/20">
                  {award.agency}
                </span>
                {award.type && (
                  <span className="px-2 py-0.5 rounded text-[10px] font-medium capitalize bg-indigo-500/20 text-indigo-200 border border-indigo-500/30">
                    {award.type}
                  </span>
                )}
                {award.year && (
                  <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-white/5 text-slate-300">
                    {award.year}
                  </span>
                )}
                {award.award_phase && (
                  <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    {award.award_phase}
                  </span>
                )}
              </div>
              <button
                onClick={onClose}
                className="p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-white/10 transition-colors"
                title="Close dossier"
              >
                <X size={18} />
              </button>
            </div>

            <h2 className="text-lg font-bold text-white leading-snug">
              {award.name}
            </h2>
            {award.title && (
              <p className="text-[13px] text-indigo-100/80 mt-1 line-clamp-2 leading-relaxed">
                {award.title}
              </p>
            )}

            {/* Quick Metrics Bar */}
            <div className="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-white/10">
              <div className="bg-white/5 rounded p-2">
                <span className="text-[10px] text-slate-300 block uppercase font-medium">Award Funding</span>
                <span className="text-base font-bold text-emerald-400">{fmt(award.amount)}</span>
              </div>
              <div className="bg-white/5 rounded p-2">
                <span className="text-[10px] text-slate-300 block uppercase font-medium">Location</span>
                <span className="text-xs font-semibold text-white truncate block">
                  {[award.city, award.state].filter(Boolean).join(', ') || 'United States'}
                </span>
              </div>
              <div className="bg-white/5 rounded p-2">
                <span className="text-[10px] text-slate-300 block uppercase font-medium">Primary Tech</span>
                <span className="text-xs font-semibold text-amber-300 truncate block">
                  {recipientDetail?.primary_technology || award.technologies?.[0] || 'Energy Innovation'}
                </span>
              </div>
            </div>
          </div>

          {/* Drawer Body */}
          <div className="flex-1 overflow-y-auto p-5 space-y-5 bg-slate-50/50">
            {isLoading ? (
              <div className="flex flex-col items-center justify-center py-16 text-slate-400 gap-2">
                <Loader2 className="animate-spin text-indigo-600" size={28} />
                <span className="text-[13px]">Loading complete award profile...</span>
              </div>
            ) : (
              <>
                {/* 9-Dimensional Lineage Provenance HUD */}
                <ProvenanceRibbon
                  entityType="award"
                  entityId={award.id}
                />

                {/* Organization Intelligence Dossier Card */}
                {recipientDetail && (
                  <div className="bg-white p-4 rounded-xl border border-indigo-200/80 shadow-2xs space-y-3 relative overflow-hidden">
                    <div className="flex items-center justify-between">
                      <h3 className="text-[11px] font-extrabold text-indigo-900 uppercase tracking-wider flex items-center gap-1.5">
                        <Building2 size={14} className="text-indigo-600" /> Organization Intelligence
                      </h3>
                      {recipientDetail.state && (
                        <span className="px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-800 border border-indigo-200 text-[10px] font-extrabold flex items-center gap-1">
                          <MapPin size={10} className="text-indigo-600" />
                          <span>{recipientDetail.state} Innovator</span>
                        </span>
                      )}
                    </div>

                    {recipientDetail.description && (
                      <p className="text-[13px] text-slate-700 leading-relaxed font-medium">
                        {recipientDetail.description}
                      </p>
                    )}

                    <div className="grid grid-cols-2 gap-3 text-[12px] pt-2 border-t border-slate-100">
                      <div>
                        <span className="text-[10px] text-slate-400 uppercase font-bold block">Primary Technology</span>
                        <span className="font-bold text-indigo-700">{recipientDetail.primary_technology}</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-400 uppercase font-bold block">Commercial Stage</span>
                        <span className="font-semibold text-slate-800">{recipientDetail.commercialization_stage}</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-400 uppercase font-bold block">State / Regional Grants</span>
                        <span className="font-extrabold text-indigo-700 font-mono">{fmt(recipientDetail.state_funding || recipientDetail.nyserda_funding)}</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-400 uppercase font-bold block">Total Innovation Capital</span>
                        <span className="font-extrabold text-emerald-700 font-mono">{fmt(recipientDetail.total_funding)}</span>
                      </div>
                      {recipientDetail.employee_range && (
                        <div>
                          <span className="text-[10px] text-slate-400 uppercase font-bold block">Employee Scale</span>
                          <span className="font-semibold text-slate-700">{recipientDetail.employee_range} employees</span>
                        </div>
                      )}
                      {(recipientDetail.website_url || award.website) && (
                        <div>
                          <span className="text-[10px] text-slate-400 uppercase font-bold block">Official Portal</span>
                          <a
                            href={(recipientDetail.website_url || award.website || '').startsWith('http') ? (recipientDetail.website_url || award.website || '') : `https://${recipientDetail.website_url || award.website}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-indigo-600 font-bold hover:underline flex items-center gap-1 truncate"
                          >
                            <Globe size={11} /> {recipientDetail.website_url || award.website}
                          </a>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Patents & Venture Capital Commercialization Intelligence */}
                {attributionDossier && (attributionDossier.patents.length > 0 || attributionDossier.investments.length > 0) && (
                  <div className="bg-white p-4 rounded-xl border border-amber-200/80 shadow-2xs space-y-3">
                    <div className="flex items-center justify-between">
                      <h3 className="text-[11px] font-extrabold text-amber-900 uppercase tracking-wider flex items-center gap-1.5">
                        <Lightbulb size={14} className="text-amber-600" /> Patents & Venture Capital Attributions
                      </h3>
                      <span className="px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200 text-[10px] font-bold">
                        Commercialized IP
                      </span>
                    </div>

                    {attributionDossier.ego_graph?.nodes?.length > 1 && (
                      <div className="pt-1">
                        <InteractiveEgoGraph
                          egoGraph={attributionDossier.ego_graph}
                          companyName={award.name}
                          height={240}
                        />
                      </div>
                    )}

                    {attributionDossier.patents.length > 0 && (
                      <div>
                        <span className="text-[10px] text-slate-400 uppercase font-bold block mb-1">
                          USPTO Bayh-Dole Patents ({attributionDossier.patents.length})
                        </span>
                        <div className="space-y-1.5">
                          {attributionDossier.patents.map(p => (
                            <div key={p.id} className="p-2 rounded bg-amber-50/50 border border-amber-100 text-xs">
                              <div className="flex items-center justify-between">
                                <span className="font-bold text-slate-900 truncate pr-2">{p.title}</span>
                                {p.patent_url ? (
                                  <a href={p.patent_url} target="_blank" rel="noopener noreferrer" className="text-indigo-600 font-mono font-bold text-[10.5px] hover:underline flex items-center gap-0.5 shrink-0">
                                    <span>{p.patent_number}</span>
                                    <ExternalLink size={9} />
                                  </a>
                                ) : (
                                  <span className="font-mono text-slate-600 text-[10.5px]">{p.patent_number}</span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {attributionDossier.investments.length > 0 && (
                      <div className="pt-2 border-t border-slate-100">
                        <span className="text-[10px] text-slate-400 uppercase font-bold block mb-1">
                          Private VC Equity Rounds ({attributionDossier.investments.length})
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {attributionDossier.investments.map(inv => (
                            <span key={inv.id} className="px-2 py-1 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-semibold">
                              {inv.round_type}: {fmt(inv.amount_usd)} ({inv.lead_investor || 'VC Backed'})
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Taxonomy & Thematic Classification */}
                <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs space-y-3">
                  <h3 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                    <Layers size={13} className="text-indigo-600" /> Thematic Classification
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                    {(award.technologies?.length ?? 0) > 0 && (
                      <div>
                        <span className="text-[10px] text-slate-400 uppercase font-semibold block mb-1">Technology</span>
                        <div className="flex flex-wrap gap-1">
                          {award.technologies?.map(t => (
                            <span key={t} className="px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-100 font-medium text-[11px]">
                              {t}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {(award.sectors?.length ?? 0) > 0 && (
                      <div>
                        <span className="text-[10px] text-slate-400 uppercase font-semibold block mb-1">Sector</span>
                        <div className="flex flex-wrap gap-1">
                          {award.sectors?.map(s => (
                            <span key={s} className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-100 font-medium text-[11px]">
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {(award.fuels?.length ?? 0) > 0 && (
                      <div>
                        <span className="text-[10px] text-slate-400 uppercase font-semibold block mb-1">Fuel / Resource</span>
                        <div className="flex flex-wrap gap-1">
                          {award.fuels?.map(f => (
                            <span key={f} className="px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-100 font-medium text-[11px]">
                              {f}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {(award.stages?.length ?? 0) > 0 && (
                      <div>
                        <span className="text-[10px] text-slate-400 uppercase font-semibold block mb-1">Innovation Stage</span>
                        <div className="flex flex-wrap gap-1">
                          {award.stages?.map(st => (
                            <span key={st} className="px-2 py-0.5 rounded-full bg-sky-50 text-sky-700 border border-sky-100 font-medium text-[11px]">
                              {st}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Project Abstract */}
                {(detail?.project_abstract || award.abstract_snippet) && (
                  <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs space-y-2">
                    <h3 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                      <FileText size={13} className="text-slate-400" /> Project Abstract & Scope
                    </h3>
                    <p className="text-[13px] text-slate-700 leading-relaxed whitespace-pre-wrap">
                      {detail?.project_abstract || award.abstract_snippet}
                    </p>
                  </div>
                )}

                {/* Recipient Details & Contacts */}
                <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs space-y-3">
                  <h3 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                    <Building2 size={13} className="text-slate-400" /> Recipient Profile & Location
                  </h3>
                  <div className="grid grid-cols-2 gap-3 text-[12px]">
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase font-medium block">Organization Name</span>
                      <span className="font-semibold text-slate-800">{award.name}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase font-medium block">Entity Type</span>
                      <span className="capitalize text-slate-700">{award.type || 'Organization'}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase font-medium block">Geographic Location</span>
                      <span className="text-slate-700 flex items-center gap-1">
                        <MapPin size={11} className="text-slate-400 shrink-0" />
                        {[award.city, award.state, detail?.recipient_zip].filter(Boolean).join(', ') || '-'}
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase font-medium block">Coordinates</span>
                      <span className="font-mono text-[11px] text-slate-600">
                        {award.lat.toFixed(4)}, {award.lng.toFixed(4)}
                      </span>
                    </div>
                    {award.website && (
                      <div className="col-span-2">
                        <span className="text-[10px] text-slate-400 uppercase font-medium block">Website</span>
                        <a
                          href={award.website.startsWith('http') ? award.website : `https://${award.website}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-indigo-600 hover:text-indigo-800 hover:underline flex items-center gap-1 font-medium truncate"
                        >
                          <Globe size={11} /> {award.website}
                        </a>
                      </div>
                    )}
                  </div>
                </div>

                {/* Principal Investigator */}
                {(award.pi || detail?.pi_name || detail?.pi_email) && (
                  <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs space-y-3">
                    <h3 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                      <User size={13} className="text-slate-400" /> Principal Investigator
                    </h3>
                    <div className="grid grid-cols-2 gap-3 text-[12px]">
                      <div>
                        <span className="text-[10px] text-slate-400 uppercase font-medium block">PI Name</span>
                        <span className="font-semibold text-slate-800">{detail?.pi_name || award.pi}</span>
                      </div>
                      {detail?.pi_institution && (
                        <div>
                          <span className="text-[10px] text-slate-400 uppercase font-medium block">Institution</span>
                          <span className="text-slate-700">{detail.pi_institution}</span>
                        </div>
                      )}
                      {detail?.pi_email && (
                        <div className="col-span-2">
                          <span className="text-[10px] text-slate-400 uppercase font-medium block">Email</span>
                          <a href={`mailto:${detail.pi_email}`} className="text-indigo-600 hover:underline flex items-center gap-1 font-medium">
                            <Mail size={11} /> {detail.pi_email}
                          </a>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Award Program & Funding Details */}
                <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs space-y-3">
                  <h3 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                    <Award size={13} className="text-slate-400" /> Award & Program Specifications
                  </h3>
                  <div className="grid grid-cols-2 gap-3 text-[12px]">
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase font-medium block">Funding Agency</span>
                      <div className="flex items-center gap-1.5 mt-0.5">
                        <OrgLogo org={award.agency} size="xs" />
                        <span className="font-semibold text-slate-800">{award.agency}</span>
                      </div>
                    </div>
                    {award.program && (
                      <div>
                        <span className="text-[10px] text-slate-400 uppercase font-medium block">Program / Initiative</span>
                        <span className="font-medium text-slate-700">{award.program}</span>
                      </div>
                    )}
                    {detail?.award_type && (
                      <div>
                        <span className="text-[10px] text-slate-400 uppercase font-medium block">Award Instrument</span>
                        <span className="capitalize text-slate-700">{detail.award_type.replace(/_/g, ' ')}</span>
                      </div>
                    )}
                    {detail?.cfda_number && (
                      <div>
                        <span className="text-[10px] text-slate-400 uppercase font-medium block">CFDA Number</span>
                        <span className="font-mono text-slate-700">{detail.cfda_number}</span>
                      </div>
                    )}
                    {detail?.start_date && (
                      <div>
                        <span className="text-[10px] text-slate-400 uppercase font-medium block">Start Date</span>
                        <span className="text-slate-700">{fmtDate(detail.start_date)}</span>
                      </div>
                    )}
                    {detail?.end_date && (
                      <div>
                        <span className="text-[10px] text-slate-400 uppercase font-medium block">End Date</span>
                        <span className="text-slate-700">{fmtDate(detail.end_date)}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Linked Solicitation Opportunity */}
                {detail?.opportunity && (
                  <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs space-y-2">
                    <h3 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                      <Layers size={13} className="text-indigo-500" /> Originating Opportunity / Solicitation
                    </h3>
                    <div className="p-3 bg-indigo-50/50 rounded-lg border border-indigo-100 flex items-start justify-between gap-3">
                      <div>
                        {detail.opportunity.solicitation_number && (
                          <span className="text-[11px] font-mono font-semibold text-indigo-700 block mb-0.5">
                            {detail.opportunity.solicitation_number}
                          </span>
                        )}
                        <h4 className="text-[13px] font-bold text-slate-900 leading-snug">{detail.opportunity.name}</h4>
                        <span className="inline-block mt-1 text-[10px] px-1.5 py-0.5 rounded bg-white text-indigo-700 border border-indigo-200 uppercase font-semibold">
                          Status: {detail.opportunity.status}
                        </span>
                      </div>
                      <a
                        href={`/opportunities/${detail.opportunity.id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1.5 text-indigo-600 hover:text-indigo-800 bg-white rounded-md border border-indigo-200 shadow-xs shrink-0"
                        title="View opportunity details"
                      >
                        <ExternalLink size={14} />
                      </a>
                    </div>
                  </div>
                )}

                {/* Research Results, Publications & Patents */}
                {detail?.results && detail.results.length > 0 && (
                  <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs space-y-2">
                    <h3 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                      <BookmarkCheck size={13} className="text-emerald-500" /> Innovation Results & Outputs ({detail.results.length})
                    </h3>
                    <div className="space-y-2">
                      {detail.results.map((r: any) => (
                        <div key={r.id} className="p-3 bg-slate-50 rounded-lg border border-slate-200/80 space-y-1">
                          <div className="flex items-center gap-1.5">
                            <span className="px-1.5 py-0.5 rounded text-[9px] font-bold uppercase bg-emerald-100 text-emerald-800">
                              {r.result_type}
                            </span>
                            {r.date && <span className="text-[10px] text-slate-400">{fmtDate(r.date)}</span>}
                          </div>
                          <p className="text-[12px] font-semibold text-slate-800">{r.title}</p>
                          {r.authors && <p className="text-[11px] text-slate-500 italic">{r.authors}</p>}
                          {r.doi && (
                            <a
                              href={`https://doi.org/${r.doi}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-[11px] text-indigo-600 hover:underline inline-flex items-center gap-0.5"
                            >
                              <ExternalLink size={10} /> DOI: {r.doi}
                            </a>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Other Awards by this Recipient */}
                {relatedAwards?.items && relatedAwards.items.length > 1 && (
                  <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs space-y-2">
                    <h3 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                      <Atom size={13} className="text-indigo-500" /> Related Awards to {award.name}
                    </h3>
                    <div className="divide-y divide-slate-100">
                      {relatedAwards.items
                        .filter((item: any) => item.id !== award.id)
                        .slice(0, 4)
                        .map((item: any) => (
                          <div
                            key={item.id}
                            className="py-2.5 flex items-center justify-between hover:bg-slate-50/80 px-2 rounded-lg cursor-pointer transition-colors"
                            onClick={() => onSelectRelatedAward?.(item.id)}
                          >
                            <div className="min-w-0 pr-2">
                              <p className="text-[12px] font-medium text-slate-800 truncate">
                                {item.project_title || item.recipient_name}
                              </p>
                              <div className="flex items-center gap-2 text-[10px] text-slate-500 mt-0.5">
                                <span className="font-semibold text-emerald-700">{fmt(item.award_amount)}</span>
                                <span>•</span>
                                <span>{item.agency}</span>
                                {item.year && (
                                  <>
                                    <span>•</span>
                                    <span>{item.year}</span>
                                  </>
                                )}
                              </div>
                            </div>
                            <ChevronRight size={14} className="text-slate-400 shrink-0" />
                          </div>
                        ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Drawer Footer */}
          <div className="p-4 border-t border-slate-200 bg-white flex items-center justify-between">
            <div className="text-[11px] text-slate-400 font-medium">
              Database ID: #{award.id}
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={onClose}
                className="px-3.5 py-1.5 text-[12px] font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
              >
                Close
              </button>
              {(detail?.source_url || award.website) && (
                <a
                  href={detail?.source_url || (award.website?.startsWith('http') ? award.website : `https://${award.website}`)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3.5 py-1.5 text-[12px] font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-xs transition-colors inline-flex items-center gap-1"
                >
                  <ExternalLink size={12} /> Official Source
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
