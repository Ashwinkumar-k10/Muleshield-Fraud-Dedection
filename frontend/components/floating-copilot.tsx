"use client";

import React, { useState, useRef, useEffect } from 'react';
import { MessageSquareCode, X, Send, Sparkles, User, RefreshCw } from 'lucide-react';

interface ChatMessage {
  sender: 'user' | 'copilot';
  text: string;
  timestamp: string;
}

export default function FloatingCopilot() {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      sender: 'copilot',
      text: "Hello! I am your global SecureMaint Copilot. Ask me anything about current machinery status or cyber threats.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputVal, setInputVal] = useState<string>("");
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  const handleSend = async () => {
    if (!inputVal.trim()) return;

    const userMsg: ChatMessage = {
      sender: 'user',
      text: inputVal,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages(prev => [...prev, userMsg]);
    setInputVal("");
    setIsTyping(true);

    try {
      const res = await fetch("http://localhost:8000/api/v1/copilot/chat", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: inputVal })
      });

      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, {
          sender: 'copilot',
          text: data.answer,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }]);
      } else {
        mockAnswer(inputVal);
      }
    } catch (err) {
      mockAnswer(inputVal);
    } finally {
      setIsTyping(false);
    }
  };

  const mockAnswer = (question: string) => {
    const q = question.toLowerCase();
    let reply = "I am processing that request. Please verify connection to the FastAPI backend Gateway service.";
    if (q.includes("health") || q.includes("fail")) {
      reply = "CNC-101 has a minor vibration drift, pump P-302 bearing wear is 17.6% (attention required).";
    } else if (q.includes("cyber") || q.includes("attack")) {
      reply = "No active network spoofing or injections are catalogued inside the cryptography registers.";
    }
    
    setMessages(prev => [...prev, {
      sender: 'copilot',
      text: reply,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }]);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      
      {/* Expanded Chat Box Widget */}
      {isOpen && (
        <div className="w-80 h-96 frosted-card flex flex-col justify-between mb-4 border border-cyan-500/25 shadow-lg shadow-cyan-900/10 overflow-hidden animate-pulse-slow">
          
          {/* Header Panel */}
          <div className="p-4 bg-slate-900/80 border-b border-slate-800/60 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-400 animate-pulse" />
              <span className="text-xs font-bold text-slate-200">AI Copilot Core</span>
            </div>
            <button 
              onClick={() => setIsOpen(false)}
              className="p-1 rounded text-slate-500 hover:text-slate-300 hover:bg-slate-800/50 transition-all"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Messages Flow Area */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3.5 scrollbar-thin text-[11px] select-text">
            {messages.map((m, idx) => {
              const isCopilot = m.sender === 'copilot';
              return (
                <div key={idx} className={`flex gap-2 max-w-[85%] ${isCopilot ? 'mr-auto' : 'ml-auto flex-row-reverse text-right'}`}>
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center border flex-shrink-0 ${
                    isCopilot 
                      ? 'bg-cyan-500/10 border-cyan-500/20 text-cyan-400'
                      : 'bg-slate-800 border-slate-700 text-slate-300'
                  }`}>
                    {isCopilot ? <Sparkles className="w-3 h-3" /> : <User className="w-3 h-3" />}
                  </div>
                  
                  <div className={`p-2.5 rounded-xl ${
                    isCopilot 
                      ? 'bg-slate-900/90 border border-slate-850 text-slate-300'
                      : 'bg-cyan-500 text-slate-950 font-semibold'
                  }`}>
                    <p className="leading-relaxed whitespace-pre-wrap">{m.text}</p>
                    <span className={`text-[8px] font-bold block mt-1 uppercase tracking-wider ${
                      isCopilot ? 'text-slate-500' : 'text-slate-900/40'
                    }`}>
                      {m.timestamp}
                    </span>
                  </div>
                </div>
              );
            })}
            {isTyping && (
              <div className="flex gap-2 mr-auto">
                <div className="w-6 h-6 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center animate-pulse">
                  <Sparkles className="w-3 h-3" />
                </div>
                <div className="p-2.5 bg-slate-900/90 border border-slate-850 rounded-xl text-slate-500 text-[10px] flex items-center gap-1.5">
                  <span className="w-1 h-1 rounded-full bg-cyan-400 animate-ping"></span>
                  <span>Copilot typing...</span>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input Box Panel */}
          <div className="p-3 bg-slate-950/80 border-t border-slate-800/60 flex gap-2">
            <input
              type="text"
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask Copilot..."
              className="flex-1 px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-[10px] text-slate-200 focus:outline-none focus:border-cyan-500/45 focus:ring-1 focus:ring-cyan-500/15"
            />
            <button
              onClick={handleSend}
              className="p-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 flex items-center justify-center transition-all"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>

        </div>
      )}

      {/* Circular floating toggle button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-14 h-14 rounded-full bg-gradient-to-tr from-cyan-400 to-emerald-500 text-slate-950 shadow-xl shadow-cyan-500/20 flex items-center justify-center hover:scale-105 transition-all duration-300 border border-cyan-300/30 group"
      >
        <MessageSquareCode className="w-6 h-6 transition-transform group-hover:rotate-12" />
      </button>

    </div>
  );
}
