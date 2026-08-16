"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Users, Award, ShieldCheck, QrCode, FileText, 
  MapPin, Clock, ArrowUpRight, BarChart2, Plus, Sparkles
} from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState({
    registered_weavers: 1,
    registered_products: 1,
    active_passports: 1,
    verification_success_rate: 96.5,
    verification_requests: 2,
    verification_logs: [],
    recent_activity: []
  });
  
  const [products, setProducts] = useState<any[]>([]);
  const [weavers, setWeavers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchData() {
      try {
        const statsRes = await fetch('http://localhost:8000/api/dashboard-stats');
        if (statsRes.ok) {
          const statsData = await statsRes.json();
          setStats(statsData);
        }
        
        // Fetch passport list from mock/local DB
        const passportListRes = await fetch('http://localhost:8000/api/get-passport/CRFT-842193');
        if (passportListRes.ok) {
          const passportData = await passportListRes.json();
          setProducts([passportData.product]);
          setWeavers([passportData.weaver]);
        }
      } catch (err) {
        console.error("Error fetching dashboard data, using mock fallback", err);
        // Fallback mock data in case backend isn't running yet (hydration safety)
        setProducts([{
          id: "CRFT-842193",
          name: "Mayil Motif Crimson Kanchipuram Silk",
          category: "Saree",
          color: "Crimson Maroon & Temple Gold",
          pattern: "Mayil (Peacock) & Chakram motifs",
          material: "Pure Mulberry Silk & 24k Gold Zari Thread",
          weaver_id: "WVR-849201",
          created_at: "2026-06-01T09:00:00Z"
        }]);
        setWeavers([{
          id: "WVR-849201",
          name: "Lakshmi Devi",
          village: "Kanchipuram",
          cooperative: "Kanchipuram Silk Cooperative",
          experience: "28 Years",
          verification_status: "Verified"
        }]);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-cream-50 flex">
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-indigo-900 text-cream-50 flex flex-col justify-between p-6 shrink-0 border-r border-indigo-950">
        <div className="space-y-8">
          <div className="flex items-center space-x-3">
            <div className="h-8 w-8 bg-maroon-600 rounded flex items-center justify-center text-gold-300 font-serif font-bold text-lg shadow-sm">
              L
            </div>
            <span className="font-serif font-semibold text-base text-white tracking-wide">
              LoomProof Console
            </span>
          </div>

          <nav className="space-y-2 text-xs">
            <p className="text-indigo-400 font-bold uppercase tracking-wider px-2 mb-2">Artisan Trust Suite</p>
            <Link href="/dashboard" className="flex items-center space-x-3 px-3 py-2.5 bg-indigo-800 text-white rounded-lg font-medium transition-all">
              <BarChart2 className="h-4 w-4 text-gold-300" />
              <span>Overview Console</span>
            </Link>
            <Link href="/weaver" className="flex items-center space-x-3 px-3 py-2.5 text-indigo-200 hover:bg-indigo-800 hover:text-white rounded-lg font-medium transition-all">
              <Users className="h-4 w-4 text-indigo-300" />
              <span>Artisan Registration</span>
            </Link>
            <Link href="/create-craft" className="flex items-center space-x-3 px-3 py-2.5 text-indigo-200 hover:bg-indigo-800 hover:text-white rounded-lg font-medium transition-all">
              <Plus className="h-4 w-4 text-indigo-300" />
              <span>Create Craft ID</span>
            </Link>
            <Link href="/weaveproof" className="flex items-center space-x-3 px-3 py-2.5 text-indigo-200 hover:bg-indigo-800 hover:text-white rounded-lg font-medium transition-all">
              <Clock className="h-4 w-4 text-indigo-300" />
              <span>Weave Checkpoints</span>
            </Link>
            <Link href="/product-match" className="flex items-center space-x-3 px-3 py-2.5 text-indigo-200 hover:bg-indigo-800 hover:text-white rounded-lg font-medium transition-all">
              <ShieldCheck className="h-4 w-4 text-indigo-300" />
              <span>FabricPrint Matcher</span>
            </Link>
            <Link href="/verify" className="flex items-center space-x-3 px-3 py-2.5 text-indigo-200 hover:bg-indigo-800 hover:text-white rounded-lg font-medium transition-all">
              <QrCode className="h-4 w-4 text-indigo-300" />
              <span>Clone Scanner Demo</span>
            </Link>
          </nav>
        </div>

        <div className="space-y-4">
          <div className="bg-indigo-950 p-4 rounded-xl border border-indigo-800/40 text-[10px] space-y-2 text-indigo-300">
            <div className="flex items-center space-x-1.5 text-gold-300 font-semibold">
              <span className="h-1.5 w-1.5 bg-green-400 rounded-full animate-ping" />
              <span>LoomProof Trust Core</span>
            </div>
            <p>Database: <strong className="text-white">Local Fallback (JSON)</strong></p>
            <p>CV Engine: <strong className="text-white">OpenCV Active</strong></p>
          </div>
          <Link href="/" className="text-xs text-indigo-400 hover:text-white transition-colors block text-center">
            ← Back to Landing
          </Link>
        </div>
      </aside>

      {/* Main Console Content */}
      <main className="flex-grow p-8 overflow-y-auto max-w-6xl">
        <header className="flex justify-between items-center mb-8 border-b border-sand-200 pb-6">
          <div>
            <h1 className="font-serif text-3xl font-semibold text-indigo-900">Artisan Provenance Console</h1>
            <p className="text-xs text-indigo-600/70 mt-1">Audit verification logs, register craft timelines, and manage digital trust passports.</p>
          </div>
          
          <div className="flex items-center space-x-3">
            <Link href="/weaver" className="px-4 py-2 text-xs font-semibold bg-maroon-600 hover:bg-maroon-700 text-white rounded-full flex items-center space-x-1.5 shadow-sm transition-all">
              <Plus className="h-3.5 w-3.5" />
              <span>Register Artisan</span>
            </Link>
            <Link href="/create-craft" className="px-4 py-2 text-xs font-semibold bg-white border border-sand-300 text-indigo-900 rounded-full hover:border-indigo-600 shadow-sm transition-all">
              <span>Generate Craft ID</span>
            </Link>
          </div>
        </header>

        {/* Dashboard Widgets Row */}
        <section className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="luxury-card p-6 bg-white flex flex-col justify-between">
            <div className="flex justify-between items-start text-indigo-600">
              <span className="text-xs font-semibold uppercase tracking-wider">Registered Weavers</span>
              <Users className="h-5 w-5 text-maroon-600" />
            </div>
            <div className="mt-4">
              <span className="text-3xl font-serif font-bold text-indigo-900">{stats.registered_weavers}</span>
              <p className="text-[10px] text-green-600 font-medium mt-1">● 100% Cooperative Affiliated</p>
            </div>
          </div>

          <div className="luxury-card p-6 bg-white flex flex-col justify-between">
            <div className="flex justify-between items-start text-indigo-600">
              <span className="text-xs font-semibold uppercase tracking-wider">Active Passports</span>
              <FileText className="h-5 w-5 text-gold-500" />
            </div>
            <div className="mt-4">
              <span className="text-3xl font-serif font-bold text-indigo-900">{stats.active_passports}</span>
              <p className="text-[10px] text-indigo-500 font-medium mt-1">● Creation Journey Sealed</p>
            </div>
          </div>

          <div className="luxury-card p-6 bg-white flex flex-col justify-between">
            <div className="flex justify-between items-start text-indigo-600">
              <span className="text-xs font-semibold uppercase tracking-wider">Verification Requests</span>
              <QrCode className="h-5 w-5 text-indigo-900" />
            </div>
            <div className="mt-4">
              <span className="text-3xl font-serif font-bold text-indigo-900">{stats.verification_requests || 2}</span>
              <p className="text-[10px] text-indigo-500 font-medium mt-1">● Consumer scans log</p>
            </div>
          </div>

          <div className="luxury-card p-6 bg-white flex flex-col justify-between">
            <div className="flex justify-between items-start text-indigo-600">
              <span className="text-xs font-semibold uppercase tracking-wider">CV Verification Rate</span>
              <ShieldCheck className="h-5 w-5 text-green-600" />
            </div>
            <div className="mt-4">
              <span className="text-3xl font-serif font-bold text-indigo-900">{stats.verification_success_rate}%</span>
              <p className="text-[10px] text-green-600 font-medium mt-1">● High-Confidence Matches</p>
            </div>
          </div>
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Registered Handlooms Table */}
          <div className="lg:col-span-2 space-y-6">
            <div className="luxury-card p-6 bg-white">
              <div className="flex justify-between items-center mb-6">
                <h3 className="font-serif text-lg font-medium text-indigo-900">Seal-Locked Handloom Products</h3>
                <span className="text-[10px] bg-sand-200 text-maroon-700 px-2.5 py-1 rounded-full font-semibold uppercase tracking-wider">
                  Active Proof Registry
                </span>
              </div>
              
              {loading ? (
                <div className="py-12 text-center text-xs text-indigo-600/70 animate-pulse">Loading Registered Crafts...</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-sand-200 text-indigo-600/80 font-medium">
                        <th className="pb-3 font-semibold uppercase">Craft ID</th>
                        <th className="pb-3 font-semibold uppercase">Product Details</th>
                        <th className="pb-3 font-semibold uppercase">Artisan</th>
                        <th className="pb-3 font-semibold uppercase">Status</th>
                        <th className="pb-3 text-right font-semibold uppercase">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-sand-100">
                      {products.map((p, idx) => (
                        <tr key={p.id || idx} className="hover:bg-cream-50/50 transition-colors">
                          <td className="py-4 font-mono font-medium text-indigo-900">{p.id}</td>
                          <td className="py-4">
                            <span className="font-serif font-medium text-indigo-900 text-sm block">{p.name}</span>
                            <span className="text-[10px] text-indigo-500 font-medium mt-0.5 block">{p.color} • {p.category}</span>
                          </td>
                          <td className="py-4">
                            <span className="font-medium text-indigo-800">{weavers.find(w => w.id === p.weaver_id)?.name || "Lakshmi Devi"}</span>
                            <span className="text-[10px] text-indigo-500 block">Kanchipuram, TN</span>
                          </td>
                          <td className="py-4">
                            <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-green-50 text-green-700 border border-green-200">
                              <span className="h-1 w-1 bg-green-500 rounded-full" />
                              <span>Journey Documented</span>
                            </span>
                          </td>
                          <td className="py-4 text-right">
                            <Link href={`/passport/${p.id}`} className="inline-flex items-center space-x-1 text-xs text-maroon-600 hover:text-maroon-800 font-semibold transition-all">
                              <span>Open Passport</span>
                              <ArrowUpRight className="h-3.5 w-3.5" />
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Verification Logs */}
            <div className="luxury-card p-6 bg-white">
              <h3 className="font-serif text-lg font-medium text-indigo-900 mb-6">Recent Customer Verification Queries</h3>
              
              <div className="space-y-4">
                {stats.verification_logs.length > 0 ? (
                  stats.verification_logs.map((log: any, idx: number) => (
                    <div key={idx} className="flex items-center justify-between border-b border-sand-100 pb-3 last:border-0 last:pb-0">
                      <div className="flex items-center space-x-3">
                        <div className={`h-8 w-8 rounded-lg flex items-center justify-center text-xs font-semibold ${log.status === "Verified Match" ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-maroon-50 text-maroon-700 border border-maroon-200'}`}>
                          {log.similarity}%
                        </div>
                        <div>
                          <span className="text-xs font-semibold text-indigo-900 block">Scan verified on {log.device}</span>
                          <span className="text-[10px] text-indigo-500 flex items-center space-x-1 mt-0.5">
                            <MapPin className="h-3 w-3" />
                            <span>{log.location}</span>
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${log.status === "Verified Match" ? 'bg-green-50 text-green-700' : 'bg-maroon-100 text-maroon-700'}`}>
                          {log.status === "Verified Match" ? 'Physical Match' : 'Mismatch'}
                        </span>
                        <span className="text-[9px] text-indigo-500/80 block mt-1">{new Date(log.timestamp).toLocaleDateString()}</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <>
                    <div className="flex items-center justify-between border-b border-sand-100 pb-3">
                      <div className="flex items-center space-x-3">
                        <div className="h-8 w-8 rounded-lg bg-green-50 text-green-700 border border-green-200 flex items-center justify-center text-xs font-semibold">
                          98.4%
                        </div>
                        <div>
                          <span className="text-xs font-semibold text-indigo-900 block">Scan verified on iPhone 15 Pro</span>
                          <span className="text-[10px] text-indigo-500 flex items-center space-x-1 mt-0.5">
                            <MapPin className="h-3 w-3" />
                            <span>Chennai, Tamil Nadu</span>
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="text-[10px] px-2 py-0.5 bg-green-50 text-green-700 rounded-full font-bold uppercase tracking-wider">
                          Physical Match
                        </span>
                        <span className="text-[9px] text-indigo-500/80 block mt-1">2026-07-13</span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="h-8 w-8 rounded-lg bg-green-50 text-green-700 border border-green-200 flex items-center justify-center text-xs font-semibold">
                          97.9%
                        </div>
                        <div>
                          <span className="text-xs font-semibold text-indigo-900 block">Scan verified on Samsung Galaxy S24</span>
                          <span className="text-[10px] text-indigo-500 flex items-center space-x-1 mt-0.5">
                            <MapPin className="h-3 w-3" />
                            <span>Mumbai, Maharashtra</span>
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="text-[10px] px-2 py-0.5 bg-green-50 text-green-700 rounded-full font-bold uppercase tracking-wider">
                          Physical Match
                        </span>
                        <span className="text-[9px] text-indigo-500/80 block mt-1">2026-07-15</span>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar Widgets (Artisan & Recent Activity) */}
          <div className="space-y-6">
            <div className="luxury-card p-6 bg-white border-l-4 border-l-maroon-600">
              <h3 className="font-serif text-lg font-medium text-indigo-900 mb-4 flex items-center space-x-1.5">
                <Sparkles className="h-5 w-5 text-gold-500" />
                <span>Featured Weaver</span>
              </h3>
              
              <div className="text-center pt-4">
                <div className="h-20 w-20 rounded-full bg-sand-300 border border-gold-500/30 overflow-hidden mx-auto flex items-center justify-center text-3xl font-serif text-indigo-900 shadow-inner">
                  LD
                </div>
                <h4 className="font-serif text-lg font-medium text-indigo-900 mt-4">Lakshmi Devi</h4>
                <p className="text-xs text-maroon-700 font-semibold uppercase tracking-wider mt-1">Master Weaver</p>
                <p className="text-[10px] text-indigo-500/80 mt-0.5">Kanchipuram cooperative • 28 yrs exp</p>
                
                <div className="bg-sand-100 p-3 rounded-lg border border-sand-200 text-[11px] text-indigo-800 leading-relaxed mt-6 italic text-left">
                  "This specific saree, featuring Peacock (Mayil) and Chariot (Chakram) motifs, took over a month of dedicated weaving. My cooperative has verified this as authentic, pure handloom silk."
                </div>
              </div>
            </div>

            <div className="luxury-card p-6 bg-white">
              <h3 className="font-serif text-lg font-medium text-indigo-900 mb-4 flex items-center space-x-1.5">
                <Clock className="h-5 w-5 text-indigo-600" />
                <span>Recent System Logs</span>
              </h3>
              
              <div className="space-y-4">
                {(stats.recent_activity.length > 0 ? stats.recent_activity : [
                  { id: 1, type: "Weaver Registered", weaver: "Lakshmi Devi", details: "Kanchipuram Coop", time: "3 hours ago" },
                  { id: 2, type: "Passport Generated", weaver: "Lakshmi Devi", details: "Craft: CRFT-842193", time: "5 hours ago" },
                  { id: 3, type: "Customer Scan", weaver: "Lakshmi Devi", details: "Verified Match (98.4%)", time: "1 day ago" }
                ]).map((act: any) => (
                  <div key={act.id} className="flex items-start space-x-3 text-xs">
                    <div className="h-2 w-2 rounded-full bg-gold-500 mt-1.5" />
                    <div>
                      <strong className="text-indigo-900 block font-medium">{act.type}</strong>
                      <span className="text-[10px] text-indigo-600/70 block mt-0.5">{act.weaver} • {act.details}</span>
                      <span className="text-[9px] text-indigo-400 block mt-0.5">{act.time}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
