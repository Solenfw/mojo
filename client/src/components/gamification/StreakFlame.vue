<script setup lang="ts">
import { Flame } from 'lucide-vue-next'
import { useGamificationStore } from '@/store/useGamificationStore'

const store = useGamificationStore()
</script>

<template>
  <div class="flex items-center gap-2 px-3 py-1.5 bg-orange-50 rounded-full border border-orange-100 transition-all hover:scale-105 active:scale-95 group">
    <Flame 
      :size="16" 
      class="text-orange-500 transition-transform group-hover:rotate-12" 
      :class="{ 'fill-orange-500': store.streak > 0 }"
    />
    <span class="text-sm font-black text-orange-700 font-label">{{ store.streak }}</span>
  </div>
</template>
