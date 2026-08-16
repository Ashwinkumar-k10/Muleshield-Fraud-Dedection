"use client";

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Award, ShieldCheck, MapPin, Landmark, 
  Clock, QrCode, FileText, Sparkles, Mic, Play, Pause,
  Languages, Globe, BookOpen, User, CheckCircle2, ChevronRight
} from 'lucide-react';

export default function DigitalPassport({ params }: { params: any }) {
  // Handle both Promise params (Next.js 15 App router standard) and standard object
  const unwrappedParams = params && (params instanceof Promise || typeof params.then === 'function') ? (React.use(params) as any) : params;
  const craftId = (unwrappedParams && unwrappedParams.craftId) || "CRFT-842193";

  const [passportData, setPassportData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
  // Passport Cover Flip State
  const [isFlipped, setIsFlipped] = useState(false);
  
  // Audio Player State
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeTab, setActiveTab] = useState<"English" | "Hindi" | "Tamil">("English");
  const waveRef = useRef<HTMLCanvasElement | null>(null);
  const animationRef = useRef<number | null>(null);

  useEffect(() => {
    async function fetchPassport() {
      try {
        const res = await fetch(`http://localhost:8000/api/get-passport/${craftId}`);
        if (res.ok) {
          const data = await res.json();
          setPassportData(data);
        } else {
          throw new Error("Passport not found");
        }
      } catch (err) {
        console.error(err);
        // Fallback local mock data
        setPassportData({
          passport: {
            craft_id: craftId,
            weaver_id: "WVR-849201",
            origin_verification: {
              status: "Verified",
              level: "Attested",
              attestor: "Kanchipuram Silk Handloom Cooperative",
              date: "2026-06-01T10:00:00Z"
            },
            weave_proof: {
              status: "Verified",
              continuity_score: 96.8,
              color_consistency: 97.5,
              texture_progression: "PASS",
              details: "Weave continuity verified across Start, Mid, and Finish checkpoints with physical consistency established."
            },
            product_proof: {
              status: "FabricPrint Matched",
              fingerprint_id: "PRNT-8942A1",
              physical_consistency: "Established",
              keypoints_extracted: 284
            },
            qr_code_data: `https://loomproof.org/verify/${craftId}`,
            status: "Passport Active",
            issued_at: "2026-07-12T12:30:00Z"
          },
          weaver: {
            id: "WVR-849201",
            name: "Lakshmi Devi",
            photo: "/images/weaver_lakshmi.jpg",
            village: "Kanchipuram",
            state: "Tamil Nadu",
            cooperative: "Kanchipuram Silk Handloom Cooperative",
            craft: "Double-Height Zari Border Silk Saree",
            experience: "28 Years",
            languages: ["Tamil", "Hindi", "English"],
            verification_status: "Verified"
          },
          product: {
            id: craftId,
            name: "Mayil Motif Crimson Kanchipuram Silk",
            category: "Saree",
            color: "Crimson Maroon & Temple Gold",
            pattern: "Mayil (Peacock) & Chakram motifs",
            material: "Pure Mulberry Silk & 24k Gold Zari Thread",
            created_at: "2026-06-01T09:00:00Z"
          },
          checkpoints: {
            start: {
              image: "/api/storage/CRFT-842193_start.png",
              timestamp: "2026-06-15T09:12:00Z",
              challenge: "Place today's gold token marker beside the loom border",
              gps: "12.8342 N, 79.7036 E"
            },
            mid: {
              image: "/api/storage/CRFT-842193_mid.png",
              timestamp: "2026-06-28T14:30:00Z",
              challenge: "Place a coin on the central peacock diamond motif",
              gps: "12.8341 N, 79.7035 E"
            },
            finish: {
              image: "/api/storage/CRFT-842193_finish.png",
              timestamp: "2026-07-12T11:45:00Z",
              challenge: "Capture border section only with weaver badge",
              gps: "12.8343 N, 79.7036 E"
            }
          },
          story: {
            original_audio_text: "En per Lakshmi. Naan 28 varushama intha kanchipuram pattu saree neiyaren. Intha mayil chakram motif neiyave oru maasam aachu. Enoda cooperative idhu rumba nalla pure silk nu verify panni irukanga.",
            translated_story: {
              English: "My name is Lakshmi. I have been weaving Kanchipuram silk sarees for 28 years. This specific saree, featuring Peacock (Mayil) and Chariot (Chakram) motifs, took over a month of dedicated weaving. My cooperative has verified this as authentic, pure handloom silk.",
              Hindi: "मेरा नाम लक्ष्मी है। मैं २८ वर्षों से कांचीपुरम रेशम की साड़ियों की बुनाई कर रही हूँ। मयूर (मयिल) और रथ (चक्रम) रूपांकनों वाली इस विशेष साड़ी को बुनने में एक महीने से अधिक का समय लगा। मेरी सहकारी समिति ने इसे प्रामाणिक, शुद्ध हथकरघा रेशम के रूप में सत्यापित किया है।",
              Tamil: "என் பெயர் லட்சுமி. நான் 28 வருடமாக இந்த காஞ்சிபுரம் பட்டு சேலை நெய்கிறேன். இந்த மயில் மற்றும் சக்கரம் உருவங்கள் நெய்யவே ஒரு மாதத்திற்கு மேல் ஆனது. எங்கள் கூட்டுறவு சங்கம் இதனை தூய பட்டு என்று சான்றளித்துள்ளது."
            },
            ai_summary: "Hand-woven over 34 days by master weaver Lakshmi Devi using pure mulberry silk and gold zari thread. Showcases classical Kanchipuram temple iconography with verified cooperative attestation."
          }
        });
      } finally {
        setLoading(false);
      }
    }
    fetchPassport();
  }, [craftId]);

  // SpeechSynthesis audio playback hook
  useEffect(() => {
    if (typeof window === "undefined" || !window.speechSynthesis) return;

    if (!isPlaying) {
      window.speechSynthesis.cancel();
      return;
    }

    if (!passportData || !passportData.story) return;

    const storyText = passportData.story.translated_story?.[activeTab] || passportData.story.translated_story?.English;
    if (!storyText) return;

    window.speechSynthesis.cancel(); // Stop any current speech first
    const utterance = new SpeechSynthesisUtterance(storyText);
    
    const langMap = {
      English: "en-IN",
      Hindi: "hi-IN",
      Tamil: "ta-IN"
    };
    utterance.lang = langMap[activeTab];

    const voices = window.speechSynthesis.getVoices();
    const voice = voices.find(v => v.lang.startsWith(langMap[activeTab]));
    if (voice) {
      utterance.voice = voice;
    }

    utterance.onend = () => setIsPlaying(false);
    utterance.onerror = () => setIsPlaying(false);

    window.speechSynthesis.speak(utterance);

    return () => {
      window.speechSynthesis.cancel();
    };
  }, [isPlaying, activeTab, passportData]);

  // Audio wave visualization simulation
  useEffect(() => {
    if (!isPlaying) {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
      return;
    }

    const canvas = waveRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = canvas.width = 400;
    let height = canvas.height = 60;
    
    let phase = 0;

    const drawWave = () => {
      ctx.clearRect(0, 0, width, height);
      ctx.strokeStyle = '#D4AF37'; // gold
      ctx.lineWidth = 2.5;
      
      // Draw a luxurious multi-layered sine wave
      for (let layer = 0; layer < 3; layer++) {
        ctx.beginPath();
        const amplitude = 12 - layer * 3;
        const speed = 0.08 + layer * 0.02;
        
        ctx.strokeStyle = layer === 0 ? 'rgba(212, 175, 55, 0.9)' : (layer === 1 ? 'rgba(128, 0, 32, 0.4)' : 'rgba(42, 59, 92, 0.2)');
        
        for (let x = 0; x < width; x++) {
          const y = height / 2 + Math.sin(x * 0.03 + phase * speed) * amplitude * Math.sin(x * Math.PI / width);
          if (x === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.stroke();
      }
      phase += 1;
      animationRef.current = requestAnimationFrame(drawWave);
    };

    drawWave();

    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
  }, [isPlaying]);

  if (loading) {
    return (
      <div className="min-h-screen bg-cream-50 flex items-center justify-center">
        <div className="text-center space-y-4 animate-pulse">
          <div className="h-10 w-10 bg-maroon-600 rounded-full mx-auto" />
          <span className="text-xs font-semibold text-indigo-900 tracking-widest uppercase">Sealing Digital Passport Data...</span>
        </div>
      </div>
    );
  }

  const { passport, weaver, product, checkpoints, story } = passportData;

  return (
    <div className="min-h-screen bg-cream-50 bg-weave py-16 px-6 relative">
      <div className="max-w-4xl mx-auto">
        
        {/* Top bar back link */}
        <div className="flex justify-between items-center mb-10">
          <Link href="/dashboard" className="text-xs font-semibold text-indigo-900 hover:text-maroon-600 transition-colors uppercase tracking-wider flex items-center space-x-1">
            <span>← Back to Dashboard</span>
          </Link>
          <span className="text-[10px] bg-sand-200 border border-gold-300/40 text-maroon-700 font-bold uppercase px-3 py-1 rounded-full tracking-wider">
            LoomProof Trust Passport
          </span>
        </div>

        {/* 3D PASSPORT COVER - Flip Presentation */}
        <section className="perspective-1000 flex justify-center mb-12">
          <motion.div 
            onClick={() => setIsFlipped(!isFlipped)}
            className="w-full max-w-sm h-[480px] cursor-pointer relative preserve-3d transition-transform duration-700 ease-out"
            style={{ transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)' }}
          >
            {/* FRONT OF PASSPORT CARD COVER */}
            <div className="absolute inset-0 bg-maroon-800 border-2 border-gold-500 rounded-2xl p-8 flex flex-col justify-between backface-hidden shadow-2xl text-cream-50">
              <div className="absolute top-2 left-2 right-2 bottom-2 border border-gold-500/20 rounded-xl" />
              <div className="absolute top-0 right-0 h-40 w-40 bg-gold-500/5 rounded-full blur-3xl" />
              
              <div className="text-center space-y-2 mt-4">
                <span className="text-[9px] font-bold text-gold-300 tracking-[0.2em] uppercase">OFFICIAL TRUST PASSPORT</span>
                <h2 className="font-serif text-3xl font-medium tracking-wide">LOOMPROOF ORIGIN</h2>
                <div className="h-0.5 w-16 bg-gold-500 mx-auto mt-2" />
              </div>
              
              <div className="my-10 flex flex-col items-center">
                <Award className="h-20 w-20 text-gold-500" />
                <span className="text-[10px] text-gold-300 font-semibold tracking-wider uppercase mt-4">Evidence-Based Authenticity</span>
              </div>
              
              <div className="flex justify-between items-end border-t border-gold-500/30 pt-6 mb-4 text-[10px] text-gold-300/80">
                <div>
                  <span className="block font-mono">ID: {passport.craft_id}</span>
                  <span className="block mt-0.5 font-medium uppercase">{product.category}</span>
                </div>
                <div className="text-right">
                  <span className="block font-bold">CLICK TO FLIP OPEN</span>
                  <span className="block mt-0.5">ESTABLISHED 2026</span>
                </div>
              </div>
            </div>

            {/* BACK OF PASSPORT CARD / DATA WINDOW */}
            <div 
              className="absolute inset-0 bg-white border-2 border-gold-500 rounded-2xl p-8 flex flex-col justify-between backface-hidden shadow-2xl text-indigo-900"
              style={{ transform: 'rotateY(180deg)' }}
            >
              <div className="absolute top-2 left-2 right-2 bottom-2 border border-gold-500/10 rounded-xl -z-10" />
              
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-[9px] font-bold text-maroon-700 tracking-wider uppercase block">LOOMPROOF TRUST PROTOCOL</span>
                  <h3 className="font-serif text-xl font-medium mt-0.5 text-indigo-900">{product.name}</h3>
                </div>
                <QrCode className="h-10 w-10 text-indigo-950 shrink-0" />
              </div>

              <div className="grid grid-cols-2 gap-4 text-xs mt-6">
                <div className="border-b border-sand-100 pb-2">
                  <span className="text-indigo-600/70 block text-[10px]">Artisan Weaver</span>
                  <strong className="text-indigo-950">{weaver.name}</strong>
                </div>
                <div className="border-b border-sand-100 pb-2">
                  <span className="text-indigo-600/70 block text-[10px]">Cooperative</span>
                  <strong className="text-indigo-950 truncate block">{weaver.cooperative}</strong>
                </div>
                <div className="border-b border-sand-100 pb-2">
                  <span className="text-indigo-600/70 block text-[10px]">Origin Verified</span>
                  <strong className="text-green-600 flex items-center space-x-1 mt-0.5 font-bold">
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    <span>{passport.origin_verification.level}</span>
                  </strong>
                </div>
                <div className="border-b border-sand-100 pb-2">
                  <span className="text-indigo-600/70 block text-[10px]">Weave Continuity</span>
                  <strong className="text-green-600 flex items-center space-x-1 mt-0.5 font-bold">
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    <span>{passport.weave_proof.continuity_score}% PASS</span>
                  </strong>
                </div>
              </div>

              <div className="bg-sand-200 p-3 rounded-lg border border-gold-300/30 text-[10px] text-indigo-800 leading-relaxed italic mt-4">
                "Verified by OpenCV fingerprint print alignment. Thread-level provenance sealed at source."
              </div>

              <div className="flex justify-between items-center text-[9px] text-indigo-500 pt-4 mt-4 border-t border-sand-200">
                <span>PASSPORT STATUS: ACTIVE</span>
                <span>CLICK TO CLOSE COVER</span>
              </div>
            </div>
          </motion.div>
        </section>

        {/* DETAILS SECTION GRID */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          {/* Timeline journey */}
          <div className="md:col-span-2 space-y-8">
            {/* Weaving Checkpoints Timeline */}
            <div className="bg-white luxury-card p-6 md:p-8">
              <h3 className="font-serif text-xl font-medium text-indigo-900 mb-8 border-b border-sand-100 pb-4">
                Creation Journey Evidence Log
              </h3>
              
              <div className="relative border-l-2 timeline-line pl-8 md:pl-10 ml-4 space-y-10">
                {/* Event 1: Origin */}
                <div className="relative">
                  <div className="absolute -left-12 md:-left-[47px] h-7 w-7 rounded-full bg-gold-500 border border-white flex items-center justify-center text-white text-[10px] font-bold shadow-md">
                    1
                  </div>
                  <div>
                    <h5 className="font-serif font-medium text-indigo-900 text-sm">Weaver Profile Verified</h5>
                    <span className="text-[9px] text-indigo-500/80 block mt-0.5">Date: {new Date(passport.origin_verification.date).toLocaleDateString()}</span>
                    <p className="text-xs text-indigo-600/80 mt-1.5 leading-relaxed">
                      Registered Weaver **{weaver.name}** verified by Kanchipuram Cooperative. ID cards issued with experience of {weaver.experience}.
                    </p>
                  </div>
                </div>

                {/* Event 2: Start Checkpoint */}
                <div className="relative">
                  <div className="absolute -left-12 md:-left-[47px] h-7 w-7 rounded-full bg-maroon-600 border border-white flex items-center justify-center text-white text-[10px] font-bold shadow-md">
                    2
                  </div>
                  <div>
                    <h5 className="font-serif font-medium text-indigo-900 text-sm">Weaving Start Checkpoint Registered</h5>
                    <span className="text-[9px] text-indigo-500/80 block mt-0.5">Date: {new Date(checkpoints.start?.timestamp || "").toLocaleString()}</span>
                    <p className="text-xs text-indigo-600/80 mt-1.5 leading-relaxed">
                      Loom verification complete. Challenge code satisfied: "{checkpoints.start?.challenge}"
                    </p>
                    <span className="text-[9px] text-indigo-500 block mt-1">Geolocation: {checkpoints.start?.gps}</span>
                  </div>
                </div>

                {/* Event 3: Mid Checkpoint */}
                <div className="relative">
                  <div className="absolute -left-12 md:-left-[47px] h-7 w-7 rounded-full bg-maroon-600 border border-white flex items-center justify-center text-white text-[10px] font-bold shadow-md">
                    3
                  </div>
                  <div>
                    <h5 className="font-serif font-medium text-indigo-900 text-sm">Weave Midway Checkpoint Registered</h5>
                    <span className="text-[9px] text-indigo-500/80 block mt-0.5">Date: {new Date(checkpoints.mid?.timestamp || "").toLocaleString()}</span>
                    <p className="text-xs text-indigo-600/80 mt-1.5 leading-relaxed">
                      Visual checks evaluate color consistency. Challenge code satisfied: "{checkpoints.mid?.challenge}"
                    </p>
                    <span className="text-[9px] text-indigo-500 block mt-1">Geolocation: {checkpoints.mid?.gps}</span>
                  </div>
                </div>

                {/* Event 4: Completion */}
                <div className="relative">
                  <div className="absolute -left-12 md:-left-[47px] h-7 w-7 rounded-full bg-green-600 border border-white flex items-center justify-center text-white text-[10px] font-bold shadow-md">
                    4
                  </div>
                  <div>
                    <h5 className="font-serif font-medium text-indigo-900 text-sm">Weave Completion & FabricPrint Locked</h5>
                    <span className="text-[9px] text-indigo-500/80 block mt-0.5">Date: {new Date(checkpoints.finish?.timestamp || "").toLocaleString()}</span>
                    <p className="text-xs text-indigo-600/80 mt-1.5 leading-relaxed">
                      Final fabric inspection. Challenge satisfied: "{checkpoints.finish?.challenge}"
                    </p>
                    <span className="text-[9px] text-indigo-500 block mt-1">Fabric Fingerprint Hash: {passport.product_proof.fingerprint_id}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Weaver Heritage Story */}
            <div className="bg-white luxury-card p-6 md:p-8">
              <h3 className="font-serif text-xl font-medium text-indigo-900 mb-6 flex items-center space-x-2">
                <BookOpen className="h-5 w-5 text-maroon-700" />
                <span>Artisan Heritage Story</span>
              </h3>
              
              {/* Pulse Audio Waveform Simulator */}
              <div className="bg-cream-100 p-4 rounded-xl border border-sand-200/60 mb-6 flex flex-col md:flex-row items-center justify-between">
                <div className="flex items-center space-x-3 mb-4 md:mb-0">
                  <button 
                    onClick={() => setIsPlaying(!isPlaying)}
                    className="h-10 w-10 bg-maroon-600 hover:bg-maroon-700 text-white rounded-full flex items-center justify-center shadow-md transition-all shrink-0"
                  >
                    {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4 ml-0.5" />}
                  </button>
                  <div>
                    <strong className="text-xs font-semibold text-indigo-900 block">Weaver Voice Recording</strong>
                    <span className="text-[10px] text-indigo-500/80 block mt-0.5">Duration: 0:42 • Tamil Original</span>
                  </div>
                </div>
                
                <canvas ref={waveRef} className="h-10 w-full max-w-[280px] bg-white/40 rounded-lg border border-sand-200/30" />
              </div>

              {/* Language Tabs translation */}
              <div className="border-b border-sand-200 flex space-x-4 mb-4 text-xs font-semibold text-indigo-600">
                {(["English", "Hindi", "Tamil"] as const).map((lang) => (
                  <button 
                    key={lang}
                    onClick={() => setActiveTab(lang)}
                    className={`pb-2 border-b-2 transition-all ${activeTab === lang ? 'border-maroon-600 text-maroon-700' : 'border-transparent text-indigo-500 hover:text-indigo-800'}`}
                  >
                    {lang} Translation
                  </button>
                ))}
              </div>

              <div className="text-xs text-indigo-900/90 leading-relaxed italic bg-cream-50 p-4 rounded-xl border border-sand-200/50">
                "{story.translated_story?.[activeTab] || story.translated_story?.English}"
              </div>

              <div className="mt-6 border-t border-sand-100 pt-6">
                <span className="text-[10px] text-maroon-700 font-bold uppercase tracking-wider block mb-1">AI heritage Summary:</span>
                <p className="text-xs text-indigo-800 leading-relaxed">{story.ai_summary}</p>
              </div>
            </div>
          </div>
          
          {/* Sidebar Stats and Weaver Details */}
          <div className="space-y-8">
            {/* Weaver profile widget */}
            <div className="bg-white luxury-card p-6 text-center">
              <div className="h-20 w-20 rounded-full bg-sand-300 border-2 border-gold-500 overflow-hidden mx-auto flex items-center justify-center text-3xl font-serif text-indigo-900 shadow-md">
                LD
              </div>
              <h4 className="font-serif text-lg font-medium text-indigo-900 mt-4">{weaver.name}</h4>
              <p className="text-xs text-maroon-700 font-semibold uppercase tracking-wider mt-1">Cooperative Master Weaver</p>
              
              <div className="mt-6 pt-6 border-t border-sand-100 text-left text-xs space-y-3">
                <div className="flex justify-between">
                  <span className="text-indigo-600/80">Village</span>
                  <span className="text-indigo-900 font-medium">{weaver.village}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-indigo-600/80">Experience</span>
                  <span className="text-indigo-900 font-medium">{weaver.experience}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-indigo-600/80">Specialty</span>
                  <span className="text-indigo-900 font-medium text-right max-w-[150px] truncate">{weaver.craft}</span>
                </div>
              </div>
            </div>

            {/* OpenCV Verification Metrics */}
            <div className="bg-indigo-900 text-cream-50 luxury-card p-6">
              <h4 className="font-serif text-base font-semibold text-white mb-4 border-b border-indigo-800 pb-2">
                CV Verification Metrics
              </h4>
              
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-[10px] text-indigo-300 font-medium uppercase mb-1">
                    <span>Weave Continuity</span>
                    <span>{passport.weave_proof.continuity_score}%</span>
                  </div>
                  <div className="h-1.5 bg-indigo-950 rounded-full overflow-hidden">
                    <div className="h-full bg-gold-500 rounded-full" style={{ width: `${passport.weave_proof.continuity_score}%` }} />
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-[10px] text-indigo-300 font-medium uppercase mb-1">
                    <span>Color Correlation</span>
                    <span>{passport.weave_proof.color_consistency}%</span>
                  </div>
                  <div className="h-1.5 bg-indigo-950 rounded-full overflow-hidden">
                    <div className="h-full bg-maroon-600 rounded-full" style={{ width: `${passport.weave_proof.color_consistency}%` }} />
                  </div>
                </div>

                <div className="pt-4 mt-4 border-t border-indigo-800 space-y-2.5 text-xs text-indigo-200/90 leading-relaxed">
                  <div className="flex justify-between">
                    <span>FabricPrint status</span>
                    <span className="text-gold-300 font-bold uppercase">{passport.product_proof.status}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Visual density</span>
                    <strong className="text-white">{passport.product_proof.keypoints_extracted} points</strong>
                  </div>
                </div>
              </div>
            </div>
            
            {/* QR Scan simulator */}
            <div className="bg-white luxury-card p-6 text-center">
              <QrCode className="h-16 w-16 text-indigo-950 mx-auto mb-4" />
              <h5 className="font-serif font-medium text-sm text-indigo-900">Scan & Verify Offline</h5>
              <p className="text-[10px] text-indigo-600/70 mt-1 max-w-[200px] mx-auto leading-relaxed">
                Scan this code from a mobile device to run the visual matching engine instantly.
              </p>
              
              <div className="mt-4 pt-4 border-t border-sand-100">
                <Link href="/verify" className="inline-flex items-center space-x-1.5 text-xs text-maroon-600 hover:text-maroon-800 font-bold uppercase tracking-wider">
                  <span>Open Scanner Simulator</span>
                  <ChevronRight className="h-4 w-4" />
                </Link>
              </div>
            </div>

          </div>
        </section>

      </div>
      
      {/* 3D Passport Style Flip Animation classes injected */}
      <style jsx global>{`
        .perspective-1000 {
          perspective: 1000px;
        }
        .preserve-3d {
          transform-style: preserve-3d;
        }
        .backface-hidden {
          backface-visibility: hidden;
        }
      `}</style>
    </div>
  );
}
