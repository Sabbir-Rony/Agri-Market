import { useState, useEffect } from 'react';
import { AlertTriangle, RefreshCw, CheckCircle, Loader2 } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export default function ApiStatusBanner() {
  const [status, setStatus] = useState('checking');

  const check = async () => {
    setStatus('checking');
    try {
      const healthUrl = API_BASE.replace(/\/api\/?$/, '') + '/health';
      const res = await fetch(healthUrl, { signal: AbortSignal.timeout(15000) });
      if (res.ok) {
        setStatus('ok');
      } else {
        setStatus('error');
      }
    } catch {
      setStatus('error');
    }
  };

  useEffect(() => {
    // Skip health check on local dev — only meaningful in production
    const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    if (isLocal) { setStatus('ok'); return; }
    check();
  }, []);

  if (status === 'ok') return null;

  const isLocalMissing = API_BASE === '/api' && window.location.hostname !== 'localhost';

  return (
    <div className={`w-full px-4 py-3 text-sm font-medium flex items-center justify-between gap-4 ${
      status === 'checking' ? 'bg-yellow-50 text-yellow-800 border-b border-yellow-200' :
      'bg-red-50 text-red-800 border-b border-red-200'
    }`}>
      <div className="flex items-center gap-2">
        {status === 'checking' ? (
          <Loader2 className="w-4 h-4 animate-spin shrink-0" />
        ) : (
          <AlertTriangle className="w-4 h-4 shrink-0" />
        )}
        <span>
          {status === 'checking' && 'Connecting to server…'}
          {status === 'error' && isLocalMissing && (
            <>
              <strong>VITE_API_URL is not set.</strong>{' '}
              Go to Vercel → Project Settings → Environment Variables and add{' '}
              <code className="bg-red-100 px-1 rounded">VITE_API_URL</code>{' '}
              = your Render backend URL (e.g. https://preharvest-backend.onrender.com/api), then redeploy.
            </>
          )}
          {status === 'error' && !isLocalMissing && (
            <>
              <strong>Backend unreachable.</strong>{' '}
              The server may be starting up (Render free tier takes ~30s after sleep). Please wait and retry.
            </>
          )}
        </span>
      </div>
      {status === 'error' && (
        <button
          onClick={check}
          className="flex items-center gap-1 px-3 py-1 rounded border border-current hover:bg-red-100 whitespace-nowrap"
        >
          <RefreshCw className="w-3 h-3" />
          Retry
        </button>
      )}
    </div>
  );
}
