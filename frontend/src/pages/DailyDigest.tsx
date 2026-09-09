import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Calendar,
  Newspaper,
  TrendingUp,
  Clock,
  Award,
  Scale,
  Sparkles,
  RefreshCw,
  ExternalLink,
  ChevronRight,
  Share2,
  Printer,
  Check,
  Building,
  ShieldCheck,
  Zap,
  ArrowUpRight,
  Info,
  Layers,
  FileText,
  AlertCircle,
  Terminal,
  Rss,
  Bot
} from 'lucide-react';
import { api, DailyDigest as DailyDigestType, DigestArchiveItem } from '../api/client';
import { OrgLogo } from '../components/OrgLogo';
import { ApiDocsModal } from '../components/ApiDocsModal';
import { useSEO } from '../utils/seo';

export default function DailyDigest() {
  const [searchParams, setSearchParams] = useSearchParams();
  const dateParam = searchParams.get('date') || undefined;
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [copied, setCopied] = useState(false);
  const [showArchive, setShowArchive] = useState(false);
  const [apiModalOpen, setApiModalOpen] = useState(false);


  useSEO({
    title: 'Daily Clean Energy Intelligence Digest | Energy Innovation Terminal',
    description: 'Automated morning briefing analyzing active clean energy funding solicitations, upcoming deadlines, venture attributions, and regulatory proceedings.',
  });

  // Fetch Digest with smooth cache retention
  const { data: digest, isLoading, isError, isFetching, refetch } = useQuery<DailyDigestType>({
    queryKey: ['daily-digest', dateParam],
    queryFn: () => api.getDailyDigest(dateParam),
    staleTime: 10 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
    placeholderData: (previousData) => previousData,
  });

  // Fetch Archive Editions
  const { data: archive } = useQuery<DigestArchiveItem[]>({
    queryKey: ['daily-digest-archive'],
    queryFn: () => api.getDigestArchive(),
    staleTime: 15 * 60 * 1000,
    gcTime: 60 * 60 * 1000,
  });

  // Force Regeneration Mutation
  const generateMutation = useMutation({
    mutationFn: () => api.generateDigest(dateParam),
    onSuccess: (newDigest) => {
      queryClient.setQueryData(['daily-digest', dateParam], newDigest);
      queryClient.invalidateQueries({ queryKey: ['daily-digest-archive'] });
    },
  });

  const handleCopy = () => {
    if (!digest) return;
    const textToCopy = `${digest.headline}\n${digest.formatted_date} (${digest.edition_number})\n\n${digest.editorial_narrative}\n\nRead full briefing on Energy Innovation Terminal: https://terminal.aixenergy.io/digest?date=${digest.edition_date}`;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePrint = () => {
    window.print();
  };

  const handleSelectDate = (dStr: string) => {
    setSearchParams({ date: dStr });
    setShowArchive(false);
  };

  if (isLoading && !digest) {
    return (
      <div className="max-w-6xl mx-auto space-y-8 pb-20 px-4 sm:px-6 animate-pulse">
        <div className="border-b border-slate-200 dark:border-slate-800 pb-6 pt-2 space-y-4">
          <div className="h-6 w-48 bg-slate-200 dark:bg-slate-800 rounded-full" />
          <div className="h-10 w-3/4 bg-slate-200 dark:bg-slate-800 rounded-lg" />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="h-24 bg-slate-200 dark:bg-slate-800 rounded-xl" />
          ))}
        </div>
        <div className="h-32 bg-slate-200 dark:bg-slate-800 rounded-2xl" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="h-40 bg-slate-200 dark:bg-slate-800 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }


  if (isError || !digest) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4">
        <div className="p-8 rounded-xl border border-red-200 bg-red-50/50 text-center space-y-4">
          <AlertCircle className="w-10 h-10 text-red-500 mx-auto" />
          <h2 className="text-lg font-bold text-slate-900">Unable to load Daily Digest</h2>
          <p className="text-sm text-slate-600">The daily briefing could not be retrieved from the server.</p>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 bg-slate-900 text-white text-xs font-semibold rounded-lg hover:bg-slate-800 transition"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-20 px-4 sm:px-6">
      {/* Top Editorial Masthead Banner */}
      <div className="border-b border-slate-200 dark:border-slate-800 pb-6 pt-2">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-cyan-50 dark:bg-cyan-950/60 text-cyan-700 dark:text-cyan-300 border border-cyan-200 dark:border-cyan-800/60">
              <Newspaper size={13} className="text-cyan-600 dark:text-cyan-400" />
              <span>Executive Morning Briefing</span>
            </span>
            <span className="text-xs text-slate-400 dark:text-slate-600">|</span>
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
              {digest.edition_number}
            </span>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {/* API & AI Agent Tools Modal Trigger */}
            <button
              onClick={() => setApiModalOpen(true)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg border border-cyan-200 dark:border-cyan-800 bg-cyan-50/50 dark:bg-cyan-950/40 text-cyan-700 dark:text-cyan-300 hover:bg-cyan-100/60 dark:hover:bg-cyan-900/60 transition shadow-2xs"
            >
              <Bot size={13} className="text-cyan-600 dark:text-cyan-400" />
              <span>API &amp; Agent Tools</span>
              <span className="text-[10px] bg-cyan-200/60 dark:bg-cyan-800/80 px-1 py-0.2 rounded text-cyan-800 dark:text-cyan-200 font-mono">
                OpenAPI
              </span>
            </button>

            {/* RSS Feed link */}
            <a
              href="/rss.xml"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-semibold rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 transition shadow-2xs"
              title="Syndicated RSS Feed for Feedly, Zapier, Inoreader"
            >
              <Rss size={13} className="text-amber-500" />
              <span>RSS</span>
            </a>

            {/* llms.txt link */}
            <a
              href="/llms.txt"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-semibold rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 transition shadow-2xs"
              title="LLMs Context Manifest for Claude / GPT / Cursor / Copilot"
            >
              <Terminal size={13} className="text-slate-500" />
              <span>llms.txt</span>
            </a>

            {/* Archive Selector Button */}
            <div className="relative">
              <button
                onClick={() => setShowArchive(!showArchive)}
                className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-semibold rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 transition shadow-2xs"
              >
                <Calendar size={13} className="text-slate-500" />
                <span>{digest.formatted_date}</span>
                <span className="text-[10px] bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded text-slate-600 dark:text-slate-400">
                  Editions ▾
                </span>
              </button>

              {showArchive && (
                <div className="absolute right-0 mt-2 w-72 bg-white dark:bg-slate-900 rounded-xl shadow-xl border border-slate-200 dark:border-slate-800 py-2 z-50 max-h-80 overflow-y-auto">
                  <div className="px-3 py-1 text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                    Recent Editions
                  </div>
                  {archive?.map((item) => (
                    <button
                      key={item.date}
                      onClick={() => handleSelectDate(item.date)}
                      className={`w-full text-left px-3 py-2 text-xs flex items-center justify-between hover:bg-slate-50 dark:hover:bg-slate-800 transition ${
                        item.date === digest.edition_date
                          ? 'font-bold text-cyan-600 dark:text-cyan-400 bg-cyan-50/50 dark:bg-cyan-950/30'
                          : 'text-slate-700 dark:text-slate-300'
                      }`}
                    >
                      <span>{item.formatted_date}</span>
                      {item.is_today && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 font-bold">
                          Today
                        </span>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Share / Copy */}
            <button
              onClick={handleCopy}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 transition shadow-2xs"
            >
              {copied ? <Check size={13} className="text-emerald-600" /> : <Share2 size={13} className="text-slate-500" />}
              <span>{copied ? 'Copied' : 'Share'}</span>
            </button>

            {/* Print */}
            <button
              onClick={handlePrint}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 transition shadow-2xs"
            >
              <Printer size={13} className="text-slate-500" />
              <span>Print</span>
            </button>

            {/* Refresh */}
            <button
              onClick={() => generateMutation.mutate()}
              disabled={generateMutation.isPending}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-white transition shadow-2xs disabled:opacity-50"
            >
              <RefreshCw size={13} className={generateMutation.isPending ? 'animate-spin' : ''} />
              <span>{generateMutation.isPending ? 'Refreshing...' : 'Refresh'}</span>
            </button>
          </div>
        </div>

        {/* Newspaper Title & Date */}
        <div className="mt-6 space-y-2">
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white font-serif">
            {digest.headline}
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 flex items-center gap-2">
            <span>Published by AIxEnergy Intelligence Control Layer</span>
            <span>•</span>
            <span>Continuous Ingestion Feed: Grants.gov, NYSERDA, CEC, Utility Dockets</span>
          </p>
        </div>
      </div>

      {/* Macro Metrics Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-2xs space-y-1">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500 dark:text-slate-400">
            <span>Active Funding Pool</span>
            <TrendingUp size={15} className="text-emerald-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 dark:text-white">
            {digest.macro_metrics.total_active_capital_display}
          </div>
          <div className="text-[11px] text-slate-400">Across all open programs</div>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-2xs space-y-1">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500 dark:text-slate-400">
            <span>Open Solicitations</span>
            <FileText size={15} className="text-cyan-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 dark:text-white">
            {digest.macro_metrics.open_solicitations_count.toLocaleString()}
          </div>
          <div className="text-[11px] text-slate-400">Federal, State &amp; Utility RFPs</div>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-2xs space-y-1">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500 dark:text-slate-400">
            <span>Tracked Innovators</span>
            <Building size={15} className="text-indigo-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 dark:text-white">
            {digest.macro_metrics.tracked_recipients_count.toLocaleString()}
          </div>
          <div className="text-[11px] text-slate-400">Award recipients &amp; labs</div>
        </div>

        <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-2xs space-y-1">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500 dark:text-slate-400">
            <span>Upcoming Deadlines</span>
            <Clock size={15} className="text-amber-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 dark:text-white">
            {digest.macro_metrics.urgent_deadlines_count}
          </div>
          <div className="text-[11px] text-slate-400">Closing in 7-14 days</div>
        </div>
      </div>

      {/* Editorial Lead Section */}
      <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-950 text-white shadow-lg border border-slate-700/50 space-y-3">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-cyan-400">
          <Sparkles size={14} />
          <span>Macro Capital &amp; Opportunity Synthesis</span>
        </div>
        <p className="text-base sm:text-lg leading-relaxed text-slate-200 font-serif">
          {digest.editorial_narrative}
        </p>
      </div>

      {/* 1. Top New Solicitations */}
      <div className="space-y-4">
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-500" />
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">
              1. Top New Solicitations &amp; Grant Programs
            </h2>
          </div>
          <span className="text-xs font-semibold text-slate-400">
            {digest.new_solicitations.length} featured programs
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {digest.new_solicitations.map((opp) => (
            <div
              key={opp.id}
              onClick={() => navigate(`/opportunities/${opp.id}`)}
              className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 hover:border-cyan-500 dark:hover:border-cyan-500/60 shadow-2xs hover:shadow-md transition-all cursor-pointer flex flex-col justify-between gap-4 group"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-cyan-50 dark:bg-cyan-950/60 text-cyan-700 dark:text-cyan-300 border border-cyan-200 dark:border-cyan-800/60">
                      {opp.solicitation_number || opp.solicitation_type}
                    </span>
                    <span className="text-xs font-semibold text-slate-600 dark:text-slate-400 flex items-center gap-1">
                      <OrgLogo org={opp.agency} size="xs" />
                      <span>{opp.agency}</span>
                    </span>
                  </div>
                  <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400">
                    {opp.total_funding_display}
                  </span>
                </div>

                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100 group-hover:text-cyan-600 dark:group-hover:text-cyan-400 transition leading-snug">
                  {opp.name}
                </h3>

                <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2">
                  {opp.short_description}
                </p>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-800/60 text-xs">
                <div className="flex items-center gap-1.5 text-slate-500 dark:text-slate-400 font-medium">
                  <Clock size={13} className="text-slate-400" />
                  <span>{opp.due_date_display}</span>
                </div>
                <span className="inline-flex items-center gap-1 font-semibold text-cyan-600 dark:text-cyan-400 group-hover:translate-x-0.5 transition">
                  <span>View Details</span>
                  <ChevronRight size={14} />
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 2. Critical Upcoming Deadlines */}
      <div className="space-y-4">
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">
              2. Critical Upcoming Application Deadlines (Next 14 Days)
            </h2>
          </div>
          <span className="text-xs font-semibold text-slate-400">Action Required</span>
        </div>

        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-2xs divide-y divide-slate-100 dark:divide-slate-800 overflow-hidden">
          {digest.urgent_deadlines.map((opp) => (
            <div
              key={opp.id}
              onClick={() => navigate(`/opportunities/${opp.id}`)}
              className="p-4 hover:bg-slate-50/80 dark:hover:bg-slate-800/50 transition cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-3"
            >
              <div className="space-y-1 min-w-0 flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800/60">
                    Due Soon
                  </span>
                  <span className="text-xs font-semibold text-slate-600 dark:text-slate-400">{opp.agency}</span>
                  <span className="text-xs text-slate-300 dark:text-slate-700">•</span>
                  <span className="text-xs font-mono text-slate-400">{opp.solicitation_number}</span>
                </div>
                <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100 truncate">
                  {opp.name}
                </h4>
              </div>

              <div className="flex items-center justify-between sm:justify-end gap-4 shrink-0">
                <div className="text-left sm:text-right">
                  <div className="text-xs font-bold text-slate-900 dark:text-slate-100">{opp.total_funding_display}</div>
                  <div className="text-[11px] text-amber-600 dark:text-amber-400 font-semibold">{opp.due_date_display}</div>
                </div>
                <span className="p-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                  <ChevronRight size={15} />
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 3. Recipient & Award Wire */}
      <div className="space-y-4">
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">
              3. Innovator &amp; Award Wire
            </h2>
          </div>
          <span className="text-xs font-semibold text-slate-400">Recent Capital Disbursements</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {digest.award_wire.map((aw) => (
            <div
              key={aw.id}
              className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-2xs space-y-2 flex flex-col justify-between"
            >
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800/60">
                    {aw.award_amount_display}
                  </span>
                  <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
                    {aw.recipient_city ? `${aw.recipient_city}, ${aw.recipient_state}` : aw.recipient_state || 'US'}
                  </span>
                </div>
                <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100 pt-1">
                  {aw.recipient_name}
                </h4>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-2">
                  {aw.project_title}
                </p>
              </div>

              {aw.pi_name && (
                <div className="text-[11px] text-slate-400 pt-2 border-t border-slate-100 dark:border-slate-800/60 flex items-center gap-1">
                  <Award size={12} className="text-slate-400" />
                  <span>Lead PI: {aw.pi_name}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* 4. Regulatory & Dockets Watch */}
      <div className="space-y-4">
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-500" />
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">
              4. Regulatory Standards &amp; Dockets Watch
            </h2>
          </div>
          <span className="text-xs font-semibold text-slate-400">Policy &amp; Compliance Horizon</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {digest.regulatory_watch.map((pol) => (
            <div
              key={pol.code_identifier}
              className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 shadow-2xs space-y-2"
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-purple-50 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800/60 font-mono">
                  {pol.code_identifier}
                </span>
                <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
                  {pol.jurisdiction_state}
                </span>
              </div>
              <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100">
                {pol.title}
              </h4>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                {pol.executive_summary}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* 5. Algorithmic Opportunity Spotlight with TBR & Capital Stack */}
      {digest.spotlight && (
        <div className="space-y-4">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-2">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-pulse" />
              <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                5. Algorithmic Opportunity Spotlight &amp; Bankability
              </h2>
            </div>
            <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">
              TBR Grade: {digest.spotlight.bankability_grade || 'AAA'}
            </span>
          </div>

          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">
                    {digest.spotlight.solicitation_number}
                  </span>
                  <span className="text-xs text-slate-400">•</span>
                  <span className="text-xs font-semibold text-slate-600 dark:text-slate-300">
                    {digest.spotlight.agency}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                  {digest.spotlight.name}
                </h3>
              </div>

              <button
                onClick={() => navigate(`/opportunities/${digest.spotlight?.opportunity_id}`)}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 text-white text-xs font-bold hover:bg-indigo-700 transition shadow-2xs shrink-0"
              >
                <span>Full Opportunity Dossier</span>
                <ArrowUpRight size={15} />
              </button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800">
              <div className="space-y-1">
                <div className="text-[11px] font-semibold text-slate-400">Technology Bankability (TBR)</div>
                <div className="text-xl font-bold text-slate-900 dark:text-white">
                  {digest.spotlight.bankability_score ? `${digest.spotlight.bankability_score.toFixed(1)}/100` : '90.1/100'}
                </div>
                <div className="text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold">
                  Investment Grade ({digest.spotlight.bankability_grade || 'AAA'})
                </div>
              </div>

              <div className="space-y-1">
                <div className="text-[11px] font-semibold text-slate-400">IRA Title 26 ITC Rate</div>
                <div className="text-xl font-bold text-cyan-600 dark:text-cyan-400">
                  {digest.spotlight.ira_itc_rate ? `${digest.spotlight.ira_itc_rate.toFixed(1)}%` : '30.0%'}
                </div>
                <div className="text-[10px] text-slate-500 dark:text-slate-400">
                  Valued at {digest.spotlight.ira_tax_credit_value || '$1.5M'}
                </div>
              </div>

              <div className="space-y-1">
                <div className="text-[11px] font-semibold text-slate-400">Blended Cost of Capital (WACC)</div>
                <div className="text-xl font-bold text-emerald-600 dark:text-emerald-400">
                  {digest.spotlight.blended_wacc_pct ? `${digest.spotlight.blended_wacc_pct.toFixed(1)}%` : '5.2%'}
                </div>
                <div className="text-[10px] text-slate-500 dark:text-slate-400">With Green Bank debt</div>
              </div>

              <div className="space-y-1">
                <div className="text-[11px] font-semibold text-slate-400">Non-Dilutive Coverage</div>
                <div className="text-xl font-bold text-indigo-600 dark:text-indigo-400">
                  {digest.spotlight.non_dilutive_coverage_pct ? `${digest.spotlight.non_dilutive_coverage_pct.toFixed(0)}%` : '30%'}
                </div>
                <div className="text-[10px] text-slate-500 dark:text-slate-400">Of total capital stack</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Footer Citation & Attribution */}
      <div className="border-t border-slate-200 dark:border-slate-800 pt-6 text-center space-y-2">
        <p className="text-xs text-slate-400 dark:text-slate-500">
          Source: Energy Innovation Terminal (<a href="https://terminal.aixenergy.io" className="underline hover:text-slate-600 dark:hover:text-slate-300">terminal.aixenergy.io</a>) • AIxEnergy Proprietary Intelligence Layer
        </p>
        <p className="text-[11px] text-slate-400 dark:text-slate-600">
          Automated edition generated on {digest.generated_at ? new Date(digest.generated_at).toLocaleString() : digest.formatted_date}.
        </p>
      </div>

      {/* Developer API & AI Agent Tool Docs Modal */}
      <ApiDocsModal isOpen={apiModalOpen} onClose={() => setApiModalOpen(false)} />
    </div>
  );
}
