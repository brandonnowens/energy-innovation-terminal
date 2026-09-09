import React, { useState, useMemo, useRef, useEffect, useCallback } from 'react';
import {
  Trophy, Building2, Lightbulb, TrendingUp, ExternalLink,
  Search, Filter, ChevronRight, X, ArrowUpRight, ShieldCheck,
  Zap, Compass, Layers, GitFork, Users, Network, DollarSign, Award,
  ArrowUpDown, ZoomIn, ZoomOut, RefreshCw, Maximize2, Minimize2,
  Download, Eye, EyeOff, Info, Check, Sliders, Play, Pause, Move
} from 'lucide-react';
import clsx from 'clsx';
import { RecipientAttributionDossier } from '../api/client';

interface NodePos {
  id: string;
  name: string;
  type: string;
  category: string;
  size: number;
  color: string;
  patent_number?: string;
  url?: string;
  x: number;
  y: number;
  vx: number;
  vy: number;
  isDragging?: boolean;
}

interface InteractiveEgoGraphProps {
  egoGraph: RecipientAttributionDossier['ego_graph'];
  companyName: string;
  height?: number;
}

function formatCurrency(val: number | null | undefined): string {
  if (!val) return '$0';
  if (val >= 1_000_000_000) return `$${(val / 1_000_000_000).toFixed(2)}B`;
  if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(1)}M`;
  if (val >= 1_000) return `$${(val / 1_000).toFixed(0)}K`;
  return `$${val.toFixed(0)}`;
}

export function InteractiveEgoGraph({
  egoGraph,
  companyName,
  height = 360
}: InteractiveEgoGraphProps) {
  const [layoutMode, setLayoutMode] = useState<'orbital' | 'physics' | 'split'>('orbital');
  const [showPatents, setShowPatents] = useState(true);
  const [showInvestors, setShowInvestors] = useState(true);
  const [showGrants, setShowGrants] = useState(true);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
  const [selectedNode, setSelectedNode] = useState<NodePos | null>(null);
  const [hoveredNode, setHoveredNode] = useState<NodePos | null>(null);
  const [isSimulating, setIsSimulating] = useState(true);

  const svgRef = useRef<SVGSVGElement>(null);
  const dragRef = useRef<{ nodeId: string | null; startX: number; startY: number; origX: number; origY: number; isPanning: boolean; panStartX: number; panStartY: number }>({
    nodeId: null,
    startX: 0,
    startY: 0,
    origX: 0,
    origY: 0,
    isPanning: false,
    panStartX: 0,
    panStartY: 0
  });

  const width = 640;
  const centerX = width / 2;
  const centerY = height / 2;

  // Initialize node state with coordinates
  const [nodes, setNodes] = useState<NodePos[]>([]);

  useEffect(() => {
    if (!egoGraph || !egoGraph.nodes.length) return;

    const rawNodes = egoGraph.nodes;
    const centerRaw = rawNodes.find(n => n.type === 'company');
    const others = rawNodes.filter(n => n.type !== 'company');

    const initialized: NodePos[] = rawNodes.map((n, idx) => {
      const isCenter = n.type === 'company';
      let color = '#38bdf8';
      let nodeSize = 18;

      if (n.type === 'patent') {
        color = '#f59e0b';
        nodeSize = 13;
      } else if (n.type === 'investor') {
        color = '#10b981';
        nodeSize = 14;
      } else if (n.type === 'grant' || n.type === 'agency') {
        color = '#818cf8';
        nodeSize = 15;
      }

      if (isCenter) {
        return {
          ...n,
          size: 22,
          color: '#0ea5e9',
          x: centerX,
          y: centerY,
          vx: 0,
          vy: 0
        };
      }

      // Compute structured initial layout
      let initX = centerX;
      let initY = centerY;

      if (layoutMode === 'orbital') {
        const angle = (idx / Math.max(others.length, 1)) * 2 * Math.PI;
        const radius = n.type === 'patent' ? 120 : (n.type === 'investor' ? 140 : 100);
        initX = centerX + Math.cos(angle) * radius;
        initY = centerY + Math.sin(angle) * (radius * 0.75);
      } else if (layoutMode === 'split') {
        if (n.type === 'agency' || n.type === 'grant') {
          initX = centerX - 160;
          initY = centerY - 60 + idx * 40;
        } else if (n.type === 'patent') {
          initX = centerX + 160;
          initY = centerY - 70 + (idx % 4) * 35;
        } else {
          initX = centerX + 140;
          initY = centerY + 40 + (idx % 4) * 35;
        }
      } else {
        // Random dispersion for physics
        const angle = Math.random() * 2 * Math.PI;
        const dist = 60 + Math.random() * 90;
        initX = centerX + Math.cos(angle) * dist;
        initY = centerY + Math.sin(angle) * dist;
      }

      return {
        ...n,
        size: nodeSize,
        color,
        x: initX,
        y: initY,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5
      };
    });

    setNodes(initialized);
  }, [egoGraph, layoutMode, centerX, centerY, height]);

  // Spring physics simulation tick
  useEffect(() => {
    if (!isSimulating || layoutMode !== 'physics') return;

    let animId: number;
    const tick = () => {
      setNodes(prevNodes => {
        const next = prevNodes.map(n => ({ ...n }));
        const center = next.find(n => n.type === 'company');
        if (center && !center.isDragging) {
          center.x = centerX;
          center.y = centerY;
        }

        // Repulsion between nodes
        for (let i = 0; i < next.length; i++) {
          for (let j = i + 1; j < next.length; j++) {
            const a = next[i];
            const b = next[j];
            const dx = b.x - a.x;
            const dy = b.y - a.y;
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;
            if (dist < 180) {
              const force = (180 - dist) / dist * 0.04;
              if (!a.isDragging && a.type !== 'company') {
                a.vx -= dx * force;
                a.vy -= dy * force;
              }
              if (!b.isDragging && b.type !== 'company') {
                b.vx += dx * force;
                b.vy += dy * force;
              }
            }
          }
        }

        // Attraction to center / springs along edges
        egoGraph.edges.forEach(e => {
          const src = next.find(n => n.id === e.source);
          const tgt = next.find(n => n.id === e.target);
          if (src && tgt) {
            const dx = tgt.x - src.x;
            const dy = tgt.y - src.y;
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;
            const targetDist = 110;
            const force = (dist - targetDist) * 0.008;
            if (!src.isDragging && src.type !== 'company') {
              src.vx += (dx / dist) * force;
              src.vy += (dy / dist) * force;
            }
            if (!tgt.isDragging && tgt.type !== 'company') {
              tgt.vx -= (dx / dist) * force;
              tgt.vy -= (dy / dist) * force;
            }
          }
        });

        // Apply velocity & damping
        next.forEach(n => {
          if (!n.isDragging && n.type !== 'company') {
            n.vx *= 0.88;
            n.vy *= 0.88;
            n.x += n.vx;
            n.y += n.vy;

            // Boundary containment
            n.x = Math.max(30, Math.min(width - 30, n.x));
            n.y = Math.max(30, Math.min(height - 30, n.y));
          }
        });

        return next;
      });

      animId = requestAnimationFrame(tick);
    };

    animId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animId);
  }, [isSimulating, layoutMode, egoGraph.edges, centerX, centerY, width, height]);

  // Filter visible nodes
  const visibleNodes = useMemo(() => {
    return nodes.filter(n => {
      if (n.type === 'patent' && !showPatents) return false;
      if (n.type === 'investor' && !showInvestors) return false;
      if ((n.type === 'grant' || n.type === 'agency') && !showGrants) return false;
      return true;
    });
  }, [nodes, showPatents, showInvestors, showGrants]);

  const visibleNodeMap = useMemo(() => {
    const map = new Map<string, NodePos>();
    visibleNodes.forEach(n => map.set(n.id, n));
    return map;
  }, [visibleNodes]);

  const visibleEdges = useMemo(() => {
    return egoGraph.edges.filter(e => visibleNodeMap.has(e.source) && visibleNodeMap.has(e.target));
  }, [egoGraph.edges, visibleNodeMap]);

  // Mouse / Drag Handlers
  const handleMouseDownNode = (e: React.MouseEvent, node: NodePos) => {
    e.stopPropagation();
    dragRef.current = {
      nodeId: node.id,
      startX: e.clientX,
      startY: e.clientY,
      origX: node.x,
      origY: node.y,
      isPanning: false,
      panStartX: 0,
      panStartY: 0
    };
    setNodes(prev => prev.map(n => n.id === node.id ? { ...n, isDragging: true } : n));
  };

  const handleMouseDownCanvas = (e: React.MouseEvent) => {
    dragRef.current = {
      nodeId: null,
      startX: 0,
      startY: 0,
      origX: 0,
      origY: 0,
      isPanning: true,
      panStartX: e.clientX - panOffset.x,
      panStartY: e.clientY - panOffset.y
    };
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (dragRef.current.nodeId) {
      const dx = (e.clientX - dragRef.current.startX) / zoomLevel;
      const dy = (e.clientY - dragRef.current.startY) / zoomLevel;
      const targetId = dragRef.current.nodeId;
      setNodes(prev => prev.map(n => {
        if (n.id === targetId) {
          return {
            ...n,
            x: dragRef.current.origX + dx,
            y: dragRef.current.origY + dy,
            vx: 0,
            vy: 0
          };
        }
        return n;
      }));
    } else if (dragRef.current.isPanning) {
      setPanOffset({
        x: e.clientX - dragRef.current.panStartX,
        y: e.clientY - dragRef.current.panStartY
      });
    }
  };

  const handleMouseUp = () => {
    if (dragRef.current.nodeId) {
      const targetId = dragRef.current.nodeId;
      setNodes(prev => prev.map(n => n.id === targetId ? { ...n, isDragging: false } : n));
    }
    dragRef.current = {
      nodeId: null,
      startX: 0,
      startY: 0,
      origX: 0,
      origY: 0,
      isPanning: false,
      panStartX: 0,
      panStartY: 0
    };
  };

  const patentCount = egoGraph.nodes.filter(n => n.type === 'patent').length;
  const investorCount = egoGraph.nodes.filter(n => n.type === 'investor').length;
  const grantCount = egoGraph.nodes.filter(n => n.type === 'agency' || n.type === 'grant').length;

  return (
    <div className="relative bg-[#070b14] rounded-xl border border-slate-800 shadow-2xl overflow-hidden select-none">
      {/* Studio Toolbar Header */}
      <div className="p-2.5 bg-[#0d1424]/90 border-b border-slate-800/80 flex flex-wrap items-center justify-between gap-2 text-xs">
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-slate-400 font-bold uppercase tracking-wider text-[10px] flex items-center gap-1">
            <Compass size={12} className="text-cyan-400" /> Mode:
          </span>
          <div className="flex items-center bg-slate-900 p-0.5 rounded-lg border border-slate-800">
            {(['orbital', 'physics', 'split'] as const).map(mode => (
              <button
                key={mode}
                onClick={() => setLayoutMode(mode)}
                className={clsx(
                  'px-2 py-0.5 rounded text-[10.5px] font-bold capitalize transition-all',
                  layoutMode === mode ? 'bg-cyan-600 text-white shadow-2xs' : 'text-slate-400 hover:text-white'
                )}
              >
                {mode === 'orbital' ? 'Orbit' : (mode === 'physics' ? 'Network' : 'Stream')}
              </button>
            ))}
          </div>

          {/* Visibility Toggles */}
          <div className="flex items-center gap-1 ml-1">
            {patentCount > 0 && (
              <button
                onClick={() => setShowPatents(!showPatents)}
                className={clsx(
                  'px-1.5 py-0.5 rounded text-[10px] font-bold border transition-colors flex items-center gap-1',
                  showPatents ? 'bg-amber-950/80 text-amber-300 border-amber-600/80' : 'bg-slate-900 text-slate-500 border-slate-800'
                )}
              >
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                <span>Patents ({patentCount})</span>
              </button>
            )}

            {investorCount > 0 && (
              <button
                onClick={() => setShowInvestors(!showInvestors)}
                className={clsx(
                  'px-1.5 py-0.5 rounded text-[10px] font-bold border transition-colors flex items-center gap-1',
                  showInvestors ? 'bg-emerald-950/80 text-emerald-300 border-emerald-600/80' : 'bg-slate-900 text-slate-500 border-slate-800'
                )}
              >
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                <span>VC ({investorCount})</span>
              </button>
            )}

            {grantCount > 0 && (
              <button
                onClick={() => setShowGrants(!showGrants)}
                className={clsx(
                  'px-1.5 py-0.5 rounded text-[10px] font-bold border transition-colors flex items-center gap-1',
                  showGrants ? 'bg-indigo-950/80 text-indigo-300 border-indigo-600/80' : 'bg-slate-900 text-slate-500 border-slate-800'
                )}
              >
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
                <span>Grants ({grantCount})</span>
              </button>
            )}
          </div>
        </div>

        {/* Zoom & View Controls */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => setZoomLevel(z => Math.max(0.6, z - 0.15))}
            className="p-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-800 transition-colors"
            title="Zoom Out"
          >
            <ZoomOut size={12} />
          </button>
          <button
            onClick={() => { setZoomLevel(1); setPanOffset({ x: 0, y: 0 }); }}
            className="px-1.5 py-0.5 text-[9.5px] font-mono rounded bg-slate-900 text-slate-400 hover:text-white border border-slate-800"
            title="Reset View"
          >
            100%
          </button>
          <button
            onClick={() => setZoomLevel(z => Math.min(2.0, z + 0.15))}
            className="p-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-800 transition-colors"
            title="Zoom In"
          >
            <ZoomIn size={12} />
          </button>
        </div>
      </div>

      {/* Interactive SVG Canvas */}
      <div
        className="relative overflow-hidden cursor-grab active:cursor-grabbing"
        style={{ height }}
        onMouseDown={handleMouseDownCanvas}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <svg
          ref={svgRef}
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-full"
        >
          <defs>
            {/* Background Cyber Grid */}
            <pattern id="egoGrid" width="30" height="30" patternUnits="userSpaceOnUse">
              <path d="M 30 0 L 0 0 0 30" fill="none" stroke="rgba(255, 255, 255, 0.03)" strokeWidth="1" />
            </pattern>
            {/* Glow Filter */}
            <filter id="neonGlow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            <radialGradient id="centerCoreGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#0ea5e9" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#0ea5e9" stopOpacity="0" />
            </radialGradient>
          </defs>

          {/* Background Grid */}
          <rect width={width} height={height} fill="url(#egoGrid)" />

          <g
            transform={`translate(${panOffset.x}, ${panOffset.y}) scale(${zoomLevel})`}
            style={{ transformOrigin: `${centerX}px ${centerY}px` }}
          >
            {/* Center Core Background Halo */}
            <circle cx={centerX} cy={centerY} r={80} fill="url(#centerCoreGlow)" />

            {/* Orbit Guides when in orbital mode */}
            {layoutMode === 'orbital' && (
              <>
                <circle cx={centerX} cy={centerY} r={100} fill="none" stroke="rgba(255, 255, 255, 0.05)" strokeDasharray="3 3" />
                <circle cx={centerX} cy={centerY} r={130} fill="none" stroke="rgba(255, 255, 255, 0.04)" strokeDasharray="4 4" />
              </>
            )}

            {/* Draw Edges */}
            {visibleEdges.map((e, idx) => {
              const src = visibleNodeMap.get(e.source);
              const tgt = visibleNodeMap.get(e.target);
              if (!src || !tgt) return null;

              const isHighlighted = (hoveredNode && (hoveredNode.id === src.id || hoveredNode.id === tgt.id)) ||
                                    (selectedNode && (selectedNode.id === src.id || selectedNode.id === tgt.id));

              return (
                <g key={idx}>
                  <line
                    x1={src.x}
                    y1={src.y}
                    x2={tgt.x}
                    y2={tgt.y}
                    stroke={isHighlighted ? '#38bdf8' : (e.color || '#334155')}
                    strokeWidth={isHighlighted ? 2.5 : 1.3}
                    strokeOpacity={isHighlighted ? 0.9 : 0.45}
                    strokeDasharray={isHighlighted ? 'none' : '4 2'}
                  />
                  {/* Subtle edge particle glow */}
                  {isHighlighted && (
                    <circle
                      cx={(src.x + tgt.x) / 2}
                      cy={(src.y + tgt.y) / 2}
                      r={3}
                      fill="#38bdf8"
                      className="animate-ping"
                    />
                  )}
                </g>
              );
            })}

            {/* Draw Nodes */}
            {visibleNodes.map((node) => {
              const isCenter = node.type === 'company';
              const isSelected = selectedNode?.id === node.id;
              const isHovered = hoveredNode?.id === node.id;
              const nodeRadius = isCenter ? 20 : node.size;

              return (
                <g
                  key={node.id}
                  transform={`translate(${node.x}, ${node.y})`}
                  className="cursor-pointer"
                  onMouseDown={(e) => handleMouseDownNode(e, node)}
                  onMouseEnter={() => setHoveredNode(node)}
                  onMouseLeave={() => setHoveredNode(null)}
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedNode(node);
                  }}
                >
                  {/* Glow Aura when Hovered / Selected */}
                  {(isSelected || isHovered || isCenter) && (
                    <circle
                      r={nodeRadius + (isCenter ? 8 : 6)}
                      fill={node.color}
                      fillOpacity={isCenter ? 0.25 : 0.35}
                      filter="url(#neonGlow)"
                    />
                  )}

                  <circle
                    r={nodeRadius}
                    fill={node.color}
                    stroke={isSelected ? '#ffffff' : (isCenter ? '#38bdf8' : '#0f172a')}
                    strokeWidth={isSelected ? 3 : (isCenter ? 2.5 : 1.5)}
                    className="transition-transform duration-150 hover:scale-115"
                  />

                  {/* Node Glyph Icon or First Letter */}
                  <text
                    dy={3.5}
                    textAnchor="middle"
                    fill="#ffffff"
                    fontSize={isCenter ? '11px' : '9px'}
                    fontWeight="bold"
                    className="pointer-events-none select-none"
                  >
                    {isCenter ? 'HQ' : (node.type === 'patent' ? 'IP' : (node.type === 'investor' ? 'VC' : 'GOV'))}
                  </text>

                  {/* Node Label Text */}
                  <text
                    dy={nodeRadius + 11}
                    textAnchor="middle"
                    fill={isSelected ? '#ffffff' : (isHovered ? '#e2e8f0' : '#94a3b8')}
                    fontSize={isCenter ? '9px' : '7.5px'}
                    fontWeight={isCenter || isSelected ? 'bold' : 'normal'}
                    className="pointer-events-none select-none drop-shadow"
                  >
                    {node.name.length > 16 ? `${node.name.slice(0, 14)}...` : node.name}
                  </text>
                </g>
              );
            })}
          </g>
        </svg>

        {/* Hover Tooltip HUD */}
        {hoveredNode && !selectedNode && (
          <div className="absolute bottom-2.5 left-2.5 bg-slate-900/95 border border-slate-700 text-white px-3 py-2 rounded-lg shadow-xl text-xs max-w-xs pointer-events-none animate-in fade-in duration-150">
            <div className="flex items-center gap-1.5">
              <span className={clsx(
                'px-1.5 py-0.2 rounded text-[9px] font-bold uppercase',
                hoveredNode.type === 'patent' ? 'bg-amber-500/20 text-amber-300' :
                hoveredNode.type === 'investor' ? 'bg-emerald-500/20 text-emerald-300' :
                hoveredNode.type === 'company' ? 'bg-sky-500/20 text-sky-300' : 'bg-indigo-500/20 text-indigo-300'
              )}>
                {hoveredNode.type === 'patent' ? 'USPTO Patent' : (hoveredNode.type === 'investor' ? 'VC Investor' : hoveredNode.type)}
              </span>
              <span className="font-bold text-slate-100 truncate">{hoveredNode.name}</span>
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">Drag to rearrange or click for complete details.</div>
          </div>
        )}

        {/* Clicked Node Detail Popup Modal */}
        {selectedNode && (
          <div className="absolute top-2.5 right-2.5 w-64 bg-slate-900/95 border border-slate-700 text-white p-3 rounded-xl shadow-2xl text-xs space-y-2.5 animate-in slide-in-from-right duration-150">
            <div className="flex items-start justify-between">
              <div>
                <span className={clsx(
                  'px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider',
                  selectedNode.type === 'patent' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                  selectedNode.type === 'investor' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                  selectedNode.type === 'company' ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30' : 'bg-indigo-500/20 text-indigo-300'
                )}>
                  {selectedNode.type === 'patent' ? 'USPTO Bayh-Dole Patent' : (selectedNode.type === 'investor' ? 'Syndicate Investor' : 'Scale-Up Startup')}
                </span>
                <h4 className="font-bold text-xs text-slate-100 mt-1 leading-snug">{selectedNode.name}</h4>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="p-1 text-slate-400 hover:text-white rounded-lg transition-colors"
              >
                <X size={13} />
              </button>
            </div>

            {selectedNode.type === 'patent' && (
              <div className="pt-1.5 border-t border-slate-800 text-[10.5px] space-y-1.5">
                <p className="text-slate-300 leading-relaxed">
                  Verified Bayh-Dole intellectual property assigned to {companyName}.
                </p>
                <a
                  href={`https://patents.google.com/patent/${selectedNode.name.replace(/[^A-Za-z0-9]/g, '')}/en`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-amber-400 hover:text-amber-300 font-bold"
                >
                  <span>Google Patents</span>
                  <ExternalLink size={10} />
                </a>
              </div>
            )}

            {selectedNode.type === 'investor' && (
              <div className="pt-1.5 border-t border-slate-800 text-[10.5px]">
                <p className="text-slate-300 leading-relaxed">
                  Institutional venture capital fund backing {companyName}'s commercialization.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
