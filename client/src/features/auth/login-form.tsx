import React from 'react';
import { 
  Mail,
  Lock,
  AlertCircle,
  Eye,
  EyeOff
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export const LoginForm = ({ 
  onSubmit, 
  onSignUp, 
  onForgotPassword,
  error,
  isLoading = false
}: { 
  onSubmit: (e: React.SubmitEvent) => void, 
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
