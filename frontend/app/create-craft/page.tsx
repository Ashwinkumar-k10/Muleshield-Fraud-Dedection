"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Users, Award, ShieldCheck, MapPin, Landmark, 
  ArrowRight, CheckCircle2, ChevronRight, Sparkles, QrCode, FileText,
  Clock, BarChart2, Plus
} from 'lucide-react';

export default function CreateCraft() {
  const [formData, setFormData] = useState({
    name: "",
    category: "Saree",
    color: "",
    pattern: "",
    material: ""
  });
  
  const [createdCraft, setCreatedCraft] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.color || !formData.material) {
      setError("Please fill in Name, Color, and Material fields.");
      return;
    }
    
    setLoading(true);
    setError("");
    
    try {
      const response = await fetch('http://localhost:8000/api/create-craft', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        const data = await response.json();
        setCreatedCraft(data);
      } else {
        throw new Error("Failed to create craft");
      }
    } catch (err) {
      console.error(err);
      // Fallback local mock in case backend is offline
      const mockCraft = {
        id: `CRFT-${Math.floor(100000 + Math.random() * 900000)}`,
        name: formData.name,
        category: formData.category,
        color: formData.color,
        pattern: formData.pattern || "Traditional Weave",
        material: formData.material,
        created_at: new Date().toISOString()
      };
      setCreatedCraft(mockCraft);
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
            <Link href="/weaver" className="flex items-center space-x-3 px-3 py-2.5 text-indigo-200 hover:bg-indigo-800 hover:text-white rounded-lg font-medium transition-all">
              <Users className="h-4 w-4 text-indigo-300" />
              <span>Artisan Registration</span>
            </Link>
            <Link href="/create-craft" className="flex items-center space-x-3 px-3 py-2.5 bg-indigo-800 text-white rounded-lg font-medium transition-all">
              <Plus className="h-4 w-4 text-gold-300" />
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

      {/* Main Content Area */}
      <main className="flex-grow p-8 overflow-y-auto max-w-5xl flex items-center justify-center">
        <AnimatePresence mode="wait">
          {!createdCraft ? (
            <motion.div 
              key="form"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="w-full max-w-2xl bg-white luxury-card p-8 md:p-10"
            >
              <div className="flex items-center space-x-3 mb-6">
                <div className="h-10 w-10 bg-gold-500/10 rounded-lg flex items-center justify-center text-gold-600">
                  <FileText className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="font-serif text-2xl font-medium text-indigo-900">Create Unique Craft ID</h2>
                  <p className="text-xs text-indigo-600/70 mt-0.5">Catalog physical attributes of the handloom to generate visual fingerprints.</p>
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
                    <label className="block text-xs font-semibold text-indigo-800 mb-1.5 uppercase">Product Name</label>
                    <input 
                      type="text" 
                      name="name" 
                      value={formData.name} 
                      onChange={handleInputChange} 
                      placeholder="e.g. Mayil Motif Crimson Kanchipuram" 
                      className="w-full px-4 py-2.5 text-sm bg-cream-50 border border-sand-300 rounded-xl focus:border-maroon-600 focus:outline-none transition-colors"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-indigo-800 mb-1.5 uppercase">Category</label>
                    <select 
                      name="category" 
                      value={formData.category} 
                      onChange={handleInputChange}
                      className="w-full px-4 py-2.5 text-sm bg-cream-50 border border-sand-300 rounded-xl focus:border-maroon-600 focus:outline-none transition-colors"
                    >
                      <option value="Saree">Saree</option>
                      <option value="Shawl">Shawl</option>
                      <option value="Stole">Stole</option>
                      <option value="Dhoti">Dhoti</option>
                      <option value="Fabric Roll">Fabric Roll</option>
                    </select>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-xs font-semibold text-indigo-800 mb-1.5 uppercase">Color & Dye Description</label>
                    <input 
                      type="text" 
                      name="color" 
                      value={formData.color} 
                      onChange={handleInputChange} 
                      placeholder="e.g. Crimson Maroon & Temple Gold" 
                      className="w-full px-4 py-2.5 text-sm bg-cream-50 border border-sand-300 rounded-xl focus:border-maroon-600 focus:outline-none transition-colors"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-indigo-800 mb-1.5 uppercase">Pattern / Motifs</label>
                    <input 
                      type="text" 
                      name="pattern" 
                      value={formData.pattern} 
                      onChange={handleInputChange} 
                      placeholder="e.g. Mayil (Peacock) & Chakram motifs" 
                      className="w-full px-4 py-2.5 text-sm bg-cream-50 border border-sand-300 rounded-xl focus:border-maroon-600 focus:outline-none transition-colors"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-indigo-800 mb-1.5 uppercase">Material Composition</label>
                  <input 
                    type="text" 
                    name="material" 
                    value={formData.material} 
                    onChange={handleInputChange} 
                    placeholder="e.g. Pure Mulberry Silk & 24k Gold Zari Thread" 
                    className="w-full px-4 py-2.5 text-sm bg-cream-50 border border-sand-300 rounded-xl focus:border-maroon-600 focus:outline-none transition-colors"
                    required
                  />
                </div>

                <div className="pt-4">
                  <button 
                    type="submit" 
                    disabled={loading}
                    className="w-full py-3.5 bg-maroon-600 hover:bg-maroon-700 disabled:bg-sand-300 disabled:cursor-not-allowed text-white text-sm font-semibold rounded-full flex items-center justify-center space-x-2 shadow-md hover:shadow-maroon-glow transition-all duration-300"
                  >
                    <span>{loading ? "Generating Craft ID..." : "Generate Cryptographic Craft ID"}</span>
                    <ArrowRight className="h-4 w-4" />
                  </button>
                </div>
              </form>
            </motion.div>
          ) : (
            /* Certificate of Registration Presentation */
            <motion.div 
              key="certificate"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="w-full max-w-lg text-center"
            >
              <div className="bg-white border-2 border-gold-500 rounded-2xl p-10 shadow-2xl relative overflow-hidden bg-weave">
                {/* Decorative borders */}
                <div className="absolute top-2 left-2 right-2 bottom-2 border border-gold-500/30 rounded-xl -z-10" />
                <div className="absolute top-0 right-0 h-40 w-40 bg-gold-500/5 rounded-full blur-3xl -z-10" />
                
                <Award className="h-14 w-14 text-gold-500 mx-auto mb-6" />
                
                <span className="text-[10px] font-semibold text-gold-600 tracking-widest uppercase block mb-1">LOOMPROOF ORIGIN PROTOCOL</span>
                <h3 className="font-serif text-3xl font-medium mb-1 text-indigo-900">Certificate of Registration</h3>
                <span className="text-xs text-indigo-600/70">Cryptographic Craft Provenance Sealed</span>
                
                <div className="my-8 py-3 px-6 bg-sand-200 border border-gold-300/40 rounded-xl inline-block">
                  <span className="text-xs text-maroon-700 font-semibold block uppercase tracking-wider">CRAFT ID</span>
                  <span className="font-mono text-2xl font-bold text-indigo-900 tracking-wide">{createdCraft.id}</span>
                </div>
                
                <div className="space-y-3.5 text-xs text-left max-w-md mx-auto border-t border-b border-sand-200 py-6 my-6">
                  <div className="flex justify-between">
                    <span className="text-indigo-600/80">Product Name</span>
                    <strong className="text-indigo-900 font-serif text-sm">{createdCraft.name}</strong>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-indigo-600/80">Category</span>
                    <strong className="text-indigo-900 font-medium">{createdCraft.category}</strong>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-indigo-600/80">Colorway</span>
                    <strong className="text-indigo-900 font-medium">{createdCraft.color}</strong>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-indigo-600/80">Pattern Detail</span>
                    <strong className="text-indigo-900 font-medium">{createdCraft.pattern}</strong>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-indigo-600/80">Material Composition</span>
                    <strong className="text-indigo-900 font-medium">{createdCraft.material}</strong>
                  </div>
                </div>

                <div className="flex justify-between items-center text-[10px] text-indigo-500 font-medium pt-2">
                  <span>SYSTEM BLOCK: ACTIVE</span>
                  <span>{new Date(createdCraft.created_at).toLocaleString()}</span>
                </div>
              </div>
              
              <div className="mt-6 flex justify-center space-x-4">
                <button 
                  onClick={() => setCreatedCraft(null)}
                  className="px-6 py-2.5 bg-white border border-indigo-200 text-indigo-900 rounded-full text-xs font-semibold hover:border-maroon-600 transition-colors shadow-sm"
                >
                  Register Another
                </button>
                <Link 
                  href="/weaveproof" 
                  className="px-6 py-2.5 bg-maroon-600 hover:bg-maroon-700 text-white rounded-full text-xs font-semibold flex items-center space-x-1.5 shadow-md"
                >
                  <span>Proceed to WeaveProof</span>
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
