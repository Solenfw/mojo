import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { ChevronRight, Book, Star as StarIcon, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { getToken } from '@/lib/auth';
import { ReadingData } from '@/types';

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

export const Reading = ({ onBack }: { onBack: () => void }) => {
  const [showPopup, setShowPopup] = useState<string | null>(null);
  const [data, setData] = useState<ReadingData | null>(null);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [result, setResult] = useState<{ score: number; xp_gained: number; is_passed: boolean, max_score: number } | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // For this demo, we assume we are fetching Lesson ID 3 (The Shinkansen lesson from seeder)
  const LESSON_ID = 3;

  useEffect(() => {
    const fetchReadingData = async () => {
      try {
        const token = getToken();
        const res = await fetch(`${API_BASE_URL}/api/v1/lessons/${LESSON_ID}/reading`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const json = await res.json();
          setData(json);
        }
      } catch (err) {
        console.error("Failed to fetch reading lesson:", err);
      }
    };
    fetchReadingData();
  }, []);

  const handleSelectOption = (questionId: number, optionId: number) => {
    setAnswers(prev => ({ ...prev, [questionId]: optionId }));
  };

  const handleSubmit = async () => {
    if (!data) return;
    setIsSubmitting(true);
    try {
      const token = getToken();
      const res = await fetch(`${API_BASE_URL}/api/v1/lessons/${LESSON_ID}/reading/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ answers })
      });
      if (res.ok) {
        const resultData = await res.json();
        setResult(resultData);
      }
    } catch (err) {
      console.error("Failed to submit quiz:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Helper to dynamically wrap vocab words in interactive spans
  const renderInteractiveText = (text: string) => {
    if (!data) return text;
    let parts: React.ReactNode[] = [text];

    Object.keys(data.words).forEach(word => {
      const newParts: React.ReactNode[] = [];
      parts.forEach((part, i) => {
        if (typeof part === 'string') {
          const split = part.split(word);
          split.forEach((s, j) => {
            newParts.push(s);
            if (j < split.length - 1) {
              newParts.push(
                <span key={`${word}-${i}-${j}`} className="relative inline-block mx-1 group">
                  <span
                    onMouseEnter={() => setShowPopup(word)}
                    onMouseLeave={() => setShowPopup(null)}
                    className="bg-primary/5 text-primary border-b-2 border-primary/20 border-dashed px-1 cursor-help hover:bg-primary/10 transition-all"
                  >
                    {word}
                  </span>
                  <AnimatePresence>
                    {showPopup === word && (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="absolute bottom-full left-1/2 -translate-x-1/2 mb-4 w-56 bg-white rounded-2xl shadow-2xl border border-primary/10 p-5 z-20 pointer-events-none"
                      >
                        <div className="text-center border-b pb-3 mb-3">
                          <p className="text-xs font-bold text-muted-foreground tracking-widest mb-1">{data.words[word].kana}</p>
                          <p className="text-2xl font-black text-primary">{word}</p>
                        </div>
                        <div className="text-center">
                          <p className="text-sm font-bold text-gray-700">{data.words[word].meaning}</p>
                          <span className="inline-block px-1.5 py-0.5 bg-gray-100 text-gray-500 text-[8px] font-black rounded uppercase mt-2">{data.words[word].level}</span>
                        </div>
                        <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-white" />
                      </motion.div>
                    )}
                  </AnimatePresence>
                </span>
              );
            }
          });
        } else {
          newParts.push(part);
        }
      });
      parts = newParts;
    });

    return parts;
  };

  if (!data) {
    return <div className="flex h-screen items-center justify-center bg-[#f7f9fb]"><p className="animate-pulse font-bold text-muted-foreground">Loading Article...</p></div>;
  }

  return (
    <div className="flex h-screen bg-[#f7f9fb] font-sans selection:bg-primary/10">
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <main className="flex-1 overflow-y-auto p-8 lg:p-12 no-scrollbar">
          <div className="max-w-5xl mx-auto flex flex-col lg:flex-row gap-12 items-start">
            {/* Article */}
            <div className="flex-1 space-y-12">
               <article className="bg-white rounded-[40px] border border-gray-100 shadow-2xl p-12 relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-2 bg-linear-to-r from-primary to-accent" />
                  <div className="flex items-center gap-3 mb-8">
                     <span className="px-2 py-1 bg-primary/10 text-primary text-[10px] font-black rounded uppercase tracking-widest">JLPT {data.difficulty}</span>
                     <span className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Culture & Daily Life</span>
                  </div>
                  <header className="mb-12">
                     <h1 className="text-5xl font-jp text-primary font-black leading-tight">{data.title}</h1>
                  </header>
                  <div className="space-y-8 text-2xl font-jp leading-[1.8] text-gray-800 whitespace-pre-wrap">
                    {renderInteractiveText(data.content)}
                  </div>
               </article>

               {/* Quiz */}
               <section className="bg-white rounded-[40px] border border-gray-100 shadow-2xl p-12 space-y-8">
                  {result ? (
                    <div className="text-center space-y-6 py-8">
                      <div className={`w-20 h-20 mx-auto rounded-full flex items-center justify-center ${result.is_passed ? 'bg-emerald-50 text-emerald-500' : 'bg-red-50 text-red-500'}`}>
                        <CheckCircle2 className="w-10 h-10" />
                      </div>
                      <div>
                        <h2 className="text-3xl font-black text-primary tracking-tight">
                          {result.is_passed ? 'Excellent Job!' : 'Keep Practicing!'}
                        </h2>
                        <p className="text-muted-foreground mt-2">You scored {result.score} / {result.max_score}</p>
                        <p className="font-bold text-accent mt-2">+{result.xp_gained} XP Earned</p>
                      </div>
                      <Button onClick={onBack} className="mt-4 px-8 bg-primary">Return to Dashboard</Button>
                    </div>
                  ) : (
                    <>
                      <div className="space-y-2">
                        <h2 className="text-3xl font-black text-primary tracking-tight">Comprehension Check</h2>
                        <p className="text-sm font-bold text-muted-foreground uppercase tracking-widest italic">Testing your understanding of the text</p>
                      </div>
                      <div className="space-y-12">
                        {data.questions.map((q, i) => (
                          <div key={q.id} className="space-y-6">
                            <p className="text-xl font-jp font-bold text-gray-800 flex gap-4">
                              <span className="w-8 h-8 rounded-full bg-primary/5 text-primary flex items-center justify-center text-sm shrink-0 border border-primary/10">{i + 1}</span>
                              {q.prompt}
                            </p>
                            <div className="grid gap-3 pl-12">
                              {q.options.map((opt) => (
                                <button 
                                  key={opt.id} 
                                  onClick={() => handleSelectOption(q.id, opt.id)}
                                  className={`text-left py-4 px-6 rounded-2xl border transition-all font-jp font-medium text-gray-600 group flex items-center justify-between ${
                                    answers[q.id] === opt.id ? 'border-primary bg-primary/5 shadow-sm' : 'border-gray-100 hover:border-primary/50'
                                  }`}
                                >
                                  {opt.text}
                                  {answers[q.id] === opt.id && <CheckCircle2 className="w-5 h-5 text-primary" />}
                                </button>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                      <div className="pt-8 flex justify-end">
                        <Button 
                          onClick={handleSubmit} 
                          disabled={Object.keys(answers).length !== data.questions.length || isSubmitting}
                          className="h-14 px-10 bg-accent hover:bg-accent/90 rounded-2xl font-black uppercase tracking-widest text-xs gap-3 shadow-xl shadow-accent/20"
                        >
                          {isSubmitting ? 'Evaluating...' : 'Submit Answers'}
                          <ChevronRight className="w-4 h-4" />
                        </Button>
                      </div>
                    </>
                  )}
               </section>
            </div>

            {/* Right Panel: Vocabulary List */}
            <aside className="w-full lg:w-72 shrink-0 space-y-8">
               <div className="bg-white rounded-3xl border border-gray-100 shadow-xl p-8 sticky top-8">
                  <div className="flex items-center gap-3 mb-8 pb-4 border-b border-gray-50">
                    <Book className="w-5 h-5 text-primary" />
                    <h3 className="font-black text-primary tracking-tight">Vocabulary</h3>
                  </div>
                  <div className="space-y-6">
                    {Object.entries(data.words).map(([kanji, details]) => (
                      <div key={kanji} className="group cursor-pointer">
                        <div className="flex justify-between items-start mb-1">
                          <span className="text-lg font-jp font-black text-gray-800 group-hover:text-primary transition-colors">{kanji}</span>
                          <span className="text-[8px] font-black uppercase bg-gray-50 px-1.5 py-0.5 rounded text-muted-foreground">{details.level}</span>
                        </div>
                        <p className="text-[10px] font-bold text-primary/40 uppercase tracking-widest">{details.kana}</p>
                        <p className="text-xs font-bold text-gray-500 mt-1">{details.meaning}</p>
                      </div>
                    ))}
                  </div>
               </div>

               <div className="bg-primary rounded-3xl p-8 text-white space-y-4 shadow-2xl shadow-primary/30 relative overflow-hidden group">
                  <StarIcon className="absolute -top-2.5 -right-2.5 w-32 h-32 text-white/5 rotate-12 group-hover:scale-110 transition-transform" />
                  <h4 className="font-black text-lg leading-tight uppercase tracking-tight">VIP Coaching</h4>
                  <p className="text-xs font-medium text-white/70 leading-relaxed">Struggling with this text? Get a 1-on-1 session with a Sensei now.</p>
                  <Button className="w-full bg-white text-primary hover:bg-white/90 rounded-xl font-black uppercase text-[10px] tracking-widest h-12 mt-4">
                    Book Sensei
                  </Button>
               </div>
            </aside>
          </div>
        </main>
      </div>
    </div>
  );
};