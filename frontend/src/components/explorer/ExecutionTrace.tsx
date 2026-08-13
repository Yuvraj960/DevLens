'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import type { CallTraceNode } from '@/types/api';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Activity, GitCommit, CornerDownRight, Cpu } from 'lucide-react';

interface ExecutionTraceProps {
  repoId: string;
}

export const ExecutionTrace: React.FC<ExecutionTraceProps> = ({ repoId }) => {
  const [nodes, setNodes] = useState<CallTraceNode[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadTrace() {
      setLoading(true);
      try {
        const data = await api.getExecutionTrace(repoId);
        setNodes(data);
      } catch (err) {
        console.error('Failed to load execution trace:', err);
      } finally {
        setLoading(false);
      }
    }
    loadTrace();
  }, [repoId]);

  if (loading) {
    return <div className="py-12 text-center text-xs font-mono text-slate-500 animate-pulse">Tracing end-to-end execution paths...</div>;
  }

  if (nodes.length === 0) {
    return <div className="py-12 text-center text-xs text-slate-500">No execution trace data available.</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2 font-mono">
          <Activity className="w-4 h-4 text-indigo-400" /> Function Call Execution Hierarchy
        </h3>
        <Badge variant="outline">{nodes.length} Call Nodes</Badge>
      </div>

      <div className="space-y-3 pl-2">
        {nodes.map((node, i) => (
          <Card
            key={i}
            style={{ marginLeft: `${node.depth * 24}px` }}
            className="p-3.5 bg-slate-950/80 border-slate-800 hover:border-slate-700 transition-all"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {node.depth > 0 && <CornerDownRight className="w-4 h-4 text-slate-500" />}
                <Cpu className="w-4 h-4 text-indigo-400" />
                <span className="font-mono text-xs font-bold text-slate-100">{node.name}</span>
              </div>
              <Badge variant="default" className="text-[10px]">{node.type}</Badge>
            </div>
            <div className="text-[10px] font-mono text-slate-400 mt-1.5 pl-6">
              Location: {node.file_path}:{node.line} &bull; Async: {node.async ? 'YES' : 'NO'}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
