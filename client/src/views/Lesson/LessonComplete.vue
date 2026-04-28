<script setup lang="ts">
import { CheckCircle2, Star, Zap, Award } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

defineProps<{
  stats: {
    xp: number
    accuracy: number
    time: string
  }
}>()

const router = useRouter()
</script>

<template>
  <div class="fixed inset-0 bg-white z-70 flex flex-col items-center justify-center p-6 bg-linear-to-b from-white to-surface-container">
    <div class="max-w-md w-full space-y-12 text-center animate-in fade-in zoom-in duration-500">
      <header class="space-y-4">
        <div class="relative inline-block">
          <div class="w-32 h-32 bg-secondary rounded-full flex items-center justify-center text-white shadow-2xl relative z-10">
            <CheckCircle2 :size="64" />
          </div>
          <div class="absolute -top-4 -right-4 w-12 h-12 bg-primary rounded-full flex items-center justify-center text-white shadow-lg animate-bounce">
            <Star :size="24" fill="currentColor" />
          </div>
        </div>
        <h1 class="font-display text-4xl font-black text-primary tracking-tight">Lesson Complete!</h1>
        <p class="text-outline font-medium">You're one step closer to fluency.</p>
      </header>

      <div class="grid grid-cols-3 gap-4">
        <div class="bg-white p-4 rounded-2xl shadow-sm border border-surface-container space-y-1">
          <div class="flex justify-center text-orange-500">
            <Zap :size="20" fill="currentColor" />
          </div>
          <div class="text-xl font-black text-primary">{{ stats.xp }}</div>
          <div class="text-[10px] font-black text-outline uppercase tracking-widest">Total XP</div>
        </div>
        
        <div class="bg-white p-4 rounded-2xl shadow-sm border border-surface-container space-y-1">
          <div class="flex justify-center text-primary">
            <Award :size="20" />
          </div>
          <div class="text-xl font-black text-primary">{{ stats.accuracy }}%</div>
          <div class="text-[10px] font-black text-outline uppercase tracking-widest">Accuracy</div>
        </div>

        <div class="bg-white p-4 rounded-2xl shadow-sm border border-surface-container space-y-1">
          <div class="flex justify-center text-secondary">
            <Star :size="20" fill="currentColor" />
          </div>
          <div class="text-xl font-black text-primary">{{ stats.time }}</div>
          <div class="text-[10px] font-black text-outline uppercase tracking-widest">Time</div>
        </div>
      </div>

      <div class="pt-8 space-y-4">
        <button 
          @click="router.push('/')"
          class="w-full py-4 bg-primary text-white font-black font-display uppercase tracking-wider rounded-2xl shadow-[0_4px_0_0_#000333] hover:translate-y-0.5 hover:shadow-[0_2px_0_0_#000333] transition-all"
        >
          Continue
        </button>
        <button 
          @click="router.push('/lessons')"
          class="w-full py-4 bg-white text-primary border-2 border-surface-container font-black font-display uppercase tracking-wider rounded-2xl hover:bg-surface-container transition-all"
        >
          Review Mistakes
        </button>
      </div>
    </div>
  </div>
</template>
