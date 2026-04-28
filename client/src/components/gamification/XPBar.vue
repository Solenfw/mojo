<script setup lang="ts">
import { useGamificationStore } from '@/store/useGamificationStore'

const store = useGamificationStore()

// Mock level calculation
const level = Math.floor(store.xp / 1000) + 1
const progressToNext = (store.xp % 1000) / 10
</script>

<template>
  <div class="flex flex-col gap-2 w-full">
    <div class="flex justify-between items-end">
      <div class="flex items-baseline gap-2">
        <span class="text-xs font-black text-outline uppercase tracking-widest">Level</span>
        <span class="text-2xl font-black text-primary font-display leading-none">{{ level }}</span>
      </div>
      <span class="text-[10px] font-bold text-outline">{{ store.xp }} / {{ (level) * 1000 }} XP</span>
    </div>
    
    <div class="h-3 w-full bg-surface-container rounded-full overflow-hidden neo-shadow-hover ring-4 ring-white">
      <div 
        class="h-full bg-gradient-to-r from-primary to-primary-container transition-all duration-1000 ease-out relative"
        :style="{ width: `${progressToNext}%` }"
      >
        <div class="absolute inset-0 bg-white/20 animate-pulse"></div>
      </div>
    </div>
  </div>
</template>
