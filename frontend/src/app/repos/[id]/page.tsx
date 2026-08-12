'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import type { FileTreeNode, RepoResponse } from '@/types/api';
import { FileTree } from '@/components/repository/FileTree';
import { SymbolBrowser } from '@/components/repository/SymbolBrowser';
import { SummaryDashboard } from '@/components/analysis/SummaryDashboard';
import { ArchitectureCanvas } from '@/components/analysis/ArchitectureCanvas';
import { FolderIntelTree } from '@/components/analysis/FolderIntelTree';
import { ChatInterface } from '@/components/chat/ChatInterface';
import { SmartSearchPanel } from '@/components/search/SmartSearchPanel';
import { ApiExplorer } from '@/components/explorer/ApiExplorer';
import { DbVisualizer } from '@/components/explorer/DbVisualizer';
import { AuthFlowMap } from '@/components/explorer/AuthFlowMap';
import { FlagshipTraceCanvas } from '@/components/trace/FlagshipTraceCanvas';
import { CodeReviewPanel } from '@/components/gamechanger/CodeReviewPanel';
import { RefactoringSuggestions } from '@/components/gamechanger/RefactoringSuggestions';
import { CommitTimeline } from '@/components/gamechanger/CommitTimeline';
import { ArchitectureDiff } from '@/components/gamechanger/ArchitectureDiff';
import { OnboardingPath } from '@/components/gamechanger/OnboardingPath';
import { InteractiveDependencyGraph } from '@/components/gamechanger/InteractiveDependencyGraph';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  FolderTree,
  FileCode,
  Layers,
  MessageSquare,
  Search,
  Database,
  ShieldAlert,
  Activity,
  ArrowLeft,
  Sparkles,
  Network,
  Lock,
  Wrench,
  History,
  GitCompare,
  Compass,
  LayoutDashboard,
} from 'lucide-react';

type TabGroup = 'overview' | 'architecture' | 'db-api' | 'dev-suite' | 'trace' | 'search';

export default function RepoDashboardPage() {
  const params = useParams();
  const repoId = params.id as string;

  const [repo, setRepo] = useState<RepoResponse | null>(null);
  const [fileTree, setFileTree] = useState<FileTreeNode[]>([]);
  const [totalFiles, setTotalFiles] = useState(0);
  const [totalLoc, setTotalLoc] = useState(0);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Redesigned Tab Groups
  const [activeGroup, setActiveGroup] = useState<TabGroup>('overview');
  const [activeSubTab, setActiveSubTab] = useState<string>('summary');

  useEffect(() => {
    async function loadData() {
      try {
        const repoData = await api.getRepo(repoId);
        setRepo(repoData);

        const filesData = await api.getRepoFiles(repoId);
        setFileTree(filesData.file_tree);
        setTotalFiles(filesData.total_files);
        setTotalLoc(filesData.total_loc);
      } catch (err) {
        console.error('Failed to load repo:', err);
      } finally {
        setLoading(false);
      }
    }
    if (repoId) loadData();
  }, [repoId]);

  // Sync default sub-tab when active main group changes
  useEffect(() => {
    if (activeGroup === 'overview') setActiveSubTab('summary');
    else if (activeGroup === 'architecture') setActiveSubTab('diagram');
    else if (activeGroup === 'db-api') setActiveSubTab('api-explorer');
    else if (activeGroup === 'dev-suite') setActiveSubTab('code-review');
    else if (activeGroup === 'trace') setActiveSubTab('trace-flow');
    else if (activeGroup === 'search') setActiveSubTab('chat');
  }, [activeGroup]);

  if (loading) {
    return (
      <div className="py-20 text-center text-slate-400 text-sm font-mono animate-pulse">
        Loading DevLens repository dashboard...
      </div>
    );
  }

  if (!repo) {
    return (
      <div className="py-20 text-center text-rose-400 text-sm">
        Repository with ID <span className="font-mono">{repoId}</span> not found.
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Top Banner Navigation */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 bg-slate-950/40 p-6 rounded-2xl border border-slate-900 shadow-xl">
        <div className="space-y-2">
          <a href="/" className="inline-flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 font-mono transition-colors">
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Ingestion
          </a>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-3">
            {repo.name}
            <Badge variant="success" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">{repo.status}</Badge>
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Source: {repo.source_type} ({repo.source_url || 'local'}) &bull; Branch: {repo.default_branch}
          </p>
        </div>

        <div className="flex items-center gap-6 text-xs font-mono bg-slate-900/60 px-5 py-3.5 rounded-xl border border-slate-800/80">
          <div>
            <span className="text-slate-500 block text-[9px] uppercase tracking-wider font-bold">TOTAL FILES</span>
            <span className="text-slate-200 text-base font-bold">{totalFiles}</span>
          </div>
          <div className="w-px h-8 bg-slate-800" />
          <div>
            <span className="text-slate-500 block text-[9px] uppercase tracking-wider font-bold">TOTAL LOC</span>
            <span className="text-slate-200 text-base font-bold">{totalLoc.toLocaleString()}</span>
          </div>
        </div>
      </div>

      {/* Main Tab Groups Header (Minimalist & Grid wrapping, no horizontal scrollbar) */}
      <div className="bg-slate-950/80 p-1.5 rounded-xl border border-slate-900 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 w-full">
        {(
          [
            { id: 'overview', label: 'Dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
            { id: 'architecture', label: 'Architecture', icon: <Layers className="w-4 h-4" /> },
            { id: 'db-api', label: 'Database & API', icon: <Database className="w-4 h-4" /> },
            { id: 'dev-suite', label: 'Dev Suite', icon: <Wrench className="w-4 h-4" /> },
            { id: 'trace', label: 'Execution Trace', icon: <Activity className="w-4 h-4" /> },
            { id: 'search', label: 'RAG & Search', icon: <Search className="w-4 h-4" /> },
          ] as const
        ).map((group) => {
          const isActive = activeGroup === group.id;
          return (
            <button
              key={group.id}
              onClick={() => setActiveGroup(group.id)}
              className={`flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-mono text-xs font-bold transition-all ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/10'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              {group.icon}
              {group.label}
            </button>
          );
        })}
      </div>

      {/* Secondary Sub-Tabs Nav (Rendered dynamically if a group has multiple sub-components) */}
      <div className="flex flex-wrap gap-2.5 p-1 bg-slate-900/30 rounded-lg border border-slate-900/60 text-xs w-full">
        {activeGroup === 'overview' && (
          <>
            <button
              onClick={() => setActiveSubTab('summary')}
              className={`px-4 py-2 rounded-lg font-mono font-medium transition-all ${
                activeSubTab === 'summary' ? 'bg-slate-800 text-slate-100 font-bold' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 inline mr-1.5" /> AI Overview
            </button>
            <button
              onClick={() => setActiveSubTab('folders')}
              className={`px-4 py-2 rounded-lg font-mono font-medium transition-all ${
                activeSubTab === 'folders' ? 'bg-slate-800 text-slate-100 font-bold' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <FolderTree className="w-3.5 h-3.5 inline mr-1.5" /> Folder Intel
            </button>
            <button
              onClick={() => setActiveSubTab('timeline')}
              className={`px-4 py-2 rounded-lg font-mono font-medium transition-all ${
                activeSubTab === 'timeline' ? 'bg-slate-800 text-slate-100 font-bold' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <History className="w-3.5 h-3.5 inline mr-1.5" /> Commit Timeline
            </button>
          </>
        )}

        {activeGroup === 'architecture' && (
          <>
            <button
              onClick={() => setActiveSubTab('diagram')}
              className={`px-4 py-2 rounded-lg font-mono font-medium transition-all ${
                activeSubTab === 'diagram' ? 'bg-slate-800 text-slate-100 font-bold' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <Layers className="w-3.5 h-3.5 inline mr-1.5" /> System Topology
            </button>
            <button
              onClick={() => setActiveSubTab('dep-graph')}
              className={`px-4 py-2 rounded-lg font-mono font-medium transition-all ${
                activeSubTab === 'dep-graph' ? 'bg-slate-800 text-slate-100 font-bold' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <Network className="w-3.5 h-3.5 inline mr-1.5" /> Dependency Graph
            </button>
            <button
              onClick={() => setActiveSubTab('files')}
              className={`px-4 py-2 rounded-lg font-mono font-medium transition-all ${
                activeSubTab === 'files' ? 'bg-slate-800 text-slate-100 font-bold' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <FolderTree className="w-3.5 h-3.5 inline mr-1.5" /> File Tree
            </button>
          </>
        )}

        {activeGroup === 'db-api' && (
          <>
            <button
              onClick={() => setActiveSubTab('api-explorer')}
              className={`px-4 py-2 rounded-lg font-mono font-medium transition-all ${
                activeSubTab === 'api-explorer' ? 'bg-slate-800 text-slate-100 font-bold' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <Network className="w-3.5 h-3.5 inline mr-1.5" /> API Explorer
            </button>
            <button
              onClick={() => setActiveSubTab('database')}
              className={`px-4 py-2 rounded-lg font-mono font-medium transition-all ${
                activeSubTab === 'database' ? 'bg-slate-800 text-slate-100 font-bold' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <Database className="w-3.5 h-3.5 inline mr-1.5" /> DB Schema
            </button>
            <button
              onClick={() => setActiveSubTab('auth')}
              className={`px-4 py-2 rounded-lg font-mono font-medium transition-all ${
                activeSubTab === 'auth' ? 'bg-slate-800 text-slate-100 font-bold' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <Lock className="w-3.5 h-3.5 inline mr-1.5" /> Auth Strategy
            </button>
          </>
        )}

        {activeGroup === 'dev-suite' && (
          <>
            <button
              onClick={() => setActiveSubTab('code-review')}
              className={`px-4 py-2 rounded-lg font-mono font-medium transition-all ${
                activeSubTab === 'code-review' ? 'bg-slate-800 text-slate-100 font-bold' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <ShieldAlert className="w-3.5 h-3.5 inline mr-1.5" /> Code Review Agent
            </button>
            <button
              onClick={() => setActiveSubTab('refactor')}
              className={`px-4 py-2 rounded-lg font-mono font-medium transition-all ${
                activeSubTab === 'refactor' ? 'bg-slate-800 text-slate-100 font-bold' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <Wrench className="w-3.5 h-3.5 inline mr-1.5" /> AST Refactor
            </button>
            <button
              onClick={() => setActiveSubTab('onboarding')}
              className={`px-4 py-2 rounded-lg font-mono font-medium transition-all ${
                activeSubTab === 'onboarding' ? 'bg-slate-800 text-slate-100 font-bold' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <Compass className="w-3.5 h-3.5 inline mr-1.5" /> Developer Onboarding
            </button>
            <button
              onClick={() => setActiveSubTab('diff')}
              className={`px-4 py-2 rounded-lg font-mono font-medium transition-all ${
                activeSubTab === 'diff' ? 'bg-slate-800 text-slate-100 font-bold' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <GitCompare className="w-3.5 h-3.5 inline mr-1.5" /> Branch Diff
            </button>
          </>
        )}

        {activeGroup === 'trace' && (
          <span className="px-4 py-2 text-slate-400 font-mono text-xs">Visual Call graph trace viewer active</span>
        )}

        {activeGroup === 'search' && (
          <>
            <button
              onClick={() => setActiveSubTab('chat')}
              className={`px-4 py-2 rounded-lg font-mono font-medium transition-all ${
                activeSubTab === 'chat' ? 'bg-slate-800 text-slate-100 font-bold' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <MessageSquare className="w-3.5 h-3.5 inline mr-1.5" /> Grounded Chat
            </button>
            <button
              onClick={() => setActiveSubTab('search')}
              className={`px-4 py-2 rounded-lg font-mono font-medium transition-all ${
                activeSubTab === 'search' ? 'bg-slate-800 text-slate-100 font-bold' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <Search className="w-3.5 h-3.5 inline mr-1.5" /> Smart Search DSL
            </button>
            <button
              onClick={() => setActiveSubTab('symbols')}
              className={`px-4 py-2 rounded-lg font-mono font-medium transition-all ${
                activeSubTab === 'symbols' ? 'bg-slate-800 text-slate-100 font-bold' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <FileCode className="w-3.5 h-3.5 inline mr-1.5" /> AST Symbol Browser
            </button>
          </>
        )}
      </div>

      {/* Primary Tab Contents Container (Consolidated and highly spaced) */}
      <div className="bg-slate-950/40 p-6 rounded-2xl border border-slate-900 shadow-xl min-h-[500px]">
        {/* Overview Sub-tabs */}
        {activeGroup === 'overview' && activeSubTab === 'summary' && <SummaryDashboard repoId={repoId} />}
        {activeGroup === 'overview' && activeSubTab === 'folders' && <FolderIntelTree repoId={repoId} />}
        {activeGroup === 'overview' && activeSubTab === 'timeline' && <CommitTimeline repoId={repoId} />}

        {/* Architecture Sub-tabs */}
        {activeGroup === 'architecture' && activeSubTab === 'diagram' && <ArchitectureCanvas repoId={repoId} />}
        {activeGroup === 'architecture' && activeSubTab === 'dep-graph' && <InteractiveDependencyGraph repoId={repoId} />}
        {activeGroup === 'architecture' && activeSubTab === 'files' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 space-y-3">
              <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono">Repository Files</h3>
              <FileTree nodes={fileTree} onSelectFile={(path) => setSelectedFile(path)} />
            </div>

            <div className="lg:col-span-2">
              <Card className="h-full min-h-[400px] flex flex-col justify-center items-center text-center p-6 border-slate-900 bg-slate-950/60">
                {selectedFile ? (
                  <div className="text-left w-full space-y-4">
                    <div className="flex items-center gap-2 text-xs font-mono text-indigo-400 bg-indigo-500/10 p-2.5 rounded-lg border border-indigo-500/20">
                      <FileCode className="w-4 h-4" /> Path: {selectedFile}
                    </div>
                    <p className="text-xs text-slate-400 font-mono">
                      File content preview and AST Tree-sitter symbol viewer activated.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <FolderTree className="w-10 h-10 text-slate-700 mx-auto" />
                    <p className="text-xs text-slate-500 font-mono">Select a file from the repository tree to inspect details.</p>
                  </div>
                )}
              </Card>
            </div>
          </div>
        )}

        {/* Database & API Sub-tabs */}
        {activeGroup === 'db-api' && activeSubTab === 'api-explorer' && <ApiExplorer repoId={repoId} />}
        {activeGroup === 'db-api' && activeSubTab === 'database' && <DbVisualizer repoId={repoId} />}
        {activeGroup === 'db-api' && activeSubTab === 'auth' && <AuthFlowMap repoId={repoId} />}

        {/* Dev Suite Sub-tabs */}
        {activeGroup === 'dev-suite' && activeSubTab === 'code-review' && <CodeReviewPanel repoId={repoId} />}
        {activeGroup === 'dev-suite' && activeSubTab === 'refactor' && <RefactoringSuggestions repoId={repoId} />}
        {activeGroup === 'dev-suite' && activeSubTab === 'onboarding' && <OnboardingPath repoId={repoId} />}
        {activeGroup === 'dev-suite' && activeSubTab === 'diff' && <ArchitectureDiff repoId={repoId} />}

        {/* Trace Sub-tabs */}
        {activeGroup === 'trace' && <FlagshipTraceCanvas repoId={repoId} />}

        {/* Search Sub-tabs */}
        {activeGroup === 'search' && activeSubTab === 'chat' && <ChatInterface repoId={repoId} />}
        {activeGroup === 'search' && activeSubTab === 'search' && <SmartSearchPanel repoId={repoId} />}
        {activeGroup === 'search' && activeSubTab === 'symbols' && <SymbolBrowser repoId={repoId} />}
      </div>
    </div>
  );
}
