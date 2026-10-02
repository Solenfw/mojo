import React from 'react';
import { 
  Mail,
  AlertCircle,
  Check
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

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
            We&apos;ve sent a password reset link to your email address. Please check your inbox.
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
          <p className="text-xs font-medium">Enter your email and we&apos;ll send you a link to reset your password.</p>
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
