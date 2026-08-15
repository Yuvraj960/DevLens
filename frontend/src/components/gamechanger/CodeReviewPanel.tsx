'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import type { CodeReviewFinding } from '@/types/api';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ShieldAlert, Zap, CheckCircle2, Wrench, Sparkles } from 'lucide-react';

interface CodeReviewPanelProps {
  repoId: string;
}

export const CodeReviewPanel: React.FC<CodeReviewPanelProps> = ({ repoId }) => {
  const [findings, setFindings] = useState<CodeReviewFinding[]>([]);
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadReview() {
      setLoading(true);
      try {
        const data = await api.postCodeReview(repoId);
        setFindings(data);
      } catch (err) {
        console.error('Failed to load code review findings:', err);
      } finally {
        setLoading(false);
      }
    }
    loadReview();
  }, [repoId]);

  if (loading) {
    return <div className="py-16 text-center text-xs font-mono text-slate-500 animate-pulse">Running multi-agent AI code review passes (security, performance, correctness)...</div>;
  }

  const filtered = filterSeverity === 'all' ? findings : findings.filter((f) => f.severity === filterSeverity);

  const categoryIcons: Record<string, React.ReactNode> = {
    security: <ShieldAlert className="w-4 h-4 text-rose-400" />,
    performance: <Zap className="w-4 h-4 text-amber-400" />,
    correctness: <CheckCircle2 className="w-4 h-4 text-emerald-400" />,
    maintainability: <Wrench className="w-4 h-4 text-indigo-400" />,
  };

  return (
    <div className="space-y-6">
      {/* Header & Filter Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center gap-2 font-mono">
            <Sparkles className="w-5 h-5 text-indigo-400" /> Multi-Agent AI Code Review Findings ({filtered.length})
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">Categorized by domain concerns and severity thresholds.</p>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="text-slate-400">Severity:</span>
          {['all', 'high', 'medium', 'low'].map((sev) => (
            <button
              key={sev}
              onClick={() => setFilterSeverity(sev)}
              className={`px-2.5 py-1 rounded text-xs uppercase font-bold transition-all ${
                filterSeverity === sev ? 'bg-indigo-600 text-white' : 'bg-slate-900 text-slate-400 hover:text-slate-200'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Findings Cards List */}
      <div className="space-y-3">
        {filtered.map((item) => (
          <Card key={item.id} className="p-4 bg-slate-950/80 border-slate-800 hover:border-slate-700 transition-all space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 font-mono text-xs font-bold text-slate-100">
                {categoryIcons[item.category]}
                {item.title}
              </div>
              <Badge variant={item.severity === 'high' ? 'error' : 'outline'} className="uppercase text-[10px]">
                {item.severity}
              </Badge>
            </div>

            <p className="text-xs text-slate-300 font-sans">{item.description}</p>

            <div className="p-2.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-xs font-mono text-indigo-300">
              💡 Suggestion: {item.suggestion}
            </div>

            <div className="text-[10px] font-mono text-slate-500">
              Location: {item.file_path}:{item.line} &bull; Symbol: `{item.symbol_name}`
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
