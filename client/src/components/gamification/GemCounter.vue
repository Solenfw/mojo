<script setup lang="ts">
import { Hexagon } from 'lucide-vue-next'
import { useGamificationStore } from '@/store/useGamificationStore'

const store = useGamificationStore()
</script>

<template>
  <div class="flex items-center gap-2 px-3 py-1.5 bg-blue-50 rounded-full border border-blue-100 transition-all hover:bg-blue-100 cursor-help">
    <Hexagon :size="16" class="text-blue-500 fill-blue-500" />
    <span class="text-sm font-black text-blue-700 font-label">{{ store.gems }}</span>
  </div>
</template>
