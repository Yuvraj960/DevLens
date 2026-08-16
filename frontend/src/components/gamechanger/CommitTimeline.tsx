'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import type { CommitTimelineEra } from '@/types/api';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { History, GitCommit, Calendar, User, Sparkles } from 'lucide-react';

interface CommitTimelineProps {
  repoId: string;
}

export const CommitTimeline: React.FC<CommitTimelineProps> = ({ repoId }) => {
  const [timeline, setTimeline] = useState<CommitTimelineEra[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadTimeline() {
      setLoading(true);
      try {
        const data = await api.getTimeline(repoId);
        setTimeline(data);
      } catch (err) {
        console.error('Failed to load commit timeline:', err);
      } finally {
        setLoading(false);
      }
    }
    loadTimeline();
  }, [repoId]);

  if (loading) {
    return <div className="py-16 text-center text-xs font-mono text-slate-500 animate-pulse">Parsing git log history and generating chronological era summaries...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-800 pb-3">
        <h2 className="text-base font-bold text-slate-100 flex items-center gap-2 font-mono">
          <History className="w-5 h-5 text-indigo-400" /> Chronological Architectural Commit Timeline
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">Narrates repository milestones and key feature evolutions over time.</p>
      </div>

      <div className="space-y-4">
        {timeline.map((era, idx) => (
          <Card key={idx} className="p-5 bg-slate-950/80 border-slate-800 hover:border-slate-700 transition-all space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center gap-2 font-mono text-sm font-bold text-slate-100">
                <GitCommit className="w-4 h-4 text-indigo-400" /> {era.period}
              </div>
              <div className="flex items-center gap-3 text-xs font-mono text-slate-400">
                <span className="flex items-center gap-1"><Calendar className="w-3.5 h-3.5" /> {era.date}</span>
                <span className="flex items-center gap-1"><User className="w-3.5 h-3.5" /> {era.author}</span>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs font-sans text-slate-200 leading-relaxed flex items-start gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
              <span>{era.summary}</span>
            </div>

            <div className="flex items-center gap-4 text-xs font-mono text-slate-400 pt-1">
              <span>Changed: <strong className="text-slate-200">{era.files_changed} files</strong></span>
              <span className="text-emerald-400">+{era.insertions}</span>
              <span className="text-rose-400">-{era.deletions}</span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
