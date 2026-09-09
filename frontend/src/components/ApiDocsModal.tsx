import React, { useState } from 'react';
import {
  X,
  Code,
  Terminal,
  Cpu,
  ExternalLink,
  Copy,
  Check,
  Zap,
  Layers,
  ShieldCheck,
  FileCode,
  Rss,
  Share2,
  Database
} from 'lucide-react';
import clsx from 'clsx';
import { API_BASE_URL } from '../api/client';

interface ApiDocsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ApiDocsModal({ isOpen, onClose }: ApiDocsModalProps) {
  const [activeTab, setActiveTab] = useState<'endpoints' | 'agents' | 'code' | 'feeds'>('endpoints');
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const API_HOST = API_BASE_URL || 'https://energy-innovation-api.onrender.com';

  const AGENT_TOOLS = [
    { name: 'match_opportunities', desc: 'Deterministic 7-dimension eligibility & scoring match against 5,740+ solicitations.' },
    { name: 'solve_capital_stack', desc: 'Title 26 IRA Section 48/45X tax credits, Green Bank debt, and blended WACC solver.' },
    { name: 'calculate_technology_bankability', desc: '4-Pillar Technology Bankability Rating (TBR), commercial gap audit, and investment grade.' },
    { name: 'estimate_win_rate_probability', desc: 'Empirical selection rate model, precedent scale factors, and agency benchmarks.' },
    { name: 'recommend_consortia_partners', desc: 'Optimal teaming partner composition with verified PI citations and track records.' },
    { name: 'forecast_unreleased_opportunities', desc: '18-month unreleased solicitation radar and unallocated capital forecasts.' },
    { name: 'map_say_yes_decision_makers', desc: 'Institutional pain point matching and agency organizational hierarchy.' },
    { name: 'reverse_engineer_reviewer_rubric', desc: 'Reverse-engineers hidden evaluation rubrics and flags scoring landmines.' },
    { name: 'query_recipient_track_record', desc: 'Track record dossiers for 13,940+ clean tech innovators across 54,300+ awards.' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-xs animate-in fade-in duration-150">
      <div
        className="relative w-full max-w-4xl max-h-[90vh] bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 flex flex-col overflow-hidden text-slate-800 dark:text-slate-100"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-6 border-b border-slate-200 dark:border-slate-800 flex items-start justify-between gap-4 bg-slate-50/50 dark:bg-slate-900/50">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-cyan-50 dark:bg-cyan-950/60 text-cyan-700 dark:text-cyan-300 border border-cyan-200 dark:border-cyan-800">
                <Terminal size={12} />
                <span>Developer Platform</span>
              </span>
              <span className="text-xs font-semibold text-slate-400 dark:text-slate-500">v1.0 Canonical API</span>
            </div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
              Energy Innovation Terminal API &amp; Automation Endpoints
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 max-w-2xl">
              Programmatic access to 54,300+ historical awards, active solicitations, IRA financial engineering, and 9 OpenAPI endpoints for programmatic analysis.
            </p>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition cursor-pointer"
          >
            <X size={18} />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 px-6 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-x-auto text-xs font-semibold">
          {[
            { id: 'endpoints', label: 'Interactive Docs & Endpoints', icon: Code },
            { id: 'agents', label: '9 Automation Endpoints', icon: Cpu },
            { id: 'code', label: 'Code Snippets (Python / cURL)', icon: FileCode },
            { id: 'feeds', label: 'Machine-Readable Feeds & Indexes', icon: Rss },
          ].map((t) => {
            const Icon = t.icon;
            return (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id as any)}
                className={clsx(
                  'flex items-center gap-2 py-3 px-3 border-b-2 transition whitespace-nowrap cursor-pointer',
                  activeTab === t.id
                    ? 'border-cyan-500 text-cyan-600 dark:text-cyan-400'
                    : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
                )}
              >
                <Icon size={14} />
                <span>{t.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-xs leading-relaxed">
          {/* 1. Endpoints & Swagger */}
          {activeTab === 'endpoints' && (
            <div className="space-y-6">
              <div className="p-4 rounded-xl bg-gradient-to-r from-cyan-500/10 to-indigo-500/10 border border-cyan-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="space-y-0.5">
                  <div className="font-bold text-slate-900 dark:text-white text-sm">Interactive Swagger UI</div>
                  <div className="text-slate-500 dark:text-slate-400">Test live endpoints, inspect request schemas, and explore all parameters in real time.</div>
                </div>
                <a
                  href={`${API_HOST}/docs`}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs shadow-sm shrink-0 transition"
                >
                  <span>Open Swagger UI</span>
                  <ExternalLink size={13} />
                </a>
              </div>

              <div className="space-y-3">
                <h3 className="font-bold text-slate-900 dark:text-white uppercase tracking-wider text-[11px]">
                  Core Versioned Endpoints (v1)
                </h3>

                <div className="space-y-2">
                  {[
                    { method: 'GET', path: '/api/v1/digest/latest', desc: 'Today\'s synthesized energy innovation morning briefing & macro capital flow.' },
                    { method: 'POST', path: '/api/v1/intelligence/capital-stack', desc: 'Title 26 IRA Section 48/45X tax credits, Green Bank debt, and WACC solver.' },
                    { method: 'POST', path: '/api/v1/intelligence/bankability', desc: '4-Pillar Technology Bankability Rating (TBR) & commercial gap score.' },
                    { method: 'GET', path: '/api/v1/intelligence/forecasts', desc: '18-month early-warning predictive radar of unreleased RFPs.' },
                    { method: 'GET', path: '/api/v1/agents/tools', desc: 'OpenAPI-compliant tool declarations for OpenAI, Anthropic & Gemini.' },
                    { method: 'GET', path: '/api/v1/seo/status', desc: 'Live SEO, sitemaps, and GEO crawler status monitor.' },
                  ].map((ep) => (
                    <div
                      key={ep.path}
                      className="p-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-800/40 flex flex-col sm:flex-row sm:items-center justify-between gap-2"
                    >
                      <div className="flex items-center gap-2 font-mono">
                        <span className={clsx('px-1.5 py-0.5 rounded text-[10px] font-bold', ep.method === 'GET' ? 'bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300' : 'bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300')}>
                          {ep.method}
                        </span>
                        <span className="font-semibold text-slate-900 dark:text-white select-all">{ep.path}</span>
                      </div>
                      <span className="text-slate-500 dark:text-slate-400 sm:text-right">{ep.desc}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 2. Automation Endpoints */}
          {activeTab === 'agents' && (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/60 flex items-start gap-3">
                <Cpu className="w-5 h-5 text-indigo-600 dark:text-indigo-400 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <div className="font-bold text-slate-900 dark:text-white">Deterministic Automation &amp; Analysis Tool Manifest</div>
                  <div className="text-slate-600 dark:text-slate-300">
                    Use these 9 grounded tool functions directly inside automated scripts, analytical pipelines, LangChain, or custom integrations.
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {AGENT_TOOLS.map((t) => (
                  <div
                    key={t.name}
                    className="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-1.5 shadow-2xs"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-cyan-600 dark:text-cyan-400 text-[11px]">
                        {t.name}()
                      </span>
                      <button
                        onClick={() => handleCopy(t.name, t.name)}
                        className="p-1 rounded text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
                        title="Copy tool name"
                      >
                        {copiedKey === t.name ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
                      </button>
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-snug">
                      {t.desc}
                    </p>
                  </div>
                ))}
              </div>

              <div className="pt-2 flex justify-end">
                <a
                  href={`${API_HOST}/api/v1/agents/tools`}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 text-cyan-600 dark:text-cyan-400 font-bold hover:underline"
                >
                  <span>Download Raw OpenAPI Tool Manifest (JSON)</span>
                  <ExternalLink size={12} />
                </a>
              </div>
            </div>
          )}

          {/* 3. Code Snippets */}
          {activeTab === 'code' && (
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-900 dark:text-white">Python Request</span>
                  <button
                    onClick={() => handleCopy(`import requests\n\nresp = requests.get("${API_HOST}/api/v1/digest/latest")\ndigest = resp.json()\nprint(digest["headline"], digest["macro_metrics"])`, 'py1')}
                    className="inline-flex items-center gap-1 text-[11px] text-slate-500 hover:text-slate-900 dark:hover:text-white"
                  >
                    {copiedKey === 'py1' ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
                    <span>{copiedKey === 'py1' ? 'Copied' : 'Copy Python'}</span>
                  </button>
                </div>
                <pre className="p-3 rounded-xl bg-slate-950 text-slate-200 font-mono text-[11px] overflow-x-auto">
{`import requests

# Fetch today's Daily Energy Innovation Intelligence Briefing
resp = requests.get("${API_HOST}/api/v1/digest/latest")
digest = resp.json()
print(f"Headline: {digest['headline']}")
print(f"Active Capital: {digest['macro_metrics']['total_active_capital_display']}")`}
                </pre>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-900 dark:text-white">cURL Command</span>
                  <button
                    onClick={() => handleCopy(`curl -X GET "${API_HOST}/api/v1/digest/latest" -H "Accept: application/json"`, 'curl1')}
                    className="inline-flex items-center gap-1 text-[11px] text-slate-500 hover:text-slate-900 dark:hover:text-white"
                  >
                    {copiedKey === 'curl1' ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
                    <span>{copiedKey === 'curl1' ? 'Copied' : 'Copy cURL'}</span>
                  </button>
                </div>
                <pre className="p-3 rounded-xl bg-slate-950 text-slate-200 font-mono text-[11px] overflow-x-auto">
{`curl -X GET "${API_HOST}/api/v1/digest/latest" \\
  -H "Accept: application/json"`}
                </pre>
              </div>
            </div>
          )}

          {/* 4. GEO & Feeds */}
          {activeTab === 'feeds' && (
            <div className="space-y-4">
              <p className="text-slate-600 dark:text-slate-300">
                The terminal natively provides standardized machine-readable data feeds and RSS 2.0 feeds for automated aggregation by external research tools, analytical systems, and syndication platforms:
              </p>

              <div className="space-y-3">
                {[
                  {
                    title: 'LLMs.txt (Machine-Readable Knowledge Base)',
                    url: `${API_HOST}/llms.txt`,
                    desc: 'Structured markdown knowledge summary formatted for external research tools and search indexers.',
                  },
                  {
                    title: 'RSS 2.0 Grants Syndication Feed',
                    url: `${API_HOST}/feed/rss/opportunities.xml`,
                    desc: 'Real-time syndication feed for newly posted grants and RFPs across DOE, NYSERDA, and CEC.',
                  },
                  {
                    title: 'Master XML Sitemap Index',
                    url: `${API_HOST}/sitemap.xml`,
                    desc: 'Segmented XML sitemaps covering all 19,800+ dynamic opportunity, recipient, and tech hub pages.',
                  },
                ].map((feed) => (
                  <div
                    key={feed.url}
                    className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                  >
                    <div className="space-y-1">
                      <div className="font-bold text-slate-900 dark:text-white">{feed.title}</div>
                      <div className="text-slate-500 dark:text-slate-400">{feed.desc}</div>
                      <div className="font-mono text-[10.5px] text-cyan-600 dark:text-cyan-400 select-all pt-0.5">{feed.url}</div>
                    </div>
                    <a
                      href={feed.url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition shrink-0"
                    >
                      <span>View Feed</span>
                      <ExternalLink size={12} />
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-900/80 flex items-center justify-between text-slate-500">
          <div className="text-[11px]">
            Canonical Intelligence Layer Hosted on Render • PostgreSQL Cluster on Supabase
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 text-xs font-semibold hover:bg-slate-800 dark:hover:bg-white transition cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
