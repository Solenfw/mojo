import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import {
  ArrowLeft,
  Volume2,
  Check,
  X,
  RotateCw,
  Library
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { getToken } from '@/lib/auth';
import { Card } from '@/types';

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');


export const Vocabulary = ({ onBack }: { onBack: () => void }) => {
  const [cards, setCards] = useState<Card[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [direction, setDirection] = useState(0);
  const [loading, setLoading] = useState(true);

  // Fetch real cards from due SRS endpoint
  useEffect(() => {
    const fetchCards = async () => {
      try {
        const token = getToken();
        const res = await fetch(`${API_BASE_URL}/api/v1/srs/due`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (res.ok) {
          const data = await res.json();
          const parsedCards = data.map((item: any) => ({
            id: item.vocab_id.toString(),
            kanji: item.kanji,
            furigana: item.furigana,
            meaning: item.meaning,
            example: item.example,
            exampleEnglish: item.exampleEnglish,
            level: item.level
          }));
          setCards(parsedCards);
        }
      } catch (err) {
        console.error("Failed to load vocab card queue:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchCards();
  }, []);

  const handleNext = async (qualityScore: number, dir: number) => {
    if (cards.length === 0) return;
    const currentCard = cards[currentIndex];

    // Post review metadata to SM-2 scheduler backend
    try {
      const token = getToken();
      await fetch(`${API_BASE_URL}/api/v1/srs/review`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          vocab_id: parseInt(currentCard.id, 10),
          quality_score: qualityScore
        })
      });
    } catch (err) {
      console.error("Failed to record review session:", err);
    }

    setDirection(dir);
    setIsFlipped(false);
    
    setTimeout(() => {
      if (cards.length > 1) {
        setCurrentIndex((prev) => (prev + 1) % cards.length);
      } else {
        // Complete current set
        setCards([]);
      }
    }, 100);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#f7f9fb] flex items-center justify-center font-sans">
        <p className="text-sm font-bold text-muted-foreground animate-pulse">Loading Vocabulary Session...</p>
      </div>
    );
  }

  if (cards.length === 0) {
    return (
      <div className="min-h-screen bg-[#f7f9fb] flex flex-col items-center justify-center font-sans p-6 text-center">
        <div className="w-16 h-16 bg-emerald-50 rounded-full flex items-center justify-center mb-4">
          <Check className="w-8 h-8 text-emerald-500" />
        </div>
        <h2 className="text-2xl font-bold text-primary mb-2">Queue Clear!</h2>
        <p className="text-sm text-muted-foreground max-w-sm mb-6">Excellent job. All of your scheduled flashcards have been successfully reviewed.</p>
        <Button onClick={onBack} className="bg-primary">Back to Dashboard</Button>
      </div>
    );
  }

  const currentCard = cards[currentIndex];

  return (
    <div className="min-h-screen bg-[#f7f9fb] flex flex-col font-sans">
      {/* Header */}
      <header className="w-full bg-white border-b sticky top-0 z-10">
        <div className="h-1 w-full bg-gray-100">
          <motion.div
            className="h-full bg-primary"
            initial={{ width: '0%' }}
            animate={{ width: `${((currentIndex + 1) / cards.length) * 100}%` }}
          />
        </div>
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <button onClick={onBack} className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-gray-50 text-gray-500 transition-colors group">
            <ArrowLeft className="w-5 h-5 group-hover:-translate-x-0.5 transition-transform" />
          </button>
          <div className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-2 bg-gray-50 px-3 py-1.5 rounded-full">
            <Library className="w-3 h-3" />
            {cards.length - currentIndex} cards remaining
          </div>
          <div className="w-10"></div>
        </div>
      </header>

      {/* Main Flashcard */}
      <main className="flex-1 flex flex-col items-center justify-center p-6 md:p-12 relative overflow-hidden">
        {/* Background Decorations */}
        <div className="absolute top-1/2 left-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl -translate-x-1/2 -z-10" />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-accent/5 rounded-full blur-3xl translate-x-1/4 translate-y-1/4 -z-10" />

        <div className="w-full max-w-2xl perspective-1000 h-112.5">
          <motion.div
            key={currentIndex}
            initial={{ x: direction * 100, opacity: 0, rotateY: 0 }}
            animate={{ x: 0, opacity: 1, rotateY: isFlipped ? 180 : 0 }}
            transition={{ type: 'spring', damping: 20, stiffness: 100 }}
            onClick={() => setIsFlipped(!isFlipped)}
            className="w-full h-full relative preserve-3d cursor-pointer"
          >
            {/* Front */}
            <div className="absolute inset-0 backface-hidden bg-white rounded-3xl border border-gray-100 shadow-2xl flex flex-col items-center justify-center text-center p-12">
               <div className="absolute top-6 left-6 px-3 py-1.5 bg-gray-50 rounded-full font-black text-[10px] text-primary uppercase tracking-widest border border-gray-100">
                  {currentCard.level}
               </div>
               <div className="space-y-4">
                  <p className="text-lg font-jp text-primary/40 tracking-[0.3em] font-medium">{currentCard.furigana}</p>
                  <h1 className="text-7xl font-jp text-primary font-black tracking-tight">{currentCard.kanji}</h1>
               </div>
               <div className="absolute bottom-8 text-[10px] font-black text-muted-foreground uppercase tracking-[0.2em] animate-pulse">
                  Click to reveal meaning
               </div>
            </div>

            {/* Back */}
            <div className="absolute inset-0 backface-hidden bg-white rounded-3xl border border-primary/10 shadow-2xl flex flex-col items-center p-0 overflow-hidden" style={{ transform: 'rotateY(180deg)' }}>
               <div className="w-full bg-primary/5 p-8 flex flex-col items-center">
                  <h2 className="text-3xl font-black text-primary tracking-tight mb-2">{currentCard.meaning}</h2>
                  <Button variant="ghost" size="icon" className="text-primary hover:bg-primary/10 rounded-full">
                    <Volume2 className="w-5 h-5" />
                  </Button>
               </div>
               <div className="flex-1 p-8 space-y-6 flex flex-col items-center justify-center max-w-md mx-auto">
                  <p className="text-xl font-jp text-gray-800 leading-relaxed font-medium">「{currentCard.example}」</p>
                  <p className="text-sm text-muted-foreground font-medium italic">"{currentCard.exampleEnglish}"</p>
               </div>
            </div>
          </motion.div>
        </div>
      </main>

      {/* Footer Actions */}
      <footer className="w-full max-w-2xl mx-auto p-8 mb-12">
        <div className="flex justify-center gap-6">
          <Button
            onClick={(e: React.MouseEvent<HTMLButtonElement>) => { e.stopPropagation(); handleNext(2, -1); }}
            variant="outline"
            className="h-16 px-10 rounded-2xl border-2 border-red-500 text-red-500 hover:bg-red-50 font-black uppercase tracking-widest text-xs gap-2 group"
          >
            <X className="w-4 h-4 group-hover:scale-125 transition-transform" />
            Hard
          </Button>
          <Button
            onClick={(e: React.MouseEvent<HTMLButtonElement>) => { e.stopPropagation(); handleNext(4, 0); }}
            variant="outline"
            className="h-16 px-10 rounded-2xl border-2 font-black uppercase tracking-widest text-xs gap-2 group"
          >
            <RotateCw className="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" />
            Good
          </Button>
          <Button
            onClick={(e: React.MouseEvent<HTMLButtonElement>) => { e.stopPropagation(); handleNext(5, 1); }}
            className="h-16 px-10 rounded-2xl bg-primary hover:bg-primary/90 shadow-xl shadow-primary/20 font-black uppercase tracking-widest text-xs gap-2 group"
          >
            <Check className="w-4 h-4 group-hover:scale-125 transition-transform" />
            Easy
          </Button>
        </div>
      </footer>
    </div>
  );
};