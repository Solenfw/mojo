import React from 'react';
import { motion } from 'motion/react';
import { ChevronLeft } from 'lucide-react';

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  subtitle: string;
  onBack: () => void;
}

export const AuthLayout = ({ children, title, subtitle, onBack }: AuthLayoutProps) => {
  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center p-6 font-sans relative overflow-hidden">
      {/* Background Orbs */}
      <div className="absolute top-[-10%] right-[-10%] w-125 h-125 bg-primary/5 rounded-full blur-[100px] -z-10"></div>
      <div className="absolute bottom-[-10%] left-[-10%] w-125 h-125 bg-accent/5 rounded-full blur-[100px] -z-10"></div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md space-y-8"
      >
        <div className="flex flex-col items-center space-y-2 text-center">
          <div 
            onClick={onBack}
            className="group absolute top-10 left-10 flex items-center gap-2 text-sm font-bold text-muted-foreground hover:text-primary cursor-pointer transition-colors"
          >
            <ChevronLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            Home
          </div>

          <div className="w-12 h-12 bg-primary rounded-2xl flex items-center justify-center shadow-lg shadow-primary/20 mb-4">
            <span className="text-white font-black text-xl">LS</span>
          </div>
          <h1 className="text-3xl font-black tracking-tight text-primary">{title}</h1>
          <p className="text-muted-foreground">{subtitle}</p>
        </div>

        {children}

        <p className="text-[10px] text-center uppercase tracking-widest font-bold text-muted-foreground pt-4">
          © 2026 Mojo. Secure Environment.
        </p>
      </motion.div>
    </div>
  );
};
