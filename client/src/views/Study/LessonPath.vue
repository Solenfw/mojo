<script setup lang="ts">
import { Star } from 'lucide-vue-next'
import ScrollingMap from '@/components/path/ScrollingMap.vue'

const units = [
  { id: 1, title: 'Greetings', status: 'completed', xOffset: 0 },
  { id: 2, title: 'Numbers', status: 'completed', xOffset: 60 },
  { id: 3, title: 'Time', status: 'completed', xOffset: -60 },
  { id: 4, title: 'Family', status: 'in-progress', xOffset: 0, isCurrent: true },
  { id: 5, title: 'Restaurant', status: 'locked', xOffset: 60 },
  { id: 6, title: 'Directions', status: 'locked', xOffset: -60 },
  { id: 7, title: 'Review', status: 'locked', xOffset: 0, isMilestone: true },
] as const
</script>

<template>
  <div class="max-w-2xl mx-auto pb-24">
    <!-- Unit Header -->
    <div class="bg-white rounded-3xl p-8 neo-shadow border border-surface-container mb-16 relative overflow-hidden group">
      <div class="absolute top-0 right-0 p-8 opacity-5">
        <span class="text-[120px] font-japanese leading-none">語</span>
      </div>
      
      <div class="relative z-10">
        <div class="flex items-center gap-2 mb-4">
          <span class="bg-primary/10 text-primary text-[10px] font-bold px-2 py-1 rounded-full uppercase tracking-tighter">Unit 1</span>
          <div class="flex gap-1">
            <div class="w-1 h-1 rounded-full bg-outline/30"></div>
            <div class="w-1 h-1 rounded-full bg-outline/30"></div>
          </div>
        </div>
        <h2 class="font-display text-3xl font-bold text-primary">Essential Conversations</h2>
        <p class="text-outline mt-2 font-body max-w-sm">Mastering common social interactions and daily survival Japanese.</p>
        
        <div class="mt-8 flex items-center gap-4">
          <div class="flex-1 h-2 bg-surface-container rounded-full overflow-hidden">
            <div class="h-full bg-secondary rounded-full" style="width: 45%"></div>
          </div>
          <span class="text-xs font-bold text-primary">45%</span>
        </div>
      </div>
    </div>

    <!-- The Path Container -->
    <ScrollingMap :nodes="units" />

    <!-- Floating Stats -->
    <div class="fixed bottom-32 right-8 z-20 hidden md:block">
      <div class="bg-white/90 backdrop-blur neo-shadow border border-surface-container p-4 rounded-2xl flex items-center gap-4">
        <div class="w-12 h-12 bg-secondary/10 rounded-xl flex items-center justify-center text-secondary">
          < Star :size="24" fill="currentColor" />
        </div>
        <div>
          <div class="text-[10px] font-black text-outline uppercase">Next Milestone</div>
          <div class="text-sm font-bold text-primary">Unit Review</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.font-japanese {
  font-family: serif;
}
</style>
