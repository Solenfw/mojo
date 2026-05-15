export type JLPTLevel = 'N5' | 'N4' | 'N3' | 'N2' | 'N1';

export interface User {
  id: string;
  name: string;
  email: string;
  proficiency: JLPTLevel;
  streak: number;
  xp: number;
  avatarUrl?: string;
}

export interface Vocabulary {
  id: string;
  kanji: string;
  kana: string;
  romaji: string;
  meaning: string;
  exampleSentence: string;
  level: JLPTLevel;
  type: 'noun' | 'verb' | 'adjective' | 'adverb' | 'particle';
}

export interface Lesson {
  id: string;
  title: string;
  description: string;
  level: JLPTLevel;
  type: 'vocabulary' | 'grammar' | 'reading' | 'writing';
  items: string[]; // List of vocabulary or content IDs
  xpReward: number;
}

export interface MasteryRecord {
  vocabularyId: string;
  userId: string;
  masteryLevel: number; // 0 to 100
  lastReviewed: Date;
  nextReview: Date;
}
