'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import type { OnboardingStep } from '@/types/api';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Compass, CheckCircle2, Clock, FileCode, HelpCircle } from 'lucide-react';

interface OnboardingPathProps {
  repoId: string;
}

export const OnboardingPath: React.FC<OnboardingPathProps> = ({ repoId }) => {
  const [steps, setSteps] = useState<OnboardingStep[]>([]);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadOnboarding() {
      setLoading(true);
      try {
        const data = await api.getOnboarding(repoId);
        setSteps(data);
      } catch (err) {
        console.error('Failed to load onboarding path:', err);
      } finally {
        setLoading(false);
      }
    }
    loadOnboarding();
  }, [repoId]);

  function toggleStep(stepNum: number) {
    if (completedSteps.includes(stepNum)) {
      setCompletedSteps(completedSteps.filter((s) => s !== stepNum));
    } else {
      setCompletedSteps([...completedSteps, stepNum]);
    }
  }

  if (loading) {
    return <div className="py-16 text-center text-xs font-mono text-slate-500 animate-pulse">Building topological onboarding reading path...</div>;
  }

  const totalMins = steps.reduce((acc, s) => acc + s.estimated_minutes, 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center gap-2 font-mono">
            <Compass className="w-5 h-5 text-indigo-400" /> AI-Generated 30-Minute Developer Onboarding Path
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">Topological dependency sort of core domain modules and verification checkpoints.</p>
        </div>

        <div className="flex items-center gap-3 text-xs font-mono">
          <Badge variant="outline" className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5 text-indigo-400" /> Est: {totalMins} mins
          </Badge>
          <Badge variant="success">
            {completedSteps.length} / {steps.length} Completed
          </Badge>
        </div>
      </div>

      <div className="space-y-4">
        {steps.map((item) => {
          const isDone = completedSteps.includes(item.step);
          return (
            <Card
              key={item.step}
              className={`p-5 space-y-3 transition-all border ${
                isDone ? 'bg-slate-950/40 border-emerald-500/30 opacity-80' : 'bg-slate-950/80 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 font-mono text-sm font-bold text-slate-100">
                  <button
                    onClick={() => toggleStep(item.step)}
                    className={`w-6 h-6 rounded-full flex items-center justify-center border transition-all ${
                      isDone ? 'bg-emerald-500 text-white border-emerald-400' : 'border-slate-700 text-slate-500 hover:border-indigo-500'
                    }`}
                  >
                    {isDone ? <CheckCircle2 className="w-4 h-4" /> : item.step}
                  </button>
                  {item.title}
                </div>

                <Badge variant="outline" className="text-[10px] font-mono">
                  {item.estimated_minutes} mins
                </Badge>
              </div>

              <p className="text-xs text-slate-300 font-sans pl-9">{item.description}</p>

              {/* Recommended Reading Files */}
              <div className="pl-9 space-y-1 font-mono text-xs">
                <span className="text-[10px] text-slate-500 uppercase block">Key Files to Read:</span>
                <div className="flex flex-wrap gap-2">
                  {item.key_files.map((kf) => (
                    <span key={kf} className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-indigo-300 text-[10px]">
                      <FileCode className="w-3 h-3 inline mr-1" /> {kf}
                    </span>
                  ))}
                </div>
              </div>

              {/* Checkpoint Question */}
              <div className="pl-9 text-xs font-mono text-indigo-300 bg-indigo-500/10 p-2.5 rounded-lg border border-indigo-500/20 flex items-center gap-2">
                <HelpCircle className="w-4 h-4 text-indigo-400 shrink-0" />
                <span>Checkpoint: {item.checkpoint_question}</span>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
