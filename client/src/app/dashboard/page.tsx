'use client';

import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { useRouter } from 'next/navigation';
import { 
  MessageSquare, ChevronRight, TrendingUp, BookMarked,
  Library, Book
} from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer
} from 'recharts';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { N5_LESSONS } from '@/utils/constants';
import { Lesson } from '@/types';
import { getToken } from '@/lib/auth';

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

const DashboardContent = () => {
  const router = useRouter();
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const token = getToken();
        const res = await fetch(`${API_BASE_URL}/api/v1/users/me/dashboard`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setDashboardData(data);
        }
      } catch (err) {
        console.error("Failed to fetch dashboard data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  const handleLessonStart = (lesson: Lesson) => {
    // Navigate to actual module dynamically. For now, route to reading or vocab
    if (lesson.type === 'reading') router.push('/dashboard/reading');
    else router.push('/dashboard/vocabulary');
  };

  if (loading || !dashboardData) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <p className="text-muted-foreground font-bold animate-pulse">Loading your learning path...</p>
      </div>
    );
  }

  const { user, activity, mastery } = dashboardData;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold tracking-tighter text-primary">Konnichiwa, {user.name.split(' ')[0]}! 👋</h2>
          <p className="text-muted-foreground">You're on a {user.streak}-day heat streak. Don't break it today!</p>
        </div>
        <Button className="bg-primary group">
          Continue Learning
          <ChevronRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="col-span-2">
          <CardHeader>
            <CardTitle className="text-lg font-bold flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-accent" />
              Activity Week
            </CardTitle>
          </CardHeader>
          <CardContent className="w-full">
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={activity}>
                <defs>
                  <linearGradient id="colorXp" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00236f" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#00236f" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#888' }} />
                <YAxis hide />
                <Tooltip 
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                  labelStyle={{ fontWeight: 'bold', color: '#00236f' }}
                  cursor={{ stroke: '#00236f', strokeWidth: 1 }}
                />
                <Area type="monotone" dataKey="xp" stroke="#00236f" strokeWidth={2} fillOpacity={1} fill="url(#colorXp)" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-bold">Skills Mastery</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {mastery.map((item: any) => (
              <div key={item.module} className="space-y-2">
                <div className="flex justify-between text-xs font-medium">
                  <span className="font-jp">{item.module}</span>
                  <span className="text-primary font-bold">{item.score}%</span>
                </div>
                <Progress value={item.score} className="h-1.5" />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle className="text-lg font-bold">Recommended Lessons</CardTitle>
              <Badge variant="secondary" className="font-bold">{user.level} Path</Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {N5_LESSONS.map((lesson: Lesson) => (
              <div 
                key={lesson.id} 
                onClick={() => handleLessonStart(lesson)}
                className="group p-4 border rounded-lg hover:border-primary hover:bg-secondary/20 transition-all cursor-pointer"
              >
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-bold text-primary">{lesson.title}</h4>
                  <span className="text-[10px] font-bold bg-secondary px-2 py-0.5 rounded text-primary">+{lesson.xpReward} XP</span>
                </div>
                <p className="text-xs text-muted-foreground line-clamp-1">{lesson.description}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="bg-primary text-white overflow-hidden relative group">
          <div className="absolute -top-5 -right-5 w-32 h-32 bg-white/10 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-500"></div>
          <CardHeader>
            <CardTitle className="text-lg font-bold">Vocabulary Cards</CardTitle>
            <CardDescription className="text-primary-foreground/70">Master kanji and meanings</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="bg-white/10 rounded-xl p-6 backdrop-blur-md border border-white/10 mb-4">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 rounded-full bg-accent flex items-center justify-center shadow-lg">
                  <Library className="w-6 h-6 text-white" />
                </div>
                <div>
                  <p className="text-sm font-bold">Today's SRS Queue</p>
                  <p className="text-[11px] opacity-70 italic">Cards waiting for review</p>
                </div>
              </div>
              <Button className="w-full bg-white text-primary hover:bg-white/90 font-bold" onClick={() => router.push('/dashboard/vocabulary')}>
                Study Now
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-primary text-white overflow-hidden relative">
          <div className="absolute -top-5 -right-5 w-32 h-32 bg-white/10 rounded-full blur-2xl"></div>
          <CardHeader>
            <CardTitle className="text-lg font-bold">AI Kaiwa Partner</CardTitle>
            <CardDescription className="text-primary-foreground/70">Practice your speaking with Gemini AI</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="bg-white/10 rounded-xl p-6 backdrop-blur-md border border-white/10 mb-4">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 rounded-full bg-accent flex items-center justify-center shadow-lg">
                  <MessageSquare className="w-6 h-6 text-white" />
                </div>
                <div>
                  <p className="text-sm font-bold">New Session: Dining Out</p>
                  <p className="text-[11px] opacity-70 italic">Focus: Ordering food</p>
                </div>
              </div>
              <Button className="w-full bg-white text-primary hover:bg-white/90 font-bold" onClick={() => router.push('/dashboard/practice')}>
                Start Practice
              </Button>
            </div>
            <div className="flex items-center gap-2 text-[10px] opacity-60">
              <BookMarked className="w-3 h-3" /> Requires Microphone
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-2 border-gray-100 overflow-hidden relative group">
          <CardHeader>
            <CardTitle className="text-lg font-bold text-primary">Reading Practice</CardTitle>
            <CardDescription>Improve comprehension with articles</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-50 rounded-xl p-6 border border-gray-100 mb-4">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                  <Book className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <p className="text-sm font-bold text-gray-800">The Shinkansen</p>
                  <p className="text-[11px] text-muted-foreground uppercase font-black tracking-widest">Culture • 5 min read</p>
                </div>
              </div>
              <Button variant="outline" className="w-full border-2 hover:bg-primary hover:text-white font-bold transition-all" onClick={() => router.push('/dashboard/reading')}>
                Read Article
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default function DashboardPage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
    >
      <DashboardContent />
    </motion.div>
  );
}