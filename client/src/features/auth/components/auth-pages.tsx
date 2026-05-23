import React from 'react';
import { motion } from 'motion/react';
import { 
  ChevronLeft, 
  Mail, 
  Lock, 
  User, 
  AlertCircle,
  Eye,
  EyeOff,
  Check
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  subtitle: string;
  onBack: () => void;
  isLoading?: boolean;
}

export const AuthLayout = ({ children, title, subtitle, onBack, isLoading }: AuthLayoutProps) => {
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
          © 2026 LinguaSphere. Secure Environment.
        </p>
      </motion.div>
    </div>
  );
};

export const LoginForm = ({ 
  onSubmit, 
  onSignUp, 
  onForgotPassword,
  error,
  isLoading = false
}: { 
  onSubmit: (e: React.FormEvent) => void, 
  onSignUp: () => void,
  onForgotPassword: () => void,
  error?: string | null,
  isLoading?: boolean
}) => {
  const [showPassword, setShowPassword] = React.useState(false);

  return (
    <div className="bg-white p-8 rounded-4xl border border-primary/5 shadow-2xl shadow-primary/5 space-y-6">
      <div className="space-y-4">
        <Button variant="outline" className="w-full h-12 border-2 hover:bg-secondary/50 font-bold gap-3 rounded-xl transition-all">
          Continue with GitHub
        </Button>
        <div className="flex items-center gap-4 py-2">
          <div className="h-px flex-1 bg-muted"></div>
          <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest">or email</span>
          <div className="h-px flex-1 bg-muted"></div>
        </div>
        {error && (
          <div className="flex items-center gap-3 p-4 bg-destructive/10 text-destructive rounded-2xl">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <p className="text-xs font-medium">{error}</p>
          </div>
        )}
        <form onSubmit={onSubmit} className="space-y-4">
          <div className="space-y-2">
             <label className="text-xs font-bold uppercase tracking-widest text-primary/60 ml-1">Email Address</label>
             <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input name="email" type="email" placeholder="name@company.com" className="h-12 pl-10 rounded-xl bg-muted/30 border-none focus-visible:ring-primary/20" required />
             </div>
          </div>
          <div className="space-y-2">
             <div className="flex justify-between items-center px-1">
                <label className="text-xs font-bold uppercase tracking-widest text-primary/60">Password</label>
                <button 
                  type="button" 
                  onClick={onForgotPassword}
                  className="text-[10px] font-bold text-primary hover:text-accent uppercase tracking-wider"
                >
                  Forgot?
                </button>
             </div>
             <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input 
                  name="password"
                  type={showPassword ? "text" : "password"} 
                  placeholder="••••••••" 
                  className="h-12 pl-10 pr-10 rounded-xl bg-muted/30 border-none focus-visible:ring-primary/20" 
                  required 
                />
                <button 
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-primary transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
             </div>
          </div>
          <Button type="submit" disabled={isLoading} className="w-full h-14 bg-primary hover:bg-primary/90 text-lg font-bold rounded-2xl shadow-xl shadow-primary/20 transition-all">
            {isLoading ? 'Signing In...' : 'Sign In'}
          </Button>
        </form>
      </div>
      <div className="text-center pt-4">
        <p className="text-sm text-muted-foreground">
          Don't have an account? {' '}
          <button onClick={onSignUp} className="text-primary font-bold hover:underline">Create Account</button>
        </p>
      </div>
    </div>
  );
};

export const SignUpForm = ({ 
  onSubmit, 
  onLogin,
  error,
  isLoading = false
}: { 
  onSubmit: (e: React.SubmitEvent<HTMLFormElement>) => void, 
  onLogin: () => void,
  error?: string | null,
  isLoading?: boolean
}) => {
  return (
    <div className="bg-white p-8 rounded-4xl border border-primary/5 shadow-2xl shadow-primary/5 space-y-6">
      <form onSubmit={onSubmit} className="space-y-4">
        <div className="space-y-2">
           <label className="text-xs font-bold uppercase tracking-widest text-primary/60 ml-1">Full Name</label>
           <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input name="fullName" type="text" placeholder="Alex Johnson" className="h-12 pl-10 rounded-xl bg-muted/30 border-none focus-visible:ring-primary/20" required />
           </div>
        </div>
        <div className="space-y-2">
           <label className="text-xs font-bold uppercase tracking-widest text-primary/60 ml-1">Email Address</label>
           <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input name="email" type="email" placeholder="name@company.com" className="h-12 pl-10 rounded-xl bg-muted/30 border-none focus-visible:ring-primary/20" required />
           </div>
        </div>
        <div className="space-y-2">
           <label className="text-xs font-bold uppercase tracking-widest text-primary/60 ml-1">Password</label>
           <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input name="password" type="password" placeholder="Create a strong password" className="h-12 pl-10 rounded-xl bg-muted/30 border-none focus-visible:ring-primary/20" required />
           </div>
        </div>
        <div className="space-y-3 pt-2">
           <p className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest">Inclusions:</p>
           <div className="flex flex-wrap gap-2">
              <Badge variant="secondary" className="bg-emerald-50 text-emerald-600 border-emerald-100 flex gap-1 items-center px-2 py-0.5">
                <Check className="w-3 h-3" /> N5 Path
              </Badge>
              <Badge variant="secondary" className="bg-emerald-50 text-emerald-600 border-emerald-100 flex gap-1 items-center px-2 py-0.5">
                <Check className="w-3 h-3" /> AI Kaiwa
              </Badge>
              <Badge variant="secondary" className="bg-emerald-50 text-emerald-600 border-emerald-100 flex gap-1 items-center px-2 py-0.5">
                <Check className="w-3 h-3" /> Writing Pro
              </Badge>
           </div>
        </div>
        {error && (
          <div className="flex items-center gap-3 p-4 bg-destructive/10 text-destructive rounded-2xl">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <p className="text-xs font-medium">{error}</p>
          </div>
        )}
        <Button type="submit" disabled={isLoading} className="w-full h-14 bg-primary hover:bg-primary/90 text-lg font-bold rounded-2xl shadow-xl shadow-primary/20 transition-all">
          {isLoading ? 'Creating Account...' : 'Create Account'}
        </Button>
      </form>
      <div className="text-center pt-4">
        <p className="text-sm text-muted-foreground">
          Already have an account? {' '}
          <button onClick={onLogin} className="text-primary font-bold hover:underline">Sign In</button>
        </p>
      </div>
    </div>
  );
};

export const ForgotPasswordForm = ({ onBack }: { onBack: () => void }) => {
  const [submitted, setSubmitted] = React.useState(false);

  if (submitted) {
    return (
      <div className="bg-white p-8 rounded-4xl border border-primary/5 shadow-2xl shadow-primary/5 text-center space-y-6">
        <div className="w-16 h-16 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center mx-auto">
          <Check className="w-8 h-8" />
        </div>
        <div className="space-y-2">
          <h3 className="text-2xl font-bold text-primary">Instructions Sent</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">
            We've sent a password reset link to your email address. Please check your inbox.
          </p>
        </div>
        <Button onClick={onBack} className="w-full h-12 bg-primary hover:bg-primary/90 font-bold rounded-xl transition-all">
          Return to Login
        </Button>
      </div>
    );
  }

  return (
    <div className="bg-white p-8 rounded-4xl border border-primary/5 shadow-2xl shadow-primary/5 space-y-6">
       <div className="flex items-center gap-3 p-4 bg-blue-50 text-primary rounded-2xl">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <p className="text-xs font-medium">Enter your email and we'll send you a link to reset your password.</p>
       </div>
       <form onSubmit={(e) => { e.preventDefault(); setSubmitted(true); }} className="space-y-4">
          <div className="space-y-2">
             <label className="text-xs font-bold uppercase tracking-widest text-primary/60 ml-1">Email Address</label>
             <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input type="email" placeholder="name@company.com" className="h-12 pl-10 rounded-xl bg-muted/30 border-none focus-visible:ring-primary/20" required />
             </div>
          </div>
          <Button type="submit" className="w-full h-14 bg-primary hover:bg-primary/90 text-lg font-bold rounded-2xl shadow-xl shadow-primary/20 transition-all">
            Send Reset Link
          </Button>
       </form>
       <div className="text-center">
          <button onClick={onBack} className="text-sm font-bold text-muted-foreground hover:text-primary transition-colors">
            Wait, I remember it!
          </button>
       </div>
    </div>
  );
};
