import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  CheckCircle2,
  ArrowRight,
  Target,
  Clock,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { STUDY_REASONS } from '@/features/onboarding/study-reasons';
import type { OnboardingRequest } from '@/types/api.generated';

interface OnboardingProps {
  onComplete: (data: OnboardingRequest) => Promise<void> | void;
  onSkip?: () => void;
  isSubmitting?: boolean;
  error?: string | null;
}

const targetLevels: { id: OnboardingRequest['targetLevel']; desc: string }[] = [
  { id: 'N4', desc: 'Basic conversations and simple everyday reading.' },
  { id: 'N3', desc: 'Everyday situations and moderately complex texts.' },
  { id: 'N2', desc: 'News, articles and most workplace situations.' },
  { id: 'N1', desc: 'Near-native: complex, abstract topics at natural speed.' },
];

const dailyTimes: { id: OnboardingRequest['dailyStudyMinutes']; label: string; intensity: string }[] = [
  { id: 10, label: '10 Minutes', intensity: 'Casual' },
  { id: 20, label: '20 Minutes', intensity: 'Regular' },
  { id: 30, label: '30 Minutes', intensity: 'Steady' },
  { id: 60, label: '60+ Minutes', intensity: 'Intense' },
];

export const OnboardingView = ({ onComplete, onSkip, isSubmitting = false, error = null }: OnboardingProps) => {
  const [step, setStep] = useState(1);
  const [data, setData] = useState<OnboardingRequest>({
    studyReason: 'travel',
    targetLevel: 'N4',
    dailyStudyMinutes: 20,
  });

  const nextStep = () => {
    if (step < 3) setStep(step + 1);
    else void onComplete(data);
  };

  return (
    <div className="min-h-screen bg-[#f7f9fb] flex flex-col items-center justify-center p-4 font-sans">
      <div className="w-full max-w-2xl mb-8 flex flex-col items-center">
        <div className="w-full bg-gray-200 rounded-full h-1.5 mb-4 overflow-hidden border border-gray-300/50">
          <motion.div 
            className="bg-primary h-full rounded-full" 
            initial={{ width: '0%' }}
            animate={{ width: `${(step / 3) * 100}%` }}
          />
        </div>
        <div className="flex justify-between w-full text-[10px] uppercase font-bold tracking-widest text-muted-foreground">
          <span>Step {step} of 3</span>
          <span>{step === 1 ? 'Your Reason' : step === 2 ? 'Goal Level' : 'Daily Commitment'}</span>
        </div>
      </div>

      <motion.main 
        key={step}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 1.05 }}
        className="w-full max-w-2xl bg-white rounded-3xl shadow-sm border border-primary/5 p-8 md:p-12 relative overflow-hidden"
      >
        <div className="absolute top-0 right-0 -mt-16 -mr-16 w-48 h-48 bg-primary/5 rounded-full blur-3xl pointer-events-none"></div>
        
        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
              <div className="text-center mb-10">
                <h1 className="text-3xl font-black text-primary tracking-tight mb-2 font-display">Welcome to Mojo</h1>
                <p className="text-muted-foreground">Let&apos;s personalize your journey. Why are you learning Japanese?</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {STUDY_REASONS.map(r => (
                  <button
                    key={r.id}
                    onClick={() => setData({ ...data, studyReason: r.id })}
                    className={`relative p-6 rounded-2xl border text-left transition-all ${
                      data.studyReason === r.id 
                      ? 'bg-secondary/50 border-primary ring-1 ring-primary shadow-lg shadow-primary/5' 
                      : 'bg-white border-gray-100 hover:border-primary/30 hover:-translate-y-0.5'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span className={`text-lg font-bold ${data.studyReason === r.id ? 'text-primary' : 'text-gray-700'}`}>{r.title}</span>
                      </div>
                      <r.icon className={`w-5 h-5 ${data.studyReason === r.id ? 'text-primary' : 'text-gray-300'}`} />
                    </div>
                    <p className="text-xs text-muted-foreground leading-relaxed">{r.desc}</p>
                    {data.studyReason === r.id && <CheckCircle2 className="absolute top-2 right-2 w-4 h-4 text-primary fill-white" />}
                  </button>
                ))}
              </div>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
              <div className="text-center mb-10">
                <h1 className="text-3xl font-black text-primary tracking-tight mb-2">Which JLPT level are you aiming for?</h1>
                <p className="text-muted-foreground">This helps us prioritize the right vocabulary and grammar.</p>
              </div>
              <div className="space-y-4">
                {targetLevels.map(g => (
                   <button
                    key={g.id}
                    onClick={() => setData({ ...data, targetLevel: g.id })}
                    className={`w-full p-6 rounded-2xl border text-left transition-all flex items-center justify-between ${
                      data.targetLevel === g.id 
                      ? 'bg-secondary/50 border-primary ring-1 ring-primary' 
                      : 'bg-white border-gray-100'
                    }`}
                  >
                    <div>
                      <span className="text-lg font-bold text-primary block mb-1">JLPT {g.id}</span>
                      <p className="text-xs text-muted-foreground">{g.desc}</p>
                    </div>
                    {data.targetLevel === g.id ? <Target className="w-6 h-6 text-primary" /> : <div className="w-6 h-6 rounded-full border border-gray-200" />}
                  </button>
                ))}
              </div>
            </motion.div>
          )}

          {step === 3 && (
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
              <div className="text-center mb-10">
                <h1 className="text-3xl font-black text-primary tracking-tight mb-2">Your Daily Commitment</h1>
                <p className="text-muted-foreground">Consistency is key to mastery. How much time can you spare?</p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {dailyTimes.map(t => (
                  <button
                    key={t.id}
                    onClick={() => setData({ ...data, dailyStudyMinutes: t.id })}
                    className={`p-6 rounded-2xl border text-center transition-all ${
                      data.dailyStudyMinutes === t.id 
                      ? 'bg-primary text-white border-primary shadow-xl shadow-primary/20' 
                      : 'bg-white border-gray-100 hover:bg-gray-50'
                    }`}
                  >
                    <Clock className={`w-6 h-6 mx-auto mb-2 ${data.dailyStudyMinutes === t.id ? 'text-white' : 'text-primary'}`} />
                    <span className="text-lg font-bold block">{t.label}</span>
                    <span className={`text-[10px] font-bold uppercase tracking-widest ${data.dailyStudyMinutes === t.id ? 'text-white/70' : 'text-muted-foreground'}`}>{t.intensity}</span>
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {error ? (
          <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        ) : null}

        <div className="flex justify-between items-center mt-12 pt-8 border-t border-gray-100">
          <Button 
            variant="ghost" 
            className="text-xs font-bold uppercase tracking-widest text-muted-foreground hover:text-primary"
            onClick={() => setStep(prev => Math.max(1, prev - 1))}
            disabled={step === 1 || isSubmitting}
          >
            Back
          </Button>
          <div className="flex gap-4">
            {step < 3 && (
               <Button 
                variant="outline" 
                className="text-xs font-bold uppercase tracking-widest hover:bg-gray-50 rounded-xl"
                onClick={onSkip}
                disabled={isSubmitting}
              >
                Skip for now
              </Button>
            )}
            <Button 
              className="px-8 h-12 bg-accent hover:bg-accent/90 rounded-xl font-bold gap-2 text-sm shadow-lg shadow-accent/20"
              onClick={nextStep}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Saving...' : step === 3 ? 'Finish Setup' : 'Next Step'}
              <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </motion.main>
    </div>
  );
};
