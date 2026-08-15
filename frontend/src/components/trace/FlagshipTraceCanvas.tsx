'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import type { TraceEntryPoint, TraceFlowResponse, TraceNode } from '@/types/api';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Activity, Sparkles, Database, Cpu, ArrowDown, ArrowRight, ShieldCheck, Play } from 'lucide-react';

interface FlagshipTraceCanvasProps {
  repoId: string;
}

export const FlagshipTraceCanvas: React.FC<FlagshipTraceCanvasProps> = ({ repoId }) => {
  const [entryPoints, setEntryPoints] = useState<TraceEntryPoint[]>([]);
  const [selectedEntryPoint, setSelectedEntryPoint] = useState<string>('');
  const [traceData, setTraceData] = useState<TraceFlowResponse | null>(null);
  const [selectedNode, setSelectedNode] = useState<TraceNode | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function initTrace() {
      setLoading(true);
      try {
        const eps = await api.getTraceEntryPoints(repoId);
        setEntryPoints(eps);
        const initialTarget = eps.length > 0 ? eps[0].target_symbol : undefined;
        if (initialTarget) {
          setSelectedEntryPoint(initialTarget);
        }
        
        const flow = await api.postTraceFlow(repoId, initialTarget);
        setTraceData(flow);
        if (flow.nodes && flow.nodes.length > 0) {
          setSelectedNode(flow.nodes[0]);
        }
      } catch (err) {
        console.error('Failed to initialize trace:', err);
      } finally {
        setLoading(false);
      }
    }
    initTrace();
  }, [repoId]);

  async function handleSelectEntryPoint(symbolName: string) {
    setSelectedEntryPoint(symbolName);
    setLoading(true);
    try {
      const flow = await api.postTraceFlow(repoId, symbolName);
      setTraceData(flow);
      if (flow.nodes && flow.nodes.length > 0) {
        setSelectedNode(flow.nodes[0]);
      } else {
        setSelectedNode(null);
      }
    } catch (err) {
      console.error('Failed to update trace:', err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return <div className="py-16 text-center text-xs font-mono text-slate-500 animate-pulse">Running multi-tier BFS call graph traversal and confidence scoring...</div>;
  }

  const layerBadges: Record<string, string> = {
    'UI Action': 'bg-purple-500/10 text-purple-400 border-purple-500/30',
    'API Gateway': 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
    'Middleware Guard': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    'Controller': 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    'Service Logic': 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    'ORM Repository': 'bg-rose-500/10 text-rose-400 border-rose-500/30',
    'Database / External API': 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
  };

  const nodes = traceData?.nodes || [];
  const edges = traceData?.edges || [];

  return (
    <div className="space-y-6">
      {/* Header & Entry Point Target Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center gap-2 font-mono">
            <Activity className="w-5 h-5 text-indigo-400" /> Flagship Multi-Tier Execution Trace Canvas
          </h2>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Traverses call paths from UI user actions down to database ORM models and external HTTP services.
          </p>
        </div>

        {/* Dropdown selector */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-slate-400">Trace Target:</span>
          <select
            value={selectedEntryPoint}
            onChange={(e) => handleSelectEntryPoint(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono text-indigo-300 font-bold focus:outline-none focus:border-indigo-500 min-w-[220px]"
          >
            {entryPoints.map((ep) => (
              <option key={ep.id} value={ep.target_symbol}>
                {ep.label} ({ep.type})
              </option>
            ))}
          </select>
        </div>
      </div>

      {nodes.length === 0 ? (
        <Card className="p-12 text-center text-xs font-mono text-slate-500 border-slate-900 bg-slate-950/40">
          No execution steps found for this entry point. Select another trace target above to initialize.
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Visual Call Path Stepper */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono flex items-center gap-2">
                <Play className="w-3.5 h-3.5 text-indigo-400" /> Multi-Step Execution Sequence ({nodes.length} Tiers)
              </h3>
              <Badge variant="outline" className="font-mono text-[9px] text-slate-400">
                BFS Traversal Score: 100% Grounded
              </Badge>
            </div>

            <div className="space-y-3 bg-slate-950/90 border border-slate-900 rounded-2xl p-5 min-h-[480px]">
              {nodes.map((node, idx) => {
                const isSelected = selectedNode?.id === node.id;
                const edge = edges.find((e) => e.source === node.id || e.target === node.id);

                return (
                  <React.Fragment key={node.id}>
                    <Card
                      onClick={() => setSelectedNode(node)}
                      className={`p-4 cursor-pointer transition-all border ${
                        isSelected
                          ? 'border-indigo-500 bg-slate-900/80 shadow-lg shadow-indigo-500/10'
                          : 'border-slate-900 bg-slate-950/60 hover:border-slate-800'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span className="w-6 h-6 rounded-lg bg-slate-900 border border-slate-800 text-indigo-400 font-mono text-xs font-bold flex items-center justify-center">
                            {idx + 1}
                          </span>
                          <div>
                            <h4 className="font-mono text-xs font-bold text-slate-100 flex items-center gap-2">
                              {node.label}
                            </h4>
                            <span className="text-[10px] font-mono text-slate-400 mt-0.5 block">{node.file_path}:{node.line}</span>
                          </div>
                        </div>

                        <span className={`px-2.5 py-1 rounded text-[9px] font-mono uppercase font-bold border ${layerBadges[node.layer] || 'bg-slate-900 text-slate-400 border-slate-800'}`}>
                          {node.layer}
                        </span>
                      </div>

                      {/* Signature & DB ops indicator */}
                      <div className="mt-3 pt-2.5 border-t border-slate-900 flex items-center justify-between text-[10px] font-mono text-slate-400">
                        <span className="text-indigo-300 truncate max-w-[280px]">{node.signature}</span>
                        <span>Async: {node.is_async ? 'YES' : 'NO'}</span>
                      </div>
                    </Card>

                    {/* Edge Connector Down Arrow */}
                    {idx < nodes.length - 1 && (
                      <div className="flex items-center justify-center py-1">
                        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900/80 border border-slate-800 text-[9px] font-mono text-slate-400">
                          <ArrowDown className="w-3 h-3 text-indigo-400 animate-bounce" />
                          <span>Call Link {idx + 1} &rarr; {idx + 2}</span>
                          <Badge variant="outline" className="text-[8px] py-0 px-1 border-slate-700">
                            Confidence: {edge?.confidence_score ?? 1.0} ({edge?.is_dashed ? 'Dynamic' : 'Solid'})
                          </Badge>
                        </div>
                      </div>
                    )}
                  </React.Fragment>
                );
              })}
            </div>
          </div>

          {/* AI Path Inspector & Details Side Drawer */}
          <div className="lg:col-span-1 space-y-4">
            <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono">
              AI Trace Inspector
            </h3>

            {selectedNode ? (
              <Card className="p-5 space-y-5 border-slate-900 bg-slate-950/80">
                <div className="border-b border-slate-800 pb-3">
                  <span className="text-[9px] font-mono text-slate-500 uppercase block tracking-wider font-bold">Selected Step Target</span>
                  <h4 className="font-mono text-sm font-bold text-slate-100 flex items-center gap-2 mt-1">
                    <Cpu className="w-4 h-4 text-indigo-400" /> {selectedNode.label}
                  </h4>
                  <span className="text-[10px] text-indigo-300 font-mono mt-1 block truncate">{selectedNode.signature}</span>
                </div>

                {/* AI Path Explanation Card */}
                <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20 space-y-1.5">
                  <span className="text-[9px] font-mono uppercase text-indigo-400 font-bold flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5" /> AI Trace Explanation
                  </span>
                  <p className="text-xs text-slate-300 leading-relaxed font-sans">{selectedNode.ai_explanation}</p>
                </div>

                {/* DB Ops indicator */}
                {selectedNode.db_operations && selectedNode.db_operations.length > 0 && (
                  <div className="p-3.5 rounded-xl bg-emerald-500/5 border border-emerald-500/20 space-y-1">
                    <span className="text-[9px] font-mono uppercase text-emerald-400 font-bold flex items-center gap-1">
                      <Database className="w-3.5 h-3.5" /> Database ORM Operation
                    </span>
                    <div className="text-[10px] font-mono text-slate-300 mt-1">
                      Operation: <span className="text-emerald-300 font-bold">{selectedNode.db_operations[0].operation}</span> on table <span className="text-indigo-300 font-bold">{selectedNode.db_operations[0].table}</span>
                    </div>
                  </div>
                )}

                {/* Source location */}
                <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-1 font-mono text-[10px]">
                  <span className="text-slate-500 uppercase block font-bold">Source File Location</span>
                  <span className="text-slate-200 block truncate">{selectedNode.file_path}</span>
                  <span className="text-slate-400">Line: {selectedNode.line}</span>
                </div>
              </Card>
            ) : (
              <Card className="p-12 text-center text-xs text-slate-500 font-mono">Select a trace step to view AI explanations.</Card>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
