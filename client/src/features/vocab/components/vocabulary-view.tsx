import React, { useState } from 'react';
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

interface Card {
  id: string;
  kanji: string;
  furigana: string;
  meaning: string;
  example: string;
  exampleEnglish: string;
  level: string;
}

const MOCK_CARDS: Card[] = [
  {
    id: '1',
    kanji: '経験',
    furigana: 'けいけん',
    meaning: 'Experience',
    example: '日本での経験は私にとって貴重です。',
    exampleEnglish: 'My experience in Japan is precious to me.',
    level: 'JLPT N3'
  },
  {
    id: '2',
    kanji: '準備',
    furigana: 'じゅんび',
    meaning: 'Preparation',
    example: '会議の準備をしています。',
    exampleEnglish: 'I am preparing for the meeting.',
    level: 'JLPT N4'
  },
  {
    id: '3',
    kanji: '連絡',
    furigana: 'れんらく',
    meaning: 'Contact / Communication',
    example: '後で連絡します。',
    exampleEnglish: 'I will contact you later.',
    level: 'JLPT N5'
  }
];

export const Vocabulary = ({ onBack }: { onBack: () => void }) => {
  const [cards, setCards] = useState<Card[]>(MOCK_CARDS);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [direction, setDirection] = useState(0);

  const currentCard = cards[currentIndex];

  const handleNext = (dir: number) => {
    setDirection(dir);
    setIsFlipped(false);
    setTimeout(() => {
      setCurrentIndex((prev) => (prev + 1) % cards.length);
    }, 100);
  };

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
            onClick={(e: React.MouseEvent<HTMLButtonElement>) => { e.stopPropagation(); handleNext(-1); }}
            variant="outline"
            className="h-16 px-10 rounded-2xl border-2 border-red-500 text-red-500 hover:bg-red-50 font-black uppercase tracking-widest text-xs gap-2 group"
          >
            <X className="w-4 h-4 group-hover:scale-125 transition-transform" />
            Hard
          </Button>
          <Button
            onClick={(e: React.MouseEvent<HTMLButtonElement>) => { e.stopPropagation(); handleNext(0); }}
            variant="outline"
            className="h-16 px-10 rounded-2xl border-2 font-black uppercase tracking-widest text-xs gap-2 group"
          >
            <RotateCw className="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" />
            Good
          </Button>
          <Button
            onClick={(e: React.MouseEvent<HTMLButtonElement>) => { e.stopPropagation(); handleNext(1); }}
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