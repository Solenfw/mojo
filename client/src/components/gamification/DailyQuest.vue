<script setup lang="ts">
import { Trophy, Star, Target } from 'lucide-vue-next'

const quests = [
  { id: 1, title: 'Morning Warrior', description: 'Complete 3 lessons before 10 AM', progress: 100, goal: 100, completed: true },
  { id: 2, title: 'Kanji Apprentice', description: 'Get 5 stars in Kanji writing', progress: 3, goal: 5, completed: false },
  { id: 3, title: 'Silent Listener', description: 'Complete 10 listening exercises', progress: 4, goal: 10, completed: false },
]
</script>

<template>
  <div class="bg-white rounded-2xl p-6 neo-shadow border border-surface-container">
    <div class="flex justify-between items-center mb-6">
      <h3 class="font-display font-bold text-primary flex items-center gap-2">
        <Target :size="18" class="text-secondary" />
        Daily Quests
      </h3>
      <span class="text-[10px] font-black text-outline uppercase tracking-widest">3 Items</span>
    </div>

    <div class="space-y-4">
      <div 
        v-for="quest in quests" 
        :key="quest.id"
        class="group cursor-help"
      >
        <div class="flex justify-between items-start mb-1.5">
          <div class="flex flex-col">
            <span 
              class="text-sm font-bold transition-colors"
              :class="quest.completed ? 'text-primary/40' : 'text-primary group-hover:text-secondary'"
            >
              {{ quest.title }}
            </span>
            <span class="text-[10px] text-outline font-medium">{{ quest.description }}</span>
          </div>
          <div class="flex items-center gap-1">
            <Trophy v-if="quest.completed" :size="14" class="text-yellow-500" />
            <span v-else class="text-[10px] font-bold text-primary">{{ quest.progress }}/{{ quest.goal }}</span>
          </div>
        </div>
        <div class="h-1.5 w-full bg-surface-container rounded-full overflow-hidden">
          <div 
            class="h-full transition-all duration-500"
            :class="quest.completed ? 'bg-green-500/50' : 'bg-primary'"
            :style="{ width: `${(quest.progress / quest.goal) * 100}%` }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>
