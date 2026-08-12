'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { IngestForm } from '@/components/ingestion/IngestForm';
import { ProgressTracker } from '@/components/ingestion/ProgressTracker';
import { Sparkles, Terminal, Network, GitPullRequest } from 'lucide-react';

export default function LandingPage() {
  const router = useRouter();
  const [activeJob, setActiveJob] = useState<{ jobId: string; repoId: string } | null>(null);

  return (
    <div className="space-y-12 py-6">
      {/* Hero Header */}
      <div className="text-center space-y-4 max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-mono">
          <Sparkles className="w-3.5 h-3.5" /> Understand Any Codebase in Minutes
        </div>
        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-100">
          AI-Powered <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">Code Intelligence</span> Platform
        </h1>
        <p className="text-slate-400 text-base leading-relaxed">
          DevLens combines AST Tree-sitter parsing, hybrid vector retrieval, and LangGraph agent DAGs to auto-generate architecture diagrams, API maps, DB visualizers, and execution traces.
        </p>
      </div>

      {/* Feature Pills */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-4xl mx-auto">
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400">
            <Terminal className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-xs font-semibold text-slate-200">AST Symbol Indexing</h4>
            <p className="text-[11px] text-slate-400">Precise file & line grounded AST symbols</p>
          </div>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-purple-500/10 text-purple-400">
            <Network className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-xs font-semibold text-slate-200">Architecture Diagrams</h4>
            <p className="text-[11px] text-slate-400">Auto-layered React Flow visual maps</p>
          </div>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400">
            <GitPullRequest className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-xs font-semibold text-slate-200">Execution Traces</h4>
            <p className="text-[11px] text-slate-400">Cross-layer call path visualization</p>
          </div>
        </div>
      </div>

      {/* Main Action Section */}
      <div>
        {activeJob ? (
          <ProgressTracker
            jobId={activeJob.jobId}
            repoId={activeJob.repoId}
            onComplete={() => router.push(`/repos/${activeJob.repoId}`)}
          />
        ) : (
          <IngestForm
            onIngestStart={(jobId, repoId) => setActiveJob({ jobId, repoId })}
          />
        )}
      </div>
    </div>
  );
}
