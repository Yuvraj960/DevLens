'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import type { FolderIntelligence } from '@/types/api';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Folder, FileCode, Sparkles, Star } from 'lucide-react';

interface FolderIntelTreeProps {
  repoId: string;
}

export const FolderIntelTree: React.FC<FolderIntelTreeProps> = ({ repoId }) => {
  const [folders, setFolders] = useState<FolderIntelligence[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadFolders() {
      setLoading(true);
      try {
        const data = await api.getFolders(repoId);
        setFolders(data);
      } catch (err) {
        console.error('Failed to load folder intelligence:', err);
      } finally {
        setLoading(false);
      }
    }
    loadFolders();
  }, [repoId]);

  if (loading) {
    return <div className="py-12 text-center text-xs font-mono text-slate-500 animate-pulse">Analyzing folder tree purpose and ranking key files...</div>;
  }

  if (folders.length === 0) {
    return <div className="py-12 text-center text-xs text-slate-500">No folder intelligence data found.</div>;
  }

  return (
    <div className="space-y-4">
      {folders.map((f) => (
        <Card key={f.path} className="p-5 space-y-3 hover:border-slate-700 transition-all">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
                <Folder className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-mono text-sm font-bold text-slate-100">{f.path}</h4>
                <p className="text-xs text-slate-400 mt-0.5">{f.purpose}</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Badge variant="outline">Complexity: {f.complexity}</Badge>
              <Badge variant="success">Test Cov: {Math.round(f.test_coverage * 100)}%</Badge>
            </div>
          </div>

          {f.key_files.length > 0 && (
            <div>
              <span className="text-[10px] font-mono uppercase text-slate-500 font-semibold block mb-2">Key Files (Centrality Ranked)</span>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                {f.key_files.map((kf) => (
                  <div key={kf.path} className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 text-xs space-y-1">
                    <div className="flex items-center gap-1.5 text-indigo-300 font-mono font-medium truncate">
                      <Star className="w-3 h-3 text-amber-400 fill-amber-400" />
                      <span className="truncate">{kf.path.split('/').pop()}</span>
                    </div>
                    <p className="text-[10px] text-slate-400 leading-tight">{kf.reason}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Card>
      ))}
    </div>
  );
};
