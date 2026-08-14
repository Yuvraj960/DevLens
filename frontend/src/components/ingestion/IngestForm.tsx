'use client';

import React, { useState } from 'react';
import { Github, Folder, Archive, ArrowRight, Code } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle } from '@/components/ui/card';
import { api } from '@/lib/api';

interface IngestFormProps {
  onIngestStart: (jobId: string, repoId: string) => void;
}

export const IngestForm: React.FC<IngestFormProps> = ({ onIngestStart }) => {
  const [sourceType, setSourceType] = useState<'github' | 'zip' | 'folder'>('github');
  const [url, setUrl] = useState('https://github.com/vercel/next-learn');
  const [filePath, setFilePath] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await api.ingestRepo({
        source: sourceType,
        url: sourceType === 'github' ? url : undefined,
        file_path: sourceType !== 'github' ? filePath : undefined,
      });

      onIngestStart(res.job_id, res.repo_id);
    } catch (err: any) {
      setError(err.message || 'Failed to submit ingestion request');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="max-w-2xl mx-auto border-indigo-500/20 shadow-2xl shadow-indigo-950/40">
      <CardHeader className="text-center pb-2">
        <div className="mx-auto w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center mb-3">
          <Code className="w-6 h-6 text-indigo-400" />
        </div>
        <CardTitle className="text-2xl font-bold bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
          Ingest Codebase
        </CardTitle>
        <p className="text-slate-400 text-sm mt-1">
          Select a repository source to analyze codebase structure, files, and dependencies.
        </p>
      </CardHeader>

      <form onSubmit={handleSubmit} className="space-y-6 mt-4">
        {/* Source Selector Tabs */}
        <div className="grid grid-cols-3 gap-2 p-1 bg-slate-950/60 rounded-lg border border-slate-800">
          <button
            type="button"
            onClick={() => setSourceType('github')}
            className={`flex items-center justify-center gap-2 py-2.5 px-3 rounded-md text-xs font-medium transition-all ${
              sourceType === 'github'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/40'
            }`}
          >
            <Github className="w-4 h-4" />
            GitHub URL
          </button>
          <button
            type="button"
            onClick={() => setSourceType('folder')}
            className={`flex items-center justify-center gap-2 py-2.5 px-3 rounded-md text-xs font-medium transition-all ${
              sourceType === 'folder'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/40'
            }`}
          >
            <Folder className="w-4 h-4" />
            Local Folder
          </button>
          <button
            type="button"
            onClick={() => setSourceType('zip')}
            className={`flex items-center justify-center gap-2 py-2.5 px-3 rounded-md text-xs font-medium transition-all ${
              sourceType === 'zip'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/40'
            }`}
          >
            <Archive className="w-4 h-4" />
            ZIP Archive
          </button>
        </div>

        {/* Input Field */}
        <div>
          {sourceType === 'github' ? (
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-2">GitHub Repository URL</label>
              <input
                type="url"
                required
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://github.com/org/repo"
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500"
              />
            </div>
          ) : (
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-2">
                {sourceType === 'folder' ? 'Absolute Folder Path' : 'ZIP Archive Path'}
              </label>
              <input
                type="text"
                required
                value={filePath}
                onChange={(e) => setFilePath(e.target.value)}
                placeholder={sourceType === 'folder' ? 'C:/Projects/my-app' : 'C:/Downloads/repo.zip'}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500"
              />
            </div>
          )}
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
            {error}
          </div>
        )}

        <Button type="submit" disabled={loading} className="w-full py-3 gap-2">
          {loading ? 'Submitting...' : 'Analyze Repository'}
          <ArrowRight className="w-4 h-4" />
        </Button>
      </form>
    </Card>
  );
};
