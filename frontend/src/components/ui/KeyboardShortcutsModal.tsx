'use client';

import React, { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Command, X, Search, Layers, MessageSquare, Activity } from 'lucide-react';

export const KeyboardShortcutsModal: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === '/') {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      }
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  if (!isOpen) return null;

  const shortcuts = [
    { key: 'Cmd / Ctrl + K', description: 'Open Smart Search DSL Panel', icon: <Search className="w-3.5 h-3.5 text-indigo-400" /> },
    { key: 'Cmd / Ctrl + /', description: 'Toggle Keyboard Shortcuts Modal', icon: <Command className="w-3.5 h-3.5 text-purple-400" /> },
    { key: 'Cmd / Ctrl + Enter', description: 'Submit Grounded RAG Chat Prompt', icon: <MessageSquare className="w-3.5 h-3.5 text-emerald-400" /> },
    { key: 'Esc', description: 'Close Active Modal / Side Drawer', icon: <X className="w-3.5 h-3.5 text-rose-400" /> },
  ];

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-6 space-y-4 border-slate-800 bg-slate-900 shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="font-mono text-sm font-bold text-slate-100 flex items-center gap-2">
            <Command className="w-4 h-4 text-indigo-400" /> DevLens Keyboard Navigation
          </h3>
          <button onClick={() => setIsOpen(false)} className="text-slate-400 hover:text-slate-200">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-2.5">
          {shortcuts.map((sc, i) => (
            <div key={i} className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono">
              <span className="flex items-center gap-2 text-slate-300">
                {sc.icon} {sc.description}
              </span>
              <Badge variant="outline">{sc.key}</Badge>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
