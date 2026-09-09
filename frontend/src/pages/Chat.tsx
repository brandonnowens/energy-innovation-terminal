import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowUp, Plus, Copy, Check, Key, ShieldCheck,
  ChevronDown, ChevronUp, ExternalLink, RefreshCw, FileText,
  Building2, TrendingUp, BookOpen, Zap, User, Award, CheckCircle2,
  Landmark, Rocket, Video, MessageSquare, Compass, Sliders
} from 'lucide-react';
import {
  api,
  ChatMessageItem,
  ChatCitationsMetadata,
  streamChatCompletion
} from '../api/client';

import { MermaidDiagram } from '../components/MermaidDiagram';
import TavusVideoConversation from '../components/TavusVideoConversation';

export type UserRole = 'institutional_leader' | 'startup_entrepreneur' | 'developer' | 'investor' | 'researcher' | 'utility' | 'policy' | 'grant_writer';
export type AdvisoryMode = 'landing' | 'chat' | 'video';

export interface RoleOption {
  id: UserRole;
  title: string;
  badge: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  description: string;
  starterPrompts: Array<{ title: string; prompt: string }>;
  spokenStarters: string[];
}

export const ROLES: RoleOption[] = [
  {
    id: 'institutional_leader',
    title: 'Institutional Leader & Provost',
    badge: 'Institutional Leader',
    icon: Landmark,
    description: '5-year research agendas, center grants, issuing PONs, faculty clusters & F&A recovery',
    spokenStarters: [
      'How should we structure our 5-year energy innovation research roadmap and internal PONs?',
      'What strategies anchor a $50M regional energy innovation hub consortium?',
      'Which faculty clusters show the highest verified grant momentum in hydrogen and storage?',
      'How do we structure master industry agreements while protecting Bayh-Dole IP?'
    ],
    starterPrompts: [
      {
        title: '5-Year Research Strategy & PONs',
        prompt: 'Craft a 5-year research strategy for our institution that includes creating internal research programs and issuing competitive Program Opportunity Notices (PONs).'
      },
      {
        title: '$50M+ Regional Hub Consortium',
        prompt: 'How can our institution anchor a $50M+ regional energy innovation hub consortium across DOE OCED, state agencies, and utility off-takers?'
      },
      {
        title: 'High-Impact Faculty Clusters',
        prompt: 'Identify top Principal Investigators and faculty clusters with verified historical award momentum in energy storage and hydrogen.'
      },
      {
        title: 'Bayh-Dole IP & Matching Funds',
        prompt: 'How can our university structure master corporate research agreements paired with state cost-share without encumbering Bayh-Dole patent rights?'
      }
    ]
  },
  {
    id: 'startup_entrepreneur',
    title: 'Start-Up / Deep Tech Founder',
    badge: 'Start-Up',
    icon: Rocket,
    description: 'Non-dilutive runway extension, SBIR Phase I/II stacking, cap table preservation & customer LOIs',
    spokenStarters: [
      'How can we stack SBIR Phase I and II awards with state matching funds to extend our runway?',
      'What active solicitations exist for TRL 3 to 5 hardware with zero to 20% cost-share?',
      'How do public grant awards help drive our Series A valuation step-up?',
      'What strategies secure pilot customer letters of intent to maximize grant win rates?'
    ],
    starterPrompts: [
      {
        title: 'SBIR / Non-Dilutive Runway Stack',
        prompt: 'How can our pre-seed deep tech startup stack SBIR/STTR Phase I/II grants with state matching funds to extend runway without equity dilution?'
      },
      {
        title: 'TRL 3-5 Seed Grant Programs',
        prompt: 'What active solicitations and incubator programs exist for TRL 3-5 clean tech hardware startups with 0-20% cost-share?'
      },
      {
        title: 'Series A Valuation Step-Up',
        prompt: 'How can we leverage public grant track records to command a higher valuation step-up in our upcoming Series A round?'
      },
      {
        title: 'Pilot Customer Off-Take LOIs',
        prompt: 'What are the best strategies to secure utility/industrial pilot customer letters of intent (LOI) to maximize federal grant win rates?'
      }
    ]
  },
  {
    id: 'developer',
    title: 'Project Developer / Sponsor',
    badge: 'Developer',
    icon: Building2,
    description: 'Capital stacking, FEED studies, FOAK demo bankability & cost-share strategy',
    spokenStarters: [
      'How can we stack state energy innovation grants with federal DOE demonstration awards?',
      'What active solicitations have cost-share under 20% and close in the next 90 days for hydrogen?',
      'Who are the top repeat winning prime developers for CEC microgrid awards in California?',
      'What are the statutory Disadvantaged Community requirements for energy innovation grants?'
    ],
    starterPrompts: [
      {
        title: 'Grant Stacking Strategy',
        prompt: 'How can we stack state energy innovation grants with federal DOE demonstration awards for a 10MW Long-Duration Energy Storage facility?'
      },
      {
        title: 'Active Hydrogen Solicitations',
        prompt: 'What active solicitations have cost-share under 20% and close in the next 90 days for clean hydrogen?'
      },
      {
        title: 'California Microgrid Comps',
        prompt: 'Who are the top repeat winning prime developers for CEC EPIC microgrid awards in California?'
      },
      {
        title: 'Justice40 / DAC Match',
        prompt: 'What are the statutory Disadvantaged Community (DAC) requirements for New York clean heat grants?'
      }
    ]
  },
  {
    id: 'investor',
    title: 'Climate Tech VC / Investor',
    badge: 'Investor',
    icon: TrendingUp,
    description: 'Technical diligence, public grant traction comps, IP moats & follow-on risk',
    spokenStarters: [
      'What is the historical average grant award and co-funding ratio in thermal networks?',
      'Analyze public grant track records and patent linkages for solid-state battery companies.',
      'Which institutions in California and Massachusetts have captured the highest non-dilutive capital?',
      'What are typical TRL 4 to 7 scale-up hurdles identified in public demonstration filings?'
    ],
    starterPrompts: [
      {
        title: 'Grant Comp Benchmarks',
        prompt: 'What is the historical average grant award and co-funding ratio across Building Decarbonization and thermal network startups?'
      },
      {
        title: 'Battery IP & Award Track Record',
        prompt: 'Analyze public grant track records and patent linkages for solid-state battery companies in our database.'
      },
      {
        title: 'Top Regional Recipients',
        prompt: 'Which institutions in California and Massachusetts have captured the highest non-dilutive capital in thermal networks?'
      },
      {
        title: 'TRL 4-7 Scale-up Risk',
        prompt: 'What are typical TRL 4-7 scale-up hurdles and equipment lead times identified in public demonstration filings?'
      }
    ]
  },
  {
    id: 'researcher',
    title: 'University / National Lab PI',
    badge: 'Researcher',
    icon: BookOpen,
    description: 'FOA scoring rubrics, academic-industry consortia & Bayh-Dole tech transfer',
    spokenStarters: [
      'Find active ARPA-E and NSF solicitations for next-gen perovskite solar cells.',
      'Who are the leading Principal Investigators with active awards in Grid Modernization?',
      'How can our university team structure a compliant proposal consortium for DOE OCED funding?',
      'Which universities hold the most Bayh-Dole patents in geothermal and direct air capture?'
    ],
    starterPrompts: [
      {
        title: 'ARPA-E Solar Solicitations',
        prompt: 'Find active ARPA-E and NSF solicitations for next-gen perovskite solar cells and identify potential utility testbed partners.'
      },
      {
        title: 'Grid Modernization PIs',
        prompt: 'Who are the leading Principal Investigators in New York and Massachusetts with active awards in Grid Modernization?'
      },
      {
        title: 'Consortium Teaming Structure',
        prompt: 'How can our university team structure a compliant proposal consortium for DOE OCED funding with industrial partners?'
      },
      {
        title: 'Bayh-Dole Patent Filings',
        prompt: 'Which universities hold the most Bayh-Dole patents in geothermal and direct air capture?'
      }
    ]
  },
  {
    id: 'utility',
    title: 'Electric Utility Grid Lead',
    badge: 'Utility',
    icon: Zap,
    description: 'Non-Wires Alternatives (NWA), FERC Order 1920 & hosting capacity',
    spokenStarters: [
      'What Non-Wires Alternative utility filings and solicitation precedents exist for congested zones?',
      'What Grid-Enhancing Technologies and Dynamic Line Rating solutions receive federal matching grants?',
      'What utility-backed microgrid demonstration projects have proven black-start resilience?',
      'What active funding programs support utility-scale DERMS and IEEE 2030.5 pilots?'
    ],
    starterPrompts: [
      {
        title: 'Utility NWA Filings',
        prompt: 'What Non-Wires Alternative (NWA) utility filings and solicitation precedents exist for transmission-congested load zones?'
      },
      {
        title: 'FERC 1920 Grid Technologies',
        prompt: 'What Grid-Enhancing Technologies (GETs) and Dynamic Line Rating solutions are receiving federal matching grants?'
      },
      {
        title: 'Microgrid Islanding Comps',
        prompt: 'What utility-backed microgrid demonstration projects have proven black-start resilience in the Northeast?'
      },
      {
        title: 'DERMS Orchestration Grants',
        prompt: 'What active funding programs support utility-scale DERMS and IEEE 2030.5 interoperability pilots?'
      }
    ]
  },
  {
    id: 'policy',
    title: 'State Energy Official',
    badge: 'Policy Lead',
    icon: ShieldCheck,
    description: 'Designing public funding programs, statutory Justice40 / DAC compliance & ratepayer ROI',
    spokenStarters: [
      'Benchmark programmatic funding allocation and median award size across state energy agencies.',
      'How do state energy offices ensure 35 to 40% of energy innovation benefits flow to DAC communities?',
      'What are the primary equipment lead times and interconnection queue bottlenecks?',
      'How are state green banks structuring risk-sharing facilities with federal loan programs?'
    ],
    starterPrompts: [
      {
        title: 'Agency Benchmark Comps',
        prompt: 'Benchmark programmatic funding allocation and median award size across state energy agencies (NYSERDA vs CEC vs MassCEC).'
      },
      {
        title: 'DAC Equity Allocation',
        prompt: 'How do state energy offices ensure 35-40% of energy innovation program benefits flow to frontline disadvantaged communities?'
      },
      {
        title: 'Interconnection Bottlenecks',
        prompt: 'What are the primary equipment lead times and interconnection queue bottlenecks impacting state energy innovation targets?'
      },
      {
        title: 'Green Bank Loan Facilities',
        prompt: 'How are state green banks structuring risk-sharing facilities with federal loan programs for FOAK demonstration projects?'
      }
    ]
  },
  {
    id: 'grant_writer',
    title: 'Grant Writer / Consultant',
    badge: 'Grant Writer',
    icon: FileText,
    description: 'Compliance matrices, scoring rubric maximization & SOPO work plans',
    spokenStarters: [
      'Draft a 4-phase Statement of Project Objectives and milestone schedule for clean hydrogen.',
      'Analyze active DOE and state energy innovation storage solicitations for mandatory disqualifying rules.',
      'What are allowable non-federal cost-share sources and third-party in-kind contributions?',
      'What key technical differentiators and community benefit plans maximize scores in review panels?'
    ],
    starterPrompts: [
      {
        title: 'Proposal WBS & SOPO Plan',
        prompt: 'Draft a 4-phase Statement of Project Objectives (SOPO) and milestone schedule for a DOE clean hydrogen demonstration grant.'
      },
      {
        title: 'Hard vs Soft Requirements',
        prompt: 'Analyze active DOE and state energy innovation storage solicitations and list all mandatory disqualifying eligibility rules.'
      },
      {
        title: 'Cost-Share Match Strategy',
        prompt: 'What are the allowable non-federal cost-share sources and third-party in-kind contributions for federal grant applications?'
      },
      {
        title: 'Scoring Rubric Alignment',
        prompt: 'What key technical differentiators and community benefit plans maximize scores in multi-agency review panels?'
      }
    ]
  }
];

export default function Chat() {
  const [advisoryMode, setAdvisoryMode] = useState<AdvisoryMode>(() => {
    return ((localStorage.getItem('energysignal_advisory_mode') || localStorage.getItem('cleangrants_advisory_mode')) as AdvisoryMode) || 'chat';
  });
  const [messages, setMessages] = useState<ChatMessageItem[]>([]);
  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userRole, setUserRole] = useState<UserRole>(() => {
    return ((localStorage.getItem('energysignal_user_role') || localStorage.getItem('cleangrants_user_role')) as UserRole) || 'institutional_leader';
  });
  const [isRoleDropdownOpen, setIsRoleDropdownOpen] = useState(false);
  const [apiKey, setApiKey] = useState(() => localStorage.getItem('energysignal_openai_api_key') || localStorage.getItem('openai_api_key') || '');
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [openSourcesId, setOpenSourcesId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const currentRoleConfig = ROLES.find(r => r.id === userRole) || ROLES[0];

  const handleRoleSelect = (role: UserRole) => {
    setUserRole(role);
    localStorage.setItem('energysignal_user_role', role);
    setIsRoleDropdownOpen(false);
  };

  const handleSwitchMode = (mode: AdvisoryMode) => {
    setAdvisoryMode(mode);
    localStorage.setItem('energysignal_advisory_mode', mode);
  };

  // Auto-scroll to bottom on new tokens
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Check backend OpenAI status on mount
  useEffect(() => {
    fetch('/api/chat/status')
      .then(res => res.json())
      .then(data => {
        if (data.openai_configured && !apiKey) {
          setApiKey('backend-configured');
        }
      })
      .catch(() => {});
  }, []);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [inputQuery]);

  const handleSaveApiKey = async (key: string) => {
    const trimmed = key.trim();
    setApiKey(trimmed);
    if (trimmed) {
      localStorage.setItem('openai_api_key', trimmed);
    } else {
      localStorage.removeItem('openai_api_key');
    }

    try {
      await fetch('/api/chat/set-api-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: trimmed })
      });
    } catch (e) {
      console.error('Failed to sync API key to backend:', e);
    }

    setShowKeyModal(false);
  };

  const handleSend = async (queryText?: string) => {
    const textToSend = (queryText || inputQuery).trim();
    if (!textToSend || isLoading) return;

    setInputQuery('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';

    const userMessageId = `usr_${Date.now()}`;
    const assistantMessageId = `ast_${Date.now()}`;

    const userMessage: ChatMessageItem = {
      id: userMessageId,
      role: 'user',
      content: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    const initialAssistantMessage: ChatMessageItem = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      isStreaming: true,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages(prev => [...prev, userMessage, initialAssistantMessage]);
    setIsLoading(true);

    const historyPayload = messages.map(m => ({ role: m.role, content: m.content }));

    try {
      const stream = streamChatCompletion(
        textToSend,
        historyPayload,
        apiKey || undefined,
        'gpt-4o-mini',
        userRole
      );

      let accumulatedContent = '';
      let citationsData: ChatCitationsMetadata | undefined;

      for await (const chunk of stream) {
        if (chunk.type === 'retrieval' && chunk.data) {
          citationsData = chunk.data;
          setMessages(prev =>
            prev.map(m => (m.id === assistantMessageId ? { ...m, citations: citationsData } : m))
          );
        } else if (chunk.type === 'token' && chunk.token) {
          accumulatedContent += chunk.token;
          setMessages(prev =>
            prev.map(m =>
              m.id === assistantMessageId
                ? { ...m, content: accumulatedContent, citations: citationsData }
                : m
            )
          );
        } else if (chunk.type === 'review_complete') {
          if (chunk.reviewed_text) accumulatedContent = chunk.reviewed_text;
          if (chunk.data) citationsData = chunk.data;
          setMessages(prev =>
            prev.map(m =>
              m.id === assistantMessageId
                ? { ...m, content: accumulatedContent, citations: citationsData }
                : m
            )
          );
        } else if (chunk.type === 'done') {
          setMessages(prev =>
            prev.map(m =>
              m.id === assistantMessageId
                ? { ...m, content: accumulatedContent, citations: citationsData, isStreaming: false }
                : m
            )
          );
        }
      }
    } catch (err: any) {
      console.error('Chat error:', err);
      setMessages(prev =>
        prev.map(m =>
          m.id === assistantMessageId
            ? {
                ...m,
                content:
                  m.content ||
                  `**Error communicating with database assistant:** ${err.message || 'Unknown network error'}. Please verify connection or retry.`,
                isStreaming: false,
              }
            : m
        )
      );
    } finally {
      setIsLoading(false);
      setTimeout(() => textareaRef.current?.focus(), 50);
    }
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleNewChat = () => {
    setMessages([]);
    setInputQuery('');
    setTimeout(() => textareaRef.current?.focus(), 50);
  };

  // Helper to render markdown table into a clean, responsive HTML table
  const renderMarkdownTable = (tableText: string, key: number) => {
    const lines = tableText.trim().split('\n').map(l => l.trim()).filter(Boolean);
    if (lines.length < 2) return null;

    const headerLine = lines[0];
    const rawHeaders = headerLine.split('|').map(h => h.trim());
    // Filter empty ends from split on `| col1 | col2 |`
    const headers = rawHeaders.filter((_, idx, arr) => idx > 0 && idx < arr.length - (rawHeaders[rawHeaders.length - 1] === '' ? 1 : 0));
    const activeHeaders = headers.length > 0 ? headers : rawHeaders.filter(Boolean);

    // Filter delimiter lines e.g. |---|---|
    const rowsLines = lines.slice(1).filter(l => !/^[|\s-:]+$/.test(l));

    return (
      <div key={key} className="overflow-x-auto rounded-xl border border-slate-200 shadow-2xs my-3 bg-white">
        <table className="w-full text-left text-[13px] border-collapse">
          <thead>
            <tr className="bg-slate-100/90 text-slate-800 text-[11.5px] uppercase tracking-wider font-semibold border-b border-slate-200">
              {activeHeaders.map((h, hIdx) => (
                <th key={hIdx} className="px-3.5 py-2.5 whitespace-nowrap">
                  {h.replace(/\*\*/g, '')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {rowsLines.map((row, rIdx) => {
              const rawCells = row.split('|').map(c => c.trim());
              const cells = rawCells.filter((_, idx, arr) => idx > 0 && idx < arr.length - (rawCells[rawCells.length - 1] === '' ? 1 : 0));
              const activeCells = cells.length > 0 ? cells : rawCells.filter(Boolean);

              return (
                <tr key={rIdx} className="hover:bg-cyan-50/40 transition-colors even:bg-slate-50/50">
                  {activeCells.map((cell, cIdx) => (
                    <td key={cIdx} className="px-3.5 py-2.5 text-slate-700 leading-snug">
                      <span dangerouslySetInnerHTML={{ __html: formatInlineMarkdown(cell) }} />
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    );
  };

  // Helper to render markdown text with narrative typography, Mermaid diagrams, code cards, callouts, tables, and lists
  const renderFormattedContent = (content: string) => {
    if (!content) return null;

    return (
      <div className="space-y-3.5 leading-relaxed text-slate-800 text-[14.5px]">
        {content.split('\n\n').map((paragraph, pIdx) => {
          const trimmedP = paragraph.trim();

          // 1. Mermaid Architecture / Flowchart Diagram
          if (trimmedP.startsWith('```mermaid') || trimmedP.includes('```mermaid')) {
            const code = trimmedP.replace(/```mermaid\n?/, '').replace(/```$/, '').trim();
            return <MermaidDiagram key={pIdx} chart={code} />;
          }

          // 2. Syntax-Highlighted Code & Schema Block
          if (trimmedP.startsWith('```') && trimmedP.endsWith('```')) {
            const lines = trimmedP.split('\n');
            const lang = lines[0].replace(/^```/, '').trim() || 'code';
            const code = lines.slice(1, -1).join('\n');
            return (
              <div key={pIdx} className="my-3 rounded-xl border border-slate-800 bg-slate-900 text-slate-100 overflow-hidden font-mono text-[12px] shadow-xs">
                <div className="flex items-center justify-between px-3.5 py-1.5 bg-slate-950 border-b border-slate-800 text-[11px] text-slate-400">
                  <span className="uppercase font-semibold tracking-wider">{lang}</span>
                  <button
                    type="button"
                    onClick={() => navigator.clipboard.writeText(code)}
                    className="hover:text-white transition-colors cursor-pointer px-1.5 py-0.5 rounded hover:bg-slate-800"
                  >
                    Copy
                  </button>
                </div>
                <pre className="p-3.5 overflow-x-auto leading-relaxed">{code}</pre>
              </div>
            );
          }

          // 3. Executive Callout / Warning Box
          if (trimmedP.startsWith('> [!NOTE]') || trimmedP.startsWith('> [!IMPORTANT]') || trimmedP.startsWith('> [!WARNING]') || trimmedP.startsWith('> [!TIP]')) {
            const isWarning = trimmedP.includes('[!WARNING]') || trimmedP.includes('[!CAUTION]');
            const isTip = trimmedP.includes('[!TIP]');
            const cleanBody = trimmedP.replace(/^> \[[!A-Z]+\]\n?/, '').replace(/^> /gm, '');
            return (
              <div
                key={pIdx}
                className={`my-3 p-3.5 rounded-xl border flex items-start gap-2.5 text-[13px] leading-relaxed shadow-2xs ${
                  isWarning
                    ? 'bg-amber-50/90 border-amber-200 text-amber-950'
                    : isTip
                    ? 'bg-emerald-50/90 border-emerald-200 text-emerald-950'
                    : 'bg-cyan-50/90 border-cyan-200 text-cyan-950'
                }`}
              >
                <ShieldCheck size={16} className={`shrink-0 mt-0.5 ${isWarning ? 'text-amber-600' : isTip ? 'text-emerald-600' : 'text-cyan-700'}`} />
                <div className="flex-1" dangerouslySetInnerHTML={{ __html: formatInlineMarkdown(cleanBody) }} />
              </div>
            );
          }

          // 4. Embedded Image / Infographic
          if (/^!\[(.*?)\]\((.*?)\)$/.test(trimmedP)) {
            const match = trimmedP.match(/^!\[(.*?)\]\((.*?)\)$/);
            if (match) {
              const [, alt, src] = match;
              return (
                <div key={pIdx} className="my-3 rounded-2xl border border-slate-200 overflow-hidden bg-slate-50 p-2 shadow-2xs text-center">
                  <img src={src} alt={alt} className="max-h-96 mx-auto rounded-xl object-contain shadow-2xs" />
                  {alt && <p className="text-[11.5px] text-slate-500 mt-1.5 font-medium">{alt}</p>}
                </div>
              );
            }
          }

          // 5. Responsive Markdown Table
          if (trimmedP.includes('|') && trimmedP.split('\n').some(l => /^[|\s-:]+$/.test(l))) {
            return renderMarkdownTable(trimmedP, pIdx);
          }

          // 6. Typography Headers
          if (paragraph.startsWith('### ')) {
            return (
              <h3 key={pIdx} className="text-[15.5px] font-semibold text-slate-900 border-b border-slate-100 pb-1.5 pt-2">
                {paragraph.replace('### ', '').replace(/\*\*/g, '')}
              </h3>
            );
          }
          if (paragraph.startsWith('#### ')) {
            return (
              <h4 key={pIdx} className="text-[14.5px] font-semibold text-cyan-950 pt-1">
                {paragraph.replace('#### ', '').replace(/\*\*/g, '')}
              </h4>
            );
          }

          // 7. Numbered List
          if (/^\d+\.\s/.test(paragraph) || paragraph.includes('\n1. ') || paragraph.includes('\n2. ')) {
            const items = paragraph.split(/\n(?=\d+\.\s)/);
            return (
              <ol key={pIdx} className="space-y-2 pl-5 list-decimal text-slate-700">
                {items.map((item, iIdx) => (
                  <li key={iIdx} dangerouslySetInnerHTML={{ __html: formatInlineMarkdown(item.replace(/^\d+\.\s*/, '')) }} />
                ))}
              </ol>
            );
          }

          // 8. Bullet List
          if (paragraph.includes('\n- ') || paragraph.startsWith('- ')) {
            const items = paragraph.split('\n- ').map(i => i.replace(/^- /, ''));
            return (
              <ul key={pIdx} className="space-y-2 pl-5 list-disc text-slate-700">
                {items.map((item, iIdx) => (
                  <li key={iIdx} dangerouslySetInnerHTML={{ __html: formatInlineMarkdown(item) }} />
                ))}
              </ul>
            );
          }

          // 9. Standard Narrative Paragraph
          return (
            <p key={pIdx} dangerouslySetInnerHTML={{ __html: formatInlineMarkdown(paragraph) }} />
          );
        })}
      </div>
    );
  };

  const formatInlineMarkdown = (text: string) => {
    let formatted = text
      // Remove any asterisks / bolding
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/\*(.*?)\*/g, '$1')
      // Code tags
      .replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 rounded bg-slate-100 text-slate-800 font-mono text-[12px] border border-slate-200">$1</code>')
      // Interactive Citation Badges
      .replace(/\[OPP:(\d+)\]/g, '<a href="/opportunities/$1" class="inline-flex items-center gap-1 px-1.5 py-0.2 rounded-md bg-cyan-500/15 hover:bg-cyan-500/25 text-[#00E5FF] hover:text-white border border-cyan-400/40 text-[11px] font-mono font-bold transition-all shadow-glow-cyan-sm mx-0.5 cursor-pointer no-underline" title="View Solicitation #$1"><span>FOA #$1</span><span class="text-[9px] opacity-70">↗</span></a>')
      .replace(/\[ORG:(\d+)\]/g, '<a href="/organizations" class="inline-flex items-center gap-1 px-1.5 py-0.2 rounded-md bg-cyan-500/15 hover:bg-cyan-500/25 text-[#00E5FF] hover:text-white border border-cyan-400/40 text-[11px] font-mono font-bold transition-all shadow-glow-cyan-sm mx-0.5 cursor-pointer no-underline" title="Explore Verified Organization Directory"><span>Org #$1</span><span class="text-[9px] opacity-70">↗</span></a>')
      .replace(/\[AWD:(\d+)\]/g, '<a href="/awards" class="inline-flex items-center gap-1 px-1.5 py-0.2 rounded-md bg-emerald-500/15 hover:bg-emerald-500/25 text-[#00F5A0] hover:text-white border border-emerald-400/40 text-[11px] font-mono font-bold transition-all shadow-[0_0_8px_rgba(0,245,160,0.2)] mx-0.5 cursor-pointer no-underline" title="Explore Historical Award Ledger"><span>Award #$1</span><span class="text-[9px] opacity-70">↗</span></a>')
      .replace(/\[PI:(\d+)\]/g, '<a href="/contacts" class="inline-flex items-center gap-1 px-1.5 py-0.2 rounded-md bg-purple-500/15 hover:bg-purple-500/25 text-purple-300 hover:text-white border border-purple-400/40 text-[11px] font-mono font-bold transition-all shadow-2xs mx-0.5 cursor-pointer no-underline" title="Explore Principal Investigators Directory"><span>PI #$1</span><span class="text-[9px] opacity-70">↗</span></a>')
      // Clean Markdown Links
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-[#00E5FF] hover:underline font-semibold underline-offset-2">$1</a>');

    return formatted;
  };

  if (advisoryMode === 'video') {
    return (
      <div className="flex flex-col h-[calc(100vh-6rem)] -mt-2 -mx-2 bg-slate-900 relative">
        <TavusVideoConversation
          userRole={userRole}
          onRoleChange={handleRoleSelect}
          roles={ROLES}
          onSwitchToChat={() => handleSwitchMode('chat')}
          onBackToHub={() => handleSwitchMode('landing')}
        />
      </div>
    );
  }

  if (advisoryMode === 'landing') {
    return (
      <div className="flex flex-col h-[calc(100vh-6rem)] -mt-2 -mx-2 bg-slate-50 overflow-y-auto">
        <div className="max-w-5xl mx-auto w-full px-4 py-8 space-y-8">
          {/* Landing Header */}
          <div className="text-center space-y-3">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-100 border border-cyan-200 text-cyan-900 text-xs font-semibold shadow-2xs">
              <Compass size={14} className="text-cyan-600" />
              <span>Strategic Advisory · Interactive Research Counsel</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
              Advisory Hub
            </h1>
            <p className="text-slate-600 text-sm sm:text-base max-w-2xl mx-auto leading-relaxed">
              Select your operational perspective below, then choose whether to interact via deep text chat or launch directly into a live face-to-face video session with Brandon Owens, grounded in the US Energy Innovation Database by Brandon N. Owens.
            </p>
          </div>

          {/* Step 1: Perspective Selector */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-cyan-600 text-white text-xs font-bold">1</span>
                <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                  Select Your Operational Perspective
                </h2>
              </div>
              <span className="text-xs text-slate-500 font-medium">
                Active: <strong className="text-cyan-700">{currentRoleConfig.badge}</strong>
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {ROLES.map(r => {
                const isSelected = userRole === r.id;
                return (
                  <button
                    key={r.id}
                    type="button"
                    onClick={() => handleRoleSelect(r.id)}
                    className={`p-3.5 rounded-xl text-left transition-all cursor-pointer border flex flex-col justify-between group relative ${
                      isSelected
                        ? 'bg-cyan-50/70 border-2 border-cyan-600 shadow-sm ring-2 ring-cyan-500/20'
                        : 'bg-white hover:bg-slate-50 border-slate-200 shadow-2xs hover:border-slate-300'
                    }`}
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className={`p-2 rounded-lg ${isSelected ? 'bg-cyan-600 text-white' : 'bg-slate-100 text-slate-700 group-hover:bg-slate-200'}`}>
                          <r.icon size={16} />
                        </div>
                        {isSelected && (
                          <span className="flex items-center gap-1 text-[11px] font-bold text-cyan-700 bg-cyan-100 px-1.5 py-0.5 rounded-md">
                            <Check size={12} strokeWidth={3} />
                            <span>Selected</span>
                          </span>
                        )}
                      </div>
                      <div>
                        <div className={`font-bold text-[13px] leading-snug ${isSelected ? 'text-cyan-950' : 'text-slate-900'}`}>
                          {r.title}
                        </div>
                        <p className="text-[11px] text-slate-500 mt-1 line-clamp-2 leading-relaxed">
                          {r.description}
                        </p>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Active Perspective Strategic Insight Pill */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-700 uppercase tracking-wider">
                <currentRoleConfig.icon size={14} className="text-cyan-600" />
                <span>Advisory Focus for {currentRoleConfig.badge}:</span>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                {currentRoleConfig.description}
              </p>
            </div>
          </div>

          {/* Step 2: Choose Advisory Modality & Launch */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-cyan-600 text-white text-xs font-bold">2</span>
              <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                Choose Your Advisory Modality &amp; Launch
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {/* Option A: Advisory Chat */}
              <div className="rounded-2xl border-2 border-slate-200 hover:border-cyan-500 p-6 flex flex-col justify-between bg-white hover:bg-cyan-50/20 transition-all group shadow-2xs">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="p-3 rounded-xl bg-cyan-500/10 text-cyan-600">
                      <MessageSquare size={24} />
                    </div>
                    <span className="text-[10px] font-bold font-mono uppercase bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
                      Grounded RAG
                    </span>
                  </div>

                  <div className="space-y-1">
                    <h3 className="text-lg font-bold text-slate-900 group-hover:text-cyan-900">
                      Advisory Chat
                    </h3>
                    <p className="text-xs text-slate-500 leading-relaxed">
                      Deep reasoning text conversation with citation badges, Mermaid charts, proposal WBS drafting, and monograph exports.
                    </p>
                  </div>

                  <ul className="space-y-2 text-xs text-slate-600 pt-2 border-t border-slate-100">
                    <li className="flex items-start gap-2">
                      <CheckCircle2 size={14} className="text-cyan-600 shrink-0 mt-0.5" />
                      <span>Instant citations across 56,413 awards &amp; 5,757 solicitations</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 size={14} className="text-cyan-600 shrink-0 mt-0.5" />
                      <span>Interactive Mermaid system diagrams &amp; proposal matrices</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 size={14} className="text-cyan-600 shrink-0 mt-0.5" />
                      <span>Adopts {currentRoleConfig.badge} strategic directives</span>
                    </li>
                  </ul>
                </div>

                <div className="pt-6">
                  <button
                    type="button"
                    onClick={() => handleSwitchMode('chat')}
                    className="w-full inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-sm shadow-md transition-all cursor-pointer"
                  >
                    <span>Launch Advisory Chat</span>
                    <ArrowUp size={15} className="rotate-90" />
                  </button>
                </div>
              </div>

              {/* Option B: Live Video Advisor (Direct Launch) */}
              <div className="rounded-2xl border-2 border-cyan-500 p-6 flex flex-col justify-between bg-gradient-to-b from-cyan-50/40 to-emerald-50/30 transition-all shadow-md relative overflow-hidden group">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="p-3 rounded-xl bg-gradient-to-tr from-cyan-500 to-emerald-500 text-white shadow-sm">
                      <Video size={24} />
                    </div>
                    <span className="text-[10px] font-bold font-mono uppercase bg-cyan-600 text-white px-2 py-0.5 rounded shadow-2xs">
                      Video Advisory · Live Session
                    </span>
                  </div>

                  <div className="space-y-1">
                    <h3 className="text-lg font-bold text-slate-900">
                      Live Video Advisor
                    </h3>
                    <p className="text-xs text-slate-600 leading-relaxed">
                      Bidirectional face-to-face video advisory session with Brandon Owens (April 14 2026), grounded in the US Energy Innovation Database by Brandon N. Owens.
                    </p>
                  </div>

                  <ul className="space-y-2 text-xs text-slate-700 pt-2 border-t border-cyan-100">
                    <li className="flex items-start gap-2">
                      <CheckCircle2 size={14} className="text-emerald-600 shrink-0 mt-0.5" />
                      <span>Sub-second real-time conversational streaming</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 size={14} className="text-emerald-600 shrink-0 mt-0.5" />
                      <span>Grounded in 56,413 energy innovation awards &amp; 5,757 solicitations</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 size={14} className="text-emerald-600 shrink-0 mt-0.5" />
                      <span><strong className="text-slate-900">Zero waiting room:</strong> Launches directly into live session</span>
                    </li>
                  </ul>
                </div>

                <div className="pt-6">
                  <button
                    type="button"
                    onClick={() => handleSwitchMode('video')}
                    className="w-full inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-sm shadow-md transition-all cursor-pointer"
                  >
                    <Video size={16} />
                    <span>Launch Live Video Advisor</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)] -mt-2 -mx-2 bg-white dark:bg-slate-900 relative">
      {/* Top Header Bar with Mode Switcher, Role Selector & Controls */}
      <header className="h-13 border-b border-slate-200 dark:border-slate-800 px-4 flex items-center justify-between shrink-0 bg-white/95 dark:bg-slate-900/95 backdrop-blur-sm z-20">
        <div className="flex items-center gap-3">
          {/* Back to Advisor Hub Link */}
          <button
            type="button"
            onClick={() => handleSwitchMode('landing')}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-[12px] font-semibold transition-colors cursor-pointer"
            title="Return to Advisor Perspectives"
          >
            <Compass size={13} className="text-slate-500 dark:text-slate-400" />
            <span>Perspectives</span>
          </button>

          {/* Segmented Control for Chat vs Video Mode */}
          <div className="flex items-center bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg border border-slate-200 dark:border-slate-700">
            <button
              type="button"
              onClick={() => handleSwitchMode('chat')}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11.5px] font-bold bg-[#00E5FF] text-slate-950 shadow-glow-cyan-sm transition-all cursor-pointer"
            >
              <MessageSquare size={13} className="text-slate-950 font-bold" />
              <span>Advisory Chat</span>
            </button>
            <button
              type="button"
              onClick={() => handleSwitchMode('video')}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11.5px] font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 transition-all cursor-pointer"
            >
              <Video size={13} className="text-slate-500 dark:text-slate-400" />
              <span>Video Advisor</span>
            </button>
          </div>

          {/* Active Role Selector Dropdown */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setIsRoleDropdownOpen(!isRoleDropdownOpen)}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-[12px] font-medium text-slate-700 dark:text-slate-300 transition-colors shadow-2xs cursor-pointer"
            >
              <currentRoleConfig.icon size={13} className="text-slate-500 dark:text-slate-400" />
              <span>Perspective: <strong className="font-semibold text-slate-900 dark:text-slate-100">{currentRoleConfig.badge}</strong></span>
              <ChevronDown size={12} className="text-slate-400 ml-0.5" />
            </button>

            {isRoleDropdownOpen && (
              <div className="absolute left-0 mt-1 w-80 bg-white dark:bg-slate-900 rounded-xl shadow-xl border border-slate-200 dark:border-slate-800 p-1.5 z-30 animate-in fade-in-50 duration-100 max-h-96 overflow-y-auto">
                <div className="px-2.5 py-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  Select Your Perspective
                </div>
                {ROLES.map(r => (
                  <button
                    key={r.id}
                    type="button"
                    onClick={() => handleRoleSelect(r.id)}
                    className={`w-full text-left p-2 rounded-lg flex items-start gap-2.5 text-[12px] transition-colors cursor-pointer ${
                      userRole === r.id ? 'bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-semibold' : 'hover:bg-slate-50 dark:hover:bg-slate-800/50 text-slate-700 dark:text-slate-300'
                    }`}
                  >
                    <r.icon size={14} className={`shrink-0 mt-0.5 ${userRole === r.id ? 'text-blue-600 dark:text-blue-400' : 'text-slate-400'}`} />
                    <div>
                      <div className="flex items-center justify-between">
                        <span>{r.title}</span>
                        {userRole === r.id && <Check size={12} className="text-blue-600 dark:text-blue-400" />}
                      </div>
                      <div className="text-[10.5px] text-slate-500 dark:text-slate-400 font-normal leading-tight mt-0.5">
                        {r.description}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/60 text-[11.5px] font-medium"
            title="Database Connected (56,413 Awards · 5,757 Solicitations)"
          >
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span>Database Connected</span>
          </div>

          <button
            type="button"
            onClick={handleNewChat}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 text-[12px] font-medium transition-all cursor-pointer shadow-2xs"
          >
            <Plus size={13} />
            <span>New chat</span>
          </button>
        </div>
      </header>

      {/* Conversation Thread */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-3xl mx-auto space-y-6">
          {messages.length === 0 ? (
            /* Simple Clean Query Empty State Tailored to Role */
            <div className="min-h-[50vh] flex flex-col items-center justify-center text-center space-y-6 pt-2">
              <div className="space-y-2">
                <div className="inline-flex items-center justify-center w-11 h-11 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 mb-2">
                  <Compass size={20} className="text-slate-600 dark:text-slate-300" />
                </div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">
                  What can I help you evaluate today?
                </h1>
                <p className="text-[13.5px] text-slate-500 dark:text-slate-400 max-w-lg mx-auto">
                  Strategic intelligence across 56,413 awards, 5,757 solicitations, and innovation networks.
                </p>

                {/* Perspective & Spoken Prompt Starters */}
                <div className="pt-4 max-w-xl mx-auto space-y-3">
                  <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 px-1">
                    <span>Perspective: <strong className="text-slate-800 dark:text-slate-200">{currentRoleConfig.badge}</strong></span>
                    <button
                      type="button"
                      onClick={() => handleSwitchMode('landing')}
                      className="text-blue-600 dark:text-blue-400 hover:underline font-semibold cursor-pointer"
                    >
                      Change Perspective &rarr;
                    </button>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-left">
                    {currentRoleConfig.starterPrompts.map((sp, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => handleSend(sp.prompt)}
                        className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-slate-400 dark:hover:border-slate-600 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800/60 text-left transition-all cursor-pointer group shadow-2xs"
                      >
                        <div className="font-semibold text-xs text-slate-900 dark:text-slate-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 leading-snug">
                          {sp.title}
                        </div>
                        <div className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-2 mt-1">
                          {sp.prompt}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            /* Messages */
            messages.map(msg => (
              <div key={msg.id} className="space-y-2">
                {msg.role === 'user' ? (
                  /* User Message - Right-aligned clean bubble */
                  <div className="flex justify-end">
                    <div className="bg-slate-900 dark:bg-slate-800 text-white px-4.5 py-3 rounded-2xl rounded-br-xs max-w-[85%] text-[14px] leading-relaxed shadow-2xs border border-slate-800 dark:border-slate-700">
                      {msg.content}
                    </div>
                  </div>
                ) : (
                  /* Assistant Message - Left-aligned clean typography */
                  <div className="flex gap-3 text-slate-800 dark:text-slate-200 pt-1">
                    <div className="w-7 h-7 rounded-lg bg-slate-900 dark:bg-slate-800 border border-slate-700 text-slate-200 flex items-center justify-center shrink-0 shadow-2xs mt-0.5">
                      <FileText size={14} className="text-slate-300" />
                    </div>

                    <div className="flex-1 min-w-0 space-y-3">
                      {/* Markdown Body */}
                      {renderFormattedContent(msg.content)}

                      {/* Streaming Indicator */}
                      {msg.isStreaming && (
                        <div className="flex items-center gap-2 text-slate-400 text-[12px] font-medium animate-pulse pt-1">
                          <RefreshCw size={12} className="animate-spin text-slate-500" />
                          <span>Searching records and analyzing strategic directives for {currentRoleConfig.badge}...</span>
                        </div>
                      )}

                      {/* Collapsible Verified Sources Capsule */}
                      {msg.citations && !msg.isStreaming && (
                        <div className="pt-2">
                          <button
                            type="button"
                            onClick={() => setOpenSourcesId(openSourcesId === msg.id ? null : msg.id)}
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700/80 text-slate-600 dark:text-slate-400 text-[11.5px] font-medium transition-colors cursor-pointer"
                          >
                            <ShieldCheck size={13} className="text-emerald-600 dark:text-emerald-400" />
                            <span>
                              {msg.citations.statistics.retrieved_opportunities_count} Solicitations · {msg.citations.statistics.retrieved_awards_count} Awards · {msg.citations.organizations?.length || 0} Orgs · {msg.citations.contacts?.length || 0} PIs Verified
                            </span>
                            {openSourcesId === msg.id ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                          </button>

                          {openSourcesId === msg.id && (
                            <div className="mt-2 p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-800/80 space-y-3.5 animate-in fade-in-50 duration-150 text-[12px]">
                              {/* Matching Solicitations */}
                              {msg.citations.opportunities.length > 0 && (
                                <div className="space-y-1.5">
                                  <div className="flex items-center justify-between">
                                    <span className="font-bold text-slate-700 dark:text-slate-300 text-[11px] uppercase tracking-wider flex items-center gap-1.5">
                                      <FileText size={12} className="text-slate-500" />
                                      <span>Matching Solicitations &amp; PONs:</span>
                                    </span>
                                    <Link to="/opportunities" className="text-[10.5px] font-semibold text-blue-600 dark:text-blue-400 hover:underline">
                                      All Solicitations &rarr;
                                    </Link>
                                  </div>
                                  <div className="space-y-1">
                                    {msg.citations.opportunities.slice(0, 4).map(o => (
                                      <Link
                                        key={o.id}
                                        to={o.url}
                                        className="flex items-center justify-between p-2 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:border-slate-400 transition-all text-slate-800 dark:text-slate-200 group"
                                      >
                                        <div className="truncate pr-2">
                                          <span className="font-semibold text-slate-900 dark:text-slate-100 group-hover:text-blue-600 dark:group-hover:text-blue-400">{o.agency} · {o.solicitation_number}</span>
                                          <span className="text-slate-500 dark:text-slate-400 text-[11px] ml-1.5 truncate">{o.name}</span>
                                        </div>
                                        <div className="flex items-center gap-2 shrink-0">
                                          {o.total_funding ? (
                                            <span className="font-mono text-[10.5px] text-emerald-700 dark:text-emerald-400 font-semibold bg-emerald-50 dark:bg-emerald-950/40 px-1.5 py-0.2 rounded border border-emerald-200 dark:border-emerald-800">
                                              ${(o.total_funding / 1e6).toFixed(1)}M
                                            </span>
                                          ) : null}
                                          <span className="text-slate-400 font-semibold text-[11px] group-hover:translate-x-0.5 transition-transform">&rarr;</span>
                                        </div>
                                      </Link>
                                    ))}
                                  </div>
                                </div>
                              )}

                              {/* Verified Organizations */}
                              {msg.citations.organizations && msg.citations.organizations.length > 0 && (
                                <div className="space-y-1.5 pt-1">
                                  <div className="flex items-center justify-between">
                                    <span className="font-bold text-slate-700 dark:text-slate-300 text-[11px] uppercase tracking-wider flex items-center gap-1.5">
                                      <Building2 size={12} className="text-slate-500" />
                                      <span>Verified Organization Performers:</span>
                                    </span>
                                    <Link to="/organizations" className="text-[10.5px] font-semibold text-blue-600 dark:text-blue-400 hover:underline">
                                      Organization Directory &rarr;
                                    </Link>
                                  </div>
                                  <div className="space-y-1">
                                    {msg.citations.organizations.slice(0, 3).map(org => (
                                      <div key={org.id} className="flex items-center justify-between p-2 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-[11.5px]">
                                        <span className="truncate text-slate-800 dark:text-slate-200 font-medium">
                                          {org.name} <span className="text-slate-400">({org.state || 'US'})</span> · <span className="text-slate-500 dark:text-slate-400 text-[11px]">{org.primary_technology || org.sector || 'Clean Tech'}</span>
                                        </span>
                                        <span className="font-mono font-semibold text-slate-700 dark:text-slate-300 shrink-0 ml-2 bg-slate-100 dark:bg-slate-800 px-1.5 py-0.2 rounded border border-slate-200 dark:border-slate-700 text-[10.5px]">
                                          {org.total_funding ? `$${(org.total_funding / 1e6).toFixed(1)}M` : `${org.awards_count || 1} awards`}
                                        </span>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}

                              {/* Deep Dive Action Links */}
                              <div className="pt-2 border-t border-slate-200 dark:border-slate-700 flex flex-wrap items-center gap-2 text-[11px]">
                                <span className="text-slate-400 font-medium">Explore Database:</span>
                                <Link to="/awards" className="px-2 py-0.5 rounded-md bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:border-slate-400 text-slate-700 dark:text-slate-300 font-medium transition-colors">
                                  GIS Map Studio
                                </Link>
                                <Link to="/sankey" className="px-2 py-0.5 rounded-md bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:border-slate-400 text-slate-700 dark:text-slate-300 font-medium transition-colors">
                                  Sankey Flow
                                </Link>
                                <Link to="/reports" className="px-2 py-0.5 rounded-md bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:border-slate-400 text-slate-700 dark:text-slate-300 font-medium transition-colors">
                                  Executive Monographs
                                </Link>
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Clean Message Action Bar */}
                      {!msg.isStreaming && (
                        <div className="flex items-center gap-3 pt-1 text-[11.5px] text-slate-400">
                          <button
                            type="button"
                            onClick={() => handleCopy(msg.id, msg.content)}
                            className="hover:text-slate-700 dark:hover:text-slate-200 transition-colors flex items-center gap-1 cursor-pointer"
                          >
                            {copiedId === msg.id ? <Check size={12} className="text-emerald-600" /> : <Copy size={12} />}
                            <span>{copiedId === msg.id ? 'Copied' : 'Copy'}</span>
                          </button>
                          <Link
                            to="/reports"
                            className="hover:text-slate-700 dark:hover:text-slate-200 transition-colors flex items-center gap-1"
                          >
                            <FileText size={12} />
                            <span>Export Monograph</span>
                          </Link>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Floating Bottom Input Capsule (ChatGPT-Style) */}
      <div className="p-4 bg-gradient-to-t from-white via-white dark:from-slate-900 dark:via-slate-900 to-transparent shrink-0">
        <div className="max-w-3xl mx-auto">
          <form
            onSubmit={e => {
              e.preventDefault();
              handleSend();
            }}
            className="relative rounded-2xl bg-slate-50 dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700 focus-within:border-slate-500 focus-within:bg-white dark:focus-within:bg-slate-800 transition-all shadow-xs flex items-center px-4 py-2"
          >
            <textarea
              ref={textareaRef}
              rows={1}
              value={inputQuery}
              onChange={e => setInputQuery(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder={`Message Expert as ${currentRoleConfig.title}...`}
              className="flex-1 resize-none bg-transparent py-1.5 pr-10 text-[14px] text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-hidden max-h-[180px] leading-relaxed"
            />

            <button
              type="submit"
              disabled={isLoading || !inputQuery.trim()}
              className={`absolute right-3 bottom-2.5 w-8 h-8 rounded-lg flex items-center justify-center transition-all cursor-pointer ${
                isLoading || !inputQuery.trim()
                  ? 'bg-slate-200 dark:bg-slate-700 text-slate-400 cursor-not-allowed'
                  : 'bg-slate-900 dark:bg-slate-100 hover:bg-slate-800 dark:hover:bg-white text-white dark:text-slate-900 shadow-2xs'
              }`}
            >
              {isLoading ? (
                <RefreshCw size={14} className="animate-spin text-slate-400" />
              ) : (
                <ArrowUp size={16} strokeWidth={2.5} />
              )}
            </button>
          </form>

          <p className="text-center text-[11px] text-slate-400 dark:text-slate-500 mt-2">
            Expert answers are tailored for <strong className="text-slate-600 dark:text-slate-300">{currentRoleConfig.badge}</strong> and grounded in 56,413 verified awards.
          </p>
        </div>
      </div>
    </div>
  );
}
