import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  Mic,
  Volume2,
  ChevronLeft,
  Bot,
  User,
  Settings,
  X,
  Play,
  RotateCcw,
  Lightbulb,
  Info,
  ChevronDown
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { GoogleGenAI } from "@google/genai";

// Ensure the API key is handled correctly
const API_KEY = process.env.GEMINI_API_KEY || "";
const genAI = new GoogleGenAI({ apiKey: API_KEY });

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  translation?: string;
  romaji?: string;
  score?: number;
  feedback?: string;
}

export const KaiwaPractice = ({ onBack }: { onBack: () => void }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'いらっしゃいませ。ご注文はお決まりですか？',
      translation: 'Welcome. Have you decided on your order?',
      romaji: 'Irasshaimase. Go-chuumon wa okimari desu ka?'
    }
  ]);
  const [activeMessageId, setActiveMessageId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [lastAnalysis, setLastAnalysis] = useState<{ score: number; text: string; feedback: string } | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (text: string) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Simulate real-time pronunciation analysis for the user message
      const score = Math.floor(Math.random() * 20) + 80;
      setLastAnalysis({
        score,
        text,
        feedback: "Great job! Your pronunciation is clear and natural. Pay attention to the long vowel sounds in 'coffee' for near-perfect results."
      });

      const chat = genAI.models.generateContent({
        model: "gemini-2.5-flash",
        contents: text
      });

      const result = (await chat).text;
      const responseText = result || "申し訳ありませんが、応答を生成できませんでした。";

      const parts = responseText.split('|').map((p: string) => p.trim());

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: parts[0] || responseText,
        romaji: parts[1],
        translation: parts[2]
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error("AI Error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    if (!isRecording) {
      setTimeout(() => {
        setIsRecording(false);
        handleSend("はい、ホットコーヒーを一つお願いします。");
      }, 2000);
    }
  };

  return (
    <div className="fixed inset-0 h-screen bg-[#f7f9fb] flex flex-col font-sans z-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 flex justify-between items-center px-6 h-16 w-full shrink-0">
        <div className="flex items-center gap-4">
          <button onClick={onBack} className="text-gray-500 hover:text-primary transition-colors p-2 rounded-full hover:bg-gray-100">
            <X className="w-5 h-5" />
          </button>
          <div className="h-6 w-px bg-gray-200 mx-2"></div>
          <h1 className="text-lg font-bold text-primary tracking-tight">LinguaSphere</h1>
          <span className="hidden md:block text-[10px] font-black uppercase tracking-widest bg-gray-100 px-3 py-1 rounded-full text-gray-500 ml-4">
            KAIWA PRACTICE
          </span>
        </div>
        <div className="flex items-center gap-4">
          <button className="text-gray-500 hover:text-primary p-2 rounded-full hover:bg-gray-100">
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col lg:flex-row w-full overflow-hidden">
        {/* Left Panel: Conversation */}
        <section className="flex-1 flex flex-col bg-white border-r border-gray-100 relative h-full">
          <div className="p-6 border-b border-gray-50 flex flex-col gap-1 shrink-0">
            <h2 className="text-2xl font-black text-primary tracking-tight">Ordering at a Cafe</h2>
            <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Lesson 4 • Casual Conversation</p>
          </div>

          <div className="flex-1 overflow-y-auto p-6 space-y-6 pb-24 no-scrollbar" ref={scrollRef}>
            <div className="space-y-6">
              {messages.map((m, i) => (
                <motion.div
                  key={m.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex gap-4 group"
                >
                  <div className="w-8 shrink-0 flex flex-col items-center">
                    <span className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-[10px] ${
                      m.role === 'assistant' ? 'bg-gray-100 text-gray-500' : 'bg-primary text-white shadow-lg shadow-primary/20'
                    }`}>
                      {i + 1}
                    </span>
                  </div>
                  <div className={`flex-1 rounded-2xl p-5 border transition-all ${
                    m.role === 'assistant'
                    ? 'bg-gray-50 border-gray-100'
                    : 'bg-primary-fixed border-primary/20 ring-2 ring-primary shadow-sm'
                  }`}>
                    <div className="flex items-center gap-2 mb-3">
                      {m.role === 'assistant' ? (
                        <Bot className="w-3.5 h-3.5 text-primary" />
                      ) : (
                        <User className="w-3.5 h-3.5 text-primary" />
                      )}
                      <span className="text-[10px] font-black uppercase tracking-widest text-primary">
                        {m.role === 'assistant' ? 'CLERK' : 'YOU'}
                      </span>
                    </div>
                    <p className="text-3xl font-jp mb-3 leading-tight text-primary">{m.content}</p>
                    <p className="text-sm font-medium text-primary/70 italic">{m.romaji || m.content}</p>
                    <p className="text-xs text-muted-foreground mt-2">{m.translation}</p>
                  </div>
                </motion.div>
              ))}
              {isLoading && (
                <div className="flex gap-4 animate-pulse">
                  <div className="w-8 h-8 bg-gray-100 rounded-full" />
                  <div className="flex-1 h-32 bg-gray-50 rounded-2xl border border-gray-100" />
                </div>
              )}
            </div>
          </div>

          {/* Audio Footer */}
          <div className="absolute bottom-0 left-0 w-full bg-white border-t p-4 px-6 flex items-center gap-4 shadow-[0_-4px_20px_rgba(0,0,0,0.03)] z-10">
            <Button size="icon" className="w-10 h-10 rounded-full bg-primary hover:bg-primary-container">
              <Play className="w-5 h-5 fill-white" />
            </Button>
            <span className="text-[10px] font-bold text-muted-foreground w-12 text-right">0:12</span>
            <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div className="h-full bg-primary w-1/3 rounded-full" />
            </div>
            <span className="text-[10px] font-bold text-muted-foreground w-12">0:45</span>
            <div className="flex items-center gap-2 border-l pl-4 ml-2">
              <Button variant="ghost" size="sm" className="text-[10px] font-bold text-muted-foreground">1.0x</Button>
            </div>
          </div>
        </section>

        {/* Right Panel: Feedback */}
        <section className="flex-1 bg-[#f7f9fb] flex flex-col h-full relative p-8 lg:p-12 overflow-y-auto no-scrollbar">
          <div className="max-w-lg mx-auto w-full space-y-12 py-12">
            {/* Score */}
            <div className="flex justify-center">
              <div className="relative w-48 h-48 flex items-center justify-center">
                <svg className="w-full h-full absolute inset-0 transform -rotate-90" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="45" fill="none" stroke="#E2E8F0" strokeWidth="8" />
                  <motion.circle
                    cx="50" cy="50" r="45" fill="none"
                    stroke="#b52330" strokeWidth="8"
                    strokeLinecap="round"
                    initial={{ strokeDasharray: "282.7", strokeDashoffset: "282.7" }}
                    animate={{ strokeDashoffset: lastAnalysis ? (282.7 - (282.7 * lastAnalysis.score) / 100) : "282.7" }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                  />
                </svg>
                <div className="flex flex-col items-center justify-center bg-white w-36 h-36 rounded-full shadow-lg border border-gray-100">
                  <span className="text-5xl font-black text-[#b52330]">{lastAnalysis?.score || '--'}</span>
                  <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground mt-1">SCORE</span>
                </div>
              </div>
            </div>

            {/* Analysis */}
            <AnimatePresence mode="wait">
              {lastAnalysis ? (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-white rounded-3xl p-8 border border-gray-100 shadow-xl shadow-primary/5 space-y-6"
                >
                  <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground flex items-center gap-2">
                    <Mic className="w-3.5 h-3.5" />
                    Your Pronunciation
                  </h3>
                  <div className="text-3xl font-jp leading-snug flex flex-wrap gap-x-2 gap-y-3 justify-center">
                    {lastAnalysis.text.split(' ').map((word, i) => (
                      <span key={i} className="text-emerald-600 hover:scale-105 transition-transform cursor-pointer border-b-2 border-emerald-100">{word}</span>
                    ))}
                  </div>
                  <div className="p-4 bg-[#f8fafc] rounded-2xl flex items-start gap-4">
                    <div className="p-2 bg-accent/10 rounded-xl">
                      <Lightbulb className="w-5 h-5 text-accent" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-700 leading-relaxed font-medium">{lastAnalysis.feedback}</p>
                    </div>
                  </div>
                </motion.div>
              ) : (
                <div className="bg-white/50 border-2 border-dashed border-gray-200 rounded-3xl p-12 text-center space-y-4">
                   <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto opacity-50">
                      <Mic className="w-8 h-8 text-gray-400" />
                   </div>
                   <p className="text-sm font-bold text-gray-400 uppercase tracking-widest">Awaiting Audio Input...</p>
                </div>
              )}
            </AnimatePresence>

            {/* Visualizer Placeholder */}
            {isRecording && (
               <div className="h-16 flex items-center justify-center gap-1">
                  {[...Array(12)].map((_, i) => (
                    <motion.div
                      key={i}
                      className="w-1.5 bg-accent rounded-full"
                      animate={{ height: [10, 40, 20, 60, 30] }}
                      transition={{ duration: 0.5, repeat: Infinity, delay: i * 0.05 }}
                    />
                  ))}
               </div>
            )}
          </div>

          {/* Controls */}
          <div className="bg-white border-t p-8 flex flex-col items-center justify-center shrink-0">
             <div className="flex items-center gap-12 w-full max-w-md justify-center">
                <button className="flex flex-col items-center gap-2 group">
                  <div className="w-12 h-12 rounded-full border border-gray-200 group-hover:bg-primary-fixed group-hover:border-primary flex items-center justify-center transition-all bg-white">
                    <RotateCcw className="w-5 h-5 text-gray-400 group-hover:text-primary" />
                  </div>
                  <span className="text-[8px] font-black uppercase tracking-widest text-muted-foreground group-hover:text-primary">Listen Again</span>
                </button>

                <button
                  onClick={toggleRecording}
                  className="relative group outline-none"
                >
                  <div className={`absolute inset-0 bg-accent transition-all duration-500 rounded-full ${isRecording ? 'opacity-20 scale-150 animate-ping' : 'opacity-0 scale-110'}`} />
                  <div className={`w-24 h-24 rounded-full flex items-center justify-center shadow-2xl relative z-10 border-4 border-white transition-all ${
                    isRecording ? 'bg-red-600 scale-105' : 'bg-accent hover:bg-accent/90'
                  }`}>
                    <Mic className={`w-10 h-10 fill-white text-white ${isRecording ? 'animate-pulse' : ''}`} />
                  </div>
                </button>

                <button className="flex flex-col items-center gap-2 group">
                  <div className="w-12 h-12 rounded-full border border-gray-200 group-hover:bg-primary-fixed group-hover:border-primary flex items-center justify-center transition-all bg-white">
                    <Volume2 className="w-5 h-5 text-gray-400 group-hover:text-primary" />
                  </div>
                  <span className="text-[8px] font-black uppercase tracking-widest text-muted-foreground group-hover:text-primary">Check Example</span>
                </button>
             </div>
          </div>
        </section>
      </main>
    </div>
  );
};