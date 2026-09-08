import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { KeyRound, Copy, CheckCircle, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export function useCreator() {
  const { user } = useAuth();
  const [token, setToken] = useState<string | null>(localStorage.getItem('creator_token') || localStorage.getItem('auth_token'));
  
  useEffect(() => {
    const handleStorageChange = () => setToken(localStorage.getItem('creator_token') || localStorage.getItem('auth_token'));
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  return {
    token: token || (user ? 'user_authenticated' : null),
    isAuthenticated: !!token || !!user
  };
}

export function CreatorAuth() {
  const { isAuthenticated } = useCreator();
  const { user, openAuthModal } = useAuth();
  const [recoveryKey, setRecoveryKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);

  if (isAuthenticated && !recoveryKey) {
    return null;
  }

  const handleCreate = async () => {
    setLoading(true);
    try {
      const res = await api.createToken();
      localStorage.setItem('creator_token', res.token);
      setRecoveryKey(res.recovery_key);
      window.dispatchEvent(new Event('storage'));
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const copyKey = () => {
    if (recoveryKey) {
      navigator.clipboard.writeText(recoveryKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (recoveryKey) {
    return (
      <div className="bg-amber-50 border border-amber-200 p-4 rounded-xl mb-6">
        <h3 className="font-semibold text-amber-800 flex items-center gap-2 mb-2">
          <KeyRound size={18} /> Save Your Recovery Key
        </h3>
        <p className="text-sm text-amber-700 mb-3">
          This is the only time this key will be shown. Save it somewhere safe to recover your work on other devices.
        </p>
        <div className="flex items-center gap-2">
          <code className="bg-white px-3 py-2 rounded-lg border border-amber-200 text-amber-900 font-mono text-sm flex-1">
            {recoveryKey}
          </code>
          <button 
            onClick={copyKey}
            className="p-2 bg-amber-100 hover:bg-amber-200 text-amber-700 rounded-lg transition-colors"
          >
            {copied ? <CheckCircle size={18} /> : <Copy size={18} />}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200 shadow-sm p-6 rounded-xl flex flex-col items-center text-center">
      <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mb-4">
        <ShieldCheck size={24} />
      </div>
      <h3 className="text-lg font-semibold text-slate-800 mb-2">Institutional Research Account</h3>
      <p className="text-sm text-slate-500 mb-6 max-w-sm">
        Sign in or register to save your custom strategies, reports, and portfolio scenarios.
      </p>
      <div className="flex flex-col sm:flex-row items-center gap-3">
        <button
          onClick={() => openAuthModal('register')}
          className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg shadow-sm transition-all cursor-pointer"
        >
          Create Account
        </button>
        <button
          onClick={handleCreate}
          disabled={loading}
          className="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded-lg transition-all text-xs cursor-pointer"
        >
          {loading ? 'Generating...' : 'Continue Anonymously'}
        </button>
      </div>
    </div>
  );
}
