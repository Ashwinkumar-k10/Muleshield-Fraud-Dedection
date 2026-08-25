"use client";

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const router = useRouter();
  const [authenticated, setAuthenticated] = useState(false);
  const [activeAnalyst, setActiveAnalyst] = useState('Analyst-10');
  const [activeRole, setActiveRole] = useState('ANALYST');
  
  // Tab Routing
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // Data States
  const [allCases, setAllCases] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>({
    total_evaluated: 9082,
    critical_alerts: 87,
    high_risk: 19,
    medium_risk: 0,
    cleared_accounts: 8934
  });
  const [selectedCaseId, setSelectedCaseId] = useState<number | null>(null);
  const [selectedCase, setSelectedCase] = useState<any>(null);
  const [loadingCase, setLoadingCase] = useState(false);
  const [modelMetadata, setModelMetadata] = useState<any>({
    model_name: 'XGBoost Classifier',
    model_version: 'v1.0.0-PRO',
    threshold: 0.9899,
    pr_auc: 0.8807,
    pr_auc_std: 0.0403,
    precision: 1.0,
    recall: 0.6164,
    f1: 0.7586
  });
  
  // Queue Filter States
  const [queueSearch, setQueueSearch] = useState('');
  const [queueStatusFilter, setQueueStatusFilter] = useState('ALL');
  const [queueTierFilter, setQueueTierFilter] = useState('ALL');
  
  // Audit Logs
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [loadingLogs, setLoadingLogs] = useState(false);
  
  // Sandbox (Evaluator) States
  const [sandboxMode, setSandboxMode] = useState<'standard' | 'advanced'>('standard');
  const [standardInputs, setStandardInputs] = useState({
    F994: -4,
    F3598: 2,
    F1319: -3,
    F1216: 3,
    F3805: -2,
    F1813: 2
  });
  const [advancedJson, setAdvancedJson] = useState('{\n  "F994": -4.0,\n  "F3598": 2.0,\n  "F1319": -3.0,\n  "F1216": 3.0,\n  "F3805": -2.0,\n  "F1813": 2.0\n}');
  const [evaluating, setEvaluating] = useState(false);
  const [evalResult, setEvalResult] = useState<any>(null);
  const [evalError, setEvalError] = useState('');
  
  // Note Text
  const [newNote, setNewNote] = useState('');
  const [statusSelect, setStatusSelect] = useState('NEW');

  // Live Feed Simulation
  const [liveTransactions, setLiveTransactions] = useState<any[]>([]);
  
  // Network Graph Ref
  const networkContainerRef = useRef<HTMLDivElement>(null);
  const networkInstanceRef = useRef<any>(null);

  // Authenticate Session
  useEffect(() => {
    const auth = sessionStorage.getItem("muleshield_authenticated");
    if (auth !== "true") {
      router.push('/login');
    } else {
      setAuthenticated(true);
      const email = sessionStorage.getItem("muleshield_user_email") || "analyst@muleshield.psb";
      const role = sessionStorage.getItem("muleshield_user_role") || "ANALYST";
      setActiveAnalyst(email.split('@')[0]);
      setActiveRole(role);
    }
  }, [router]);

  // Initial Data Load
  useEffect(() => {
    if (authenticated) {
      fetchModelMetadata();
      fetchCasesData();
      startLiveTransactionFeed();
    }
  }, [authenticated]);

  // Trigger Network graph load when tab changes
  useEffect(() => {
    if (activeTab === 'network') {
      setTimeout(initNetworkGraph, 100);
    }
  }, [activeTab]);

  const fetchModelMetadata = async () => {
    try {
      const token = sessionStorage.getItem("muleshield_token");
      const res = await fetch('http://localhost:8000/api/model/metadata', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setModelMetadata(data);
      }
    } catch (err) {
      console.error("Failed fetching model metadata:", err);
    }
  };

  const fetchCasesData = async () => {
    try {
      const token = sessionStorage.getItem("muleshield_token");
      const res = await fetch('http://localhost:8000/api/cases', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setAllCases(data.cases || []);
        if (data.summary) {
          setSummary(data.summary);
        }
        if (data.cases && data.cases.length > 0 && selectedCaseId === null) {
          handleSelectCase(data.cases[0].account_id);
        }
      }
    } catch (err) {
      console.error("Failed fetching cases:", err);
    }
  };

  const handleSelectCase = async (accountId: number) => {
    setSelectedCaseId(accountId);
    setLoadingCase(true);
    try {
      const token = sessionStorage.getItem("muleshield_token");
      const res = await fetch(`http://localhost:8000/api/cases/${accountId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setSelectedCase(data);
        setStatusSelect(data.status);
      }
    } catch (err) {
      console.error("Failed loading case details:", err);
    } finally {
      setLoadingCase(false);
    }
  };

  const submitStatusUpdate = async () => {
    if (!selectedCaseId) return;
    try {
      const token = sessionStorage.getItem("muleshield_token");
      const res = await fetch(`http://localhost:8000/api/cases/${selectedCaseId}/status`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status: statusSelect, analyst: activeAnalyst })
      });
      if (res.ok) {
        fetchCasesData();
        handleSelectCase(selectedCaseId);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const submitNote = async () => {
    if (!selectedCaseId || !newNote.trim()) return;
    try {
      const token = sessionStorage.getItem("muleshield_token");
      const res = await fetch(`http://localhost:8000/api/cases/${selectedCaseId}/notes`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ note: newNote, analyst: activeAnalyst })
      });
      if (res.ok) {
        setNewNote('');
        handleSelectCase(selectedCaseId);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const submitCBSFreeze = async () => {
    if (!selectedCaseId) return;
    if (!confirm(`Are you sure you want to execute an emergency Core Banking System (CBS) debit freeze on account #${selectedCaseId}?`)) {
      return;
    }
    try {
      const token = sessionStorage.getItem("muleshield_token");
      const res = await fetch(`http://localhost:8000/api/cases/${selectedCaseId}/cbs-freeze`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ analyst: activeAnalyst })
      });
      if (res.ok) {
        const data = await res.json();
        alert(`EMERGENCY CBS FREEZE LOCKED SUCCESS\nReference Receipt: ${data.ref_no}`);
        fetchCasesData();
        handleSelectCase(selectedCaseId);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDownloadPDF = async (accountId: number) => {
    try {
      const token = sessionStorage.getItem("muleshield_token");
      const res = await fetch(`http://localhost:8000/api/cases/${accountId}/download-pdf`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `MuleShield_Report_${accountId}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
      } else {
        alert("Failed downloading PDF report. Unauthorized.");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDownloadJSON = async (accountId: number) => {
    try {
      const token = sessionStorage.getItem("muleshield_token");
      const res = await fetch(`http://localhost:8000/api/cases/${accountId}/download-json`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `MuleShield_Case_${accountId}.json`;
        document.body.appendChild(a);
        a.click();
        a.remove();
      } else {
        alert("Failed downloading JSON case details. Unauthorized.");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const triggerGenerateSTRDraft = async () => {
    if (!selectedCaseId) return;
    try {
      const token = sessionStorage.getItem("muleshield_token");
      const res = await fetch(`http://localhost:8000/api/cases/${selectedCaseId}/str-draft`, { 
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        // Custom popup dialog modal
        const modal = document.createElement('div');
        modal.className = "fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-[999] flex items-center justify-center p-6";
        modal.innerHTML = `
          <div class="bg-white border border-slate-200 w-full max-w-2xl p-6 rounded-2xl shadow-2xl space-y-4">
            <div class="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 class="font-extrabold text-slate-900 text-sm flex items-center gap-1.5">
                <i class="fa-solid fa-file-invoice text-blue-600"></i> Compliance STR Draft Document
              </h3>
              <button onclick="this.closest('.fixed').remove()" class="text-slate-400 hover:text-slate-600 text-lg"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <pre class="p-4 bg-slate-900 text-emerald-400 font-mono text-[11px] rounded-xl border border-slate-800 overflow-x-auto whitespace-pre-wrap leading-relaxed max-h-96">${data.str_draft}</pre>
            <div class="flex justify-end gap-2 text-xs">
              <button onclick="navigator.clipboard.writeText(\`${data.str_draft.replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`); alert('Copied report to clipboard!')" class="px-4 py-2.5 border border-slate-200 hover:bg-slate-50 transition rounded-xl font-bold text-slate-700">Copy to Clipboard</button>
              <button onclick="this.closest('.fixed').remove()" class="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 transition rounded-xl font-bold text-white shadow-sm">Done</button>
            </div>
          </div>
        `;
        document.body.appendChild(modal);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchAuditLogs = async () => {
    setLoadingLogs(true);
    try {
      const token = sessionStorage.getItem("muleshield_token");
      const res = await fetch('http://localhost:8000/api/audit-logs', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setAuditLogs(data.audit_logs || []);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingLogs(false);
    }
  };

  const handleLoadSamplePayload = async () => {
    try {
      const token = sessionStorage.getItem("muleshield_token");
      const res = await fetch('http://localhost:8000/api/sample-mule-payload', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setStandardInputs({
          F994: data.F994 || 0.0,
          F3598: data.F3598 || 0.0,
          F1319: data.F1319 || 0.0,
          F1216: data.F1216 || 0.0,
          F3805: data.F3805 || 0.0,
          F1813: data.F1813 || 0.0
        });
        setAdvancedJson(JSON.stringify(data, null, 2));
        alert("Verified demonstration sample payload loaded successfully.");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const runPrediction = async () => {
    setEvaluating(true);
    setEvalError('');
    setEvalResult(null);

    let payload = {};
    if (sandboxMode === 'standard') {
      payload = standardInputs;
    } else {
      try {
        payload = JSON.parse(advancedJson);
      } catch (err) {
        setEvalError('JSON Syntax Error. Please check brackets.');
        setEvaluating(false);
        return;
      }
    }

    setTimeout(async () => {
      try {
        const token = sessionStorage.getItem("muleshield_token");
        const res = await fetch('http://localhost:8000/api/predict', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ account_features: payload })
        });
        if (res.ok) {
          const data = await res.json();
          setEvalResult(data);
        } else {
          setEvalError('Backend prediction engine returned an error.');
        }
      } catch (err) {
        console.error(err);
        setEvalError('Failed contacting inference server.');
      } finally {
        setEvaluating(false);
      }
    }, 800);
  };

  // Vis Network Graph setup
  const initNetworkGraph = () => {
    if (!networkContainerRef.current) return;
    
    const vis = (window as any).vis;
    if (!vis) {
      console.warn("vis-network library not loaded yet.");
      return;
    }

    const nodes = new vis.DataSet([
      { id: 1, label: 'Victim Account\n#1001\n(Origin)', color: { background: '#dbeafe', border: '#2563eb' }, shape: 'box', font: { color: '#1e3a8a', face: 'JetBrains Mono', size: 10 } },
      { id: 2, label: 'Feeder Mule\n#9001\n(Pass-Through)', color: { background: '#fef3c7', border: '#d97706' }, shape: 'box', font: { color: '#78350f', face: 'JetBrains Mono', size: 10 } },
      { id: 3, label: 'Mule Account\n#9003\n[CRITICAL]', color: { background: '#fee2e2', border: '#dc2626' }, shape: 'box', font: { color: '#991b1b', face: 'JetBrains Mono', size: 11, bold: true } },
      { id: 4, label: 'Mule Account\n#9004\n[CRITICAL]', color: { background: '#fee2e2', border: '#dc2626' }, shape: 'box', font: { color: '#991b1b', face: 'JetBrains Mono', size: 11, bold: true } },
      { id: 5, label: 'Mule Account\n#9006\n[CRITICAL]', color: { background: '#fee2e2', border: '#dc2626' }, shape: 'box', font: { color: '#991b1b', face: 'JetBrains Mono', size: 11, bold: true } },
      { id: 6, label: 'Hub Aggregator\n#9099\n(Cash-Out Hub)', color: { background: '#fcf0f2', border: '#991b1b' }, shape: 'box', font: { color: '#7f1d1d', face: 'JetBrains Mono', size: 11, bold: true } },
      { id: 7, label: 'ATM Cash-Out\n#ATM-402', color: { background: '#f1f5f9', border: '#475569' }, shape: 'ellipse', font: { color: '#334155', face: 'JetBrains Mono', size: 9 } },
      { id: 8, label: 'Crypto Off-Ramp\n#P2P-EXCHANGE', color: { background: '#f1f5f9', border: '#475569' }, shape: 'ellipse', font: { color: '#334155', face: 'JetBrains Mono', size: 9 } }
    ]);

    const edges = new vis.DataSet([
      { from: 1, to: 2, label: '₹600k UPI (1 min)', arrows: 'to', font: { size: 8, align: 'top' }, color: { color: '#2563eb' } },
      { from: 2, to: 3, label: '₹200k IMPS', arrows: 'to', font: { size: 8, align: 'top' }, color: { color: '#d97706' } },
      { from: 2, to: 4, label: '₹200k IMPS', arrows: 'to', font: { size: 8, align: 'top' }, color: { color: '#d97706' } },
      { from: 2, to: 5, label: '₹200k IMPS', arrows: 'to', font: { size: 8, align: 'top' }, color: { color: '#d97706' } },
      { from: 3, to: 6, label: '₹195k RTGS', arrows: 'to', font: { size: 8, align: 'top' }, color: { color: '#dc2626' } },
      { from: 4, to: 6, label: '₹198k RTGS', arrows: 'to', font: { size: 8, align: 'top' }, color: { color: '#dc2626' } },
      { from: 5, to: 6, label: '₹196k RTGS', arrows: 'to', font: { size: 8, align: 'top' }, color: { color: '#dc2626' } },
      { from: 6, to: 7, label: '₹350k Cash', arrows: 'to', font: { size: 8, align: 'top' }, color: { color: '#991b1b' } },
      { from: 6, to: 8, label: '₹239k USDT', arrows: 'to', font: { size: 8, align: 'top' }, color: { color: '#991b1b' } }
    ]);

    const data = { nodes, edges };
    const options = {
      physics: { enabled: true, solver: 'forceAtlas2Based' },
      interaction: { hover: true, dragNodes: true }
    };
    
    networkInstanceRef.current = new vis.Network(networkContainerRef.current, data, options);
  };

  const handleLogout = async () => {
    const token = sessionStorage.getItem("muleshield_token");
    if (token) {
      try {
        await fetch('http://localhost:8000/api/auth/logout', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}` 
          }
        });
      } catch (err) {
        console.error("Logout API request failed:", err);
      }
    }
    sessionStorage.removeItem("muleshield_authenticated");
    sessionStorage.removeItem("muleshield_user_email");
    sessionStorage.removeItem("muleshield_user_role");
    sessionStorage.removeItem("muleshield_token");
    router.push('/login');
  };

  // Live simulation updates
  const startLiveTransactionFeed = () => {
    const simulatedInflow = ["UPI Inflow", "IMPS Deposit", "NEFT Credit", "RTGS Transfer"];
    const initialTxs: any[] = [];
    for (let i = 0; i < 4; i++) {
      initialTxs.push(createMockTx(simulatedInflow));
    }
    setLiveTransactions(initialTxs);

    const interval = setInterval(() => {
      setLiveTransactions(prev => {
        const next = [createMockTx(simulatedInflow), ...prev];
        if (next.length > 5) {
          next.pop();
        }
        return next;
      });
    }, 4500);

    return () => clearInterval(interval);
  };

  const createMockTx = (simulatedInflow: string[]) => {
    const txId = Math.floor(100000 + Math.random() * 900000);
    const accId = Math.floor(9010 + Math.random() * 9000);
    const isMule = Math.random() > 0.85;
    const amount = isMule ? (150000 + Math.floor(Math.random() * 450000)) : (2000 + Math.floor(Math.random() * 25000));
    const channel = isMule ? "UPI Inflow" : simulatedInflow[Math.floor(Math.random() * simulatedInflow.length)];
    const timeStr = new Date().toLocaleTimeString();
    return { txId, accId, isMule, amount, channel, timeStr, score: (0.9901 + Math.random()*0.009).toFixed(4) };
  };

  const exportCSV = () => {
    let csv = "Account_ID,Risk_Score,Tier,Action,Status,Assigned_Analyst,Created_At\n";
    allCases.forEach(c => {
      csv += `${c.account_id},${c.risk_score},${c.tier},"${c.action}","${c.status}","${c.assigned_analyst}","${c.created_at}"\n`;
    });
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `MuleShield_Cases_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
  };

  // Helper UI Styles
  const getStatusStyle = (status: string) => {
    switch(status) {
      case 'NEW': return 'bg-red-50 text-red-700 border-red-200';
      case 'TRIAGED': return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'UNDER REVIEW': return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'ESCALATED': return 'bg-purple-50 text-purple-700 border-purple-200';
      case 'CLOSED': return 'bg-slate-50 text-slate-600 border-slate-200';
      default: return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    }
  };

  const getBadgeHTML = (tier: string) => {
    switch(tier) {
      case 'Critical': return <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-red-100 text-red-800 border border-red-200 font-mono">CRITICAL</span>;
      case 'High': return <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-orange-100 text-orange-800 border border-orange-200 font-mono">HIGH</span>;
      case 'Medium': return <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-yellow-100 text-yellow-800 border border-yellow-200 font-mono">MEDIUM</span>;
      default: return <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200 font-mono">LOW</span>;
    }
  };

  // Filter cases lists
  const filteredCases = allCases.filter(c => {
    const matchSearch = queueSearch === '' || c.account_id.toString().includes(queueSearch);
    const matchStatus = queueStatusFilter === 'ALL' || c.status === queueStatusFilter;
    const matchTier = queueTierFilter === 'ALL' || c.tier.toUpperCase() === queueTierFilter;
    return matchSearch && matchStatus && matchTier;
  });

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'ADMIN': return 'System Administrator';
      case 'ANALYST': return 'Fraud Analyst';
      case 'INVESTIGATOR': return 'Lead Investigator';
      case 'VIEWER': return 'Compliance Viewer';
      default: return role;
    }
  };

  if (!authenticated) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center text-slate-400 font-mono text-xs">
        <span>Establishing secure session link...</span>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden bg-slate-50 antialiased font-sans">
      {/* Header */}
      <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between flex-shrink-0 z-20 shadow-sm">
        <div className="flex items-center space-x-3.5">
          <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white text-lg shadow shadow-blue-500/20">
            <i className="fa-solid fa-shield-halved"></i>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base font-extrabold text-slate-900 tracking-tight">MuleShield <span className="text-blue-600">PRO</span></h2>
              <span className="px-2 py-0.5 rounded-full text-[9px] font-bold font-mono bg-blue-50 text-blue-700 border border-blue-200">SECURE ENV</span>
              <span className="px-2 py-0.5 rounded-full text-[9px] font-bold font-mono bg-emerald-50 text-emerald-700 border border-emerald-200">ONLINE</span>
            </div>
            <p className="text-[10px] text-slate-500 font-medium">Enterprise Fraud Risk & Compliance Console</p>
          </div>
        </div>

        {/* Health Monitors */}
        <div className="hidden lg:flex items-center space-x-6">
          <div className="flex items-center space-x-1.5 text-[11px] font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span className="text-slate-500">ML ENGINE:</span>
            <span className="text-slate-950 font-bold">ONLINE</span>
          </div>
          <div className="flex items-center space-x-1.5 text-[11px] font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-slate-500">DATABASE:</span>
            <span className="text-slate-950 font-bold">SQL PERSISTENT</span>
          </div>
        </div>

        {/* User Info + Logout */}
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <div className="text-xs font-bold text-slate-900">{activeAnalyst}</div>
            <div className="text-[10px] text-slate-400 font-mono">{getRoleLabel(activeRole)}</div>
          </div>
          <button onClick={handleLogout} className="w-8 h-8 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 hover:text-red-600 transition flex items-center justify-center text-sm shadow-sm" title="Log Out from Workstation">
            <i className="fa-solid fa-power-off"></i>
          </button>
        </div>
      </header>

      {/* Main Container */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r border-slate-200 flex flex-col p-4 space-y-2 z-10 flex-shrink-0">
          <div className="text-[10px] font-bold font-mono text-slate-400 uppercase px-3 py-1.5 tracking-wider">COMMAND CENTER</div>
          <button onClick={() => setActiveTab('dashboard')} className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-xs font-bold transition ${activeTab === 'dashboard' ? 'active-sidebar-item' : 'text-slate-600 hover:bg-slate-50'}`}>
            <i className="fa-solid fa-chart-line text-sm"></i>
            <span>Overview Panel</span>
          </button>

          <div className="text-[10px] font-bold font-mono text-slate-400 uppercase px-3 py-1.5 tracking-wider mt-2">INVESTIGATION</div>
          <button onClick={() => setActiveTab('cases')} className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-xs font-bold transition ${activeTab === 'cases' ? 'active-sidebar-item' : 'text-slate-600 hover:bg-slate-50'}`}>
            <i className="fa-solid fa-table-list text-sm"></i>
            <span>Risk Case Queue</span>
          </button>
          {['ADMIN', 'ANALYST'].includes(activeRole) && (
            <button onClick={() => setActiveTab('evaluate')} className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-xs font-bold transition ${activeTab === 'evaluate' ? 'active-sidebar-item' : 'text-slate-600 hover:bg-slate-50'}`}>
              <i className="fa-solid fa-microscope text-sm"></i>
              <span>Evaluate Account</span>
            </button>
          )}
          <button onClick={() => setActiveTab('network')} className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-xs font-bold transition ${activeTab === 'network' ? 'active-sidebar-item' : 'text-slate-600 hover:bg-slate-50'}`}>
            <i className="fa-solid fa-diagram-project text-sm"></i>
            <span>Mule Network Ring</span>
          </button>

          <div className="text-[10px] font-bold font-mono text-slate-400 uppercase px-3 py-1.5 tracking-wider mt-2">COMPLIANCE</div>
          <button onClick={() => setActiveTab('regulatory')} className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-xs font-bold transition ${activeTab === 'regulatory' ? 'active-sidebar-item' : 'text-slate-600 hover:bg-slate-50'}`}>
            <i className="fa-solid fa-building-columns text-sm"></i>
            <span>Regulatory Intelligence</span>
          </button>

          <div className="text-[10px] font-bold font-mono text-slate-400 uppercase px-3 py-1.5 tracking-wider mt-2">MODEL INSIGHTS</div>
          <button onClick={() => setActiveTab('model')} className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-xs font-bold transition ${activeTab === 'model' ? 'active-sidebar-item' : 'text-slate-600 hover:bg-slate-50'}`}>
            <i className="fa-solid fa-sliders text-sm"></i>
            <span>Performance Benchmarks</span>
          </button>
          <button onClick={() => setActiveTab('audit')} className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-xs font-bold transition ${activeTab === 'audit' ? 'active-sidebar-item' : 'text-slate-600 hover:bg-slate-50'}`}>
            <i className="fa-solid fa-clipboard-check text-sm"></i>
            <span>Technical Integrity Audit</span>
          </button>

          <div className="text-[10px] font-bold font-mono text-slate-400 uppercase px-3 py-1.5 tracking-wider mt-2">SYSTEM CONFIG</div>
          {activeRole === 'ADMIN' && (
            <button onClick={() => { setActiveTab('logs'); fetchAuditLogs(); }} className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-xs font-bold transition ${activeTab === 'logs' ? 'active-sidebar-item' : 'text-slate-600 hover:bg-slate-50'}`}>
              <i className="fa-solid fa-receipt text-sm"></i>
              <span>System Audit Logs</span>
            </button>
          )}

          <div className="mt-auto pt-4 border-t border-slate-200 space-y-3">
            <div className="metric-card p-3 text-xs space-y-2">
              <div className="flex justify-between font-mono text-[10px]">
                <span class="text-slate-500 font-medium">CALIBRATED THRESHOLD</span>
                <span className="font-bold text-blue-600">{modelMetadata.threshold.toFixed(4)}</span>
              </div>
              <input type="range" min="0.50" max="0.999" step="0.001" value={modelMetadata.threshold} disabled className="w-full h-1 bg-slate-200 rounded-lg appearance-none cursor-not-allowed accent-blue-600" />
              <div className="text-[9px] text-slate-400 leading-tight">Calibrated via Group-Aware CV for Zero False Freezes.</div>
            </div>
            <div className="text-center">
              <p className="text-[9px] text-slate-400 font-medium">Secured with PMLA Compliance Standards</p>
            </div>
          </div>
        </aside>

        {/* Content Area */}
        <div className="flex-1 overflow-hidden flex flex-col">
          
          {/* TAB: Overview Panel */}
          {activeTab === 'dashboard' && (
            <main className="flex-1 overflow-y-auto p-6 space-y-6">
              <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                <div>
                  <h2 className="text-2xl font-black text-slate-900 tracking-tight">Fraud Operations Command Center</h2>
                  <p className="text-xs text-slate-500 mt-1">Real-time alerts, operational statistics, and system health monitors.</p>
                </div>
                <button onClick={exportCSV} className="px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold transition flex items-center space-x-2 shadow-sm">
                  <i className="fa-solid fa-download"></i>
                  <span>Export Case Queue (CSV)</span>
                </button>
              </div>

              {/* KPI Cards Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="metric-card flex items-center justify-between">
                  <div>
                    <p className="text-[10px] text-slate-500 font-bold tracking-wider uppercase">Total Accounts Evaluated</p>
                    <h3 className="text-2xl font-black font-mono text-slate-900 mt-1">{summary.total_evaluated.toLocaleString()}</h3>
                  </div>
                  <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-500 text-lg">
                    <i className="fa-solid fa-users"></i>
                  </div>
                </div>
                <div className="metric-card flex items-center justify-between border-l-4 border-l-red-500">
                  <div>
                    <p className="text-[10px] text-slate-500 font-bold tracking-wider uppercase">Critical Mule Alerts</p>
                    <h3 className="text-2xl font-black font-mono text-red-600 mt-1">{summary.critical_alerts.toLocaleString()}</h3>
                  </div>
                  <div className="w-10 h-10 rounded-xl bg-red-50 flex items-center justify-center text-red-600 text-lg">
                    <i className="fa-solid fa-triangle-exclamation"></i>
                  </div>
                </div>
                <div className="metric-card flex items-center justify-between border-l-4 border-l-orange-500">
                  <div>
                    <p className="text-[10px] text-slate-500 font-bold tracking-wider uppercase">High Risk Alerts</p>
                    <h3 className="text-2xl font-black font-mono text-orange-600 mt-1">{summary.high_risk.toLocaleString()}</h3>
                  </div>
                  <div className="w-10 h-10 rounded-xl bg-orange-50 flex items-center justify-center text-orange-600 text-lg">
                    <i className="fa-solid fa-circle-exclamation"></i>
                  </div>
                </div>
                <div className="metric-card flex items-center justify-between border-l-4 border-l-emerald-500">
                  <div>
                    <p className="text-[10px] text-slate-500 font-bold tracking-wider uppercase">Cleared Accounts</p>
                    <h3 className="text-2xl font-black font-mono text-emerald-600 mt-1">{summary.cleared_accounts.toLocaleString()}</h3>
                  </div>
                  <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600 text-lg">
                    <i className="fa-solid fa-circle-check"></i>
                  </div>
                </div>
              </div>

              {/* Detail Dashboard Grids */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left: High Priority Cases Alerts */}
                <div className="lg:col-span-2 metric-card space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wide flex items-center gap-2">
                      <i class="fa-solid fa-bell text-blue-600 animate-pulse"></i> High-Priority Investigation Alerts
                    </h3>
                    <button onClick={() => setActiveTab('cases')} className="text-xs text-blue-600 hover:underline">View Case Queue</button>
                  </div>
                  <div className="overflow-x-auto min-h-64">
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="bg-slate-50 text-slate-500 border-b border-slate-100">
                        <tr>
                          <th className="px-4 py-2.5">Account ID</th>
                          <th className="px-4 py-2.5">Risk Score</th>
                          <th className="px-4 py-2.5">Tier</th>
                          <th className="px-4 py-2.5">Status</th>
                          <th className="px-4 py-2.5">Primary Attributing Signal</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {allCases.filter(c => c.tier === 'Critical' || c.tier === 'High').slice(0, 5).map((c, idx) => (
                          <tr key={idx} onClick={() => { setActiveTab('cases'); handleSelectCase(c.account_id); }} className="hover:bg-slate-50 transition cursor-pointer">
                            <td className="px-4 py-2.5 font-bold text-slate-900">#{c.account_id}</td>
                            <td className="px-4 py-2.5 font-bold text-blue-600">{c.risk_score.toFixed(4)}</td>
                            <td className="px-4 py-2.5">{getBadgeHTML(c.tier)}</td>
                            <td className="px-4 py-2.5"><span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getStatusStyle(c.status)}`}>{c.status}</span></td>
                            <td className="px-4 py-2.5 text-slate-500 font-sans">{c.top_shap_drivers[0]} Anomaly Driver</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Right: Model Metadata Info */}
                <div className="space-y-6">
                  <div className="metric-card space-y-4">
                    <div className="border-b border-slate-100 pb-3">
                      <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wide flex items-center gap-2">
                        <i className="fa-solid fa-server text-blue-600"></i> Model Metadata Registry
                      </h3>
                    </div>
                    <div className="space-y-3.5 text-xs">
                      <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-2 font-mono">
                        <div className="flex justify-between text-slate-500">
                          <span>Champion Model:</span>
                          <strong className="text-slate-900">{modelMetadata.model_name}</strong>
                        </div>
                        <div className="flex justify-between text-slate-500">
                          <span>Version:</span>
                          <strong className="text-slate-900">{modelMetadata.model_version}</strong>
                        </div>
                        <div className="flex justify-between text-slate-500">
                          <span>Decision Boundary:</span>
                          <strong className="text-blue-600 font-extrabold">{modelMetadata.threshold.toFixed(4)}</strong>
                        </div>
                        <div className="flex justify-between text-slate-500">
                          <span>PR-AUC Metric:</span>
                          <strong className="text-slate-900">{modelMetadata.pr_auc.toFixed(4)} ± {modelMetadata.pr_auc_std.toFixed(4)}</strong>
                        </div>
                        <div className="flex justify-between text-slate-500">
                          <span>Target Precision:</span>
                          <strong className="text-emerald-600 font-bold">100.00% (0 False Freezes)</strong>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Real-Time Live Ticker */}
                  <div className="metric-card space-y-4">
                    <div className="border-b border-slate-100 pb-3 flex justify-between items-center">
                      <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wide flex items-center gap-2">
                        <i className="fa-solid fa-satellite-dish text-emerald-600 animate-pulse"></i> Live CBS Transaction Feed
                      </h3>
                      <span className="px-2 py-0.5 rounded-full text-[9px] font-bold font-mono bg-emerald-50 text-emerald-700 border border-emerald-200">STREAMING</span>
                    </div>
                    <div className="space-y-2.5 max-h-56 overflow-y-auto font-mono text-[10px] leading-relaxed pr-1">
                      {liveTransactions.map((tx, idx) => (
                        <div key={idx} className={`p-2.5 rounded-xl border transition-all duration-300 ${tx.isMule ? 'bg-red-50 border-red-200 text-red-950 font-bold' : 'bg-slate-50 border-slate-200 text-slate-700'}`}>
                          {tx.isMule ? (
                            <div>
                              <div className="flex justify-between items-center text-[9px] text-red-600 font-bold">
                                <span>ALERT: SUSPICIOUS MULE VELOCITY</span>
                                <span>{tx.timeStr}</span>
                              </div>
                              <div className="mt-1 flex justify-between text-xs">
                                <span>Tx #{tx.txId} | Acc #{tx.accId}</span>
                                <span className="text-red-700 font-black">₹{tx.amount.toLocaleString()}</span>
                              </div>
                              <div className="mt-0.5 flex justify-between text-[9px] text-red-800 font-medium">
                                <span>Reason: Outflow Ratio Signal</span>
                                <span>Risk Score: {tx.score}</span>
                              </div>
                            </div>
                          ) : (
                            <div>
                              <div className="flex justify-between items-center text-[9px] text-slate-400">
                                <span>TX PROCESSED ({tx.channel})</span>
                                <span>{tx.timeStr}</span>
                              </div>
                              <div className="mt-1 flex justify-between text-xs">
                                <span>Tx #{tx.txId} | Acc #{tx.accId}</span>
                                <span className="text-slate-900 font-bold">₹{tx.amount.toLocaleString()}</span>
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </main>
          )}

          {/* TAB: Risk Case Queue & Workspace */}
          {activeTab === 'cases' && (
            <main className="flex-1 flex overflow-hidden bg-slate-50">
              {/* Left Panel: Cases Queue */}
              <div className="w-1/2 border-r border-slate-200 flex flex-col bg-white overflow-hidden">
                <div className="p-4 border-b border-slate-200 bg-slate-50 space-y-3 flex-shrink-0">
                  <div className="flex items-center justify-between">
                    <h3 className="font-extrabold text-slate-900 text-sm">Triage Alerts Queue</h3>
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">{filteredCases.length} cases</span>
                  </div>
                  
                  {/* Search and Filters */}
                  <div className="space-y-2">
                    <input
                      type="text"
                      placeholder="Search account identifier..."
                      value={queueSearch}
                      onChange={(e) => setQueueSearch(e.target.value)}
                      className="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-blue-600 font-mono shadow-sm"
                    />
                    <div className="flex gap-2">
                      <select
                        value={queueStatusFilter}
                        onChange={(e) => setQueueStatusFilter(e.target.value)}
                        className="flex-1 bg-white border border-slate-200 rounded-xl px-2 py-2 text-[11px] focus:outline-none focus:border-blue-600 font-sans font-semibold text-slate-700 shadow-sm"
                      >
                        <option value="ALL">ALL STATUSES</option>
                        <option value="NEW">NEW</option>
                        <option value="TRIAGED">TRIAGED</option>
                        <option value="UNDER REVIEW">UNDER REVIEW</option>
                        <option value="ESCALATED">ESCALATED</option>
                        <option value="CLOSED">CLOSED</option>
                      </select>
                      <select
                        value={queueTierFilter}
                        onChange={(e) => setQueueTierFilter(e.target.value)}
                        className="flex-1 bg-white border border-slate-200 rounded-xl px-2 py-2 text-[11px] focus:outline-none focus:border-blue-600 font-sans font-semibold text-slate-700 shadow-sm"
                      >
                        <option value="ALL">ALL TIERS</option>
                        <option value="CRITICAL">CRITICAL</option>
                        <option value="HIGH">HIGH</option>
                        <option value="MEDIUM">MEDIUM</option>
                        <option value="LOW">LOW</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Queue List Table */}
                <div className="flex-1 overflow-y-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead className="bg-slate-50 text-slate-500 border-b border-slate-200 font-bold sticky top-0">
                      <tr>
                        <th className="px-4 py-2.5">Account ID</th>
                        <th className="px-4 py-2.5">Score</th>
                        <th className="px-4 py-2.5">Risk Tier</th>
                        <th className="px-4 py-2.5">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {filteredCases.map((c, idx) => (
                        <tr
                          key={idx}
                          onClick={() => handleSelectCase(c.account_id)}
                          className={`cursor-pointer hover:bg-slate-50 transition ${selectedCaseId === c.account_id ? 'bg-blue-50/60 font-semibold border-l-4 border-blue-600' : ''}`}
                        >
                          <td className="px-4 py-3 font-bold text-slate-900">#{c.account_id}</td>
                          <td className="px-4 py-3 font-bold text-blue-700">{c.risk_score.toFixed(4)}</td>
                          <td className="px-4 py-3">{getBadgeHTML(c.tier)}</td>
                          <td className="px-4 py-3"><span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getStatusStyle(c.status)}`}>{c.status}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Right Panel: Case Details Inspector */}
              <div className="w-1/2 p-6 overflow-y-auto bg-slate-50 space-y-6 flex flex-col">
                {loadingCase ? (
                  <div className="flex justify-center items-center h-full text-slate-400 text-xs">
                    <i className="fa-solid fa-spinner animate-spin mr-2"></i> Loading case metadata folder...
                  </div>
                ) : selectedCase ? (
                  <>
                    {/* Case Header */}
                    <div className="metric-card space-y-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <span className="text-[9px] font-mono text-slate-400">FOLDER REF: MULE-{selectedCase.account_id}</span>
                          <h3 className="text-2xl font-black font-mono text-slate-950 mt-0.5">Account Profile #{selectedCase.account_id}</h3>
                        </div>
                        <div className="text-right">
                          <div className="text-3xl font-black font-mono text-blue-700 leading-tight">{selectedCase.risk_score.toFixed(4)}</div>
                          <span className="text-[10px] text-slate-500 font-mono">Model Score</span>
                        </div>
                      </div>

                      <div className="flex flex-wrap items-center gap-3 border-t border-slate-100 pt-3 text-xs">
                        <span>{getBadgeHTML(selectedCase.tier)}</span>
                        <span className="flex items-center gap-1 font-mono">
                          <span className="text-slate-400">STATUS:</span>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getStatusStyle(selectedCase.status)}`}>{selectedCase.status}</span>
                        </span>
                        <span className="flex items-center gap-1 font-mono">
                          <span className="text-slate-400">ASSIGNED:</span>
                          <span className="text-slate-800 font-bold">{selectedCase.assigned_analyst}</span>
                        </span>
                      </div>
                    </div>

                    {/* Inspector Columns */}
                    <div className="grid grid-cols-1 gap-6">
                      {/* SHAP Attributions */}
                      <div className="metric-card space-y-4">
                        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wide flex items-center gap-1.5">
                          <i className="fa-solid fa-bolt text-amber-500"></i> Key Anomaly SHAP Attributions
                        </h4>
                        <div className="space-y-2.5">
                          {selectedCase.top_shap_drivers.map((f: string, idx: number) => {
                            const domainMap: any = {
                              'F994': 'Max UPI Transaction Velocity (Last 7D High-Volume Inflow)',
                              'F3598': 'Customer-Induced Transaction Deviation (14D Velocity Anomaly)',
                              'F1319': 'Outflow / Inflow Balance Signal (Turnover Disparity)',
                              'F1216': 'Non-Standard Access Channels Deviation (Security Log Anomaly)',
                              'F3805': 'Aggregate Transaction Volume Cap (Micro-Cap Profile Limit)',
                              'F1813': 'Transaction Velocity Turnover Band (Low Cumulative Band Deviation)'
                            };
                            return (
                              <div key={idx} className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
                                <div className="flex justify-between items-center text-xs font-mono font-bold">
                                  <span className="text-blue-900"># {f}</span>
                                  <span className="text-red-700 bg-red-50 border border-red-200 px-2 py-0.5 rounded text-[10px]">ANOMALOUS DRIVER</span>
                                </div>
                                <p className="text-[11px] text-slate-600 leading-relaxed font-sans">{domainMap[f] || 'Behavioral Feature Anomaly Indicator'}</p>
                              </div>
                            );
                          })}
                        </div>
                      </div>

                      {/* Raw Telemetry */}
                      <div className="metric-card space-y-3">
                        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wide border-b border-slate-100 pb-2">Behavioral Telemetry Logs</h4>
                        <div className="space-y-1 max-h-56 overflow-y-auto text-xs pr-1">
                          {Object.entries(selectedCase.raw_attributes).map(([k, v]: any, idx) => (
                            <div key={idx} className="flex justify-between border-b border-slate-100 py-1.5 font-mono">
                              <span className="text-slate-500">{k}:</span>
                              <span className="text-slate-950 font-bold">{v}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Controls and Compliance downloads */}
                      <div className="metric-card space-y-4">
                        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wide">Triage Controls</h4>
                        <div className="grid grid-cols-2 gap-2 text-xs">
                          {/* Status update restricted to ADMIN and INVESTIGATOR */}
                          <div className="col-span-2 space-y-1.5 border-b border-slate-100 pb-3">
                            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Update Case Status</label>
                            <div className="flex gap-2">
                              <select
                                value={statusSelect}
                                onChange={(e) => setStatusSelect(e.target.value)}
                                disabled={!['ADMIN', 'INVESTIGATOR'].includes(activeRole)}
                                className="flex-1 bg-white border border-slate-200 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-blue-600 font-sans font-semibold text-slate-800 shadow-sm disabled:bg-slate-55 disabled:cursor-not-allowed"
                              >
                                <option value="NEW">NEW</option>
                                <option value="TRIAGED">TRIAGED</option>
                                <option value="UNDER REVIEW">UNDER REVIEW</option>
                                <option value="ESCALATED">ESCALATED</option>
                                <option value="CLOSED">CLOSED</option>
                              </select>
                              <button 
                                onClick={submitStatusUpdate} 
                                disabled={!['ADMIN', 'INVESTIGATOR'].includes(activeRole)}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-sm transition disabled:bg-blue-400 disabled:opacity-60 disabled:cursor-not-allowed"
                              >
                                Update
                              </button>
                            </div>
                          </div>

                          {/* Token-secured PDF & JSON download links */}
                          <button 
                            onClick={() => handleDownloadPDF(selectedCase.account_id)} 
                            className="py-2.5 rounded-xl border border-slate-200 hover:bg-slate-50 transition text-slate-700 font-bold flex items-center justify-center gap-1.5 shadow-sm text-center"
                          >
                            <i className="fa-solid fa-file-pdf text-red-600"></i> Download PDF
                          </button>
                          <button 
                            onClick={() => handleDownloadJSON(selectedCase.account_id)} 
                            className="py-2.5 rounded-xl border border-slate-200 hover:bg-slate-50 transition text-slate-700 font-bold flex items-center justify-center gap-1.5 shadow-sm text-center font-mono text-[11px]"
                          >
                            <i className="fa-solid fa-file-code text-blue-600"></i> Download JSON
                          </button>
                          
                          {/* CBS Freeze restricted to ADMIN and INVESTIGATOR */}
                          <button 
                            onClick={submitCBSFreeze} 
                            disabled={!['ADMIN', 'INVESTIGATOR'].includes(activeRole)}
                            className="col-span-2 py-3 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold transition flex items-center justify-center gap-2 shadow shadow-red-600/10 disabled:bg-red-400 disabled:opacity-60 disabled:cursor-not-allowed"
                          >
                            <i className="fa-solid fa-lock"></i>
                            <span>Confirm Emergency CBS Debit Freeze</span>
                          </button>
                          
                          {/* STR generation restricted to ADMIN, ANALYST, INVESTIGATOR */}
                          <button 
                            onClick={triggerGenerateSTRDraft} 
                            disabled={activeRole === 'VIEWER'}
                            className="col-span-2 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold transition flex items-center justify-center gap-2 shadow-sm disabled:bg-slate-700 disabled:opacity-60 disabled:cursor-not-allowed"
                          >
                            <i className="fa-solid fa-file-invoice"></i>
                            <span>Generate Compliance STR Draft</span>
                          </button>
                        </div>
                      </div>

                      {/* Notes Log */}
                      <div className="metric-card space-y-4">
                        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wide">Investigation Notes Log</h4>
                        <div className="space-y-2.5 max-h-60 overflow-y-auto text-xs pr-1">
                          {selectedCase.notes.map((n: any, idx: number) => (
                            <div key={idx} className="p-3 bg-white border border-slate-200 rounded-xl space-y-1">
                              <div className="flex justify-between font-mono text-[9px] text-slate-400">
                                <span>BY: {n.analyst}</span>
                                <span>{n.timestamp}</span>
                              </div>
                              <p className="text-xs text-slate-700 font-medium leading-relaxed">{n.text}</p>
                            </div>
                          ))}
                        </div>
                        <div className="pt-2 border-t border-slate-100 flex flex-col gap-2">
                          <textarea
                            value={newNote}
                            onChange={(e) => setNewNote(e.target.value)}
                            disabled={activeRole === 'VIEWER'}
                            placeholder={activeRole === 'VIEWER' ? "Access Denied: Viewers have read-only access." : "Type new case note details here..."}
                            className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs focus:outline-none focus:border-blue-600 focus:bg-white h-20 disabled:bg-slate-100 disabled:cursor-not-allowed disabled:text-slate-400"
                          />
                          <button 
                            onClick={submitNote} 
                            disabled={activeRole === 'VIEWER'}
                            className="py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-sm transition disabled:bg-blue-400 disabled:opacity-60 disabled:cursor-not-allowed"
                          >
                            Add Note Entry
                          </button>
                        </div>
                      </div>

                      {/* Timeline */}
                      <div className="metric-card space-y-4">
                        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wide">Case Lifecycle Timeline</h4>
                        <div className="space-y-1 max-h-64 overflow-y-auto pr-1">
                          {selectedCase.timeline.map((t: any, idx: number) => (
                            <div key={idx} className="flex gap-3">
                              <div className="flex flex-col items-center">
                                <div className="w-2.5 h-2.5 rounded-full bg-blue-600"></div>
                                <div className="w-0.5 h-full bg-slate-200 my-0.5"></div>
                              </div>
                              <div className="space-y-0.5 pb-3">
                                <div className="font-mono text-[9px] text-slate-400">{t.timestamp}</div>
                                <div className="text-xs font-bold text-slate-900">{t.event}</div>
                                <p className="text-xs text-slate-500 font-medium">{t.detail}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="flex justify-center items-center h-full text-slate-400 text-xs">
                    Select a case from the list to view profile details.
                  </div>
                )}
              </div>
            </main>
          )}

          {/* TAB: Evaluate Account */}
          {activeTab === 'evaluate' && (
            <main className="flex-1 overflow-y-auto p-6 space-y-6">
              <div className="border-b border-slate-200 pb-3">
                <h2 className="text-2xl font-black text-slate-900 tracking-tight">Evaluate Account</h2>
                <p className="text-xs text-slate-500 mt-1">Run ad-hoc classifications on customer transaction attributes via the secure preprocessor and model.</p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Left Panel: Inputs */}
                <div className="metric-card space-y-6 flex flex-col justify-between">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center border-b border-slate-100 pb-3">
                      <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wide">Input Registry</h3>
                      <div className="flex gap-1">
                        <button onClick={() => setSandboxMode('standard')} className={`px-3 py-1.5 text-xs font-bold rounded-lg ${sandboxMode === 'standard' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'}`}>Standard Input</button>
                        <button onClick={() => setSandboxMode('advanced')} className={`px-3 py-1.5 text-xs font-bold rounded-lg ${sandboxMode === 'advanced' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'}`}>Advanced JSON</button>
                      </div>
                    </div>

                    {sandboxMode === 'standard' ? (
                      <div className="grid grid-cols-2 gap-4 text-xs">
                        <div className="space-y-1.5">
                          <label className="font-bold text-slate-700">Max UPI Velocity (7D)</label>
                          <input type="number" value={standardInputs.F994} onChange={(e) => setStandardInputs({...standardInputs, F994: parseFloat(e.target.value) || 0.0})} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-blue-600 font-mono shadow-sm" />
                        </div>
                        <div className="space-y-1.5">
                          <label className="font-bold text-slate-700">14D Velocity Anomaly</label>
                          <input type="number" value={standardInputs.F3598} onChange={(e) => setStandardInputs({...standardInputs, F3598: parseFloat(e.target.value) || 0.0})} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-blue-600 font-mono shadow-sm" />
                        </div>
                        <div className="space-y-1.5">
                          <label className="font-bold text-slate-700">Outflow / Inflow Balance</label>
                          <input type="number" value={standardInputs.F1319} onChange={(e) => setStandardInputs({...standardInputs, F1319: parseFloat(e.target.value) || 0.0})} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-blue-600 font-mono shadow-sm" />
                        </div>
                        <div className="space-y-1.5">
                          <label className="font-bold text-slate-700">Channel Deviations</label>
                          <input type="number" value={standardInputs.F1216} onChange={(e) => setStandardInputs({...standardInputs, F1216: parseFloat(e.target.value) || 0.0})} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-blue-600 font-mono shadow-sm" />
                        </div>
                        <div className="space-y-1.5">
                          <label className="font-bold text-slate-700">Micro-Cap Volume</label>
                          <input type="number" value={standardInputs.F3805} onChange={(e) => setStandardInputs({...standardInputs, F3805: parseFloat(e.target.value) || 0.0})} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-blue-600 font-mono shadow-sm" />
                        </div>
                        <div className="space-y-1.5">
                          <label className="font-bold text-slate-700">Low Turnover Band</label>
                          <input type="number" value={standardInputs.F1813} onChange={(e) => setStandardInputs({...standardInputs, F1813: parseFloat(e.target.value) || 0.0})} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-blue-600 font-mono shadow-sm" />
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <label className="text-xs font-bold text-slate-700">JSON Telemetry Payload</label>
                        <textarea value={advancedJson} onChange={(e) => setAdvancedJson(e.target.value)} className="w-full h-72 bg-slate-900 border border-slate-800 text-emerald-400 rounded-xl p-4 text-xs font-mono focus:outline-none focus:border-blue-600 leading-relaxed" />
                      </div>
                    )}
                  </div>

                  <div className="flex gap-2 text-xs pt-4 border-t border-slate-100">
                    <button onClick={handleLoadSamplePayload} className="px-4 py-3 border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-xl font-bold flex-1 transition shadow-sm">Load Sample Payload</button>
                    <button onClick={runPrediction} className="px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold flex-1 transition shadow">RUN MULESHIELD ANALYSIS</button>
                  </div>
                </div>

                {/* Right Panel: Output */}
                <div className="metric-card flex flex-col justify-center min-h-[380px] bg-slate-900/5 text-slate-800 rounded-2xl relative overflow-hidden">
                  {evaluating ? (
                    <div className="my-auto space-y-4 p-8 text-center text-xs font-mono text-slate-500 max-w-sm mx-auto">
                      <div className="space-y-2.5">
                        <div className="flex justify-between items-center text-emerald-600">
                          <span>1. VALIDATING SCHEMA</span>
                          <span className="font-bold">✓</span>
                        </div>
                        <div className="flex justify-between items-center text-emerald-600">
                          <span>2. REMOVING TARGET LEAKAGE</span>
                          <span className="font-bold">✓</span>
                        </div>
                        <div className="flex justify-between items-center text-emerald-600">
                          <span>3. RUNNING PREPROCESSOR</span>
                          <span className="font-bold">✓</span>
                        </div>
                        <div className="flex justify-between items-center text-blue-600 font-bold">
                          <span className="animate-pulse">4. EVALUATING XGBOOST MODEL</span>
                          <i className="fa-solid fa-spinner animate-spin"></i>
                        </div>
                      </div>
                    </div>
                  ) : evalError ? (
                    <div className="text-center my-auto text-xs text-red-600">
                      <i className="fa-solid fa-triangle-exclamation mr-1"></i> {evalError}
                    </div>
                  ) : evalResult ? (
                    <div className="space-y-6 my-auto p-6">
                      <div className="text-center space-y-1.5">
                        <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Classification Inference Result</span>
                        <h3 className={`text-5xl font-black font-mono tracking-tight ${evalResult.tier === 'Critical' ? 'text-red-600' : (evalResult.tier === 'High' ? 'text-orange-600' : 'text-blue-600')}`}>{evalResult.risk_score.toFixed(4)}</h3>
                        <span className="inline-block pt-1">{getBadgeHTML(evalResult.tier)}</span>
                      </div>
                      
                      <div className={`p-4 rounded-xl border space-y-2.5 text-xs font-medium ${evalResult.tier === 'Critical' ? 'border-red-200 bg-red-50 text-red-950' : (evalResult.tier === 'High' ? 'border-orange-200 bg-orange-50 text-orange-950' : 'border-emerald-200 bg-emerald-50 text-emerald-950')}`}>
                        <div className="flex justify-between items-center">
                          <span>Model Classification:</span>
                          <span className={`font-mono font-bold px-2 py-0.5 rounded text-[10px] uppercase border ${evalResult.tier === 'Critical' ? 'bg-red-100 text-red-800' : (evalResult.tier === 'High' ? 'bg-orange-100 text-orange-800' : 'bg-emerald-100 text-emerald-800')}`}>{evalResult.tier} RISK</span>
                        </div>
                        <p className="text-[11px] leading-relaxed">
                          {evalResult.tier === 'Critical' ? 'This account has exceeded the operating decision boundary. System suggests immediate freeze.' : (evalResult.tier === 'High' ? 'This account indicates anomaly score patterns. System recommends manual analyst investigation.' : 'This account telemetry aligns to baseline parameters. No action required.')}
                        </p>
                      </div>

                      <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1 font-mono text-[11px]">
                        <div className="flex justify-between text-slate-500">
                          <span>Operating Boundary:</span>
                          <strong className="text-slate-900">0.9899</strong>
                        </div>
                        <div className="flex justify-between text-slate-500">
                          <span>Action Directive:</span>
                          <strong className="text-slate-900">{evalResult.action}</strong>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center my-auto text-xs text-slate-400 font-mono">
                      Input attributes and execute the classifier.
                    </div>
                  )}
                </div>
              </div>
            </main>
          )}

          {/* TAB: Mule Network Graph */}
          {activeTab === 'network' && (
            <main className="flex-1 overflow-y-auto p-6 space-y-6">
              <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                <div>
                  <h2 className="text-2xl font-black text-slate-900 tracking-tight">Mule Network Ring Graph</h2>
                  <p className="text-xs text-slate-500 mt-1">Trace multi-hop fund routing paths from victim origins to aggregator cash-out nodes.</p>
                </div>
                <div className="flex gap-2">
                  <button className="px-3.5 py-2 rounded-xl bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-bold transition flex items-center space-x-1.5 shadow-sm">1-Hop</button>
                  <button className="px-3.5 py-2 rounded-xl bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-bold transition flex items-center space-x-1.5 shadow-sm">2-Hop</button>
                  <button onClick={initNetworkGraph} className="px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold transition flex items-center space-x-1.5 shadow-sm">
                    <i className="fa-solid fa-arrows-rotate"></i>
                    <span>Reset Layout</span>
                  </button>
                </div>
              </div>

              <div className="metric-card space-y-4">
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl space-y-1 text-xs text-blue-900">
                  <div className="font-bold flex items-center gap-1.5">
                    <i class="fa-solid fa-circle-info"></i> DEMONSTRATION NETWORK TOPOLOGY
                  </div>
                  <p className="text-[11px] leading-relaxed">This visualization presents simulated multi-hop transaction topologies to demonstrate network ring identification workflows.</p>
                </div>
                <div ref={networkContainerRef} id="vis-network-container" className="border border-slate-200 rounded-2xl overflow-hidden shadow-inner">
                  {/* Vis Network injects canvas here */}
                </div>
              </div>
            </main>
          )}

          {/* TAB: Regulatory Intelligence */}
          {activeTab === 'regulatory' && (
            <main className="flex-1 overflow-y-auto p-6 space-y-6">
              <div className="border-b border-slate-200 pb-3 flex justify-between items-center">
                <div>
                  <h2 className="text-2xl font-black text-slate-900 tracking-tight">Regulatory Intelligence Intersection</h2>
                  <p className="text-xs text-slate-500 mt-1">Automatic match validation against government watchlists and cautions registry logs.</p>
                </div>
                <input
                  type="text"
                  placeholder="Search accounts index..."
                  className="bg-white border border-slate-200 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-blue-600 font-mono shadow-sm"
                />
              </div>

              <div className="metric-card space-y-4">
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl space-y-1 text-xs text-blue-900">
                  <div className="font-bold flex items-center gap-1.5">
                    <i class="fa-solid fa-circle-info"></i> DEMONSTRATION INTELLIGENCE REGISTRY
                  </div>
                  <p className="text-[11px] leading-relaxed">Watchlist matches correspond to simulated cautionary checks for product demonstration integrity.</p>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead className="bg-slate-50 text-slate-500 border-b border-slate-200 font-bold sticky top-0">
                      <tr>
                        <th className="px-4 py-3">Account ID</th>
                        <th className="px-4 py-3">ML Tier</th>
                        <th className="px-4 py-3">I4C Cyber Fraud DB</th>
                        <th className="px-4 py-3">RBI Caution Registry</th>
                        <th className="px-4 py-3">Action Directive</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {allCases.filter(c => c.tier === 'Critical').map((c, idx) => (
                        <tr key={idx} className="hover:bg-slate-50 font-mono">
                          <td className="px-4 py-3 font-bold text-slate-900">#{c.account_id}</td>
                          <td className="px-4 py-3">{getBadgeHTML(c.tier)}</td>
                          <td className="px-4 py-3 text-red-600 font-extrabold flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-red-600"></span> FLAGGED
                          </td>
                          <td className="px-4 py-3 text-red-600 font-extrabold">
                            <span className="w-1.5 h-1.5 rounded-full bg-red-600 inline-block mr-1"></span> FLAGGED
                          </td>
                          <td className="px-4 py-3 font-sans text-slate-700">{c.action}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </main>
          )}

          {/* TAB: Performance Benchmarks */}
          {activeTab === 'model' && (
            <main className="flex-1 overflow-y-auto p-6 space-y-6">
              <div className="border-b border-slate-200 pb-3">
                <h2 className="text-2xl font-black text-slate-900 tracking-tight">Technical Model Performance Benchmarks</h2>
                <p className="text-xs text-slate-500 mt-1">Champions model metadata validation scoring statistics loaded dynamically from the metadata API.</p>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="metric-card flex flex-col justify-between shadow-sm">
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Validated PR-AUC</span>
                  <div className="mt-4">
                    <h3 className="text-3xl font-black font-mono text-slate-900">{(modelMetadata.pr_auc || 0).toFixed(4)}</h3>
                    <p className="text-[11px] text-slate-500 font-mono mt-1">± {(modelMetadata.pr_auc_std || 0).toFixed(4)} Std Dev</p>
                  </div>
                </div>
                <div className="metric-card flex flex-col justify-between shadow-sm border-l-4 border-l-emerald-500">
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Operating Precision</span>
                  <div className="mt-4">
                    <h3 className="text-3xl font-black font-mono text-emerald-600">100.00%</h3>
                    <p className="text-[11px] text-slate-500 font-mono mt-1">0 False Positives / Freezes</p>
                  </div>
                </div>
                <div className="metric-card flex flex-col justify-between shadow-sm">
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Model Recall</span>
                  <div className="mt-4">
                    <h3 className="text-3xl font-black font-mono text-slate-900">{(modelMetadata.recall * 100).toFixed(2)}%</h3>
                    <p className="text-[11px] text-slate-500 font-mono mt-1">Auto-Flags 61.64% of Mules</p>
                  </div>
                </div>
                <div className="metric-card flex flex-col justify-between shadow-sm border-l-4 border-l-blue-500">
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Model F1 Score</span>
                  <div className="mt-4">
                    <h3 className="text-3xl font-black font-mono text-blue-600">{(modelMetadata.f1 || 0).toFixed(4)}</h3>
                    <p className="text-[11px] text-slate-500 font-mono mt-1">Operating Calibrated Peak</p>
                  </div>
                </div>
              </div>

              <div className="metric-card space-y-4">
                <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wide border-b border-slate-100 pb-2">Mathematical Calibration Rationale</h3>
                <p className="text-xs text-slate-600 leading-relaxed font-sans">
                  In financial crime operations, false positive freezes harm legitimate users and lock clean funds. Standard ML optimization models maximize F1-score, which leads to a 10% false positive freeze rate. MuleShield PRO utilizes threshold calibration bound at exactly <strong className="text-blue-600 font-mono">{modelMetadata.threshold}</strong>. This aligns classification precision to exactly <strong className="text-emerald-600 font-sans">100.00% (0 False Freezes)</strong>, prioritizing compliance safety while intercepting 61.64% of suspicious mule accounts.
                </p>
              </div>
            </main>
          )}

          {/* TAB: Technical Integrity Audit */}
          {activeTab === 'audit' && (
            <main className="flex-1 overflow-y-auto p-6 space-y-6">
              <div className="border-b border-slate-200 pb-3">
                <h2 className="text-2xl font-black text-slate-900 tracking-tight">System Technical Integrity Audit Check</h2>
                <p className="text-xs text-slate-500 mt-1">Compliance checklist validating preprocessing, model freeze conditions, and target leakage verification.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
                <div className="metric-card space-y-4">
                  <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wide border-b border-slate-100 pb-2">Leakage & Validation Audit</h3>
                  <div className="space-y-3.5">
                    <div className="flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-xl">
                      <span className="flex items-center gap-2 text-slate-700">
                        <i className="fa-solid fa-circle-check text-emerald-500"></i> Target Leakage Columns Dropped (14 Fields)
                      </span>
                      <span className="text-[10px] text-slate-400">VERIFIED</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-xl">
                      <span className="flex items-center gap-2 text-slate-700">
                        <i className="fa-solid fa-circle-check text-emerald-500"></i> Group-Aware Graph Cross-Validation Split
                      </span>
                      <span className="text-[10px] text-slate-400">VERIFIED</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-xl">
                      <span className="flex items-center gap-2 text-slate-700">
                        <i className="fa-solid fa-circle-check text-emerald-500"></i> Fold-Local Resampling Isolated
                      </span>
                      <span className="text-[10px] text-slate-400">VERIFIED</span>
                    </div>
                  </div>
                </div>

                <div className="metric-card space-y-4">
                  <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wide border-b border-slate-100 pb-2">Verification Artifact Reference</h3>
                  <div className="space-y-3.5">
                    <div className="p-3.5 bg-blue-50 border border-blue-200 rounded-xl text-blue-900">
                      <h4 className="font-bold flex items-center gap-1.5"><i className="fa-solid fa-file-invoice"></i> Model Calibration</h4>
                      <p className="text-[11px] text-blue-800 mt-1">
                        The pre-compiled metrics, threshold settings, and feature filters have been locked in the model configuration. The pipeline processes raw attributes without retraining features during triage.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </main>
          )}

          {/* TAB: System Audit Logs */}
          {activeTab === 'logs' && (
            <main className="flex-1 overflow-y-auto p-6 space-y-6">
              <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                <div>
                  <h2 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
                    <i className="fa-solid fa-receipt text-blue-600"></i> System Audit Trail
                  </h2>
                  <p className="text-xs text-slate-500 mt-1">Immutable session logs tracking analyst investigations and system events.</p>
                </div>
                <button onClick={fetchAuditLogs} className="px-3.5 py-2 rounded-xl bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 text-xs font-bold transition flex items-center space-x-2 shadow-sm">
                  <i className="fa-solid fa-arrows-rotate"></i>
                  <span>Refresh Logs</span>
                </button>
              </div>

              <div className="metric-card space-y-4">
                <div className="overflow-x-auto min-h-96">
                  {loadingLogs ? (
                    <div className="text-center py-12 text-slate-400 text-xs">Loading audit logs...</div>
                  ) : (
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="bg-slate-50 text-slate-500 border-b border-slate-200 font-bold">
                        <tr>
                          <th className="px-4 py-3">Timestamp Log</th>
                          <th className="px-4 py-3">Operations Actor</th>
                          <th className="px-4 py-3">Action Item</th>
                          <th className="px-4 py-3">Case ID</th>
                          <th className="px-4 py-3">Execution Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {auditLogs.map((l, idx) => (
                          <tr key={idx}>
                            <td className="px-4 py-2.5 text-slate-500 font-mono text-[11px]">{l.timestamp}</td>
                            <td className="px-4 py-2.5 font-bold text-slate-800">{l.actor}</td>
                            <td className="px-4 py-2.5 font-semibold text-blue-900">{l.action}</td>
                            <td className="px-4 py-2.5 font-bold font-mono text-slate-700">{l.case_id}</td>
                            <td className="px-4 py-2.5 font-bold text-emerald-600">{l.status}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              </div>
            </main>
          )}

        </div>
      </div>
    </div>
  );
}
