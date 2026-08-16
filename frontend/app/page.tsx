"use client";

import React, { useState, useEffect } from "react";

interface CaseItem {
  account_id: number;
  risk_score: number;
  tier: "Critical" | "High" | "Medium" | "Low";
  action: string;
  top_shap_drivers: string[];
  regulatory_flags: {
    i4c_db: string;
    cert_in_botnet: string;
    rbi_caution_list: string;
  };
  raw_attributes: Record<string, string>;
}

export default function MuleShieldDashboard() {
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [selectedCase, setSelectedCase] = useState<CaseItem | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [strDraft, setStrDraft] = useState<string | null>(null);
  const [loadingStr, setLoadingStr] = useState<boolean>(false);
  const [filterTier, setFilterTier] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");

  useEffect(() => {
    fetchCases();
  }, []);

  const fetchCases = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/cases");
      const data = await res.json();
      setCases(data.cases || []);
      if (data.cases && data.cases.length > 0) {
        setSelectedCase(data.cases[0]);
      }
    } catch (err) {
      console.error("Error fetching cases from backend API:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCase = async (accId: number) => {
    setStrDraft(null);
    try {
      const res = await fetch(`http://localhost:8000/api/cases/${accId}`);
      const data = await res.json();
      setSelectedCase(data);
    } catch (err) {
      console.error("Error fetching case details:", err);
    }
  };

  const handleGenerateSTR = async () => {
    if (!selectedCase) return;
    setLoadingStr(true);
    try {
      const res = await fetch(`http://localhost:8000/api/cases/${selectedCase.account_id}/str-draft`, {
        method: "POST",
      });
      const data = await res.json();
      setStrDraft(data.str_draft);
    } catch (err) {
      console.error("Error generating STR draft:", err);
    } finally {
      setLoadingStr(false);
    }
  };

  // Filter and search
  const filteredCases = cases.filter((c) => {
    const matchesTier = filterTier === "ALL" || c.tier.toUpperCase() === filterTier;
    const matchesSearch = searchQuery === "" || c.account_id.toString().includes(searchQuery);
    return matchesTier && matchesSearch;
  });

  // Calculate Metrics
  const totalCount = cases.length;
  const criticalCount = cases.filter((c) => c.tier === "Critical").length;
  const highCount = cases.filter((c) => c.tier === "High").length;
  const clearedCount = cases.filter((c) => c.tier === "Low").length;

  const getTierBadge = (tier: string) => {
    switch (tier) {
      case "Critical":
        return (
          <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-red-500/20 text-red-400 border border-red-500/30">
            CRITICAL
          </span>
        );
      case "High":
        return (
          <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-orange-500/20 text-orange-400 border border-orange-500/30">
            HIGH
          </span>
        );
      case "Medium":
        return (
          <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">
            MEDIUM
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            LOW
          </span>
        );
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-950 text-slate-100 font-sans overflow-hidden">
      {/* Navbar */}
      <header className="glass-panel px-6 py-4 flex items-center justify-between z-10">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-500 flex items-center justify-center text-xl shadow-lg shadow-indigo-500/20">
            🛡️
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              MuleShield <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-mono border border-indigo-500/30">PSB CyberShield 2026</span>
            </h1>
            <p className="text-xs text-slate-400">AI/ML Mule Account Detection & Regulatory Risk Engine</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-xs text-slate-300 bg-slate-900/90 px-3 py-1.5 rounded-lg border border-slate-800 font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>API: http://localhost:8000 (XGBoost 0.9115 CV)</span>
          </div>
        </div>
      </header>

      {/* Metric Cards Banner */}
      <div className="grid grid-cols-4 gap-4 px-6 py-4 bg-slate-950 border-b border-slate-800/80">
        <div className="glass-card p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 font-medium">Total Account Queue</p>
            <h3 className="text-2xl font-black font-mono text-white mt-1">{totalCount}</h3>
          </div>
          <div className="text-2xl">📋</div>
        </div>
        <div className="glass-card p-4 flex items-center justify-between border-l-4 border-l-red-500">
          <div>
            <p className="text-xs text-slate-400 font-medium">Critical Mule Alerts</p>
            <h3 className="text-2xl font-black font-mono text-red-400 mt-1">{criticalCount}</h3>
          </div>
          <div className="text-2xl">🚨</div>
        </div>
        <div className="glass-card p-4 flex items-center justify-between border-l-4 border-l-orange-500">
          <div>
            <p className="text-xs text-slate-400 font-medium">High Risk Cases</p>
            <h3 className="text-2xl font-black font-mono text-orange-400 mt-1">{highCount}</h3>
          </div>
          <div className="text-2xl">⚠️</div>
        </div>
        <div className="glass-card p-4 flex items-center justify-between border-l-4 border-l-emerald-500">
          <div>
            <p className="text-xs text-slate-400 font-medium">Cleared Accounts</p>
            <h3 className="text-2xl font-black font-mono text-emerald-400 mt-1">{clearedCount}</h3>
          </div>
          <div className="text-2xl">✅</div>
        </div>
      </div>

      {/* Main Workspace Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel: Case Queue */}
        <div className="w-1/2 border-r border-slate-800/80 flex flex-col bg-slate-950">
          {/* Controls */}
          <div className="p-4 border-b border-slate-800/80 flex items-center justify-between bg-slate-900/40 gap-3">
            <input
              type="text"
              placeholder="Search by Account ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-slate-900 border border-slate-800 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-500 w-48 font-mono"
            />

            <div className="flex space-x-1 bg-slate-900 p-1 rounded-lg border border-slate-800">
              {["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"].map((t) => (
                <button
                  key={t}
                  onClick={() => setFilterTier(t)}
                  className={`px-2.5 py-1 text-xs rounded-md font-medium transition ${
                    filterTier === t ? "bg-indigo-600 text-white shadow" : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* Table */}
          <div className="flex-1 overflow-y-auto">
            {loading ? (
              <div className="flex justify-center items-center h-48 text-slate-500 text-sm">
                Loading case queue from backend...
              </div>
            ) : (
              <table className="w-full text-left text-xs">
                <thead className="sticky top-0 bg-slate-900 text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="px-4 py-3 font-semibold">Account ID</th>
                    <th className="px-4 py-3 font-semibold">Risk Score</th>
                    <th className="px-4 py-3 font-semibold">Tier</th>
                    <th className="px-4 py-3 font-semibold">Top Driver</th>
                    <th className="px-4 py-3 font-semibold">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {filteredCases.map((c) => {
                    const isSelected = selectedCase && selectedCase.account_id === c.account_id;
                    return (
                      <tr
                        key={c.account_id}
                        onClick={() => handleSelectCase(c.account_id)}
                        className={`cursor-pointer transition hover:bg-slate-900/80 ${
                          isSelected ? "bg-indigo-950/50 border-l-4 border-indigo-500" : ""
                        }`}
                      >
                        <td className="px-4 py-3 font-mono font-bold text-slate-200">#{c.account_id}</td>
                        <td className="px-4 py-3 font-mono font-extrabold text-slate-100">{c.risk_score.toFixed(4)}</td>
                        <td className="px-4 py-3">{getTierBadge(c.tier)}</td>
                        <td className="px-4 py-3 font-mono text-slate-400 truncate max-w-[120px]">
                          {c.top_shap_drivers[0] || "N/A"}
                        </td>
                        <td className="px-4 py-3 text-slate-300">{c.action}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Right Panel: Account Review & STR Draft */}
        <div className="w-1/2 flex flex-col bg-slate-900/30 overflow-y-auto p-6 space-y-6">
          {selectedCase ? (
            <>
              {/* Header Overview Card */}
              <div className="glass-card p-6 rounded-2xl flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-3">
                    <h3 className="text-3xl font-extrabold text-white font-mono">Account #{selectedCase.account_id}</h3>
                    {getTierBadge(selectedCase.tier)}
                  </div>
                  <p className="text-xs text-slate-400 mt-2">
                    Recommended Action: <strong className="text-slate-200 font-semibold">{selectedCase.action}</strong>
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-4xl font-black font-mono text-indigo-400 tracking-tight">
                    {selectedCase.risk_score.toFixed(4)}
                  </div>
                  <div className="text-xs text-slate-400 font-medium mt-1">Classifier Risk Probability</div>
                </div>
              </div>

              {/* SHAP Behavioral Drivers */}
              <div className="glass-card p-6 rounded-2xl space-y-4">
                <h4 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                  <span>⚡</span> Top Behavioral Anomaly Drivers (SHAP Explanation)
                </h4>
                <div className="space-y-2">
                  {selectedCase.top_shap_drivers.map((feat, i) => (
                    <div key={feat} className="flex items-center justify-between p-3 rounded-xl bg-slate-950/70 border border-slate-800 text-xs">
                      <span className="font-mono text-indigo-300 font-bold">#{i + 1} {feat}</span>
                      <span className="px-2.5 py-1 rounded-md bg-red-500/10 text-red-400 text-[10px] font-mono font-bold">HIGH ANOMALY IMPACT</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Regulatory Intersections */}
              <div className="glass-card p-6 rounded-2xl space-y-4">
                <h4 className="text-sm font-bold text-slate-200 flex items-center justify-between">
                  <span className="flex items-center gap-2">🌐 Mocked Regulatory Flags Panel</span>
                  <span className="text-[10px] text-slate-400 font-mono">I4C / CERT-In / RBI Mock</span>
                </h4>
                <div className="grid grid-cols-3 gap-3">
                  <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 text-center">
                    <div className="text-[10px] text-slate-400 font-medium">I4C Cyber Fraud DB</div>
                    <div className={`mt-1 text-xs font-bold font-mono ${selectedCase.regulatory_flags.i4c_db === "FLAGGED" ? "text-red-400" : "text-emerald-400"}`}>
                      {selectedCase.regulatory_flags.i4c_db}
                    </div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 text-center">
                    <div className="text-[10px] text-slate-400 font-medium">CERT-In Botnet List</div>
                    <div className="mt-1 text-xs font-bold font-mono text-emerald-400">
                      {selectedCase.regulatory_flags.cert_in_botnet}
                    </div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 text-center">
                    <div className="text-[10px] text-slate-400 font-medium">RBI Caution List</div>
                    <div className={`mt-1 text-xs font-bold font-mono ${selectedCase.regulatory_flags.rbi_caution_list === "FLAGGED" ? "text-red-400" : "text-emerald-400"}`}>
                      {selectedCase.regulatory_flags.rbi_caution_list}
                    </div>
                  </div>
                </div>
              </div>

              {/* STR Action */}
              <div className="space-y-4">
                <button
                  onClick={handleGenerateSTR}
                  disabled={loadingStr}
                  className="w-full py-3.5 px-4 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white font-bold text-sm shadow-lg shadow-indigo-600/30 transition flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  <span>📄</span>
                  <span>{loadingStr ? "Generating STR Draft..." : "Generate Suspicious Transaction Report (STR) Draft"}</span>
                </button>

                {strDraft && (
                  <div className="glass-panel p-5 rounded-2xl border border-indigo-500/30 space-y-3">
                    <div className="flex items-center justify-between text-xs text-indigo-300 font-bold">
                      <span>REGULATORY COMPLIANCE DRAFT (FIU-IND)</span>
                      <button
                        onClick={() => navigator.clipboard.writeText(strDraft)}
                        className="text-slate-400 hover:text-white underline text-xs"
                      >
                        Copy Text
                      </button>
                    </div>
                    <pre className="p-4 bg-slate-950 rounded-xl text-xs font-mono text-emerald-400 overflow-x-auto border border-slate-800 whitespace-pre-wrap leading-relaxed">
                      {strDraft}
                    </pre>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="flex justify-center items-center h-full text-slate-500 text-sm">
              Select an account from the queue to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
