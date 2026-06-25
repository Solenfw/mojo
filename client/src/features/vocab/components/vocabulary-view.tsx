'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  ChevronRight, 
  Library, 
  CheckCircle2, 
  ChevronLeft, 
  Volume2, 
  Award,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { getToken } from '@/lib/auth';
import { VocabularyDeck, NormalizedCard} from '@/types';

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

export function Vocabulary({ onBack }: { onBack: () => void }) {
  const [screen, setScreen] = useState<'decks' | 'flashcards' | 'results'>('decks');
  const [decks, setDecks] = useState<VocabularyDeck[]>([]);
  const [selectedDeck, setSelectedDeck] = useState<VocabularyDeck | null>(null);
  const [cards, setCards] = useState<NormalizedCard[]>([]);
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [isFlipped, setIsFlipped] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [sessionXp, setSessionXp] = useState<number>(0);

  // --- API CALL: FETCH OVERVIEW SET LIST ---
  useEffect(() => {
    const fetchDecks = async () => {
      try {
        const token = getToken();
        setLoading(true);

        // 1. Fetch due SRS counts
        const srsRes = await fetch(`${API_BASE_URL}/api/v1/srs/due`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const dueItems = srsRes.ok ? await srsRes.json() : [];

        // 2. Fetch standard N5 Course Lessons
        const courseRes = await fetch(`${API_BASE_URL}/api/v1/courses/by-level?targetLevel=N5`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }).then(r => r.json());
        
        const courseId = courseRes.data?.[0]?.courseId;
        let lessonsDecks: VocabularyDeck[] = [];

        if (courseId) {
          const lessonsRes = await fetch(`${API_BASE_URL}/api/v1/courses/lessons?recommendedCourseId=${courseId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
          }).then(r => r.json());
          
          lessonsDecks = (lessonsRes.data || [])
            .filter((l: any) => l.lessonType === 'vocabulary')
            .map((l: any) => ({
              id: l.lessonId.toString(),
              title: l.lessonTitle,
              description: `Structured curriculum vocabulary lesson.`,
              totalItems: l.estimatedDuration, // approximate count of concepts
              type: 'lesson'
            }));
        }

        const combinedDecks: VocabularyDeck[] = [
          {
            id: 'srs_due',
            title: 'Adaptive Due Queue (SRS)',
            description: 'Intelligent review scheduling based on your retention rate.',
            totalItems: dueItems.length,
            type: 'srs'
          },
          ...lessonsDecks
        ];

        setDecks(combinedDecks);
      } catch (err) {
        console.error("Failed to load vocabulary decks", err);
      } finally {
        setLoading(false);
      }
    };
    
    if (screen === 'decks') {
      fetchDecks();
    }
  }, [screen]);

  // --- API CALL: LOAD DECK ITEMS ---
  const handleSelectDeck = async (deck: VocabularyDeck) => {
    setSelectedDeck(deck);
    setLoading(true);
    setSessionXp(0);

    try {
      const token = getToken();
      let rawCards: any[] = [];

      if (deck.type === 'srs') {
        const res = await fetch(`${API_BASE_URL}/api/v1/srs/due`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) rawCards = await res.json();
      } else {
        const res = await fetch(`${API_BASE_URL}/api/v1/lessons/${deck.id}/vocabulary`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          rawCards = data.items || [];
        }
      }

      // Normalize different backend payloads to a uniform structure
      const normalized: NormalizedCard[] = rawCards.map((c) => ({
        id: parseInt(c.vocab_id || c.id || Math.floor(Math.random() * 100000)),
        vocab: c.vocab || c.furigana || '',
        kanji: (c.kanji && c.kanji !== c.vocab && c.kanji !== c.furigana) ? c.kanji : undefined,
        romaji: c.romaji || '',
        meaning: c.meaning || '',
        example: c.example || c.example_sentence || '',
        exampleMeaning: c.exampleEnglish || c.example_meaning || '',
      }));

      setCards(normalized);
      setCurrentIndex(0);
      setIsFlipped(false);
      setScreen('flashcards');
    } catch (err) {
      console.error("Error loading items:", err);
    } finally {
      setLoading(false);
    }
  };

  // --- API CALL: SUBMIT PERFORMANCE METRIC ---
  const handleReviewScore = async (qualityScore: number) => {
    if (!selectedDeck || cards.length === 0) return;
    const currentCard = cards[currentIndex];
    const token = getToken();

    try {
      if (selectedDeck.type === 'srs') {
        // Post review results directly to the fixed SM-2 API endpoint
        await fetch(`${API_BASE_URL}/api/v1/srs/review`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            vocab_id: currentCard.id,
            quality_score: qualityScore
          })
        });
      }
      
      // Award progress XP
      setSessionXp(prev => prev + (qualityScore >= 3 ? 10 : 2));

      // Advance
      if (currentIndex < cards.length - 1) {
        setIsFlipped(false);
        setCurrentIndex(prev => prev + 1);
      } else {
        // Complete Lesson and post learned items
        if (selectedDeck.type === 'lesson') {
          await fetch(`${API_BASE_URL}/api/v1/lessons/${selectedDeck.id}/complete`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
              xp_gained: sessionXp + 15,
              vocab_learned: cards.map(c => c.id)
            })
          });
        }
        setScreen('results');
      }
    } catch (err) {
      console.error("Error recording vocabulary performance", err);
    }
  };

  const handleSpeak = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'ja-JP';
      window.speechSynthesis.speak(utterance);
    }
  };

  if (loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <p className="text-muted-foreground font-bold animate-pulse">Loading Vocabulary Modules...</p>
      </div>
    );
  }

  const currentCard = cards[currentIndex];

  return (
    <div className="max-w-4xl mx-auto space-y-6 py-4 font-sans">
      <AnimatePresence mode="wait">
        
        {/* VIEW 1: DECK OVERVIEW LISTING SCREEN */}
        {screen === 'decks' && (
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            className="space-y-8"
          >
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-black text-primary tracking-tight">Vocabulary Training</h2>
                <p className="text-muted-foreground font-medium">Select a focused lesson or practice with Spaced Repetition.</p>
              </div>
              <Button variant="ghost" className="gap-2 text-muted-foreground hover:text-primary" onClick={onBack}>
                <ChevronLeft className="w-4 h-4" /> Back to Dashboard
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {decks.map((deck) => (
                <Card 
                  key={deck.id}
                  onClick={() => handleSelectDeck(deck)}
                  className={`hover:shadow-xl hover:border-primary/40 transition-all duration-300 group cursor-pointer border-gray-100 rounded-3xl ${
                    deck.type === 'srs' ? 'bg-secondary/40 border-primary/20' : 'bg-white'
                  }`}
                >
                  <CardContent className="p-6 flex flex-col justify-between h-56">
                    <div className="flex justify-between items-start">
                      <div className="p-3 bg-white rounded-2xl border shadow-sm group-hover:bg-primary group-hover:text-white transition-colors duration-300">
                        <Library className="w-6 h-6 text-primary group-hover:text-white" />
                      </div>
                      <Badge className={`${
                        deck.type === 'srs' ? 'bg-orange-500 text-white' : 'bg-primary text-white'
                      } border-none font-bold uppercase tracking-wider text-[9px]`}>
                        {deck.type === 'srs' ? 'SRS Active' : 'CURRICULUM'}
                      </Badge>
                    </div>

                    <div className="space-y-1">
                      <h3 className="text-xl font-bold text-primary group-hover:text-accent transition-colors">{deck.title}</h3>
                      <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">{deck.description}</p>
                    </div>

                    <div className="flex items-center justify-between border-t pt-4">
                      <span className="text-xs font-bold text-muted-foreground">{deck.totalItems} elements queue</span>
                      <span className="text-xs font-bold text-primary flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
                        Study Now <ChevronRight className="w-4 h-4" />
                      </span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </motion.div>
        )}

        {/* VIEW 2: FLASHCARD STUDY SESSION */}
        {screen === 'flashcards' && currentCard && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="max-w-2xl mx-auto space-y-6"
          >
            <div className="flex items-center justify-between">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setScreen('decks')}
                className="text-xs font-bold uppercase tracking-widest text-muted-foreground hover:text-primary"
              >
                ← Exit Session
              </Button>
              <span className="text-xs font-mono font-bold text-muted-foreground">
                Card {currentIndex + 1} of {cards.length}
              </span>
            </div>

            <Progress value={((currentIndex + 1) / cards.length) * 100} className="h-2 bg-gray-100 rounded-full" />

            {/* Flashcard Component with Interactive Flipping */}
            <div 
              onClick={() => !isFlipped && setIsFlipped(true)}
              className={`w-full min-h-85 bg-white rounded-4xl border p-8 flex flex-col justify-between transition-all duration-300 select-none ${
                isFlipped 
                  ? 'border-gray-100 shadow-sm' 
                  : 'border-primary/20 shadow-md hover:border-primary/50 cursor-pointer'
              }`}
            >
              {/* FRONT: Vocab + Kanji + Romaji */}
              <div className="text-center my-auto space-y-4">
                <div className="flex justify-center items-center gap-3">
                  <h1 className="text-4xl md:text-5xl font-black text-primary font-jp">
                    {currentCard.vocab}
                  </h1>
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSpeak(currentCard.vocab);
                    }}
                    className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                  >
                    <Volume2 className="w-5 h-5 text-primary" />
                  </button>
                </div>

                {currentCard.kanji && (
                  <p className="text-2xl font-bold text-muted-foreground font-jp">{currentCard.kanji}</p>
                )}

                <p className="text-xs font-mono font-black tracking-widest text-muted-foreground/60 uppercase">
                  {currentCard.romaji}
                </p>
              </div>

              {/* BACK: English meaning & context sentence */}
              {isFlipped ? (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-6 pt-6 border-t border-gray-100 space-y-5"
                >
                  <div className="text-center">
                    <span className="text-[10px] font-black tracking-widest text-primary uppercase block mb-1">Definition</span>
                    <p className="text-2xl font-black text-gray-900 leading-tight">{currentCard.meaning}</p>
                  </div>

                  {currentCard.example && (
                    <div className="bg-secondary/35 border border-primary/5 p-4 rounded-2xl space-y-1 text-left relative overflow-hidden">
                      <span className="text-[9px] font-black tracking-widest text-primary/60 uppercase block mb-1">Context Example</span>
                      <p className="text-sm font-bold text-primary font-jp leading-relaxed">{currentCard.example}</p>
                      {currentCard.exampleMeaning && <p className="text-xs text-muted-foreground leading-relaxed">{currentCard.exampleMeaning}</p>}
                    </div>
                  )}
                </motion.div>
              ) : (
                <div className="text-center text-[10px] font-black text-muted-foreground/40 uppercase tracking-widest animate-pulse">
                  Click flashcard to flip and reveal answer
                </div>
              )}
            </div>

            {/* SRS Retention Quality Score Controls */}
            {isFlipped && (
              <div className="grid grid-cols-3 gap-3 pt-2">
                <Button 
                  onClick={() => handleReviewScore(1)}
                  className="h-16 rounded-2xl bg-red-50 border border-red-200 text-red-600 hover:bg-red-100/70 flex flex-col items-center justify-center gap-0.5 shadow-none"
                >
                  <span className="text-xs font-black uppercase tracking-wider">Forgot</span>
                  <span className="text-[9px] font-mono opacity-60">Grade 1</span>
                </Button>
                
                <Button 
                  onClick={() => handleReviewScore(3)}
                  className="h-16 rounded-2xl bg-amber-50 border border-amber-200 text-amber-600 hover:bg-amber-100/70 flex flex-col items-center justify-center gap-0.5 shadow-none"
                >
                  <span className="text-xs font-black uppercase tracking-wider">Hard</span>
                  <span className="text-[9px] font-mono opacity-60">Grade 3</span>
                </Button>

                <Button 
                  onClick={() => handleReviewScore(5)}
                  className="h-16 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-600 hover:bg-emerald-100/70 flex flex-col items-center justify-center gap-0.5 shadow-none"
                >
                  <span className="text-xs font-black uppercase tracking-wider">Easy</span>
                  <span className="text-[9px] font-mono opacity-60">Grade 5</span>
                </Button>
              </div>
            )}
          </motion.div>
        )}

        {/* VIEW 3: RESULTS SUMMARY SCREEN */}
        {screen === 'results' && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="max-w-xl mx-auto text-center space-y-8 bg-white rounded-[40px] border border-gray-100 shadow-2xl p-12 relative overflow-hidden"
          >
            <div className="absolute top-0 left-0 w-full h-2 bg-linear-to-r from-emerald-500 to-primary" />

            <div className="w-20 h-20 bg-emerald-50 rounded-full flex items-center justify-center mx-auto shadow-xs border border-emerald-100">
              <CheckCircle2 className="w-10 h-10 text-emerald-500" />
            </div>

            <div className="space-y-2">
              <Badge className="bg-emerald-50 text-emerald-600 border-none font-bold uppercase text-[10px] tracking-widest px-3 py-1">
                STUDY DECK COMPLETED!
              </Badge>
              <h2 className="text-3xl font-black text-primary tracking-tight">Active Learning Session Complete</h2>
              <p className="text-sm text-muted-foreground font-medium">
                Awesome! You studied all vocabulary cards scheduled in this deck segment.
              </p>
            </div>

            <div className="p-5 bg-[#f8fafc] rounded-2xl border flex justify-between items-center max-w-sm mx-auto">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center text-white shadow-md">
                  <Award className="w-5 h-5" />
                </div>
                <div className="text-left">
                  <p className="text-xs font-bold text-primary">Awarded Session XP</p>
                  <p className="text-[10px] text-muted-foreground uppercase font-black tracking-wider">Vocabulary Study</p>
                </div>
              </div>
              <span className="bg-emerald-500 text-white font-black text-xs px-3 py-1 rounded-lg">
                +{sessionXp} XP
              </span>
            </div>

            <div className="pt-4 flex flex-col gap-3">
              <Button 
                onClick={() => setScreen('decks')} 
                className="w-full h-12 bg-primary hover:bg-primary/95 font-bold uppercase text-[10px] tracking-widest rounded-xl transition-all"
              >
                Back to Decks
              </Button>
              <Button 
                onClick={onBack} 
                variant="outline"
                className="w-full h-12 border-2 text-muted-foreground font-bold uppercase text-[10px] tracking-widest rounded-xl hover:bg-gray-50"
              >
                Return to Dashboard
              </Button>
            </div>
          </motion.div>
        )}

      </AnimatePresence>
    </div>
  );
}