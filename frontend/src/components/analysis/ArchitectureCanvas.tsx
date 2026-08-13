'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import type { ArchNode, ArchitectureDiagram } from '@/types/api';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Layers, GitFork, Box, FileText, Code2 } from 'lucide-react';

interface ArchitectureCanvasProps {
  repoId: string;
}

export const ArchitectureCanvas: React.FC<ArchitectureCanvasProps> = ({ repoId }) => {
  const [diagram, setDiagram] = useState<ArchitectureDiagram | null>(null);
  const [selectedNode, setSelectedNode] = useState<ArchNode | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadArch() {
      setLoading(true);
      try {
        const data = await api.getArchitecture(repoId);
        setDiagram(data);
        if (data.nodes && data.nodes.length > 0) {
          setSelectedNode(data.nodes[0]);
        }
      } catch (err) {
        console.error('Failed to load architecture:', err);
      } finally {
        setLoading(false);
      }
    }
    loadArch();
  }, [repoId]);

  if (loading) {
    return <div className="py-16 text-center text-xs font-mono text-slate-500 animate-pulse">Clustering system layers and generating architecture topology map...</div>;
  }

  if (!diagram || !diagram.nodes || diagram.nodes.length === 0) {
    return <div className="py-16 text-center text-xs text-rose-400 font-mono">Failed to load architecture topology diagram.</div>;
  }

  const layerStyles: Record<string, { border: string; bg: string; text: string; label: string }> = {
    presentation: { border: 'border-blue-500/30', bg: 'bg-blue-500/5', text: 'text-blue-400', label: 'Presentation Layer' },
    api: { border: 'border-indigo-500/30', bg: 'bg-indigo-500/5', text: 'text-indigo-400', label: 'API & Gateway Layer' },
    business_logic: { border: 'border-purple-500/30', bg: 'bg-purple-500/5', text: 'text-purple-400', label: 'Service & Business Logic' },
    data_access: { border: 'border-emerald-500/30', bg: 'bg-emerald-500/5', text: 'text-emerald-400', label: 'Data Access & ORM Repository' },
    external: { border: 'border-amber-500/30', bg: 'bg-amber-500/5', text: 'text-amber-400', label: 'External Services & APIs' },
    infrastructure: { border: 'border-slate-700/50', bg: 'bg-slate-800/10', text: 'text-slate-300', label: 'Infrastructure & System Core' },
  };

  // Filter ONLY active layers that contain nodes to eliminate weird gaps
  const activeLayers = (diagram.layers || []).filter((layer) =>
    diagram.nodes.some((n) => n.layer === layer)
  );

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* System Topology Map */}
      <div className="lg:col-span-2 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2 font-mono">
            <Layers className="w-4 h-4 text-indigo-400" /> Layered System Topology Map
          </h3>
          <Badge variant="outline" className="font-mono text-[10px] text-slate-400">
            {diagram.nodes.length} Component Clusters Across {activeLayers.length} Active Layers
          </Badge>
        </div>

        <div className="space-y-4">
          {activeLayers.map((layer) => {
            const layerNodes = diagram.nodes.filter((n) => n.layer === layer);
            const style = layerStyles[layer] || { border: 'border-slate-800', bg: 'bg-slate-900/20', text: 'text-slate-400', label: layer.replace('_', ' ') };

            return (
              <div
                key={layer}
                className={`p-4 rounded-2xl border ${style.border} ${style.bg} space-y-3`}
              >
                {/* Layer Header */}
                <div className="flex items-center justify-between">
                  <span className={`text-xs font-mono font-bold uppercase tracking-wider ${style.text}`}>
                    {style.label}
                  </span>
                  <span className="text-[10px] font-mono text-slate-500 font-bold">
                    {layerNodes.length} Clusters
                  </span>
                </div>

                {/* Flexbox Wrapping Grid with generous 16px gap separation */}
                <div className="flex flex-wrap gap-4">
                  {layerNodes.map((node) => {
                    const isSelected = selectedNode?.id === node.id;

                    return (
                      <Card
                        key={node.id}
                        onClick={() => setSelectedNode(node)}
                        className={`p-3.5 cursor-pointer transition-all border min-w-[200px] flex-1 ${
                          isSelected
                            ? 'border-indigo-500 bg-slate-900/90 shadow-lg shadow-indigo-500/10'
                            : 'border-slate-900 bg-slate-950/80 hover:border-slate-800'
                        }`}
                      >
                        <div className="flex items-center justify-between gap-2">
                          <h4 className="font-mono text-xs font-bold text-slate-100 flex items-center gap-1.5 truncate">
                            <Box className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0" />
                            <span className="truncate">{node.label}</span>
                          </h4>
                        </div>

                        <div className="mt-2 flex items-center justify-between text-[10px] font-mono text-slate-400">
                          <span className="flex items-center gap-1">
                            <FileText className="w-3 h-3 text-slate-500" /> {node.metadata.file_count} Files
                          </span>
                          <span className="flex items-center gap-1">
                            <Code2 className="w-3 h-3 text-slate-500" /> {node.metadata.loc} LOC
                          </span>
                        </div>
                      </Card>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Cluster Inspector Drawer */}
      <div className="lg:col-span-1 space-y-4">
        <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono">
          Node Inspector
        </h3>

        {selectedNode ? (
          <Card className="p-5 space-y-5 border-slate-900 bg-slate-950/80">
            <div>
              <Badge variant="outline" className="capitalize text-[10px] mb-2 font-mono">
                {selectedNode.layer.replace('_', ' ')}
              </Badge>
              <h4 className="font-mono text-sm font-bold text-slate-100 flex items-center gap-2">
                <GitFork className="w-4 h-4 text-indigo-400" /> {selectedNode.label}
              </h4>
              <p className="text-[11px] text-slate-400 mt-1 font-mono">
                Contains {selectedNode.metadata.file_count} files ({selectedNode.metadata.loc} LOC).
              </p>
            </div>

            <div className="space-y-2">
              <h5 className="text-[10px] font-bold text-slate-400 uppercase font-mono tracking-wider">Contained File Paths</h5>
              <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                {selectedNode.file_paths.map((fp) => (
                  <div key={fp} className="text-[10px] font-mono text-slate-300 bg-slate-900/80 p-2.5 rounded-xl border border-slate-800/80 truncate">
                    {fp}
                  </div>
                ))}
              </div>
            </div>

            {selectedNode.symbols && selectedNode.symbols.length > 0 && (
              <div className="space-y-2">
                <h5 className="text-[10px] font-bold text-slate-400 uppercase font-mono tracking-wider">Exported AST Symbols</h5>
                <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                  {selectedNode.symbols.map((sym) => (
                    <div key={sym.id} className="text-[10px] font-mono text-indigo-300 bg-indigo-950/20 p-2 rounded-lg border border-indigo-900/30 flex justify-between items-center">
                      <span className="font-bold truncate max-w-[140px]">{sym.name}</span>
                      <span className="text-[8px] uppercase tracking-wider font-bold text-slate-400 bg-slate-900 px-1.5 py-0.5 rounded">{sym.kind}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        ) : (
          <Card className="p-12 text-center text-xs text-slate-500 font-mono">Select a topology cluster node to inspect files and AST symbols.</Card>
        )}
      </div>
    </div>
  );
};
