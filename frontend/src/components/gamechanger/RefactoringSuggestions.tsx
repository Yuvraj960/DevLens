'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import type { RefactoringSuggestion } from '@/types/api';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Wrench, Code2, ArrowUpRight, Flame } from 'lucide-react';

interface RefactoringSuggestionsProps {
  repoId: string;
}

export const RefactoringSuggestions: React.FC<RefactoringSuggestionsProps> = ({ repoId }) => {
  const [suggestions, setSuggestions] = useState<RefactoringSuggestion[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadRefactors() {
      setLoading(true);
      try {
        const data = await api.postRefactor(repoId);
        setSuggestions(data);
      } catch (err) {
        console.error('Failed to load refactoring suggestions:', err);
      } finally {
        setLoading(false);
      }
    }
    loadRefactors();
  }, [repoId]);

  if (loading) {
    return <div className="py-16 text-center text-xs font-mono text-slate-500 animate-pulse">Calculating AST cyclomatic and cognitive complexity metrics...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-800 pb-3">
        <h2 className="text-base font-bold text-slate-100 flex items-center gap-2 font-mono">
          <Wrench className="w-5 h-5 text-indigo-400" /> AST Complexity & Refactoring Suggestions ({suggestions.length})
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">Identifies high-complexity monolithic functions and proposes structured refactors.</p>
      </div>

      <div className="space-y-4">
        {suggestions.map((item) => (
          <Card key={item.id} className="p-5 space-y-4 bg-slate-950/80 border-slate-800 hover:border-slate-700 transition-all">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
              <div>
                <h3 className="font-mono text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Flame className="w-4 h-4 text-amber-400" /> Refactor `{item.symbol_name}`
                </h3>
                <p className="text-xs text-rose-400 font-mono mt-0.5">{item.issue}</p>
              </div>

              <div className="flex items-center gap-2 font-mono text-xs">
                <Badge variant="warning">Impact: {item.impact}</Badge>
                <Badge variant="outline">Effort: {item.effort}</Badge>
              </div>
            </div>

            {/* Metrics Bar */}
            <div className="grid grid-cols-3 gap-3 text-xs font-mono bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <div>
                <span className="text-[10px] text-slate-500 uppercase block">Cyclomatic</span>
                <span className="text-indigo-300 font-bold">{item.metrics.cyclomatic_complexity}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase block">Cognitive</span>
                <span className="text-purple-300 font-bold">{item.metrics.cognitive_complexity}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase block">Lines of Code</span>
                <span className="text-slate-200 font-bold">{item.metrics.loc} LOC</span>
              </div>
            </div>

            {/* Proposed Diff Block */}
            <div className="space-y-1.5">
              <span className="text-[10px] font-mono uppercase text-slate-400 font-bold flex items-center gap-1">
                <Code2 className="w-3.5 h-3.5 text-indigo-400" /> Proposed Refactor Diff
              </span>
              <pre className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-slate-300 overflow-x-auto">
                {item.proposed_diff}
              </pre>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
