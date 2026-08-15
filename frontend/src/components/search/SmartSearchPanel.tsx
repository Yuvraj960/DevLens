'use client';

import React, { useState } from 'react';
import { api } from '@/lib/api';
import type { SmartSearchResultItem } from '@/types/api';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Search, Code2, Sparkles, Filter, FileCode } from 'lucide-react';

interface SmartSearchPanelProps {
  repoId: string;
}

export const SmartSearchPanel: React.FC<SmartSearchPanelProps> = ({ repoId }) => {
  const [dslQuery, setDslQuery] = useState('kind:function');
  const [results, setResults] = useState<SmartSearchResultItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  async function handleExecuteSearch(queryToRun?: string) {
    const q = queryToRun || dslQuery;
    if (!q.trim()) return;

    setLoading(true);
    setSearched(true);
    try {
      const res = await api.postSmartSearch(repoId, q);
      setResults(res.results);
    } catch (err) {
      console.error('Smart Search error:', err);
    } finally {
      setLoading(false);
    }
  }

  const suggestionChips = [
    'kind:function',
    'kind:class',
    'kind:interface',
    'import:express',
    'name:auth*',
    'loc>50',
  ];

  return (
    <div className="space-y-6">
      {/* Search Header & DSL Chips */}
      <Card className="p-5 space-y-4 bg-slate-900/90 border-slate-800">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-400" /> Structural Query Engine
          </h3>
          <span className="text-[10px] font-mono text-slate-500">Syntax: kind:, import:, name:, loc&gt;</span>
        </div>

        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
            <input
              type="text"
              value={dslQuery}
              onChange={(e) => setDslQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleExecuteSearch()}
              placeholder="e.g. kind:function import:express name:auth*"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2.5 text-xs text-slate-100 font-mono focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <Button onClick={() => handleExecuteSearch()} disabled={loading}>
            {loading ? 'Searching...' : 'Run Query'}
          </Button>
        </div>

        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-[10px] font-mono text-slate-500 mr-1">DSL Examples:</span>
          {suggestionChips.map((chip) => (
            <button
              key={chip}
              onClick={() => {
                setDslQuery(chip);
                handleExecuteSearch(chip);
              }}
              className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 hover:border-indigo-500 text-[11px] font-mono text-indigo-300 transition-all"
            >
              {chip}
            </button>
          ))}
        </div>
      </Card>

      {/* Results List */}
      {loading ? (
        <div className="py-12 text-center text-xs font-mono text-slate-500 animate-pulse">
          Parsing DSL AST query and searching repository...
        </div>
      ) : results.length > 0 ? (
        <div className="space-y-3">
          <div className="flex justify-between items-center text-xs font-mono text-slate-400">
            <span>Found {results.length} structural matches</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {results.map((res, i) => (
              <Card key={i} className="p-4 space-y-3 hover:border-slate-700 transition-all">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded bg-slate-950 border border-slate-800 text-indigo-400">
                      <Code2 className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="font-mono text-sm font-bold text-slate-100">{res.symbol.name}</h4>
                      <span className="text-[10px] font-mono text-slate-500">
                        {res.file_path}:{res.symbol.start_line}-{res.symbol.end_line}
                      </span>
                    </div>
                  </div>

                  <Badge variant="outline">{res.symbol.kind}</Badge>
                </div>

                <div className="p-2.5 rounded bg-slate-950/80 border border-slate-800 text-[11px] font-mono text-slate-300">
                  {res.context}
                </div>
              </Card>
            ))}
          </div>
        </div>
      ) : searched ? (
        <div className="py-12 text-center text-xs text-slate-500 border border-dashed border-slate-800 rounded-xl">
          No symbols found matching structural query `{dslQuery}`. Try another DSL filter.
        </div>
      ) : null}
    </div>
  );
};
