import React, { useEffect, useRef } from 'react';
import Graph from 'graphology';
import { SigmaContainer, useLoadGraph } from '@react-sigma/core';
import "@react-sigma/core/lib/style.css";
import forceAtlas2 from 'graphology-layout-forceatlas2';

interface NetworkGraphProps {
  nodes: Array<{ id: string; label: string; size?: number; color?: string }>;
  edges: Array<{ source: string; target: string; color?: string }>;
  onNodeClick?: (id: string) => void;
}

const GraphLoader = ({ nodes, edges }: { nodes: any[], edges: any[] }) => {
  const loadGraph = useLoadGraph();

  useEffect(() => {
    const graph = new Graph();
    
    nodes.forEach(node => {
      if (!graph.hasNode(node.id)) {
        graph.addNode(node.id, {
          x: Math.random(),
          y: Math.random(),
          size: node.size || 5,
          label: node.label,
          color: node.color || '#6366f1'
        });
      }
    });

    edges.forEach(edge => {
      if (graph.hasNode(edge.source) && graph.hasNode(edge.target) && !graph.hasEdge(edge.source, edge.target)) {
        graph.addEdge(edge.source, edge.target, {
          color: edge.color || '#cbd5e1',
          size: 1
        });
      }
    });

    if (nodes.length > 0) {
      forceAtlas2.assign(graph, { iterations: 100, settings: forceAtlas2.inferSettings(graph) });
    }
    
    loadGraph(graph);
  }, [nodes, edges, loadGraph]);

  return null;
};

export function NetworkGraph({ nodes, edges, onNodeClick }: NetworkGraphProps) {
  return (
    <div className="w-full h-full bg-white rounded-xl border border-slate-200 overflow-hidden relative">
      <SigmaContainer style={{ width: '100%', height: '100%' }} settings={{ allowInvalidContainer: true }}>
        <GraphLoader nodes={nodes} edges={edges} />
      </SigmaContainer>
    </div>
  );
}
