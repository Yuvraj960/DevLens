'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import type { ProjectSummary } from '@/types/api';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Sparkles, Clock, AlertTriangle, Layers, Database, Shield, FileCode } from 'lucide-react';

interface SummaryDashboardProps {
  repoId: string;
}

export const SummaryDashboard: React.FC<SummaryDashboardProps> = ({ repoId }) => {
  const [summary, setSummary] = useState<ProjectSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadSummary() {
      setLoading(true);
      try {
        const data = await api.getSummary(repoId);
        setSummary(data);
      } catch (err) {
        console.error('Failed to fetch summary:', err);
      } finally {
        setLoading(false);
      }
    }
    loadSummary();
  }, [repoId]);

  if (loading) {
    return <div className="py-12 text-center text-xs font-mono text-slate-500 animate-pulse">Running AI Stack Fingerprinting & Summary Engine...</div>;
  }

  if (!summary) {
    return <div className="py-12 text-center text-xs text-rose-400">Failed to load project summary.</div>;
  }

  const stack = summary.stack || {};
  const metrics = summary.metrics || {};
  const keyModules = summary.key_modules || [];
  const entryPoints = summary.entry_points || [];
  const risks = summary.risks || [];

  return (
    <div className="space-y-6">
      {/* Overview Hero Card */}
      <Card className="p-6 border-indigo-500/20 bg-gradient-to-br from-slate-900 via-slate-900/90 to-indigo-950/30">
        <div className="flex items-center gap-2 text-xs font-mono text-indigo-400 mb-2">
          <Sparkles className="w-4 h-4" /> AI Repository Analysis
        </div>
        <p className="text-sm text-slate-200 leading-relaxed font-sans">{summary.overview || 'Analyzing codebase metrics...'}</p>

        {/* Stack Badges */}
        <div className="flex flex-wrap gap-2 mt-4">
          <Badge variant="default"><Layers className="w-3 h-3 mr-1" /> {stack.framework || 'Custom Architecture'}</Badge>
          <Badge variant="outline"><FileCode className="w-3 h-3 mr-1" /> {stack.language || 'Multi-language'}</Badge>
          <Badge variant="outline"><Database className="w-3 h-3 mr-1" /> {stack.database || 'No Database'}</Badge>
          <Badge variant="outline"><Shield className="w-3 h-3 mr-1" /> {stack.auth || 'Basic Auth'}</Badge>
        </div>
      </Card>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="p-4 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono text-slate-500 uppercase block">Complexity Rating</span>
            <span className="text-2xl font-bold text-slate-100">{metrics.complexity_score ?? 1} / 10</span>
          </div>
          <div className="w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 font-bold">
            {(metrics.complexity_score ?? 1) > 6 ? 'HIGH' : 'MED'}
          </div>
        </Card>

        <Card className="p-4 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono text-slate-500 uppercase block">Est. Onboarding Time</span>
            <span className="text-2xl font-bold text-slate-100">{Math.round((metrics.estimated_onboarding_minutes || 60) / 60 * 10) / 10} hrs</span>
          </div>
          <div className="w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <Clock className="w-5 h-5" />
          </div>
        </Card>

        <Card className="p-4 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono text-slate-500 uppercase block">Code Risks Flagged</span>
            <span className="text-2xl font-bold text-slate-100">{risks.length}</span>
          </div>
          <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </Card>
      </div>

      {/* Key Modules & Entry Points */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-5 space-y-3">
          <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">Key Architectural Modules</h4>
          <div className="space-y-2">
            {keyModules.map((mod) => (
              <div key={mod.path || mod.name} className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800 text-xs">
                <div className="flex justify-between font-mono font-medium text-indigo-300 mb-1">
                  <span>{mod.name}</span>
                  <span className="text-[10px] text-slate-500">Imp: {mod.importance}/10</span>
                </div>
                <p className="text-[11px] text-slate-400">{mod.purpose}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-5 space-y-3">
          <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">Entry Points & Bootstrap Files</h4>
          <div className="space-y-2">
            {entryPoints.map((ep) => (
              <div key={ep.file_path || ep.name} className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800 text-xs">
                <div className="flex justify-between font-mono font-medium text-emerald-400 mb-1">
                  <span>{ep.name}</span>
                  <Badge variant="outline">{ep.type}</Badge>
                </div>
                <p className="text-[11px] text-slate-400">{ep.description}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};
