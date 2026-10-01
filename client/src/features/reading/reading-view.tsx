import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  ChevronRight, 
  Book, 
  CheckCircle2, 
  ChevronLeft, 
  HelpCircle, 
  Clock, 
  Trophy, 
  BookOpen, 
  ArrowRight,
  Eye,
  EyeOff
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { getToken } from '@/lib/auth';
import { ReadingData } from '@/types';

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

interface ReadingLesson {
  lessonId: number;
  lessonTitle: string;
  lessonOrder: number;
  estimatedDuration: number;
  isPreviewAvailable: boolean;
}

export const Reading = ({ onBack }: { onBack: () => void }) => {
  // Navigation & Mode states
  const [screen, setScreen] = useState<'lessons' | 'practice' | 'results'>('lessons');
  const [lessons, setLessons] = useState<ReadingLesson[]>([]);
  const [selectedLesson, setSelectedLesson] = useState<ReadingLesson | null>(null);
  const [lessonId, setLessonId] = useState<number | null>(null);

  // Practice States
  const [data, setData] = useState<ReadingData | null>(null);
  const [showPopup, setShowPopup] = useState<string | null>(null);
  const [showTranslation, setShowTranslation] = useState<Record<number, boolean>>({});
  
  // Quiz Answers
  const [answers, setAnswers] = useState<Record<number, number>>({}); // exercise_id -> selected_option_id
  const [typedAnswers, setTypedAnswers] = useState<Record<number, string>>({}); // exercise_id -> user typed string for short answers

  // Result states
  const [result, setResult] = useState<{ score: number; xp_gained: number; is_passed: boolean; max_score: number } | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch Reading Lessons List on Load
  useEffect(() => {
    const fetchLessons = async () => {
      try {
        const token = getToken();
        // Fetch course first to get the dynamic N5 Course ID
        const courseRes = await fetch(`${API_BASE_URL}/api/v1/courses/by-level?targetLevel=N5`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }).then(r => r.json());
        
        const courseId = courseRes.data?.[0]?.courseId;
        if (!courseId) return;

        // Fetch all lessons linked to the N5 course
        const lessonsRes = await fetch(`${API_BASE_URL}/api/v1/courses/lessons?recommendedCourseId=${courseId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }).then(r => r.json());
        
        // Filter out only reading lessons
        const readingLessons = (lessonsRes.data || []).filter((l: any) => l.lessonType === 'reading');
        setLessons(readingLessons);
      } catch (err) {
        console.error("Failed to fetch reading lessons list:", err);
      }
    };
    fetchLessons();
  }, []);

  // Fetch Chosen Reading Lesson Details
  const handleSelectLesson = async (lesson: ReadingLesson) => {
    setSelectedLesson(lesson);
    setLessonId(lesson.lessonId);
    
    // Reset quiz state
    setAnswers({});
    setTypedAnswers({});
    setResult(null);
    setShowTranslation({});

    try {
      const token = getToken();
      const res = await fetch(`${API_BASE_URL}/api/v1/lessons/${lesson.lessonId}/reading`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const json = await res.json();
        setData(json);
        setScreen('practice');
      }
    } catch (err) {
      console.error("Failed to load reading details:", err);
    }
  };

  const handleSelectOption = (questionId: number, optionId: number) => {
    setAnswers(prev => ({ ...prev, [questionId]: optionId }));
  };

  const handleSubmit = async () => {
    if (!data) return;
    setIsSubmitting(true);

    // Dynamic Client-side validation mapper to adapt the typed input to standard Backend option-id checking
    const finalAnswers: Record<number, number> = {};

    data.questions.forEach((q) => {
      const isSA = q.options.length === 1; // Backend seeder seeds exactly 1 correct answer option for short-answers [17]
      
      if (isSA) {
        const typed = typedAnswers[q.id] || "";
        const correctText = q.options[0].text;
        
        // Clean comparison between typed answer and the correct answer text
        const isCorrect = typed.trim().toLowerCase() === correctText.trim().toLowerCase();
        
        // If correct, submit the valid option id, else map to a dummy invalid id (-1)
        finalAnswers[q.id] = isCorrect ? q.options[0].id : -1;
      } else {
        // Multiple Choice or True/False
        finalAnswers[q.id] = answers[q.id] || -1;
      }
    });

    try {
      const token = getToken();
      const res = await fetch(`${API_BASE_URL}/api/v1/lessons/${lessonId}/reading/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ answers: finalAnswers })
      });
      if (res.ok) {
        const resultData = await res.json();
        setResult(resultData);
        setScreen('results');
      }
    } catch (err) {
      console.error("Failed to submit reading quiz:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Helper to dynamically wrap vocab words in interactive hover spans
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
                <span key={`${word}-${i}-${j}`} className="relative inline-block mx-0.5">
                  <span
                    onMouseEnter={() => setShowPopup(word)}
                    onMouseLeave={() => setShowPopup(null)}
                    className="bg-primary/5 text-primary border-b-2 border-primary/20 border-dashed px-1 cursor-help hover:bg-primary/10 transition-all font-bold"
                  >
                    {word}
                  </span>
                  <AnimatePresence>
                    {showPopup === word && (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 10 }}
                        className="absolute bottom-full left-1/2 -translate-x-1/2 mb-4 w-56 bg-white rounded-2xl shadow-2xl border border-primary/10 p-5 z-20 pointer-events-none"
                      >
                        <div className="text-center border-b pb-3 mb-3">
                          <p className="text-xs font-bold text-muted-foreground tracking-widest mb-1">{data.words[word].kana}</p>
                          <p className="text-2xl font-black text-primary">{word}</p>
                        </div>
                        <div className="text-center space-y-1">
                          <p className="text-sm font-bold text-gray-700">{data.words[word].meaning}</p>
                          <span className="inline-block px-1.5 py-0.5 bg-gray-100 text-gray-500 text-[8px] font-black rounded uppercase mt-2">JLPT {data.words[word].level}</span>
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

  return (
    <div className="min-h-screen bg-[#f7f9fb] flex flex-col font-sans selection:bg-primary/10">
      
      {/* Header bar */}
      <div className="w-full bg-white border-b sticky top-0 z-10 shrink-0">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <button 
            onClick={() => {
              if (screen !== 'lessons') {
                setScreen('lessons');
              } else {
                onBack();
              }
            }} 
            className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-gray-50 text-gray-500 transition-colors group"
          >
            <ChevronLeft className="w-5 h-5 group-hover:-translate-x-0.5 transition-transform" />
          </button>
          <div className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2 bg-gray-50 px-3 py-1.5 rounded-full">
            <Book className="w-3 h-3 text-primary" />
            Reading Comprehension
          </div>
          <div className="w-10"></div>
        </div>
      </div>

      <AnimatePresence mode="wait">
        {/* SCREEN 1: LESSON SELECTION */}
        {screen === 'lessons' && (
          <motion.main 
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            className="flex-1 overflow-y-auto p-8 max-w-4xl mx-auto w-full space-y-8"
          >
            <div className="text-center space-y-3">
              <Badge className="bg-primary/10 text-primary border-primary/20 hover:bg-primary/20 font-bold uppercase tracking-widest">
                JLPT N5 Reading Foundation
              </Badge>
              <h2 className="text-4xl font-black text-primary tracking-tight">Japanese Reading Comprehension N5</h2>
              <p className="text-muted-foreground max-w-lg mx-auto font-medium">
                Pick one of the cultural articles below to build your vocabulary through images and practice reading comprehension.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {lessons.map((lesson) => (
                <Card 
                  key={lesson.lessonId}
                  className="hover:shadow-xl hover:border-primary/40 transition-all duration-300 group cursor-pointer border-gray-100 rounded-3xl"
                  onClick={() => void handleSelectLesson(lesson)}
                >
                  <CardContent className="p-6 flex flex-col justify-between h-full space-y-6">
                    <div className="flex justify-between items-start">
                      <div className="p-3 bg-secondary rounded-2xl group-hover:bg-primary group-hover:text-white transition-colors duration-300">
                        <BookOpen className="w-6 h-6 text-primary group-hover:text-white" />
                      </div>
                      <Badge variant="outline" className="text-[10px] font-bold text-muted-foreground uppercase border-gray-200">
                        {lesson.estimatedDuration} min
                      </Badge>
                    </div>

                    <div className="space-y-2">
                      {/* <span className="text-[10px] font-black uppercase text-accent tracking-[0.2em]">Lesson {lesson.lessonOrder}</span> */}
                      <h3 className="text-xl font-bold text-primary tracking-tight leading-snug group-hover:text-accent transition-colors">
                        {lesson.lessonTitle}
                      </h3>
                    </div>

                    <div className="flex items-center gap-2 text-xs font-bold text-primary group-hover:gap-3 transition-all pt-2">
                      Read the article
                      <ChevronRight className="w-4 h-4" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </motion.main>
        )}

        {/* SCREEN 2: PRACTICE */}
        {screen === 'practice' && data && (
          <motion.main 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex-1 overflow-y-auto p-8 lg:p-12 no-scrollbar"
          >
            <div className="max-w-6xl mx-auto flex flex-col lg:flex-row gap-12 items-start">
              
              {/* Left Column: Reading Content & Questions */}
              <div className="flex-1 space-y-12 w-full">
                
                {/* Reading Passage Cards */}
                <article className="bg-white rounded-[40px] border border-gray-100 shadow-2xl p-8 md:p-12 relative overflow-hidden space-y-8">
                  <div className="absolute top-0 left-0 w-full h-2 bg-linear-to-r from-primary to-accent" />
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="px-2 py-1 bg-primary/10 text-primary text-[10px] font-black rounded uppercase tracking-widest">JLPT {data.difficulty}</span>
                      <span className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Detailed Reading</span>
                    </div>
                  </div>

                  <h1 className="text-4xl font-jp text-primary font-black leading-tight border-b pb-6">
                    {data.title}
                  </h1>

                  {/* Dynamic Render Passages with individual JP-VN show/hide features */}
                  <div className="space-y-10">
                    {data.passages && data.passages.length > 0 ? (
                      data.passages.map((p) => (
                        <div key={p.id} className="space-y-4">
                          <div className="text-2xl font-jp leading-[1.9] text-gray-800 whitespace-pre-wrap">
                            {renderInteractiveText(p.japanese)}
                          </div>
                          
                          <div className="pt-2">
                            <Button 
                              variant="outline" 
                              size="sm" 
                              onClick={() => setShowTranslation(prev => ({ ...prev, [p.id]: !prev[p.id] }))}
                              className="text-primary text-[10px] font-bold uppercase tracking-widest gap-2 rounded-xl border-primary/20 hover:bg-primary/5"
                            >
                              {showTranslation[p.id] ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                              {showTranslation[p.id] ? "Hide translation" : "Show translation"}
                            </Button>
                          </div>

                          <AnimatePresence>
                            {showTranslation[p.id] && p.vietnamese && (
                              <motion.div 
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="p-5 bg-secondary/40 border border-primary/5 rounded-2xl text-sm text-gray-600 leading-relaxed font-medium mt-2"
                              >
                                {p.vietnamese}
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                      ))
                    ) : (
                      <div className="text-2xl font-jp leading-[1.9] text-gray-800 whitespace-pre-wrap">
                        {renderInteractiveText(data.content)}
                      </div>
                    )}
                  </div>
                </article>

                {/* Comprehension Quiz Card */}
                <section className="bg-white rounded-[40px] border border-gray-100 shadow-2xl p-8 md:p-12 space-y-8">
                  <div className="space-y-2">
                    <h2 className="text-3xl font-black text-primary tracking-tight">Comprehension Check</h2>
                    <p className="text-sm font-bold text-muted-foreground uppercase tracking-widest italic">Answer the following questions based on the reading passage</p>
                  </div>

                  <div className="space-y-12 pt-6">
                    {data.questions.map((q, i) => {
                      // Dynamically infer question types based on option structure [17]
                      const isTF = q.options.length === 2 && (
                        q.options[0].text === '〇' || q.options[0].text === '✕' || q.options[0].text === '✖' ||
                        q.options[1].text === '〇' || q.options[1].text === '✕' || q.options[1].text === '✖'
                      );
                      const isSA = q.options.length === 1;

                      return (
                        <div key={q.id} className="space-y-6">
                          <div className="text-lg font-jp font-bold text-gray-800 flex gap-4">
                            <span className="w-8 h-8 rounded-full bg-primary/5 text-primary flex items-center justify-center text-sm shrink-0 border border-primary/10">
                              {i + 1}
                            </span>
                            <div className="pt-0.5">{q.prompt}</div>
                          </div>

                          {/* CASE A: True/False Render Style */}
                          {isTF && (() => {
                            const trueOpt = q.options.find(o => o.text === '〇' || o.text === '○') || q.options[0];
                            const falseOpt = q.options.find(o => o.text === '✕' || o.text === '✖') || q.options[1];

                            return (
                              <div className="flex gap-4 pl-12 max-w-md">
                                <button
                                  onClick={() => handleSelectOption(q.id, trueOpt.id)}
                                  className={`flex-1 py-4 px-6 rounded-2xl border-2 transition-all font-jp font-bold text-base flex items-center justify-center gap-2 ${
                                    answers[q.id] === trueOpt.id 
                                      ? 'border-emerald-500 bg-emerald-50 text-emerald-600 shadow-sm' 
                                      : 'border-gray-100 hover:border-emerald-200 text-gray-500 bg-white'
                                  }`}
                                >
                                  True 〇
                                </button>
                                <button
                                  onClick={() => handleSelectOption(q.id, falseOpt.id)}
                                  className={`flex-1 py-4 px-6 rounded-2xl border-2 transition-all font-jp font-bold text-base flex items-center justify-center gap-2 ${
                                    answers[q.id] === falseOpt.id 
                                      ? 'border-red-500 bg-red-50 text-red-600 shadow-sm' 
                                      : 'border-gray-100 hover:border-red-200 text-gray-500 bg-white'
                                  }`}
                                >
                                  False ✖
                                </button>
                              </div>
                            );
                          })()}

                          {/* CASE B: Short Answer Textbox Render Style */}
                          {isSA && (
                            <div className="pl-12 space-y-2">
                              <span className="text-[10px] font-black uppercase text-muted-foreground tracking-widest">Type the answer in Japanese:</span>
                              <input 
                                type="text"
                                value={typedAnswers[q.id] || ""}
                                onChange={(e) => setTypedAnswers(prev => ({ ...prev, [q.id]: e.target.value }))}
                                placeholder="Example: ４にんです / 45さい / ..."
                                className="w-full h-12 border rounded-xl px-4 text-sm font-jp font-semibold outline-none focus:border-primary focus:bg-primary/5 transition-all bg-muted/20"
                              />
                            </div>
                          )}

                          {/* CASE C: Standard Multiple Choice Style */}
                          {!isTF && !isSA && (
                            <div className="grid gap-3 pl-12">
                              {q.options.map((opt) => (
                                <button 
                                  key={opt.id} 
                                  onClick={() => handleSelectOption(q.id, opt.id)}
                                  className={`text-left py-4 px-6 rounded-2xl border transition-all font-jp font-medium text-gray-600 group flex items-center justify-between ${
                                    answers[q.id] === opt.id ? 'border-primary bg-primary/5 shadow-xs' : 'border-gray-100 hover:border-primary/50'
                                  }`}
                                >
                                  {opt.text}
                                  {answers[q.id] === opt.id && <CheckCircle2 className="w-5 h-5 text-primary" />}
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>

                  <div className="pt-8 flex justify-end">
                    <Button 
                      onClick={handleSubmit} 
                      disabled={isSubmitting}
                      className="h-14 px-10 bg-accent hover:bg-accent/90 rounded-2xl font-black uppercase tracking-widest text-xs gap-3 shadow-xl shadow-accent/25"
                    >
                      {isSubmitting ? 'Evaluating...' : 'Submit and grade'}
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                </section>
              </div>

              {/* Right Column: Vocabulary Panel */}
              <aside className="w-full lg:w-80 shrink-0 space-y-8">
                <div className="bg-white rounded-3xl border border-gray-100 shadow-xl p-8 sticky top-24">
                  <div className="flex items-center gap-3 mb-8 pb-4 border-b border-gray-50">
                    <Book className="w-5 h-5 text-primary" />
                    <h3 className="font-black text-primary tracking-tight">Vocabulary</h3>
                  </div>
                  <div className="space-y-6 max-h-[60vh] overflow-y-auto no-scrollbar pr-2">
                    {Object.entries(data.words).map(([kanji, details]) => (
                      <div key={kanji} className="group cursor-pointer">
                        <div className="flex justify-between items-start mb-1">
                          <span className="text-lg font-jp font-black text-gray-800 group-hover:text-primary transition-colors">{kanji}</span>
                          <span className="text-[8px] font-black uppercase bg-gray-100 px-1.5 py-0.5 rounded text-muted-foreground">{details.level}</span>
                        </div>
                        <p className="text-[10px] font-bold text-primary/40 uppercase tracking-widest">{details.kana}</p>
                        <p className="text-xs font-bold text-gray-500 mt-1">{details.meaning}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </aside>

            </div>
          </motion.main>
        )}

        {/* SCREEN 3: RESULTS SUMMARY */}
        {screen === 'results' && result && (
          <motion.main 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="flex-1 overflow-y-auto p-8 max-w-xl mx-auto w-full flex flex-col justify-center items-center py-16"
          >
            <div className="bg-white rounded-[40px] border border-gray-100 shadow-2xl p-12 text-center w-full space-y-8 relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-2 bg-linear-to-r from-emerald-500 to-primary" />
              
              <div className="w-20 h-20 bg-emerald-50 rounded-full flex items-center justify-center mx-auto shadow-xs border border-emerald-100">
                <Trophy className="w-10 h-10 text-emerald-500" />
              </div>

              <div className="space-y-2">
                <Badge className="bg-emerald-50 text-emerald-600 border-none font-bold uppercase text-[10px] tracking-widest px-3 py-1">
                  Reading comprehension successful!
                </Badge>
                <h2 className="text-3xl font-black text-primary tracking-tight">Lesson Complete</h2>
                <p className="text-sm text-muted-foreground font-medium">
                  {result.is_passed ? 'Congratulations! You have met the reading comprehension requirements.' : 'The lesson did not meet the desired score. Please try again.'}
                </p>
              </div>

              {/* Central circular score graph */}
              <div className="flex justify-center py-4">
                <div className="relative w-40 h-40 flex items-center justify-center">
                  <svg className="w-full h-full absolute inset-0 transform -rotate-90" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="45" fill="none" stroke="#E2E8F0" strokeWidth="6" />
                    <motion.circle
                      cx="50"
                      cy="50"
                      r="45"
                      fill="none"
                      stroke="#10b981"
                      strokeWidth="6"
                      strokeLinecap="round"
                      initial={{ strokeDasharray: "282.7", strokeDashoffset: "282.7" }}
                      animate={{ strokeDashoffset: (282.7 - (282.7 * result.score) / (result.max_score || 100)) }}
                      transition={{ duration: 1.2, ease: "easeOut" }}
                    />
                  </svg>
                  <div className="flex flex-col items-center justify-center">
                    <span className="text-5xl font-black text-emerald-500">{result.score}</span>
                    <span className="text-[9px] font-black uppercase tracking-widest text-muted-foreground mt-1">Points received</span>
                  </div>
                </div>
              </div>

              {/* Awarded XP Summary Card */}
              <div className="p-5 bg-[#f8fafc] rounded-2xl border flex justify-between items-center max-w-sm mx-auto">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center text-white shadow-md">
                    <CheckCircle2 className="w-5 h-5" />
                  </div>
                  <div className="text-left">
                    <p className="text-xs font-bold text-primary">Exercise Points received</p>
                    <p className="text-[10px] text-muted-foreground uppercase font-black tracking-wider">Reflex Dialogue</p>
                  </div>
                </div>
                <span className="bg-emerald-500 text-white font-black text-xs px-3 py-1 rounded-lg">
                  +{result.xp_gained} XP
                </span>
              </div>

              <div className="pt-4 flex flex-col gap-3">
                <Button 
                  onClick={() => setScreen('lessons')} 
                  className="w-full h-12 bg-primary hover:bg-primary/95 font-bold uppercase text-[10px] tracking-widest rounded-xl transition-all"
                >
                  Read other scripts
                </Button>
                <Button 
                  onClick={onBack} 
                  variant="outline"
                  className="w-full h-12 border-2 text-muted-foreground font-bold uppercase text-[10px] tracking-widest rounded-xl hover:bg-gray-50"
                >
                  Return to Dashboard
                </Button>
              </div>
            </div>
          </motion.main>
        )}
      </AnimatePresence>
    </div>
  );
};