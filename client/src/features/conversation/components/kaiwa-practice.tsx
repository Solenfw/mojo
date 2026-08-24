import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  Mic,
  MicOff,
  Volume2,
  Bot,
  User,
  Settings,
  X,
  Play,
  RotateCcw,
  Lightbulb,
  BookOpen,
  Award,
  ChevronRight,
  Sparkles,
  CheckCircle,
  HelpCircle,
  Keyboard,
  ArrowRight
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { getToken } from '@/lib/auth';
import { SpeakingLesson, Dialogue, DialogueTurn, ChatMessage } from '@/types';

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

export const KaiwaPractice = ({ onBack }: { onBack: () => void }) => {
  // Navigation & Mode states
  const [screen, setScreen] = useState<'lessons' | 'dialogue-practice' | 'results'>('lessons');
  const [lessons, setLessons] = useState<SpeakingLesson[]>([]);
  const [selectedLesson, setSelectedLesson] = useState<SpeakingLesson | null>(null);
  const [dialogue, setDialogue] = useState<Dialogue | null>(null);

  // Practice Flow states
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [currentLineIndex, setCurrentLineIndex] = useState(0);
  const [appRole, setAppRole] = useState<string>('');
  
  // Microphone & Speech States
  const [isRecording, setIsRecording] = useState(false);
  const [recognitionSupported, setRecognitionSupported] = useState(true);
  const [transcript, setTranscript] = useState('');
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [manualInput, setManualInput] = useState('');
  const [showManualInput, setShowManualInput] = useState(false);
  const [scores, setScores] = useState<number[]>([]);

  // Feedback states
  const [currentTurnFeedback, setCurrentTurnFeedback] = useState<{
    score: number;
    feedback: string;
    isCorrect: boolean;
  } | null>(null);

  const scrollRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  // Initialize Speech Recognition
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.lang = 'ja-JP';
      rec.continuous = false;
      rec.interimResults = false;

      rec.onstart = () => {
        setIsRecording(true);
        setTranscript('');
      };

      rec.onresult = (event: any) => {
        const text = event.results[0][0].transcript;
        setTranscript(text);
        void evaluateUserSpeech(text);
      };

      rec.onerror = (event: any) => {
        console.error("Speech recognition error", event.error);
        setIsRecording(false);
      };

      rec.onend = () => {
        setIsRecording(false);
      };

      recognitionRef.current = rec;
    } else {
      setRecognitionSupported(false);
    }
  }, [screen, currentLineIndex]);

  // Fetch Speaking Lessons on Load
  useEffect(() => {
    const fetchLessons = async () => {
      try {
        const token = getToken();
        const res = await fetch(`${API_BASE_URL}/api/v1/lessons/speaking?course_id=1`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const json = await res.json();
          setLessons(json.data || []);
        }
      } catch (err) {
        console.error("Failed to load speaking lessons:", err);
      }
    };
    void fetchLessons();
  }, []);

  // Auto-scroll chat history
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const speakJapanese = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'ja-JP';
      
      const voices = window.speechSynthesis.getVoices();
      const jaVoice = voices.find(voice => voice.lang.startsWith('ja'));
      if (jaVoice) {
        utterance.voice = jaVoice;
      }
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleSelectLesson = async (lesson: SpeakingLesson) => {
    setSelectedLesson(lesson);
    try {
      const token = getToken();
      const res = await fetch(`${API_BASE_URL}/api/v1/lessons/${lesson.lessonId}/speaking`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const json = await res.json();
        const dialogues = json.data?.dialogues || [];
        if (dialogues.length > 0) {
          const firstDialogue = dialogues[0];
          setDialogue(firstDialogue);
          setScreen('dialogue-practice');
          
          // Setup state for new practice flow
          setChatHistory([]);
          setScores([]);
          setCurrentLineIndex(0);
          setCurrentTurnFeedback(null);
          
          // Identify speaker roles dynamically:
          // The first speaker is played by the App (Assistant). Others areplayed by the User.
          const firstSpeaker = firstDialogue.conversation[0]?.speaker || 'A';
          setAppRole(firstSpeaker);

          // Run the first turn
          setTimeout(() => {
            void runConversationTurn(0, firstDialogue.conversation, firstSpeaker);
          }, 500);
        }
      }
    } catch (err) {
      console.error("Failed to load dialogue details:", err);
    }
  };

  const runConversationTurn = (index: number, conversation: DialogueTurn[], botRole: string) => {
    if (index >= conversation.length) {
      setScreen('results');
      return;
    }

    const currentLine = conversation[index];
    
    if (currentLine.speaker === botRole) {
      // App (Bot) Turn
      const newMsg: ChatMessage = {
        id: `bot-${index}-${Date.now()}`,
        speaker: currentLine.speaker,
        role: 'assistant',
        japanese: currentLine.japanese,
        romaji: currentLine.romaji,
        vietnamese: currentLine.vietnamese
      };

      setChatHistory(prev => [...prev, newMsg]);
      speakJapanese(currentLine.japanese);

      // Auto-advance to the next line (User turn) after audio read and a brief pause
      setTimeout(() => {
        setCurrentLineIndex(index + 1);
        runConversationTurn(index + 1, conversation, botRole);
      }, 3500);
    } else {
      // User Turn: Wait for user interaction
      setCurrentLineIndex(index);
      setCurrentTurnFeedback(null);
      setTranscript('');
      setManualInput('');
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      recognitionRef.current?.stop();
    } else {
      try {
        recognitionRef.current?.start();
      } catch (err) {
        console.error("Recognition start failed", err);
        setIsRecording(false);
      }
    }
  };

  const simulateUserSpeech = () => {
    if (!dialogue) return;
    const currentLine = dialogue.conversation[currentLineIndex];
    // Simply submit expected Japanese as transcribed output
    void evaluateUserSpeech(currentLine.japanese);
  };

  const handleManualSubmit = () => {
    if (!manualInput.trim()) return;
    setShowManualInput(false);
    void evaluateUserSpeech(manualInput);
  };

  const evaluateUserSpeech = async (spokenText: string) => {
    if (!dialogue) return;
    const currentLine = dialogue.conversation[currentLineIndex];
    setIsEvaluating(true);

    try {
      const token = getToken();
      const res = await fetch(`${API_BASE_URL}/api/v1/speaking/evaluate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          expected_text: currentLine.japanese,
          transcript: spokenText,             // key mới đổi từ user_transcript sang transcript
          romaji: currentLine.romaji
        })
      });

      if (res.ok) {
        const rating = await res.json(); // Nhận về cấu trúc gộp: score, feedback, is_correct, v.v.
        
        setCurrentTurnFeedback({
          score: rating.score,
          feedback: rating.feedback,
          isCorrect: rating.is_correct
        });

        setScores(prev => [...prev, rating.score]);

        // Append User Speech message to Chat History log
        const userMsg: ChatMessage = {
          id: `user-${currentLineIndex}-${Date.now()}`,
          speaker: currentLine.speaker,
          role: 'user',
          japanese: currentLine.japanese,
          userTranscript: spokenText,
          score: rating.score,
          feedback: rating.feedback
        };
        setChatHistory(prev => [...prev, userMsg]);
      }
    } catch (err) {
      console.error("Error rating pronunciation:", err);
    } finally {
      setIsEvaluating(false);
    }
  };

  const handleNextLine = () => {
    if (!dialogue) return;
    const nextIndex = currentLineIndex + 1;
    setCurrentTurnFeedback(null);
    setCurrentLineIndex(nextIndex);
    void runConversationTurn(nextIndex, dialogue.conversation, appRole);
  };

  const handleRepeatLine = (text: string) => {
    speakJapanese(text);
  };

  const getAverageScore = () => {
    if (scores.length === 0) return 0;
    const sum = scores.reduce((a, b) => a + b, 0);
    return Math.round(sum / scores.length);
  };

  return (
    <div className="fixed inset-0 h-screen bg-[#f7f9fb] flex flex-col font-sans z-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 flex justify-between items-center px-6 h-16 w-full shrink-0 shadow-xs">
        <div className="flex items-center gap-4">
          <button 
            onClick={() => {
              if (screen !== 'lessons') {
                setScreen('lessons');
              } else {
                onBack();
              }
            }} 
            className="text-gray-500 hover:text-primary transition-colors p-2 rounded-full hover:bg-gray-100"
          >
            <X className="w-5 h-5" />
          </button>
          <div className="h-6 w-px bg-gray-200 mx-2"></div>
          <h1 className="text-lg font-bold text-primary tracking-tight">Mojo</h1>
          <Badge className="bg-accent/15 text-accent border-none font-bold text-[10px] tracking-widest px-3 py-1 uppercase">
            Kaiwa Partner
          </Badge>
        </div>
      </header>

      <AnimatePresence mode="wait">
        {/* SCREEN 1: LESSON SELECTION */}
        {screen === 'lessons' && (
          <motion.main 
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            className="flex-1 overflow-y-auto p-8 max-w-4xl mx-auto w-full space-y-8"
          >
            <div className="text-center space-y-3">
              <Badge className="bg-primary/10 text-primary border-primary/20 hover:bg-primary/20 font-bold uppercase tracking-widest">
                JLPT N5 Speaking Path
              </Badge>
              <h2 className="text-4xl font-black text-primary tracking-tight">Practicing Conversational Japanese dialogues with AI</h2>
              <p className="text-muted-foreground max-w-lg mx-auto font-medium">
                Choose a real-world conversational scenario below to start practicing your speaking skills with our AI assistant.
              </p>
              </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {lessons.map((lesson) => (
                <Card 
                  key={lesson.lessonId}
                  className="hover:shadow-xl hover:border-primary/40 transition-all duration-300 group cursor-pointer border-gray-100 rounded-3xl"
                  onClick={() => void handleSelectLesson(lesson)}
                >
                  <CardContent className="p-6 flex flex-col justify-between h-full space-y-6">
                    <div className="flex justify-between items-start">
                      <div className="p-3 bg-secondary rounded-2xl group-hover:bg-primary group-hover:text-white transition-colors duration-300">
                        <BookOpen className="w-6 h-6 text-primary group-hover:text-white" />
                      </div>
                      <Badge variant="outline" className="text-[10px] font-bold text-muted-foreground uppercase border-gray-200">
                        {lesson.estimatedDuration} phút
                      </Badge>
                    </div>

                    <div className="space-y-2">
                      <span className="text-[10px] font-black uppercase text-accent tracking-[0.2em]">Lesson {lesson.lessonOrder}</span>
                      <h3 className="text-xl font-bold text-primary tracking-tight leading-snug group-hover:text-accent transition-colors">
                        {lesson.lessonTitle}
                      </h3>
                    </div>

                    <div className="flex items-center gap-2 text-xs font-bold text-primary group-hover:gap-3 transition-all pt-2">
                      Start the dialogue
                      <ChevronRight className="w-4 h-4" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </motion.main>
        )}

        {/* SCREEN 2: ACTIVE PRACTICE FLOW */}
        {screen === 'dialogue-practice' && dialogue && (
          <motion.main 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex-1 flex flex-col lg:flex-row w-full overflow-hidden"
          >
            {/* Left Panel: Conversation log */}
            <div className="flex-1 flex flex-col bg-white border-r border-gray-100 relative h-full">
              <div className="p-6 border-b border-gray-50 flex justify-between items-center bg-gray-50/50 shrink-0">
                <div>
                  <h2 className="text-xl font-black text-primary tracking-tight">{selectedLesson?.lessonTitle}</h2>
                  <p className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">{dialogue.title}</p>
                </div>
                <Badge className="bg-emerald-50 text-emerald-600 border border-emerald-100 font-bold uppercase text-[9px]">
                  Auto-play Pronunciation
                </Badge>
              </div>

              {/* Chat View */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6 pb-24 no-scrollbar" ref={scrollRef}>
                {chatHistory.map((msg, idx) => (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    {msg.role === 'assistant' && (
                      <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center shrink-0 border shadow-xs">
                        <Bot className="w-4 h-4 text-primary" />
                      </div>
                    )}
                    <div className={`max-w-xl rounded-2xl p-5 border transition-all ${
                      msg.role === 'assistant'
                        ? 'bg-gray-50 border-gray-100'
                        : 'bg-indigo-50/50 border-indigo-100 shadow-xs'
                    }`}>
                      <div className="flex items-center justify-between gap-12 mb-2">
                        <span className="text-[9px] font-black uppercase tracking-widest text-primary/60">
                          {msg.speaker}
                        </span>
                        {msg.role === 'user' && msg.score !== undefined && (
                          <Badge className="bg-accent text-white border-none font-black text-[9px]">
                            {msg.score}/100 points
                          </Badge>
                        )}
                        {msg.role === 'assistant' && (
                          <button 
                            onClick={() => handleRepeatLine(msg.japanese)} 
                            className="p-1 hover:bg-gray-200/50 rounded-full text-primary transition-colors"
                          >
                            <Volume2 className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                      <p className="text-2xl font-jp mb-2 text-primary leading-tight font-medium">
                        {msg.japanese}
                      </p>
                      {msg.role === 'user' && msg.userTranscript && (
                        <div className="mt-2 text-xs border-t border-indigo-100/50 pt-2 space-y-1">
                          <p className="font-bold text-indigo-900/60">Speech Recognized:</p>
                          <p className="font-jp text-indigo-900 italic">"{msg.userTranscript}"</p>
                        </div>
                      )}
                      {msg.romaji && <p className="text-xs text-primary/60 italic font-medium">{msg.romaji}</p>}
                      {msg.vietnamese && <p className="text-xs text-muted-foreground mt-2 border-t pt-2 border-gray-100">{msg.vietnamese}</p>}
                    </div>
                  </motion.div>
                ))}
                
                {isEvaluating && (
                  <div className="flex justify-end gap-4 animate-pulse">
                    <div className="max-w-xl flex-1 bg-gray-50 border rounded-2xl h-24" />
                  </div>
                )}
              </div>
            </div>

            {/* Right Panel: Active Action Card */}
            <div className="w-full lg:w-112.5 bg-[#f8fafc] border-t lg:border-t-0 flex flex-col shrink-0 justify-between">
              
              {/* Top: Current Prompt Display */}
              <div className="p-8 space-y-6 flex-1 overflow-y-auto no-scrollbar">
                <div className="space-y-2 text-center lg:text-left">
                  <span className="text-[10px] font-black uppercase text-accent tracking-[0.25em]">It's your turn to speak</span>
                  <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest">
                    Turn {currentLineIndex + 1} of {dialogue.conversation.length}
                  </h3>
                </div>

                {dialogue.conversation[currentLineIndex] && (
                  <Card className="border-none shadow-lg rounded-3xl overflow-hidden bg-white">
                    <CardContent className="p-8 space-y-6">
                      <div className="space-y-2 text-center">
                        <span className="text-[9px] font-black uppercase text-primary/40 tracking-wider">Correct Speaking Example:</span>
                        <h4 className="text-3xl font-jp font-black text-primary leading-snug">
                          {dialogue.conversation[currentLineIndex].japanese}
                        </h4>
                        <p className="text-sm font-medium text-primary/70 italic">
                          {dialogue.conversation[currentLineIndex].romaji}
                        </p>
                      </div>

                      <div className="p-4 bg-secondary/30 rounded-2xl text-center border">
                        <span className="text-[9px] font-black uppercase text-primary/40 tracking-wider block mb-1">Vietnamese Meaning:</span>
                        <p className="text-xs text-primary font-bold">
                          {dialogue.conversation[currentLineIndex].vietnamese}
                        </p>
                      </div>

                      <div className="flex justify-center">
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          onClick={() => handleRepeatLine(dialogue.conversation[currentLineIndex].japanese)}
                          className="text-primary hover:bg-secondary text-[10px] font-bold uppercase tracking-widest gap-2"
                        >
                          <Volume2 className="w-4 h-4" />
                          Auto-play Pronunciation
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Score and Vietnamese Feedback Panel */}
                <AnimatePresence mode="wait">
                  {currentTurnFeedback && (
                    <motion.div
                      initial={{ opacity: 0, y: 15 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="bg-white rounded-3xl p-6 border shadow-lg space-y-4"
                    >
                      <div className="flex items-center justify-between border-b pb-4">
                        <div className="flex items-center gap-2">
                          <Award className="w-5 h-5 text-accent" />
                          <span className="text-xs font-black uppercase tracking-wider text-primary">Pronunciation Score</span>
                        </div>
                        <span className="text-3xl font-black text-accent">{currentTurnFeedback.score}/100</span>
                      </div>
                      
                      <div className="flex gap-3">
                        <div className="p-2 bg-emerald-50 rounded-xl shrink-0">
                          <Lightbulb className="w-5 h-5 text-emerald-500" />
                        </div>
                        <div className="space-y-1">
                          <span className="text-[10px] font-black uppercase tracking-widest text-emerald-600">Feedback from Sensei</span>
                          <p className="text-xs font-semibold text-gray-700 leading-relaxed">
                            {currentTurnFeedback.feedback}
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Bottom: Interactive Recording and Controls */}
              <div className="p-8 bg-white border-t border-gray-100 flex flex-col gap-6">
                
                {/* Fallback Manual Input Field Toggle */}
                {showManualInput && (
                  <motion.div 
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="space-y-2"
                  >
                    <label className="text-[9px] font-black uppercase text-muted-foreground tracking-widest">No microphone? Enter Japanese text:</label>
                    <div className="flex gap-2">
                      <input 
                        type="text"
                        value={manualInput}
                        onChange={(e) => setManualInput(e.target.value)}
                        placeholder="Ví dụ: はい、ホットコーヒーを..."
                        className="flex-1 border rounded-xl px-4 h-12 text-sm outline-none focus:border-primary"
                      />
                      <Button onClick={handleManualSubmit} className="bg-primary h-12 rounded-xl font-bold text-xs uppercase px-4">Send</Button>
                    </div>
                  </motion.div>
                )}

                <div className="flex items-center justify-center gap-6 w-full">
                  {/* Simulate speak button - extremely useful for testing without mic setup */}
                  <button 
                    onClick={simulateUserSpeech}
                    className="flex flex-col items-center gap-1.5 group outline-none"
                    title="Simulate Accurate Pronunciation"
                  >
                    <div className="w-10 h-10 rounded-full border border-gray-200 group-hover:bg-primary/5 group-hover:border-primary flex items-center justify-center transition-all bg-white shadow-xs">
                      <Sparkles className="w-4 h-4 text-gray-400 group-hover:text-primary" />
                    </div>
                    <span className="text-[8px] font-black uppercase tracking-widest text-muted-foreground group-hover:text-primary">Simulate</span>
                  </button>

                  {/* Main Record Trigger */}
                  {currentTurnFeedback ? (
                    // Proceed to the next dialogue segment
                    <Button 
                      onClick={handleNextLine}
                      className="w-20 h-20 rounded-full bg-accent hover:bg-accent/90 shadow-xl shadow-accent/25 flex items-center justify-center border-4 border-white transition-all group"
                    >
                      <ArrowRight className="w-8 h-8 text-white group-hover:translate-x-0.5 transition-transform" />
                    </Button>
                  ) : (
                    // Capture User audio
                    <button
                      onClick={toggleRecording}
                      disabled={isEvaluating}
                      className="relative outline-none"
                    >
                      <div className={`absolute inset-0 bg-accent transition-all duration-500 rounded-full ${isRecording ? 'opacity-20 scale-150 animate-ping' : 'opacity-0 scale-110'}`} />
                      <div className={`w-20 h-20 rounded-full flex items-center justify-center shadow-xl relative z-10 border-4 border-white transition-all ${
                        isRecording ? 'bg-red-600 scale-105' : 'bg-accent hover:bg-accent/90'
                      }`}>
                        {isRecording ? (
                          <MicOff className="w-8 h-8 text-white animate-pulse" />
                        ) : (
                          <Mic className="w-8 h-8 text-white" />
                        )}
                      </div>
                    </button>
                  )}

                  {/* Keyboard input option toggler */}
                  <button 
                    onClick={() => setShowManualInput(!showManualInput)}
                    className="flex flex-col items-center gap-1.5 group outline-none"
                  >
                    <div className={`w-10 h-10 rounded-full border flex items-center justify-center transition-all bg-white shadow-xs ${
                      showManualInput ? 'border-primary bg-primary/5 text-primary' : 'border-gray-200 text-gray-400 group-hover:text-primary group-hover:border-primary'
                    }`}>
                      <Keyboard className="w-4 h-4" />
                    </div>
                    <span className="text-[8px] font-black uppercase tracking-widest text-muted-foreground group-hover:text-primary">Enter Text</span>
                  </button>
                </div>

                <div className="text-center">
                  <p className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">
                    {currentTurnFeedback 
                      ? "Press the red button to proceed to the next line" 
                      : isRecording 
                        ? "Recording... Please speak the sentence above into the microphone" 
                        : "Press the microphone button to start recording"
                    }
                  </p>
                </div>
              </div>
            </div>
          </motion.main>
        )}

        {/* SCREEN 3: RESULTS SUMMARY */}
        {screen === 'results' && (
          <motion.main 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="flex-1 overflow-y-auto p-8 max-w-xl mx-auto w-full flex flex-col justify-center items-center py-16"
          >
            <div className="bg-white rounded-[40px] border border-gray-100 shadow-2xl p-12 text-center w-full space-y-8 relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-2 bg-linear-to-r from-emerald-500 to-primary" />
              
              <div className="w-20 h-20 bg-emerald-50 rounded-full flex items-center justify-center mx-auto shadow-xs border border-emerald-100">
                <CheckCircle className="w-10 h-10 text-emerald-500" />
              </div>

              <div className="space-y-2">
                <Badge className="bg-emerald-50 text-emerald-600 border-none font-bold uppercase text-[10px] tracking-widest px-3 py-1">
                  Conversation Completed!
                </Badge>
                <h2 className="text-3xl font-black text-primary tracking-tight">Script Completed</h2>
                <p className="text-sm text-muted-foreground font-medium">
                  Congratulations! You have completed the conversational practice session.
                </p>
              </div>

              {/* Central circular score graph */}
              <div className="flex justify-center py-4">
                <div className="relative w-40 h-40 flex items-center justify-center">
                  <svg className="w-full h-full absolute inset-0 transform -rotate-90" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="45" fill="none" stroke="#E2E8F0" strokeWidth="6" />
                    <motion.circle
                      cx="50"
                      cy="50"
                      r="45"
                      fill="none"
                      stroke="#10b981"
                      strokeWidth="6"
                      strokeLinecap="round"
                      initial={{ strokeDasharray: "282.7", strokeDashoffset: "282.7" }}
                      animate={{ strokeDashoffset: (282.7 - (282.7 * getAverageScore()) / 100) }}
                      transition={{ duration: 1.2, ease: "easeOut" }}
                    />
                  </svg>
                  <div className="flex flex-col items-center justify-center">
                    <span className="text-5xl font-black text-emerald-500">{getAverageScore()}</span>
                    <span className="text-[9px] font-black uppercase tracking-widest text-muted-foreground mt-1">AVERAGE SCORE</span>
                  </div>
                </div>
              </div>

              {/* Awarded XP Summary Card */}
              <div className="p-5 bg-[#f8fafc] rounded-2xl border flex justify-between items-center max-w-sm mx-auto">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center text-white shadow-md">
                    <Award className="w-5 h-5" />
                  </div>
                  <div className="text-left">
                    <p className="text-xs font-bold text-primary">Awarded Practice Points</p>
                    <p className="text-[10px] text-muted-foreground uppercase font-black tracking-wider">Conversational Practice</p>
                  </div>
                </div>
                <span className="bg-emerald-500 text-white font-black text-xs px-3 py-1 rounded-lg">
                  +50 XP
                </span>
              </div>

              <div className="pt-4 flex flex-col gap-3">
                <Button 
                  onClick={() => setScreen('lessons')} 
                  className="w-full h-12 bg-primary hover:bg-primary/95 font-bold uppercase text-[10px] tracking-widest rounded-xl transition-all"
                >
                  Practice Different Script
                </Button>
                <Button 
                  onClick={onBack} 
                  variant="outline"
                  className="w-full h-12 border-2 text-muted-foreground font-bold uppercase text-[10px] tracking-widest rounded-xl hover:bg-gray-50"
                >
                  Return to Dashboard
                </Button>
              </div>
            </div>
          </motion.main>
        )}
      </AnimatePresence>
    </div>
  );
};