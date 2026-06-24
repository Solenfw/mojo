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
import { N5_VOCABULARY } from '@/utils/constants';
import { getToken } from '@/lib/auth';

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

export const KanjiCanvas = ({ onBack }: { onBack: () => void }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [targetKanji, setTargetKanji] = useState(N5_VOCABULARY[0]);
  const [feedback, setFeedback] = useState<{ text: string; score: number; xp: number } | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
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
    if (!canvas) return;

    setIsAnalyzing(true);
    setFeedback(null);

    const base64Image = canvas.toDataURL('image/png');
    const token = getToken();

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/writing/evaluate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          image_base64: base64Image,
          target_kanji: targetKanji.kanji
        })
      });

      if (res.ok) {
        const data = await res.json();
        setFeedback({
          text: data.feedback,
          score: data.score,
          xp: data.xp_awarded
        });
      } else {
        setFeedback({ text: 'Failed to evaluate. Please try again.', score: 0, xp: 0 });
      }
    } catch (err) {
      console.error(err);
      setFeedback({ text: 'Network error. Could not connect to AI.', score: 0, xp: 0 });
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
                  <CardTitle className="text-4xl font-jp">{targetKanji.kanji}</CardTitle>
                  <p className="text-sm opacity-80">{targetKanji.kana} ({targetKanji.meaning})</p>
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
              disabled={isAnalyzing}
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
                  className={`p-5 rounded-2xl border text-sm ${feedback.score >= 60 ? 'bg-emerald-50 border-emerald-100 text-emerald-800' : 'bg-red-50 border-red-100 text-red-800'}`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="font-bold flex items-center gap-2">
                      {feedback.score >= 60 ? <CheckCircle className="w-5 h-5 text-emerald-500" /> : <AlertCircle className="w-5 h-5 text-red-500" />}
                      Sensei's Feedback
                    </div>
                    <span className={`font-black text-lg ${feedback.score >= 60 ? 'text-emerald-600' : 'text-red-600'}`}>
                      {feedback.score}/100
                    </span>
                  </div>
                  <p className="leading-relaxed font-medium">{feedback.text}</p>
                  
                  {feedback.xp > 0 && (
                     <div className="mt-3 pt-3 border-t border-current/10 font-bold text-emerald-600 flex justify-between items-center">
                        <span>XP Awarded</span>
                        <span className="bg-emerald-500 text-white px-2 py-0.5 rounded text-xs">+{feedback.xp} XP</span>
                     </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>

            <div className="pt-6 border-t border-gray-100">
              <p className="text-[10px] uppercase font-bold text-muted-foreground mb-4 tracking-widest text-center">Practice Queue</p>
              <div className="flex justify-center gap-4">
                {N5_VOCABULARY.slice(1, 5).map(v => (
                  <button
                    key={v.id}
                    className={`w-12 h-12 rounded-xl border-2 transition-all font-jp text-xl flex items-center justify-center ${
                      targetKanji.id === v.id ? 'border-primary bg-primary/5 text-primary shadow-sm' : 'border-gray-100 hover:border-primary/40 text-gray-500'
                    }`}
                    onClick={() => {
                        setTargetKanji(v);
                        clearCanvas();
                    }}
                  >
                    {v.kanji}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};