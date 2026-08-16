"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Users, Award, ShieldCheck, MapPin, Landmark, 
  ArrowRight, CheckCircle2, ChevronRight, QrCode, FileText,
  Clock, Camera, Check, AlertTriangle, ShieldAlert, Cpu,
  HelpCircle, Eye, Navigation, Info, RefreshCw
} from 'lucide-react';

export default function CustomerScanner() {
  const [craftId, setCraftId] = useState("CRFT-842193");
  const [scanning, setScanning] = useState(false);
  const [scanResult, setScanResult] = useState<any>(null);
  const [deviceLocation, setDeviceLocation] = useState("New Delhi, Delhi");
  const [scanTargetType, setScanTargetType] = useState<"authentic" | "fake" | null>(null);

  const triggerScan = async (type: "authentic" | "fake") => {
    setScanning(true);
    setScanTargetType(type);
    setScanResult(null);
    
    // Create form data to match API expectations
    const formData = new FormData();
    formData.append("craft_id", craftId);
    formData.append("device_location", deviceLocation);
    
    let resultPayload: any = null;

    try {
      const fileUrl = type === "authentic" ? `http://localhost:8000/api/storage/${craftId}_finish.png` : `http://localhost:8000/api/storage/${craftId}_fake.png`;
      const fileRes = await fetch(fileUrl);
      const blob = await fileRes.blob();
      const file = new File([blob], type === "authentic" ? "finish.png" : "fake.png", { type: "image/png" });
      formData.append("image", file);
      
      const res = await fetch('http://localhost:8000/api/verify-product', {
        method: 'POST',
        body: formData
      });
      
      if (res.ok) {
        resultPayload = await res.json();
      } else {
        throw new Error();
      }
    } catch (err) {
      console.error("Backend error during scan verify, falling back to client simulation", err);
      // Offline fallback simulations
      if (type === "authentic") {
        resultPayload = {
          status: "Matched",
          similarity_percentage: 98.4,
          title: "Origin Verified. Product Match Confirmed.",
          recommendation: "Product verified successfully",
          reason: "Analyzed 581 vs 581 keypoints. Found 311 close descriptor alignments. Color correlation at 100.0%.",
          visualization: "/api/storage/vis_CRFT-842193.png"
        };
      } else {
        resultPayload = {
          status: "Mismatch",
          similarity_percentage: 0.0,
          title: "Digital Identity Found. Physical Consistency Not Established.",
          recommendation: "Manual Review Recommended",
          reason: "Analyzed 581 vs 963 keypoints. Found 0 close descriptor alignments. Color correlation at 0.0%.",
          visualization: null
        };
      }
    }

    // Force a 3-second delay to show the scanning animation in viewfinder
    await new Promise(resolve => setTimeout(resolve, 3000));
    setScanResult(resultPayload);
    setScanning(false);
  };

  return (
    <div className="min-h-screen bg-cream-50 overflow-hidden bg-weave">
      {/* Top Header */}
      <header className="glass-header px-6 py-4 flex justify-between items-center fixed top-0 left-0 w-full z-50">
        <Link href="/" className="flex items-center space-x-3">
          <div className="h-8 w-8 bg-maroon-600 rounded flex items-center justify-center text-gold-300 font-serif font-bold text-lg">L</div>
          <span className="font-serif font-semibold text-base text-indigo-900 tracking-wide">LoomProof Origin</span>
        </Link>
        <div className="flex space-x-4">
          <Link href="/dashboard" className="px-4 py-2 text-xs font-semibold text-indigo-900 border border-indigo-200 rounded-full hover:border-maroon-600 transition-colors">
            Cooperative Console
          </Link>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-4xl mx-auto pt-28 pb-16 px-6">
        <section className="text-center max-w-2xl mx-auto mb-10">
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="inline-flex items-center space-x-2 bg-maroon-50 border border-maroon-200 text-maroon-700 px-4.5 py-1.5 rounded-full text-xs font-medium mb-6 shadow-sm"
          >
            <ShieldCheck className="h-4 w-4 text-maroon-600 animate-pulse" />
            <span>Anti-Counterfeit Clone Protection Center</span>
          </motion.div>
          
          <h1 className="font-serif text-3xl md:text-5xl font-semibold text-indigo-900">
            Artisanal Clone Protection
          </h1>
          <p className="text-xs md:text-sm text-indigo-600/70 mt-3 leading-relaxed">
            Verify if a physical textile matches its registered digital identity. Counterfeits copying a valid QR code will fail physical consistency checks.
          </p>
        </section>

        <section className="grid md:grid-cols-2 gap-8 items-start">
          {/* Scanner Controls */}
          <div className="bg-white luxury-card p-6 md:p-8 space-y-6">
            <h3 className="font-serif text-lg font-medium text-indigo-900 border-b border-sand-100 pb-3">
              Scanner Simulator
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-[10px] font-semibold text-indigo-800 mb-1.5 uppercase">Simulate QR Scan (Craft ID)</label>
                <input 
                  type="text" 
                  value={craftId} 
                  onChange={(e) => setCraftId(e.target.value)} 
                  className="w-full px-4 py-2.5 text-xs font-mono bg-cream-50 border border-sand-300 rounded-xl focus:border-maroon-600 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-[10px] font-semibold text-indigo-800 mb-1.5 uppercase">Device Verification Geolocation</label>
                <input 
                  type="text" 
                  value={deviceLocation} 
                  onChange={(e) => setDeviceLocation(e.target.value)} 
                  className="w-full px-4 py-2.5 text-xs bg-cream-50 border border-sand-300 rounded-xl focus:border-maroon-600 focus:outline-none"
                />
              </div>
            </div>

            <div className="pt-4 border-t border-sand-100 space-y-4">
              <span className="text-[10px] font-semibold text-indigo-500 uppercase block tracking-wider">Trigger Verification Queries:</span>
              
              <div className="grid grid-cols-2 gap-4">
                <button 
                  onClick={() => triggerScan("authentic")}
                  disabled={scanning}
                  className="py-3 bg-green-50 hover:bg-green-100 border border-green-200 text-green-800 rounded-xl text-xs font-semibold flex flex-col items-center justify-center space-y-1 transition-all"
                >
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                  <span>Scan Authentic Saree</span>
                </button>

                <button 
                  onClick={() => triggerScan("fake")}
                  disabled={scanning}
                  className="py-3 bg-maroon-50 hover:bg-maroon-100 border border-maroon-200 text-maroon-800 rounded-xl text-xs font-semibold flex flex-col items-center justify-center space-y-1 transition-all"
                >
                  <ShieldAlert className="h-5 w-5 text-maroon-600" />
                  <span>Scan Clone/Fake Saree</span>
                </button>
              </div>
            </div>
          </div>

          {/* Live Viewfinder Scanner / Map */}
          <div className="bg-white luxury-card p-6 md:p-8 space-y-6 min-h-[380px] flex flex-col justify-between">
            {scanning ? (
              <div className="flex-grow flex flex-col justify-between">
                <h3 className="font-serif text-lg font-medium text-indigo-900 border-b border-sand-100 pb-3 flex justify-between items-center">
                  <span>Live Keypoint Alignment Viewfinder</span>
                  <span className="text-[9px] bg-maroon-100 text-maroon-700 font-bold px-2 py-0.5 rounded animate-pulse">
                    ANALYZING TEXTURE
                  </span>
                </h3>
                
                {/* Visual Camera Box */}
                <div className="h-52 bg-slate-900 rounded-xl overflow-hidden relative border border-slate-800 flex items-center justify-center mt-4">
                  {/* Camera brackets */}
                  <div className="absolute top-3 left-3 w-4 h-4 border-t-2 border-l-2 border-white/60 rounded-tl z-10" />
                  <div className="absolute top-3 right-3 w-4 h-4 border-t-2 border-r-2 border-white/60 rounded-tr z-10" />
                  <div className="absolute bottom-3 left-3 w-4 h-4 border-b-2 border-l-2 border-white/60 rounded-bl z-10" />
                  <div className="absolute bottom-3 right-3 w-4 h-4 border-b-2 border-r-2 border-white/60 rounded-br z-10" />
                  
                  {/* Fabric under scan */}
                  <div className={`absolute inset-0 transition-all duration-500 opacity-60 ${scanTargetType === 'authentic' ? 'bg-maroon-800' : 'bg-green-800'}`}>
                    {scanTargetType === 'authentic' ? (
                      /* CSS representation of Maroon Gold border */
                      <div className="h-full w-full flex">
                        <div className="w-14 bg-amber-500 border-r-4 border-amber-600 flex flex-col justify-around py-4">
                          <div className="h-4 w-4 rounded-full bg-amber-300 mx-auto" />
                          <div className="h-4 w-4 rounded-full bg-amber-300 mx-auto" />
                          <div className="h-4 w-4 rounded-full bg-amber-300 mx-auto" />
                        </div>
                        <div className="flex-grow bg-weave" style={{ backgroundImage: "repeating-linear-gradient(45deg, #58111A 0px, #58111A 2px, transparent 2px, transparent 10px)" }} />
                      </div>
                    ) : (
                      /* CSS representation of Green Silver stripe */
                      <div className="h-full w-full flex">
                        <div className="w-14 bg-slate-300 border-r-4 border-slate-400 flex flex-col justify-around py-4">
                          <div className="h-1 w-full bg-slate-400" />
                          <div className="h-1 w-full bg-slate-400" />
                          <div className="h-1 w-full bg-slate-400" />
                        </div>
                        <div className="flex-grow bg-weave" style={{ backgroundImage: "repeating-linear-gradient(45deg, #166534 0px, #166534 2px, transparent 2px, transparent 10px)" }} />
                      </div>
                    )}
                  </div>
                  
                  {/* Yellow feature point crosshairs blinking */}
                  <div className="absolute inset-0 pointer-events-none">
                    {Array.from({ length: 15 }).map((_, i) => (
                      <span 
                        key={i} 
                        className="absolute h-2.5 w-2.5 rounded-full border border-yellow-400 bg-yellow-400/40 animate-ping"
                        style={{
                          top: `${20 + (i * 17) % 60}%`,
                          left: `${20 + (i * 29) % 60}%`,
                          animationDelay: `${i * 150}ms`,
                          animationDuration: '1.2s'
                        }}
                      />
                    ))}
                  </div>

                  {/* Scanning glowing green laser line */}
                  <div className="absolute left-0 right-0 h-1 bg-green-400 shadow-[0_0_12px_#34d399] animate-scan-laser z-10" />

                  {/* Scanning Text Overlay */}
                  <div className="absolute bottom-3 left-1/2 -translate-x-1/2 bg-black/70 text-[9px] text-green-400 font-mono px-3 py-1 rounded border border-green-500/30 flex items-center space-x-1.5 uppercase tracking-wider z-10">
                    <span className="h-1.5 w-1.5 bg-green-400 rounded-full animate-ping" />
                    <span className="animate-pulse">Matching descriptors...</span>
                  </div>
                </div>

                <div className="text-[11px] text-indigo-600/70 mt-4 leading-relaxed font-mono text-center">
                  Target: <strong className="text-indigo-950 font-bold">{craftId}</strong> • Scanner active • GPS Sealed
                </div>
              </div>
            ) : (
              <div className="flex-grow flex flex-col justify-between">
                <h3 className="font-serif text-lg font-medium text-indigo-900 border-b border-sand-100 pb-3 flex items-center justify-between">
                  <span>Trust Verification Map</span>
                  <span className="text-[10px] text-indigo-500 flex items-center space-x-1 font-sans uppercase font-bold">
                    <Navigation className="h-3 w-3 text-gold-500" />
                    <span>2 Active nodes</span>
                  </span>
                </h3>
                
                {/* Draw a gorgeous SVG map vector representation of India scans */}
                <div className="h-52 bg-indigo-950 rounded-xl overflow-hidden relative border border-indigo-900 flex items-center justify-center mt-4">
                  <svg className="h-full w-full opacity-30" viewBox="0 0 200 200" fill="none">
                    <path d="M100 20 C70 50, 40 80, 70 120 C80 140, 60 170, 90 190 C110 180, 130 160, 120 140 C140 120, 150 90, 130 60 C120 40, 110 30, 100 20 Z" fill="#D4AF37" stroke="rgba(212, 175, 55, 0.4)" strokeWidth="1" />
                  </svg>
                  
                  {/* Scan point 1: Chennai */}
                  <div className="absolute top-2/3 left-[45%] text-center">
                    <span className="absolute h-3 w-3 bg-green-400 rounded-full animate-ping -left-1" />
                    <span className="absolute h-2 w-2 bg-green-500 rounded-full -left-0.5" />
                    <span className="text-[8px] text-white bg-indigo-900/90 border border-indigo-800 px-1 rounded absolute top-3 -left-6 whitespace-nowrap">
                      Chennai match 98.4%
                    </span>
                  </div>
                  
                  {/* Scan point 2: Mumbai */}
                  <div className="absolute top-[45%] left-1/3 text-center">
                    <span className="absolute h-3 w-3 bg-green-400 rounded-full animate-ping -left-1" />
                    <span className="absolute h-2 w-2 bg-green-500 rounded-full -left-0.5" />
                    <span className="text-[8px] text-white bg-indigo-900/90 border border-indigo-800 px-1 rounded absolute top-3 -left-6 whitespace-nowrap">
                      Mumbai match 97.9%
                    </span>
                  </div>

                  {/* Scan point 3: Delhi (Current scan simulation node) */}
                  {scanResult && (
                    <div className="absolute top-1/3 left-[48%] text-center">
                      <span className={`absolute h-4 w-4 rounded-full animate-ping -left-1.5 ${scanResult.status === "Matched" ? 'bg-green-400' : 'bg-red-400'}`} />
                      <span className={`absolute h-2.5 w-2.5 rounded-full -left-1 ${scanResult.status === "Matched" ? 'bg-green-500' : 'bg-red-500'}`} />
                      <span className="text-[8px] text-white bg-indigo-900/90 border border-indigo-800 px-1 rounded absolute top-4 -left-12 whitespace-nowrap font-bold">
                        {scanResult.status === "Matched" ? 'Delhi VERIFIED (98.4%)' : 'Delhi WARNING (0.0%)'}
                      </span>
                    </div>
                  )}
                  
                  <div className="absolute bottom-2 left-2 text-[9px] text-indigo-300/80">
                    LoomProof Geographic Provenance Tracker
                  </div>
                </div>
                
                <p className="text-xs text-indigo-600/70 leading-relaxed mt-4">
                  Every verification query logs the timestamp, device, and location coordinates to detect anomalies like multiple concurrent scans from differing states.
                </p>
              </div>
            )}
          </div>
        </section>

        {/* Loader placeholder */}

        {/* Scan Result Details */}
        {scanResult && (
          <motion.section 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`luxury-card p-6 md:p-8 mt-8 border-l-4 shadow-xl relative overflow-hidden ${scanResult.status === "Matched" ? 'border-l-green-600 bg-white' : 'border-l-maroon-600 bg-white'}`}
          >
            <div className="flex justify-between items-start border-b border-sand-200 pb-4 mb-6">
              <div>
                <span className="text-[10px] font-semibold text-indigo-600/80 tracking-wider uppercase block">Clone protection scan results</span>
                <h3 className="font-serif text-2xl text-indigo-900 font-medium">{scanResult.title}</h3>
              </div>
              <div className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest ${scanResult.status === "Matched" ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-maroon-100 text-maroon-700 border border-maroon-200'}`}>
                {scanResult.status === "Matched" ? 'VERIFIED MATCH' : 'MISMATCH WARNING'}
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-8 items-center">
              <div>
                <div className="space-y-4 text-xs">
                  <div className="flex justify-between border-b border-sand-100 pb-2">
                    <span className="text-indigo-600/80">Dye & Feature similarity</span>
                    <strong className="text-sm text-indigo-900 font-mono">{scanResult.similarity_percentage}%</strong>
                  </div>
                  <div className="flex justify-between border-b border-sand-100 pb-2">
                    <span className="text-indigo-600/80">Action Recommendation</span>
                    <strong className="text-indigo-950">{scanResult.recommendation}</strong>
                  </div>
                  <div className="flex justify-between pb-2">
                    <span className="text-indigo-600/80">Diagnostic analysis</span>
                    <strong className="text-indigo-950 font-normal text-right max-w-xs">{scanResult.reason}</strong>
                  </div>
                </div>

                {scanResult.status === "Mismatch" && (
                  <div className="bg-maroon-100/50 border border-maroon-200 rounded-xl p-4 text-xs text-maroon-800 mt-6 leading-relaxed flex items-start space-x-2">
                    <AlertTriangle className="h-5 w-5 text-maroon-600 shrink-0 mt-0.5" />
                    <div>
                      <strong className="block mb-0.5 font-bold">Clone Detection Alert:</strong>
                      This duplicate query attempts to resolve using a registered digital QR, but surface descriptors do not align. Counterfeit alert logged.
                    </div>
                  </div>
                )}
              </div>

              {/* Show Side-by-Side Match Drawing if Matched */}
              {scanResult.visualization && (
                <div className="border border-sand-200 rounded-xl overflow-hidden shadow-inner">
                  <span className="text-[9px] bg-indigo-900 text-white px-2 py-1 block font-mono">
                    OpenCV keypoint alignment verification:
                  </span>
                  <img 
                    src={`http://localhost:8000${scanResult.visualization}`} 
                    alt="OpenCV matches visualization"
                    className="w-full object-contain h-48 bg-slate-900"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = "/images/weaver_placeholder.jpg";
                    }}
                  />
                </div>
              )}
            </div>

            {scanResult.status === "Matched" && (
              <div className="mt-8 flex justify-end">
                <Link 
                  href={`/passport/${craftId}`} 
                  className="px-6 py-2.5 bg-indigo-900 hover:bg-maroon-600 text-white text-xs font-semibold rounded-full flex items-center space-x-1 shadow-md"
                >
                  <span>View Full Digital Passport</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>
            )}
          </motion.section>
        )}
      </main>
    </div>
  );
}

/* Local scanner styles for scan animation */
const globalStyles = `
  @keyframes scan-laser {
    0% { top: 0%; }
    50% { top: 100%; }
    100% { top: 0%; }
  }
  .animate-scan-laser {
    position: absolute;
    animation: scan-laser 2.5s infinite ease-in-out;
  }
`;
