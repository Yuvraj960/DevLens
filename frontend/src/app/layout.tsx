import type { Metadata } from 'next';
import './globals.css';
import { Layers, ShieldCheck, Code2 } from 'lucide-react';

export const metadata: Metadata = {
  title: 'DevLens — AI Code Intelligence Platform',
  description: 'Understand any codebase in minutes with AST parsing, architecture diagrams, and execution traces.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#090d16] text-slate-100 antialiased min-h-screen flex flex-col">
        {/* Navigation Header */}
        <header className="border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-md sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <a href="/" className="flex items-center gap-3 group">
              <div className="p-2 rounded-lg bg-indigo-600/20 border border-indigo-500/30 group-hover:border-indigo-500/60 transition-colors">
                <Code2 className="w-5 h-5 text-indigo-400" />
              </div>
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
                DevLens
              </span>
              <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                Phase 0 MVP
              </span>
            </a>

            <div className="flex items-center gap-4 text-xs font-medium text-slate-400">
              <a href="/docs" className="hover:text-slate-200 transition-colors flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5" /> Docs Mindmap
              </a>
              <a
                href="https://github.com"
                target="_blank"
                rel="noreferrer"
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all flex items-center gap-1.5"
              >
                <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" /> GitHub
              </a>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8">{children}</main>

        {/* Footer */}
        <footer className="border-t border-slate-800/60 py-6 text-center text-xs text-slate-500 font-mono">
          DevLens Code Intelligence Platform &copy; 2026 — Comprehension First Developer Tools
        </footer>
      </body>
    </html>
  );
}
