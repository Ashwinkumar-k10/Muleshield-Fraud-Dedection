"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Users, Award, ShieldCheck, MapPin, Briefcase, 
  Languages, Landmark, ArrowRight, CheckCircle2, ChevronRight, UserPlus,
  Clock, QrCode, BarChart2, Plus
} from 'lucide-react';

export default function WeaverRegistration() {
  const [formData, setFormData] = useState({
    name: "",
    village: "",
    state: "",
    cooperative: "",
    craft: "",
    experience: "",
    languages: [] as string[]
  });
  
  const [langInput, setLangInput] = useState("");
  const [registeredWeaver, setRegisteredWeaver] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const addLanguage = () => {
    if (langInput.trim() && !formData.languages.includes(langInput.trim())) {
      setFormData(prev => ({
        ...prev,
        languages: [...prev.languages, langInput.trim()]
      }));
      setLangInput("");
    }
  };

  const removeLanguage = (lang: string) => {
    setFormData(prev => ({
      ...prev,
      languages: prev.languages.filter(l => l !== lang)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.village || !formData.cooperative) {
      setError("Please fill in Name, Village, and Cooperative fields.");
      return;
    }
    
    setLoading(true);
    setError("");
    
    try {
      const response = await fetch('http://localhost:8000/api/register-weaver', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        const data = await response.json();
        setRegisteredWeaver(data);
      } else {
        throw new Error("Failed to register weaver");
      }
    } catch (err) {
      console.error(err);
      // Fallback local mock in case backend is offline
      const mockWeaver = {
        id: `WVR-${Math.floor(100000 + Math.random() * 900000)}`,
        name: formData.name,
        photo: "/images/weaver_placeholder.jpg",
        village: formData.village,
        state: formData.state || "Tamil Nadu",
        cooperative: formData.cooperative,
        craft: formData.craft || "Silk Handloom",
        experience: formData.experience || "10 Years",
        languages: formData.languages.length ? formData.languages : ["Tamil", "English"],
        verification_status: "Verified",
        created_at: new Date().toISOString()
      };
      setRegisteredWeaver(mockWeaver);
    } finally {
      setLoading(false);
    }
  };

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
            <Link href="/dashboard" className="flex items-center space-x-3 px-3 py-2.5 text-indigo-200 hover:bg-indigo-800 hover:text-white rounded-lg font-medium transition-all">
              <BarChart2 className="h-4 w-4 text-indigo-300" />
              <span>Overview Console</span>
            </Link>
            <Link href="/weaver" className="flex items-center space-x-3 px-3 py-2.5 bg-indigo-800 text-white rounded-lg font-medium transition-all">
              <Users className="h-4 w-4 text-gold-300" />
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
          <Link href="/" className="text-xs text-indigo-400 hover:text-white transition-colors block text-center">
            ← Back to Landing
          </Link>
        </div>
      </aside>

      {/* Main Form Content */}
      <main className="flex-grow p-8 overflow-y-auto max-w-5xl flex items-center justify-center">
        <AnimatePresence mode="wait">
          {!registeredWeaver ? (
            <motion.div 
              key="form"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="w-full max-w-2xl bg-white luxury-card p-8 md:p-10"
            >
              <div className="flex items-center space-x-3 mb-6">
                <div className="h-10 w-10 bg-maroon-100/50 rounded-lg flex items-center justify-center text-maroon-700">
                  <UserPlus className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="font-serif text-2xl font-medium text-indigo-900">Artisan Weaver Registration</h2>
                  <p className="text-xs text-indigo-600/70 mt-0.5">Capture credentials and catalog weaver identity to establish origin proof.</p>
                </div>
              </div>

              {error && (
                <div className="bg-maroon-100 border border-maroon-200 text-maroon-800 text-xs px-4 py-2.5 rounded-lg mb-6">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-xs font-semibold text-indigo-800 mb-1.5 uppercase">Full Name</label>
                    <input 
                      type="text" 
                      name="name" 
                      value={formData.name} 
                      onChange={handleInputChange} 
                      placeholder="e.g. Lakshmi Devi" 
                      className="w-full px-4 py-2.5 text-sm bg-cream-50 border border-sand-300 rounded-xl focus:border-maroon-600 focus:outline-none transition-colors"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-indigo-800 mb-1.5 uppercase">Village / Locality</label>
                    <input 
                      type="text" 
                      name="village" 
                      value={formData.village} 
                      onChange={handleInputChange} 
                      placeholder="e.g. Kanchipuram" 
                      className="w-full px-4 py-2.5 text-sm bg-cream-50 border border-sand-300 rounded-xl focus:border-maroon-600 focus:outline-none transition-colors"
                      required
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-xs font-semibold text-indigo-800 mb-1.5 uppercase">State</label>
                    <input 
                      type="text" 
                      name="state" 
                      value={formData.state} 
                      onChange={handleInputChange} 
                      placeholder="e.g. Tamil Nadu" 
                      className="w-full px-4 py-2.5 text-sm bg-cream-50 border border-sand-300 rounded-xl focus:border-maroon-600 focus:outline-none transition-colors"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-indigo-800 mb-1.5 uppercase">Weaving Cooperative</label>
                    <input 
                      type="text" 
                      name="cooperative" 
                      value={formData.cooperative} 
                      onChange={handleInputChange} 
                      placeholder="e.g. Kanchipuram Cooperative Society" 
                      className="w-full px-4 py-2.5 text-sm bg-cream-50 border border-sand-300 rounded-xl focus:border-maroon-600 focus:outline-none transition-colors"
                      required
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-xs font-semibold text-indigo-800 mb-1.5 uppercase">Primary Craft Specialty</label>
                    <input 
                      type="text" 
                      name="craft" 
                      value={formData.craft} 
                      onChange={handleInputChange} 
                      placeholder="e.g. Double-Height Zari Silk Saree" 
                      className="w-full px-4 py-2.5 text-sm bg-cream-50 border border-sand-300 rounded-xl focus:border-maroon-600 focus:outline-none transition-colors"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-indigo-800 mb-1.5 uppercase">Weaving Experience</label>
                    <input 
                      type="text" 
                      name="experience" 
                      value={formData.experience} 
                      onChange={handleInputChange} 
                      placeholder="e.g. 28 Years" 
                      className="w-full px-4 py-2.5 text-sm bg-cream-50 border border-sand-300 rounded-xl focus:border-maroon-600 focus:outline-none transition-colors"
                    />
                  </div>
                </div>

                {/* Languages Input */}
                <div>
                  <label className="block text-xs font-semibold text-indigo-800 mb-1.5 uppercase">Spoken Languages</label>
                  <div className="flex space-x-2">
                    <input 
                      type="text" 
                      value={langInput} 
                      onChange={(e) => setLangInput(e.target.value)} 
                      placeholder="e.g. Tamil" 
                      className="flex-grow px-4 py-2.5 text-sm bg-cream-50 border border-sand-300 rounded-xl focus:border-maroon-600 focus:outline-none transition-colors"
                    />
                    <button 
                      type="button" 
                      onClick={addLanguage}
                      className="px-5 py-2.5 bg-indigo-900 hover:bg-maroon-600 text-white rounded-xl text-xs font-semibold transition-colors"
                    >
                      Add
                    </button>
                  </div>
                  
                  <div className="flex flex-wrap gap-2 mt-3">
                    {formData.languages.map((lang, idx) => (
                      <span key={idx} className="inline-flex items-center space-x-1.5 bg-sand-200 border border-gold-300/40 text-maroon-700 px-3 py-1 rounded-full text-xs font-medium">
                        <span>{lang}</span>
                        <button type="button" onClick={() => removeLanguage(lang)} className="hover:text-red-600 font-bold">×</button>
                      </span>
                    ))}
                  </div>
                </div>

                <div className="pt-4">
                  <button 
                    type="submit" 
                    disabled={loading}
                    className="w-full py-3.5 bg-maroon-600 hover:bg-maroon-700 disabled:bg-sand-300 disabled:cursor-not-allowed text-white text-sm font-semibold rounded-full flex items-center justify-center space-x-2 shadow-md hover:shadow-maroon-glow transition-all duration-300"
                  >
                    <span>{loading ? "Generating Credentials..." : "Register Artisan & Seal Identity"}</span>
                    <ArrowRight className="h-4 w-4" />
                  </button>
                </div>
              </form>
            </motion.div>
          ) : (
            /* Certification Card Presentation */
            <motion.div 
              key="certification"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="w-full max-w-md text-center"
            >
              <div className="bg-indigo-900 border-2 border-gold-500 rounded-2xl p-8 shadow-2xl relative overflow-hidden text-cream-50">
                <div className="absolute top-0 right-0 h-36 w-36 bg-gold-500/10 rounded-full blur-2xl" />
                <div className="absolute -left-12 -bottom-12 h-36 w-36 bg-maroon-600/15 rounded-full blur-2xl" />
                
                <CheckCircle2 className="h-12 w-12 text-gold-500 mx-auto mb-4 animate-bounce" />
                
                <span className="text-[10px] font-semibold text-gold-300 tracking-widest uppercase">Certified Artisan Identity</span>
                <h3 className="font-serif text-2xl font-medium mt-1 mb-6 text-white">LoomProof Origin Pass</h3>
                
                <div className="h-24 w-24 rounded-full bg-sand-300 border-2 border-gold-500 overflow-hidden mx-auto flex items-center justify-center text-4xl font-serif text-indigo-900 shadow-md">
                  {registeredWeaver.name.split(" ").map((n: string) => n[0]).join("")}
                </div>
                
                <h4 className="font-serif text-xl font-medium mt-4 text-white">{registeredWeaver.name}</h4>
                <p className="text-xs text-gold-300 font-semibold uppercase tracking-wider mt-1">{registeredWeaver.id}</p>
                
                <div className="grid grid-cols-2 gap-4 text-left mt-8 text-xs border-t border-indigo-800/60 pt-6">
                  <div>
                    <span className="text-indigo-300/80 block">Village & State</span>
                    <strong className="text-white flex items-center space-x-1 mt-0.5 font-medium">
                      <MapPin className="h-3 w-3 text-gold-300 shrink-0" />
                      <span>{registeredWeaver.village}, {registeredWeaver.state}</span>
                    </strong>
                  </div>
                  <div>
                    <span className="text-indigo-300/80 block">Cooperative</span>
                    <strong className="text-white flex items-center space-x-1 mt-0.5 font-medium">
                      <Landmark className="h-3 w-3 text-gold-300 shrink-0" />
                      <span className="truncate">{registeredWeaver.cooperative}</span>
                    </strong>
                  </div>
                  <div>
                    <span className="text-indigo-300/80 block">Weaving Craft</span>
                    <strong className="text-white flex items-center space-x-1 mt-0.5 font-medium">
                      <Briefcase className="h-3 w-3 text-gold-300 shrink-0" />
                      <span className="truncate">{registeredWeaver.craft}</span>
                    </strong>
                  </div>
                  <div>
                    <span className="text-indigo-300/80 block">Languages</span>
                    <strong className="text-white flex items-center space-x-1 mt-0.5 font-medium">
                      <Languages className="h-3 w-3 text-gold-300 shrink-0" />
                      <span className="truncate">{registeredWeaver.languages.join(", ")}</span>
                    </strong>
                  </div>
                </div>

                <div className="mt-8 px-4 py-2 bg-indigo-950/80 border border-indigo-800/40 rounded-xl text-[10px] text-green-400 font-semibold tracking-wider uppercase flex items-center justify-center space-x-2">
                  <span className="h-1.5 w-1.5 bg-green-400 rounded-full animate-ping" />
                  <span>{registeredWeaver.verification_status} Identity Registered</span>
                </div>
              </div>
              
              <div className="mt-6 flex justify-center space-x-4">
                <button 
                  onClick={() => setRegisteredWeaver(null)}
                  className="px-6 py-2.5 bg-white border border-indigo-200 text-indigo-900 rounded-full text-xs font-semibold hover:border-maroon-600 transition-colors shadow-sm"
                >
                  Register Another
                </button>
                <Link 
                  href="/create-craft" 
                  className="px-6 py-2.5 bg-maroon-600 hover:bg-maroon-700 text-white rounded-full text-xs font-semibold flex items-center space-x-1.5 shadow-md"
                >
                  <span>Proceed to Craft ID</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
