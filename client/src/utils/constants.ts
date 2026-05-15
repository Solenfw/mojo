import { Vocabulary, Lesson } from '@/types';

export const N5_VOCABULARY: Vocabulary[] = [
  {
    id: 'v1',
    kanji: '私',
    kana: 'わたし',
    romaji: 'watashi',
    meaning: 'I, me',
    exampleSentence: '私は学生です。',
    level: 'N5',
    type: 'noun'
  },
  {
    id: 'v2',
    kanji: '学生',
    kana: 'がくせい',
    romaji: 'gakusei',
    meaning: 'student',
    exampleSentence: '彼は学生です。',
    level: 'N5',
    type: 'noun'
  },
  {
    id: 'v3',
    kanji: '先生',
    kana: 'せんせい',
    romaji: 'sensei',
    meaning: 'teacher',
    exampleSentence: '先生、こんにちは。',
    level: 'N5',
    type: 'noun'
  },
  {
    id: 'v4',
    kanji: '日本語',
    kana: 'にほんご',
    romaji: 'nihongo',
    meaning: 'Japanese language',
    exampleSentence: '日本語を勉強します。',
    level: 'N5',
    type: 'noun'
  },
  {
    id: 'v5',
    kanji: '勉強',
    kana: 'べんきょう',
    romaji: 'benkyou',
    meaning: 'study',
    exampleSentence: '毎日勉強します。',
    level: 'N5',
    type: 'noun'
  }
];

export const N5_LESSONS: Lesson[] = [
  {
    id: 'l1',
    title: 'Self-Introduction',
    description: 'Learn how to introduce yourself and others in Japanese.',
    level: 'N5',
    type: 'vocabulary',
    items: ['v1', 'v2', 'v3'],
    xpReward: 50
  },
  {
    id: 'l2',
    title: 'School Life',
    description: 'Vocabulary for subjects, learning, and classroom activities.',
    level: 'N5',
    type: 'vocabulary',
    items: ['v4', 'v5'],
    xpReward: 75
  }
];
