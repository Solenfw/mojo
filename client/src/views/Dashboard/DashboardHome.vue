<script setup lang="ts">
import { ChevronRight, Play, BookOpen, Clock, Activity } from 'lucide-vue-next'
import { useUserStore } from '@/store/useUserStore'
import DailyQuest from '@/components/gamification/DailyQuest.vue'
import XPBar from '@/components/gamification/XPBar.vue'
import LeagueBoard from '@/components/gamification/LeagueBoard.vue'

const userStore = useUserStore()
</script>

<template>
  <div class="space-y-8">
    <header>
      <h1 class="font-display text-3xl font-bold text-primary">{{ userStore.greeting }}</h1>
      <p class="text-outline mt-1 font-body">Your language journey is 65% complete. You're doing great!</p>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Main Content Card -->
      <div class="md:col-span-2 space-y-6">
        <div class="bg-white rounded-2xl p-6 neo-shadow-hover border border-surface-container relative overflow-hidden group">
          <div class="absolute -top-12 -right-12 w-48 h-48 bg-primary/5 rounded-full blur-3xl group-hover:bg-primary/10 transition-colors"></div>
          <div class="relative z-10 flex flex-col h-full">
            <div class="flex justify-between items-start">
              <span class="bg-primary/10 text-primary text-xs font-bold px-3 py-1 rounded-full uppercase tracking-tighter">JLPT N5 Path</span>
              <div class="w-12 h-12 rounded-xl bg-surface-container flex items-center justify-center">
                <span class="text-2xl font-japanese">水</span>
              </div>
            </div>
            <h2 class="font-display text-2xl font-semibold mt-4 text-primary">Today's Journey</h2>
            <p class="text-outline mt-1">Focusing on basic Kanji components and common radical variants.</p>
            
            <div class="mt-8 space-y-2">
              <div class="flex justify-between text-xs font-bold text-primary">
                <span class="font-label">Unit 4: Elements</span>
                <span>65%</span>
              </div>
              <div class="h-2 w-full bg-surface-container rounded-full overflow-hidden">
                <div class="h-full bg-secondary rounded-full" style="width: 65%"></div>
              </div>
            </div>

            <div class="mt-8 flex gap-3">
              <router-link to="/lessons" class="bg-primary text-white font-label text-sm px-6 py-3 rounded-xl shadow-lg hover:bg-primary-container transition-all flex items-center gap-2 group/btn">
                <Play :size="16" fill="currentColor" />
                Continue Path
                <ChevronRight :size="16" class="group-hover/btn:translate-x-1 transition-transform" />
              </router-link>
              <button class="border border-outline/30 text-primary font-label text-sm px-6 py-3 rounded-xl hover:bg-surface-container transition-all">
                Review Notes
              </button>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div v-for="i in 4" :key="i" class="bg-white rounded-2xl p-5 neo-shadow-hover border border-surface-container flex flex-col gap-3">
            <div class="w-10 h-10 rounded-lg bg-surface-container flex items-center justify-center">
              <BookOpen v-if="i === 1" :size="20" class="text-primary" />
              <Clock v-else-if="i === 2" :size="20" class="text-secondary" />
              <Activity v-else-if="i === 3" :size="20" class="text-primary" />
              <Play v-else :size="20" class="text-secondary" />
            </div>
            <div class="mt-2">
              <h4 class="font-display font-semibold text-sm text-primary">
                {{ i === 1 ? 'Reading' : i === 2 ? 'SRS Review' : i === 3 ? 'Grammar' : 'Speaking' }}
              </h4>
              <p class="text-xs text-outline mt-1 line-clamp-1">
                {{ i === 1 ? 'Practice native flow' : i === 2 ? 'Upcoming: 24 items' : i === 3 ? 'Mastering 〜てください' : 'Conversation simulation' }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="flex flex-col gap-6">
        <div class="bg-white rounded-2xl p-6 neo-shadow border border-surface-container">
          <XPBar />
        </div>

        <LeagueBoard />

        <div class="bg-white rounded-2xl p-6 neo-shadow border border-surface-container flex flex-col gap-6">
          <div class="flex justify-between items-center">
            <h3 class="font-display font-bold text-primary">Daily Progress</h3>
            <Activity :size="18" class="text-secondary" />
          </div>
          <div class="flex flex-col items-center justify-center py-4">
            <div class="relative w-32 h-32 flex items-center justify-center">
              <svg class="w-full h-full transform -rotate-90">
                <circle cx="64" cy="64" r="58" stroke="currentColor" stroke-width="8" fill="transparent" class="text-surface-container" />
                <circle cx="64" cy="64" r="58" stroke="currentColor" stroke-width="8" fill="transparent" stroke-dasharray="364.4" stroke-dashoffset="109.3" class="text-secondary" />
              </svg>
              <div class="absolute inset-0 flex flex-col items-center justify-center">
                <span class="text-2xl font-bold text-primary">12</span>
                <span class="text-[10px] font-bold text-outline uppercase tracking-widest">/ 15 words</span>
              </div>
            </div>
            <p class="text-xs text-outline mt-6 text-center">3 more words to hit your personal best streaks.</p>
          </div>
          <button class="w-full py-3 bg-surface-container text-primary font-label text-xs rounded-xl hover:bg-surface-container-highest transition-colors">
            View Analytics
          </button>
        </div>

        <DailyQuest />
      </div>
    </div>
  </div>
</template>

<style scoped>
.font-japanese {
  font-family: inherit;
  font-weight: 500;
}
</style>
