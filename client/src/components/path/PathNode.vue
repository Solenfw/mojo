<script setup lang="ts">
import { Play, Lock, CheckCircle2 } from 'lucide-vue-next'

defineProps<{
  id: number
  title: string
  status: 'completed' | 'in-progress' | 'locked'
  xOffset: number
  isCurrent?: boolean
  isMilestone?: boolean
}>()
</script>

<template>
  <div 
    class="relative z-10 transition-transform duration-500"
    :style="{ transform: `translateX(${xOffset}px)` }"
  >
    <!-- Milestone Node -->
    <div v-if="isMilestone" class="relative group">
      <div 
        class="w-24 h-24 rounded-full flex items-center justify-center border-4 border-white shadow-xl text-white transition-all duration-300"
        :class="status === 'locked' ? 'bg-outline/20' : 'bg-primary-container'"
      >
        <slot name="icon">
          <CheckCircle2 :size="40" :class="status === 'locked' ? 'opacity-30' : 'text-secondary-container'" />
        </slot>
      </div>
      <div class="absolute -bottom-10 left-1/2 -translate-x-1/2 whitespace-nowrap">
        <span class="text-[10px] font-black text-outline uppercase tracking-widest">{{ title }}</span>
      </div>
    </div>

    <!-- Regular Lesson Node -->
    <div v-else class="relative group">
      <router-link
        to="/lesson/session"
        class="w-20 h-20 rounded-full flex items-center justify-center border-4 border-white shadow-lg transition-all duration-300 relative"
        :class="[
          status === 'completed' ? 'bg-primary text-white hover:bg-primary/90' : 
          status === 'in-progress' ? 'bg-secondary text-white node-pulse scale-110 hover:scale-115' : 
          'bg-surface-container text-outline/30 cursor-not-allowed pointer-events-none'
        ]"
      >
        <CheckCircle2 v-if="status === 'completed'" :size="32" />
        <Play v-else-if="status === 'in-progress'" :size="32" fill="currentColor" />
        <Lock v-else :size="24" />

        <!-- Tooltip/Label for In-Progress -->
        <div 
          v-if="isCurrent"
          class="absolute -right-32 top-1/2 -translate-y-1/2 bg-white px-4 py-2 rounded-xl shadow-lg border border-secondary/20 flex items-center gap-3 whitespace-nowrap animate-in fade-in"
        >
          <div class="w-2 h-2 bg-secondary rounded-full"></div>
          <span class="text-xs font-bold text-primary">{{ title }}</span>
        </div>
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.node-pulse {
  box-shadow: 0 0 0 0 rgba(134, 78, 90, 0.4);
  animation: pulse 2.5s infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(134, 78, 90, 0.4); }
  70% { box-shadow: 0 0 0 20px rgba(134, 78, 90, 0); }
  100% { box-shadow: 0 0 0 0 rgba(134, 78, 90, 0); }
}
</style>
