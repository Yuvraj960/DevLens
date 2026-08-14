'use client';

import React, { useEffect, useState } from 'react';
import { Loader2, CheckCircle2, AlertCircle, Cpu } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface ProgressTrackerProps {
  jobId: string;
  repoId: string;
  onComplete: () => void;
}

export const ProgressTracker: React.FC<ProgressTrackerProps> = ({ jobId, repoId, onComplete }) => {
  const [stage, setStage] = useState('Initializing');
  const [progress, setProgress] = useState(10);
  const [message, setMessage] = useState('Connecting to WebSocket event stream...');
  const [status, setStatus] = useState<'IN_PROGRESS' | 'COMPLETE' | 'FAILED'>('IN_PROGRESS');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    let completed = false;

    // HTTP Polling fallback (runs every 1s)
    const interval = setInterval(async () => {
      if (completed) return;
      try {
        const res = await fetch(`http://localhost:8000/api/v1/jobs/${jobId}`);
        if (res.ok) {
          const data = await res.json();
          if (data.stage) setStage(data.stage);
          if (typeof data.progress === 'number') setProgress(data.progress);
          if (data.message) setMessage(data.message);

          if (data.status === 'COMPLETE' || data.progress === 100) {
            completed = true;
            setStatus('COMPLETE');
            setProgress(100);
            clearInterval(interval);
            setTimeout(onComplete, 1000);
          } else if (data.status === 'FAILED') {
            completed = true;
            setStatus('FAILED');
            setErrorMsg(data.message || 'Job failed');
            clearInterval(interval);
          }
        }
      } catch (err) {
        console.error('Job polling error:', err);
      }
    }, 1000);

    // WebSocket Stream
    const wsUrl = `ws://${window.location.hostname}:8000/ws/jobs/${jobId}`;
    let socket: WebSocket | null = null;

    try {
      socket = new WebSocket(wsUrl);

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.stage) setStage(data.stage);
          if (typeof data.progress === 'number') setProgress(data.progress);
          if (data.message) setMessage(data.message);
          if (data.status) setStatus(data.status);

          if ((data.status === 'COMPLETE' || data.progress === 100) && !completed) {
            completed = true;
            setStatus('COMPLETE');
            setProgress(100);
            clearInterval(interval);
            setTimeout(onComplete, 1000);
          } else if (data.status === 'FAILED' && !completed) {
            completed = true;
            setStatus('FAILED');
            setErrorMsg(data.message || 'Job failed');
            clearInterval(interval);
          }
        } catch (e) {
          console.error('Error parsing WebSocket message:', e);
        }
      };
    } catch (e) {
      console.error(e);
    }

    return () => {
      clearInterval(interval);
      if (socket) socket.close();
    };
  }, [jobId, onComplete]);

  return (
    <Card className="max-w-xl mx-auto border-slate-800 bg-slate-900/90 shadow-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20">
            <Cpu className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-100 text-sm">Ingestion Job Pipeline</h3>
            <p className="text-xs text-slate-400 font-mono mt-0.5">ID: {jobId.slice(0, 8)}</p>
          </div>
        </div>

        <Badge
          variant={
            status === 'COMPLETE' ? 'success' : status === 'FAILED' ? 'error' : 'default'
          }
        >
          {status === 'IN_PROGRESS' && <Loader2 className="w-3 h-3 animate-spin mr-1.5" />}
          {status}
        </Badge>
      </div>

      <div className="space-y-3">
        <div className="flex justify-between text-xs text-slate-300 font-medium">
          <span>{stage}</span>
          <span>{Math.round(progress)}%</span>
        </div>

        <Progress value={progress} className="h-2.5" />

        <p className="text-xs text-slate-400 font-mono bg-slate-950/80 p-3 rounded-lg border border-slate-800">
          {message}
        </p>

        {status === 'COMPLETE' && (
          <div className="flex items-center justify-between pt-2">
            <span className="text-xs text-emerald-400 flex items-center gap-1.5 font-medium">
              <CheckCircle2 className="w-4 h-4" /> Ready for browsing!
            </span>
            <Button size="sm" onClick={onComplete}>
              Open Dashboard
            </Button>
          </div>
        )}

        {status === 'FAILED' && (
          <div className="flex items-center gap-2 pt-2 text-xs text-rose-400">
            <AlertCircle className="w-4 h-4" /> {errorMsg || 'An error occurred during ingestion.'}
          </div>
        )}
      </div>
    </Card>
  );
};
