"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const [email, setEmail] = useState('analyst@muleshield.psb');
  const [password, setPassword] = useState('password');
  const [role, setRole] = useState('ANALYST');
  const [isLogin, setIsLogin] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // Check if already authenticated
    const auth = sessionStorage.getItem("muleshield_authenticated");
    if (auth === "true") {
      router.push('/dashboard');
    }
  }, [router]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      
      if (!res.ok) {
        setError(data.error || 'Authentication failed. Please check credentials.');
        setLoading(false);
        return;
      }

      sessionStorage.setItem("muleshield_authenticated", "true");
      sessionStorage.setItem("muleshield_user_email", data.email);
      sessionStorage.setItem("muleshield_user_role", data.role);
      sessionStorage.setItem("muleshield_token", data.token);
      
      setSuccess('Access granted. Initializing operations console...');
      setTimeout(() => {
        router.push('/dashboard');
      }, 1000);
    } catch (err) {
      console.error(err);
      setError('Connection Error: Unable to contact authentication services.');
      setLoading(false);
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, role })
      });
      const data = await res.json();
      
      if (!res.ok) {
        setError(data.error || 'Registration failed. Check format.');
        setLoading(false);
        return;
      }

      setSuccess('Registration successful! Please sign in using your new credentials.');
      setIsLogin(true);
      setPassword('');
      setLoading(false);
    } catch (err) {
      console.error(err);
      setError('Connection Error: Unable to contact registration services.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-6 relative overflow-hidden bg-weave">
      {/* Background radial effects */}
      <div className="absolute top-1/4 -left-20 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl" />
      <div className="absolute bottom-1/4 -right-20 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl" />

      <div className="bg-slate-800 border border-slate-700 w-full max-w-md p-8 rounded-2xl shadow-2xl space-y-6 z-10">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 bg-blue-600 rounded-2xl text-white flex items-center justify-center text-2xl mx-auto shadow-lg shadow-blue-600/30">
            <i className="fa-solid fa-shield-halved"></i>
          </div>
          <h1 className="text-2xl font-black text-white tracking-tight">MuleShield <span className="text-blue-500">PRO</span></h1>
          <p className="text-xs text-slate-400 font-medium">Enterprise Fraud Risk & Compliance Console</p>
        </div>

        {error && (
          <div className="p-3.5 bg-red-500/15 border border-red-500/30 rounded-xl text-xs text-red-400 font-medium flex items-center gap-2">
            <i className="fa-solid fa-circle-exclamation text-base"></i>
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="p-3.5 bg-emerald-500/15 border border-emerald-500/30 rounded-xl text-xs text-emerald-400 font-medium flex items-center gap-2 animate-pulse">
            <i className="fa-solid fa-circle-check text-base"></i>
            <span>{success}</span>
          </div>
        )}

        <div className="p-3.5 bg-slate-700/50 border border-slate-600 rounded-xl space-y-1 text-xs text-slate-300">
          <div className="font-bold flex items-center gap-1.5 text-blue-400">
            <i className="fa-solid fa-circle-info"></i> SECURE WORKSTATION ACCESS
          </div>
          <p className="text-[11px] leading-relaxed">
            MuleShield verification portal. Authenticate with corporate credentials or register a compliance officer ID.
          </p>
        </div>

        {isLogin ? (
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wide">Corporate Email / ID</label>
              <input
                type="text"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-slate-900 border border-slate-700 text-white rounded-xl px-4 py-3 text-xs focus:outline-none focus:border-blue-500 font-mono"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wide">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-slate-900 border border-slate-700 text-white rounded-xl px-4 py-3 text-xs focus:outline-none focus:border-blue-500 font-mono"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 transition font-bold py-3.5 rounded-xl text-xs text-white shadow-lg shadow-blue-600/20 disabled:opacity-50"
            >
              {loading ? 'Authenticating...' : 'Sign In to Workstation'}
            </button>
            <div className="text-center pt-2">
              <button
                type="button"
                onClick={() => setIsLogin(false)}
                className="text-xs font-semibold text-blue-400 hover:underline bg-transparent border-none cursor-pointer"
              >
                New Analyst? Register Workstation ID
              </button>
            </div>
          </form>
        ) : (
          <form onSubmit={handleSignup} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wide">Corporate Email / ID</label>
              <input
                type="text"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="e.g. officer@muleshield.psb"
                required
                className="w-full bg-slate-900 border border-slate-700 text-white rounded-xl px-4 py-3 text-xs focus:outline-none focus:border-blue-500 font-mono"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wide">Secure Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full bg-slate-900 border border-slate-700 text-white rounded-xl px-4 py-3 text-xs focus:outline-none focus:border-blue-500 font-mono"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wide">Officer Role</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 text-white rounded-xl px-4 py-3 text-xs focus:outline-none focus:border-blue-500 font-semibold"
              >
                <option value="ANALYST">Fraud Analyst (Default)</option>
                <option value="VIEWER">Compliance Viewer</option>
              </select>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-emerald-600 hover:bg-emerald-700 transition font-bold py-3.5 rounded-xl text-xs text-white shadow-lg shadow-emerald-600/20 disabled:opacity-50"
            >
              {loading ? 'Registering...' : 'Register Workstation ID'}
            </button>
            <div className="text-center pt-2">
              <button
                type="button"
                onClick={() => setIsLogin(true)}
                className="text-xs font-semibold text-blue-400 hover:underline bg-transparent border-none cursor-pointer"
              >
                Already have an ID? Sign In
              </button>
            </div>
          </form>
        )}

        <div className="text-center pt-2 border-t border-slate-700/40">
          <span className="text-[10px] font-mono text-slate-500">Security Standard: PMLA / FIU-IND Compliant Shell v2.0.0</span>
        </div>
      </div>
    </div>
  );
}
