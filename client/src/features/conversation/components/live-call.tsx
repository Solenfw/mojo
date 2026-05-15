import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  X,
  Mic,
  MicOff,
  Video,
  VideoOff,
  PhoneOff,
  MessageSquare,
  Timer,
  Signal,
  MoreVertical,
  Send,
  Construction
} from 'lucide-react';
import { Button } from '@/components/ui/button';

export const LiveCall = ({ onBack }: { onBack: () => void }) => {
  const [micOn, setMicOn] = useState(true);
  const [videoOn, setVideoOn] = useState(true);

  return (
    <div className="fixed inset-0 h-screen bg-[#0F172A] flex flex-col font-sans z-100 text-white">
      {/* Video Canvas */}
      <div className="flex-1 relative flex items-center justify-center overflow-hidden">

        {/* Placeholder for Remote Video */}
        <div className="absolute inset-0 z-0">
          <img
            src="https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&q=80&w=1000"
            alt="Instructor"
            className="w-full h-full object-cover opacity-60"
          />
        </div>

        {/* Overlay Info */}
        <div className="absolute top-0 left-0 w-full p-8 flex justify-between items-start z-20">
           <div className="space-y-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-red-600 rounded-full text-[10px] font-black uppercase tracking-widest shadow-lg">
                <span className="w-1.5 h-1.5 bg-white rounded-full animate-pulse" />
                Live
              </div>
              <h2 className="text-3xl font-black tracking-tight drop-shadow-2xl">Advanced Business Japanese</h2>
           </div>

           <div className="hidden md:flex gap-4">
              <div className="bg-white/10 backdrop-blur-md px-4 py-2 rounded-2xl flex items-center gap-3 border border-white/5">
                <Timer className="w-4 h-4 text-emerald-400" />
                <span className="text-sm font-bold tracking-tighter">45:00</span>
              </div>
              <div className="bg-white/10 backdrop-blur-md px-4 py-2 rounded-2xl flex items-center gap-3 border border-white/5">
                <Signal className="w-4 h-4 text-emerald-400" />
                <span className="text-sm font-bold tracking-tighter uppercase">Excellent</span>
              </div>
           </div>
        </div>

        {/* Not Implemented Banner */}
        <div className="z-10 bg-white/5 backdrop-blur-xl border border-white/10 p-12 rounded-[40px] text-center max-w-lg mx-4 space-y-6">
           <div className="w-20 h-20 bg-primary rounded-full flex items-center justify-center mx-auto shadow-2xl">
              <Construction className="w-10 h-10 text-white" />
           </div>
           <div className="space-y-2">
              <h3 className="text-3xl font-black tracking-tight">VIP Infrastructure</h3>
              <p className="text-white/60 font-medium">Real-time video streaming is currently being provisioned for your region.</p>
           </div>
           <div className="pt-4 flex items-center justify-center gap-3 text-white/40 text-[10px] uppercase font-black tracking-widest">
              <span className="w-1 h-1 bg-current rounded-full" />
              WebRTC Protected Environment
              <span className="w-1 h-1 bg-current rounded-full" />
           </div>
        </div>

        {/* Self Preview */}
        <div className="absolute bottom-8 right-8 w-64 h-48 bg-gray-900 rounded-4xl border-4 border-white/10 overflow-hidden shadow-2xl z-20 group">
           <img
              src="https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&q=80&w=500"
              alt="Me"
              className="w-full h-full object-cover opacity-80 transition-transform group-hover:scale-105"
           />
           <div className="absolute bottom-4 left-4 px-2 py-1 bg-black/40 backdrop-blur-md rounded-lg text-[8px] font-black uppercase tracking-widest flex items-center gap-1">
              <div className="w-1 h-1 bg-emerald-400 rounded-full" />
              You (Alex)
           </div>
        </div>
      </div>

      {/* Control Bar */}
      <div className="h-32 flex items-center justify-center px-12 bg-linear-to-t from-black to-transparent shrink-0 z-30">
         <div className="bg-white/10 backdrop-blur-2xl border border-white/10 p-4 rounded-full flex items-center gap-6 shadow-2xl">
            <button
              onClick={() => setMicOn(!micOn)}
              className={`w-14 h-14 rounded-full flex items-center justify-center transition-all ${micOn ? 'bg-white/10 hover:bg-white/20' : 'bg-red-600'}`}
            >
              {micOn ? <Mic className="w-6 h-6 text-white" /> : <MicOff className="w-6 h-6 text-white" />}
            </button>

            <button
              onClick={() => setVideoOn(!videoOn)}
              className={`w-14 h-14 rounded-full flex items-center justify-center transition-all ${videoOn ? 'bg-white/10 hover:bg-white/20' : 'bg-red-600'}`}
            >
              {videoOn ? <Video className="w-6 h-6 text-white" /> : <VideoOff className="w-6 h-6 text-white" />}
            </button>

            <div className="w-px h-8 bg-white/10 mx-2" />

            <button className="w-14 h-14 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center transition-all">
               <MessageSquare className="w-6 h-6 text-white" />
            </button>

            <div className="w-px h-8 bg-white/10 mx-2" />

            <button
              onClick={onBack}
              className="h-14 px-8 bg-red-600 hover:bg-red-700 rounded-full flex items-center gap-3 font-black uppercase text-xs tracking-widest transition-all shadow-xl shadow-red-900/40"
            >
              <PhoneOff className="w-5 h-5 fill-white" />
              End Session
            </button>
         </div>
      </div>
    </div>
  );
};