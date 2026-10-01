import React from 'react';
import { 
  Mail,
  Lock,
  User,
  AlertCircle,
  Check
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

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
           <label className="text-xs font-bold uppercase tracking-widest text-primary/60 ml-1">Username</label>
           <Input name="username" type="text" placeholder="alexj" minLength={2} maxLength={50} className="h-12 rounded-xl bg-muted/30 border-none focus-visible:ring-primary/20" required />
        </div>
        <div className="space-y-2">
           <label className="text-xs font-bold uppercase tracking-widest text-primary/60 ml-1">Password</label>
           <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input name="password" type="password" placeholder="Create a strong password" minLength={8} className="h-12 pl-10 rounded-xl bg-muted/30 border-none focus-visible:ring-primary/20" required />
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
