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

export interface Card {
  id: string;
  kanji: string;
  furigana: string;
  meaning: string;
  example: string;
  exampleEnglish: string;
  level: string;
}

export interface Option {
  id: number;
  text: string;
}

export interface Question {
  id: number;
  prompt: string;
  options: Option[];
}

export interface ReadingData {
  id: number;
  title: string;
  content: string;
  difficulty: string;
  passages: Array<{
    id: number;
    title: string;
    japanese: string;
    vietnamese?: string | null;
  }>;
  questions: Question[];
  words: Record<
    string,
    {
      kana: string;
      meaning: string;
      level: string;
      kanji: string;
      romaji: string;
      type: string;
    }
  >;
} 

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  translation?: string;
  romaji?: string;
}


export interface AuthToken {
  access_token: string;
  token_type: string;
  refresh_token?: string;
}

export interface CheckUserPayload {
  email?: string;
  phone?: string;
}

export interface CurrentUser {
  id: number;
  username: string;
  email: string;
  phone: string;
  is_onboarded: boolean;
}

export interface AuthPayload {
  emailOrPhone?: string;
  passwordHash: string;
  fullName?: string;
  email?: string;
  phone?: string;
  deviceId?: string;
  platform?: 'mobile' | 'web';
}

export type ErrorBag = {
  message?: string;
  detail?: string;
  errors?: Array<{ message?: string }>;
};

export interface SpeakingLesson {
  lessonId: number;
  lessonTitle: string;
  lessonOrder: number;
  estimatedDuration: number;
}

export interface DialogueTurn {
  speaker: string;
  japanese: string;
  romaji: string;
  vietnamese: string;
}

export interface Dialogue {
  title: string;
  conversation: DialogueTurn[];
}

export interface ChatMessage {
  id: string;
  speaker: string;
  role: 'assistant' | 'user';
  japanese: string;
  romaji?: string;
  vietnamese?: string;
  userTranscript?: string;
  score?: number;
  feedback?: string;
}


export interface NormalizedCard {
  id: number;
  vocab: string;
  kanji?: string;
  romaji: string;
  meaning: string;
  example?: string;
  exampleMeaning?: string;
}

export interface VocabularyDeck {
  id: string; // 'srs_due' or standard numeric lesson id
  title: string;
  description: string;
  totalItems: number;
  type: 'srs' | 'lesson';
}