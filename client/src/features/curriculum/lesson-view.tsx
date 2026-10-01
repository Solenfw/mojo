import { useState } from 'react';
import { motion } from 'motion/react';
import {
  Volume2,
  CheckCircle2,
  Info,
  PlayCircle,
  Lightbulb,
  ChevronLeft
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Lesson } from '@/types';
import { N5_VOCABULARY } from '@/utils/constants';

interface LessonViewProps {
  lesson: Lesson;
  onBack: () => void;
  onComplete: () => void;
}

export const LessonView = ({ lesson, onBack, onComplete }: LessonViewProps) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [completedItems, setCompletedItems] = useState<string[]>([]);

  const vocabItems = N5_VOCABULARY.filter(v => lesson.items.includes(v.id));
  const currentItem = vocabItems[currentIndex];

  const progress = (completedItems.length / vocabItems.length) * 100;

  const handleNext = () => {
    if (!completedItems.includes(currentItem.id)) {
      setCompletedItems([...completedItems, currentItem.id]);
    }

    if (currentIndex < vocabItems.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else if (completedItems.length + 1 >= vocabItems.length) {
      onComplete();
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 py-4">
      <div className="flex items-center justify-between">
        <Button variant="ghost" className="gap-2 text-muted-foreground hover:text-primary" onClick={onBack}>
          <ChevronLeft className="w-4 h-4" />
          Back to Dashboard
        </Button>
        <div className="flex items-center gap-4 w-64">
          <Progress value={progress} className="h-2" />
          <span className="text-xs font-bold text-muted-foreground whitespace-nowrap">
            {completedItems.length} / {vocabItems.length}
          </span>
        </div>
      </div>

      <div className="text-center space-y-2">
        <Badge className="bg-primary/10 text-primary border-primary/20 hover:bg-primary/20">{lesson.level} Module</Badge>
        <h2 className="text-4xl font-bold tracking-tighter text-primary">{lesson.title}</h2>
        <p className="text-muted-foreground">{lesson.description}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center pt-8">
        <motion.div
          key={currentItem.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-6"
        >
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <h3 className="text-7xl font-bold font-jp text-primary">{currentItem.kanji}</h3>
              <Button variant="outline" size="icon" className="rounded-full w-12 h-12 bg-secondary/50 border-primary/10 hover:bg-secondary">
                <Volume2 className="w-6 h-6 text-primary" />
              </Button>
            </div>
            <div className="space-y-1">
              <p className="text-2xl font-medium text-muted-foreground font-jp">{currentItem.kana}</p>
              <p className="text-lg text-muted-foreground italic">({currentItem.romaji})</p>
            </div>
          </div>

          <div className="p-6 bg-secondary/30 rounded-2xl border border-primary/5">
            <h4 className="text-xs font-bold uppercase tracking-widest text-primary/60 mb-2">English Meaning</h4>
            <p className="text-2xl font-bold text-primary">{currentItem.meaning}</p>
          </div>

          <Card className="border-none bg-muted/50 shadow-none">
            <CardContent className="p-4 flex gap-3 italic text-sm text-muted-foreground">
              <Lightbulb className="w-5 h-5 text-accent shrink-0" />
              "{currentItem.exampleSentence}"
            </CardContent>
          </Card>
        </motion.div>

        <div className="bg-white rounded-3xl p-8 border shadow-xl shadow-primary/5 space-y-6">
          <div className="space-y-4">
            <h4 className="font-bold flex items-center gap-2">
              <Info className="w-4 h-4 text-primary" />
              Cultural Context
            </h4>
            <p className="text-sm text-muted-foreground leading-relaxed">
              In Japanese business culture, {currentItem.meaning === 'student' ? 'students often respect their teachers with deep bows' : 'referring to oneself clearly is essential for establishing professional hierarchy'}. Using "{currentItem.kanji}" correctly signifies your awareness of social standing.
            </p>
          </div>

          <Separator />

          <div className="space-y-4">
            <h4 className="font-bold flex items-center gap-2">
              <PlayCircle className="w-4 h-4 text-primary" />
              Practice Tip
            </h4>
            <ul className="space-y-2">
              <li className="flex items-center gap-2 text-xs text-muted-foreground">
                <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                Focus on the rhythm of "{currentItem.kana}"
              </li>
              <li className="flex items-center gap-2 text-xs text-muted-foreground">
                <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                The stroke order of "{currentItem.kanji}" starts from top-left.
              </li>
            </ul>
          </div>

          <Button
            className="w-full h-14 text-lg bg-primary hover:bg-primary/90 rounded-xl"
            onClick={handleNext}
          >
            {currentIndex < vocabItems.length - 1 ? 'Next Item' : 'Finish Lesson'}
          </Button>
        </div>
      </div>
    </div>
  );
};
