import { useState } from 'react';
import { motion } from 'motion/react';
import { 
  Users, 
  BarChart3, 
  Settings, 
  LogOut, 
  Search, 
  Bell, 
  MoreHorizontal,
  ChevronDown,
  LayoutDashboard,
  Building,
  Flame,
  CheckCircle2,
  DollarSign,
  Download,
  Filter
} from 'lucide-react';
import { Button } from '@/components/ui/button';

export const AdminDashboard = ({ onSignOut }: { onSignOut: () => void }) => {
  const [viewAs, setViewAs] = useState('admin');

  const stats = [
    { label: 'Total Students', value: '12,450', growth: '+12%', icon: Users },
    { label: 'Active (Daily)', value: '3,892', growth: '+5%', icon: Flame },
    { label: 'Completion Rate', value: '68.4%', growth: 'Steady', icon: CheckCircle2 },
    { label: 'Monthly Revenue', value: '$142k', growth: '+18%', icon: DollarSign },
  ];

  const students = [
    { name: 'Anna Kowalski', email: 'anna.k@example.com', level: 'JLPT N4', progress: 75, lastActive: '2 hours ago', status: 'Active' },
    { name: 'John Smith', email: 'jsmith99@example.com', level: 'JLPT N5', progress: 30, lastActive: '3 days ago', status: 'Idle' },
    { name: 'Maria Tanaka', email: 'mtanaka@example.com', level: 'JLPT N2', progress: 92, lastActive: '10 mins ago', status: 'Active' }
  ];

  return (
    <div className="flex h-screen bg-[#f7f9fb] font-sans overflow-hidden">
      {/* Sidebar */}
      <aside className="hidden md:flex flex-col w-72 bg-[#0F172A] border-r border-[#1E293B] p-8 shrink-0">
        <div className="flex flex-col items-center text-center gap-4 mb-12">
           <div className="w-16 h-16 rounded-full bg-primary/20 border-2 border-primary/40 overflow-hidden">
              <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=admin" alt="Admin" />
           </div>
           <div>
              <h2 className="text-white font-black tracking-tight">Admin Portal</h2>
              <p className="text-[#94A3B8] text-[10px] font-bold uppercase tracking-[0.2em] mt-1">Global Administrator</p>
           </div>
        </div>

        <nav className="flex-1 space-y-2">
           <button className="w-full flex items-center gap-3 px-4 py-3 bg-primary text-white rounded-xl font-bold transition-all shadow-lg shadow-primary/20">
              <LayoutDashboard className="w-4 h-4" />
              <span className="text-sm">Overview</span>
           </button>
           {['Students', 'Companies', 'Reports', 'System'].map((item, i) => (
             <button key={item} className="w-full flex items-center gap-3 px-4 py-3 text-[#94A3B8] hover:text-white hover:bg-[#1E293B] rounded-xl font-bold transition-all">
                {i === 0 ? <Users className="w-4 h-4" /> : i === 1 ? <Building className="w-4 h-4" /> : i === 2 ? <BarChart3 className="w-4 h-4" /> : <Settings className="w-4 h-4" />}
                <span className="text-sm">{item}</span>
             </button>
           ))}
        </nav>

        <div className="pt-8 border-t border-[#1E293B]">
           <button onClick={onSignOut} className="w-full flex items-center gap-3 px-4 py-3 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-xl font-bold transition-all">
              <LogOut className="w-4 h-4" />
              <span className="text-sm">Log Out</span>
           </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <header className="h-16 bg-white border-b border-gray-100 flex items-center justify-between px-8 shrink-0">
           <div className="flex items-center gap-4">
              <h1 className="text-lg font-black text-primary tracking-tighter">Mojo</h1>
           </div>
           <div className="flex items-center gap-6">
              <div className="hidden lg:flex items-center gap-2 bg-gray-50 border border-gray-100 rounded-xl px-3 py-1.5 cursor-pointer hover:bg-gray-100 transition-all">
                 <span className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">View as:</span>
                 <span className="text-xs font-bold text-primary">Global Admin</span>
                 <ChevronDown className="w-3 h-3 text-primary" />
              </div>
              <div className="flex items-center gap-4">
                 <button className="p-2 text-gray-400 hover:text-primary transition-colors"><Bell className="w-5 h-5" /></button>
                 <div className="w-8 h-8 rounded-full bg-gray-100 border border-gray-200" />
              </div>
           </div>
        </header>

        {/* Dashboard Canvas */}
        <main className="flex-1 overflow-y-auto p-8 lg:p-12 no-scrollbar">
           <div className="max-w-7xl mx-auto space-y-12">
              
              <div className="space-y-2">
                 <h2 className="text-4xl font-black text-primary tracking-tight">System Overview</h2>
                 <p className="text-muted-foreground font-medium uppercase tracking-widest text-[10px]">Real-time insights and metrics</p>
              </div>

              {/* KPI Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                 {stats.map((s) => (
                   <div key={s.label} className="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm space-y-4 hover:shadow-lg transition-all group">
                      <div className="flex justify-between items-start">
                         <div className="p-3 bg-primary/5 rounded-2xl group-hover:bg-primary transition-colors">
                            <s.icon className="w-5 h-5 text-primary group-hover:text-white" />
                         </div>
                         <span className={`text-[10px] font-black px-2 py-1 rounded-full ${s.growth.startsWith('+') ? 'bg-emerald-50 text-emerald-600' : 'bg-gray-50 text-gray-400'}`}>
                            {s.growth}
                         </span>
                      </div>
                      <div>
                         <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest">{s.label}</p>
                         <h3 className="text-2xl font-black text-primary mt-1">{s.value}</h3>
                      </div>
                   </div>
                 ))}
              </div>

              {/* Charts Logic Placeholder - Simple Visuals */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                 <div className="bg-white rounded-[40px] border border-gray-100 p-10 h-80 flex flex-col">
                    <h3 className="text-lg font-black text-primary tracking-tight mb-8">User Engagement</h3>
                    <div className="flex-1 flex items-end justify-between gap-2 px-4">
                       {[40, 70, 45, 90, 65, 80, 55].map((h, i) => (
                         <motion.div 
                          key={i}
                          initial={{ height: 0 }}
                          animate={{ height: `${h}%` }}
                          className="flex-1 bg-primary/10 rounded-t-xl hover:bg-primary transition-colors cursor-pointer relative group"
                         >
                           <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 bg-primary text-white text-[10px] font-bold px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                              {h*120} users
                           </div>
                         </motion.div>
                       ))}
                    </div>
                    <div className="flex justify-between mt-4 px-2 text-[8px] font-black text-muted-foreground uppercase tracking-widest">
                       <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>
                    </div>
                 </div>

                 <div className="bg-white rounded-[40px] border border-gray-100 p-10 h-80 flex flex-col">
                    <h3 className="text-lg font-black text-primary tracking-tight mb-8">Course Completion</h3>
                    <div className="flex-1 flex flex-col justify-center gap-6">
                       {['JLPT N5', 'JLPT N4', 'Business', 'Reading'].map((cat, i) => (
                         <div key={cat} className="space-y-2">
                            <div className="flex justify-between text-[10px] font-black uppercase tracking-widest">
                               <span className="text-primary">{cat}</span>
                               <span className="text-muted-foreground">{90 - i*15}%</span>
                            </div>
                            <div className="h-1.5 bg-gray-50 rounded-full overflow-hidden">
                               <motion.div 
                                 initial={{ width: 0 }}
                                 animate={{ width: `${90 - i*15}%` }}
                                 className="h-full bg-accent rounded-full"
                               />
                            </div>
                         </div>
                       ))}
                    </div>
                 </div>
              </div>

              {/* Student Table */}
              <div className="bg-white rounded-[40px] border border-gray-100 shadow-xl overflow-hidden">
                 <div className="p-8 border-b border-gray-50 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6">
                    <h3 className="text-xl font-black text-primary tracking-tight">Active Student Directory</h3>
                    <div className="flex flex-wrap gap-3">
                       <div className="relative">
                          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                          <input type="text" placeholder="Search by name..." className="h-10 pl-10 pr-4 bg-gray-50 border-none rounded-xl text-xs font-bold outline-none focus:ring-2 focus:ring-primary/10 w-48" />
                       </div>
                       <Button variant="outline" className="h-10 rounded-xl border-gray-200 font-bold uppercase tracking-widest text-[9px] gap-2">
                          <Filter className="w-3 h-3" /> Filter
                       </Button>
                       <div className="flex gap-2">
                          <Button variant="outline" className="h-10 px-3 rounded-xl border-emerald-100 bg-emerald-50/50 text-emerald-600 font-bold uppercase tracking-widest text-[9px] gap-2 hover:bg-emerald-50">
                             <Download className="w-3 h-3" /> CSV
                          </Button>
                       </div>
                    </div>
                 </div>

                 <div className="overflow-x-auto">
                    <table className="w-full text-left">
                       <thead>
                          <tr className="bg-gray-50 text-[10px] font-black text-muted-foreground uppercase tracking-widest border-b border-gray-100">
                             <th className="px-8 py-4">Student</th>
                             <th className="px-8 py-4">Current Level</th>
                             <th className="px-8 py-4">Progress</th>
                             <th className="px-8 py-4">Last Activity</th>
                             <th className="px-8 py-4">Status</th>
                             <th className="px-8 py-4 text-right">Actions</th>
                          </tr>
                       </thead>
                       <tbody className="divide-y divide-gray-50">
                          {students.map((st) => (
                             <tr key={st.email} className="hover:bg-gray-50/50 transition-colors">
                                <td className="px-8 py-5">
                                   <div className="flex items-center gap-4">
                                      <div className="w-10 h-10 rounded-full bg-primary/5 flex items-center justify-center text-primary font-black text-xs">
                                         {st.name.split(' ').map(n => n[0]).join('')}
                                      </div>
                                      <div>
                                         <p className="text-sm font-black text-gray-800">{st.name}</p>
                                         <p className="text-[10px] font-bold text-muted-foreground">{st.email}</p>
                                      </div>
                                   </div>
                                </td>
                                <td className="px-8 py-5">
                                   <span className="px-2 py-1 bg-primary/5 text-primary text-[10px] font-black rounded uppercase tracking-wider">
                                      {st.level}
                                   </span>
                                </td>
                                <td className="px-8 py-5">
                                   <div className="flex items-center gap-3">
                                      <div className="w-24 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                         <div className="h-full bg-accent rounded-full" style={{ width: `${st.progress}%` }} />
                                      </div>
                                      <span className="text-[10px] font-black text-gray-500">{st.progress}%</span>
                                   </div>
                                </td>
                                <td className="px-8 py-5 text-[11px] font-medium text-gray-500">{st.lastActive}</td>
                                <td className="px-8 py-5">
                                   <div className="flex items-center gap-1.5">
                                      <div className={`w-1.5 h-1.5 rounded-full ${st.status === 'Active' ? 'bg-emerald-500' : 'bg-amber-400'}`} />
                                      <span className={`text-[10px] font-black uppercase tracking-widest ${st.status === 'Active' ? 'text-emerald-600' : 'text-amber-600'}`}>
                                         {st.status}
                                      </span>
                                   </div>
                                </td>
                                <td className="px-8 py-5 text-right">
                                   <button className="p-2 text-gray-400 hover:text-primary transition-colors"><MoreHorizontal className="w-5 h-5" /></button>
                                </td>
                             </tr>
                          ))}
                       </tbody>
                    </table>
                 </div>

                 <div className="p-8 border-t border-gray-50 flex justify-between items-center bg-gray-50/30">
                    <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Showing 3 of 12,450 results</span>
                    <div className="flex gap-2">
                       <Button variant="outline" size="sm" className="h-8 rounded-lg font-bold text-[10px] text-muted-foreground hover:text-primary uppercase tracking-widest px-4 border-none bg-white shadow-sm">Previous</Button>
                       <Button variant="ghost" size="sm" className="w-8 h-8 rounded-lg font-black text-xs bg-primary text-white shadow-md">1</Button>
                       <Button variant="ghost" size="sm" className="w-8 h-8 rounded-lg font-black text-xs text-muted-foreground hover:bg-white hover:shadow-sm">2</Button>
                       <Button variant="outline" size="sm" className="h-8 rounded-lg font-bold text-[10px] text-muted-foreground hover:text-primary uppercase tracking-widest px-4 border-none bg-white shadow-sm">Next</Button>
                    </div>
                 </div>
              </div>
           </div>
        </main>
      </div>
    </div>
  );
};
