<script setup lang="ts">
import { Trophy, Medal, ChevronUp } from 'lucide-vue-next'

const players = [
  { rank: 1, name: 'Yuki', xp: 12450, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Yuki' },
  { rank: 2, name: 'Kenji', xp: 11200, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Kenji' },
  { rank: 3, name: 'You', xp: 2450, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix', isUser: true },
  { rank: 4, name: 'Sora', xp: 2100, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sora' },
  { rank: 5, name: 'Miku', xp: 1800, avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Miku' },
]
</script>

<template>
  <div class="bg-white rounded-2xl p-6 neo-shadow border border-surface-container">
    <div class="flex justify-between items-center mb-6">
      <h3 class="font-display font-bold text-primary flex items-center gap-2">
        <Medal :size="18" class="text-secondary" />
        Bronze League
      </h3>
      <span class="text-[10px] font-black text-outline uppercase tracking-widest">Ends in 2d 4h</span>
    </div>

    <div class="space-y-3">
      <div 
        v-for="player in players" 
        :key="player.rank"
        class="flex items-center gap-3 p-2 rounded-xl transition-colors"
        :class="player.isUser ? 'bg-primary/5 ring-1 ring-primary/10' : 'hover:bg-surface-container'"
      >
        <span class="w-4 text-xs font-black text-outline">{{ player.rank }}</span>
        <div class="h-8 w-8 rounded-lg bg-surface-container overflow-hidden">
          <img :src="player.avatar" :alt="player.name" />
        </div>
        <div class="flex-1">
          <div class="text-sm font-bold text-primary">{{ player.name }}</div>
          <div class="text-[10px] font-bold text-outline">{{ player.xp }} XP</div>
        </div>
        <ChevronUp v-if="player.rank <= 3" :size="14" class="text-green-500" />
      </div>
    </div>

    <button class="w-full mt-6 py-3 bg-surface-container text-primary font-label text-xs rounded-xl hover:bg-surface-container-highest transition-colors uppercase tracking-widest font-black">
      View Full Leaderboard
    </button>
  </div>
</template>
