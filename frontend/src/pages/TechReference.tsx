import React, { useState, useMemo, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Search, BatteryCharging, Sun, Atom, Flame, Network, Factory,
  Wind, Home, Truck, Layers, Cpu, ShieldCheck, ArrowRight,
  ExternalLink, Sparkles, CheckCircle2, AlertTriangle, Clock,
  DollarSign, Trophy, FileText, ChevronRight, ChevronDown, Activity, Info,
  TrendingUp, TrendingDown, Award, Building2, Lightbulb, RefreshCw, Send,
  HelpCircle, Compass, BarChart3, Sliders, Target, Zap, Grid, List, X,
  ArrowUpRight, Gauge, Fuel, Droplets, FlaskConical, Scale, Split,
  SlidersHorizontal, Check, Plus, Minus, Share2, Copy, Workflow
} from 'lucide-react';
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, Tooltip as RechartsTooltip,
  ScatterChart, Scatter, XAxis, YAxis, ZAxis, CartesianGrid, Cell, Legend
} from 'recharts';
import clsx from 'clsx';
import {
  api, TechCategory, TechSummary, TechDossier, TechAIInsights,
  FuelsMatrixItem, FrontierMatrixItem, TechSubsystemNode,
  TechnologyBankabilityRating
} from '../api/client';
import { TechSystemDiagram } from '../components/TechSystemDiagram';
import { useNyserda } from '../context/NyserdaContext';

// Category Icon Mapping Helper
function getCategoryIcon(iconName: string, size = 18, className = '') {
  switch (iconName) {
    case 'BatteryCharging': return <BatteryCharging size={size} className={className} />;
    case 'Sun': return <Sun size={size} className={className} />;
    case 'Atom': return <Atom size={size} className={className} />;
    case 'Flame': return <Flame size={size} className={className} />;
    case 'Network': return <Network size={size} className={className} />;
    case 'Factory': return <Factory size={size} className={className} />;
    case 'Wind': return <Wind size={size} className={className} />;
    case 'Home': return <Home size={size} className={className} />;
    case 'Truck': return <Truck size={size} className={className} />;
    case 'Layers': return <Layers size={size} className={className} />;
    case 'Cpu': return <Cpu size={size} className={className} />;
    case 'ShieldCheck': return <ShieldCheck size={size} className={className} />;
    default: return <Zap size={size} className={className} />;
  }
}

function getTRLBadgeColor(trl: number) {
  if (trl <= 4) return 'bg-purple-500/15 text-purple-300 border-purple-500/30';
  if (trl <= 6) return 'bg-amber-500/15 text-amber-300 border-amber-500/30';
  if (trl <= 8) return 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30';
  return 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30';
}

function getStatusBadge(status: string) {
  switch (status) {
    case 'achieved':
      return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10.5px] font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">Achieved</span>;
    case 'on_track':
      return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10.5px] font-semibold bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">On Track</span>;
    case 'challenging':
      return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10.5px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30">Frontier Barrier</span>;
    default:
      return null;
  }
}

const SECTOR_COLORS: Record<string, string> = {
  solar_systems: '#f59e0b',
  wind_systems: '#0284c7',
  hydro_marine: '#2563eb',
  geothermal_subsurface: '#dc2626',
  energy_storage: '#ea580c',
  grid_modernization: '#6366f1',
  clean_hydrogen: '#06b6d4',
  bioenergy_waste: '#10b981',
  advanced_nuclear: '#8b5cf6',
  industrial_decarb: '#e11d48',
  buildings_thermal: '#0d9488',
  clean_transportation: '#84cc16',
  carbon_management: '#78716c',
  critical_minerals: '#eab308',
  ai_datacenter: '#d946ef'
};

// ─── Brandon Owens Technology Bankability Rating (TBR) & Causal Lineage ─────

function TechBankabilityCard({ techId, techName }: { techId: string; techName: string }) {
  const { data: bankability } = useQuery<TechnologyBankabilityRating>({
    queryKey: ['tech-bankability', techId],
    queryFn: () => api.getTechnologyBankability(techId),
    staleTime: 10 * 60 * 1000,
  });

  if (!bankability) return null;

  return (
    <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 border border-indigo-500/30 shadow-2xl space-y-6 text-white">
      {/* Header Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-5 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/20 border border-cyan-400/40 text-cyan-300 text-[11px] font-bold uppercase tracking-wider flex items-center gap-1.5">
              <ShieldCheck size={12} className="text-cyan-400" />
              Brandon Owens Bankability Rating (TBR)
            </span>
            <span className={clsx(
              'px-2.5 py-0.5 rounded-full text-xs font-black font-mono border',
              bankability.grade_color === 'emerald' && 'bg-emerald-500/20 text-emerald-300 border-emerald-400/40',
              bankability.grade_color === 'teal' && 'bg-teal-500/20 text-teal-300 border-teal-400/40',
              bankability.grade_color === 'blue' && 'bg-blue-500/20 text-blue-300 border-blue-400/40',
              bankability.grade_color === 'amber' && 'bg-amber-500/20 text-amber-300 border-amber-400/40',
              bankability.grade_color === 'rose' && 'bg-rose-500/20 text-rose-300 border-rose-400/40'
            )}>
              Grade: {bankability.rating_grade} ({bankability.bankability_score}/100)
            </span>
            <span className="text-xs text-slate-300 font-medium">
              {bankability.grade_label}
            </span>
          </div>
          <h3 className="text-xl font-bold text-white mt-1">
            Institutional Diligence &amp; Commercial Bankability Scorecard
          </h3>
          <p className="text-xs text-slate-300 max-w-3xl mt-1 leading-relaxed">
            {bankability.executive_diligence_brief}
          </p>
        </div>

        <div className="flex items-center gap-3 bg-white/5 p-3.5 rounded-2xl border border-white/10 shrink-0 text-right font-mono">
          <div>
            <div className="text-[10px] uppercase font-bold text-slate-400">Private Capital Leverage</div>
            <div className="text-2xl font-black text-cyan-300">{bankability.empirical_leverage_ratio}</div>
            <div className="text-[10px] text-slate-400">{bankability.tracked_award_precedents} Precedent Awards</div>
          </div>
        </div>
      </div>

      {/* 4 Analytical Pillars Grid */}
      <div>
        <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-1.5">
          <Layers size={13} className="text-cyan-400" />
          4-Pillar Bankability Methodology
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {bankability.pillars.map((pillar) => (
            <div key={pillar.pillar_number} className="p-4 rounded-2xl bg-white/[0.04] border border-white/[0.08] space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-[10px] uppercase font-bold text-slate-400">Pillar {pillar.pillar_number} ({pillar.weight_pct}%)</span>
                <span className="font-mono font-bold text-cyan-300 text-sm">{pillar.score}/100</span>
              </div>
              <div className="font-bold text-sm text-white">{pillar.name}</div>
              <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-cyan-500 to-indigo-500 rounded-full" style={{ width: `${pillar.score}%` }} />
              </div>
              <div className="text-[11px] text-slate-300 pt-1 leading-tight">{pillar.rating}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Causal Lineage Continuum */}
      {bankability.causal_lineage?.length > 0 && (
        <div className="pt-2">
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <Workflow size={13} className="text-emerald-400" />
            Causal Innovation Genome &amp; Commercialization Lineage
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {bankability.causal_lineage.map((node) => (
              <div
                key={node.step}
                className={clsx(
                  'p-4 rounded-2xl border transition-all space-y-2',
                  node.completed
                    ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-100'
                    : 'bg-white/[0.03] border-white/[0.06] text-slate-300'
                )}
              >
                <div className="flex items-center justify-between text-[10.5px] font-bold uppercase tracking-wider">
                  <span className={node.completed ? 'text-emerald-400' : 'text-slate-400'}>
                    Step {node.step}: {node.stage}
                  </span>
                  {node.completed ? (
                    <span className="px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 text-[9.5px] font-bold">VERIFIED</span>
                  ) : (
                    <span className="px-1.5 py-0.2 rounded bg-white/10 text-slate-400 text-[9.5px] font-bold">FRONTIER</span>
                  )}
                </div>
                <div className="text-xs font-bold text-white">{node.mechanism}</div>
                <div className="text-[11px] text-slate-400">{node.entity}</div>
                <p className="text-[11px] opacity-80 pt-1 leading-snug">{node.output}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function TechReference() {
  const { includeNyserda } = useNyserda();
  const { id: paramTechId } = useParams<{ id?: string }>();
  const navigate = useNavigate();

  // Primary Navigation Mode: 'explorer' | 'comparison' | 'fuels_matrix' | 'frontier_matrix' | 'regulatory_matrix' | 'lab_facilities' | 'der_benchmarks'
  const [viewMode, setViewMode] = useState<'explorer' | 'comparison' | 'fuels_matrix' | 'frontier_matrix' | 'regulatory_matrix' | 'lab_facilities' | 'der_benchmarks'>('explorer');

  // Filters & State
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedVectorType, setSelectedVectorType] = useState<'all' | 'hardware' | 'fuel_carrier'>('all');
  const [selectedTrlTier, setSelectedTrlTier] = useState<'all' | 'early' | 'pilot' | 'commercial'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Dossier Tabs
  const [activeTab, setActiveTab] = useState<'overview' | 'architecture' | 'frontier' | 'evidence' | 'tradeoffs' | 'policies' | 'ai'>('overview');
  const [policyCategoryFilter, setPolicyCategoryFilter] = useState<string>('all');
  const [policySubView, setPolicySubView] = useState<'standards' | 'proceedings'>('standards');
  const [aiQuestion, setAiQuestion] = useState('');
  const [customApiKey, setCustomApiKey] = useState('');
  const [isSectorGridModalOpen, setIsSectorGridModalOpen] = useState(false);
  const [sidebarViewMode, setSidebarViewMode] = useState<'grouped' | 'flat'>('grouped');
  const [expandedSectors, setExpandedSectors] = useState<Record<string, boolean>>({});

  // Comparison Multi-Select Tray (Array of technology IDs, max 4)
  const [comparisonIds, setComparisonIds] = useState<string[]>(['iron_air_battery', 'vanadium_redox_flow', 'sodium_ion_battery']);

  // 1. Fetch Categories
  const { data: categories = [] } = useQuery({
    queryKey: ['tech-categories'],
    queryFn: () => api.getTechCategories(),
    staleTime: 10 * 60 * 1000
  });

  // 2. Fetch All Technologies List
  const { data: allTechnologies = [], isLoading: isLoadingList } = useQuery({
    queryKey: ['tech-list', selectedCategory, searchQuery, selectedVectorType],
    queryFn: () => api.getTechnologies({
      category_id: selectedCategory || undefined,
      search: searchQuery || undefined,
      vector_type: selectedVectorType !== 'all' ? selectedVectorType : undefined
    }),
    staleTime: 5 * 60 * 1000
  });

  // Filter list by TRL tier
  const filteredTechnologies = useMemo(() => {
    return allTechnologies.filter(t => {
      if (selectedTrlTier === 'early') return t.trl_current <= 6;
      if (selectedTrlTier === 'pilot') return t.trl_current >= 7 && t.trl_current <= 8;
      if (selectedTrlTier === 'commercial') return t.trl_current >= 9;
      return true;
    });
  }, [allTechnologies, selectedTrlTier]);

  // Group technologies by sector
  const technologiesByCategory = useMemo(() => {
    const map: Record<string, TechSummary[]> = {};
    filteredTechnologies.forEach(t => {
      if (!map[t.category_id]) map[t.category_id] = [];
      map[t.category_id].push(t);
    });
    return map;
  }, [filteredTechnologies]);

  // Determine active technology ID for dossier view
  const activeTechId = useMemo(() => {
    if (paramTechId) return paramTechId;
    if (filteredTechnologies.length > 0) return filteredTechnologies[0].id;
    return 'iron_air_battery';
  }, [paramTechId, filteredTechnologies]);

  // 3. Fetch Selected Technology Dossier
  const { data: dossier, isLoading: isLoadingDossier } = useQuery({
    queryKey: ['tech-dossier', activeTechId],
    queryFn: () => api.getTechnologyDossier(activeTechId),
    enabled: !!activeTechId && viewMode === 'explorer',
    staleTime: 5 * 60 * 1000
  });

  // 4. Fetch Applicable Policies & Dockets
  const { data: techPoliciesData } = useQuery({
    queryKey: ['tech-policies', activeTechId],
    queryFn: () => api.getPoliciesByTechnology(activeTechId),
    enabled: !!activeTechId && (viewMode === 'explorer' || viewMode === 'regulatory_matrix'),
    staleTime: 5 * 60 * 1000
  });

  const { data: techProceedingsData } = useQuery({
    queryKey: ['tech-proceedings', activeTechId],
    queryFn: () => api.getProceedingsByTechnology(activeTechId),
    enabled: !!activeTechId && (viewMode === 'explorer' || viewMode === 'regulatory_matrix'),
    staleTime: 5 * 60 * 1000
  });

  // 5. Fetch Comparative Technologies Data for Comparison Mode
  const { data: comparisonData, isLoading: isLoadingComparison } = useQuery({
    queryKey: ['tech-comparison', comparisonIds],
    queryFn: () => api.getComparativeTechnologies(comparisonIds),
    enabled: viewMode === 'comparison' && comparisonIds.length > 0,
    staleTime: 5 * 60 * 1000
  });

  // 6. Fetch Fuels & Molecular Pathways Matrix
  const { data: fuelsMatrix = [], isLoading: isLoadingFuels } = useQuery({
    queryKey: ['fuels-matrix'],
    queryFn: () => api.getFuelsMatrix(),
    enabled: viewMode === 'fuels_matrix',
    staleTime: 10 * 60 * 1000
  });

  // 7. Fetch Frontier Matrix for Scatter / Quadrant Visualizer
  const { data: frontierMatrix = [], isLoading: isLoadingFrontier } = useQuery({
    queryKey: ['frontier-matrix'],
    queryFn: () => api.getFrontierMatrix(),
    enabled: viewMode === 'frontier_matrix',
    staleTime: 10 * 60 * 1000
  });

  // 8. Fetch Global Policies & Proceedings for Regulatory Matrix Mode
  const { data: globalPoliciesData } = useQuery({
    queryKey: ['all-policies'],
    queryFn: () => api.getPolicies({ limit: 100 }),
    enabled: viewMode === 'regulatory_matrix',
    staleTime: 10 * 60 * 1000
  });

  const { data: globalProceedingsData } = useQuery({
    queryKey: ['all-proceedings'],
    queryFn: () => api.getRegulatoryProceedings({ limit: 100 }),
    enabled: viewMode === 'regulatory_matrix',
    staleTime: 10 * 60 * 1000
  });

  // 9. Fetch National Lab User Facilities & Testbeds
  const { data: labFacilitiesData, isLoading: isLoadingLabs } = useQuery({
    queryKey: ['national-lab-facilities'],
    queryFn: () => api.getLabFacilities({ limit: 50 }),
    enabled: viewMode === 'lab_facilities',
    staleTime: 10 * 60 * 1000
  });

  // 10. Fetch DER Empirical Installed Cost Benchmarks & Manufacturers
  const { data: derBenchmarksData, isLoading: isLoadingDer } = useQuery({
    queryKey: ['der-cost-benchmarks'],
    queryFn: () => api.getDerCostBenchmarks(),
    enabled: viewMode === 'der_benchmarks',
    staleTime: 10 * 60 * 1000
  });

  // Keep active category expanded in sidebar
  useEffect(() => {
    if (dossier?.category_id) {
      setExpandedSectors(prev => ({ ...prev, [dossier.category_id]: true }));
    }
  }, [dossier?.category_id]);

  const toggleSectorExpand = (catId: string) => {
    setExpandedSectors(prev => ({ ...prev, [catId]: !prev[catId] }));
  };

  // AI Insights Mutation
  const aiMutation = useMutation({
    mutationFn: (questionText: string) => api.getTechAIInsights(activeTechId, {
      custom_question: questionText,
      api_key: customApiKey || undefined,
      force_refresh: false
    })
  });

  const handleSelectTech = (techId: string) => {
    navigate(`/technologies/${techId}`);
    if (viewMode !== 'explorer') setViewMode('explorer');
  };

  const toggleCompareTech = (techId: string) => {
    setComparisonIds(prev => {
      if (prev.includes(techId)) {
        return prev.filter(id => id !== techId);
      }
      if (prev.length >= 4) {
        return [...prev.slice(1), techId];
      }
      return [...prev, techId];
    });
  };

  const handleRunAiDiligence = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    aiMutation.mutate(aiQuestion || 'Provide an executive technology and fuel pathway diligence briefing with frontier risk assessment.');
  };

  return (
    <div className="flex flex-col h-full bg-[#080c14] text-slate-100 overflow-y-auto pb-16 selection:bg-cyan-500/20 selection:text-cyan-200">
      
      {/* ── SECTOR EXPLORER MODAL / GRID DRAWER ─────────────────────── */}
      {isSectorGridModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
          <div className="bg-[#0b101b] border border-white/10 rounded-3xl w-full max-w-6xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden text-white">
            <div className="p-6 border-b border-white/10 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                    Technology & Fuels Sector Directory
                  </span>
                  <span className="text-xs text-slate-400 font-mono">15 Canonical Innovation Sectors</span>
                </div>
                <h2 className="text-xl font-black text-white mt-1">
                  Select a Clean Tech or Fuel Innovation Sector
                </h2>
              </div>
              <button
                onClick={() => setIsSectorGridModalOpen(false)}
                className="p-2 rounded-xl bg-white/10 hover:bg-white/20 text-slate-300 hover:text-white transition-all cursor-pointer"
              >
                <X size={20} />
              </button>
            </div>

            <div className="p-6 overflow-y-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {categories.map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => {
                    setSelectedCategory(cat.id);
                    setIsSectorGridModalOpen(false);
                  }}
                  className="p-4 rounded-2xl bg-white/[0.03] hover:bg-white/[0.08] border border-white/[0.08] hover:border-cyan-400/40 text-left transition-all group flex flex-col justify-between"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="p-2.5 rounded-xl bg-white/[0.05] group-hover:bg-cyan-500/20 text-cyan-300 transition-colors">
                      {getCategoryIcon(cat.icon, 20)}
                    </div>
                    <span className="text-[11px] font-mono text-slate-500 uppercase font-semibold">
                      {cat.id.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="mt-4">
                    <h3 className="text-sm font-bold text-white group-hover:text-cyan-300 transition-colors">
                      {cat.name}
                    </h3>
                    <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                      {cat.description}
                    </p>
                  </div>
                </button>
              ))}
            </div>

            <div className="p-4 border-t border-white/10 bg-white/[0.02] flex justify-end">
              <button
                onClick={() => {
                  setSelectedCategory(null);
                  setIsSectorGridModalOpen(false);
                }}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white hover:bg-white/10 transition-all cursor-pointer"
              >
                Clear Sector Filter
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── MASTER TERMINAL HERO & TELEMETRY CONTROL BAR ──────────────── */}
      <div className="px-6 py-5 border-b border-white/[0.08] bg-[#070a12]/90 backdrop-blur-md shrink-0">
        <div className="max-w-7xl mx-auto space-y-4">
          
          {/* Top Title & Live Telemetry Ticker */}
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div>
              <div className="flex items-center gap-2.5 flex-wrap">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-mono font-bold uppercase tracking-wider bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  National Clean Tech &amp; Fuels Corpus
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  {includeNyserda ? 'DOE · NYSERDA · CEC · ARPA-E · NSF · 140+ Utilities' : 'DOE · CEC · ARPA-E · NSF · 140+ Utilities'}
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-white mt-1.5 flex items-center gap-3">
                <span>Technology &amp; Fuels Innovation Reference</span>
                <span className="text-xs font-mono px-2.5 py-0.5 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  2026–2035 Horizon
                </span>
              </h1>
            </div>

            {/* Live Corpus Macro Stats Badge */}
            <div className="flex items-center gap-2.5 overflow-x-auto no-scrollbar py-1">
              <div className="px-3.5 py-2 rounded-xl bg-white/[0.04] border border-white/[0.08] flex items-center gap-2 shrink-0">
                <Layers size={14} className="text-cyan-400" />
                <div>
                  <div className="text-[10px] text-slate-400 font-mono uppercase">Sectors</div>
                  <div className="text-xs font-bold text-white">15 Verticals</div>
                </div>
              </div>
              <div className="px-3.5 py-2 rounded-xl bg-white/[0.04] border border-white/[0.08] flex items-center gap-2 shrink-0">
                <Atom size={14} className="text-purple-400" />
                <div>
                  <div className="text-[10px] text-slate-400 font-mono uppercase">Engines &amp; Fuels</div>
                  <div className="text-xs font-bold text-white">36 Pathways</div>
                </div>
              </div>
              <div className="px-3.5 py-2 rounded-xl bg-white/[0.04] border border-white/[0.08] flex items-center gap-2 shrink-0">
                <DollarSign size={14} className="text-emerald-400" />
                <div>
                  <div className="text-[10px] text-slate-400 font-mono uppercase">Tracked Grants</div>
                  <div className="text-xs font-bold text-emerald-300">$104.16B USD</div>
                </div>
              </div>
              <div className="px-3.5 py-2 rounded-xl bg-white/[0.04] border border-white/[0.08] flex items-center gap-2 shrink-0">
                <Scale size={14} className="text-amber-400" />
                <div>
                  <div className="text-[10px] text-slate-400 font-mono uppercase">Codes &amp; Dockets</div>
                  <div className="text-xs font-bold text-amber-300">23 / 15 PUC</div>
                </div>
              </div>
            </div>
          </div>

          {/* ── 5 MASTER VIEW MODE SWITCHER TABS ────────────────────────── */}
          <div className="flex items-center justify-between gap-3 flex-wrap pt-1 border-t border-white/[0.06]">
            <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar p-1 rounded-xl bg-black/40 border border-white/[0.08]">
              <button
                onClick={() => setViewMode('explorer')}
                className={`px-3.5 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 cursor-pointer shrink-0 ${
                  viewMode === 'explorer'
                    ? 'bg-gradient-to-r from-cyan-500/20 to-emerald-500/20 text-white border border-cyan-400/40 shadow-xs'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
                }`}
              >
                <FileText size={14} className={viewMode === 'explorer' ? 'text-cyan-300' : 'text-slate-400'} />
                <span>Sector &amp; Technology Dossier Explorer</span>
              </button>

              <button
                onClick={() => setViewMode('comparison')}
                className={`px-3.5 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 cursor-pointer shrink-0 ${
                  viewMode === 'comparison'
                    ? 'bg-gradient-to-r from-purple-500/20 to-cyan-500/20 text-white border border-purple-400/40 shadow-xs'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
                }`}
              >
                <Split size={14} className={viewMode === 'comparison' ? 'text-purple-300' : 'text-slate-400'} />
                <span>Side-by-Side Comparison Matrix</span>
                {comparisonIds.length > 0 && (
                  <span className="px-1.5 py-0.2 rounded-full text-[10px] font-mono font-bold bg-purple-500/30 text-purple-200">
                    {comparisonIds.length}
                  </span>
                )}
              </button>

              <button
                onClick={() => setViewMode('fuels_matrix')}
                className={`px-3.5 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 cursor-pointer shrink-0 ${
                  viewMode === 'fuels_matrix'
                    ? 'bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 text-white border border-emerald-400/40 shadow-xs'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
                }`}
              >
                <Fuel size={14} className={viewMode === 'fuels_matrix' ? 'text-emerald-300' : 'text-slate-400'} />
                <span>Zero-Carbon Fuels &amp; Molecules Matrix</span>
              </button>

              <button
                onClick={() => setViewMode('frontier_matrix')}
                className={`px-3.5 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 cursor-pointer shrink-0 ${
                  viewMode === 'frontier_matrix'
                    ? 'bg-gradient-to-r from-amber-500/20 to-orange-500/20 text-white border border-amber-400/40 shadow-xs'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
                }`}
              >
                <Compass size={14} className={viewMode === 'frontier_matrix' ? 'text-amber-300' : 'text-slate-400'} />
                <span>Innovation Frontier &amp; TRL Quadrant Map</span>
              </button>

              <button
                onClick={() => setViewMode('regulatory_matrix')}
                className={`px-3.5 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 cursor-pointer shrink-0 ${
                  viewMode === 'regulatory_matrix'
                    ? 'bg-gradient-to-r from-blue-500/20 to-indigo-500/20 text-white border border-blue-400/40 shadow-xs'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
                }`}
              >
                <Scale size={14} className={viewMode === 'regulatory_matrix' ? 'text-blue-300' : 'text-slate-400'} />
                <span>Regulatory &amp; Policy Reference Matrix</span>
              </button>

              <button
                onClick={() => setViewMode('lab_facilities')}
                className={`px-3.5 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 cursor-pointer shrink-0 ${
                  viewMode === 'lab_facilities'
                    ? 'bg-gradient-to-r from-teal-500/20 to-cyan-500/20 text-white border border-teal-400/40 shadow-xs'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
                }`}
              >
                <FlaskConical size={14} className={viewMode === 'lab_facilities' ? 'text-teal-300' : 'text-slate-400'} />
                <span>National Lab Validation Testbeds</span>
              </button>

              <button
                onClick={() => setViewMode('der_benchmarks')}
                className={`px-3.5 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 cursor-pointer shrink-0 ${
                  viewMode === 'der_benchmarks'
                    ? 'bg-gradient-to-r from-emerald-500/20 to-amber-500/20 text-white border border-emerald-400/40 shadow-xs'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
                }`}
              >
                <BarChart3 size={14} className={viewMode === 'der_benchmarks' ? 'text-emerald-300' : 'text-slate-400'} />
                <span>Installed Cost Curves &amp; OEM Shares</span>
              </button>
            </div>

            {/* Quick Sector Browse Drawer Button */}
            <button
              onClick={() => setIsSectorGridModalOpen(true)}
              className="px-3.5 py-2 rounded-xl bg-white/[0.06] hover:bg-white/[0.12] border border-white/10 text-xs font-bold text-slate-200 hover:text-white transition-all flex items-center gap-2 cursor-pointer"
            >
              <Grid size={13} className="text-cyan-400" />
              <span>15 Sector Directory</span>
            </button>
          </div>
        </div>
      </div>

      {/* ── VIEW MODE A: SECTOR & TECHNOLOGY DOSSIER EXPLORER ─────────────── */}
      {viewMode === 'explorer' && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 w-full flex-1 flex flex-col lg:flex-row gap-6 items-start">
          
          {/* Left Taxonomy & Navigation Sidebar */}
          <aside className="w-full lg:w-80 shrink-0 flex flex-col gap-4">
            
            {/* Search and Filters Box */}
            <div className="p-4 rounded-2xl bg-[#0b101b] border border-white/[0.08] shadow-xl space-y-3">
              <div className="relative">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search 36 clean tech & fuels..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-8 py-2 rounded-xl bg-white/[0.04] border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400/60 focus:bg-white/[0.06] transition-all"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                  >
                    <X size={13} />
                  </button>
                )}
              </div>

              {/* Vector Type Filter Pills */}
              <div className="flex items-center gap-1 bg-black/40 p-1 rounded-xl border border-white/[0.06]">
                <button
                  onClick={() => setSelectedVectorType('all')}
                  className={`flex-1 py-1 text-[11px] font-bold rounded-lg transition-all ${
                    selectedVectorType === 'all' ? 'bg-white/15 text-white shadow-xs' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  All ({allTechnologies.length})
                </button>
                <button
                  onClick={() => setSelectedVectorType('hardware')}
                  className={`flex-1 py-1 text-[11px] font-bold rounded-lg transition-all ${
                    selectedVectorType === 'hardware' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Hardware
                </button>
                <button
                  onClick={() => setSelectedVectorType('fuel_carrier')}
                  className={`flex-1 py-1 text-[11px] font-bold rounded-lg transition-all ${
                    selectedVectorType === 'fuel_carrier' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Fuels
                </button>
              </div>

              {/* TRL Tier Filter Buttons */}
              <div className="flex items-center gap-1 text-[10.5px]">
                <span className="text-slate-500 font-mono text-[10px] uppercase font-semibold">TRL:</span>
                {(['all', 'early', 'pilot', 'commercial'] as const).map(tier => (
                  <button
                    key={tier}
                    onClick={() => setSelectedTrlTier(tier)}
                    className={`px-2 py-0.5 rounded-lg font-medium transition-all ${
                      selectedTrlTier === tier
                        ? 'bg-white/20 text-white font-bold'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
                    }`}
                  >
                    {tier === 'all' ? 'All' : tier === 'early' ? '4–6' : tier === 'pilot' ? '7–8' : '9'}
                  </button>
                ))}
              </div>

              {/* Active Sector Chip if filtered */}
              {selectedCategory && (
                <div className="flex items-center justify-between px-2.5 py-1.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-xs">
                  <span className="truncate font-medium">{categories.find(c => c.id === selectedCategory)?.name}</span>
                  <button
                    onClick={() => setSelectedCategory(null)}
                    className="hover:text-white shrink-0 ml-2"
                  >
                    <X size={13} />
                  </button>
                </div>
              )}
            </div>

            {/* List / Grouped Directory */}
            <div className="p-3 rounded-2xl bg-[#0b101b] border border-white/[0.08] shadow-xl max-h-[calc(100vh-320px)] overflow-y-auto no-scrollbar space-y-2">
              <div className="px-2 py-1 flex items-center justify-between text-[11px] text-slate-400 border-b border-white/[0.06] pb-2">
                <span className="font-mono uppercase text-[10px] tracking-wider text-slate-400">Canonical Taxonomy</span>
                <span className="font-mono text-cyan-400 font-bold">{filteredTechnologies.length} Technologies</span>
              </div>

              {categories.map((cat) => {
                const techsInCat = technologiesByCategory[cat.id] || [];
                if (techsInCat.length === 0 && selectedCategory) return null;
                const isExpanded = expandedSectors[cat.id] ?? true;

                return (
                  <div key={cat.id} className="space-y-1">
                    <button
                      onClick={() => toggleSectorExpand(cat.id)}
                      className="w-full px-2.5 py-1.5 rounded-xl hover:bg-white/[0.04] text-xs font-bold text-slate-300 flex items-center justify-between group cursor-pointer transition-colors"
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        <span style={{ color: SECTOR_COLORS[cat.id] || '#06b6d4' }}>
                          {getCategoryIcon(cat.icon, 14)}
                        </span>
                        <span className="truncate text-left">{cat.name}</span>
                      </div>
                      <div className="flex items-center gap-1.5 shrink-0">
                        <span className="text-[10px] font-mono text-slate-400 font-normal">
                          {techsInCat.length}
                        </span>
                        {isExpanded ? (
                          <ChevronDown size={13} className="text-slate-400" />
                        ) : (
                          <ChevronRight size={13} className="text-slate-400" />
                        )}
                      </div>
                    </button>

                    {isExpanded && techsInCat.length > 0 && (
                      <div className="space-y-0.5 pl-3 border-l border-white/[0.06] ml-3 my-1">
                        {techsInCat.map((t) => {
                          const isSelected = t.id === activeTechId;
                          const isCompared = comparisonIds.includes(t.id);

                          return (
                            <div
                              key={t.id}
                              className={`group relative flex items-center justify-between px-2.5 py-2 rounded-xl text-xs transition-all cursor-pointer ${
                                isSelected
                                  ? 'bg-cyan-500/15 text-white font-bold border border-cyan-400/40 shadow-xs'
                                  : 'text-slate-300 hover:bg-white/[0.05] hover:text-white'
                              }`}
                              onClick={() => handleSelectTech(t.id)}
                            >
                              <div className="flex flex-col min-w-0 pr-2">
                                <span className="truncate">{t.name}</span>
                                <div className="flex items-center gap-1.5 mt-0.5">
                                  <span className={`px-1.5 py-0.2 rounded text-[9.5px] font-mono font-bold border ${getTRLBadgeColor(t.trl_current)}`}>
                                    TRL {t.trl_current}
                                  </span>
                                  {t.vector_type === 'fuel_carrier' && (
                                    <span className="px-1.5 py-0.2 rounded text-[9.5px] font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                                      Fuel
                                    </span>
                                  )}
                                </div>
                              </div>

                              {/* Quick Compare Toggle Button */}
                              <button
                                type="button"
                                title={isCompared ? "Remove from comparison" : "Add to comparison"}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  toggleCompareTech(t.id);
                                }}
                                className={`p-1 rounded-md transition-all ${
                                  isCompared
                                    ? 'bg-purple-500/30 text-purple-200 border border-purple-400/40'
                                    : 'opacity-0 group-hover:opacity-100 hover:bg-white/10 text-slate-400 hover:text-white'
                                }`}
                              >
                                <Split size={12} />
                              </button>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </aside>

          {/* Main Technology Dossier View Pane */}
          <main className="flex-1 min-w-0 w-full space-y-6">
            {isLoadingDossier ? (
              <div className="p-12 rounded-3xl bg-[#0b101b] border border-white/[0.08] flex flex-col items-center justify-center gap-3 text-slate-400">
                <RefreshCw size={24} className="animate-spin text-cyan-400" />
                <span className="text-sm font-mono">Synthesizing live technology intelligence...</span>
              </div>
            ) : !dossier ? (
              <div className="p-12 rounded-3xl bg-[#0b101b] border border-white/[0.08] text-center text-slate-400">
                <AlertTriangle size={32} className="mx-auto text-amber-400 mb-2" />
                <h3 className="text-base font-bold text-white">Technology Not Found</h3>
                <p className="text-xs text-slate-400 mt-1">Please select an innovation vector from the left directory.</p>
              </div>
            ) : (
              <>
                {/* ── DOSSIER HERO HEADER CARD ────────────────────────────── */}
                <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-br from-[#0c1322] via-[#0b101b] to-[#080c14] border border-white/10 shadow-2xl space-y-5">
                  <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                    <div className="space-y-2 max-w-3xl">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="px-3 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 flex items-center gap-1.5">
                          {getCategoryIcon(categories.find(c => c.id === dossier.category_id)?.icon || 'Zap', 13)}
                          {dossier.category_name}
                        </span>
                        {dossier.vector_type === 'fuel_carrier' && (
                          <span className="px-3 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                            <Fuel size={12} />
                            Zero-Carbon Fuel Carrier
                          </span>
                        )}
                        <span className="text-xs text-slate-400 font-mono">
                          Vector: <span className="text-slate-200">{dossier.fuel_vector}</span>
                        </span>
                      </div>

                      <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                        {dossier.name}
                      </h2>
                      <p className="text-sm sm:text-base text-slate-300 font-medium leading-relaxed">
                        {dossier.headline}
                      </p>
                    </div>

                    {/* Action Bar (Compare, AI Diligence) */}
                    <div className="flex items-center gap-2 shrink-0">
                      <button
                        onClick={() => {
                          if (!comparisonIds.includes(dossier.id)) {
                            setComparisonIds(prev => [...prev, dossier.id].slice(-4));
                          }
                          setViewMode('comparison');
                        }}
                        className="px-3.5 py-2 rounded-xl bg-purple-500/20 hover:bg-purple-500/30 text-purple-200 border border-purple-500/30 text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer"
                      >
                        <Split size={14} />
                        <span>Compare Matrix</span>
                      </button>
                    </div>
                  </div>

                  {/* TRL Horizon Stepper */}
                  <div className="pt-4 border-t border-white/[0.08]">
                    <div className="flex items-center justify-between text-xs mb-2">
                      <span className="font-mono uppercase text-slate-400 font-bold">Technology Readiness Progression</span>
                      <span className="font-mono text-cyan-300 font-bold">
                        Current: TRL {dossier.trl_current} → Target 2030: TRL {dossier.trl_target}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-4 gap-2">
                      {dossier.trl_progression.map((stage, sIdx) => {
                        const isCurrent = (sIdx === 0 && dossier.trl_current <= 3) ||
                          (sIdx === 1 && dossier.trl_current >= 4 && dossier.trl_current <= 6) ||
                          (sIdx === 2 && dossier.trl_current >= 7 && dossier.trl_current <= 8) ||
                          (sIdx === 3 && dossier.trl_current >= 9);

                        return (
                          <div
                            key={stage.stage}
                            className={`p-3 rounded-2xl border transition-all ${
                              isCurrent
                                ? 'bg-cyan-500/15 border-cyan-400/50 shadow-[0_0_15px_rgba(6,182,212,0.15)]'
                                : stage.active
                                ? 'bg-white/[0.04] border-white/10'
                                : 'bg-black/30 border-white/[0.04] opacity-50'
                            }`}
                          >
                            <div className="flex items-center justify-between text-[11px] mb-1">
                              <span className={`font-bold ${isCurrent ? 'text-cyan-300' : 'text-slate-300'}`}>
                                {stage.stage.split(':')[0]}
                              </span>
                              {stage.active && (
                                <CheckCircle2 size={12} className={isCurrent ? 'text-cyan-400' : 'text-emerald-400'} />
                              )}
                            </div>
                            <p className="text-[10.5px] text-slate-400 line-clamp-2 leading-snug">
                              {stage.description}
                            </p>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* DOE Earthshot & Cost/Performance Highlight Banner */}
                  {dossier.cost_performance && (
                    <div className="p-4 rounded-2xl bg-white/[0.03] border border-white/[0.08] flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <Target size={14} className="text-amber-400" />
                          <span className="text-[11px] font-mono uppercase font-bold text-amber-300">
                            DOE Decarbonization Earthshot Alignment
                          </span>
                        </div>
                        <p className="text-xs font-semibold text-white">
                          {dossier.cost_performance.earthshot_goal}
                        </p>
                      </div>

                      <div className="flex items-center gap-4 shrink-0 font-mono">
                        <div className="text-right">
                          <div className="text-[10px] text-slate-400 uppercase">Learning Rate</div>
                          <div className="text-xs font-bold text-cyan-300">{dossier.cost_performance.learning_rate}</div>
                        </div>
                        <div className="h-8 w-px bg-white/10" />
                        <div className="text-right">
                          <div className="text-[10px] text-slate-400 uppercase">Cost Reduction 2030</div>
                          <div className="text-xs font-bold text-emerald-400">{dossier.cost_performance.cost_metric.reduction_pct}</div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* ── 7 DOSSIER INTELLIGENCE TABS ─────────────────────────── */}
                <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar border-b border-white/10 pb-2">
                  {[
                    { id: 'overview', label: 'Mechanical & Molecular Fundamentals', icon: Atom },
                    { id: 'architecture', label: 'Explorable Subsystem Architecture', icon: Workflow },
                    { id: 'frontier', label: 'Innovation Frontier & R&D Tracks', icon: Target },
                    { id: 'evidence', label: 'Empirical Capital & Solicitations ($104.16B)', icon: DollarSign },
                    { id: 'tradeoffs', label: '6D Radar & Trade-Offs', icon: Gauge },
                    { id: 'policies', label: 'Codes, Standards & PUC Dockets', icon: Scale },
                    { id: 'ai', label: 'AI Diligence Specialist Copilot', icon: Sparkles },
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id as any)}
                      className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer shrink-0 ${
                        activeTab === tab.id
                          ? 'bg-cyan-500/20 text-cyan-200 border border-cyan-400/40 shadow-xs'
                          : 'text-slate-400 hover:text-white hover:bg-white/[0.05]'
                      }`}
                    >
                      <tab.icon size={14} className={activeTab === tab.id ? 'text-cyan-300' : 'text-slate-400'} />
                      <span>{tab.label}</span>
                    </button>
                  ))}
                </div>

                {/* TAB 1: FUNDAMENTALS & PLAIN ENGLISH */}
                {activeTab === 'overview' && (
                  <div className="space-y-6 animate-in fade-in-50 duration-200">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] space-y-2">
                        <div className="flex items-center gap-2 text-cyan-400 font-bold text-xs font-mono uppercase">
                          <Info size={14} />
                          <span>What Is It in Plain English?</span>
                        </div>
                        <p className="text-sm text-slate-200 leading-relaxed">
                          {dossier.plain_english.what_is_it}
                        </p>
                      </div>

                      <div className="p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] space-y-2">
                        <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs font-mono uppercase">
                          <Activity size={14} />
                          <span>How It Works (Thermodynamics & Physics)</span>
                        </div>
                        <p className="text-sm text-slate-200 leading-relaxed">
                          {dossier.plain_english.how_it_works}
                        </p>
                      </div>

                      <div className="p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] space-y-2">
                        <div className="flex items-center gap-2 text-purple-400 font-bold text-xs font-mono uppercase">
                          <Sparkles size={14} />
                          <span>Why It Matters & Macro Problem Solved</span>
                        </div>
                        <p className="text-sm text-slate-200 leading-relaxed">
                          {dossier.plain_english.why_it_matters}
                        </p>
                      </div>

                      <div className="p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] space-y-2">
                        <div className="flex items-center gap-2 text-amber-400 font-bold text-xs font-mono uppercase">
                          <Clock size={14} />
                          <span>Evolutionary Arc (Past → Present → Future)</span>
                        </div>
                        <div className="text-xs text-slate-300 space-y-2">
                          <div><strong className="text-slate-400">Past:</strong> {dossier.evolution.past}</div>
                          <div><strong className="text-cyan-300">Present:</strong> {dossier.evolution.present}</div>
                          <div><strong className="text-emerald-300">Future (2030+):</strong> {dossier.evolution.future}</div>
                        </div>
                      </div>
                    </div>

                    {/* Dedicated Molecular Fuel Profile Card if Applicable */}
                    {dossier.fuel_profile && (
                      <div className="p-6 rounded-3xl bg-gradient-to-r from-emerald-950/40 via-[#0b101b] to-cyan-950/40 border border-emerald-500/30 space-y-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Fuel size={18} className="text-emerald-400" />
                            <h3 className="text-base font-extrabold text-white">
                              Zero-Carbon Molecular Fuel &amp; Carrier Profile
                            </h3>
                          </div>
                          <span className="font-mono text-xs text-emerald-300 font-bold">
                            {dossier.fuel_profile.chemical_formula}
                          </span>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs font-mono">
                          <div className="p-3 rounded-2xl bg-black/40 border border-white/[0.06]">
                            <div className="text-slate-400 uppercase text-[10px]">Lifecycle Carbon Intensity (CI)</div>
                            <div className="text-sm font-bold text-emerald-300 mt-1">{dossier.fuel_profile.carbon_intensity_ci}</div>
                          </div>
                          <div className="p-3 rounded-2xl bg-black/40 border border-white/[0.06]">
                            <div className="text-slate-400 uppercase text-[10px]">Gravimetric Energy Density</div>
                            <div className="text-sm font-bold text-white mt-1">{dossier.fuel_profile.energy_density_gravimetric}</div>
                          </div>
                          <div className="p-3 rounded-2xl bg-black/40 border border-white/[0.06]">
                            <div className="text-slate-400 uppercase text-[10px]">Volumetric Energy Density</div>
                            <div className="text-sm font-bold text-white mt-1">{dossier.fuel_profile.energy_density_volumetric}</div>
                          </div>
                          <div className="p-3 rounded-2xl bg-black/40 border border-white/[0.06]">
                            <div className="text-slate-400 uppercase text-[10px]">Primary Feedstock Vector</div>
                            <div className="text-xs font-bold text-slate-200 mt-1">{dossier.fuel_profile.feedstock_pathway}</div>
                          </div>
                          <div className="p-3 rounded-2xl bg-black/40 border border-white/[0.06]">
                            <div className="text-slate-400 uppercase text-[10px]">Drop-in Infrastructure</div>
                            <div className="text-xs font-bold text-slate-200 mt-1">{dossier.fuel_profile.drop_in_compatibility}</div>
                          </div>
                          <div className="p-3 rounded-2xl bg-black/40 border border-white/[0.06]">
                            <div className="text-slate-400 uppercase text-[10px]">Tax &amp; Policy Incentives</div>
                            <div className="text-xs font-bold text-cyan-300 mt-1">{dossier.fuel_profile.policy_incentives}</div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Brandon Owens Bankability Scorecard & Causal Lineage */}
                    <TechBankabilityCard techId={dossier.id} techName={dossier.name} />
                  </div>
                )}

                {/* TAB 2: EXPLORABLE SUBSYSTEM ARCHITECTURE */}
                {activeTab === 'architecture' && (
                  <div className="space-y-6 animate-in fade-in-50 duration-200">
                    <TechSystemDiagram
                      technologyId={dossier.id}
                      technologyName={dossier.name}
                      categoryName={dossier.category_name}
                      subsystems={dossier.subsystems}
                    />
                  </div>
                )}

                {/* TAB 3: INNOVATION FRONTIER & R&D */}
                {activeTab === 'frontier' && (
                  <div className="space-y-6 animate-in fade-in-50 duration-200">
                    {/* Moonshot Banner */}
                    <div className="p-6 rounded-3xl bg-gradient-to-r from-amber-500/10 via-purple-500/10 to-transparent border border-amber-500/20 space-y-2">
                      <div className="flex items-center gap-2 text-amber-400 font-bold text-xs font-mono uppercase">
                        <Target size={16} />
                        <span>Moonshot Engineering Horizon Target</span>
                      </div>
                      <p className="text-base sm:text-lg font-bold text-white">
                        {dossier.frontier.moonshot_goal}
                      </p>
                    </div>

                    {/* Standardized Milestone KPIs Table */}
                    <div className="p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] space-y-4">
                      <div className="flex items-center justify-between">
                        <h3 className="text-sm font-extrabold text-white font-mono uppercase">
                          Standardized Milestone Key Performance Indicators (KPIs)
                        </h3>
                        <span className="text-xs text-slate-400 font-mono">4 Target Benchmarks</span>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {dossier.frontier.kpis.map((kpi) => (
                          <div key={kpi.name} className="p-4 rounded-2xl bg-white/[0.03] border border-white/[0.06] space-y-2">
                            <div className="flex items-center justify-between gap-2">
                              <span className="text-xs font-bold text-slate-200">{kpi.name}</span>
                              {getStatusBadge(kpi.status)}
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-xs font-mono pt-2 border-t border-white/[0.06]">
                              <div>
                                <div className="text-[10px] text-slate-400 uppercase">Current Baseline</div>
                                <div className="text-xs font-bold text-slate-300 mt-0.5">{kpi.current}</div>
                              </div>
                              <div>
                                <div className="text-[10px] text-slate-400 uppercase">2030 Target</div>
                                <div className="text-xs font-bold text-cyan-300 mt-0.5">{kpi.target_2030}</div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Physics Bottlenecks vs Active Research Tracks */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="p-6 rounded-3xl bg-[#0b101b] border border-red-500/20 space-y-3">
                        <div className="flex items-center gap-2 text-red-400 font-bold text-xs font-mono uppercase">
                          <AlertTriangle size={14} />
                          <span>Critical Engineering &amp; Physics Bottlenecks</span>
                        </div>
                        <ul className="space-y-2 text-xs text-slate-300">
                          {dossier.frontier.bottlenecks.map((bn, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <span className="text-red-400 font-bold shrink-0">•</span>
                              <span>{bn}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div className="p-6 rounded-3xl bg-[#0b101b] border border-cyan-500/20 space-y-3">
                        <div className="flex items-center gap-2 text-cyan-400 font-bold text-xs font-mono uppercase">
                          <Sparkles size={14} />
                          <span>Active R&amp;D Tracks &amp; Consortia Focus</span>
                        </div>
                        <ul className="space-y-2 text-xs text-slate-300">
                          {dossier.frontier.active_research_tracks.map((rt, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <span className="text-cyan-400 font-bold shrink-0">→</span>
                              <span>{rt}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}

                {/* TAB 4: EMPIRICAL CAPITAL ALLOCATION & SOLICITATIONS */}
                {activeTab === 'evidence' && (
                  <div className="space-y-6 animate-in fade-in-50 duration-200">
                    {/* Empirical Evidence Top Cards */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 font-mono">
                      <div className="p-4 rounded-2xl bg-[#0b101b] border border-white/[0.08]">
                        <div className="text-[10px] text-slate-400 uppercase">Verified Grant Funding</div>
                        <div className="text-lg font-black text-emerald-300 mt-1">{dossier.evidence.tracked_capital_fmt}</div>
                        <div className="text-[10px] text-slate-500 mt-1">{dossier.evidence.temporal_vintage}</div>
                      </div>
                      <div className="p-4 rounded-2xl bg-[#0b101b] border border-white/[0.08]">
                        <div className="text-[10px] text-slate-400 uppercase">Awarded Projects</div>
                        <div className="text-lg font-black text-white mt-1">{dossier.evidence.award_count.toLocaleString()}</div>
                        <div className="text-[10px] text-slate-500 mt-1">{dossier.evidence.distinct_recipients_count} prime entities</div>
                      </div>
                      <div className="p-4 rounded-2xl bg-[#0b101b] border border-white/[0.08]">
                        <div className="text-[10px] text-slate-400 uppercase">Open Solicitations</div>
                        <div className="text-lg font-black text-cyan-300 mt-1">{dossier.evidence.active_solicitations_count} FOAs</div>
                        <div className="text-[10px] text-slate-500 mt-1">{dossier.evidence.pipeline_funding_fmt} pipeline</div>
                      </div>
                      <div className="p-4 rounded-2xl bg-[#0b101b] border border-white/[0.08]">
                        <div className="text-[10px] text-slate-400 uppercase">Linked Patents</div>
                        <div className="text-lg font-black text-purple-300 mt-1">{dossier.evidence.patent_count} Patents</div>
                        <div className="text-[10px] text-slate-500 mt-1">USPTO Bayh-Dole</div>
                      </div>
                    </div>

                    {/* Top Prime Recipients & Active Solicitations Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      
                      {/* Top Prime Recipients */}
                      <div className="p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] space-y-4">
                        <div className="flex items-center justify-between">
                          <h3 className="text-xs font-extrabold text-white font-mono uppercase flex items-center gap-2">
                            <Building2 size={14} className="text-cyan-400" />
                            <span>Top Prime Grant Recipients</span>
                          </h3>
                          <span className="text-[10px] text-slate-400 font-mono">By Verified Total Capital</span>
                        </div>

                        <div className="space-y-2">
                          {dossier.evidence.top_recipients.map((rec, rIdx) => (
                            <div key={rIdx} className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.05] flex items-center justify-between gap-3">
                              <div className="min-w-0">
                                <div className="text-xs font-bold text-slate-200 truncate">{rec.name}</div>
                                <div className="text-[10px] text-slate-400 font-mono">{rec.city}, {rec.state} · {rec.type}</div>
                              </div>
                              <div className="text-right shrink-0 font-mono">
                                <div className="text-xs font-bold text-emerald-300">{rec.total_awarded_fmt}</div>
                                <div className="text-[10px] text-slate-400">{rec.awards_count} awards</div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Active Open Solicitations */}
                      <div className="p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] space-y-4">
                        <div className="flex items-center justify-between">
                          <h3 className="text-xs font-extrabold text-white font-mono uppercase flex items-center gap-2">
                            <FileText size={14} className="text-emerald-400" />
                            <span>Active Matching Solicitations (FOAs)</span>
                          </h3>
                          <span className="text-[10px] text-emerald-400 font-mono font-bold">Open Access</span>
                        </div>

                        <div className="space-y-2">
                          {dossier.evidence.active_solicitations.length === 0 ? (
                            <div className="p-6 text-center text-xs text-slate-400 font-mono">
                              No active open solicitations matching current keywords.
                            </div>
                          ) : (
                            dossier.evidence.active_solicitations.map((opp) => (
                              <Link
                                key={opp.id}
                                to={`/opportunities/${opp.id}`}
                                className="p-3 rounded-xl bg-white/[0.03] hover:bg-white/[0.07] border border-white/[0.05] flex items-center justify-between gap-3 transition-colors block"
                              >
                                <div className="min-w-0">
                                  <div className="text-xs font-bold text-slate-200 truncate hover:text-cyan-300">{opp.name}</div>
                                  <div className="text-[10px] text-slate-400 font-mono">{opp.solicitation_number} · {opp.agency}</div>
                                </div>
                                <div className="text-right shrink-0 font-mono">
                                  <div className="text-xs font-bold text-emerald-300">{opp.funding_fmt}</div>
                                  <div className="text-[10px] text-cyan-400 font-semibold uppercase">{opp.status}</div>
                                </div>
                              </Link>
                            ))
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Linked USPTO Patents */}
                    {dossier.evidence.top_patents.length > 0 && (
                      <div className="p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] space-y-4">
                        <div className="flex items-center justify-between">
                          <h3 className="text-xs font-extrabold text-white font-mono uppercase flex items-center gap-2">
                            <Lightbulb size={14} className="text-purple-400" />
                            <span>Linked USPTO Patents &amp; IP Citations</span>
                          </h3>
                          <span className="text-[10px] text-purple-300 font-mono">Bayh-Dole Federal Provenance</span>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                          {dossier.evidence.top_patents.map((pat) => (
                            <div key={pat.id} className="p-3.5 rounded-xl bg-white/[0.03] border border-white/[0.05] space-y-1">
                              <div className="flex items-center justify-between text-[11px] font-mono">
                                <span className="text-purple-300 font-bold">{pat.number}</span>
                                <span className="text-slate-400">{pat.date || 'Granted'}</span>
                              </div>
                              <div className="text-xs font-bold text-white line-clamp-2">{pat.title}</div>
                              <div className="text-[10px] text-slate-400 font-mono truncate">{pat.assignee}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* TAB 5: 6D RADAR COMPETITIVENESS & TRADE-OFFS */}
                {activeTab === 'tradeoffs' && (
                  <div className="space-y-6 animate-in fade-in-50 duration-200">
                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
                      
                      {/* Radar Chart */}
                      <div className="lg:col-span-6 p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] flex flex-col items-center">
                        <div className="text-xs font-mono uppercase font-bold text-cyan-300 mb-2">
                          6-Dimensional Competitiveness Radar
                        </div>
                        <div className="w-full h-80">
                          <ResponsiveContainer width="100%" height="100%">
                            <RadarChart data={dossier.radar_data}>
                              <PolarGrid stroke="rgba(255,255,255,0.1)" />
                              <PolarAngleAxis dataKey="dimension" stroke="#94a3b8" tick={{ fontSize: 10, fill: '#cbd5e1' }} />
                              <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="rgba(255,255,255,0.2)" />
                              <Radar name={dossier.name} dataKey="score" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.4} />
                              <Radar name="Sector Benchmark" dataKey="benchmark" stroke="#a855f7" fill="#a855f7" fillOpacity={0.15} />
                              <RechartsTooltip />
                            </RadarChart>
                          </ResponsiveContainer>
                        </div>
                        <div className="flex items-center gap-4 text-xs font-mono text-slate-400 mt-2">
                          <div className="flex items-center gap-1.5">
                            <span className="w-3 h-3 rounded-full bg-cyan-400" />
                            <span>{dossier.name}</span>
                          </div>
                          <div className="flex items-center gap-1.5">
                            <span className="w-3 h-3 rounded-full bg-purple-400" />
                            <span>Sector Benchmark</span>
                          </div>
                        </div>
                      </div>

                      {/* Trade-Offs Text Breakdown */}
                      <div className="lg:col-span-6 space-y-4">
                        <div className="p-5 rounded-2xl bg-emerald-950/20 border border-emerald-500/20 space-y-2">
                          <div className="text-xs font-mono font-bold uppercase text-emerald-400 flex items-center gap-1.5">
                            <CheckCircle2 size={13} />
                            <span>Primary Competitive Advantages</span>
                          </div>
                          <ul className="text-xs text-slate-300 space-y-1.5">
                            {dossier.trade_offs.strengths.map((str, idx) => (
                              <li key={idx} className="flex items-start gap-2">
                                <span className="text-emerald-400 font-bold shrink-0">✓</span>
                                <span>{str}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div className="p-5 rounded-2xl bg-amber-950/20 border border-amber-500/20 space-y-2">
                          <div className="text-xs font-mono font-bold uppercase text-amber-400 flex items-center gap-1.5">
                            <AlertTriangle size={13} />
                            <span>Trade-Offs &amp; Disadvantages</span>
                          </div>
                          <ul className="text-xs text-slate-300 space-y-1.5">
                            {dossier.trade_offs.weaknesses.map((wk, idx) => (
                              <li key={idx} className="flex items-start gap-2">
                                <span className="text-amber-400 font-bold shrink-0">!</span>
                                <span>{wk}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div className="p-5 rounded-2xl bg-white/[0.03] border border-white/[0.08] space-y-2">
                          <div className="text-xs font-mono font-bold uppercase text-cyan-400 flex items-center gap-1.5">
                            <Split size={13} />
                            <span>Direct Competing Technologies</span>
                          </div>
                          <div className="flex flex-wrap gap-2 pt-1">
                            {dossier.trade_offs.competing_technologies.map((comp, idx) => (
                              <span key={idx} className="px-2.5 py-1 rounded-lg text-xs bg-white/[0.05] text-slate-200 border border-white/10 font-mono">
                                {comp}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* TAB 6: CODES, STANDARDS & PUC DOCKETS */}
                {activeTab === 'policies' && (
                  <div className="space-y-6 animate-in fade-in-50 duration-200">
                    <div className="flex items-center justify-between flex-wrap gap-3">
                      <div className="flex items-center gap-2 bg-black/40 p-1 rounded-xl border border-white/[0.08]">
                        <button
                          onClick={() => setPolicySubView('standards')}
                          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                            policySubView === 'standards' ? 'bg-white/15 text-white shadow-xs' : 'text-slate-400 hover:text-white'
                          }`}
                        >
                          Codes &amp; Standards ({techPoliciesData?.policies_count || 0})
                        </button>
                        <button
                          onClick={() => setPolicySubView('proceedings')}
                          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                            policySubView === 'proceedings' ? 'bg-white/15 text-white shadow-xs' : 'text-slate-400 hover:text-white'
                          }`}
                        >
                          PUC &amp; FERC Dockets ({techProceedingsData?.proceedings_count || 0})
                        </button>
                      </div>

                      <span className="text-xs text-slate-400 font-mono">
                        Relational Policy &amp; Regulatory Compliance Graph
                      </span>
                    </div>

                    {/* SubView: Standards */}
                    {policySubView === 'standards' && (
                      <div className="space-y-4">
                        {!techPoliciesData || techPoliciesData.policies.length === 0 ? (
                          <div className="p-8 rounded-3xl bg-[#0b101b] border border-white/[0.08] text-center text-xs text-slate-400 font-mono">
                            No governing standards linked to this specific technology profile yet.
                          </div>
                        ) : (
                          techPoliciesData.policies.map((pol) => (
                            <div key={pol.id} className="p-5 rounded-2xl bg-[#0b101b] border border-white/[0.08] space-y-3">
                              <div className="flex items-start justify-between gap-3">
                                <div>
                                  <div className="flex items-center gap-2">
                                    <span className="px-2 py-0.5 rounded-md text-[10px] font-mono font-bold uppercase bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                                      {pol.code_identifier}
                                    </span>
                                    <span className="text-xs text-slate-400 font-mono uppercase">{pol.category}</span>
                                    <span className="text-xs text-slate-400 font-mono">({pol.jurisdiction_level})</span>
                                  </div>
                                  <h4 className="text-sm font-bold text-white mt-1.5">{pol.title}</h4>
                                </div>
                                <span className={`px-2.5 py-0.5 rounded-full text-[10.5px] font-mono font-bold uppercase shrink-0 ${
                                  pol.compliance_impact === 'critical_gate'
                                    ? 'bg-red-500/20 text-red-300 border border-red-500/30'
                                    : pol.compliance_impact === 'cost_driver'
                                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                                    : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                                }`}>
                                  {pol.compliance_impact.replace('_', ' ')}
                                </span>
                              </div>

                              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                                <div className="p-3 rounded-xl bg-white/[0.02] border border-white/[0.04]">
                                  <div className="text-[10px] text-slate-400 font-mono uppercase font-bold">Compliance Mandate</div>
                                  <p className="text-slate-300 mt-1">{pol.compliance_mandate}</p>
                                </div>
                                <div className="p-3 rounded-xl bg-white/[0.02] border border-white/[0.04]">
                                  <div className="text-[10px] text-amber-400 font-mono uppercase font-bold">Commercial Friction Points</div>
                                  <p className="text-slate-300 mt-1">{pol.commercial_friction_points || 'None documented.'}</p>
                                </div>
                              </div>

                              {pol.associated_incentives && (
                                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-start gap-2.5">
                                  <DollarSign size={14} className="text-emerald-400 shrink-0 mt-0.5" />
                                  <div>
                                    <div className="text-[10px] text-emerald-300 font-mono uppercase font-bold">
                                      Associated IRA Tax Credits &amp; Policy Incentives
                                    </div>
                                    <p className="text-emerald-100 text-xs mt-0.5 leading-relaxed font-medium">
                                      {pol.associated_incentives}
                                    </p>
                                  </div>
                                </div>
                              )}
                            </div>
                          ))
                        )}
                      </div>
                    )}

                    {/* SubView: Proceedings */}
                    {policySubView === 'proceedings' && (
                      <div className="space-y-4">
                        {!techProceedingsData || techProceedingsData.proceedings.length === 0 ? (
                          <div className="p-8 rounded-3xl bg-[#0b101b] border border-white/[0.08] text-center text-xs text-slate-400 font-mono">
                            No active regulatory dockets directly evaluating this technology profile yet.
                          </div>
                        ) : (
                          techProceedingsData.proceedings.map((proc) => (
                            <div key={proc.id} className="p-5 rounded-2xl bg-[#0b101b] border border-white/[0.08] space-y-3">
                              <div className="flex items-start justify-between gap-3">
                                <div>
                                  <div className="flex items-center gap-2">
                                    <span className="px-2 py-0.5 rounded-md text-[10px] font-mono font-bold uppercase bg-purple-500/20 text-purple-300 border border-purple-500/30">
                                      {proc.docket_number}
                                    </span>
                                    <span className="text-xs text-cyan-300 font-mono font-bold">{proc.commission}</span>
                                    <span className="text-xs text-slate-400 font-mono uppercase">({proc.topic_category.replace(/_/g, ' ')})</span>
                                  </div>
                                  <h4 className="text-sm font-bold text-white mt-1.5">{proc.title}</h4>
                                </div>
                                <span className={`px-2.5 py-0.5 rounded-full text-[10.5px] font-mono font-bold uppercase shrink-0 ${
                                  proc.impact_level === 'high_catalyst'
                                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                                    : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                                }`}>
                                  {proc.impact_level.replace('_', ' ')}
                                </span>
                              </div>

                              <p className="text-xs text-slate-300 leading-relaxed">
                                {proc.executive_summary}
                              </p>

                              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                                <div className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/20">
                                  <div className="text-[10px] text-emerald-400 font-mono uppercase font-bold">Commercial Tailwinds</div>
                                  <p className="text-slate-300 mt-1">{proc.commercial_tailwinds}</p>
                                </div>
                                <div className="p-3 rounded-xl bg-red-950/20 border border-red-500/20">
                                  <div className="text-[10px] text-red-400 font-mono uppercase font-bold">Interconnection Friction</div>
                                  <p className="text-slate-300 mt-1">{proc.commercial_friction_points}</p>
                                </div>
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    )}
                  </div>
                )}

                {/* TAB 7: AI TECHNICAL SPECIALIST DILIGENCE COPILOT */}
                {activeTab === 'ai' && (
                  <div className="space-y-6 animate-in fade-in-50 duration-200">
                    <div className="p-6 rounded-3xl bg-gradient-to-br from-[#0c1424] to-[#080c14] border border-cyan-500/30 shadow-2xl space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Sparkles size={18} className="text-cyan-400" />
                          <h3 className="text-base font-extrabold text-white">
                            AI Technical Diligence Specialist (Deterministic &amp; OpenAI Mode)
                          </h3>
                        </div>
                        <span className="text-xs text-slate-400 font-mono">
                          SHA-256 Cached Engine
                        </span>
                      </div>

                      <form onSubmit={handleRunAiDiligence} className="space-y-3">
                        <div className="relative">
                          <input
                            type="text"
                            placeholder="Ask a technical, thermodynamic, or grant-readiness diligence question..."
                            value={aiQuestion}
                            onChange={(e) => setAiQuestion(e.target.value)}
                            className="w-full pl-4 pr-12 py-3 rounded-2xl bg-white/[0.04] border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
                          />
                          <button
                            type="submit"
                            disabled={aiMutation.isPending}
                            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold transition-all disabled:opacity-50 cursor-pointer"
                          >
                            {aiMutation.isPending ? <RefreshCw size={14} className="animate-spin" /> : <Send size={14} />}
                          </button>
                        </div>

                        {/* Quick Prompts */}
                        <div className="flex items-center gap-2 flex-wrap text-[11px] text-slate-400">
                          <span className="font-mono">Quick Inquiries:</span>
                          {[
                            "Thermodynamic efficiency ceilings",
                            "Commercial scaling bottlenecks",
                            "Grant proposal milestone alignment",
                            "Materials degradation failure modes"
                          ].map((p) => (
                            <button
                              type="button"
                              key={p}
                              onClick={() => {
                                setAiQuestion(p);
                                aiMutation.mutate(p);
                              }}
                              className="px-2.5 py-1 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] text-slate-300 hover:text-white border border-white/[0.06] transition-all cursor-pointer"
                            >
                              {p}
                            </button>
                          ))}
                        </div>
                      </form>

                      {/* AI Response Output */}
                      {aiMutation.data && (
                        <div className="p-6 rounded-2xl bg-black/40 border border-cyan-500/30 space-y-4 text-xs animate-in fade-in-50">
                          <div>
                            <div className="text-[10px] text-cyan-400 font-mono uppercase font-bold">Executive Synthesis</div>
                            <p className="text-slate-200 mt-1 text-sm leading-relaxed whitespace-pre-line">
                              {aiMutation.data.executive_synthesis}
                            </p>
                          </div>

                          <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.05]">
                            <div className="text-[10px] text-purple-400 font-mono uppercase font-bold">Engineering Deep-Dive</div>
                            <p className="text-slate-300 mt-1 whitespace-pre-line leading-relaxed">
                              {aiMutation.data.engineering_deep_dive}
                            </p>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.05]">
                              <div className="text-[10px] text-cyan-300 font-mono uppercase font-bold">Frontier Research Tracks</div>
                              <ul className="mt-1 space-y-1 text-slate-300">
                                {aiMutation.data.frontier_research_tracks.map((rt: string, i: number) => (
                                  <li key={i}>• {rt}</li>
                                ))}
                              </ul>
                            </div>

                            <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.05]">
                              <div className="text-[10px] text-emerald-300 font-mono uppercase font-bold">Strategic Recommendations</div>
                              <ul className="mt-1 space-y-1 text-slate-300">
                                {aiMutation.data.strategic_recommendations.map((rec: string, i: number) => (
                                  <li key={i}>→ {rec}</li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </>
            )}
          </main>
        </div>
      )}

      {/* ── VIEW MODE B: SIDE-BY-SIDE COMPARATIVE MATRIX ────────────────── */}
      {viewMode === 'comparison' && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 w-full space-y-6">
          <div className="p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  Head-to-Head Diligence
                </span>
                <span className="text-xs text-slate-400 font-mono">Select up to 4 technologies</span>
              </div>
              <h2 className="text-xl sm:text-2xl font-black text-white mt-1">
                Side-by-Side Clean Tech &amp; Fuels Comparative Benchmark
              </h2>
            </div>

            {/* Quick Add Dropdown */}
            <div className="flex items-center gap-2 flex-wrap">
              <select
                onChange={(e) => {
                  if (e.target.value) {
                    toggleCompareTech(e.target.value);
                    e.target.value = '';
                  }
                }}
                className="px-3 py-2 rounded-xl bg-white/[0.05] border border-white/10 text-xs text-white focus:outline-none focus:border-purple-400"
              >
                <option value="">+ Add Technology to Compare...</option>
                {allTechnologies.map(t => (
                  <option key={t.id} value={t.id} disabled={comparisonIds.includes(t.id)}>
                    {t.name} (TRL {t.trl_current})
                  </option>
                ))}
              </select>

              {comparisonIds.length > 0 && (
                <button
                  onClick={() => setComparisonIds([])}
                  className="px-3 py-2 rounded-xl text-xs font-bold text-slate-400 hover:text-white hover:bg-white/10 transition-all cursor-pointer"
                >
                  Clear All
                </button>
              )}
            </div>
          </div>

          {/* Comparison Cards Grid */}
          {isLoadingComparison ? (
            <div className="p-12 text-center text-slate-400 font-mono">Loading comparative analytics...</div>
          ) : !comparisonData || comparisonData.technologies.length === 0 ? (
            <div className="p-12 text-center text-slate-400 rounded-3xl bg-[#0b101b] border border-white/[0.08]">
              <Split size={32} className="mx-auto text-purple-400 mb-2" />
              <h3 className="text-base font-bold text-white">No Technologies Selected for Comparison</h3>
              <p className="text-xs text-slate-400 mt-1">Add technologies from the selector above or click the compare icon in the directory.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {comparisonData.technologies.map((t) => (
                <div key={t.id} className="p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] space-y-4 flex flex-col justify-between">
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                        {t.category_name}
                      </span>
                      <button
                        onClick={() => toggleCompareTech(t.id)}
                        className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10"
                      >
                        <X size={14} />
                      </button>
                    </div>

                    <div>
                      <h3 className="text-base font-black text-white">{t.name}</h3>
                      <p className="text-xs text-slate-300 mt-1 line-clamp-2">{t.headline}</p>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs font-mono pt-2 border-t border-white/[0.06]">
                      <div className="p-2.5 rounded-xl bg-white/[0.03]">
                        <div className="text-[10px] text-slate-400 uppercase">TRL Horizon</div>
                        <div className="text-xs font-bold text-cyan-300 mt-0.5">TRL {t.trl_current} → {t.trl_target}</div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-white/[0.03]">
                        <div className="text-[10px] text-slate-400 uppercase">Tracked Grants</div>
                        <div className="text-xs font-bold text-emerald-300 mt-0.5">{t.evidence.tracked_capital_fmt}</div>
                      </div>
                    </div>

                    {t.cost_performance && (
                      <div className="p-3 rounded-2xl bg-white/[0.02] border border-white/[0.05] space-y-1 text-xs font-mono">
                        <div className="text-[10px] text-slate-400 uppercase">{t.cost_performance.cost_metric.name}</div>
                        <div className="flex items-center justify-between text-xs font-bold">
                          <span className="text-slate-300">{t.cost_performance.cost_metric.baseline_fmt}</span>
                          <span className="text-cyan-400">→</span>
                          <span className="text-emerald-300">{t.cost_performance.cost_metric.target_2030_fmt}</span>
                        </div>
                        <div className="text-[10px] text-emerald-400 font-bold">{t.cost_performance.cost_metric.reduction_pct} reduction</div>
                      </div>
                    )}

                    <div className="space-y-1 text-xs">
                      <div className="text-[10px] font-mono uppercase text-slate-400 font-bold">Primary Bottleneck</div>
                      <p className="text-slate-300 text-xs line-clamp-2">{t.frontier.bottlenecks[0] || 'Durability'}</p>
                    </div>
                  </div>

                  <button
                    onClick={() => handleSelectTech(t.id)}
                    className="w-full py-2.5 rounded-xl bg-white/[0.05] hover:bg-cyan-500 hover:text-slate-950 text-xs font-bold text-white transition-all cursor-pointer mt-4"
                  >
                    Open Deep Dossier →
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── VIEW MODE C: ZERO-CARBON FUELS & MOLECULAR CARRIERS MATRIX ─── */}
      {viewMode === 'fuels_matrix' && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 w-full space-y-6">
          <div className="p-6 rounded-3xl bg-gradient-to-r from-emerald-950/40 via-[#0b101b] to-cyan-950/40 border border-emerald-500/30 space-y-2">
            <div className="flex items-center gap-2">
              <Fuel size={20} className="text-emerald-400" />
              <h2 className="text-xl sm:text-2xl font-black text-white">
                Zero-Carbon Fuels &amp; Molecular Energy Carriers Matrix
              </h2>
            </div>
            <p className="text-xs sm:text-sm text-slate-300 max-w-3xl">
              Comparative benchmark of synthetic hydrocarbons, green hydrogen, ammonia, e-methanol, and biomethane across lifecycle Carbon Intensity (CI), volumetric/gravimetric energy density, and policy incentives (IRA §45V / §45Z).
            </p>
          </div>

          {/* Fuels Matrix Cards */}
          {isLoadingFuels ? (
            <div className="p-12 text-center text-slate-400 font-mono">Loading molecular carriers matrix...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {fuelsMatrix.map((fuel) => (
                <div key={fuel.id} className="p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] hover:border-emerald-500/40 transition-all space-y-4 flex flex-col justify-between">
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                        {fuel.carrier_name}
                      </span>
                      <span className="text-xs font-mono font-bold text-cyan-300">
                        {fuel.chemical_formula}
                      </span>
                    </div>

                    <div>
                      <h3 className="text-base font-black text-white">{fuel.name}</h3>
                      <p className="text-xs text-slate-300 mt-1 line-clamp-2">{fuel.headline}</p>
                    </div>

                    <div className="space-y-2 text-xs font-mono pt-2 border-t border-white/[0.06]">
                      <div className="p-2.5 rounded-xl bg-black/40 border border-white/[0.05]">
                        <div className="text-[10px] text-slate-400 uppercase">Lifecycle Carbon Intensity (CI)</div>
                        <div className="text-xs font-bold text-emerald-300 mt-0.5">{fuel.carbon_intensity_ci}</div>
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        <div className="p-2 rounded-xl bg-black/40 border border-white/[0.05]">
                          <div className="text-[9px] text-slate-400 uppercase">Gravimetric</div>
                          <div className="text-[11px] font-bold text-white mt-0.5">{fuel.energy_density_gravimetric}</div>
                        </div>
                        <div className="p-2 rounded-xl bg-black/40 border border-white/[0.05]">
                          <div className="text-[9px] text-slate-400 uppercase">Volumetric</div>
                          <div className="text-[11px] font-bold text-white mt-0.5">{fuel.energy_density_volumetric}</div>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-1 text-xs">
                      <div className="text-[10px] font-mono uppercase text-slate-400 font-bold">Policy &amp; Tax Credits</div>
                      <p className="text-cyan-300 text-xs">{fuel.policy_incentives}</p>
                    </div>
                  </div>

                  <button
                    onClick={() => handleSelectTech(fuel.id)}
                    className="w-full py-2 rounded-xl bg-white/[0.05] hover:bg-emerald-500 hover:text-slate-950 text-xs font-bold text-white transition-all cursor-pointer mt-4"
                  >
                    View Molecular Dossier →
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── VIEW MODE D: INNOVATION FRONTIER & TRL QUADRANT MAP ────────── */}
      {viewMode === 'frontier_matrix' && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 w-full space-y-6">
          <div className="p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] space-y-2">
            <div className="flex items-center gap-2">
              <Compass size={20} className="text-amber-400" />
              <h2 className="text-xl sm:text-2xl font-black text-white">
                Innovation Frontier &amp; TRL Quadrant Map
              </h2>
            </div>
            <p className="text-xs sm:text-sm text-slate-300 max-w-3xl">
              Mapping all 36 clean technology pathways across TRL Maturity (X-Axis) vs 2030 CapEx Cost Reduction Potential (Y-Axis). Bubble size represents tracked historical grant commitments ($M).
            </p>
          </div>

          {/* Scatter Plot Visualizer */}
          <div className="p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] space-y-4">
            <div className="text-xs font-mono uppercase font-bold text-cyan-300">
              TRL Maturity vs. CapEx Reduction Potential Scatter Map
            </div>

            <div className="w-full h-96">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis
                    type="number"
                    dataKey="trl_current"
                    name="Current TRL"
                    domain={[3, 10]}
                    stroke="#94a3b8"
                    tick={{ fontSize: 11, fill: '#cbd5e1' }}
                    label={{ value: 'Current TRL Maturity (4 = Lab, 9 = Commercial)', position: 'insideBottom', offset: -10, fill: '#94a3b8', fontSize: 11 }}
                  />
                  <YAxis
                    type="number"
                    dataKey="cost_reduction_pct_num"
                    name="Cost Reduction %"
                    domain={[0, 100]}
                    stroke="#94a3b8"
                    tick={{ fontSize: 11, fill: '#cbd5e1' }}
                    label={{ value: 'CapEx Reduction Target % by 2030', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 11 }}
                  />
                  <ZAxis type="number" dataKey="tracked_capital_usd" range={[60, 400]} />
                  <RechartsTooltip
                    cursor={{ strokeDasharray: '3 3' }}
                    content={({ payload }) => {
                      if (!payload || payload.length === 0) return null;
                      const data = payload[0].payload as FrontierMatrixItem;
                      return (
                        <div className="p-3 rounded-xl bg-slate-900 border border-cyan-500/40 text-xs font-mono space-y-1 shadow-xl">
                          <div className="font-bold text-white text-sm">{data.name}</div>
                          <div className="text-cyan-300">{data.category_name}</div>
                          <div className="text-slate-300">TRL: {data.trl_current} → {data.trl_target}</div>
                          <div className="text-emerald-400">CapEx Reduction: {data.cost_reduction_pct_str}</div>
                          <div className="text-purple-300">Grant Capital: {data.tracked_capital_fmt}</div>
                        </div>
                      );
                    }}
                  />
                  <Scatter
                    name="Technologies"
                    data={frontierMatrix}
                    onClick={(entry: any) => handleSelectTech(entry?.id || entry?.payload?.id || entry?.payload?.payload?.id)}
                    cursor="pointer"
                  >
                    {frontierMatrix.map((entry) => (
                      <Cell
                        key={entry.id}
                        fill={SECTOR_COLORS[entry.category_id] || '#06b6d4'}
                      />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Sortable Frontier Matrix Table */}
          <div className="p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] overflow-x-auto space-y-3">
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="font-bold uppercase text-white">All 36 Innovation Pathways</span>
              <span className="text-slate-400">Click any row to open deep engineering dossier</span>
            </div>

            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-white/10 text-slate-400 uppercase text-[10px]">
                  <th className="pb-3 font-semibold">Technology</th>
                  <th className="pb-3 font-semibold">Sector</th>
                  <th className="pb-3 font-semibold text-center">TRL</th>
                  <th className="pb-3 font-semibold">2024 Baseline</th>
                  <th className="pb-3 font-semibold">2030 Target</th>
                  <th className="pb-3 font-semibold text-right">CapEx Delta</th>
                  <th className="pb-3 font-semibold text-right">Tracked Grants</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.05]">
                {frontierMatrix.map((row) => (
                  <tr
                    key={row.id}
                    onClick={() => handleSelectTech(row.id)}
                    className="hover:bg-white/[0.04] transition-colors cursor-pointer"
                  >
                    <td className="py-3 font-bold text-white pr-4">{row.name}</td>
                    <td className="py-3 text-slate-300 pr-4">{row.category_name}</td>
                    <td className="py-3 text-center">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getTRLBadgeColor(row.trl_current)}`}>
                        {row.trl_current}
                      </span>
                    </td>
                    <td className="py-3 text-slate-400">{row.cost_baseline_fmt}</td>
                    <td className="py-3 text-cyan-300 font-bold">{row.cost_target_2030_fmt}</td>
                    <td className="py-3 text-right font-bold text-emerald-400">{row.cost_reduction_pct_str}</td>
                    <td className="py-3 text-right font-bold text-purple-300">{row.tracked_capital_fmt}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── VIEW MODE E: REGULATORY & CODES COMPLIANCE MATRIX ──────────── */}
      {viewMode === 'regulatory_matrix' && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 w-full space-y-6">
          <div className="p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] space-y-2">
            <div className="flex items-center gap-2">
              <Scale size={20} className="text-blue-400" />
              <h2 className="text-xl sm:text-2xl font-black text-white">
                Clean Technology Codes, Standards &amp; Regulatory Reference Matrix
              </h2>
            </div>
            <p className="text-xs sm:text-sm text-slate-300 max-w-3xl">
              Cross-sector regulatory landscape covering NFPA/UL safety codes, IEEE interconnection rules, IRA §45V/§48C tax incentives, and active utility commission (PUC/FERC) dockets.
            </p>
          </div>

          {/* Governing Policy Standards Grid */}
          <div className="p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-mono uppercase font-bold text-cyan-300">
                Governing Safety Codes, Interconnection Standards &amp; Statutes
              </h3>
              <span className="text-xs text-slate-400 font-mono">23 National Codes Tracked</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {globalPoliciesData?.policies.map((pol) => (
                <div key={pol.id} className="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06] space-y-2 text-xs">
                  <div className="flex items-start justify-between gap-2">
                    <span className="px-2 py-0.5 rounded-md text-[10px] font-mono font-bold uppercase bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                      {pol.code_identifier}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono uppercase">{pol.jurisdiction_level}</span>
                  </div>
                  <h4 className="text-xs font-bold text-white line-clamp-2">{pol.title}</h4>
                  <p className="text-[11px] text-slate-400 line-clamp-2">{pol.executive_summary}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Active PUC & FERC Regulatory Dockets Grid */}
          <div className="p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-mono uppercase font-bold text-purple-300">
                Landmark Utility Commission (PUC &amp; FERC) Dockets
              </h3>
              <span className="text-xs text-slate-400 font-mono">15 Active Proceedings Tracked</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {globalProceedingsData?.proceedings.map((proc) => (
                <div key={proc.id} className="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06] space-y-2 text-xs">
                  <div className="flex items-start justify-between gap-2">
                    <span className="px-2 py-0.5 rounded-md text-[10px] font-mono font-bold uppercase bg-purple-500/20 text-purple-300 border border-purple-500/30">
                      {proc.docket_number}
                    </span>
                    <span className="text-xs text-cyan-300 font-mono font-bold">{proc.commission}</span>
                  </div>
                  <h4 className="text-xs font-bold text-white line-clamp-2">{proc.title}</h4>
                  <p className="text-[11px] text-slate-400 line-clamp-2">{proc.executive_summary}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── VIEW MODE F: NATIONAL LAB VALIDATION TESTBEDS ───────────────── */}
      {viewMode === 'lab_facilities' && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 w-full space-y-6">
          <div className="p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] space-y-2">
            <div className="flex items-center gap-2">
              <FlaskConical size={20} className="text-teal-400" />
              <h2 className="text-xl sm:text-2xl font-black text-white">
                DOE National Laboratory User Facilities &amp; Validation Testbeds
              </h2>
            </div>
            <p className="text-xs sm:text-sm text-slate-300 max-w-3xl">
              17 Department of Energy National Lab user testbeds for independent hardware validation, battery abuse testing, high-field magnetics, and advanced pilot scale-up. Access mechanisms include General User Proposals, CRADA, SPP, and Agreements for Commercializing Technology (ACT).
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {labFacilitiesData?.items?.map((facility) => (
              <div key={facility.id} className="p-5 rounded-3xl bg-[#0b101b] border border-white/[0.08] hover:border-teal-500/40 transition-all flex flex-col justify-between space-y-4 shadow-xl group">
                <div className="space-y-2.5">
                  <div className="flex items-start justify-between gap-2">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase bg-teal-500/20 text-teal-300 border border-teal-500/30">
                      {facility.lab_name}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-white/10 text-slate-300">
                      TRL {facility.trl_focus_min}–{facility.trl_focus_max}
                    </span>
                  </div>

                  <div>
                    <h3 className="text-base font-bold text-white group-hover:text-teal-300 transition-colors">
                      {facility.facility_name}
                    </h3>
                    <div className="text-[11px] text-slate-400 font-mono mt-0.5">
                      {[facility.city, facility.state].filter(Boolean).join(', ')} · {facility.facility_type || 'User Testbed'}
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed line-clamp-3">
                    {facility.summary}
                  </p>

                  {facility.instruments && facility.instruments.length > 0 && (
                    <div className="pt-2 border-t border-white/[0.06] space-y-1.5">
                      <div className="text-[10px] uppercase font-mono font-bold text-slate-400">Key Scientific Instruments</div>
                      <div className="space-y-1">
                        {facility.instruments.slice(0, 2).map((inst, iidx) => (
                          <div key={iidx} className="p-1.5 rounded-lg bg-white/[0.03] text-[10.5px] text-slate-300 font-mono">
                            <span className="text-teal-300 font-semibold">{inst.instrument}:</span> {inst.spec}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {facility.linked_technologies && facility.linked_technologies.length > 0 && (
                    <div className="pt-2">
                      <div className="text-[10px] uppercase font-mono font-bold text-slate-400 mb-1">Linked Innovation Domains</div>
                      <div className="flex flex-wrap gap-1">
                        {facility.linked_technologies.map((t, tidx) => (
                          <button
                            key={tidx}
                            onClick={() => handleSelectTech(t)}
                            className="px-2 py-0.5 rounded-md bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/20 text-[10px] font-mono transition-colors"
                          >
                            {t.replace(/_/g, ' ')}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="pt-3 border-t border-white/[0.06] flex items-center justify-between text-xs">
                  <span className="text-[10.5px] text-slate-400 font-mono">
                    Cycles: {facility.proposal_deadline_cycles || 'Continuous / Rolling'}
                  </span>
                  {facility.official_url && (
                    <a
                      href={facility.official_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-teal-400 hover:text-teal-300 font-bold font-mono text-[11px]"
                    >
                      <span>Access Portal</span>
                      <ExternalLink size={11} />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── VIEW MODE G: EMPIRICAL INSTALLED COST CURVES & OEM SHARES ─────── */}
      {viewMode === 'der_benchmarks' && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 w-full space-y-6">
          <div className="p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] space-y-2">
            <div className="flex items-center gap-2">
              <BarChart3 size={20} className="text-emerald-400" />
              <h2 className="text-xl sm:text-2xl font-black text-white">
                Empirical DER Installed Cost Curves &amp; OEM Market Deployments
              </h2>
            </div>
            <p className="text-xs sm:text-sm text-slate-300 max-w-3xl">
              Real-world turnkey installation cost curves ($/W, $/kWh) and OEM inverter/battery market share derived from Open NY (NY-Sun, Clean Heat), CA SGIP, and MassCEC PTS project ledgers.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Installed Cost Trajectories */}
            <div className="p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-mono uppercase font-bold text-emerald-400 flex items-center gap-1.5">
                  <TrendingDown size={14} /> Empirical $/W &amp; $/kWh Learning Curves (2020–2025)
                </h3>
                <span className="text-xs font-mono text-slate-400">
                  {includeNyserda ? 'NYSERDA & SGIP Verified' : 'SGIP Verified'}
                </span>
              </div>

              <div className="space-y-2">
                {derBenchmarksData?.cost_curves?.map((curve: any, idx: number) => (
                  <div key={idx} className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06] flex items-center justify-between text-xs">
                    <div>
                      <div className="font-bold text-white text-[13px]">{curve.technology_type} ({curve.year})</div>
                      <div className="text-[11px] text-slate-400 font-mono mt-0.5">
                        {curve.sector} · {curve.total_installs.toLocaleString()} Installs ({((curve.total_kw || 0) / 1000).toFixed(1)} MW)
                      </div>
                    </div>
                    <div className="text-right font-mono">
                      <div className="text-base font-bold text-emerald-400">
                        ${curve.avg_unit_cost.toFixed(2)} / {curve.technology_type.includes('Storage') ? 'kWh' : 'W'}
                      </div>
                      <div className="text-[10px] text-slate-400">Installed Turnkey</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Top Equipment Manufacturers & Market Share */}
            <div className="p-6 rounded-3xl bg-[#0b101b] border border-white/[0.08] space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-mono uppercase font-bold text-cyan-400 flex items-center gap-1.5">
                  <Award size={14} /> Top Equipment Manufacturers &amp; Market Share
                </h3>
                <span className="text-xs font-mono text-slate-400">Grid Connected MW</span>
              </div>

              <div className="space-y-2.5">
                {derBenchmarksData?.top_manufacturers?.map((mfg: any, idx: number) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-white/[0.03] border border-white/[0.06] flex items-center justify-between text-xs">
                    <div className="flex items-center gap-3">
                      <span className="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-300 font-mono font-bold text-[11px] flex items-center justify-center">
                        #{idx + 1}
                      </span>
                      <div>
                        <div className="font-bold text-white text-[13px]">{mfg.manufacturer}</div>
                        <div className="text-[11px] text-slate-400 font-mono mt-0.5">
                          {mfg.installs_count.toLocaleString()} Tracked Commercial &amp; Utility Installs
                        </div>
                      </div>
                    </div>
                    <div className="text-right font-mono">
                      <div className="text-base font-bold text-cyan-400">
                        {mfg.total_mw.toFixed(1)} MW
                      </div>
                      <div className="text-[10px] text-slate-400">Deployments</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
