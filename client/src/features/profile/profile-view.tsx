'use client';

import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { useRouter } from 'next/navigation';
import {
  BookOpen, CalendarDays, CheckCircle2, Clock, Flame, Globe, Mail,
  MapPin, Sparkles, Star, Target, Trophy, User, Zap
} from 'lucide-react';

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { getToken } from '@/lib/auth';

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

const WEEKLY_PLAN = [
  { day: 'Mon', focus: 'Vocabulary', minutes: 30, complete: true },
  { day: 'Tue', focus: 'Kaiwa', minutes: 25, complete: true },
  { day: 'Wed', focus: 'Grammar', minutes: 35, complete: true },
  { day: 'Thu', focus: 'Reading', minutes: 20, complete: true },
  { day: 'Fri', focus: 'Kanji', minutes: 30, complete: false },
  { day: 'Sat', focus: 'Review', minutes: 45, complete: false },
  { day: 'Sun', focus: 'Speaking', minutes: 60, complete: false }
];

export const ProfileView = () => {
  const router = useRouter();
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = getToken();
        const res = await fetch(`${API_BASE_URL}/api/v1/users/me/profile`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setProfile(data);
        }
      } catch (err) {
        console.error("Failed to fetch profile:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  if (loading || !profile) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <p className="text-muted-foreground font-bold animate-pulse">Loading Profile...</p>
      </div>
    );
  }

  const completedMinutes = WEEKLY_PLAN.filter(i => i.complete).reduce((t, i) => t + i.minutes, 0);
  const plannedMinutes = WEEKLY_PLAN.reduce((t, i) => t + i.minutes, 0);
  const weeklyProgress = Math.round((completedMinutes / plannedMinutes) * 100);

  const PROFILE_DETAILS = [
    { label: 'Email', value: profile.email, icon: Mail },
    { label: 'Phone', value: profile.phone, icon: MapPin },
    { label: 'Study Goal', value: profile.study_goal, icon: Target },
    { label: 'Interface Language', value: 'English', icon: Globe }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      {/* Top Profile Summary Header */}
      <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div className="flex items-center gap-5">
          <Avatar className="w-20 h-20 ring-4 ring-secondary">
            <AvatarImage src={profile.avatarUrl} />
            <AvatarFallback>{profile.name[0].toUpperCase()}</AvatarFallback>
          </Avatar>
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <Badge variant="secondary" className="font-bold">JLPT {profile.current_level}</Badge>
              <Badge className="bg-primary text-white border-none font-bold">Active Learner</Badge>
            </div>
            <h2 className="text-3xl font-bold tracking-tighter text-primary">{profile.name}</h2>
            <p className="text-muted-foreground">Target Level: JLPT {profile.target_level}</p>
          </div>
        </div>

        <Button className="bg-primary group w-full sm:w-fit" onClick={() => router.push('/dashboard/curriculum')}>
          Continue Curriculum
          <Sparkles className="ml-2 w-4 h-4 group-hover:scale-110 transition-transform" />
        </Button>
      </div>

      {/* KPI Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { label: 'Current Level', value: `JLPT ${profile.current_level}`, helper: 'current level', icon: BookOpen },
          { label: 'Active Streak', value: `${profile.streak} Days`, helper: 'Active Streak', icon: Flame },
          { label: 'Total XP', value: profile.xp.toLocaleString(), helper: 'Total XP', icon: Zap },
          { label: 'Target Level', value: `JLPT ${profile.target_level}`, helper: 'Target Level', icon: Trophy }
        ].map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-5">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest">{stat.label}</p>
                  <h3 className="text-2xl font-black text-primary tracking-tight">{stat.value}</h3>
                  <p className="text-[10px] font-bold text-muted-foreground">{stat.helper}</p>
                </div>
                <div className="w-10 h-10 rounded-xl bg-primary/5 flex items-center justify-center">
                  <stat.icon className="w-5 h-5 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Profile Details Panel */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <CardTitle className="text-lg font-bold flex items-center gap-2">
                  <User className="w-4 h-4 text-accent" /> Profile Details
                </CardTitle>
                <CardDescription>Account information and learning path orientation</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {PROFILE_DETAILS.map((detail) => (
                <div key={detail.label} className="p-4 border rounded-lg bg-muted/20">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-8 h-8 rounded-lg bg-white border flex items-center justify-center shadow-xs">
                      <detail.icon className="w-4 h-4 text-primary" />
                    </div>
                    <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">{detail.label}</span>
                  </div>
                  <p className="text-sm font-bold text-primary">{detail.value}</p>
                </div>
              ))}
            </div>
            
            <Separator />
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="rounded-xl bg-primary text-white p-5 relative overflow-hidden">
                <Star className="absolute -right-3 -top-3 w-20 h-20 text-white/10" />
                <p className="text-[10px] font-black uppercase tracking-widest text-white/70 mb-2">Learning Path Orientation</p>
                <p className="text-lg font-bold">Career Goals & Daily Life</p>
              </div>
              <div className="rounded-xl bg-secondary/50 p-5">
                <CalendarDays className="w-5 h-5 text-primary mb-3" />
                <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground mb-2">Member Since</p>
                <p className="text-lg font-bold text-primary">{profile.member_since}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Weekly Focus & Commitments */}
        <Card className="bg-primary text-white relative overflow-hidden">
          <div className="absolute -top-5 -right-5 w-32 h-32 bg-white/10 rounded-full blur-2xl" />
          <CardHeader>
            <CardTitle className="text-lg font-bold">Weekly Training Path</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-white/10 rounded-xl p-6 backdrop-blur-md border border-white/10 space-y-5">
              <div>
                <div className="flex items-end justify-between mb-2">
                  <span className="text-4xl font-black tracking-tight">{weeklyProgress}%</span>
                  <span className="text-[10px] font-bold uppercase tracking-widest text-white/60">{completedMinutes}/{plannedMinutes} minutes</span>
                </div>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <div className="h-full bg-accent rounded-full" style={{ width: `${weeklyProgress}%` }} />
                </div>
              </div>
              <div className="space-y-3">
                {WEEKLY_PLAN.map((item) => (
                  <div key={item.day} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      {item.complete ? <CheckCircle2 className="w-4 h-4 text-accent" /> : <Clock className="w-4 h-4 text-white/40" />}
                      <span className="font-bold">{item.day}</span>
                      <span className="text-white/60">{item.focus}</span>
                    </div>
                    <span className="text-[10px] font-bold text-white/60">{item.minutes}m</span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
};