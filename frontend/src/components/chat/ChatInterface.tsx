'use client';

import React, { useState } from 'react';
import { api } from '@/lib/api';
import type { ChatResponse, Citation } from '@/types/api';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Send, Bot, User, Sparkles, FileCode, ExternalLink } from 'lucide-react';

interface ChatMessageItem {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  suggested_followups?: string[];
}

interface ChatInterfaceProps {
  repoId: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ repoId }) => {
  const [messages, setMessages] = useState<ChatMessageItem[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Hello! I am your DevLens Codebase Assistant. Ask me anything about this repository structure, modules, or implementation details.',
      suggested_followups: [
        'Where is user authentication handled?',
        'What are the primary entry points?',
        'How is database persistence structured?',
      ],
    },
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);

  async function handleSendMessage(queryText?: string) {
    const textToSend = queryText || inputQuery;
    if (!textToSend.trim() || loading) return;

    const userMsg: ChatMessageItem = {
      id: String(Date.now()),
      role: 'user',
      content: textToSend,
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!queryText) setInputQuery('');
    setLoading(true);

    try {
      const res: ChatResponse = await api.postChat(repoId, textToSend);

      const assistantMsg: ChatMessageItem = {
        id: String(Date.now() + 1),
        role: 'assistant',
        content: res.message,
        citations: res.citations,
        suggested_followups: res.suggested_followups,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: String(Date.now() + 2),
          role: 'assistant',
          content: 'Sorry, I encountered an error retrieving codebase context.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-[650px]">
      {/* Chat Conversation Stream */}
      <Card className="md:col-span-2 flex flex-col h-full overflow-hidden p-0 border-slate-800 bg-slate-950/90">
        {/* Stream Messages List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 text-xs leading-relaxed ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.role === 'assistant' && (
                <div className="w-7 h-7 rounded-lg bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400 shrink-0">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div
                className={`max-w-[85%] rounded-xl p-3.5 space-y-3 ${
                  msg.role === 'user'
                    ? 'bg-indigo-600 text-white font-sans'
                    : 'bg-slate-900 border border-slate-800 text-slate-200'
                }`}
              >
                <div className="whitespace-pre-wrap font-sans text-xs">{msg.content}</div>

                {/* Inline Citations List */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="pt-2 border-t border-slate-800/80 space-y-1">
                    <span className="text-[10px] font-mono uppercase text-slate-500 font-semibold block">Source Code Citations</span>
                    <div className="flex flex-wrap gap-1.5">
                      {msg.citations.map((cit, idx) => (
                        <button
                          key={idx}
                          onClick={() => setSelectedCitation(cit)}
                          className="inline-flex items-center gap-1 px-2 py-1 rounded bg-indigo-950/60 border border-indigo-500/30 text-[10px] font-mono text-indigo-300 hover:border-indigo-400 transition-all"
                        >
                          <FileCode className="w-3 h-3" />
                          {cit.file_path}:{cit.start_line}-{cit.end_line}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Suggested Follow-up Chips */}
                {msg.suggested_followups && msg.suggested_followups.length > 0 && (
                  <div className="pt-2 border-t border-slate-800/80 space-y-1.5">
                    <span className="text-[10px] font-mono uppercase text-slate-500 font-semibold flex items-center gap-1">
                      <Sparkles className="w-3 h-3 text-indigo-400" /> Suggested Follow-ups
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {msg.suggested_followups.map((sug, sIdx) => (
                        <button
                          key={sIdx}
                          onClick={() => handleSendMessage(sug)}
                          className="text-[11px] text-slate-300 bg-slate-950/80 border border-slate-800 hover:border-indigo-500 px-2.5 py-1 rounded-lg text-left transition-all"
                        >
                          {sug}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {msg.role === 'user' && (
                <div className="w-7 h-7 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-2 text-xs font-mono text-indigo-400 animate-pulse py-2">
              <Bot className="w-4 h-4" /> Grounding answer in codebase context...
            </div>
          )}
        </div>

        {/* Input Bar */}
        <div className="p-3 bg-slate-900/90 border-t border-slate-800 flex gap-2">
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Ask a question about this codebase..."
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-100 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-sans"
          />
          <Button onClick={() => handleSendMessage()} disabled={loading || !inputQuery.trim()}>
            <Send className="w-4 h-4 mr-1" /> Send
          </Button>
        </div>
      </Card>

      {/* Citation Snippet Inspector Drawer */}
      <Card className="md:col-span-1 p-4 space-y-3 h-full overflow-y-auto">
        <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <FileCode className="w-4 h-4 text-indigo-400" /> Source Citation Inspector
        </h3>
        {selectedCitation ? (
          <div className="space-y-3 text-xs">
            <div className="p-2.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 font-mono text-[11px] truncate">
              {selectedCitation.file_path}:{selectedCitation.start_line}-{selectedCitation.end_line}
            </div>
            <div>
              <span className="text-[10px] font-mono text-slate-500 uppercase block mb-1">Snippet Excerpt</span>
              <pre className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-[11px] font-mono text-slate-200 overflow-x-auto whitespace-pre-wrap">
                {selectedCitation.snippet}
              </pre>
            </div>
          </div>
        ) : (
          <div className="py-16 text-center text-xs text-slate-500">
            Click any source citation badge in assistant messages to inspect the exact line range and snippet.
          </div>
        )}
      </Card>
    </div>
  );
};
