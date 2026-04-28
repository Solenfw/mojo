<script setup lang="ts">
import { Settings, Users, History, Award } from 'lucide-vue-next'
import { useUserStore } from '@/store/useUserStore'
import { useProgressStore } from '@/store/useProgressStore'

const userStore = useUserStore()
const progressStore = useProgressStore()

const stats = [
  { label: 'Lessons', value: progressStore.totalLessonsCompleted, icon: History },
  { label: 'Accuracy', value: `${progressStore.averageAccuracy}%`, icon: Users },
  { label: 'Mastered', value: progressStore.totalKanjiMastered, icon: Award },
]
</script>

<template>
  <div class="max-w-4xl mx-auto space-y-8">
    <!-- Profile Header -->
    <div class="relative h-48 bg-linear-to-r from-primary to-primary-container rounded-t-3xl overflow-hidden">
      <div class="absolute inset-0 opacity-10 font-japanese text-[120px] flex items-center justify-center pointer-events-none">
        日本語
      </div>
    </div>
    
    <div class="px-8 -mt-20 relative z-10 flex flex-col md:flex-row items-end gap-6">
      <div class="h-40 w-40 rounded-3xl bg-white p-2 shadow-xl">
        <div class="h-full w-full rounded-2xl bg-surface-container overflow-hidden">
          <img :src="userStore.avatar" alt="User avatar" class="h-full w-full object-cover" />
        </div>
      </div>
      
      <div class="flex-1 pb-4 flex flex-col md:flex-row justify-between items-start md:items-end gap-4 w-full">
        <div>
          <h1 class="font-display text-4xl font-black text-primary">{{ userStore.name }}</h1>
          <p class="text-outline font-bold flex items-center gap-2">
            <span class="px-2 py-0.5 bg-secondary text-white text-[10px] rounded uppercase pr-1">Pro</span>
            Current Path: {{ progressStore.currentPath }}
          </p>
        </div>
        <button class="flex items-center gap-2 px-6 py-3 bg-white rounded-xl border border-surface-container font-black text-primary font-display text-sm hover:bg-surface-container transition-all">
          <Settings :size="18" />
          Edit Profile
        </button>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 px-4">
      <div v-for="stat in stats" :key="stat.label" class="bg-white p-6 rounded-2xl border border-surface-container neo-shadow flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-surface-container flex items-center justify-center text-primary">
          <component :is="stat.icon" :size="24" />
        </div>
        <div>
          <div class="text-[10px] font-black text-outline uppercase tracking-widest">{{ stat.label }}</div>
          <div class="text-2xl font-black text-primary font-display">{{ stat.value }}</div>
        </div>
      </div>
    </div>

    <!-- Badges Section (Placeholder) -->
    <div class="bg-white rounded-3xl border border-surface-container p-8 neo-shadow">
      <h3 class="font-display text-xl font-black text-primary mb-6">Recent Achievements</h3>
      <div class="flex flex-wrap gap-4">
        <div v-for="i in 5" :key="i" class="w-20 h-20 rounded-2xl bg-surface-container flex items-center justify-center grayscale hover:grayscale-0 transition-all cursor-help opacity-40">
           <Award :size="32" class="text-outline" />
        </div>
      </div>
    </div>
  </div>
</template>
