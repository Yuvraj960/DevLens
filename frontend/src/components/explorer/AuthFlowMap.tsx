'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import type { AuthFlow } from '@/types/api';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ShieldCheck, Lock, ArrowDown, Key, CheckCircle2 } from 'lucide-react';

interface AuthFlowMapProps {
  repoId: string;
}

export const AuthFlowMap: React.FC<AuthFlowMapProps> = ({ repoId }) => {
  const [authFlow, setAuthFlow] = useState<AuthFlow | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAuth() {
      setLoading(true);
      try {
        const data = await api.getAuthFlow(repoId);
        setAuthFlow(data);
      } catch (err) {
        console.error('Failed to load auth flow:', err);
      } finally {
        setLoading(false);
      }
    }
    loadAuth();
  }, [repoId]);

  if (loading) {
    return <div className="py-12 text-center text-xs font-mono text-slate-500 animate-pulse">Mapping security pipeline and authentication guards...</div>;
  }

  if (!authFlow) {
    return <div className="py-12 text-center text-xs text-rose-400">Failed to load authentication flow.</div>;
  }

  return (
    <div className="space-y-6">
      {/* Strategy Summary Card */}
      <Card className="p-5 border-emerald-500/30 bg-slate-900/90 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-mono text-sm font-bold text-slate-100 uppercase">Auth Strategy: {authFlow.token_handling.type}</h3>
            <p className="text-xs text-slate-400 mt-0.5">Verification: {authFlow.token_handling.verification_method}</p>
          </div>
        </div>

        <Badge variant="success">Active Protection</Badge>
      </Card>

      {/* Step-by-Step Flow Pipeline */}
      <div className="space-y-3">
        <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono">Authentication Pipeline Steps</h4>
        <div className="space-y-3">
          {authFlow.steps.map((step, idx) => (
            <React.Fragment key={step.id}>
              <Card className="p-4 bg-slate-950/80 border-slate-800 space-y-2 hover:border-slate-700 transition-all">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 font-mono text-xs font-bold text-slate-100">
                    <span className="w-5 h-5 rounded bg-indigo-600/30 text-indigo-400 text-[10px] flex items-center justify-center">
                      {idx + 1}
                    </span>
                    {step.label}
                  </div>
                  <Badge variant="outline">{step.type}</Badge>
                </div>
                <p className="text-xs text-slate-400">{step.description}</p>
                <div className="text-[10px] font-mono text-slate-500">
                  Location: {step.file_path}:{step.line}
                </div>
              </Card>

              {idx < authFlow.steps.length - 1 && (
                <div className="flex justify-center my-1">
                  <ArrowDown className="w-4 h-4 text-slate-600" />
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
};
