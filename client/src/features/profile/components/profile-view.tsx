'use client';

import { motion } from 'motion/react';
import { useRouter } from 'next/navigation';
import {
  Award,
  BookOpen,
  CalendarDays,
  CheckCircle2,
  Clock,
  Flame,
  Globe,
  Mail,
  MapPin,
  Mic,
  PenTool,
  ShieldCheck,
  Sparkles,
  Star,
  Target,
  Trophy,
  User,
  Zap
} from 'lucide-react';

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { User as UserType } from '@/types';

const USER: UserType = {
  id: 'u1',
  name: 'Alex Johnson',
  email: 'alex@linguasphere.io',
  proficiency: 'N5',
  streak: 12,
  xp: 1250,
  avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alex'
};

const PROFILE_DETAILS = [
  { label: 'Email', value: USER.email, icon: Mail },
  { label: 'Home Base', value: 'Bangkok, Thailand', icon: MapPin },
  { label: 'Study Goal', value: 'Professional fluency', icon: Target },
  { label: 'Interface Language', value: 'English', icon: Globe }
];

const STATS = [
  { label: 'Current Level', value: USER.proficiency, helper: 'JLPT Foundation', icon: BookOpen },
  { label: 'Active Streak', value: `${USER.streak} Days`, helper: 'Daily practice run', icon: Flame },
  { label: 'Total XP', value: USER.xp.toLocaleString(), helper: 'Top 18% this month', icon: Zap },
  { label: 'Certificates', value: '2', helper: 'Kana and Basics', icon: Trophy }
];

const SKILLS = [
  { name: 'Hiragana', value: 100 },
  { name: 'Katakana', value: 95 },
  { name: 'Vocabulary N5', value: 74 },
  { name: 'Grammar N5', value: 62 },
  { name: 'Kaiwa', value: 58 },
  { name: 'Kanji Writing', value: 45 }
];

const WEEKLY_PLAN = [
  { day: 'Mon', focus: 'Vocabulary', minutes: 30, complete: true },
  { day: 'Tue', focus: 'Kaiwa', minutes: 25, complete: true },
  { day: 'Wed', focus: 'Grammar', minutes: 35, complete: true },
  { day: 'Thu', focus: 'Reading', minutes: 20, complete: true },
  { day: 'Fri', focus: 'Kanji', minutes: 30, complete: false },
  { day: 'Sat', focus: 'Review', minutes: 45, complete: false },
  { day: 'Sun', focus: 'VIP Session', minutes: 60, complete: false }
];

const ACHIEVEMENTS = [
  { title: 'Kana Certified', description: 'Completed hiragana and katakana foundations.', icon: Award },
  { title: 'Conversation Starter', description: 'Finished five Kaiwa practice sessions.', icon: Mic },
  { title: 'Writing Momentum', description: 'Submitted ten kanji writing analyses.', icon: PenTool }
];

export const ProfileView = () => {
  const router = useRouter();
  const firstName = USER.name.split(' ')[0];
  const completedMinutes = WEEKLY_PLAN
    .filter((item) => item.complete)
    .reduce((total, item) => total + item.minutes, 0);
  const plannedMinutes = WEEKLY_PLAN.reduce((total, item) => total + item.minutes, 0);
  const weeklyProgress = Math.round((completedMinutes / plannedMinutes) * 100);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
      className="space-y-6"
    >
      <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div className="flex items-center gap-5">
          <Avatar className="w-20 h-20 ring-4 ring-secondary">
            <AvatarImage src={USER.avatarUrl} />
            <AvatarFallback>{USER.name[0]}</AvatarFallback>
          </Avatar>
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <Badge variant="secondary" className="font-bold">JLPT {USER.proficiency}</Badge>
              <Badge className="bg-accent text-white border-none font-bold">Pro</Badge>
            </div>
            <h2 className="text-3xl font-bold tracking-tighter text-primary">{USER.name}</h2>
            <p className="text-muted-foreground">Focused N5 learner building daily Japanese confidence.</p>
          </div>
        </div>

        <Button className="bg-primary group w-full sm:w-fit" onClick={() => router.push('/dashboard/curriculum')}>
          Continue {firstName}'s Plan
          <Sparkles className="ml-2 w-4 h-4 group-hover:scale-110 transition-transform" />
        </Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {STATS.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-2">
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
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <CardTitle className="text-lg font-bold flex items-center gap-2">
                  <User className="w-4 h-4 text-accent" />
                  Profile Details
                </CardTitle>
                <CardDescription>Account identity and learning preferences</CardDescription>
              </div>
              <Badge variant="outline" className="bg-primary/5 text-primary border-primary/10 font-bold">Verified Learner</Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {PROFILE_DETAILS.map((detail) => (
                <div key={detail.label} className="p-4 border rounded-lg bg-muted/20">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-8 h-8 rounded-lg bg-white border flex items-center justify-center">
                      <detail.icon className="w-4 h-4 text-primary" />
                    </div>
                    <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">{detail.label}</span>
                  </div>
                  <p className="text-sm font-bold text-primary">{detail.value}</p>
                </div>
              ))}
            </div>

            <Separator />

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="rounded-xl bg-primary text-white p-5 relative overflow-hidden">
                <Star className="absolute -right-3 -top-3 w-20 h-20 text-white/10" />
                <p className="text-[10px] font-black uppercase tracking-widest text-white/70 mb-2">Learning Track</p>
                <p className="text-lg font-bold">N5 Professional</p>
              </div>
              <div className="rounded-xl bg-secondary/50 p-5">
                <Clock className="w-5 h-5 text-primary mb-3" />
                <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground mb-2">Daily Target</p>
                <p className="text-lg font-bold text-primary">30 minutes</p>
              </div>
              <div className="rounded-xl bg-secondary/50 p-5">
                <CalendarDays className="w-5 h-5 text-primary mb-3" />
                <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground mb-2">Member Since</p>
                <p className="text-lg font-bold text-primary">Jan 2026</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-primary text-white relative overflow-hidden">
          <div className="absolute -top-5 -right-5 w-32 h-32 bg-white/10 rounded-full blur-2xl" />
          <CardHeader>
            <CardTitle className="text-lg font-bold">Weekly Focus</CardTitle>
            <CardDescription className="text-primary-foreground/70">Study minutes completed</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="bg-white/10 rounded-xl p-6 backdrop-blur-md border border-white/10 space-y-5">
              <div>
                <div className="flex items-end justify-between mb-2">
                  <span className="text-4xl font-black tracking-tight">{weeklyProgress}%</span>
                  <span className="text-[10px] font-bold uppercase tracking-widest text-white/60">{completedMinutes}/{plannedMinutes} min</span>
                </div>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <div className="h-full bg-accent rounded-full" style={{ width: `${weeklyProgress}%` }} />
                </div>
              </div>
              <div className="space-y-3">
                {WEEKLY_PLAN.map((item) => (
                  <div key={item.day} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      {item.complete ? (
                        <CheckCircle2 className="w-4 h-4 text-accent" />
                      ) : (
                        <Clock className="w-4 h-4 text-white/40" />
                      )}
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-bold">Skill Mastery</CardTitle>
            <CardDescription>Current performance across your study areas</CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            {SKILLS.map((skill) => (
              <div key={skill.name} className="space-y-2">
                <div className="flex justify-between text-xs font-medium">
                  <span className="font-jp">{skill.name}</span>
                  <span className="text-primary font-bold">{skill.value}%</span>
                </div>
                <Progress value={skill.value} className="h-1.5" />
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-bold">Achievements</CardTitle>
            <CardDescription>Milestones unlocked through consistent study</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {ACHIEVEMENTS.map((achievement) => (
              <div key={achievement.title} className="group p-4 border rounded-lg hover:border-primary hover:bg-secondary/20 transition-all">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-xl bg-primary/5 flex items-center justify-center group-hover:bg-primary transition-colors">
                    <achievement.icon className="w-5 h-5 text-primary group-hover:text-white" />
                  </div>
                  <div>
                    <h4 className="font-bold text-primary">{achievement.title}</h4>
                    <p className="text-xs text-muted-foreground leading-relaxed">{achievement.description}</p>
                  </div>
                </div>
              </div>
            ))}
            <div className="p-4 bg-secondary/50 rounded-lg flex items-center gap-3">
              <ShieldCheck className="w-5 h-5 text-primary" />
              <p className="text-xs font-bold text-primary">Account security is active with verified email access.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
};
