import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  ChevronRight,
  Book,
  Star as StarIcon
} from 'lucide-react';
import { Button } from '@/components/ui/button';

export const Reading = ({ onBack }: { onBack: () => void }) => {
  const [showPopup, setShowPopup] = useState<string | null>(null);

  const words = {
    '新幹線': { kana: 'しんかんせん', meaning: 'bullet train', level: 'N4' },
    '到着': { kana: 'とうちゃく', meaning: 'arrival', level: 'N4' },
    '切符': { kana: 'きっぷ', meaning: 'ticket', level: 'N5' }
  };

  return (
    <div className="flex h-screen bg-[#f7f9fb] font-sans selection:bg-primary/10">
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Content */}
        <main className="flex-1 overflow-y-auto p-8 lg:p-12 no-scrollbar">
          <div className="max-w-5xl mx-auto flex flex-col lg:flex-row gap-12 items-start">

            {/* Article */}
            <div className="flex-1 space-y-12">
               <article className="bg-white rounded-[40px] border border-gray-100 shadow-2xl p-12 relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-2 bg-linear-to-r from-primary to-accent" />

                  <div className="flex items-center gap-3 mb-8">
                     <span className="px-2 py-1 bg-primary/10 text-primary text-[10px] font-black rounded uppercase tracking-widest">JLPT N4</span>
                     <span className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Culture & Daily Life</span>
                  </div>

                  <header className="mb-12">
                     <h1 className="text-5xl font-jp text-primary font-black leading-tight">日本の新幹線</h1>
                     <p className="text-xl text-muted-foreground font-medium mt-3 italic">The Japanese Shinkansen</p>
                  </header>

                  <div className="space-y-8 text-2xl font-jp leading-[1.8] text-gray-800">
                    <p>
                        日本の
                        <span className="relative inline-block mx-1 group">
                          <span
                            onMouseEnter={() => setShowPopup('新幹線')}
                            onMouseLeave={() => setShowPopup(null)}
                            className="bg-primary/5 text-primary border-b-2 border-primary/20 border-dashed px-1 cursor-help hover:bg-primary/10 transition-all"
                          >新幹線</span>
                          <AnimatePresence>
                            {showPopup === '新幹線' && (
                              <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="absolute bottom-full left-1/2 -translate-x-1/2 mb-4 w-56 bg-white rounded-2xl shadow-2xl border border-primary/10 p-5 z-20 pointer-events-none"
                              >
                                <div className="text-center border-b pb-3 mb-3">
                                  <p className="text-xs font-bold text-muted-foreground tracking-widest mb-1">{words['新幹線'].kana}</p>
                                  <p className="text-2xl font-black text-primary">{showPopup}</p>
                                </div>
                                <div className="text-center">
                                  <p className="text-sm font-bold text-gray-700">{words['新幹線'].meaning}</p>
                                  <span className="inline-block px-1.5 py-0.5 bg-gray-100 text-gray-500 text-[8px] font-black rounded uppercase mt-2">{words['新幹線'].level}</span>
                                </div>
                                <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-white" />
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </span>
                        は、とても速くて便利な乗り物です。最初の新幹線は1964年にできました。
                    </p>
                    <p>
                        東京から大阪まで、約2時間半で
                        <span className="relative inline-block mx-1 group">
                          <span className="bg-primary/5 text-primary border-b-2 border-primary/20 border-dashed px-1 cursor-help">到着</span>
                        </span>
                        します。時間がとても正確で、安全なことで世界中で有名です。
                    </p>
                    <p>
                        新幹線に乗る時は、特別な
                        <span className="relative inline-block mx-1 group">
                          <span className="bg-primary/5 text-primary border-b-2 border-primary/20 border-dashed px-1 cursor-help">切符</span>
                        </span>
                        を買わなければなりません。駅で買ったお弁当を食べるのが好きです。
                    </p>
                  </div>
               </article>

               {/* Quiz */}
               <section className="bg-white rounded-[40px] border border-gray-100 shadow-2xl p-12 space-y-8">
                  <div className="space-y-2">
                    <h2 className="text-3xl font-black text-primary tracking-tight">Comprehension Check</h2>
                    <p className="text-sm font-bold text-muted-foreground uppercase tracking-widest italic">Testing your understanding of the text</p>
                  </div>

                  <div className="space-y-12">
                    {[
                      { q: "最初の新幹線はいつできましたか。", a: ["1954年", "1964年", "1984年"] },
                      { q: "新幹線は何で有名ですか。", a: ["時間が正確で安全", "切符が安い", "走るのが遅い"] }
                    ].map((item, i) => (
                      <div key={i} className="space-y-6">
                        <p className="text-xl font-jp font-bold text-gray-800 flex gap-4">
                          <span className="w-8 h-8 rounded-full bg-primary/5 text-primary flex items-center justify-center text-sm shrink-0 border border-primary/10">{i+1}</span>
                          {item.q}
                        </p>
                        <div className="grid gap-3 pl-12">
                          {item.a.map((ans, j) => (
                            <button key={j} className="text-left py-4 px-6 rounded-2xl border border-gray-100 hover:border-primary hover:bg-primary/5 transition-all font-jp font-medium text-gray-600 group flex items-center justify-between">
                              {ans}
                              <ChevronRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                            </button>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="pt-8 flex justify-end">
                    <Button className="h-14 px-10 bg-accent hover:bg-accent/90 rounded-2xl font-black uppercase tracking-widest text-xs gap-3 shadow-xl shadow-accent/20">
                      Submit Answers
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
               </section>
            </div>

            {/* Right Panel: Vocabulary List */}
            <aside className="w-full lg:w-72 shrink-0 space-y-8">
               <div className="bg-white rounded-3xl border border-gray-100 shadow-xl p-8 sticky top-8">
                  <div className="flex items-center gap-3 mb-8 pb-4 border-b border-gray-50">
                    <Book className="w-5 h-5 text-primary" />
                    <h3 className="font-black text-primary tracking-tight">Vocabulary</h3>
                  </div>
                  <div className="space-y-6">
                    {Object.entries(words).map(([kanji, data]) => (
                      <div key={kanji} className="group">
                        <div className="flex justify-between items-start mb-1">
                          <span className="text-lg font-jp font-black text-gray-800">{kanji}</span>
                          <span className="text-[8px] font-black uppercase bg-gray-50 px-1.5 py-0.5 rounded text-muted-foreground">{data.level}</span>
                        </div>
                        <p className="text-[10px] font-bold text-primary/40 uppercase tracking-widest">{data.kana}</p>
                        <p className="text-xs font-bold text-gray-500 mt-1">{data.meaning}</p>
                      </div>
                    ))}
                  </div>
                  <Button variant="outline" className="w-full mt-10 rounded-xl font-bold uppercase tracking-widest text-[9px] h-10 border-accent text-accent hover:bg-accent/5">
                    Save to library
                  </Button>
               </div>

               <div className="bg-primary rounded-3xl p-8 text-white space-y-4 shadow-2xl shadow-primary/30 relative overflow-hidden group">
                  <StarIcon className="absolute -top-2.5 -right-2.5 w-32 h-32 text-white/5 rotate-12 group-hover:scale-110 transition-transform" />
                  <h4 className="font-black text-lg leading-tight uppercase tracking-tight">VIP Coaching</h4>
                  <p className="text-xs font-medium text-white/70 leading-relaxed">Struggling with this text? Get a 1-on-1 session with a Sensei now.</p>
                  <Button className="w-full bg-white text-primary hover:bg-white/90 rounded-xl font-black uppercase text-[10px] tracking-widest h-12 mt-4">
                    Book Sensei
                  </Button>
               </div>
            </aside>

          </div>
        </main>
      </div>
    </div>
  );
};