'use client';

import React, { useEffect, useState } from 'react';
import { Search, Code2, Box, Cpu, FileCode, Filter } from 'lucide-react';
import { api } from '@/lib/api';
import type { SymbolResponse } from '@/types/api';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';

interface SymbolBrowserProps {
  repoId: string;
}

export const SymbolBrowser: React.FC<SymbolBrowserProps> = ({ repoId }) => {
  const [symbols, setSymbols] = useState<SymbolResponse[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedKind, setSelectedKind] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadSymbols() {
      setLoading(true);
      try {
        const kindFilter = selectedKind === 'all' ? undefined : selectedKind;
        const res = await api.getSymbols(repoId, searchQuery || undefined, kindFilter);
        setSymbols(res);
      } catch (err) {
        console.error('Failed to load symbols:', err);
      } finally {
        setLoading(false);
      }
    }
    loadSymbols();
  }, [repoId, searchQuery, selectedKind]);

  const kindIcons: Record<string, React.ReactNode> = {
    function: <Cpu className="w-4 h-4 text-indigo-400" />,
    class: <Box className="w-4 h-4 text-purple-400" />,
    interface: <Code2 className="w-4 h-4 text-emerald-400" />,
    type: <FileCode className="w-4 h-4 text-amber-400" />,
    struct: <Box className="w-4 h-4 text-blue-400" />,
  };

  return (
    <div className="space-y-4">
      {/* Search & Kind Filters */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between bg-slate-900/90 p-3 rounded-xl border border-slate-800">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search symbols (e.g., UserService)..."
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-100 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono"
          />
        </div>

        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto">
          {['all', 'function', 'class', 'interface', 'type', 'struct'].map((kind) => (
            <button
              key={kind}
              onClick={() => setSelectedKind(kind)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-all ${
                selectedKind === kind
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {kind}
            </button>
          ))}
        </div>
      </div>

      {/* Symbol List */}
      {loading ? (
        <div className="py-12 text-center text-xs text-slate-500 font-mono animate-pulse">
          Parsing and querying AST symbols...
        </div>
      ) : symbols.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {symbols.map((sym) => (
            <Card key={sym.id} className="p-4 hover:border-slate-700 transition-all">
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-lg bg-slate-950 border border-slate-800">
                    {kindIcons[sym.kind] || <Code2 className="w-4 h-4 text-slate-400" />}
                  </div>
                  <div>
                    <h4 className="font-mono text-sm font-semibold text-slate-100">{sym.name}</h4>
                    <span className="text-[10px] text-slate-500 font-mono">
                      {sym.file_path}:{sym.start_line}-{sym.end_line}
                    </span>
                  </div>
                </div>
                <Badge variant="outline">{sym.kind}</Badge>
              </div>

              {sym.signature && (
                <div className="mt-3 p-2 rounded bg-slate-950/80 border border-slate-800 text-[11px] font-mono text-slate-300 truncate">
                  {sym.signature}
                </div>
              )}
            </Card>
          ))}
        </div>
      ) : (
        <div className="py-12 text-center text-xs text-slate-500 border border-dashed border-slate-800 rounded-xl">
          No AST symbols found matching query. Try adjusting filters or ingesting a repository.
        </div>
      )}
    </div>
  );
};
