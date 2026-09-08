import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import {
  Network as NetworkIcon, Search, Download, Filter, RefreshCw, X, ZoomIn, ZoomOut,
  Maximize2, Building2, FileSearch, Trophy, Landmark, Cpu, Factory, Globe, Users,
  ChevronRight, ExternalLink, Loader2, Crosshair, Sparkles, HelpCircle,
  TrendingUp, Compass, Layers, GitFork, Activity, Share2,
  CheckCircle2, Flame, Sliders, BarChart3,
} from 'lucide-react';
import Graph from 'graphology';
import { SigmaContainer, useLoadGraph, useSigma, useRegisterEvents } from '@react-sigma/core';
import "@react-sigma/core/lib/style.css";
import forceAtlas2 from 'graphology-layout-forceatlas2';
import louvain from 'graphology-communities-louvain';
import betweennessCentrality from 'graphology-metrics/centrality/betweenness';
import pagerankCentrality from 'graphology-metrics/centrality/pagerank';
import clsx from 'clsx';
import { OrgLogo } from '../components/OrgLogo';
import { saveAs } from 'file-saver';
import { NYTGraphicExportModal } from '../components/NYTGraphicExportModal';
import { useNyserda } from '../context/NyserdaContext';

// ── VISUAL SEMANTICS ──
const NODE_COLORS: Record<string, string> = {
  organization: '#6366f1', opportunity: '#0ea5e9', award: '#f59e0b',
  awardee: '#10b981', technology: '#ec4899', sector: '#8b5cf6',
  program: '#14b8a6', fuel: '#f97316', geography: '#64748b',
  patent: '#f59e0b', investor: '#10b981',
};

const CLUSTER_PALETTE = [
  '#4f46e5', '#059669', '#d97706', '#db2777', '#7c3aed',
  '#0284c7', '#ea580c', '#0d9488', '#475569', '#e11d48',
  '#2563eb', '#16a34a', '#ca8a04', '#9333ea', '#0891b2',
];

const NODE_LABELS: Record<string, string> = {
  organization: 'Organization',
  opportunity: 'Opportunity',
  awardee: 'Awardee',
  technology: 'Technology',
  sector: 'Sector',
  program: 'Program',
  fuel: 'Clean Fuel',
  patent: 'USPTO Patent',
  investor: 'VC Investor',
};

const NODE_ICONS: Record<string, any> = {
  organization: <Building2 size={11} />, opportunity: <FileSearch size={11} />,
  award: <Trophy size={11} />, awardee: <Users size={11} />,
  technology: <Cpu size={11} />, sector: <Factory size={11} />,
  program: <Landmark size={11} />, fuel: <Flame size={11} />,
  geography: <Globe size={11} />,
  patent: <Trophy size={11} />, investor: <Building2 size={11} />,
};

const EDGE_COLORS: Record<string, string> = {
  funds: '#6366f1', awarded_to: '#10b981', has_technology: '#ec4899',
  in_sector: '#8b5cf6', uses_fuel: '#f97316', recurring: '#94a3b8',
  complementary: '#3b82f6', stackable: '#22c55e', topical_cluster: '#f59e0b',
  same_program_family: '#a855f7', part_of: '#64748b', focuses_on: '#f472b6',
  funder: '#6366f1', administrator: '#0ea5e9', partner: '#14b8a6',
  patented: '#f59e0b', invested_in: '#10b981',
};

const EDGE_LABELS: Record<string, string> = {
  funds: 'Funds', awarded_to: 'Awarded To', has_technology: 'Technology',
  in_sector: 'Sector', uses_fuel: 'Fuel', recurring: 'Recurring',
  complementary: 'Complementary', stackable: 'Stackable',
  topical_cluster: 'Topic Cluster', same_program_family: 'Same Family',
  part_of: 'Part Of', focuses_on: 'Focus Area', funder: 'Funder',
  administrator: 'Administrator', partner: 'Partner',
  predecessor: 'Predecessor', successor: 'Successor',
  patented: 'Bayh-Dole Patent', invested_in: 'VC Equity Backed',
};

function fmt(v?: number | null): string {
  if (!v) return '—';
  if (v >= 1e9) return `$${(v / 1e9).toFixed(1)}B`;
  if (v >= 1e6) return `$${(v / 1e6).toFixed(1)}M`;
  if (v >= 1e3) return `$${(v / 1e3).toFixed(0)}K`;
  return `$${v.toLocaleString()}`;
}

// ── GRAPH CONTROLLER (Completely Static & Stable, No Motion/Rotation) ──
function GraphController({
  graph,
  search,
  highlightedType,
  neighborhoodNode,
  colorMode,
  selectedCluster,
  pathNodes,
  onNodeClick,
  onHover,
}: {
  graph: Graph | null;
  search: string;
  highlightedType: string | null;
  neighborhoodNode: string | null;
  colorMode: 'type' | 'cluster';
  selectedCluster: number | null;
  pathNodes: string[];
  onNodeClick: (node: any) => void;
  onHover: (info: { node: any; x: number; y: number } | null) => void;
}) {
  const loadGraph = useLoadGraph();
  const sigma = useSigma();
  const registerEvents = useRegisterEvents();
  const isDragging = useRef(false);
  const draggedNode = useRef<string | null>(null);

  // Load graph into Sigma once when graph instance changes
  useEffect(() => {
    if (graph && graph.order > 0) {
      loadGraph(graph);
    }
  }, [graph, loadGraph]);

  // Apply visual filtering (dimming, highlighting, search) without recalculating physics or positions
  useEffect(() => {
    if (!graph || graph.order === 0) return;

    const pathSet = new Set(pathNodes);
    const neighborSet = new Set<string>();

    if (neighborhoodNode) {
      neighborSet.add(neighborhoodNode);
      graph.forEachNeighbor(neighborhoodNode, (n) => neighborSet.add(n));
      // 2-hop
      const hop1 = Array.from(neighborSet);
      hop1.forEach((h) => {
        graph.forEachNeighbor(h, (n) => neighborSet.add(n));
      });
    }

    const s = search.trim().toLowerCase();

    graph.forEachNode((node, attrs) => {
      const d = attrs.originalData || {};
      const inNeighborhood = !neighborhoodNode || neighborSet.has(node);
      const isPath = pathSet.has(node);

      let isMatch = true;
      if (s) {
        isMatch = (
          d.name?.toLowerCase().includes(s) ||
          d.agency?.toLowerCase().includes(s) ||
          d.solicitation_number?.toLowerCase().includes(s) ||
          d.keywords?.toLowerCase().includes(s) ||
          d.type?.toLowerCase().includes(s)
        );
      }

      const isDimmed = (
        !inNeighborhood ||
        !isMatch ||
        (highlightedType && d.type !== highlightedType) ||
        (colorMode === 'cluster' && selectedCluster !== null && attrs.community !== selectedCluster)
      );

      const baseColor = colorMode === 'cluster' ? (attrs.clusterColor || '#64748b') : (attrs.typeColor || '#64748b');

      graph.setNodeAttribute(node, 'hidden', !inNeighborhood || !isMatch);
      graph.setNodeAttribute(node, 'color', isPath ? '#f59e0b' : isDimmed ? '#f1f5f9' : baseColor);
      graph.setNodeAttribute(node, 'size', isPath ? (attrs.baseSize || 5) * 1.5 : (attrs.baseSize || 5));
    });

    graph.forEachEdge((edge, attrs, source, target) => {
      const srcHidden = graph.getNodeAttribute(source, 'hidden');
      const tgtHidden = graph.getNodeAttribute(target, 'hidden');
      const isPathEdge = pathSet.has(source) && pathSet.has(target);
      const baseCol = attrs.baseEdgeColor || '#cbd5e1';

      graph.setEdgeAttribute(edge, 'hidden', srcHidden || tgtHidden);
      graph.setEdgeAttribute(edge, 'color', isPathEdge ? '#f59e0b' : (srcHidden || tgtHidden) ? '#f8fafc' : baseCol);
      graph.setEdgeAttribute(edge, 'size', isPathEdge ? 3.5 : 1);
    });

    sigma.refresh();
  }, [graph, search, highlightedType, neighborhoodNode, colorMode, selectedCluster, pathNodes, sigma]);

  // Node Click & Drag events (No auto motion, camera stays fully stationary)
  useEffect(() => {
    registerEvents({
      clickNode: (e) => {
        const nd = sigma.getGraph().getNodeAttribute(e.node, 'originalData');
        const connections: any[] = [];
        sigma.getGraph().forEachEdge(e.node, (_edge, attrs, source, target) => {
          const neighborId = source === e.node ? target : source;
          if (sigma.getGraph().hasNode(neighborId)) {
            connections.push({ node: sigma.getGraph().getNodeAttribute(neighborId, 'originalData'), edge: attrs.originalData });
          }
        });
        onNodeClick({
          ...nd,
          id: e.node,
          degree: sigma.getGraph().degree(e.node),
          community: sigma.getGraph().getNodeAttribute(e.node, 'community'),
          connections,
        });
      },
      enterNode: (e) => {
        const nd = sigma.getGraph().getNodeAttribute(e.node, 'originalData');
        const vp = sigma.graphToViewport({
          x: sigma.getGraph().getNodeAttribute(e.node, 'x'),
          y: sigma.getGraph().getNodeAttribute(e.node, 'y'),
        });
        onHover({
          node: {
            ...nd,
            id: e.node,
            degree: sigma.getGraph().degree(e.node),
            community: sigma.getGraph().getNodeAttribute(e.node, 'community'),
            betweenness: sigma.getGraph().getNodeAttribute(e.node, 'betweenness'),
          },
          x: vp.x,
          y: vp.y,
        });
        sigma.getGraph().setNodeAttribute(e.node, 'highlighted', true);
        document.body.style.cursor = 'pointer';
      },
      leaveNode: (e) => {
        onHover(null);
        if (sigma.getGraph().hasNode(e.node)) sigma.getGraph().removeNodeAttribute(e.node, 'highlighted');
        document.body.style.cursor = 'default';
      },
      downNode: (e) => {
        isDragging.current = true;
        draggedNode.current = e.node;
        sigma.getGraph().setNodeAttribute(e.node, 'highlighted', true);
        sigma.getCamera().disable();
      },
      mousemovebody: (e: any) => {
        if (isDragging.current && draggedNode.current) {
          const pos = sigma.viewportToGraph(e);
          sigma.getGraph().setNodeAttribute(draggedNode.current, 'x', pos.x);
          sigma.getGraph().setNodeAttribute(draggedNode.current, 'y', pos.y);
          if (e.preventSigmaDefault) e.preventSigmaDefault();
          e.original?.preventDefault?.();
        }
      },
      mouseup: () => {
        if (isDragging.current && draggedNode.current) {
          sigma.getGraph().removeNodeAttribute(draggedNode.current, 'highlighted');
          sigma.getCamera().enable();
        }
        isDragging.current = false;
        draggedNode.current = null;
      },
    });
  }, [registerEvents, sigma, onNodeClick, onHover]);

  return null;
}

function ZoomControls() {
  const sigma = useSigma();
  return (
    <div className="absolute bottom-16 right-4 z-30 bg-white/95 backdrop-blur rounded-lg border border-slate-200 shadow-lg flex flex-col">
      <button onClick={() => sigma.getCamera().animatedZoom({ duration: 200 })} className="p-2.5 hover:bg-indigo-50 rounded-t-lg text-slate-600 hover:text-indigo-600 transition-colors" title="Zoom In"><ZoomIn size={15} /></button>
      <div className="border-t border-slate-100" />
      <button onClick={() => sigma.getCamera().animatedUnzoom({ duration: 200 })} className="p-2.5 hover:bg-indigo-50 text-slate-600 hover:text-indigo-600 transition-colors" title="Zoom Out"><ZoomOut size={15} /></button>
      <div className="border-t border-slate-100" />
      <button onClick={() => sigma.getCamera().animatedReset({ duration: 250 })} className="p-2.5 hover:bg-indigo-50 rounded-b-lg text-slate-600 hover:text-indigo-600 transition-colors" title="Fit to Screen"><Maximize2 size={15} /></button>
    </div>
  );
}

// ── EXPLANATORY GUIDE MODAL ──
function NetworkGuideModal({ onClose }: { onClose: () => void }) {
  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]">
        <div className="px-6 py-4 bg-gradient-to-r from-indigo-900 via-indigo-800 to-slate-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-white/10 rounded-lg"><Compass size={20} className="text-indigo-300" /></div>
            <div>
              <h2 className="text-base font-bold">How to Explore &amp; Extract Network Insights</h2>
              <p className="text-xs text-indigo-200">Interactive Guide to the Energy Innovation Knowledge Graph</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-colors"><X size={18} /></button>
        </div>

        <div className="p-6 overflow-y-auto space-y-5 text-[13px] text-slate-600 leading-relaxed">
          <div>
            <h3 className="text-sm font-semibold text-slate-900 mb-1.5 flex items-center gap-2"><Layers size={16} className="text-indigo-600" /> 1. Semantic Node Hierarchy</h3>
            <p>Every node represents an innovation entity with visual semantics:</p>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-2">
              {Object.entries(NODE_LABELS).map(([t, l]) => (
                <div key={t} className="p-2 bg-slate-50 rounded-lg border border-slate-100 flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: NODE_COLORS[t] }} />
                  <span className="font-medium text-slate-800 text-[11px]">{l}</span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-slate-900 mb-1.5 flex items-center gap-2"><Sparkles size={16} className="text-amber-500" /> 2. Community &amp; Thematic Clusters</h3>
            <p>
              The graph automatically groups tightly interconnected programs, technologies, and awardees using the <strong>Louvain Modularity Algorithm</strong>.
              Toggle <strong>Color by Cluster</strong> to reveal innovation thematic boundaries.
            </p>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-slate-900 mb-1.5 flex items-center gap-2"><TrendingUp size={16} className="text-emerald-600" /> 3. Centrality &amp; Bridge Connectors</h3>
            <ul className="list-disc pl-5 space-y-1 text-slate-600">
              <li><strong>Degree Centrality (Hubs)</strong>: Agencies and technologies with the widest reach across programs.</li>
              <li><strong>Betweenness Centrality (Bridges)</strong>: Awardees connecting otherwise separate technological or agency silos.</li>
              <li><strong>PageRank (Authority)</strong>: High-influence nodes receiving connections from other highly-funded entities.</li>
            </ul>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-slate-900 mb-1.5 flex items-center gap-2"><Sliders size={16} className="text-indigo-600" /> 4. De-cluttering &amp; Density Management</h3>
            <p>
              Use the <strong>Min Degree Slider</strong> to filter out peripheral leaf nodes and uncover the core structural spine of the ecosystem.
            </p>
          </div>
        </div>

        <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 flex justify-end">
          <button onClick={onClose} className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-xs font-semibold hover:bg-indigo-700 transition-colors shadow-sm">Got it, Let's Explore</button>
        </div>
      </div>
    </div>
  );
}

// ── CENTRALITY & BRIDGE ANALYTICS DRAWER ──
function CentralityDrawer({
  topCentrality, topBetweenness, topPageRank, onClose, onSelectNode
}: {
  topCentrality: any[]; topBetweenness: any[]; topPageRank: any[];
  onClose: () => void; onSelectNode: (node: any) => void;
}) {
  const [tab, setTab] = useState<'hubs' | 'bridges' | 'influence'>('bridges');
  const items = tab === 'hubs' ? topCentrality : tab === 'bridges' ? topBetweenness : topPageRank;

  return (
    <div className="fixed right-0 top-0 bottom-0 w-96 bg-white shadow-2xl z-50 border-l border-slate-200 flex flex-col">
      <div className="p-4 border-b border-slate-100 bg-slate-900 text-white flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BarChart3 size={18} className="text-indigo-400" />
          <h2 className="text-sm font-bold">Network Centrality &amp; Bridges</h2>
        </div>
        <button onClick={onClose} className="p-1 rounded text-slate-400 hover:text-white hover:bg-white/10"><X size={16} /></button>
      </div>

      <div className="flex border-b border-slate-200 bg-slate-50 p-1">
        <button onClick={() => setTab('bridges')} className={clsx('flex-1 py-1.5 text-xs font-medium rounded transition-colors', tab === 'bridges' ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-500 hover:text-slate-800')}>Bridges ({topBetweenness.length})</button>
        <button onClick={() => setTab('hubs')} className={clsx('flex-1 py-1.5 text-xs font-medium rounded transition-colors', tab === 'hubs' ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-500 hover:text-slate-800')}>Top Hubs ({topCentrality.length})</button>
        <button onClick={() => setTab('influence')} className={clsx('flex-1 py-1.5 text-xs font-medium rounded transition-colors', tab === 'influence' ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-500 hover:text-slate-800')}>PageRank ({topPageRank.length})</button>
      </div>

      <div className="p-3 bg-indigo-50/50 border-b border-indigo-100 text-[11px] text-indigo-900 leading-snug">
        {tab === 'bridges' && 'Bridge nodes connect distinct funding silos and technological clusters. High betweenness indicates critical cross-domain intermediaries.'}
        {tab === 'hubs' && 'Hub nodes have the highest direct degree connectivity across the innovation ecosystem.'}
        {tab === 'influence' && 'PageRank highlights nodes connected to other influential, highly-funded organizations and programs.'}
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {items.map((item, idx) => {
          const d = item.data;
          return (
            <button key={item.node} onClick={() => onSelectNode(d)}
              className="w-full text-left p-3 rounded-xl border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/30 transition-all group">
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-1.5">
                  <span className="w-5 h-5 rounded-full bg-slate-100 text-slate-600 text-[10px] font-bold flex items-center justify-center group-hover:bg-indigo-600 group-hover:text-white transition-colors">#{idx + 1}</span>
                  <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: NODE_COLORS[d.type] || '#64748b' }} />
                  <span className="text-[12px] font-semibold text-slate-800 group-hover:text-indigo-900 truncate max-w-[180px]">{d.name}</span>
                </div>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 capitalize">{d.type}</span>
              </div>
              <div className="mt-2 flex items-center justify-between text-[11px] text-slate-500">
                <span>Degree: <strong className="text-slate-700">{item.degree}</strong></span>
                {tab === 'bridges' && <span>Betweenness: <strong className="text-indigo-700">{(item.betweenness * 100).toFixed(2)}%</strong></span>}
                {tab === 'influence' && <span>PageRank: <strong className="text-emerald-700">{(item.pagerank * 1000).toFixed(1)}</strong></span>}
                {d.funding && <span className="font-semibold text-emerald-700">{fmt(d.funding)}</span>}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

// ── AUTOMATED INSIGHTS DRAWER ──
function InsightsDrawer({ analyticsData, onClose, onSelectAgency, onSelectTech }: {
  analyticsData: any; onClose: () => void;
  onSelectAgency: (a: string) => void; onSelectTech: (t: string) => void;
}) {
  const [insightFilter, setInsightFilter] = useState<'all' | 'anchors' | 'tech' | 'strategy'>('all');
  const insights = analyticsData?.insights || [];
  const synergies = analyticsData?.cross_agency_synergies || [];
  const bridgeAwardees = analyticsData?.bridge_awardees || [];
  const stateCorridors = analyticsData?.state_corridors || [];
  const summary = analyticsData?.summary || {};

  const filteredInsights = useMemo(() => {
    if (insightFilter === 'all') return insights;
    if (insightFilter === 'anchors') return insights.filter((ins: any) => ['Funder Anchor', 'Bridge Connector', 'Capital Concentration'].includes(ins.category));
    if (insightFilter === 'tech') return insights.filter((ins: any) => ['Tech Convergence', 'Agency Synergy'].includes(ins.category));
    if (insightFilter === 'strategy') return insights.filter((ins: any) => ['Geographic Flow', 'Strategic Positioning'].includes(ins.category));
    return insights;
  }, [insights, insightFilter]);

  return (
    <div className="fixed right-0 top-0 bottom-0 w-[450px] bg-white shadow-2xl z-50 border-l border-slate-200 flex flex-col">
      <div className="p-4 border-b border-slate-100 bg-gradient-to-r from-indigo-950 via-indigo-900 to-slate-900 text-white flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-amber-400/20 rounded-xl border border-amber-400/30">
            <Sparkles size={18} className="text-amber-300" />
          </div>
          <div>
            <h2 className="text-sm font-bold tracking-tight">Network Intelligence Discoveries</h2>
            <p className="text-[11px] text-indigo-200">Automated topological &amp; structural analytics</p>
          </div>
        </div>
        <button onClick={onClose} className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"><X size={16} /></button>
      </div>

      {/* Summary Stat Strip */}
      <div className="grid grid-cols-3 gap-2 p-3 bg-slate-50 border-b border-slate-200 text-center">
        <div className="p-2 bg-white rounded-lg border border-slate-200/80 shadow-xs">
          <div className="text-[10px] uppercase font-semibold text-slate-400">Tracked Funding</div>
          <div className="text-xs font-bold text-emerald-700">{summary.total_tracked_funding ? fmt(summary.total_tracked_funding) : '$98.9B+'}</div>
        </div>
        <div className="p-2 bg-white rounded-lg border border-slate-200/80 shadow-xs">
          <div className="text-[10px] uppercase font-semibold text-slate-400">Bridge Awardees</div>
          <div className="text-xs font-bold text-indigo-700">{bridgeAwardees.length} Multi-Funder</div>
        </div>
        <div className="p-2 bg-white rounded-lg border border-slate-200/80 shadow-xs">
          <div className="text-[10px] uppercase font-semibold text-slate-400">Cross Synergies</div>
          <div className="text-xs font-bold text-purple-700">{synergies.length} Agency Pairs</div>
        </div>
      </div>

      {/* Category Tab Filter */}
      <div className="flex border-b border-slate-200 bg-white p-1 gap-1">
        <button onClick={() => setInsightFilter('all')} className={clsx('flex-1 py-1.5 text-[11px] font-semibold rounded-md transition-colors', insightFilter === 'all' ? 'bg-indigo-50 text-indigo-700 border border-indigo-200' : 'text-slate-500 hover:text-slate-800')}>All ({insights.length})</button>
        <button onClick={() => setInsightFilter('anchors')} className={clsx('flex-1 py-1.5 text-[11px] font-semibold rounded-md transition-colors', insightFilter === 'anchors' ? 'bg-indigo-50 text-indigo-700 border border-indigo-200' : 'text-slate-500 hover:text-slate-800')}>Anchors &amp; Bridges</button>
        <button onClick={() => setInsightFilter('tech')} className={clsx('flex-1 py-1.5 text-[11px] font-semibold rounded-md transition-colors', insightFilter === 'tech' ? 'bg-indigo-50 text-indigo-700 border border-indigo-200' : 'text-slate-500 hover:text-slate-800')}>Tech &amp; Synergies</button>
        <button onClick={() => setInsightFilter('strategy')} className={clsx('flex-1 py-1.5 text-[11px] font-semibold rounded-md transition-colors', insightFilter === 'strategy' ? 'bg-indigo-50 text-indigo-700 border border-indigo-200' : 'text-slate-500 hover:text-slate-800')}>Strategy</button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-5">
        <div>
          <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2.5 flex items-center justify-between">
            <span className="flex items-center gap-1.5"><Activity size={13} className="text-indigo-600" /> Key Structural Discoveries</span>
            <span className="text-[10px] font-normal text-slate-400">{filteredInsights.length} discoveries</span>
          </h3>
          <div className="space-y-3">
            {filteredInsights.map((ins: any, i: number) => (
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

        {synergies.length > 0 && (
          <div>
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5"><Share2 size={13} className="text-emerald-600" /> Cross-Agency Co-Investment Synergies</h3>
            <div className="space-y-2">
              {synergies.slice(0, 8).map((syn: any, i: number) => (
                <div key={i} className="p-2.5 bg-slate-50 rounded-xl border border-slate-200 text-xs hover:border-indigo-300 transition-colors">
                  <div className="flex items-center justify-between font-semibold text-slate-800 mb-1">
                    <span className="truncate pr-2 cursor-pointer hover:text-indigo-600" onClick={() => onSelectAgency(syn.agency_a)}>{syn.agency_a} &amp; {syn.agency_b}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold shrink-0">{syn.shared_technologies_count} Shared Sectors</span>
                  </div>
                  <div className="flex flex-wrap gap-1 mt-1.5">
                    {syn.shared_technologies?.map((tech: string, ti: number) => (
                      <span key={ti} onClick={() => onSelectTech(tech)} className="text-[10px] px-1.5 py-0.5 rounded bg-white text-slate-600 border border-slate-200 hover:border-indigo-300 hover:text-indigo-600 cursor-pointer transition-colors">{tech}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {bridgeAwardees.length > 0 && (
          <div>
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5"><Users size={13} className="text-violet-600" /> Top Multi-Agency Bridge Awardees</h3>
            <div className="space-y-1.5">
              {bridgeAwardees.slice(0, 10).map((aw: any, i: number) => (
                <div key={i} className="p-2.5 bg-slate-50 rounded-lg border border-slate-100 text-xs flex items-center justify-between hover:border-indigo-200 transition-colors">
                  <div className="min-w-0 pr-2">
                    <span className="font-semibold text-slate-800 block truncate">{aw.name}</span>
                    <span className="text-[10px] text-slate-500">{aw.location} &middot; {aw.award_count} awards &middot; <strong className="text-indigo-600">{aw.agency_count} agencies</strong></span>
                  </div>
                  <span className="font-bold text-emerald-700 shrink-0">{fmt(aw.total_funding)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {stateCorridors.length > 0 && (
          <div>
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5"><Globe size={13} className="text-sky-600" /> Top Regional Clean Energy Corridors</h3>
            <div className="grid grid-cols-2 gap-2">
              {stateCorridors.slice(0, 6).map((st: any, i: number) => (
                <div key={i} className="p-2.5 bg-slate-50 rounded-lg border border-slate-200/80 text-xs">
                  <div className="flex items-center justify-between font-bold text-slate-800">
                    <span>{st.state} State</span>
                    <span className="text-[10px] text-emerald-700 font-extrabold">{fmt(st.funding)}</span>
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5">{st.recipients.toLocaleString()} awardees &middot; {st.award_count.toLocaleString()} awards</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


// ── NODE DETAIL PANEL ──
function DetailPanel({
  node, onClose, onNavigate, onFindPathFromHere, onIsolate
}: {
  node: any; onClose: () => void; onNavigate: (n: any) => void;
  onFindPathFromHere: (n: any) => void; onIsolate: (n: any) => void;
}) {
  const { data: detail, isLoading } = useQuery<any>({
    queryKey: ['node-detail', node.type, node.db_id || node.name],
    queryFn: () => api.getNodeDetail(node.type, node.db_id || node.name),
    enabled: !!node && (node.type === 'organization' || node.type === 'opportunity' || node.type === 'awardee'),
  });

  const d = detail || node;
  const connections = node.connections || [];
  const byType: Record<string, any[]> = {};
  connections.forEach((c: any) => {
    const t = c.node?.type || 'other';
    byType[t] = byType[t] || [];
    byType[t].push(c);
  });

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-xl flex flex-col w-96 max-h-full overflow-hidden shrink-0">
      <div className="px-4 py-3 border-b border-slate-100 bg-gradient-to-r from-slate-50 to-white rounded-t-xl">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap gap-1 mb-1.5">
              <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold text-white" style={{ backgroundColor: NODE_COLORS[node.type] || '#64748b' }}>
                {NODE_ICONS[node.type]} {NODE_LABELS[node.type] || node.type}
              </span>
              {node.agency && <div className="flex items-center gap-1"><OrgLogo org={node.agency} size="xs" /><span className="text-[10px] font-medium text-slate-600">{node.agency}</span></div>}
              {node.status && <span className={clsx("px-1.5 py-0.5 rounded text-[10px] font-medium border", node.status === 'open' ? "bg-green-50 text-green-700 border-green-200" : "bg-slate-50 text-slate-600 border-slate-200")}>{node.status}</span>}
              {node.degree !== undefined && <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-100">Degree: {node.degree}</span>}
            </div>
            <h2 className="text-[14px] font-bold text-slate-900 leading-snug">{node.name || 'Unknown'}</h2>
            {node.solicitation_number && <p className="text-[11px] text-slate-400 font-mono mt-0.5">{node.solicitation_number}</p>}
          </div>
          <button onClick={onClose} className="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors shrink-0"><X size={14} /></button>
        </div>

        <div className="flex items-center gap-1.5 mt-2.5 pt-2 border-t border-slate-100">
          <button onClick={() => onIsolate(node)} className="flex-1 py-1 px-2 rounded bg-amber-50 text-amber-700 hover:bg-amber-100 text-[10px] font-semibold border border-amber-200 flex items-center justify-center gap-1 transition-colors"><Crosshair size={11} /> Isolate Ego</button>
          <button onClick={() => onFindPathFromHere(node)} className="flex-1 py-1 px-2 rounded bg-indigo-50 text-indigo-700 hover:bg-indigo-100 text-[10px] font-semibold border border-indigo-200 flex items-center justify-center gap-1 transition-colors"><GitFork size={11} /> Trace Path</button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 max-h-[60vh]">
        {isLoading && <div className="flex justify-center py-8"><Loader2 className="animate-spin text-slate-300" size={20} /></div>}

        {(node.funding || node.award_count || d.total_funding) && (
          <div className="grid grid-cols-2 gap-2 bg-emerald-50/50 p-3 rounded-lg border border-emerald-100">
            {(node.funding || d.funding || d.total_funding) && <div><span className="block text-[9px] font-semibold text-slate-500 uppercase">Funding</span><span className="text-lg font-bold text-emerald-700">{fmt(node.funding || d.funding || d.total_funding)}</span></div>}
            {(node.award_count || d.award_count) && <div><span className="block text-[9px] font-semibold text-slate-500 uppercase">Awards</span><span className="text-lg font-bold text-slate-800">{(node.award_count || d.award_count)?.toLocaleString()}</span></div>}
            {d.max_award && <div><span className="block text-[9px] font-semibold text-slate-500 uppercase">Max Award</span><span className="text-sm font-semibold text-slate-700">{fmt(d.max_award)}</span></div>}
            {node.employees && <div><span className="block text-[9px] font-semibold text-slate-500 uppercase">Employees</span><span className="text-sm font-semibold text-slate-700">{node.employees?.toLocaleString()}</span></div>}
          </div>
        )}

        {(d.description || node.description) && (
          <div>
            <h3 className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1">Description</h3>
            <p className="text-[12px] text-slate-600 leading-relaxed line-clamp-4">{d.description || node.description}</p>
          </div>
        )}

        {connections.length > 0 && (
          <div>
            <h3 className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Network Connections ({connections.length})</h3>
            {Object.entries(byType).map(([type, conns]) => (
              <div key={type} className="mb-2">
                <div className="text-[9px] font-semibold text-slate-400 uppercase tracking-wider mb-1 flex items-center gap-1">
                  {NODE_ICONS[type]} {NODE_LABELS[type] || type} ({conns.length})
                </div>
                <div className="space-y-1">
                  {conns.slice(0, 6).map((c: any, i: number) => (
                    <button key={i} onClick={() => onNavigate(c.node)}
                      className="w-full text-left p-1.5 bg-slate-50 rounded border border-slate-100 text-[11px] hover:bg-indigo-50 hover:border-indigo-200 transition-colors group flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: NODE_COLORS[c.node?.type] || '#64748b' }} />
                      <span className="truncate flex-1 text-slate-700">{c.node?.name || '?'}</span>
                      <span className="text-[9px] px-1 py-0.5 rounded capitalize" style={{ color: EDGE_COLORS[c.edge?.type] || '#94a3b8' }}>{EDGE_LABELS[c.edge?.type] || c.edge?.type || ''}</span>
                      <ChevronRight size={10} className="text-slate-300 group-hover:text-indigo-500 shrink-0" />
                    </button>
                  ))}
                  {conns.length > 6 && <p className="text-[10px] text-slate-400 text-center">+{conns.length - 6} more</p>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="px-3 py-2 border-t border-slate-100 bg-slate-50 flex items-center gap-2 rounded-b-xl">
        {(d.source_url || d.detail_url || node.source_url) && (
          <a href={d.detail_url || d.source_url || node.source_url} target="_blank" rel="noopener noreferrer"
            className="flex-1 flex items-center justify-center gap-1 px-2 py-1.5 text-[11px] font-medium text-indigo-700 bg-indigo-50 rounded hover:bg-indigo-100 transition-colors border border-indigo-200">
            <ExternalLink size={11} /> View Source
          </a>
        )}
        <button onClick={onClose} className="px-3 py-1.5 text-[11px] font-medium text-slate-600 bg-white rounded border border-slate-200 hover:bg-slate-100 transition-colors">Close</button>
      </div>
    </div>
  );
}

// ── MAIN NETWORK COMPONENT ──
export default function Network() {
  const { includeNyserda, isNyserda } = useNyserda();
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [hoverInfo, setHoverInfo] = useState<{ node: any; x: number; y: number } | null>(null);
  const [highlightedType, setHighlightedType] = useState<string | null>(null);
  const [neighborhoodNode, setNeighborhoodNode] = useState<string | null>(null);
  const [exportOpen, setExportOpen] = useState(false);
  const [filtersOpen, setFiltersOpen] = useState(true);
  const [agencyFilter, setAgencyFilter] = useState('');
  const [entityFilter, setEntityFilter] = useState('organization,opportunity,awardee,technology,sector,program,fuel');
  const [statusFilter, setStatusFilter] = useState('');
  const [yearMin, setYearMin] = useState<number | ''>('');
  const [yearMax, setYearMax] = useState<number | ''>('');
  const [nodeLimit, setNodeLimit] = useState(800);

  // Clear agencyFilter if NYSERDA is excluded and was selected
  useEffect(() => {
    if (!includeNyserda && agencyFilter && isNyserda(agencyFilter)) {
      setAgencyFilter('');
    }
  }, [includeNyserda, agencyFilter, isNyserda]);

  // Advanced Exploration States
  const [minDegree, setMinDegree] = useState(1);
  const [colorMode, setColorMode] = useState<'type' | 'cluster'>('type');
  const [selectedCluster, setSelectedCluster] = useState<number | null>(null);
  const [layoutType, setLayoutType] = useState<'forceAtlas2' | 'circular' | 'radial'>('forceAtlas2');

  const [guideOpen, setGuideOpen] = useState(false);
  const [centralityOpen, setCentralityOpen] = useState(false);
  const [insightsOpen, setInsightsOpen] = useState(false);
  const [nytExportOpen, setNytExportOpen] = useState(false);

  // Pathfinder state
  const [pathStart, setPathStart] = useState<any | null>(null);
  const [pathEnd, setPathEnd] = useState<any | null>(null);
  const [pathNodes, setPathNodes] = useState<string[]>([]);
  const [pathMode, setPathMode] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(t);
  }, [search]);

  const { data: graphData, isLoading } = useQuery({
    queryKey: ['knowledge-graph', agencyFilter, entityFilter, statusFilter, yearMin, yearMax, nodeLimit, includeNyserda],
    queryFn: () => api.getKnowledgeGraph({
      entity_types: entityFilter,
      agency: agencyFilter || undefined,
      status: statusFilter || undefined,
      year_min: yearMin || undefined,
      year_max: yearMax || undefined,
      node_limit: nodeLimit,
      exclude_nyserda: !includeNyserda,
    }),
  });

  const { data: analyticsData } = useQuery({
    queryKey: ['network-analytics', agencyFilter, yearMin, yearMax, includeNyserda],
    queryFn: () => api.getNetworkAnalytics({
      agency: agencyFilter || undefined,
      year_min: yearMin || undefined,
      year_max: yearMax || undefined,
      exclude_nyserda: !includeNyserda,
    }),
  });

  const allNodes = useMemo(() => {
    const nodes = graphData?.nodes || [];
    if (includeNyserda) return nodes;
    return nodes.filter((n: any) => !isNyserda(n.name) && !isNyserda(n.agency));
  }, [graphData, includeNyserda, isNyserda]);

  const allEdges = useMemo(() => {
    const edges = graphData?.edges || [];
    if (includeNyserda) return edges;
    const validNodeIds = new Set(allNodes.map((n: any) => n.id));
    return edges.filter((e: any) => validNodeIds.has(e.source) && validNodeIds.has(e.target));
  }, [graphData, allNodes, includeNyserda]);

  const summary = graphData?.summary || {};

  // Build and compute graph statically (Deterministic, Runs Once Per Filter Change)
  const { graph, clusters, topCentrality, topBetweenness, topPageRank, stats } = useMemo(() => {
    if (!allNodes.length) {
      return {
        graph: null, clusters: [], topCentrality: [], topBetweenness: [], topPageRank: [],
        stats: { nodes: 0, edges: 0, density: 0, clusters: 0 }
      };
    }

    const g = new Graph({ multi: true });
    const degreeMap = new Map<string, number>();

    allEdges.forEach((e: any) => {
      degreeMap.set(e.source, (degreeMap.get(e.source) || 0) + 1);
      degreeMap.set(e.target, (degreeMap.get(e.target) || 0) + 1);
    });

    const activeTypes = new Set(entityFilter.split(',').map(s => s.trim().toLowerCase()).filter(Boolean));
    const validNodes = allNodes.filter((n: any) => {
      if (activeTypes.size > 0 && !activeTypes.has(n.type)) return false;
      return (degreeMap.get(n.id) || 0) >= minDegree;
    });
    const validSet = new Set(validNodes.map((n: any) => n.id));

    // Deterministic golden-ratio spiral positioning (avoids random jitter and rotation)
    validNodes.forEach((node: any, idx: number) => {
      const degree = degreeMap.get(node.id) || 0;
      const baseSize = node.type === 'organization' ? 14 : node.type === 'program' ? 10 :
        node.type === 'awardee' ? 7 : node.type === 'opportunity' ? 5 :
        node.type === 'technology' ? 6 : node.type === 'sector' ? 6 : 4;
      const fundingBoost = node.funding ? Math.log10(Math.max(node.funding, 1000)) * 1.3 : 0;
      const size = Math.max(3.5, Math.min(26, baseSize + degree * 0.35 + fundingBoost));

      // Deterministic angle & radius
      const angle = idx * 2.399963; // golden angle in radians
      const r = Math.sqrt(idx + 1) * 6;
      const x = r * Math.cos(angle);
      const y = r * Math.sin(angle);

      const label = node.name || '';

      g.addNode(node.id, {
        x,
        y,
        size,
        baseSize: size,
        label: degree > 0 || node.type === 'organization' || node.type === 'program'
          ? (label.length > 28 ? label.substring(0, 28) + '\u2026' : label) : '',
        typeColor: NODE_COLORS[node.type] || '#64748b',
        color: NODE_COLORS[node.type] || '#64748b',
        originalData: node,
        zIndex: node.type === 'organization' ? 10 : 1,
        borderColor: node.status === 'open' ? '#22c55e' : undefined,
      });
    });

    allEdges.forEach((edge: any) => {
      if (!validSet.has(edge.source) || !validSet.has(edge.target)) return;
      if (!g.hasNode(edge.source) || !g.hasNode(edge.target)) return;
      const edgeId = `${edge.source}|${edge.target}|${edge.type}`;
      if (g.hasEdge(edgeId)) return;

      const isFunding = ['funds', 'awarded_to', 'funder'].includes(edge.type);
      try {
        g.addEdgeWithKey(edgeId, edge.source, edge.target, {
          color: EDGE_COLORS[edge.type] || '#cbd5e1',
          baseEdgeColor: EDGE_COLORS[edge.type] || '#cbd5e1',
          size: isFunding ? 2 : edge.type === 'stackable' ? 1.5 : 0.8,
          type: 'line',
          originalData: edge,
        });
      } catch { /* skip */ }
    });

    // Louvain Community Detection (Deterministic resolution)
    const clusterMap = new Map<number, { id: number; nodes: any[]; dominantType: string; totalFunding: number; label: string }>();
    if (g.order > 2) {
      try {
        louvain.assign(g, { resolution: 1.0 });
        g.forEachNode((node, attrs) => {
          const comm = attrs.community ?? 0;
          if (!clusterMap.has(comm)) {
            clusterMap.set(comm, { id: comm, nodes: [], dominantType: '', totalFunding: 0, label: '' });
          }
          const cObj = clusterMap.get(comm)!;
          cObj.nodes.push(attrs.originalData);
          cObj.totalFunding += (attrs.originalData?.funding || 0);

          const clusterColor = CLUSTER_PALETTE[comm % CLUSTER_PALETTE.length];
          g.setNodeAttribute(node, 'clusterColor', clusterColor);
        });

        clusterMap.forEach((c) => {
          const techNames: string[] = [];
          c.nodes.forEach((n: any) => {
            if (n.type === 'technology' || n.type === 'program' || n.type === 'sector') {
              if (n.name) techNames.push(n.name);
            }
          });
          const topTech = techNames.slice(0, 2).join(' & ') || 'Energy Innovation';
          c.label = `Cluster ${c.id + 1}: ${topTech} (${c.nodes.length})`;
        });
      } catch (err) {
        console.warn('Louvain error:', err);
      }
    }

    // Centrality metrics
    let topC: any[] = [];
    let topB: any[] = [];
    let topPR: any[] = [];

    if (g.order > 2) {
      try {
        const betMap = betweennessCentrality(g);
        const prMap = pagerankCentrality(g);

        const nodeMetrics: any[] = [];
        g.forEachNode((node, attrs) => {
          const d = attrs.originalData;
          const deg = g.degree(node);
          const bet = betMap[node] || 0;
          const pr = prMap[node] || 0;
          g.setNodeAttribute(node, 'betweenness', bet);
          g.setNodeAttribute(node, 'pagerank', pr);
          nodeMetrics.push({ node, data: d, degree: deg, betweenness: bet, pagerank: pr });
        });

        topC = [...nodeMetrics].sort((a, b) => b.degree - a.degree).slice(0, 10);
        topB = [...nodeMetrics].sort((a, b) => b.betweenness - a.betweenness).slice(0, 10);
        topPR = [...nodeMetrics].sort((a, b) => b.pagerank - a.pagerank).slice(0, 10);
      } catch (err) {
        console.warn('Centrality error:', err);
      }
    }

    // Apply Static Layout (Synchronous, 0 runtime motion)
    if (g.order > 0) {
      try {
        if (layoutType === 'circular') {
          const nTotal = g.order;
          let i = 0;
          g.forEachNode((node) => {
            const angle = (i / nTotal) * Math.PI * 2;
            g.setNodeAttribute(node, 'x', 75 * Math.cos(angle));
            g.setNodeAttribute(node, 'y', 75 * Math.sin(angle));
            i++;
          });
        } else if (layoutType === 'radial') {
          let idx = 0;
          g.forEachNode((node) => {
            const deg = g.degree(node);
            const radius = Math.max(12, 85 - Math.min(65, deg * 4));
            const angle = idx * 2.399963;
            g.setNodeAttribute(node, 'x', radius * Math.cos(angle));
            g.setNodeAttribute(node, 'y', radius * Math.sin(angle));
            idx++;
          });
        } else {
          // ForceAtlas2 single-pass static layout
          const fa2Settings = forceAtlas2.inferSettings(g);
          fa2Settings.gravity = 1.8;
          fa2Settings.scalingRatio = 3.0;
          fa2Settings.barnesHutOptimize = g.order > 150;
          forceAtlas2.assign(g, {
            iterations: Math.min(180, Math.max(80, 400 - g.order)),
            settings: fa2Settings,
          });
        }
      } catch { /* layout fallback */ }
    }

    const density = g.order > 1 ? (2 * g.size) / (g.order * (g.order - 1)) : 0;
    const computedClusters = Array.from(clusterMap.values()).sort((a, b) => b.nodes.length - a.nodes.length);

    return {
      graph: g,
      clusters: computedClusters,
      topCentrality: topC,
      topBetweenness: topB,
      topPageRank: topPR,
      stats: { nodes: g.order, edges: g.size, density, clusters: computedClusters.length }
    };
  }, [allNodes, allEdges, minDegree, layoutType]);

  const handleNodeClick = useCallback((node: any) => {
    if (pathMode) {
      if (!pathStart) {
        setPathStart(node);
      } else if (!pathEnd && node.id !== pathStart.id) {
        setPathEnd(node);
      }
    } else {
      setSelectedNode(node);
    }
  }, [pathMode, pathStart, pathEnd]);

  const handleHover = useCallback((info: { node: any; x: number; y: number } | null) => setHoverInfo(info), []);
  const handleNavigate = useCallback((node: any) => {
    setSelectedNode(node);
    setNeighborhoodNode(null);
  }, []);

  const handleFindPathFromHere = useCallback((node: any) => {
    setPathStart(node);
    setPathEnd(null);
    setPathNodes([node.id]);
    setPathMode(true);
  }, []);

  const handleIsolate = useCallback((node: any) => {
    setNeighborhoodNode(node.id);
  }, []);

  // Compute Shortest Path
  useEffect(() => {
    if (pathStart && pathEnd && graph) {
      if (graph.hasNode(pathStart.id) && graph.hasNode(pathEnd.id)) {
        const queue: string[][] = [[pathStart.id]];
        const visited = new Set<string>([pathStart.id]);
        let foundPath: string[] = [];

        while (queue.length > 0) {
          const currentPath = queue.shift()!;
          const currentNode = currentPath[currentPath.length - 1];

          if (currentNode === pathEnd.id) {
            foundPath = currentPath;
            break;
          }

          graph.forEachNeighbor(currentNode, (neighbor) => {
            if (!visited.has(neighbor)) {
              visited.add(neighbor);
              queue.push([...currentPath, neighbor]);
            }
          });
        }

        setPathNodes(foundPath.length > 0 ? foundPath : [pathStart.id, pathEnd.id]);
      }
    } else if (!pathMode) {
      setPathNodes([]);
    }
  }, [pathStart, pathEnd, graph, pathMode]);

  const selectedEntityTypes = useMemo(() => {
    return new Set(entityFilter.split(',').map(s => s.trim().toLowerCase()).filter(Boolean));
  }, [entityFilter]);

  const toggleEntity = (type: string) => {
    const current = new Set(entityFilter.split(',').map(s => s.trim().toLowerCase()).filter(Boolean));
    if (current.has(type)) {
      current.delete(type);
    } else {
      current.add(type);
    }
    setEntityFilter(Array.from(current).join(','));
  };

  const selectAllEntities = () => {
    setEntityFilter(Object.keys(NODE_LABELS).join(','));
  };

  const clearAllEntities = () => {
    setEntityFilter('');
  };

  const generateHighDefGraphCanvas = (graphInstance: any, width = 3200, height = 2000): HTMLCanvasElement | null => {
    if (!graphInstance || graphInstance.order === 0) return null;
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;

    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';

    // 1. Deep Obsidian Aurora Background
    ctx.fillStyle = '#080C17';
    ctx.fillRect(0, 0, width, height);

    // Subtle Radial Background Glows
    const bgGlow1 = ctx.createRadialGradient(width * 0.3, height * 0.3, 10, width * 0.3, height * 0.3, width * 0.45);
    bgGlow1.addColorStop(0, 'rgba(0, 245, 160, 0.06)');
    bgGlow1.addColorStop(1, 'rgba(8, 12, 23, 0)');
    ctx.fillStyle = bgGlow1;
    ctx.fillRect(0, 0, width, height);

    const bgGlow2 = ctx.createRadialGradient(width * 0.7, height * 0.7, 10, width * 0.7, height * 0.7, width * 0.45);
    bgGlow2.addColorStop(0, 'rgba(0, 229, 255, 0.07)');
    bgGlow2.addColorStop(1, 'rgba(8, 12, 23, 0)');
    ctx.fillStyle = bgGlow2;
    ctx.fillRect(0, 0, width, height);

    // Subtle Grid Lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.025)';
    ctx.lineWidth = 1;
    const gridStep = 100;
    for (let x = 0; x < width; x += gridStep) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += gridStep) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // 2. Compute Coordinate Extents
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    graphInstance.forEachNode((_node: string, attrs: any) => {
      if (attrs.x !== undefined && attrs.y !== undefined) {
        if (attrs.x < minX) minX = attrs.x;
        if (attrs.x > maxX) maxX = attrs.x;
        if (attrs.y < minY) minY = attrs.y;
        if (attrs.y > maxY) maxY = attrs.y;
      }
    });

    const spanX = (maxX - minX) || 1;
    const spanY = (maxY - minY) || 1;
    const padX = width * 0.08;
    const padY = height * 0.08;
    const drawW = width - padX * 2;
    const drawH = height - padY * 2;
    const scale = Math.min(drawW / spanX, drawH / spanY);
    const offsetX = padX + (drawW - spanX * scale) / 2;
    const offsetY = padY + (drawH - spanY * scale) / 2;

    const toScreenX = (gx: number) => offsetX + (gx - minX) * scale;
    const toScreenY = (gy: number) => offsetY + (gy - minY) * scale;

    // 3. Draw High-Res Edges with Color Gradients
    graphInstance.forEachEdge((_edge: string, attrs: any, source: string, target: string) => {
      const sAttrs = graphInstance.getNodeAttributes(source);
      const tAttrs = graphInstance.getNodeAttributes(target);
      if (!sAttrs || !tAttrs || sAttrs.x === undefined || tAttrs.x === undefined) return;

      const sx = toScreenX(sAttrs.x);
      const sy = toScreenY(sAttrs.y);
      const tx = toScreenX(tAttrs.x);
      const ty = toScreenY(tAttrs.y);

      const grad = ctx.createLinearGradient(sx, sy, tx, ty);
      grad.addColorStop(0, sAttrs.color ? `${sAttrs.color}45` : 'rgba(99, 102, 241, 0.3)');
      grad.addColorStop(1, tAttrs.color ? `${tAttrs.color}45` : 'rgba(0, 229, 255, 0.3)');

      ctx.strokeStyle = grad;
      ctx.lineWidth = Math.max(1.2, (attrs.size || 1) * 1.5);
      ctx.beginPath();
      ctx.moveTo(sx, sy);
      ctx.lineTo(tx, ty);
      ctx.stroke();
    });

    // 4. Collect and Draw Nodes
    const nodeEntries: { id: string; attrs: any; degree: number; sx: number; sy: number }[] = [];
    graphInstance.forEachNode((node: string, attrs: any) => {
      if (attrs.x === undefined || attrs.y === undefined) return;
      const sx = toScreenX(attrs.x);
      const sy = toScreenY(attrs.y);
      const degree = graphInstance.degree(node);
      nodeEntries.push({ id: node, attrs, degree, sx, sy });
    });

    // Render smaller nodes first, prominent hubs last
    nodeEntries.sort((a, b) => a.degree - b.degree);

    nodeEntries.forEach(({ attrs, degree, sx, sy }) => {
      const radius = Math.max(5, Math.min(26, 4 + Math.sqrt(degree) * 2.8));
      const nodeColor = attrs.color || '#6366F1';

      // Ambient Glow Halo
      const glowGrad = ctx.createRadialGradient(sx, sy, radius * 0.2, sx, sy, radius * 3.0);
      glowGrad.addColorStop(0, `${nodeColor}A0`);
      glowGrad.addColorStop(0.5, `${nodeColor}40`);
      glowGrad.addColorStop(1, `${nodeColor}00`);
      ctx.fillStyle = glowGrad;
      ctx.beginPath();
      ctx.arc(sx, sy, radius * 3.0, 0, Math.PI * 2);
      ctx.fill();

      // Outer White Stroke Ring
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = Math.max(1, radius * 0.18);
      ctx.beginPath();
      ctx.arc(sx, sy, radius, 0, Math.PI * 2);
      ctx.stroke();

      // Center Color Core
      ctx.fillStyle = nodeColor;
      ctx.beginPath();
      ctx.arc(sx, sy, radius, 0, Math.PI * 2);
      ctx.fill();
    });

    // 5. Draw High-Contrast Typography Labels for Key Hubs
    const labeledNodes = nodeEntries.filter(n => n.degree >= 2 || nodeEntries.length < 50);
    labeledNodes.sort((a, b) => b.degree - a.degree);
    const topLabels = labeledNodes.slice(0, Math.min(90, labeledNodes.length));

    topLabels.forEach(({ attrs, degree, sx, sy }) => {
      const label = attrs.label || attrs.name || '';
      if (!label) return;

      const fontSize = Math.max(12, Math.min(20, 11 + Math.sqrt(degree) * 1.6));
      ctx.font = `bold ${fontSize}px "Plus Jakarta Sans", "Inter", -apple-system, sans-serif`;

      const labelY = sy - Math.max(8, 4 + Math.sqrt(degree) * 2.8) - 5;

      // Dark Outline Halo for 100% legibility
      ctx.strokeStyle = '#050811';
      ctx.lineWidth = 4.5;
      ctx.lineJoin = 'round';
      ctx.miterLimit = 2;
      ctx.textAlign = 'center';
      ctx.strokeText(label, sx, labelY);

      // Crisp White Text Fill
      ctx.fillStyle = '#FFFFFF';
      ctx.fillText(label, sx, labelY);
    });

    return canvas;
  };

  const handleExport = (type: 'png' = 'png') => {
    const hdGraph = generateHighDefGraphCanvas(graph, 2560, 1400);
    if (hdGraph) {
      const width = 2560;
      const headerHeight = 180;
        const footerHeight = 70;
        const padding = 45;
        const graphHeight = 1400;
        const height = headerHeight + graphHeight + footerHeight;

        const compCanvas = document.createElement('canvas');
        compCanvas.width = width;
        compCanvas.height = height;
        const ctx = compCanvas.getContext('2d');
        if (ctx) {
          ctx.imageSmoothingEnabled = true;
          ctx.imageSmoothingQuality = 'high';

          // Background
          ctx.fillStyle = '#080C17';
          ctx.fillRect(0, 0, width, height);

          // Archival Framing
          ctx.strokeStyle = '#334155';
          ctx.lineWidth = 3;
          ctx.strokeRect(20, 20, width - 40, height - 40);

          ctx.strokeStyle = '#1E293B';
          ctx.lineWidth = 1;
          ctx.strokeRect(28, 28, width - 56, height - 56);

          // Eyebrow
          ctx.font = '700 14px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
          ctx.fillStyle = '#60A5FA';
          ctx.fillText('ENERGY INNOVATION KNOWLEDGE GRAPH · NATIONAL TOPOLOGY ATLAS', padding, 65);

          // Headline
          ctx.font = 'bold 32px Georgia, "Playfair Display", "Times New Roman", serif';
          ctx.fillStyle = '#F8FAFC';
          ctx.fillText('Energy Innovation Topological Knowledge Graph', padding, 105);

          // Subtitle & Date
          const today = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
          ctx.font = '400 16px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
          ctx.fillStyle = '#94A3B8';
          ctx.fillText(`Mapping ${stats.nodes} nodes, ${stats.edges} interconnections, and ${stats.clusters} thematic communities across the United States.`, padding, 138);

          ctx.textAlign = 'right';
          ctx.fillText(`Edition: ${today}`, width - padding, 65);
          ctx.fillText('U.S. Energy Innovation Database by Brandon N. Owens', width - padding, 90);
          ctx.textAlign = 'left';

          // Divider
          ctx.strokeStyle = '#1E293B';
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.moveTo(padding, 155);
          ctx.lineTo(width - padding, 155);
          ctx.stroke();

          // Render High-Def Graph Area
          ctx.drawImage(hdGraph, padding, headerHeight, width - padding * 2, graphHeight);

          // Frame around graph
          ctx.strokeStyle = '#334155';
          ctx.lineWidth = 1;
          ctx.strokeRect(padding, headerHeight, width - padding * 2, graphHeight);

          // Footer Source Attribution
          const footerY = height - 32;
          ctx.font = '500 14px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
          ctx.fillStyle = '#94A3B8';
          ctx.fillText('U.S. Energy Innovation Database by Brandon N. Owens', padding, footerY);

          ctx.textAlign = 'right';
          ctx.fillText('U.S. Energy Innovation Database by Brandon N. Owens', width - padding, footerY);
          ctx.textAlign = 'left';

          compCanvas.toBlob((b) => {
            if (b) saveAs(b, 'knowledge-graph-highres.png');
          }, 'image/png');
        }
      }
    setExportOpen(false);
  };

  const { data: agenciesData } = useQuery<any>({
    queryKey: ['agencies'],
    queryFn: () => api.getAgencies(),
  });

  const allAgenciesList = Array.isArray(agenciesData) ? agenciesData : agenciesData?.items || [];
  const agencies = useMemo(() => {
    const s = new Set<string>();
    allNodes.forEach((n: any) => { if (n.agency) s.add(n.agency); });
    return Array.from(s).sort();
  }, [allNodes]);

  const groupedAgencies = useMemo(() => {
    const map: Record<string, string[]> = {
      utility: [],
      federal: [],
      state: [],
      foundation: [],
    };
    agencies.forEach(agName => {
      const match = allAgenciesList.find((a: any) => a.name === agName || a.code === agName);
      const cat = match?.category || 'state';
      if (!map[cat]) map[cat] = [];
      map[cat].push(agName);
    });
    return map;
  }, [agencies, allAgenciesList]);

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)] space-y-2.5">
      {/* Top Intelligence Toolbar */}
      <div className="bg-white p-3.5 rounded-2xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <NetworkIcon size={20} className="text-indigo-600" />
              Energy Innovation Knowledge Graph
            </h1>
            <button onClick={() => setGuideOpen(true)} className="p-1 rounded-full text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors" title="How to explore this network">
              <HelpCircle size={16} />
            </button>
          </div>
          <p className="text-[12px] text-slate-500 mt-0.5 flex items-center gap-2 flex-wrap">
            <span className="px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 text-[11px] font-semibold border border-indigo-100">
              {stats.nodes} nodes &middot; {stats.edges} edges &middot; {stats.clusters} clusters
            </span>
            {neighborhoodNode && (
              <span className="px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 text-[11px] font-medium border border-amber-100 flex items-center gap-1">
                <Crosshair size={10} /> Ego Neighborhood
              </span>
            )}
            {pathNodes.length > 1 && (
              <span className="px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 text-[11px] font-bold border border-indigo-200 flex items-center gap-1">
                <GitFork size={11} /> Path Length: {pathNodes.length - 1} hops
              </span>
            )}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 flex-wrap">
          <button onClick={() => setInsightsOpen(true)}
            className="flex items-center gap-1.5 px-3 py-2 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 text-white rounded-xl text-xs font-semibold shadow-xs transition-all">
            <Sparkles size={13} className="text-amber-300" /> Generate Insights
          </button>

          <button onClick={() => setCentralityOpen(true)}
            className="flex items-center gap-1.5 px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50 shadow-2xs transition-colors">
            <BarChart3 size={13} className="text-indigo-600" /> Centrality &amp; Bridges
          </button>

          <button onClick={() => { setPathMode(!pathMode); setPathStart(null); setPathEnd(null); setPathNodes([]); }}
            className={clsx("flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold border transition-colors shadow-2xs",
              pathMode ? "bg-amber-50 text-amber-800 border-amber-300 font-bold" : "bg-white text-slate-700 border-slate-200 hover:bg-slate-50")}>
            <GitFork size={13} /> {pathMode ? 'Exit Pathfinder' : 'Find Path'}
          </button>

          <div className="relative">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input type="text" placeholder="Search knowledge graph..." value={search} onChange={e => setSearch(e.target.value)}
              className="pl-8 pr-8 py-2 bg-slate-50 border border-slate-200 rounded-xl text-[12px] focus:ring-2 focus:ring-indigo-500 outline-none w-52 shadow-2xs" />
            {search && <button onClick={() => setSearch('')} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"><X size={12} /></button>}
          </div>

          {neighborhoodNode && (
            <button onClick={() => setNeighborhoodNode(null)} className="px-3 py-2 bg-amber-50 border border-amber-200 rounded-xl text-xs font-bold text-amber-800 hover:bg-amber-100 flex items-center gap-1 shadow-2xs">
              <Maximize2 size={13} /> Show All
            </button>
          )}

          {/* Executive Graphic Export Action Button */}
          <button
            onClick={() => setNytExportOpen(true)}
            className="flex items-center gap-1.5 px-3 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold shadow-xs transition-all cursor-pointer"
            title="Generate high-resolution Executive Publication infographic wall art"
          >
            <Sparkles size={13} className="text-amber-300" />
            <span>Executive Graphic</span>
          </button>

          <div className="relative">
            <button onClick={() => setExportOpen(!exportOpen)} className="flex items-center gap-1.5 px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50 shadow-2xs">
              <Download size={13} /> Export
            </button>
            {exportOpen && (
              <div className="absolute right-0 top-full mt-1 w-48 bg-white border border-slate-200 rounded-xl shadow-xl z-50 overflow-hidden">
                <button onClick={() => { setNytExportOpen(true); setExportOpen(false); }} className="w-full text-left px-3 py-2 text-xs text-indigo-900 hover:bg-indigo-50 font-semibold flex items-center gap-2">
                  <Sparkles size={12} className="text-amber-500" /> Executive Wall Art (PNG)
                </button>
                <button onClick={() => { handleExport('png'); setExportOpen(false); }} className="w-full text-left px-3 py-2 text-xs text-slate-700 hover:bg-indigo-50 hover:text-indigo-700 flex items-center gap-2 border-t border-slate-100">Standard High-Res PNG</button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── TOPOLOGY EXECUTIVE HUD METRICS RIBBON ── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
        <div className="bg-white px-3.5 py-2.5 rounded-xl border border-slate-200/80 shadow-2xs flex items-center justify-between">
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Topology Scale</div>
            <div className="text-base font-extrabold text-slate-900">{stats.nodes} Nodes · {stats.edges} Links</div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-sm">
            🌐
          </div>
        </div>

        <div className="bg-white px-3.5 py-2.5 rounded-xl border border-slate-200/80 shadow-2xs flex items-center justify-between">
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Thematic Clusters</div>
            <div className="text-base font-extrabold text-emerald-600">{stats.clusters} Communities</div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-sm">
            ✨
          </div>
        </div>

        <div className="bg-white px-3.5 py-2.5 rounded-xl border border-slate-200/80 shadow-2xs flex items-center justify-between">
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Network Interconnect</div>
            <div className="text-base font-extrabold text-slate-800">{(stats.density * 100).toFixed(2)}% Density</div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center font-bold text-sm">
            ⚡
          </div>
        </div>

        <div className="bg-white px-3.5 py-2.5 rounded-xl border border-slate-200/80 shadow-2xs flex items-center justify-between">
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Cross-Domain Bridges</div>
            <div className="text-base font-extrabold text-indigo-700">{topBetweenness.length} Key Connectors</div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-sky-50 text-sky-600 flex items-center justify-center font-bold text-sm">
            🌉
          </div>
        </div>
      </div>

      {/* Pathfinder Banner */}
      {pathMode && (
        <div className="mb-2 px-4 py-2 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900 flex items-center justify-between shadow-2xs">
          <div className="flex items-center gap-2">
            <GitFork size={15} className="text-amber-600" />
            <span>
              {!pathStart ? 'Click Start Node on graph' : !pathEnd ? `Start: "${pathStart.name}". Now click Target Node to trace path.` : `Path between "${pathStart.name}" and "${pathEnd.name}" highlighted below.`}
            </span>
          </div>
          {(pathStart || pathEnd) && (
            <button onClick={() => { setPathStart(null); setPathEnd(null); setPathNodes([]); }} className="text-xs text-amber-700 underline font-semibold hover:text-amber-900">Clear</button>
          )}
        </div>
      )}

      {/* Main Canvas + Control Panels */}
      <div className="flex-1 flex gap-3 min-h-0 relative overflow-hidden">
        {/* Filters & Control Panel */}
        <div className={clsx("bg-white border border-slate-200 rounded-xl flex flex-col transition-all duration-300 shadow-[var(--shadow-xs)] shrink-0", filtersOpen ? "w-64" : "w-11 items-center")}>
          <div className="p-3 border-b border-slate-100 flex items-center justify-between">
            {filtersOpen && <h3 className="text-xs font-bold text-slate-800 flex items-center gap-1.5"><Filter size={13}/>Graph Controls</h3>}
            <button onClick={() => setFiltersOpen(!filtersOpen)} className="p-1 rounded text-slate-400 hover:bg-slate-100 hover:text-slate-600"><Filter size={13} /></button>
          </div>

          {filtersOpen && (
            <div className="flex-1 overflow-y-auto p-3 space-y-4 text-xs">
              {/* Density Management Slider */}
              <div className="p-2.5 bg-slate-50 rounded-xl border border-slate-200/80">
                <div className="flex items-center justify-between mb-1">
                  <label className="text-[10px] font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1">
                    <Sliders size={11} className="text-indigo-600" /> Min Degree (Density)
                  </label>
                  <span className="font-bold text-indigo-700 bg-indigo-50 px-1.5 py-0.5 rounded border border-indigo-100">{minDegree}</span>
                </div>
                <input type="range" min="1" max="10" step="1" value={minDegree} onChange={e => setMinDegree(parseInt(e.target.value))} className="w-full accent-indigo-600 h-1.5 cursor-pointer" />
                <p className="text-[10px] text-slate-400 mt-1">Strip peripheral leaves to reveal core structure.</p>
              </div>

              {/* Color Mode & Thematic Clusters */}
              <div>
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5 block">Coloring &amp; Partitioning</label>
                <div className="flex bg-slate-100 p-0.5 rounded-lg mb-2">
                  <button onClick={() => { setColorMode('type'); setSelectedCluster(null); }} className={clsx("flex-1 text-[11px] font-medium py-1 rounded transition-all", colorMode === 'type' ? "bg-white text-slate-800 shadow-sm font-semibold" : "text-slate-500 hover:text-slate-800")}>By Type</button>
                  <button onClick={() => setColorMode('cluster')} className={clsx("flex-1 text-[11px] font-medium py-1 rounded transition-all", colorMode === 'cluster' ? "bg-white text-indigo-700 shadow-sm font-semibold" : "text-slate-500 hover:text-slate-800")}>By Cluster</button>
                </div>

                {colorMode === 'cluster' && clusters.length > 0 && (
                  <div className="space-y-1 max-h-36 overflow-y-auto pr-1">
                    <button onClick={() => setSelectedCluster(null)} className={clsx("w-full text-left px-2 py-1 rounded text-[10px] font-medium transition-colors", selectedCluster === null ? "bg-indigo-100 text-indigo-900 font-bold" : "text-slate-600 hover:bg-slate-100")}>All Clusters ({clusters.length})</button>
                    {clusters.slice(0, 10).map(c => (
                      <button key={c.id} onClick={() => setSelectedCluster(selectedCluster === c.id ? null : c.id)}
                        className={clsx("w-full text-left px-2 py-1 rounded text-[10px] transition-colors flex items-center justify-between", selectedCluster === c.id ? "bg-indigo-600 text-white font-bold" : "hover:bg-slate-100 text-slate-700")}>
                        <div className="flex items-center gap-1.5 truncate">
                          <div className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: CLUSTER_PALETTE[c.id % CLUSTER_PALETTE.length] }} />
                          <span className="truncate">{c.label}</span>
                        </div>
                        {c.totalFunding > 0 && <span className="text-[9px] opacity-80 shrink-0">{fmt(c.totalFunding)}</span>}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Layout Engine Switcher */}
              <div>
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5 block">Layout Physics</label>
                <div className="grid grid-cols-3 gap-1 bg-slate-100 p-0.5 rounded-lg">
                  <button onClick={() => setLayoutType('forceAtlas2')} className={clsx("py-1 text-[10px] font-medium rounded transition-all", layoutType === 'forceAtlas2' ? "bg-white text-indigo-700 shadow-sm font-semibold" : "text-slate-500 hover:text-slate-800")}>Organic</button>
                  <button onClick={() => setLayoutType('circular')} className={clsx("py-1 text-[10px] font-medium rounded transition-all", layoutType === 'circular' ? "bg-white text-indigo-700 shadow-sm font-semibold" : "text-slate-500 hover:text-slate-800")}>Circular</button>
                  <button onClick={() => setLayoutType('radial')} className={clsx("py-1 text-[10px] font-medium rounded transition-all", layoutType === 'radial' ? "bg-white text-indigo-700 shadow-sm font-semibold" : "text-slate-500 hover:text-slate-800")}>Radial</button>
                </div>
              </div>

              {/* Entity Types */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Entity Types</label>
                  <div className="flex items-center gap-1.5 text-[10px]">
                    <button
                      type="button"
                      onClick={selectAllEntities}
                      className="text-indigo-600 hover:text-indigo-800 font-semibold"
                    >
                      All
                    </button>
                    <span className="text-slate-300">·</span>
                    <button
                      type="button"
                      onClick={clearAllEntities}
                      className="text-slate-400 hover:text-slate-600"
                    >
                      None
                    </button>
                  </div>
                </div>
                <div className="space-y-1 bg-slate-50 p-2 rounded-lg border border-slate-200/80">
                  {Object.entries(NODE_LABELS).map(([type, label]) => {
                    const isChecked = selectedEntityTypes.has(type);
                    const count = (summary?.node_types as Record<string, number>)?.[type] || 0;
                    return (
                      <label key={type} className="flex items-center justify-between text-[11px] text-slate-700 cursor-pointer hover:text-slate-900 group py-0.5">
                        <div className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={() => toggleEntity(type)}
                            className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 w-3.5 h-3.5 cursor-pointer"
                          />
                          <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: NODE_COLORS[type] || '#64748b' }} />
                          <span className={clsx(isChecked ? "font-medium text-slate-900" : "text-slate-400 line-through")}>{label}</span>
                        </div>
                        {count > 0 && (
                          <span className={clsx("text-[9px] px-1.5 py-0.2 rounded font-mono", isChecked ? "bg-white text-slate-600 border border-slate-200" : "text-slate-400")}>
                            {count}
                          </span>
                        )}
                      </label>
                    );
                  })}
                </div>
              </div>

              {/* Organization */}
              <div>
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1.5 block">Organization</label>
                <select value={agencyFilter} onChange={e => setAgencyFilter(e.target.value)} className="w-full px-2 py-1.5 text-[11px] bg-slate-50 border border-slate-200 rounded outline-none focus:ring-1 focus:ring-indigo-500">
                  <option value="">All Organizations ({agencies.length})</option>
                  {groupedAgencies.utility?.length > 0 && (
                    <optgroup label="⚡ Electric & Gas Utilities">
                      {groupedAgencies.utility.map((a: string) => <option key={a} value={a}>{a}</option>)}
                    </optgroup>
                  )}
                  {groupedAgencies.federal?.length > 0 && (
                    <optgroup label="🏛️ Federal Agencies">
                      {groupedAgencies.federal.map((a: string) => <option key={a} value={a}>{a}</option>)}
                    </optgroup>
                  )}
                  {groupedAgencies.state?.length > 0 && (
                    <optgroup label="🗽 State Energy Agencies">
                      {groupedAgencies.state.map((a: string) => <option key={a} value={a}>{a}</option>)}
                    </optgroup>
                  )}
                  {groupedAgencies.foundation?.length > 0 && (
                    <optgroup label="🌱 Philanthropic Foundations">
                      {groupedAgencies.foundation.map((a: string) => <option key={a} value={a}>{a}</option>)}
                    </optgroup>
                  )}
                </select>
              </div>

              {/* Node Limit */}
              <div>
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1 flex items-center justify-between">
                  <span>Node Limit</span>
                  <span className="text-indigo-600 font-semibold">{nodeLimit}</span>
                </label>
                <input type="range" min="200" max="2500" step="100" value={nodeLimit} onChange={e => setNodeLimit(parseInt(e.target.value))} className="w-full accent-indigo-600 h-1.5" />
              </div>

              <div className="pt-2 border-t border-slate-100">
                <button onClick={() => {
                  setAgencyFilter(''); setStatusFilter(''); setYearMin(''); setYearMax('');
                  setEntityFilter('org,opp,award,tech,program,awardee,fuel'); setSearch('');
                  setHighlightedType(null); setNeighborhoodNode(null); setMinDegree(1);
                  setColorMode('type'); setSelectedCluster(null); setLayoutType('forceAtlas2');
                  setNodeLimit(800); setPathNodes([]); setPathMode(false);
                }}
                  className="w-full py-1.5 flex items-center justify-center gap-1 text-[11px] font-medium text-slate-600 bg-slate-50 hover:bg-slate-100 rounded border border-slate-200/60 transition-colors">
                  <RefreshCw size={11} /> Reset Graph
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Graph Canvas */}
        <div className="flex-1 bg-slate-50 rounded-xl relative border border-slate-200 shadow-[var(--shadow-xs)] overflow-hidden">
          {isLoading ? (
            <div className="absolute inset-0 flex items-center justify-center bg-white/70 backdrop-blur-sm z-10">
              <div className="flex flex-col items-center gap-3">
                <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
                <span className="text-xs font-semibold text-slate-600">Synthesizing network topology &amp; computing clusters...</span>
              </div>
            </div>
          ) : !graph || stats.nodes === 0 ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <NetworkIcon size={40} className="mx-auto mb-3 text-slate-300" />
                <p className="text-xs text-slate-500 font-medium">No nodes match current filters</p>
              </div>
            </div>
          ) : (
            <SigmaContainer style={{ width: '100%', height: '100%' }} settings={{
              allowInvalidContainer: true,
              renderEdgeLabels: false,
              labelSize: 10,
              labelColor: { color: '#475569' },
              labelRenderedSizeThreshold: 5.5,
              defaultEdgeType: 'line',
              defaultNodeColor: '#64748b',
              zIndex: true,
              minCameraRatio: 0.05,
              maxCameraRatio: 10,
              stagePadding: 40,
              labelFont: '"Inter", system-ui, sans-serif',
            }}>
              <GraphController
                graph={graph}
                search={debouncedSearch}
                highlightedType={highlightedType}
                neighborhoodNode={neighborhoodNode}
                colorMode={colorMode}
                selectedCluster={selectedCluster}
                pathNodes={pathNodes}
                onNodeClick={handleNodeClick}
                onHover={handleHover}
              />
              <ZoomControls />
            </SigmaContainer>
          )}

          {/* Hover Tooltip Card */}
          {hoverInfo && (
            <div className="absolute pointer-events-none z-40" style={{ left: Math.min(hoverInfo.x + 14, window.innerWidth - 380), top: hoverInfo.y - 10, maxWidth: 340 }}>
              <div className="bg-slate-950/95 text-white text-[11px] px-3.5 py-3 rounded-xl shadow-2xl border border-slate-700/80 backdrop-blur-md">
                <div className="flex items-center gap-1.5 mb-1.5">
                  <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[9px] font-bold text-white uppercase tracking-wider" style={{ backgroundColor: NODE_COLORS[hoverInfo.node.type] || '#64748b' }}>
                    {NODE_ICONS[hoverInfo.node.type]} {NODE_LABELS[hoverInfo.node.type] || hoverInfo.node.type}
                  </span>
                  {hoverInfo.node.agency && <OrgLogo org={hoverInfo.node.agency} size="xs" />}
                  {hoverInfo.node.degree !== undefined && (
                    <span className="text-[10px] text-indigo-300 font-semibold ml-auto">Degree: {hoverInfo.node.degree}</span>
                  )}
                </div>
                <div className="font-semibold text-white leading-snug">{hoverInfo.node.name}</div>
                {hoverInfo.node.funding && <div className="text-emerald-400 text-xs mt-1 font-bold">{fmt(hoverInfo.node.funding)}</div>}
                {hoverInfo.node.keywords && <div className="mt-1 text-[10px] text-slate-400 line-clamp-2">{hoverInfo.node.keywords}</div>}
                <div className="text-[9px] text-slate-400 mt-2 pt-1.5 border-t border-slate-800 flex items-center justify-between">
                  <span>Click to inspect</span>
                  <span>Drag to reposition</span>
                </div>
              </div>
            </div>
          )}

          {/* Interactive Semantic Legend */}
          <div className="absolute bottom-3 left-3 right-3 bg-white/95 backdrop-blur-sm border border-slate-200/80 rounded-lg px-3 py-2 shadow-sm z-20">
            <div className="flex flex-wrap items-center gap-x-2.5 gap-y-1 text-[10px]">
              <span className="font-bold text-slate-500 text-[9px] uppercase tracking-wider">Nodes</span>
              {Object.entries(NODE_COLORS).map(([type, color]) => (
                <button key={type} onClick={() => setHighlightedType(p => p === type ? null : type)}
                  className={clsx("flex items-center gap-1 cursor-pointer transition-all rounded-full px-1.5 py-0.5",
                    highlightedType === type ? "ring-2 ring-indigo-400 ring-offset-1 bg-indigo-50 font-bold text-indigo-700" : "hover:bg-slate-100 text-slate-600")}>
                  <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: color }} />
                  <span>{NODE_LABELS[type]}</span>
                  {summary.node_types?.[type] && <span className="text-slate-400 font-normal">({summary.node_types[type]})</span>}
                </button>
              ))}
              <div className="w-px h-3 bg-slate-200 mx-0.5" />
              <span className="font-bold text-slate-500 text-[9px] uppercase tracking-wider">Edges</span>
              {Object.entries(EDGE_COLORS).slice(0, 6).map(([type, color]) => (
                <span key={type} className="flex items-center gap-1 text-slate-500">
                  <div className="w-3 h-[2px] rounded-full" style={{ backgroundColor: color }} />
                  {EDGE_LABELS[type]}
                </span>
              ))}
              {highlightedType && (
                <button onClick={() => setHighlightedType(null)} className="text-[9px] text-indigo-600 hover:text-indigo-700 font-bold ml-1">Clear</button>
              )}
            </div>
          </div>
        </div>

        {/* Selected Node Detail Panel */}
        {selectedNode && (
          <DetailPanel
            node={selectedNode}
            onClose={() => setSelectedNode(null)}
            onNavigate={handleNavigate}
            onFindPathFromHere={handleFindPathFromHere}
            onIsolate={handleIsolate}
          />
        )}
      </div>

      {/* Guide Modal */}
      {guideOpen && <NetworkGuideModal onClose={() => setGuideOpen(false)} />}

      {/* Centrality & Bridge Drawer */}
      {centralityOpen && (
        <CentralityDrawer
          topCentrality={topCentrality}
          topBetweenness={topBetweenness}
          topPageRank={topPageRank}
          onClose={() => setCentralityOpen(false)}
          onSelectNode={(node) => {
            setSelectedNode(node);
            setCentralityOpen(false);
          }}
        />
      )}

      {/* Automated AI Insights Drawer */}
      {insightsOpen && (
        <InsightsDrawer
          analyticsData={analyticsData}
          onClose={() => setInsightsOpen(false)}
          onSelectAgency={(ag) => { setAgencyFilter(ag); setInsightsOpen(false); }}
          onSelectTech={(tech) => { setSearch(tech); setInsightsOpen(false); }}
        />
      )}

      {/* Executive Style High-Resolution Infographic Export Modal */}
      <NYTGraphicExportModal
        isOpen={nytExportOpen}
        onClose={() => setNytExportOpen(false)}
        defaultTitle="ENERGY INNOVATION KNOWLEDGE GRAPH"
        defaultSubtitle={`Topological network topology mapping ${stats.nodes.toLocaleString()} organizations, programs, opportunities, awardees, technologies, and clean fuels across the United States.`}
        eyebrow="ENERGY INNOVATION KNOWLEDGE GRAPH · NATIONAL TOPOLOGY ATLAS"
        getContentCanvas={() => {
          const hdc = generateHighDefGraphCanvas(graph, 3840, 2160);
          if (hdc) return hdc;
          const canvases = document.querySelectorAll('.sigma-container canvas');
          if (canvases.length > 0) {
            const base = canvases[0] as HTMLCanvasElement;
            const merged = document.createElement('canvas');
            merged.width = base.width;
            merged.height = base.height;
            const mCtx = merged.getContext('2d');
            if (mCtx) {
              mCtx.fillStyle = '#080C17';
              mCtx.fillRect(0, 0, merged.width, merged.height);
              canvases.forEach((c) => {
                mCtx.drawImage(c as HTMLCanvasElement, 0, 0);
              });
            }
            return merged;
          }
          return null;
        }}
        stats={[
          { label: 'Total Entities', val: stats.nodes.toLocaleString() },
          { label: 'Network Interconnections', val: stats.edges.toLocaleString() },
          { label: 'Thematic Communities', val: stats.clusters.toString() },
          { label: 'Network Graph Density', val: `${(stats.density * 100).toFixed(2)}%` },
        ]}
        legendItems={Object.entries(NODE_LABELS).map(([k, v]) => ({
          label: v,
          color: NODE_COLORS[k] || '#64748b',
        }))}
        legendTitle="NETWORK NODE TAXONOMY"
        sourceAttribution="U.S. Energy Innovation Database by Brandon N. Owens"
        filenamePrefix="energy-innovation-knowledge-graph"
      />
    </div>
  );
}
