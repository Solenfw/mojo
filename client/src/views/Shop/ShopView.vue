<script setup lang="ts">
import { Sparkles, ShoppingBag, Zap, Heart, Shield } from 'lucide-vue-next'
import { useGamificationStore } from '@/store/useGamificationStore'

const store = useGamificationStore()

const items = [
  { id: 1, name: 'Streak Freeze', price: 200, icon: Shield, desc: 'Protects your streak if you miss a day.' },
  { id: 2, name: 'Refill Hearts', price: 100, icon: Heart, desc: 'Instantly restore all hearts.' },
  { id: 3, name: 'Double XP', price: 50, icon: Zap, desc: 'Double your XP for the next 30 mins.' },
]
</script>

<template>
  <div class="space-y-8">
    <header class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-8 rounded-3xl border border-surface-container neo-shadow">
      <div>
        <h1 class="font-display text-3xl font-bold text-primary flex items-center gap-3">
          <ShoppingBag :size="32" class="text-secondary" />
          Linguasphere Shop
        </h1>
        <p class="text-outline mt-1 font-body">Use your hard-earned gems to boost your progress.</p>
      </div>
      <div class="flex items-center gap-3 px-6 py-3 bg-blue-50 rounded-2xl border border-blue-100">
        <Sparkles :size="24" class="text-blue-500 fill-blue-500" />
        <span class="text-2xl font-black text-blue-700 font-label">{{ store.gems }}</span>
      </div>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div 
        v-for="item in items" 
        :key="item.id"
        class="bg-white p-6 rounded-3xl border border-surface-container neo-shadow-hover flex flex-col gap-6 group"
      >
        <div class="w-16 h-16 rounded-2xl bg-surface-container flex items-center justify-center text-primary group-hover:scale-110 group-hover:rotate-6 transition-all duration-300">
          <component :is="item.icon" :size="32" />
        </div>
        
        <div>
          <h3 class="font-display font-bold text-primary text-xl">{{ item.name }}</h3>
          <p class="text-outline text-sm mt-1 leading-relaxed">{{ item.desc }}</p>
        </div>

        <button 
          @click="store.addGems(-item.price)"
          :disabled="store.gems < item.price"
          class="mt-auto w-full py-4 rounded-2xl font-black font-display uppercase tracking-wider transition-all"
          :class="store.gems >= item.price 
            ? 'bg-blue-600 text-white shadow-lg hover:bg-blue-700 shadow-blue-200' 
            : 'bg-surface-container text-outline/50 cursor-not-allowed'"
        >
          {{ store.gems >= item.price ? `${item.price} Gems` : 'Not Enough Gems' }}
        </button>
      </div>
    </div>
  </div>
</template>
