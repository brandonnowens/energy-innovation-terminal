import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api, LinkageTraceResponse } from '../api/client';
import {
  Building2,
  Landmark,
  FileSearch,
  DollarSign,
  Users,
  Lightbulb,
  Cpu,
  Flame,
  Factory,
  TrendingUp,
  ChevronRight,
  Sparkles,
  ExternalLink,
  ShieldCheck,
  Loader2,
} from 'lucide-react';
import clsx from 'clsx';
import { OrgLogo } from './OrgLogo';

interface ProvenanceRibbonProps {
  entityType?: 'patent' | 'recipient' | 'award' | 'opportunity' | 'program' | 'organization';
  entityId?: string | number;
  traceData?: LinkageTraceResponse;
  compact?: boolean;
  className?: string;
  onSelectNode?: (type: string, id: string | number) => void;
}

export function ProvenanceRibbon({
  entityType,
  entityId,
  traceData: initialTraceData,
  compact = false,
  className = '',
  onSelectNode,
}: ProvenanceRibbonProps) {
  const { data: fetchedData, isLoading } = useQuery({
    queryKey: ['linkage-trace', entityType, entityId],
    queryFn: () => api.getLinkageTrace(entityType!, entityId!),
    enabled: !initialTraceData && !!entityType && !!entityId,
    staleTime: 5 * 60 * 1000,
  });

  const trace = initialTraceData || fetchedData;

  if (isLoading) {
    return (
      <div className={clsx('flex items-center gap-2 px-3 py-2 bg-slate-50 border border-slate-200/80 rounded-xl text-xs text-slate-500 animate-pulse', className)}>
        <Loader2 size={13} className="animate-spin text-indigo-600" />
        <span>Tracing 9-dimensional innovation lineage...</span>
      </div>
    );
  }

  if (!trace || !trace.provenance_chain) {
    return null;
  }

  const { provenance_chain: chain, taxonomies } = trace;
  const org = chain.organization;
  const prog = chain.program;
  const opp = chain.opportunity;
  const awd = chain.award;
  const rec = chain.recipient;
  const patents = chain.patents || [];
  const investments = chain.investments || [];

  return (
    <div className={clsx('bg-white border border-slate-200/90 rounded-2xl shadow-2xs p-3.5 space-y-3 overflow-hidden', className)}>
      {/* Header Banner with 9D Indicator */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-2">
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1 text-[11px] font-bold text-indigo-700 bg-indigo-50 border border-indigo-200 px-2 py-0.5 rounded-full">
            <Sparkles size={11} className="text-indigo-600" />
            <span>9-D Innovation Lineage HUD</span>
          </span>
          <span className="text-[11px] text-slate-400 font-medium">
            Policy & Funding ➔ Grant Award ➔ Bayh-Dole IP & Commercial Growth
          </span>
        </div>
        {rec && rec.total_grants_usd ? (
          <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-md">
            ${(rec.total_grants_usd / 1e6).toFixed(1)}M Total Grants
          </span>
        ) : null}
      </div>

      {/* Main Horizontal Provenance Pipeline Flow */}
      <div className="flex items-center gap-1.5 overflow-x-auto py-1 scrollbar-thin">
        {/* 1. Funder Organization */}
        {org && (
          <div
            onClick={() => onSelectNode?.('organization', org.id)}
            className="group flex-shrink-0 flex items-center gap-2 px-2.5 py-1.5 bg-indigo-50/70 hover:bg-indigo-100/80 border border-indigo-200/80 rounded-xl cursor-pointer transition shadow-2xs"
            title={`Funder: ${org.name} (${org.org_type || 'Agency'})`}
          >
            <OrgLogo org={org.name} domain={org.website} size="xs" />
            <div className="text-left leading-tight">
              <div className="text-[9px] font-bold uppercase tracking-wider text-indigo-600">1. Funder Org</div>
              <div className="text-[11px] font-bold text-slate-800 truncate max-w-[120px]">{org.name}</div>
            </div>
          </div>
        )}

        {org && (prog || opp) && <ChevronRight size={14} className="text-slate-300 flex-shrink-0" />}

        {/* 2. Program Portfolio */}
        {prog && (
          <div
            onClick={() => onSelectNode?.('program', prog.id)}
            className="group flex-shrink-0 flex items-center gap-2 px-2.5 py-1.5 bg-teal-50/70 hover:bg-teal-100/80 border border-teal-200/80 rounded-xl cursor-pointer transition shadow-2xs"
            title={`Program: ${prog.name}`}
          >
            <div className="w-5 h-5 rounded-md bg-teal-600 text-white flex items-center justify-center flex-shrink-0 shadow-2xs">
              <Landmark size={11} />
            </div>
            <div className="text-left leading-tight">
              <div className="text-[9px] font-bold uppercase tracking-wider text-teal-600">2. Program</div>
              <div className="text-[11px] font-bold text-slate-800 truncate max-w-[130px]">{prog.name}</div>
            </div>
          </div>
        )}

        {prog && opp && <ChevronRight size={14} className="text-slate-300 flex-shrink-0" />}

        {/* 3. Opportunity Solicitation */}
        {opp && (
          <div
            onClick={() => onSelectNode?.('opportunity', opp.id)}
            className="group flex-shrink-0 flex items-center gap-2 px-2.5 py-1.5 bg-sky-50/70 hover:bg-sky-100/80 border border-sky-200/80 rounded-xl cursor-pointer transition shadow-2xs"
            title={`Opportunity: ${opp.solicitation_number || ''} ${opp.name}`}
          >
            {opp.agency ? (
              <OrgLogo org={opp.agency} size="xs" />
            ) : (
              <div className="w-5 h-5 rounded-md bg-sky-600 text-white flex items-center justify-center flex-shrink-0 shadow-2xs">
                <FileSearch size={11} />
              </div>
            )}
            <div className="text-left leading-tight">
              <div className="text-[9px] font-bold uppercase tracking-wider text-sky-600">3. Opportunity</div>
              <div className="text-[11px] font-bold text-slate-800 truncate max-w-[130px]">
                {opp.solicitation_number || opp.name}
              </div>
            </div>
          </div>
        )}

        {opp && (awd || rec) && <ChevronRight size={14} className="text-slate-300 flex-shrink-0" />}

        {/* 4. Grant Award */}
        {awd && (
          <div
            onClick={() => onSelectNode?.('award', awd.id)}
            className="group flex-shrink-0 flex items-center gap-2 px-2.5 py-1.5 bg-purple-50/70 hover:bg-purple-100/80 border border-purple-200/80 rounded-xl cursor-pointer transition shadow-2xs"
            title={`Award: $${((awd.amount_usd || 0) / 1000).toFixed(0)}K - ${awd.project_title || ''}`}
          >
            <div className="w-5 h-5 rounded-md bg-purple-600 text-white flex items-center justify-center flex-shrink-0 shadow-2xs">
              <DollarSign size={11} />
            </div>
            <div className="text-left leading-tight">
              <div className="text-[9px] font-bold uppercase tracking-wider text-purple-600">4. Award Grant</div>
              <div className="text-[11px] font-bold text-slate-800">
                {awd.amount_usd ? `$${(awd.amount_usd / 1e3).toFixed(0)}K` : 'Grant Award'}
              </div>
            </div>
          </div>
        )}

        {(awd || opp) && rec && <ChevronRight size={14} className="text-slate-300 flex-shrink-0" />}

        {/* 5. Recipient / Startup */}
        {rec && (
          <div
            onClick={() => onSelectNode?.('recipient', rec.id)}
            className="group flex-shrink-0 flex items-center gap-2 px-2.5 py-1.5 bg-emerald-50/70 hover:bg-emerald-100/80 border border-emerald-200/80 rounded-xl cursor-pointer transition shadow-2xs"
            title={`Recipient: ${rec.name} (${rec.city || ''}, ${rec.state || ''})`}
          >
            <OrgLogo org={rec.name} domain={rec.website} size="xs" />
            <div className="text-left leading-tight">
              <div className="text-[9px] font-bold uppercase tracking-wider text-emerald-600">5. Recipient</div>
              <div className="text-[11px] font-bold text-slate-800 truncate max-w-[130px]">{rec.name}</div>
            </div>
          </div>
        )}

        {rec && (patents.length > 0 || investments.length > 0) && (
          <ChevronRight size={14} className="text-slate-300 flex-shrink-0" />
        )}

        {/* 6. Bayh-Dole Patents */}
        {patents.length > 0 && (
          <div
            onClick={() => onSelectNode?.('patent', patents[0].id)}
            className="group flex-shrink-0 flex items-center gap-2 px-2.5 py-1.5 bg-amber-50/70 hover:bg-amber-100/80 border border-amber-200/80 rounded-xl cursor-pointer transition"
            title={`Patent: ${patents[0].patent_number} - ${patents[0].title}`}
          >
            <div className="w-6 h-6 rounded-lg bg-amber-600 text-white flex items-center justify-center flex-shrink-0">
              <Lightbulb size={12} />
            </div>
            <div className="text-left leading-tight">
              <div className="text-[9px] font-bold uppercase tracking-wider text-amber-600">6. Bayh-Dole IP</div>
              <div className="text-[11px] font-bold text-slate-800">
                {patents[0].patent_number} {patents.length > 1 ? `(+${patents.length - 1})` : ''}
              </div>
            </div>
          </div>
        )}

        {/* 7. Follow-on VC Rounds */}
        {investments.length > 0 && (
          <div className="group flex-shrink-0 flex items-center gap-2 px-2.5 py-1.5 bg-rose-50/70 hover:bg-rose-100/80 border border-rose-200/80 rounded-xl transition">
            <div className="w-6 h-6 rounded-lg bg-rose-600 text-white flex items-center justify-center flex-shrink-0">
              <TrendingUp size={12} />
            </div>
            <div className="text-left leading-tight">
              <div className="text-[9px] font-bold uppercase tracking-wider text-rose-600">7. Follow-On VC</div>
              <div className="text-[11px] font-bold text-slate-800">
                {investments[0].round_type} {investments[0].amount_usd ? `($${(investments[0].amount_usd / 1e6).toFixed(1)}M)` : ''}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Taxonomy Strip (Technology, Fuel, Sector, Stage) */}
      {!compact && (
        <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-100 text-xs">
          <span className="text-[10px] font-bold uppercase text-slate-400 tracking-wider">Classification:</span>

          {taxonomies?.technology && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-pink-50 text-pink-700 border border-pink-200">
              <Cpu size={11} className="text-pink-600" />
              <span>{taxonomies.technology}</span>
            </span>
          )}

          {taxonomies?.fuel && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-orange-50 text-orange-700 border border-orange-200">
              <Flame size={11} className="text-orange-600" />
              <span>{taxonomies.fuel}</span>
            </span>
          )}

          {taxonomies?.sector && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-violet-50 text-violet-700 border border-violet-200">
              <Factory size={11} className="text-violet-600" />
              <span>{taxonomies.sector}</span>
            </span>
          )}

          {taxonomies?.stage && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <TrendingUp size={11} className="text-emerald-600" />
              <span>{taxonomies.stage}</span>
            </span>
          )}
        </div>
      )}
    </div>
  );
}
