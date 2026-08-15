'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import type { ArchitectureDiffResponse } from '@/types/api';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { GitCompare, PlusCircle, MinusCircle, AlertTriangle, ShieldCheck } from 'lucide-react';

interface ArchitectureDiffProps {
  repoId: string;
}

export const ArchitectureDiff: React.FC<ArchitectureDiffProps> = ({ repoId }) => {
  const [diff, setDiff] = useState<ArchitectureDiffResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDiff() {
      setLoading(true);
      try {
        const data = await api.postDiff(repoId, 'main', 'feature/v2');
        setDiff(data);
      } catch (err) {
        console.error('Failed to load architecture diff:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDiff();
  }, [repoId]);

  if (loading) {
    return <div className="py-16 text-center text-xs font-mono text-slate-500 animate-pulse">Comparing architecture diff between base and feature branches...</div>;
  }

  if (!diff) {
    return <div className="py-16 text-center text-xs text-rose-400">Failed to load architecture diff.</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center gap-2 font-mono">
            <GitCompare className="w-5 h-5 text-indigo-400" /> Architecture Branch Diff Inspector
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Base: <span className="font-mono text-indigo-300">{diff.base_branch}</span> &bull; Head: <span className="font-mono text-indigo-300">{diff.head_branch}</span>
          </p>
        </div>

        <Badge variant={diff.risk_score > 3 ? 'error' : 'success'}>
          Risk Score: {diff.risk_score} / 10
        </Badge>
      </div>

      {/* Grid of Differences */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Added Endpoints */}
        <Card className="p-5 space-y-3 bg-slate-950/80 border-slate-800">
          <h3 className="text-xs font-mono font-bold text-emerald-400 uppercase flex items-center gap-2">
            <PlusCircle className="w-4 h-4" /> Added API Endpoints ({diff.added_endpoints.length})
          </h3>
          <div className="space-y-2">
            {diff.added_endpoints.map((ep, idx) => (
              <div key={idx} className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-xs font-mono text-emerald-300 flex items-center justify-between">
                <span>{ep.method} {ep.path}</span>
                <span className="text-[10px] text-slate-400">{ep.controller}</span>
              </div>
            ))}
          </div>
        </Card>

        {/* Schema Modifications */}
        <Card className="p-5 space-y-3 bg-slate-950/80 border-slate-800">
          <h3 className="text-xs font-mono font-bold text-indigo-400 uppercase flex items-center gap-2">
            <ShieldCheck className="w-4 h-4" /> Schema Modifications ({diff.modified_schemas.length})
          </h3>
          <div className="space-y-2">
            {diff.modified_schemas.map((m, idx) => (
              <div key={idx} className="p-2.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-xs font-mono space-y-1">
                <span className="font-bold text-indigo-300">Table: {m.table}</span>
                <p className="text-[10px] text-slate-300 font-sans">{m.change}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Security Risks Warning */}
      {diff.security_risks.length > 0 && (
        <Card className="p-4 border-amber-500/40 bg-amber-500/5 space-y-2">
          <h4 className="text-xs font-mono font-bold text-amber-400 uppercase flex items-center gap-1.5">
            <AlertTriangle className="w-4 h-4" /> Security & Breaking Change Warnings
          </h4>
          {diff.security_risks.map((r, idx) => (
            <p key={idx} className="text-xs text-slate-300 font-sans">
              &bull; <span className="font-mono text-amber-300">[{r.severity.toUpperCase()}]</span> {r.description}
            </p>
          ))}
        </Card>
      )}
    </div>
  );
};
