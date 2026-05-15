import React, { useRef, useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  Undo,
  Trash2,
  CheckCircle,
  ChevronLeft,
  Sparkles,
  Info
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { N5_VOCABULARY } from '@/utils/constants';

export const KanjiCanvas = ({ onBack }: { onBack: () => void }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [targetKanji, setTargetKanji] = useState(N5_VOCABULARY[0]);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.strokeStyle = '#00236f';
        ctx.lineWidth = 6;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
      }
    }
  }, []);

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
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      setFeedback(null);
    }
  };

  const handleAnalyze = () => {
    setIsAnalyzing(true);
    // Simulate AI analysis
    setTimeout(() => {
      setFeedback("Excellent balance. Your stroke order for the left radical is correct. Try to make the right hook slightly sharper.");
      setIsAnalyzing(false);
    }, 1500);
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
            <CardContent className="p-0 flex items-center justify-center bg-white">
              <canvas
                ref={canvasRef}
                width={400}
                height={400}
                className="cursor-crosshair touch-none"
                onMouseDown={startDrawing}
                onMouseUp={stopDrawing}
                onMouseMove={draw}
                onTouchStart={startDrawing}
                onTouchEnd={stopDrawing}
                onTouchMove={draw}
              />
            </CardContent>
            <div className="p-4 border-t bg-gray-50 flex justify-between">
              <Button variant="outline" size="sm" onClick={clearCanvas} className="gap-2">
                <Trash2 className="w-4 h-4" />
                Clear
              </Button>
              <Button variant="outline" size="sm" className="gap-2">
                <Undo className="w-4 h-4" />
                Undo
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
                Focus on the "tome" (stop) at the end of the vertical stroke. The horizontal stroke should slightly tilt upwards for a natural calligraphic feel.
              </p>
            </div>

            <Button
              className="w-full h-14 text-lg bg-primary hover:bg-primary/90"
              onClick={handleAnalyze}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? (
                 <span className="flex items-center gap-2">
                   <Sparkles className="w-5 h-5 animate-spin" />
                   AI Analyzing...
                 </span>
              ) : 'Submit for Feedback'}
            </Button>

            <AnimatePresence>
              {feedback && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="p-4 bg-secondary/30 rounded-xl border border-primary/10 text-sm text-primary"
                >
                  <div className="font-bold mb-2 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-emerald-500" />
                    AI Critique
                  </div>
                  {feedback}
                </motion.div>
              )}
            </AnimatePresence>

            <div className="pt-4 border-t">
              <p className="text-[10px] uppercase font-bold text-muted-foreground mb-4 tracking-widest text-center">Upcoming Kanji</p>
              <div className="flex justify-center gap-4">
                {N5_VOCABULARY.slice(1, 4).map(v => (
                  <button
                    key={v.id}
                    className="w-12 h-12 rounded-xl border hover:border-primary hover:bg-secondary/20 transition-all font-jp text-xl"
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