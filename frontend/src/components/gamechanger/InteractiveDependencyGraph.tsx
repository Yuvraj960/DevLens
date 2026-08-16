'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import type { DependencyGraphData } from '@/types/api';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Network, Search, Cpu, HelpCircle } from 'lucide-react';

interface InteractiveDependencyGraphProps {
  repoId: string;
}

type DependencyGraphNode = DependencyGraphData['nodes'][0];

export const InteractiveDependencyGraph: React.FC<InteractiveDependencyGraphProps> = ({ repoId }) => {
  const [graph, setGraph] = useState<DependencyGraphData | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadGraph() {
      setLoading(true);
      try {
        const data = await api.getDependencyGraph(repoId);
        setGraph(data);
        if (data.nodes.length > 0) setSelectedNodeId(data.nodes[0].id);
      } catch (err) {
        console.error('Failed to load dependency graph:', err);
      } finally {
        setLoading(false);
      }
    }
    loadGraph();
  }, [repoId]);

  if (loading) {
    return <div className="py-16 text-center text-xs font-mono text-slate-500 animate-pulse">Constructing interactive symbol import dependency graph...</div>;
  }

  if (!graph) {
    return <div className="py-16 text-center text-xs text-rose-400">Failed to load dependency graph.</div>;
  }

  const filteredNodes = graph.nodes.filter(
    (n) => n.label.toLowerCase().includes(searchQuery.toLowerCase()) || n.file_path.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const selectedNode = graph.nodes.find((n) => n.id === selectedNodeId);

  // Get active orbit connections for the selected node
  const activeEdges = graph.edges.filter(
    (e) => e.source === selectedNodeId || e.target === selectedNodeId
  );
  
  const orbitNodes: DependencyGraphNode[] = [];
  activeEdges.forEach((edge) => {
    const otherId = edge.source === selectedNodeId ? edge.target : edge.source;
    const otherNode = graph.nodes.find((n) => n.id === otherId);
    if (otherNode && !orbitNodes.some((n) => n.id === otherNode.id)) {
      orbitNodes.push(otherNode);
    }
  });

  // Limit visual nodes on SVG to top 8 to prevent overlap, full list remains interactive below
  const maxVisualOrbits = 8;
  const visualOrbitNodes = orbitNodes.slice(0, maxVisualOrbits);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center gap-2 font-mono">
            <Network className="w-5 h-5 text-indigo-400" /> Interactive Symbol Import Dependency Graph
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">Explore import reference connections across all codebase symbols.</p>
        </div>

        {/* Search Input */}
        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search symbol or path..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      {/* Guide Note Box */}
      <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-850 text-xs text-slate-400 font-mono flex items-start gap-2.5 leading-relaxed">
        <HelpCircle className="w-4.5 h-4.5 text-indigo-400 shrink-0 mt-0.5" />
        <div>
          <span className="text-slate-200 font-bold block mb-0.5">How to operate:</span>
          Select any symbol from the list on the left to center the orbit graph around it.
          Clicking any surrounding orbiting node on the canvas instantly shifts focus to that symbol, pulling its own dependencies into view!
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Symbol Nodes List */}
        <div className="lg:col-span-1 space-y-3">
          <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono">
            Symbols ({filteredNodes.length})
          </h3>
          <div className="space-y-2 max-h-[480px] overflow-y-auto pr-1">
            {filteredNodes.map((node) => (
              <Card
                key={node.id}
                onClick={() => setSelectedNodeId(node.id)}
                className={`p-3.5 cursor-pointer transition-all ${
                  selectedNodeId === node.id ? 'border-indigo-500 bg-slate-900/60' : 'hover:border-slate-700 bg-slate-950/40'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-slate-100 flex items-center gap-2">
                    <Cpu className="w-3.5 h-3.5 text-indigo-400" /> {node.label}
                  </span>
                  <Badge variant="outline" className="text-[9px]">
                    {node.kind}
                  </Badge>
                </div>
                <div className="text-[10px] font-mono text-slate-500 truncate mt-1">{node.file_path}</div>
              </Card>
            ))}
          </div>
        </div>

        {/* Selected Node Details & Connected Edges Canvas */}
        <div className="lg:col-span-2 space-y-4">
          {selectedNode ? (
            <Card className="p-5 space-y-5 border-slate-900 bg-slate-950/80">
              <div className="border-b border-slate-800 pb-3">
                <span className="text-[9px] font-mono text-slate-500 uppercase block tracking-wider">Dependency Orbit</span>
                <h3 className="font-mono text-base font-bold text-slate-100 flex items-center gap-2">
                  <Cpu className="w-5 h-5 text-indigo-400" /> {selectedNode.label}
                </h3>
                <p className="text-[10px] font-mono text-slate-400 mt-1">{selectedNode.file_path}:{selectedNode.line}</p>
              </div>

              {/* Dynamic SVG dependency star chart */}
              <div className="bg-slate-950/60 border border-slate-900 rounded-xl p-4 flex items-center justify-center min-h-[350px] relative">
                <svg className="w-full max-w-[600px] h-[320px]" viewBox="0 0 600 320" xmlns="http://www.w3.org/2000/svg">
                  {(() => {
                    const cx = 300;
                    const cy = 160;
                    const r = 135; // Increased orbit radius to completely avoid overlapping

                    return (
                      <>
                        {/* Draw connection lines to orbit nodes */}
                        {visualOrbitNodes.map((node, idx) => {
                          const angle = (idx * 2 * Math.PI) / visualOrbitNodes.length;
                          const ox = cx + r * Math.cos(angle);
                          const oy = cy + r * Math.sin(angle);

                          return (
                            <line
                              key={`line-${node.id}`}
                              x1={cx}
                              y1={cy}
                              x2={ox}
                              y2={oy}
                              stroke="#1e293b"
                              strokeWidth="1.5"
                            />
                          );
                        })}

                        {/* Orbit nodes */}
                        {visualOrbitNodes.map((node, idx) => {
                          const angle = (idx * 2 * Math.PI) / visualOrbitNodes.length;
                          const ox = cx + r * Math.cos(angle);
                          const oy = cy + r * Math.sin(angle);

                          return (
                            <g
                              key={node.id}
                              transform={`translate(${ox - 55}, ${oy - 16})`}
                              className="cursor-pointer"
                              onClick={() => setSelectedNodeId(node.id)}
                            >
                              <rect
                                width="110"
                                height="32"
                                rx="6"
                                className="fill-slate-950 stroke-slate-800 hover:stroke-slate-400 transition-colors"
                              />
                              <text
                                x="55"
                                y="20"
                                textAnchor="middle"
                                className="fill-slate-200 font-mono text-[9px] font-bold truncate max-w-[95px]"
                              >
                                {node.label.slice(0, 16)}
                              </text>
                            </g>
                          );
                        })}

                        {/* Draw central node */}
                        <g transform={`translate(${cx - 70}, ${cy - 20})`}>
                          <rect
                            width="140"
                            height="40"
                            rx="8"
                            className="fill-indigo-950/80 stroke-indigo-500 stroke-2 animate-pulse"
                          />
                          <text
                            x="70"
                            y="25"
                            textAnchor="middle"
                            className="fill-indigo-300 font-mono text-[10px] font-bold truncate max-w-[125px]"
                          >
                            {selectedNode.label.slice(0, 18)}
                          </text>
                        </g>
                      </>
                    );
                  })()}
                </svg>
              </div>

              {/* Orbit Connection Details */}
              <div className="space-y-2">
                <h4 className="text-[10px] font-bold text-slate-400 uppercase font-mono tracking-wider">
                  Full Dependencies list ({orbitNodes.length})
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-40 overflow-y-auto pr-1">
                  {orbitNodes.map((node) => (
                    <div
                      key={node.id}
                      onClick={() => setSelectedNodeId(node.id)}
                      className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 text-[10px] font-mono flex items-center justify-between cursor-pointer hover:border-slate-400"
                    >
                      <span className="font-bold text-indigo-300 truncate max-w-[170px]">{node.label}</span>
                      <Badge variant="outline" className="text-[8px]">{node.kind}</Badge>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          ) : (
            <Card className="p-12 text-center text-xs text-slate-500 font-mono">Select a symbol to inspect import dependency connections.</Card>
          )}
        </div>
      </div>
    </div>
  );
};
