import React, { useState, useMemo, useRef, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import {
  sankey,
  sankeyJustify,
  sankeyLeft,
  sankeyRight,
  sankeyCenter,
  sankeyLinkHorizontal,
  SankeyNode,
  SankeyLink,
} from 'd3-sankey';
import {
  GitMerge,
  Target,
  Layers,
  Zap,
  Landmark,
  Building2,
  TrendingUp,
  Download,
  Filter,
  RefreshCw,
  Sliders,
  HelpCircle,
  X,
  ChevronRight,
  Maximize2,
  ArrowRight,
  DollarSign,
  Briefcase,
  PieChart,
  Move,
  Search,
  ExternalLink,
  ChevronDown,
  Info,
  Activity,
  CheckCircle2,
  HeartHandshake,
  FlaskConical,
  Globe,
} from 'lucide-react';

import clsx from 'clsx';
import { saveAs } from 'file-saver';
import { OrgLogo } from '../components/OrgLogo';
import { NYTGraphicExportModal } from '../components/NYTGraphicExportModal';
import { useNyserda } from '../context/NyserdaContext';
import { useSEO } from '../utils/seo';

// ── FORMATTERS ──
function formatSmartCurrency(val: number): string {
  if (!val || val === 0) return '$0';
  if (val >= 1_000_000_000) return `$${(val / 1_000_000_000).toFixed(2)}B`;
  if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(1)}M`;
  if (val >= 1_000) return `$${(val / 1_000).toFixed(0)}K`;
  return `$${val.toLocaleString()}`;
}

function formatMetricValue(val: number, metric: string): string {
  if (metric === 'funding') return formatSmartCurrency(val);
  return `${Math.round(val).toLocaleString()} ${metric === 'awards' ? 'awards' : 'opps'}`;
}

// ── COLOR PALETTES ──
const THEMES: Record<string, { name: string; palettes: string[][] }> = {
  dynamic: {
    name: 'Dynamic Gradients',
    palettes: [
      ['#4f46e5', '#6366f1', '#818cf8', '#3b82f6', '#2563eb'],
      ['#059669', '#10b981', '#34d399', '#14b8a6', '#0d9488'],
      ['#d97706', '#f59e0b', '#fbbf24', '#f97316', '#ea580c'],
      ['#0284c7', '#0ea5e9', '#38bdf8', '#06b6d4', '#0891b2'],
      ['#7c3aed', '#8b5cf6', '#a78bfa', '#9333ea', '#c084fc'],
    ],
  },
  emerald: {
    name: 'Clean Tech Emerald',
    palettes: [
      ['#064e3b', '#065f46', '#047857', '#059669', '#10b981'],
      ['#0f766e', '#0d9488', '#14b8a6', '#2dd4bf', '#5eead4'],
      ['#0369a1', '#0284c7', '#0ea5e9', '#38bdf8', '#7dd3fc'],
      ['#15803d', '#16a34a', '#22c55e', '#4ade80', '#86efac'],
      ['#b45309', '#d97706', '#f59e0b', '#fbbf24', '#fde68a'],
    ],
  },
  gold: {
    name: 'Utility Gold & Grid',
    palettes: [
      ['#78350f', '#92400e', '#b45309', '#d97706', '#f59e0b'],
      ['#1e1b4b', '#312e81', '#3730a3', '#4338ca', '#4f46e5'],
      ['#1e3a8a', '#1e40af', '#1d4ed8', '#2563eb', '#3b82f6'],
      ['#831843', '#9d174d', '#be185d', '#db2777', '#ec4899'],
      ['#134e4a', '#115e59', '#0f766e', '#0d9488', '#14b8a6'],
    ],
  },
  neon: {
    name: 'Cyberpunk Neon',
    palettes: [
      ['#ec4899', '#f43f5e', '#fb7185', '#fda4af', '#f472b6'],
      ['#8b5cf6', '#a855f7', '#c084fc', '#d8b4fe', '#e879f9'],
      ['#06b6d4', '#0891b2', '#22d3ee', '#67e8f9', '#a5f3fc'],
      ['#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#2dd4bf'],
      ['#f59e0b', '#fbbf24', '#fde047', '#fef08a', '#facc15'],
    ],
  },
};

const ALL_DIMENSIONS = [
  { id: 'org_tier', label: 'Organization Tier', icon: Landmark, desc: 'Macro classification of funding institutions' },
  { id: 'agency', label: 'Funding Organization / Utility', icon: Building2, desc: 'Specific utilities, state agencies, non-profits, or federal funders' },
  { id: 'utility_type', label: 'Organization Structure', icon: Zap, desc: 'IOU, Public Power, State Authority, Foundation, Cabinet Dept' },
  { id: 'program', label: 'Program / Portfolio', icon: Layers, desc: 'Specific program initiative or funding solicitation area' },
  { id: 'sector', label: 'Sector / End-Use', icon: Briefcase, desc: 'Economic sector (Grid, Buildings, Mobility, Industry)' },
  { id: 'technology', label: 'Technology Solution', icon: TrendingUp, desc: 'Clean technology focus (Storage, Heat Pumps, Geothermal)' },
  { id: 'fuel', label: 'Clean Fuel / Resource', icon: Zap, desc: 'Energy resource (Electricity, Hydrogen, Thermal, Solar)' },
  { id: 'activity', label: 'Innovation Stage', icon: Target, desc: 'R&D, Demonstration, Commercialization, Technical Assistance' },
  { id: 'recipient_type', label: 'Recipient Type', icon: PieChart, desc: 'Startups, Universities, Utilities, Municipalities' },
  { id: 'recipient_state', label: 'Recipient State', icon: Landmark, desc: 'Geographic location of capital deployment' },
  { id: 'status', label: 'Solicitation Status', icon: Filter, desc: 'Open solicitations vs closed/archived' },
];

const ORG_TIER_TABS = [
  { id: 'all', label: 'All Organizations', short: 'All Ecosystem', icon: Globe, color: 'indigo', desc: 'Unified cross-tier view across all utilities, state agencies, foundations, and federal bodies' },
  { id: 'utility', label: 'Electric & Gas Utilities', short: 'Utilities', icon: Zap, color: 'amber', desc: '98+ Investor-Owned Utilities, Public Power Authorities, Co-ops, and NWA Programs' },
  { id: 'state', label: 'State Energy Agencies', short: 'State Agencies', icon: Building2, color: 'blue', desc: 'State Energy Innovation Authorities (NYSERDA, MassCEC, CEC, State Energy Offices)' },
  { id: 'foundation', label: 'Non-Profits & Foundations', short: 'Foundations', icon: HeartHandshake, color: 'emerald', desc: 'Philanthropic Climate Foundations & Non-profit Grantmakers' },
  { id: 'federal', label: 'Federal Agencies', short: 'Federal', icon: Landmark, color: 'indigo', desc: 'DOE, NSF, ARPA-E, DOD, EPA, USDA, NASA, DOT, DOC' },
  { id: 'national_lab', label: 'Research Institutions', short: 'Research', icon: FlaskConical, color: 'purple', desc: 'EPRI, National Laboratories, and Energy Research Consortia' },
];

export default function Sankey() {
  useSEO({
    title: 'Energy Innovation Capital Flows & Multi-Stage Sankey Visualization',
    description: 'Interactive multi-dimensional Sankey diagrams tracking $104B+ in public energy funding from federal and state agencies through utilities, sectors, and clean technologies.',
    canonicalUrl: 'https://terminal.aixenergy.io/capital-flows',
    keywords: ['energy innovation capital flows', 'energy funding sankey diagram', 'DOE funding distribution', 'utility innovation capital flows'],
  });

  const { includeNyserda, isNyserda } = useNyserda();
  // Organization Tier & Preset configuration
  const [selectedTier, setSelectedTier] = useState<string>('all');
  const [selectedPreset, setSelectedPreset] = useState<string>('ecosystem');
  const [customDimensions, setCustomDimensions] = useState<string[]>([
    'org_tier',
    'agency',
    'sector',
    'technology',
  ]);
  const [isCustomMode, setIsCustomMode] = useState(false);

  // Display & layout settings
  const [metric, setMetric] = useState<'funding' | 'opportunities' | 'awards'>('funding');
  const [alignment, setAlignment] = useState<'justify' | 'left' | 'right' | 'center'>('justify');
  const [theme, setTheme] = useState<string>('dynamic');
  const [nodePadding, setNodePadding] = useState<number>(20);
  const [nodeWidth, setNodeWidth] = useState<number>(24);
  const [topN, setTopN] = useState<number>(12);
  const [agencyFilter, setAgencyFilter] = useState<string>('');
  const [agencySearchOpen, setAgencySearchOpen] = useState(false);
  const [agencyQuery, setAgencyQuery] = useState('');

  // Clear agencyFilter if NYSERDA is excluded and was selected
  useEffect(() => {
    if (!includeNyserda && agencyFilter && isNyserda(agencyFilter)) {
      setAgencyFilter('');
    }
  }, [includeNyserda, agencyFilter, isNyserda]);

  // Interactive selection state
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [hoveredNode, setHoveredNode] = useState<any | null>(null);
  const [hoveredLink, setHoveredLink] = useState<any | null>(null);
  const [tooltipPos, setTooltipPos] = useState<{ x: number; y: number } | null>(null);

  // Drawers & Modals
  const [insightsOpen, setInsightsOpen] = useState(false);
  const [activeInsightTab, setActiveInsightTab] = useState<'all' | 'conduits' | 'utility' | 'tech' | 'strategy'>('all');
  const [guideOpen, setGuideOpen] = useState(false);

  const [exportOpen, setExportOpen] = useState(false);
  const [builderOpen, setBuilderOpen] = useState(false);
  const [nytExportOpen, setNytExportOpen] = useState(false);

  // SVG ref for sizing & export
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensionsState, setDimensionsState] = useState({ width: 1100, height: 650 });

  // Update container dimensions on resize
  useEffect(() => {
    function updateSize() {
      if (containerRef.current) {
        const { clientWidth } = containerRef.current;
        setDimensionsState({
          width: Math.max(800, clientWidth - 24),
          height: Math.max(580, window.innerHeight - 260),
        });
      }
    }
    updateSize();
    window.addEventListener('resize', updateSize);
    return () => window.removeEventListener('resize', updateSize);
  }, []);

  // Fetch Sankey Flow Data
  const flowParams = useMemo(() => {
    return {
      preset: isCustomMode ? undefined : selectedPreset,
      dimensions: isCustomMode ? customDimensions.join(',') : undefined,
      metric,
      agency: agencyFilter || undefined,
      org_type: selectedTier !== 'all' ? selectedTier : undefined,
      top_n_per_stage: topN,
      exclude_nyserda: !includeNyserda,
    };
  }, [selectedPreset, customDimensions, isCustomMode, metric, agencyFilter, selectedTier, topN, includeNyserda]);

  const { data: flowData, isLoading, isError, refetch } = useQuery<any>({
    queryKey: ['sankey-flow', flowParams],
    queryFn: () => api.getSankeyFlow(flowParams),
  });

  // Fetch Insights Data
  const { data: insightsData } = useQuery<any>({
    queryKey: ['sankey-insights', includeNyserda],
    queryFn: () => api.getSankeyInsights({ exclude_nyserda: !includeNyserda }),
  });

  // Fetch Agencies for Filter
  const { data: agenciesData } = useQuery<any>({
    queryKey: ['agencies'],
    queryFn: () => api.getAgencies(),
  });
  const agenciesList = useMemo(() => {
    const list = Array.isArray(agenciesData) ? agenciesData : agenciesData?.items || [];
    return list.filter((ag: any) => includeNyserda || !isNyserda(ag.name));
  }, [agenciesData, includeNyserda, isNyserda]);

  // Compute D3-Sankey layout
  const { layoutNodes, layoutLinks } = useMemo(() => {
    if (!flowData || !flowData.nodes || flowData.nodes.length === 0 || !flowData.links) {
      return { layoutNodes: [], layoutLinks: [] };
    }

    const { width, height } = dimensionsState;

    const alignFunc =
      alignment === 'left'
        ? sankeyLeft
        : alignment === 'right'
        ? sankeyRight
        : alignment === 'center'
        ? sankeyCenter
        : sankeyJustify;

    const sankeyGenerator = sankey<any, any>()
      .nodeWidth(nodeWidth)
      .nodePadding(nodePadding)
      .extent([
        [40, 45],
        [width - 40, height - 30],
      ])
      .nodeAlign(alignFunc)
      .iterations(32);

    // Deep clone nodes and links so D3 mutation doesn't mutate query cache
    const clonedNodes = flowData.nodes.map((n: any) => ({ ...n }));
    const clonedLinks = flowData.links.map((l: any) => ({ ...l }));

    try {
      const graph = sankeyGenerator({
        nodes: clonedNodes,
        links: clonedLinks,
      });

      // Apply selected theme colors
      const themeConfig = THEMES[theme] || THEMES.dynamic;
      graph.nodes.forEach((node: any) => {
        const stagePalettes = themeConfig.palettes[node.stage % themeConfig.palettes.length];
        node.color = stagePalettes[node.index % stagePalettes.length];
      });

      return { layoutNodes: graph.nodes, layoutLinks: graph.links };
    } catch (err) {
      console.error('Sankey layout computation error:', err);
      return { layoutNodes: [], layoutLinks: [] };
    }
  }, [flowData, dimensionsState, alignment, nodeWidth, nodePadding, theme]);

  // Compute Active Highlight Sets for Connected Path Tracing (Hover and Select)
  const { connectedNodes, connectedLinks } = useMemo(() => {
    const activeTarget = selectedNode || hoveredNode;
    if (!activeTarget && !hoveredLink) return { connectedNodes: null, connectedLinks: null };

    const cNodes = new Set<number>();
    const cLinks = new Set<number>();

    if (activeTarget) {
      cNodes.add(activeTarget.index);

      // Trace upstream ancestors
      function traceUpstream(nodeIdx: number) {
        layoutLinks.forEach((link: any, linkIdx: number) => {
          const targetIdx = typeof link.target === 'object' ? link.target.index : link.target;
          const sourceIdx = typeof link.source === 'object' ? link.source.index : link.source;
          if (targetIdx === nodeIdx) {
            cLinks.add(linkIdx);
            if (!cNodes.has(sourceIdx)) {
              cNodes.add(sourceIdx);
              traceUpstream(sourceIdx);
            }
          }
        });
      }

      // Trace downstream descendants
      function traceDownstream(nodeIdx: number) {
        layoutLinks.forEach((link: any, linkIdx: number) => {
          const targetIdx = typeof link.target === 'object' ? link.target.index : link.target;
          const sourceIdx = typeof link.source === 'object' ? link.source.index : link.source;
          if (sourceIdx === nodeIdx) {
            cLinks.add(linkIdx);
            if (!cNodes.has(targetIdx)) {
              cNodes.add(targetIdx);
              traceDownstream(targetIdx);
            }
          }
        });
      }

      traceUpstream(activeTarget.index);
      traceDownstream(activeTarget.index);
    } else if (hoveredLink) {
      const srcIdx = typeof hoveredLink.source === 'object' ? hoveredLink.source.index : hoveredLink.source;
      const tgtIdx = typeof hoveredLink.target === 'object' ? hoveredLink.target.index : hoveredLink.target;
      cNodes.add(srcIdx);
      cNodes.add(tgtIdx);
      layoutLinks.forEach((link: any, linkIdx: number) => {
        if (link === hoveredLink) cLinks.add(linkIdx);
      });
    }

    return { connectedNodes: cNodes, connectedLinks: cLinks };
  }, [selectedNode, hoveredNode, hoveredLink, layoutLinks]);

  // Executive Flow Analytics calculation
  const sankeyStats = useMemo(() => {
    let totalVal = 0;
    let maxLink: any = null;
    layoutLinks.forEach((l: any) => {
      totalVal += (l.value || 0);
      if (!maxLink || (l.value || 0) > (maxLink.value || 0)) {
        maxLink = l;
      }
    });

    return {
      totalFlow: totalVal,
      corridorsCount: layoutLinks.length,
      maxCorridor: maxLink ? `${maxLink.source.name} → ${maxLink.target.name}` : 'Ecosystem Matrix',
      maxCorridorValue: maxLink?.value || 0,
      stageCount: flowData?.stages?.length || 0,
      uniqueNodes: layoutNodes.length,
    };
  }, [layoutLinks, layoutNodes, flowData]);

  // Exports
  const handleExport = (format: 'svg' | 'png') => {
    if (format === 'svg') {
      if (svgRef.current) {
        const serializer = new XMLSerializer();
        const svgString = serializer.serializeToString(svgRef.current);
        saveAs(new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' }), `sankey-flow-${metric}.svg`);
      }
    } else if (format === 'png') {
      if (svgRef.current) {
        const serializer = new XMLSerializer();
        const svgString = serializer.serializeToString(svgRef.current);
        const img = new Image();
        const svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
        const url = URL.createObjectURL(svgBlob);
        img.onload = () => {
          const width = 2560;
          const headerHeight = 180;
          const footerHeight = 70;
          const padding = 45;
          const diagramHeight = Math.round(dimensionsState.height * (width / dimensionsState.width));
          const height = headerHeight + diagramHeight + footerHeight;

          const canvas = document.createElement('canvas');
          canvas.width = width;
          canvas.height = height;
          const ctx = canvas.getContext('2d');
          if (ctx) {
            ctx.imageSmoothingEnabled = true;
            ctx.imageSmoothingQuality = 'high';

            // Background
            ctx.fillStyle = '#FFFFFF';
            ctx.fillRect(0, 0, width, height);

            // Frame
            ctx.strokeStyle = '#1E293B';
            ctx.lineWidth = 3;
            ctx.strokeRect(20, 20, width - 40, height - 40);

            ctx.strokeStyle = '#E2E8F0';
            ctx.lineWidth = 1;
            ctx.strokeRect(28, 28, width - 56, height - 56);

            // Eyebrow
            ctx.font = '700 14px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
            ctx.fillStyle = '#B45309';
            ctx.fillText('ENERGY INNOVATION CAPITAL FLOWS · MULTI-STAGE TRAJECTORY', padding, 65);

            // Headline
            const currentPresetLabel = PRESET_OPTIONS.find(p => p.id === selectedPreset)?.label || metric.toUpperCase();
            ctx.font = 'bold 32px Georgia, "Playfair Display", "Times New Roman", serif';
            ctx.fillStyle = '#0F172A';
            ctx.fillText(`Energy Innovation Capital Flow: ${currentPresetLabel}`, padding, 105);

            // Date & Meta
            const today = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
            ctx.font = '400 16px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
            ctx.fillStyle = '#64748B';
            ctx.fillText(`Tracking multi-dimensional capital deployment across ${layoutNodes.length} nodes and ${layoutLinks.length} conduits.`, padding, 138);

            ctx.textAlign = 'right';
            ctx.fillText(`Edition: ${today}`, width - padding, 65);
            ctx.fillText('Energy Innovation Terminal Archive', width - padding, 90);
            ctx.textAlign = 'left';

            // Divider
            ctx.strokeStyle = '#E2E8F0';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(padding, 155);
            ctx.lineTo(width - padding, 155);
            ctx.stroke();

            // Draw SVG diagram
            ctx.drawImage(img, padding, headerHeight, width - padding * 2, diagramHeight);

            // Footer Source
            const footerY = height - 32;
            ctx.font = '500 14px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
            ctx.fillStyle = '#64748B';
            ctx.fillText('U.S. Energy Innovation Database · Clean Energy Research, LLC (https://terminal.aixenergy.io)', padding, footerY);

            ctx.textAlign = 'right';
            ctx.fillText('U.S. Energy Innovation Database · Clean Energy Research, LLC', width - padding, footerY);
            ctx.textAlign = 'left';

            canvas.toBlob((blob) => {
              if (blob) saveAs(blob, `sankey-flow-${metric}-highres.png`);
              URL.revokeObjectURL(url);
            });
          }
        };
        img.src = url;
      }
    }
    setExportOpen(false);
  };

  const PRESET_OPTIONS = [
    { id: 'ecosystem', label: 'Macro Ecosystem Flow', desc: 'Tier → Funder → Sector → Tech', tier: 'all' },
    { id: 'commercialization_9d', label: 'Commercialization Pipeline', desc: 'Agency → Program → Sector → Tech → Fuel → Stage', tier: 'all' },
    { id: 'patent_catalyst', label: 'Patent & Grant Catalyst', desc: 'Tier → Agency → Tech → Stage → Recipient', tier: 'all' },
    { id: 'utilities', label: 'Utility Capital Pipeline', desc: 'Structure → Utility → Program → Tech', tier: 'utility' },
    { id: 'state_energy', label: 'State Energy Innovation', desc: 'State Funder → Program → Sector → Tech', tier: 'state' },
    { id: 'nonprofit_funds', label: 'Philanthropic Capital', desc: 'Foundation → Stage → Sector → Tech', tier: 'foundation' },
    { id: 'capital_deployment', label: 'State Capital Deployment', desc: 'Funder → Stage → Recipient → State', tier: 'all' },
    { id: 'portfolio', label: 'Portfolio Stages', desc: 'Agency → Program → Activity → Status', tier: 'all' },
    { id: 'tech_fuels', label: 'Sector & Fuels Matrix', desc: 'Sector → Tech → Fuel → Agency', tier: 'all' },
  ];

  // Filtered agencies for dropdown
  const filteredAgencies = useMemo(() => {
    return agenciesList.filter((ag: any) => {
      const matchesTier = selectedTier === 'all' || ag.category === selectedTier;
      const matchesQuery = !agencyQuery || ag.name.toLowerCase().includes(agencyQuery.toLowerCase()) || (ag.full_name && ag.full_name.toLowerCase().includes(agencyQuery.toLowerCase()));
      return matchesTier && matchesQuery;
    });
  }, [agenciesList, selectedTier, agencyQuery]);

  return (
    <div className="flex flex-col h-[calc(100vh-6.5rem)] space-y-3" ref={containerRef}>
      
      {/* ── TOP CONTROL BAR ── */}
      <div className="bg-white p-3 rounded-2xl border border-slate-200 shadow-sm flex flex-col gap-2.5 relative z-30">
        
        {/* ROW 1: Organization Tier Filter Strip & Search */}
        <div className="flex items-center justify-between gap-2 flex-wrap border-b border-slate-100 pb-2.5">
          {/* Org Tier Selector Tabs */}
          <div className="flex items-center gap-1 bg-slate-100/80 p-1 rounded-xl overflow-x-auto max-w-full">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-2 shrink-0">
              Org Tier:
            </span>
            {ORG_TIER_TABS.map((tier) => {
              const IconComp = tier.icon;
              const isSelected = selectedTier === tier.id;
              return (
                <button
                  key={tier.id}
                  onClick={() => {
                    setSelectedTier(tier.id);
                    setSelectedNode(null);
                    // If switching tier and current preset has a default tier, sync it
                    if (tier.id === 'utility' && selectedPreset !== 'utilities') {
                      setSelectedPreset('utilities');
                    } else if (tier.id === 'state' && selectedPreset !== 'state_energy') {
                      setSelectedPreset('state_energy');
                    } else if (tier.id === 'foundation' && selectedPreset !== 'nonprofit_funds') {
                      setSelectedPreset('nonprofit_funds');
                    }
                  }}
                  className={clsx(
                    'px-2.5 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 shrink-0',
                    isSelected
                      ? 'bg-white text-slate-900 shadow-xs ring-1 ring-slate-200'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-white/60'
                  )}
                  title={tier.desc}
                >
                  <IconComp size={13} className={isSelected ? 'text-indigo-600' : 'text-slate-400'} />
                  <span>{tier.short}</span>
                </button>
              );
            })}
          </div>

          {/* Specific Agency Filter Dropdown */}
          <div className="relative">
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setAgencySearchOpen(!agencySearchOpen)}
                className={clsx(
                  'flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium border shadow-xs transition-colors',
                  agencyFilter
                    ? 'bg-indigo-50 border-indigo-200 text-indigo-900 font-bold'
                    : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                )}
              >
                <Building2 size={13} className={agencyFilter ? 'text-indigo-600' : 'text-slate-500'} />
                <span>{agencyFilter ? `Funder: ${agencyFilter}` : 'Filter by Specific Organization'}</span>
                <ChevronDown size={12} className="text-slate-400" />
              </button>
              {agencyFilter && (
                <button
                  onClick={() => setAgencyFilter('')}
                  className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
                  title="Clear organization filter"
                >
                  <X size={14} />
                </button>
              )}
            </div>

            {agencySearchOpen && (
              <div className="absolute right-0 mt-1.5 w-72 bg-white border border-slate-200 rounded-xl shadow-2xl p-2 z-50 text-xs animate-in fade-in zoom-in-95 duration-100">
                <div className="relative mb-2">
                  <Search size={13} className="absolute left-2.5 top-2.5 text-slate-400" />
                  <input
                    type="text"
                    value={agencyQuery}
                    onChange={(e) => setAgencyQuery(e.target.value)}
                    placeholder="Search utilities, agencies, foundations..."
                    className="w-full pl-8 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs outline-none focus:border-indigo-500 focus:bg-white"
                    autoFocus
                  />
                </div>

                <div className="max-h-60 overflow-y-auto space-y-1">
                  <button
                    onClick={() => {
                      setAgencyFilter('');
                      setAgencySearchOpen(false);
                    }}
                    className={clsx(
                      'w-full text-left px-2.5 py-1.5 rounded-lg flex items-center justify-between',
                      !agencyFilter ? 'bg-indigo-50 font-bold text-indigo-900' : 'hover:bg-slate-50 text-slate-700'
                    )}
                  >
                    <span>All Organizations (No Filter)</span>
                    <span className="text-[10px] text-slate-400">{agenciesList.length}</span>
                  </button>

                  {filteredAgencies.map((ag: any) => (
                    <button
                      key={ag.name}
                      onClick={() => {
                        setAgencyFilter(ag.name);
                        setAgencySearchOpen(false);
                      }}
                      className={clsx(
                        'w-full text-left px-2.5 py-1.5 rounded-lg flex items-center justify-between transition-colors',
                        agencyFilter === ag.name
                          ? 'bg-indigo-600 text-white font-bold'
                          : 'hover:bg-slate-50 text-slate-700'
                      )}
                    >
                      <div className="flex items-center gap-2 min-w-0 pr-2">
                        <OrgLogo org={ag.name} size="xs" />
                        <span className="truncate">{ag.name}</span>
                      </div>
                      <span className={clsx(
                        'text-[10px] px-1.5 py-0.5 rounded shrink-0 font-semibold',
                        agencyFilter === ag.name ? 'bg-indigo-500 text-white' : 'bg-slate-100 text-slate-500'
                      )}>
                        {ag.count} opps
                      </span>
                    </button>
                  ))}

                  {filteredAgencies.length === 0 && (
                    <div className="p-3 text-center text-slate-400 text-xs">
                      No organizations found matching "{agencyQuery}"
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ROW 2: Presets, Metric Switcher, & Action Controls */}
        <div className="flex items-center justify-between gap-3 flex-wrap">
          {/* Left: Presets & Custom Pipeline Switcher */}
          <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl overflow-x-auto max-w-full">
            {PRESET_OPTIONS.map((p) => (
              <button
                key={p.id}
                onClick={() => {
                  setSelectedPreset(p.id);
                  setIsCustomMode(false);
                  setSelectedNode(null);
                  if (p.tier && p.tier !== 'all') {
                    setSelectedTier(p.tier);
                  }
                }}
                className={clsx(
                  'px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 shrink-0',
                  !isCustomMode && selectedPreset === p.id
                    ? 'bg-white text-slate-900 shadow-xs ring-1 ring-slate-200'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
                )}
                title={p.desc}
              >
                {p.label}
              </button>
            ))}
            <button
              onClick={() => {
                setIsCustomMode(true);
                setBuilderOpen(true);
              }}
              className={clsx(
                'px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 shrink-0',
                isCustomMode
                  ? 'bg-indigo-600 text-white shadow-xs'
                  : 'text-indigo-600 hover:bg-indigo-50'
              )}
            >
              <Sliders size={13} /> Custom Builder
            </button>
          </div>

          {/* Right: Metric Switcher, Insights & Export */}
          <div className="flex items-center gap-2 flex-wrap">
            {/* Metric Selector */}
            <div className="flex items-center bg-slate-100 p-1 rounded-xl text-xs font-medium text-slate-600">
              <button
                onClick={() => setMetric('funding')}
                className={clsx(
                  'px-2.5 py-1 rounded-lg transition-all',
                  metric === 'funding' ? 'bg-white text-indigo-700 font-bold shadow-xs' : 'hover:text-slate-900'
                )}
              >
                Funding ($)
              </button>
              <button
                onClick={() => setMetric('opportunities')}
                className={clsx(
                  'px-2.5 py-1 rounded-lg transition-all',
                  metric === 'opportunities' ? 'bg-white text-indigo-700 font-bold shadow-xs' : 'hover:text-slate-900'
                )}
              >
                Opportunities (#)
              </button>
              <button
                onClick={() => setMetric('awards')}
                className={clsx(
                  'px-2.5 py-1 rounded-lg transition-all',
                  metric === 'awards' ? 'bg-white text-indigo-700 font-bold shadow-xs' : 'hover:text-slate-900'
                )}
              >
                Awards (#)
              </button>
            </div>

            {/* Publication Export Button */}
            <button
              onClick={() => setNytExportOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold shadow-xs transition-all cursor-pointer"
              title="Download high-resolution publication graphic (PNG)"
            >
              <Download size={13} className="text-slate-300" /> Publication Graphic
            </button>

            {/* Insights Button */}
            <button
              onClick={() => setInsightsOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-xs transition-all cursor-pointer"
            >
              <Activity size={13} className="text-indigo-200" /> Flow Insights
            </button>

            {/* Guide Button */}
            <button
              onClick={() => setGuideOpen(true)}
              className="p-2 bg-slate-50 border border-slate-200 rounded-xl text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors"
              title="How to explore Sankey flow"
            >
              <HelpCircle size={15} />
            </button>

            {/* Export Dropdown */}
            <div className="relative">
              <button
                onClick={() => setExportOpen(!exportOpen)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-200 rounded-xl text-xs font-medium text-slate-700 hover:bg-slate-50 shadow-xs transition-colors"
              >
                <Download size={13} className="text-slate-500" /> Export <ChevronDown size={12} />
              </button>
              {exportOpen && (
                <div className="absolute right-0 mt-1.5 w-52 bg-white border border-slate-200 rounded-xl shadow-xl p-1 z-50 text-xs animate-in fade-in zoom-in-95 duration-100">
                  <button
                    onClick={() => { setNytExportOpen(true); setExportOpen(false); }}
                    className="w-full text-left px-3 py-1.5 rounded-lg hover:bg-indigo-50 text-indigo-900 hover:text-indigo-700 font-semibold flex items-center gap-2"
                  >
                    <Download size={12} className="text-indigo-600" /> Publication Graphic (PNG)
                  </button>
                  <button
                    onClick={() => handleExport('svg')}
                    className="w-full text-left px-3 py-1.5 rounded-lg hover:bg-indigo-50 text-slate-700 hover:text-indigo-600 font-medium border-t border-slate-100"
                  >
                    Vector SVG (Publication)
                  </button>
                  <button
                    onClick={() => handleExport('png')}
                    className="w-full text-left px-3 py-1.5 rounded-lg hover:bg-indigo-50 text-slate-700 hover:text-indigo-600 font-medium"
                  >
                    Standard PNG Image
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ── HERO EXECUTIVE ANALYTICS RIBBON ── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
        <div className="bg-white px-3.5 py-2.5 rounded-xl border border-slate-200/80 shadow-2xs flex items-center justify-between">
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Flow Volume</div>
            <div className="text-base font-extrabold text-slate-900">{formatMetricValue(sankeyStats.totalFlow, metric)}</div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-sm">
            <DollarSign size={16} />
          </div>
        </div>

        <div className="bg-white px-3.5 py-2.5 rounded-xl border border-slate-200/80 shadow-2xs flex items-center justify-between">
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Active Corridors</div>
            <div className="text-base font-extrabold text-indigo-600">{sankeyStats.corridorsCount} Streams</div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-sm">
            <GitMerge size={16} />
          </div>
        </div>

        <div className="bg-white px-3.5 py-2.5 rounded-xl border border-slate-200/80 shadow-2xs flex items-center justify-between">
          <div className="min-w-0 pr-2">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider truncate">Largest Corridor</div>
            <div className="text-xs font-bold text-slate-800 truncate" title={sankeyStats.maxCorridor}>
              {sankeyStats.maxCorridor}
            </div>
          </div>
          <div className="text-[11px] font-extrabold font-mono text-emerald-700 bg-emerald-50 px-2 py-1 rounded-md shrink-0">
            {formatMetricValue(sankeyStats.maxCorridorValue, metric)}
          </div>
        </div>

        <div className="bg-white px-3.5 py-2.5 rounded-xl border border-slate-200/80 shadow-2xs flex items-center justify-between">
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Pipeline Depth</div>
            <div className="text-base font-extrabold text-slate-800">{sankeyStats.stageCount} Stages · {sankeyStats.uniqueNodes} Nodes</div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center font-bold text-sm">
            <Layers size={16} />
          </div>
        </div>
      </div>

      {/* ── SECONDARY CONTROLS & STAGE HEADER ── */}
      <div className="flex items-center justify-between gap-4 px-2 text-xs flex-wrap">
        {/* Stage Columns Indicators & Active Filter Tags */}
        <div className="flex items-center gap-2 overflow-x-auto no-scrollbar py-0.5">
          {/* Active Filter Pills */}
          {selectedTier !== 'all' && (
            <span className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-800 border border-indigo-200 font-semibold text-[11px]">
              <span>Tier: {ORG_TIER_TABS.find(t => t.id === selectedTier)?.short}</span>
              <button onClick={() => setSelectedTier('all')} className="hover:text-indigo-950 ml-0.5"><X size={11} /></button>
            </span>
          )}

          {agencyFilter && (
            <span className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-800 border border-indigo-200 font-semibold text-[11px]">
              <span>Funder: {agencyFilter}</span>
              <button onClick={() => setAgencyFilter('')} className="hover:text-indigo-950 ml-0.5"><X size={11} /></button>
            </span>
          )}

          {selectedNode && (
            <span className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-amber-50 text-amber-800 border border-amber-200 font-semibold text-[11px]">
              <span>Focus: {selectedNode.name}</span>
              <button onClick={() => setSelectedNode(null)} className="hover:text-amber-950 ml-0.5"><X size={11} /></button>
            </span>
          )}

          {(selectedTier !== 'all' || agencyFilter || selectedNode) && (
            <button
              onClick={() => {
                setSelectedTier('all');
                setAgencyFilter('');
                setSelectedNode(null);
                setSelectedPreset('ecosystem');
                setIsCustomMode(false);
              }}
              className="text-[11px] font-bold text-slate-500 hover:text-slate-800 underline decoration-slate-300"
            >
              Reset All
            </button>
          )}

          {/* Stage Progression Path */}
          <div className="flex items-center gap-2 ml-2 pl-2 border-l border-slate-200">
            {flowData?.stages?.map((st: any, i: number) => (
              <div key={st.dimension} className="flex items-center gap-1.5 shrink-0 bg-white/80 px-2 py-0.5 rounded-lg border border-slate-200/60 shadow-2xs">
                <span className="w-3.5 h-3.5 rounded-full bg-indigo-600 text-white font-bold text-[8px] flex items-center justify-center">
                  {i + 1}
                </span>
                <span className="font-bold text-slate-800 text-[10px] uppercase tracking-wider">
                  {st.label}
                </span>
                <span className="text-[9px] text-slate-400 font-medium">({st.node_count})</span>
                {i < (flowData.stages.length - 1) && (
                  <ArrowRight size={10} className="text-slate-300 ml-1" />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Display Adjustments */}
        <div className="flex items-center gap-2 shrink-0">
          {/* Theme Switcher */}
          <select
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            className="px-2 py-1 bg-white border border-slate-200 rounded-lg text-[11px] font-semibold text-slate-700 outline-none shadow-2xs"
          >
            {Object.entries(THEMES).map(([k, v]) => (
              <option key={k} value={k}>{v.name}</option>
            ))}
          </select>

          {/* Alignment */}
          <select
            value={alignment}
            onChange={(e) => setAlignment(e.target.value as any)}
            className="px-2 py-1 bg-white border border-slate-200 rounded-lg text-[11px] font-semibold text-slate-700 outline-none shadow-2xs"
          >
            <option value="justify">Align: Justify</option>
            <option value="left">Align: Left</option>
            <option value="right">Align: Right</option>
            <option value="center">Align: Center</option>
          </select>

          {/* Top N */}
          <div className="flex items-center gap-1 text-[11px] text-slate-500 bg-white px-2 py-1 rounded-lg border border-slate-200 shadow-2xs font-medium">
            <span>Top:</span>
            <select
              value={topN}
              onChange={(e) => setTopN(parseInt(e.target.value))}
              className="bg-transparent text-[11px] font-bold text-indigo-700 outline-none cursor-pointer"
            >
              <option value="6">6</option>
              <option value="12">12</option>
              <option value="18">18</option>
              <option value="25">25</option>
              <option value="40">40</option>
            </select>
          </div>
        </div>
      </div>

      {/* ── MAIN SANKEY SVG CANVAS ── */}
      <div id="sankey-svg-canvas-container" className="flex-1 bg-white rounded-2xl border border-slate-200 shadow-sm relative overflow-hidden flex flex-col justify-center items-center">
        {isLoading ? (
          <div className="flex flex-col items-center gap-3">
            <RefreshCw className="animate-spin text-indigo-600" size={32} />
            <p className="text-sm font-semibold text-slate-600">Calculating Capital Flow Dynamics...</p>
          </div>
        ) : layoutNodes.length === 0 ? (
          <div className="text-center p-8">
            <p className="text-sm font-semibold text-slate-700">No flow paths available for the current filter settings.</p>
            <button
              onClick={() => {
                setAgencyFilter('');
                setSelectedTier('all');
                setSelectedPreset('ecosystem');
                setIsCustomMode(false);
              }}
              className="mt-3 px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-semibold shadow-xs"
            >
              Reset Filters
            </button>
          </div>
        ) : (
          <svg
            ref={svgRef}
            width={dimensionsState.width}
            height={dimensionsState.height}
            className="w-full h-full select-none"
            style={{ minHeight: '520px' }}
          >
            <defs>
              {/* Drop Shadow & Glow Filters */}
              <filter id="node-glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="glow" />
                <feComposite in="SourceGraphic" in2="glow" operator="over" />
              </filter>
              <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
                <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.12" />
              </filter>
              <filter id="ribbon-glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="2" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>

              {/* Dynamic Linear Gradients for Every Flow Ribbon */}
              {layoutLinks.map((link: any, idx: number) => {
                const srcCol = link.source.color || '#6366f1';
                const tgtCol = link.target.color || '#10b981';
                return (
                  <linearGradient
                    key={`grad-${idx}`}
                    id={`link-grad-${idx}`}
                    gradientUnits="userSpaceOnUse"
                    x1={link.source.x1}
                    x2={link.target.x0}
                  >
                    <stop offset="0%" stopColor={srcCol} stopOpacity={0.65} />
                    <stop offset="50%" stopColor={srcCol} stopOpacity={0.45} />
                    <stop offset="100%" stopColor={tgtCol} stopOpacity={0.65} />
                  </linearGradient>
                );
              })}
            </defs>

            {/* ── FLOW RIBBONS (LINKS) ── */}
            <g className="links">
              {layoutLinks.map((link: any, idx: number) => {
                const pathData = sankeyLinkHorizontal()(link);
                const isConnected = !connectedLinks || connectedLinks.has(idx);
                const isHovered = hoveredLink === link;

                return (
                  <path
                    key={`link-${idx}`}
                    d={pathData || ''}
                    fill="none"
                    stroke={`url(#link-grad-${idx})`}
                    strokeWidth={Math.max(1.5, link.width || 1)}
                    strokeOpacity={
                      isHovered ? 0.98 : isConnected ? 0.72 : 0.06
                    }
                    filter={isHovered ? 'url(#ribbon-glow)' : undefined}
                    className="transition-all duration-200 cursor-pointer hover:stroke-opacity-100"
                    onMouseEnter={(e) => {
                      setHoveredLink(link);
                      setTooltipPos({ x: e.clientX, y: e.clientY });
                    }}
                    onMouseMove={(e) => {
                      setTooltipPos({ x: e.clientX, y: e.clientY });
                    }}
                    onMouseLeave={() => setHoveredLink(null)}
                    onClick={() => {
                      // Click link to select source node
                      setSelectedNode(link.source);
                    }}
                  />
                );
              })}
            </g>

            {/* ── NODES ── */}
            <g className="nodes">
              {layoutNodes.map((node: any) => {
                const isSelected = selectedNode && selectedNode.index === node.index;
                const isConnected = !connectedNodes || connectedNodes.has(node.index);
                const isHovered = hoveredNode === node;
                const nodeHeight = Math.max(8, node.y1 - node.y0);

                return (
                  <g
                    key={node.node_key || node.index}
                    transform={`translate(${node.x0}, ${node.y0})`}
                    className="cursor-pointer group"
                    onClick={() => {
                      if (selectedNode && selectedNode.index === node.index) {
                        setSelectedNode(null);
                      } else {
                        setSelectedNode(node);
                      }
                    }}
                    onMouseEnter={(e) => {
                      setHoveredNode(node);
                      setTooltipPos({ x: e.clientX, y: e.clientY });
                    }}
                    onMouseMove={(e) => {
                      setTooltipPos({ x: e.clientX, y: e.clientY });
                    }}
                    onMouseLeave={() => setHoveredNode(null)}
                  >
                    {/* Node Bar Rectangle */}
                    <rect
                      width={node.x1 - node.x0}
                      height={nodeHeight}
                      rx={6}
                      fill={node.color || '#6366f1'}
                      fillOpacity={isConnected ? 0.95 : 0.15}
                      stroke={isSelected ? '#1e1b4b' : isHovered ? '#4f46e5' : '#ffffff'}
                      strokeWidth={isSelected ? 2.5 : isHovered ? 2 : 1}
                      filter={isSelected || isHovered ? 'url(#node-glow)' : 'url(#shadow)'}
                      className="transition-all duration-200 hover:brightness-110"
                    />

                    {/* Node Label Text */}
                    {node.x0 < dimensionsState.width / 2 ? (
                      <text
                        x={(node.x1 - node.x0) + 8}
                        y={nodeHeight / 2}
                        dy="0.35em"
                        textAnchor="start"
                        className={clsx(
                          'text-[11px] transition-all select-none pointer-events-none',
                          isConnected ? 'font-bold fill-slate-800' : 'fill-slate-300 font-normal'
                        )}
                      >
                        {node.name}
                        <tspan className="fill-slate-400 font-normal text-[10px] ml-1">
                          {' '}({formatMetricValue(node.value, metric)})
                        </tspan>
                      </text>
                    ) : (
                      <text
                        x={-8}
                        y={nodeHeight / 2}
                        dy="0.35em"
                        textAnchor="end"
                        className={clsx(
                          'text-[11px] transition-all select-none pointer-events-none',
                          isConnected ? 'font-bold fill-slate-800' : 'fill-slate-300 font-normal'
                        )}
                      >
                        {node.name}
                        <tspan className="fill-slate-400 font-normal text-[10px] ml-1">
                          {' '}({formatMetricValue(node.value, metric)})
                        </tspan>
                      </text>
                    )}
                  </g>
                );
              })}
            </g>
          </svg>
        )}

        {/* ── FLOATING HOVER TOOLTIP ── */}
        {tooltipPos && (hoveredLink || hoveredNode) && (
          <div
            className="fixed pointer-events-none bg-slate-900/95 text-white p-3 rounded-xl shadow-2xl z-50 text-xs max-w-xs border border-white/10 backdrop-blur-sm"
            style={{
              left: `${tooltipPos.x + 14}px`,
              top: `${tooltipPos.y - 30}px`,
            }}
          >
            {hoveredLink && (
              <div className="space-y-1.5">
                <div className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">
                  Funding Conduit
                </div>
                <div className="flex items-center gap-1.5 font-semibold text-white">
                  <span>{hoveredLink.source.name}</span>
                  <ArrowRight size={12} className="text-amber-400" />
                  <span>{hoveredLink.target.name}</span>
                </div>
                <div className="pt-1 border-t border-white/10 flex items-center justify-between text-slate-300">
                  <span>Volume:</span>
                  <span className="font-bold text-amber-300 text-sm">
                    {formatMetricValue(hoveredLink.value, metric)}
                  </span>
                </div>
                <div className="text-[10px] text-slate-400">
                  {hoveredLink.source.value > 0 && (
                    <div>&bull; {((hoveredLink.value / hoveredLink.source.value) * 100).toFixed(1)}% of {hoveredLink.source.name} outflow</div>
                  )}
                  {hoveredLink.target.value > 0 && (
                    <div>&bull; {((hoveredLink.value / hoveredLink.target.value) * 100).toFixed(1)}% of {hoveredLink.target.name} inflow</div>
                  )}
                </div>
              </div>
            )}

            {hoveredNode && !hoveredLink && (
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <OrgLogo org={hoveredNode.name} size="xs" />
                  <span className="font-bold text-white text-sm">{hoveredNode.name}</span>
                </div>
                <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
                  <span>Stage {hoveredNode.stage + 1}: {hoveredNode.stage_name}</span>
                  {hoveredNode.category_label && (
                    <span className="px-1.5 py-0.5 rounded bg-white/10 text-indigo-300 font-medium">
                      {hoveredNode.category_label}
                    </span>
                  )}
                </div>
                <div className="pt-1 border-t border-white/10 flex items-center justify-between">
                  <span className="text-slate-300">Total Throughput:</span>
                  <span className="font-bold text-emerald-400">
                    {formatMetricValue(hoveredNode.value, metric)}
                  </span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── SELECTED NODE DETAIL DRAWER ── */}
        {selectedNode && (
          <div className="absolute right-4 top-4 bottom-4 w-80 bg-white/95 backdrop-blur-md border border-slate-200 rounded-2xl shadow-2xl p-4 flex flex-col z-40 animate-in slide-in-from-right duration-200">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-3">
              <div className="flex items-center gap-2 min-w-0">
                <OrgLogo org={selectedNode.name} size="sm" />
                <div className="min-w-0">
                  <h3 className="text-sm font-bold text-slate-900 truncate">{selectedNode.name}</h3>
                  <div className="flex items-center gap-1 flex-wrap mt-0.5">
                    <p className="text-[10px] text-slate-500 font-medium uppercase tracking-wider">
                      {selectedNode.stage_name} &middot; Stage {selectedNode.stage + 1}
                    </p>
                    {selectedNode.category_label && (
                      <span className="text-[9px] font-semibold px-1.5 py-0.2 rounded bg-indigo-50 text-indigo-700 border border-indigo-100">
                        {selectedNode.category_label}
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X size={16} />
              </button>
            </div>

            <div className="space-y-3 flex-1 overflow-y-auto pr-1 text-xs">
              <div className="p-3 bg-indigo-50/70 border border-indigo-100 rounded-xl">
                <span className="text-[10px] font-bold text-indigo-800 uppercase tracking-wider block">
                  Total Throughput ({metric})
                </span>
                <span className="text-lg font-extrabold text-indigo-950 mt-0.5 block">
                  {formatMetricValue(selectedNode.value, metric)}
                </span>
              </div>

              {/* Inbound Links */}
              {selectedNode.targetLinks?.length > 0 && (
                <div>
                  <h4 className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center justify-between">
                    <span>Inflow Originators</span>
                    <span>{selectedNode.targetLinks.length}</span>
                  </h4>
                  <div className="space-y-1">
                    {selectedNode.targetLinks.map((tl: any, i: number) => (
                      <div
                        key={i}
                        className="p-2 bg-slate-50 border border-slate-100 rounded-lg flex items-center justify-between"
                      >
                        <span className="font-medium text-slate-700 truncate mr-2">
                          {tl.source.name}
                        </span>
                        <span className="font-bold text-slate-900 shrink-0">
                          {formatMetricValue(tl.value, metric)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Outbound Links */}
              {selectedNode.sourceLinks?.length > 0 && (
                <div>
                  <h4 className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center justify-between">
                    <span>Downstream Destinations</span>
                    <span>{selectedNode.sourceLinks.length}</span>
                  </h4>
                  <div className="space-y-1">
                    {selectedNode.sourceLinks.map((sl: any, i: number) => (
                      <div
                        key={i}
                        className="p-2 bg-slate-50 border border-slate-100 rounded-lg flex items-center justify-between"
                      >
                        <span className="font-medium text-slate-700 truncate mr-2">
                          {sl.target.name}
                        </span>
                        <span className="font-bold text-slate-900 shrink-0">
                          {formatMetricValue(sl.value, metric)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-slate-100 mt-2">
              <button
                onClick={() => setSelectedNode(null)}
                className="w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl text-xs transition-colors"
              >
                Reset Selection
              </button>
            </div>
          </div>
        )}
      </div>

      {/* ── CUSTOM PIPELINE BUILDER MODAL ── */}
      {builderOpen && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-lg w-full p-5 space-y-4 animate-in fade-in zoom-in-95 duration-150 max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 shrink-0">
              <div className="flex items-center gap-2">
                <Sliders size={18} className="text-indigo-600" />
                <h3 className="font-bold text-slate-900 text-sm">Custom Pipeline Stage Builder</h3>
              </div>
              <button onClick={() => setBuilderOpen(false)} className="p-1 rounded-lg text-slate-400 hover:text-slate-600">
                <X size={16} />
              </button>
            </div>

            <div className="space-y-3 overflow-y-auto flex-1 pr-1 text-xs">
              {/* Quick Flow Templates */}
              <div>
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1.5">
                  Quick Pipeline Archetypes
                </label>
                <div className="grid grid-cols-2 gap-1.5">
                  <button
                    onClick={() => {
                      setCustomDimensions(['org_tier', 'agency', 'sector', 'technology']);
                      setSelectedTier('all');
                    }}
                    className="p-2 rounded-lg border border-slate-200 text-left hover:border-indigo-300 hover:bg-indigo-50/30 transition-all text-xs"
                  >
                    <div className="font-bold text-slate-800">Macro Ecosystem</div>
                    <div className="text-[10px] text-slate-400">Tier → Funder → Sector → Tech</div>
                  </button>
                  <button
                    onClick={() => {
                      setCustomDimensions(['utility_type', 'agency', 'program', 'technology']);
                      setSelectedTier('utility');
                    }}
                    className="p-2 rounded-lg border border-slate-200 text-left hover:border-amber-300 hover:bg-amber-50/30 transition-all text-xs"
                  >
                    <div className="font-bold text-amber-900">Utility Modernization</div>
                    <div className="text-[10px] text-slate-400">Structure → Utility → Program → Tech</div>
                  </button>
                  <button
                    onClick={() => {
                      setCustomDimensions(['agency', 'program', 'sector', 'technology']);
                      setSelectedTier('state');
                    }}
                    className="p-2 rounded-lg border border-slate-200 text-left hover:border-blue-300 hover:bg-blue-50/30 transition-all text-xs"
                  >
                    <div className="font-bold text-blue-900">State Energy Innovation</div>
                    <div className="text-[10px] text-slate-400">State Agency → Program → Sector → Tech</div>
                  </button>
                  <button
                    onClick={() => {
                      setCustomDimensions(['agency', 'activity', 'sector', 'technology']);
                      setSelectedTier('foundation');
                    }}
                    className="p-2 rounded-lg border border-slate-200 text-left hover:border-emerald-300 hover:bg-emerald-50/30 transition-all text-xs"
                  >
                    <div className="font-bold text-emerald-900">Philanthropic Capital</div>
                    <div className="text-[10px] text-slate-400">Foundation → Stage → Sector → Tech</div>
                  </button>
                  <button
                    onClick={() => {
                      setCustomDimensions(['agency', 'activity', 'recipient_type', 'recipient_state']);
                      setSelectedTier('all');
                    }}
                    className="p-2 rounded-lg border border-slate-200 text-left hover:border-indigo-300 hover:bg-indigo-50/30 transition-all text-xs col-span-2"
                  >
                    <div className="font-bold text-indigo-900">State Capital Deployment</div>
                    <div className="text-[10px] text-slate-400">Funder → Innovation Stage → Recipient Type → Recipient State</div>
                  </button>
                </div>
              </div>

              {/* Organization Tier Filter */}
              <div>
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1.5">
                  Target Organization Scope
                </label>
                <div className="grid grid-cols-3 gap-1.5">
                  {ORG_TIER_TABS.map((tier) => (
                    <button
                      key={tier.id}
                      onClick={() => setSelectedTier(tier.id)}
                      className={clsx(
                        'p-2 rounded-lg border text-xs font-semibold text-center transition-all',
                        selectedTier === tier.id
                          ? 'bg-indigo-600 text-white border-indigo-600 shadow-xs'
                          : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                      )}
                    >
                      {tier.short}
                    </button>
                  ))}
                </div>
              </div>

              {/* Dimensions Selector */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                    Flow Dimensions Sequence (Select 2 to 5)
                  </label>
                  <span className="text-[10px] font-bold text-indigo-600">
                    {customDimensions.length} Selected
                  </span>
                </div>
                <div className="space-y-1.5">
                  {ALL_DIMENSIONS.map((dim) => {
                    const isSelected = customDimensions.includes(dim.id);
                    const orderIdx = customDimensions.indexOf(dim.id);
                    const IconComponent = dim.icon;

                    return (
                      <div
                        key={dim.id}
                        onClick={() => {
                          if (isSelected) {
                            if (customDimensions.length > 2) {
                              setCustomDimensions(customDimensions.filter((d) => d !== dim.id));
                            }
                          } else {
                            if (customDimensions.length < 5) {
                              setCustomDimensions([...customDimensions, dim.id]);
                            }
                          }
                        }}
                        className={clsx(
                          'p-2.5 rounded-xl border text-xs flex items-center justify-between cursor-pointer transition-all',
                          isSelected
                            ? 'bg-indigo-50 border-indigo-200 text-indigo-950 font-semibold'
                            : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
                        )}
                      >
                        <div className="flex items-center gap-2.5 min-w-0 pr-2">
                          <IconComponent size={14} className={isSelected ? 'text-indigo-600 shrink-0' : 'text-slate-400 shrink-0'} />
                          <div className="min-w-0">
                            <span className="block truncate">{dim.label}</span>
                            <span className="text-[10px] text-slate-400 font-normal block truncate">{dim.desc}</span>
                          </div>
                        </div>

                        {isSelected && (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-600 text-white shrink-0">
                            Stage {orderIdx + 1}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-100 flex items-center justify-between shrink-0">
              <button
                onClick={() => {
                  setCustomDimensions(['org_tier', 'agency', 'sector', 'technology']);
                  setSelectedTier('all');
                }}
                className="text-xs text-slate-500 hover:text-slate-800 font-medium"
              >
                Reset to Default
              </button>
              <button
                onClick={() => {
                  setIsCustomMode(true);
                  setBuilderOpen(false);
                }}
                className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-semibold shadow-xs hover:bg-indigo-700"
              >
                Apply Custom Flow ({customDimensions.length} Stages)
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── AUTOMATED INSIGHTS DRAWER ── */}
      {insightsOpen && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex justify-end">
          <div className="bg-white w-full max-w-[460px] h-full shadow-2xl flex flex-col animate-in slide-in-from-right duration-200">
            <div className="p-4 border-b border-slate-100 bg-gradient-to-r from-slate-950 via-indigo-950 to-slate-900 text-white flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="p-2 bg-indigo-500/20 rounded-xl border border-indigo-400/30">
                  <Activity size={18} className="text-indigo-300" />
                </div>
                <div>
                  <h2 className="text-sm font-bold tracking-tight">Capital Flow Intelligence</h2>
                  <p className="text-[11px] text-indigo-200">Multi-stage conduit &amp; allocation analytics</p>
                </div>
              </div>
              <button onClick={() => setInsightsOpen(false)} className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors">
                <X size={16} />
              </button>
            </div>

            {/* Summary Stat Strip */}
            <div className="grid grid-cols-3 gap-2 p-3 bg-slate-50 border-b border-slate-200 text-center">
              <div className="p-2 bg-white rounded-lg border border-slate-200/80 shadow-xs">
                <div className="text-[10px] uppercase font-semibold text-slate-400">Conduit Capital</div>
                <div className="text-xs font-bold text-emerald-700">
                  {insightsData?.summary?.total_conduit_capital ? formatSmartCurrency(insightsData.summary.total_conduit_capital) : '$9.4B+'}
                </div>
              </div>
              <div className="p-2 bg-white rounded-lg border border-slate-200/80 shadow-xs">
                <div className="text-[10px] uppercase font-semibold text-slate-400">Top Arteries</div>
                <div className="text-xs font-bold text-indigo-700">
                  {insightsData?.top_conduits?.length || 10} Pathways
                </div>
              </div>
              <div className="p-2 bg-white rounded-lg border border-slate-200/80 shadow-xs">
                <div className="text-[10px] uppercase font-semibold text-slate-400">Multi-Agency</div>
                <div className="text-xs font-bold text-amber-700">
                  {insightsData?.cross_agency_technologies?.length || 10} Techs
                </div>
              </div>
            </div>

            {/* Category Tab Filter */}
            <div className="flex border-b border-slate-200 bg-white p-1 gap-1">
              <button onClick={() => setActiveInsightTab('all')} className={clsx('flex-1 py-1.5 text-[11px] font-semibold rounded-md transition-colors', activeInsightTab === 'all' ? 'bg-indigo-50 text-indigo-700 border border-indigo-200' : 'text-slate-500 hover:text-slate-800')}>All ({insightsData?.insights?.length || 5})</button>
              <button onClick={() => setActiveInsightTab('conduits')} className={clsx('flex-1 py-1.5 text-[11px] font-semibold rounded-md transition-colors', activeInsightTab === 'conduits' ? 'bg-indigo-50 text-indigo-700 border border-indigo-200' : 'text-slate-500 hover:text-slate-800')}>Conduits</button>
              <button onClick={() => setActiveInsightTab('utility')} className={clsx('flex-1 py-1.5 text-[11px] font-semibold rounded-md transition-colors', activeInsightTab === 'utility' ? 'bg-indigo-50 text-indigo-700 border border-indigo-200' : 'text-slate-500 hover:text-slate-800')}>Utility</button>
              <button onClick={() => setActiveInsightTab('tech')} className={clsx('flex-1 py-1.5 text-[11px] font-semibold rounded-md transition-colors', activeInsightTab === 'tech' ? 'bg-indigo-50 text-indigo-700 border border-indigo-200' : 'text-slate-500 hover:text-slate-800')}>Convergence</button>
              <button onClick={() => setActiveInsightTab('strategy')} className={clsx('flex-1 py-1.5 text-[11px] font-semibold rounded-md transition-colors', activeInsightTab === 'strategy' ? 'bg-indigo-50 text-indigo-700 border border-indigo-200' : 'text-slate-500 hover:text-slate-800')}>Strategy</button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-5">
              {/* Structured Discoveries */}
              <div>
                <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2.5 flex items-center justify-between">
                  <span className="flex items-center gap-1.5"><Activity size={13} className="text-indigo-600" /> Key Flow Discoveries</span>
                  <span className="text-[10px] font-normal text-slate-400">{insightsData?.insights?.length || 5} discoveries</span>
                </h3>
                <div className="space-y-3">
                  {insightsData?.insights
                    ?.filter((ins: any) => {
                      if (activeInsightTab === 'all') return true;
                      if (activeInsightTab === 'conduits') return ins.category === 'Capital Conduits';
                      if (activeInsightTab === 'utility') return ins.category === 'Utility Pipeline';
                      if (activeInsightTab === 'tech') return ins.category === 'Cross-Agency Flows';
                      if (activeInsightTab === 'strategy') return ins.category === 'Strategic Navigation';
                      return true;
                    })
                    ?.map((ins: any, i: number) => (
                      <div key={i} className="p-3.5 bg-gradient-to-br from-slate-50 to-indigo-50/20 rounded-xl border border-indigo-100/80 text-xs shadow-xs hover:border-indigo-200 transition-all">
                        <div className="flex items-center justify-between gap-2 mb-1.5">
                          <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-800 border border-indigo-200/60">
                            {ins.category || 'Discovery'}
                          </span>
                          {ins.badge && (
                            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-amber-50 text-amber-800 border border-amber-200">
                              {ins.badge}
                            </span>
                          )}
                        </div>
                        <div className="font-bold text-slate-900 text-[13px] flex items-start gap-1.5 mb-1.5">
                          <CheckCircle2 size={14} className="text-indigo-600 shrink-0 mt-0.5" />
                          <span>{ins.title}</span>
                        </div>
                        <p className="text-slate-600 leading-relaxed pl-5">{ins.description}</p>
                        {ins.metric && (
                          <div className="mt-2.5 pl-5 flex items-center gap-2">
                            <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                              {ins.metric}
                            </span>
                          </div>
                        )}
                      </div>
                    ))}
                </div>
              </div>

              {/* Major Capital Conduits */}
              {(activeInsightTab === 'all' || activeInsightTab === 'conduits') && (
                <div>
                  <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <TrendingUp size={13} className="text-indigo-600" /> Primary Capital Conduits
                  </h3>
                  <div className="space-y-2">
                    {insightsData?.top_conduits?.map((c: any, idx: number) => (
                      <div key={idx} className="p-3 bg-slate-50 border border-slate-200/80 rounded-xl space-y-1 hover:border-indigo-300 transition-colors">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-900 text-xs truncate pr-2">{c.headline}</span>
                          <span className="font-extrabold text-indigo-600 text-xs shrink-0">
                            {formatSmartCurrency(c.funding)}
                          </span>
                        </div>
                        <p className="text-[10px] text-slate-500">
                          {c.opp_count} dedicated solicitations channeled through this flow.
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Utility Innovation Allocation */}
              {(activeInsightTab === 'all' || activeInsightTab === 'utility') && (
                <div className="space-y-2 pt-2 border-t border-slate-100">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-amber-900 flex items-center gap-1.5">
                    <Zap size={13} className="text-amber-600" /> Utility Innovation Focus
                  </h3>
                  <p className="text-[11px] text-slate-500">
                    Share of utility solicitations dedicated to Non-Wires Alternatives and storage:
                  </p>
                  <div className="space-y-1.5 pt-1">
                    {insightsData?.utility_breakdown?.map((u: any, idx: number) => (
                      <div key={idx} className="flex items-center justify-between text-xs p-2 rounded-lg bg-amber-50/50 border border-amber-100">
                        <span className="font-semibold text-slate-800 truncate pr-2">{u.utility}</span>
                        <div className="flex items-center gap-2 shrink-0">
                          <span className="text-[10px] text-slate-500">{u.grid_storage_opps}/{u.total_opps} opps</span>
                          <span className="font-bold text-amber-700 bg-amber-100 px-1.5 py-0.5 rounded text-[10px]">
                            {u.pct_grid_focused}% Grid Focused
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Multi-Agency Technology Overlap */}
              {(activeInsightTab === 'all' || activeInsightTab === 'tech') && (
                <div className="space-y-2 pt-2 border-t border-slate-100">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-900 flex items-center gap-1.5">
                    <Layers size={13} className="text-emerald-600" /> Multi-Agency Technology Convergence
                  </h3>
                  <p className="text-[11px] text-slate-500">
                    Clean technology domains receiving co-funding across 3 or more distinct agencies:
                  </p>
                  <div className="space-y-2 pt-1">
                    {insightsData?.cross_agency_technologies?.map((t: any, idx: number) => (
                      <div key={idx} className="p-2.5 bg-emerald-50/50 border border-emerald-100 rounded-xl space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-900 text-xs">{t.technology}</span>
                          <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-1.5 py-0.5 rounded">
                            {t.agency_count} Agencies
                          </span>
                        </div>
                        <div className="flex flex-wrap gap-1 pt-1">
                          {t.agencies.slice(0, 6).map((ag: string) => (
                            <span key={ag} className="px-1.5 py-0.5 rounded text-[9px] bg-white border border-slate-200 text-slate-600 font-medium">
                              {ag}
                            </span>
                          ))}
                          {t.agencies.length > 6 && (
                            <span className="px-1.5 py-0.5 rounded text-[9px] bg-emerald-100 text-emerald-800 font-semibold">
                              +{t.agencies.length - 6} more
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── USER GUIDE MODAL ── */}

      {guideOpen && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-lg w-full p-6 space-y-4 animate-in fade-in zoom-in-95 duration-150 text-xs">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <GitMerge size={18} className="text-indigo-600" />
                <h3 className="font-bold text-slate-900 text-base">How to Explore Funding Flows</h3>
              </div>
              <button onClick={() => setGuideOpen(false)} className="p-1 rounded-lg text-slate-400 hover:text-slate-600">
                <X size={16} />
              </button>
            </div>

            <div className="space-y-3 text-slate-600 leading-relaxed">
              <div className="flex items-start gap-2.5">
                <span className="w-5 h-5 rounded-full bg-indigo-50 text-indigo-700 font-bold flex items-center justify-center shrink-0 mt-0.5">1</span>
                <div>
                  <strong className="text-slate-800">Switch Flow Pipelines:</strong> Select from pre-configured archetypes (Ecosystem, Utilities, Capital Deployment) or use the Custom Builder to analyze any sequence of stages.
                </div>
              </div>

              <div className="flex items-start gap-2.5">
                <span className="w-5 h-5 rounded-full bg-indigo-50 text-indigo-700 font-bold flex items-center justify-center shrink-0 mt-0.5">2</span>
                <div>
                  <strong className="text-slate-800">Trace Connected Pathways:</strong> Click any node on the diagram to isolate its full upstream sources and downstream destinations, dimming unrelated flows.
                </div>
              </div>

              <div className="flex items-start gap-2.5">
                <span className="w-5 h-5 rounded-full bg-indigo-50 text-indigo-700 font-bold flex items-center justify-center shrink-0 mt-0.5">3</span>
                <div>
                  <strong className="text-slate-800">Inspect Exact Capital Volumes:</strong> Hover over any flow ribbon to view the exact dollar throughput and its percentage share of the source outflow and target inflow.
                </div>
              </div>

              <div className="flex items-start gap-2.5">
                <span className="w-5 h-5 rounded-full bg-indigo-50 text-indigo-700 font-bold flex items-center justify-center shrink-0 mt-0.5">4</span>
                <div>
                  <strong className="text-slate-800">Export for Briefings:</strong> Download vector SVG or high-resolution PNG diagrams for presentations and executive briefings.
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setGuideOpen(false)}
                className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-semibold shadow-xs"
              >
                Got it
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Executive Style High-Resolution Infographic Export Modal */}
      <NYTGraphicExportModal
        isOpen={nytExportOpen}
        onClose={() => setNytExportOpen(false)}
        defaultTitle="ENERGY INNOVATION CAPITAL FLOWS & MULTI-STAGE TRAJECTORY"
        defaultSubtitle="Cross-stage allocation dynamics tracing capital deployment from organizational tiers and funding agencies through technological solutions and economic sectors."
        eyebrow="CAPITAL FLOW DYNAMICS · MULTI-STAGE ALLOCATION ATLAS"
        targetElementId="sankey-svg-canvas-container"
        stats={[
          { label: 'Pipeline Stages', val: `${flowData?.stages?.length || 4} Dimensions` },
          {
            label: 'Total Flow Volume',
            val: formatMetricValue(
              flowData?.nodes?.reduce((acc: number, n: any) => (n.stage === 0 ? acc + (n.value || 0) : acc), 0) || 0,
              metric
            ),
          },
          { label: 'Active Pipeline Entities', val: `${layoutNodes.length} Nodes` },
          { label: 'Active Capital Conduits', val: `${layoutLinks.length} Flows` },
        ]}
        legendItems={flowData?.stages?.map((st: any, idx: number) => {
          const themeConfig = THEMES[theme] || THEMES.dynamic;
          const stagePalette = themeConfig.palettes[idx % themeConfig.palettes.length];
          return {
            label: `Stage ${idx + 1}: ${st.label}`,
            color: stagePalette[0] || '#6366f1',
            count: `${st.node_count} nodes`,
          };
        })}
        legendTitle="FLOW PIPELINE STAGES"
        sourceAttribution="U.S. Energy Innovation Database · Clean Energy Research, LLC (https://terminal.aixenergy.io)"
        filenamePrefix="energy-innovation-capital-flow"
      />
    </div>
  );
}
