<script setup lang="ts">
import { Heart } from 'lucide-vue-next'
import { useGamificationStore } from '@/store/useGamificationStore'

const store = useGamificationStore()
</script>

<template>
  <div class="flex items-center gap-1.5 px-3 py-1.5 bg-red-50 rounded-full border border-red-100 group transition-all hover:scale-105">
    <Heart 
      v-for="i in 5" 
      :key="i"
      :size="16" 
      class="transition-all duration-300"
      :class="i <= store.hearts ? 'text-red-500 fill-red-500 group-hover:scale-110' : 'text-red-200'"
    />
  </div>
</template>
