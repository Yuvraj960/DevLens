'use client';

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import type { DatabaseSchema, DbTable } from '@/types/api';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Database, Key, Table, ArrowRight, Layers } from 'lucide-react';

interface DbVisualizerProps {
  repoId: string;
}

export const DbVisualizer: React.FC<DbVisualizerProps> = ({ repoId }) => {
  const [schema, setSchema] = useState<DatabaseSchema | null>(null);
  const [selectedTable, setSelectedTable] = useState<DbTable | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDb() {
      setLoading(true);
      try {
        const data = await api.getDatabaseSchema(repoId);
        setSchema(data);
        if (data.tables.length > 0) setSelectedTable(data.tables[0]);
      } catch (err) {
        console.error('Failed to load DB schema:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDb();
  }, [repoId]);

  if (loading) {
    return <div className="py-12 text-center text-xs font-mono text-slate-500 animate-pulse">Parsing ORM database schemas and table relationships...</div>;
  }

  if (!schema) {
    return <div className="py-12 text-center text-xs text-rose-400">Failed to load database schema.</div>;
  }

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="p-4 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono text-slate-500 uppercase block">ORM Framework</span>
            <span className="text-lg font-bold text-indigo-400 uppercase font-mono">{schema.metadata.orm}</span>
          </div>
          <Database className="w-6 h-6 text-indigo-400" />
        </Card>

        <Card className="p-4 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono text-slate-500 uppercase block">Total Database Tables</span>
            <span className="text-xl font-bold text-slate-100">{schema.metadata.total_tables}</span>
          </div>
          <Table className="w-6 h-6 text-purple-400" />
        </Card>

        <Card className="p-4 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono text-slate-500 uppercase block">Total Schema Columns</span>
            <span className="text-xl font-bold text-slate-100">{schema.metadata.total_columns}</span>
          </div>
          <Layers className="w-6 h-6 text-emerald-400" />
        </Card>
      </div>

      {/* Tables Grid & Schema Inspector */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1 space-y-3">
          <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Database Tables</h3>
          <div className="space-y-2 max-h-[500px] overflow-y-auto">
            {schema.tables.map((t) => (
              <Card
                key={t.name}
                onClick={() => setSelectedTable(t)}
                className={`p-3 cursor-pointer transition-all ${
                  selectedTable?.name === t.name ? 'border-indigo-500 bg-slate-900' : 'hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-slate-100 flex items-center gap-2">
                    <Table className="w-3.5 h-3.5 text-indigo-400" /> {t.name}
                  </span>
                  <Badge variant="outline">{t.columns.length} Cols</Badge>
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Column Details Table */}
        <div className="md:col-span-2 space-y-4">
          {selectedTable ? (
            <Card className="p-6 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="font-mono text-base font-bold text-slate-100 flex items-center gap-2">
                  <Table className="w-5 h-5 text-indigo-400" /> {selectedTable.name} Table Columns
                </h3>
                <Badge variant="default">{selectedTable.source}</Badge>
              </div>

              <div className="border border-slate-800 rounded-xl overflow-hidden">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] border-b border-slate-800">
                    <tr>
                      <th className="p-3">Column Name</th>
                      <th className="p-3">Data Type</th>
                      <th className="p-3">Nullable</th>
                      <th className="p-3">Key Constraint</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 bg-slate-900/40">
                    {selectedTable.columns.map((col) => (
                      <tr key={col.name} className="hover:bg-slate-800/30 transition-all">
                        <td className="p-3 font-bold text-slate-200">{col.name}</td>
                        <td className="p-3 text-indigo-300">{col.type}</td>
                        <td className="p-3 text-slate-400">{col.nullable ? 'YES' : 'NO'}</td>
                        <td className="p-3">
                          {col.is_primary_key && (
                            <Badge variant="warning" className="text-[9px]">
                              <Key className="w-3 h-3 mr-1 inline" /> PRIMARY KEY
                            </Badge>
                          )}
                          {col.is_foreign_key && (
                            <Badge variant="outline" className="text-[9px]">
                              FOREIGN KEY
                            </Badge>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          ) : (
            <Card className="p-12 text-center text-xs text-slate-500">Select a table to inspect columns and keys.</Card>
          )}
        </div>
      </div>
    </div>
  );
};
