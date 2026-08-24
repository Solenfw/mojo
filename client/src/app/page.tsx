'use client';

import React from 'react';
import { motion } from 'motion/react';
import { useRouter } from 'next/navigation';
import { 
  ChevronRight, 
  Globe, 
  Zap, 
  MessageSquare, 
  PenTool, 
  BookOpen,
  ArrowRight,
  Star
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export default function LandingPage() {
  const router = useRouter();

  const handleStart = () => router.push('/signup');
  const handleLogin = () => router.push('/login');

  return (
    <div className="min-h-screen bg-background flex flex-col font-sans">
      {/* Navigation */}
      <nav className="h-20 flex items-center justify-between px-8 md:px-16 sticky top-0 bg-white/80 backdrop-blur-md z-50 border-b border-primary/5">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow-md shadow-primary/10 border border-primary/10 overflow-hidden">
            <img 
              src="/logo.png" 
              alt="Mojo Logo" 
              className="w-8 h-8 object-contain scale-110" 
            />
          </div>
          <span className="text-2xl font-bold tracking-tighter text-primary">Mojo</span>
        </div>
        <div className="hidden md:flex items-center gap-8">
          <a href="#features" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">Features</a>
          <Button variant="ghost" onClick={handleLogin} className="text-sm font-bold text-primary">Sign In</Button>
          <Button onClick={handleStart} className="bg-primary text-white hover:bg-primary/90 px-6 font-bold shadow-lg shadow-primary/20">Get Started</Button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-20 pb-32 overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-250 h-150 bg-primary/5 rounded-full blur-[120px] -z-10"></div>
        <div className="max-w-7xl mx-auto px-8 md:px-16 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="space-y-8 text-center lg:text-left"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-secondary text-primary font-bold text-xs uppercase tracking-widest border border-primary/10 shadow-sm">
              <Star className="w-3 h-3 fill-primary" />
              Revolutionizing Japanese Learning
            </div>
            <h1 className="text-6xl md:text-8xl font-black tracking-tight text-primary leading-[0.9]">
              Master <span className="text-accent animate-pulse">Japanese</span> <br /> 
              with <span className="italic font-serif">Precision.</span>
            </h1>
            <p className="text-xl text-muted-foreground max-w-xl leading-relaxed mx-auto lg:mx-0">
              The premium AI-powered platform for busy professionals. Zero to N5 proficiency through immersive conversation and intelligent feedback.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Button onClick={handleStart} className="h-14 px-8 text-lg bg-primary hover:bg-primary/90 rounded-2xl group shadow-2xl shadow-primary/30">
                Start Learning for Free
                <ChevronRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </div>
            <div className="flex items-center gap-6 justify-center lg:justify-start pt-4">
              <div className="flex -space-x-3">
                {[1,2,3,4].map(i => (
                  <img 
                    key={i}
                    src={`https://api.dicebear.com/7.x/avataaars/svg?seed=user${i}`}
                    className="w-10 h-10 rounded-full border-2 border-white shadow-sm"
                    alt="user"
                  />
                ))}
              </div>
              <p className="text-sm font-medium text-muted-foreground">
                <span className="text-primary font-light">constantly pushing for a larger community of learners and professionals.</span> 
              </p>
            </div>
          </motion.div> 

          {/* Visual Element */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="relative"
          >
            <div className="relative bg-white rounded-[40px] p-8 shadow-2xl border border-primary/5">
              <div className="absolute -top-6 -right-6 w-32 h-32 bg-accent rounded-full flex flex-col items-center justify-center text-white rotate-12 shadow-xl shadow-accent/40 z-10">
                <span className="text-2xl font-black">N5</span>
                <span className="text-[10px] font-bold uppercase tracking-widest">Guaranteed</span>
              </div>
              
              <div className="space-y-6">
                <div className="flex justify-between items-center bg-secondary/30 p-4 rounded-2xl border border-primary/5">
                  <div className="flex gap-3">
                    <div className="w-12 h-12 bg-white rounded-xl shadow-sm flex items-center justify-center">
                      <MessageSquare className="text-primary" />
                    </div>
                    <div>
                      <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Active Skill</p>
                      <p className="font-bold text-primary">Kaiwa (Conversation)</p>
                    </div>
                  </div>
                  <Badge className="bg-emerald-500 text-white border-none">Active</Badge>
                </div>

                <div className="p-6 bg-primary text-white rounded-3xl space-y-4">
                  <p className="text-sm font-jp italic opacity-80">"How to order Sushi in Tokyo?"</p>
                  <p className="text-2xl font-jp font-bold">すいません、中トロを二つください。</p>
                  <div className="flex items-center gap-2 pt-2 border-t border-white/10 text-xs font-medium opacity-60">
                    <Zap className="w-3 h-3 fill-white" />
                    Gemini AI: Pronunciation 98% Accurate
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                   <div className="p-4 border rounded-2xl flex flex-col items-center justify-center gap-2 group hover:border-primary transition-colors cursor-pointer">
                      <PenTool className="text-accent group-hover:scale-110 transition-transform" />
                      <span className="text-xs font-bold text-primary">Kanji Canvas</span>
                   </div>
                   <div className="p-4 border rounded-2xl flex flex-col items-center justify-center gap-2 group hover:border-primary transition-colors cursor-pointer">
                      <Globe className="text-primary group-hover:scale-110 transition-transform" />
                      <span className="text-xs font-bold text-primary">Live Scenarios</span>
                   </div>
                </div>
              </div>
            </div>
            {/* Background elements */}
            <div className="absolute -bottom-10 -left-10 w-48 h-48 bg-accent/10 rounded-full blur-3xl -z-10"></div>
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[120%] h-[120%] border border-primary/5 rounded-full -z-10 rotate-12"></div>
          </motion.div>
        </div>
      </section>

      {/* Trust Bar
      <div className="border-y bg-secondary/20 py-8">
        <div className="max-w-7xl mx-auto px-8 flex flex-wrap justify-center gap-x-16 gap-y-8 items-center grayscale opacity-50">
          <div className="font-black text-xl tracking-tighter">TECHLEARN</div>
          <div className="font-black text-xl tracking-tighter">GLOBAL EDU</div>
          <div className="font-black text-xl tracking-tighter">TOKYO HUB</div>
          <div className="font-black text-xl tracking-tighter">SENSEI NET</div>
        </div>
      </div> */}
      {/* devide line */}
      <div className="border-t border-primary/8"></div>

      {/* Features */}
      <section id="features" className="py-32">
        <div className="max-w-7xl mx-auto px-8 md:px-16 space-y-16">
          <div className="text-center space-y-4">
            <h2 className="text-4xl font-black text-primary tracking-tight">The Professional's Edge</h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">Skip the generic apps. We focus on high-impact language skills needed for the global economy.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { 
                icon: MessageSquare, 
                title: "AI Kaiwa Partner", 
                desc: "Practice endless real-world scenarios with Gemini AI, from business meetings to casual dining.",
                color: "bg-blue-50"
              },
              { 
                icon: PenTool, 
                title: "Intelligent Writing", 
                desc: "Master Kanji with our advanced stroke analyzer. Get instant feedback on balance and precision.",
                color: "bg-red-50"
              },
              { 
                icon: BookOpen, 
                title: "Currated N5 Path", 
                desc: "A surgical curriculum designed to get you JLPT N5 certified in recorded time.",
                color: "bg-emerald-50"
              }
            ].map((f, i) => (
              <Card key={i} className="hover:shadow-xl transition-shadow border-none bg-white p-8 space-y-4 rounded-3xl">
                <div className={`w-12 h-12 ${f.color} rounded-2xl flex items-center justify-center`}>
                  <f.icon className="w-6 h-6 text-primary" />
                </div>
                <h3 className="text-xl font-bold text-primary">{f.title}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">{f.desc}</p>
                <Button variant="link" className="p-0 text-primary font-bold group">
                  Learn more
                  <ArrowRight className="ml-1 w-3 h-3 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-primary text-white py-20">
        <div className="max-w-7xl mx-auto px-8 md:px-16 grid grid-cols-1 md:grid-cols-4 gap-12 border-b border-white/10 pb-16">
          <div className="space-y-6">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow-md shadow-primary/10 border border-primary/10 overflow-hidden">
                <img 
                  src="/logo.png" 
                  alt="Mojo Logo" 
                  className="w-8 h-8 object-contain scale-110" 
                />
              </div>
              <span className="text-2xl font-bold tracking-tighter text-white">Mojo</span>
            </div>
            <p className="text-sm text-primary-foreground/60 leading-relaxed">
              Elevating language education for the next generation of global leaders.
            </p>  
          </div>
          <div>
            <h4 className="font-bold mb-6 uppercase text-xs tracking-widest text-accent">Platform</h4>
            <ul className="space-y-4 text-sm text-primary-foreground/60">
              <li className="hover:text-white cursor-pointer transition-colors">Gemini AI</li>
              <li className="hover:text-white cursor-pointer transition-colors">Enterprise</li>
            </ul>
          </div>
          <div>
            <h4 className="font-bold mb-6 uppercase text-xs tracking-widest text-accent">Company</h4>
            <ul className="space-y-4 text-sm text-primary-foreground/60">
              <li className="hover:text-white cursor-pointer transition-colors">About Us</li>
              <li className="hover:text-white cursor-pointer transition-colors">Careers</li>
              <li className="hover:text-white cursor-pointer transition-colors">Contact</li>
            </ul>
          </div>
          <div>
            <h4 className="font-bold mb-6 uppercase text-xs tracking-widest text-accent">Legal</h4>
            <ul className="space-y-4 text-sm text-primary-foreground/60">
              <li className="hover:text-white cursor-pointer transition-colors">Privacy</li>
              <li className="hover:text-white cursor-pointer transition-colors">Terms</li>
              <li className="hover:text-white cursor-pointer transition-colors">Cookie Policy</li>
            </ul>
          </div>
        </div>
        <div className="max-w-7xl mx-auto px-8 mt-8 flex flex-col md:flex-row justify-between items-center gap-4 text-[10px] uppercase font-bold tracking-widest text-primary-foreground/40">
          <p>© 2026 Mojo. Crafted for Excellence.</p>
          <div className="flex items-center gap-6">
            <span>Twitter</span>
            <span>LinkedIn</span>
            <span>Instagram</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

const Card = ({ children, className }: { children: React.ReactNode, className?: string }) => (
  <div className={`p-6 border rounded-xl ${className}`}>
    {children}
  </div>
);
