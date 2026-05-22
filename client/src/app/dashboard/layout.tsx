'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { 
  BookOpen, 
  LayoutDashboard, 
  PenTool, 
  User, 
  Settings, 
  Zap, 
  LogOut,
  Bell,
  Search,
  Award,
  Library,
  Video,
  Book,
  Mic,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';

const MOCK_USER = {
  id: 'u1',
  name: 'Alex Johnson',
  email: 'alex@linguasphere.io',
  proficiency: 'N5',
  streak: 12,
  xp: 1250,
  avatarUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alex'
};

const Sidebar = ({ onSignOut }: { onSignOut: () => void }) => {
  const pathname = usePathname();
  const menuItems = [
    { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { href: '/dashboard/profile', icon: User, label: 'Profile' },
    { href: '/dashboard/curriculum', icon: BookOpen, label: 'Curriculum' },
    { href: '/dashboard/vocabulary', icon: Library, label: 'Vocabulary' },
    { href: '/dashboard/practice', icon: Mic, label: 'Kaiwa Partner' },
    { href: '/dashboard/reading', icon: Book, label: 'Reading' },
    { href: '/dashboard/writing', icon: PenTool, label: 'Kanji Writing' },
    { href: '/dashboard/live', icon: Video, label: 'VIP Session' },
  ];

  return (
    <div className="w-64 h-screen border-r bg-white flex flex-col sticky top-0">
      <div className="p-6 flex items-center gap-3">
        <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
          <span className="text-white font-bold text-xs">LS</span>
        </div>
        <h1 className="text-xl font-bold tracking-tighter text-primary">LinguaSphere</h1>
      </div>
      
      <ScrollArea className="flex-1 px-4">
        <div className="space-y-1 py-4">
          {menuItems.map((item) => {
            const isActive = pathname === item.href;

            return (
            <Link
              key={item.href}
              href={item.href}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-all cursor-pointer ${
                isActive 
                ? 'bg-primary text-white shadow-sm' 
                : 'text-muted-foreground hover:bg-secondary hover:text-primary'
              }`}
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </Link>
          )})}
        </div>

        <Separator className="my-4" />

        <div className="space-y-1 py-4">
          <p className="px-3 text-[10px] uppercase tracking-widest font-bold text-muted-foreground mb-2">Support</p>
          <button className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-muted-foreground hover:bg-secondary hover:text-primary transition-all cursor-pointer">
            <Settings className="w-4 h-4" />
            Settings
          </button>
          <button 
            onClick={onSignOut}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-destructive hover:bg-destructive/10 transition-all cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </ScrollArea>

      <div className="p-4 border-t">
        <div className="bg-secondary/50 rounded-lg p-4">
          <p className="text-xs font-bold text-primary mb-1">PRO SUBSCRIPTION</p>
          <p className="text-[10px] text-muted-foreground mb-3">Learn 3x faster with AI feedback</p>
          <Button className="w-full h-8 text-[11px] bg-accent hover:bg-accent/90">Upgrade Now</Button>
        </div>
      </div>
    </div>
  );
};

const Header = ({ user }: { user: typeof MOCK_USER }) => {
  return (
    <header className="h-16 border-b bg-white flex items-center justify-between px-8 sticky top-0 z-10 w-full">
      <div className="flex items-center gap-4 bg-muted/50 px-3 py-1 rounded-full border">
        <Search className="w-4 h-4 text-muted-foreground" />
        <input 
          type="text" 
          placeholder="Search lessons, kanji..." 
          className="bg-transparent border-none text-sm outline-none w-48 focus:w-64 transition-all"
        />
      </div>

      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <Zap className="w-5 h-5 text-orange-500 fill-orange-500" />
          <span className="font-bold text-sm tracking-tight">{user.streak} Days</span>
        </div>
        <div className="flex items-center gap-2">
          <Award className="w-5 h-5 text-primary fill-primary/10" />
          <span className="font-bold text-sm tracking-tight">{user.xp.toLocaleString()} XP</span>
        </div>
        <Separator orientation="vertical" className="h-6" />
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-2 right-2 w-2 h-2 bg-accent rounded-full border-2 border-white"></span>
        </Button>
        <Link href="/dashboard/profile" aria-label="Open profile">
          <Avatar className="w-8 h-8 cursor-pointer ring-2 ring-transparent hover:ring-primary transition-all">
            <AvatarImage src={user.avatarUrl} />
            <AvatarFallback>{user.name[0]}</AvatarFallback>
          </Avatar>
        </Link>
      </div>
    </header>
  );
};

const Mask = () => {
  const [visible, setVisible] = React.useState(true);

  if (!visible) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-xl max-w-sm w-full mx-4 p-6 flex flex-col gap-4">
        <div className="flex items-center gap-2">
          <span className="text-lg">⚠️</span>
          <h2 className="font-bold text-sm text-primary">Work in Progress : This is just a prototype.</h2>
        </div>
        <p className="text-xs text-muted-foreground leading-relaxed">
          Everything in the current project is a work in progress and subject to change.
          The final product may differ significantly from what is currently shown.
        </p>
        <Button className="w-full h-8 text-xs" onClick={() => setVisible(false)}>
          Got it
        </Button>
      </div>
    </div>
  );
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter();

  const handleSignOut = () => {
    // Handle sign out
    router.push('/');
  };

  return (
    <div className="flex min-h-screen bg-background font-sans">
      <Mask />
      <Sidebar onSignOut={handleSignOut} />
      <main className="flex-1 flex flex-col">
        <Header user={MOCK_USER} />
        <div className="flex-1 p-8 overflow-y-auto">
          <div className="max-w-6xl mx-auto">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
}
