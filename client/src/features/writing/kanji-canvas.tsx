import React, { useRef, useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  Undo,
  Trash2,
  CheckCircle,
  ChevronLeft,
  Sparkles,
  Info,
  AlertCircle
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { getLevelLessons } from '@/features/curriculum/api';
import type { EvaluateWritingData, KanjiPracticeRead } from '@/types/api.generated';
import { evaluateWriting, getKanjiPractice } from './api';

const WRITING_PASS_SCORE = 60;

export const KanjiCanvas = ({ onBack }: { onBack: () => void }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [practices, setPractices] = useState<KanjiPracticeRead[]>([]);
  const [targetKanji, setTargetKanji] = useState<KanjiPracticeRead | null>(null);
  const [feedback, setFeedback] = useState<EvaluateWritingData | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLoadingPractices, setIsLoadingPractices] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadPractices = async () => {
      try {
        const lessons = await getLevelLessons('N5');
        const practiceRefs = lessons.flatMap((lesson) => lesson.kanjiPractices);
        const loadedPractices = await Promise.all(practiceRefs.map((practice) => getKanjiPractice(practice.id)));
        setPractices(loadedPractices);
        setTargetKanji(loadedPractices[0] ?? null);
        setError(null);
      } catch (err) {
        console.error('Failed to load kanji practices:', err);
        setError(err instanceof Error ? err.message : 'Unable to load kanji practices.');
      } finally {
        setIsLoadingPractices(false);
      }
    };
    void loadPractices();
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas && targetKanji) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        // Setup canvas with white background so the saved image isn't transparent
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.strokeStyle = '#00236f';
        ctx.lineWidth = 8;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
      }
    }
  }, [targetKanji]);

  const startDrawing = (e: React.MouseEvent | React.TouchEvent) => {
    setIsDrawing(true);
    draw(e);
  };

  const stopDrawing = () => {
    setIsDrawing(false);
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      ctx?.beginPath();
    }
  };

  const draw = (e: React.MouseEvent | React.TouchEvent) => {
    if (!isDrawing) return;
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx) return;

    const rect = canvas.getBoundingClientRect();
    const x = ('touches' in e) ? e.touches[0].clientX - rect.left : e.clientX - rect.left;
    const y = ('touches' in e) ? e.touches[0].clientY - rect.top : e.clientY - rect.top;

    ctx.lineTo(x, y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x, y);
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (canvas && ctx) {
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      setFeedback(null);
    }
  };

  const handleAnalyze = async () => {
    const canvas = canvasRef.current;
    if (!canvas || !targetKanji) return;

    setIsAnalyzing(true);
    setFeedback(null);
    setError(null);

    try {
      const result = await evaluateWriting({
        kanjiPracticeId: targetKanji.id,
        imageBase64: canvas.toDataURL('image/png'),
      });
      setFeedback(result);
    } catch (err) {
      console.error('Failed to evaluate writing:', err);
      setError(err instanceof Error ? err.message : 'Unable to evaluate your writing.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 py-4">
       <div className="flex items-center justify-between">
        <Button variant="ghost" className="gap-2 text-muted-foreground hover:text-primary" onClick={onBack}>
          <ChevronLeft className="w-4 h-4" />
          Back to Dashboard
        </Button>
        <Badge variant="outline" className="bg-primary/5 text-primary border-primary/10">Kanji Mastery Series</Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
        <div className="space-y-6">
          <Card className="overflow-hidden border-none shadow-sm bg-muted/30">
            <CardHeader className="bg-primary text-white p-6">
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle className="text-4xl font-jp">{targetKanji?.kanji ?? 'Loading…'}</CardTitle>
                  <p className="text-sm opacity-80">{targetKanji?.title}</p>
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-0 flex items-center justify-center bg-gray-100 border-x">
              <canvas
                ref={canvasRef}
                width={400}
                height={400}
                className="cursor-crosshair touch-none bg-white w-full max-w-100"
                onMouseDown={startDrawing}
                onMouseUp={stopDrawing}
                onMouseMove={draw}
                onTouchStart={startDrawing}
                onTouchEnd={stopDrawing}
                onTouchMove={draw}
              />
            </CardContent>
            <div className="p-4 border border-t-0 bg-white flex justify-between rounded-b-xl">
              <Button variant="outline" size="sm" onClick={clearCanvas} className="gap-2">
                <Trash2 className="w-4 h-4" />
                Clear Canvas
              </Button>
              <Button variant="outline" size="sm" className="gap-2" onClick={clearCanvas}>
                <Undo className="w-4 h-4" />
                Restart
              </Button>
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <div className="p-6 bg-white rounded-3xl border shadow-sm space-y-6">
            <div className="space-y-2">
              <h3 className="font-bold flex items-center gap-2">
                <Info className="w-4 h-4 text-primary" />
                Writing Guide
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Try to draw the Kanji character as accurately as possible. The AI will evaluate your stroke proportions, readability, and structural balance.
              </p>
            </div>

            <Button
              className="w-full h-14 text-lg bg-primary hover:bg-primary/90 shadow-lg shadow-primary/20"
              onClick={handleAnalyze}
              disabled={isAnalyzing || !targetKanji}
            >
              {isAnalyzing ? (
                 <span className="flex items-center gap-2">
                   <Sparkles className="w-5 h-5 animate-spin" />
                   Analyzing Strokes...
                 </span>
              ) : 'Submit for Feedback'}
            </Button>

            <AnimatePresence>
              {feedback && (
                <motion.div
                  initial={{ opacity: 0, height: 0, y: -10 }}
                  animate={{ opacity: 1, height: 'auto', y: 0 }}
                  exit={{ opacity: 0, height: 0 }}
                  className={`p-5 rounded-2xl border text-sm ${feedback.score >= WRITING_PASS_SCORE ? 'bg-emerald-50 border-emerald-100 text-emerald-800' : 'bg-red-50 border-red-100 text-red-800'}`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="font-bold flex items-center gap-2">
                      {feedback.score >= WRITING_PASS_SCORE ? <CheckCircle className="w-5 h-5 text-emerald-500" /> : <AlertCircle className="w-5 h-5 text-red-500" />}
                      Sensei&apos;s Feedback
                    </div>
                    <span className={`font-black text-lg ${feedback.score >= WRITING_PASS_SCORE ? 'text-emerald-600' : 'text-red-600'}`}>
                      {feedback.score}/100
                    </span>
                  </div>
                  <p className="leading-relaxed font-medium">{feedback.feedback}</p>
                  
                  {feedback.xpEarned > 0 && (
                     <div className="mt-3 pt-3 border-t border-current/10 font-bold text-emerald-600 flex justify-between items-center">
                        <span>XP Awarded</span>
                        <span className="bg-emerald-500 text-white px-2 py-0.5 rounded text-xs">+{feedback.xpEarned} XP</span>
                     </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>

            {error && <p className="text-sm font-bold text-destructive">{error}</p>}

            <div className="pt-6 border-t border-gray-100">
              <p className="text-[10px] uppercase font-bold text-muted-foreground mb-4 tracking-widest text-center">Practice Queue</p>
              <div className="flex justify-center gap-4">
                {practices.map((practice) => (
                  <button
                    key={practice.id}
                    className={`w-12 h-12 rounded-xl border-2 transition-all font-jp text-xl flex items-center justify-center ${
                      targetKanji?.id === practice.id ? 'border-primary bg-primary/5 text-primary shadow-sm' : 'border-gray-100 hover:border-primary/40 text-gray-500'
                    }`}
                    onClick={() => {
                        setTargetKanji(practice);
                        clearCanvas();
                    }}
                  >
                    {practice.kanji}
                  </button>
                ))}
              </div>
              {isLoadingPractices && <p className="mt-3 text-center text-xs text-muted-foreground">Loading kanji practices...</p>}
              {!isLoadingPractices && practices.length === 0 && !error && (
                <p className="mt-3 text-center text-xs text-muted-foreground">No kanji practices are available yet.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};