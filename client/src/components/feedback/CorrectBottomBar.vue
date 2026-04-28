<script setup lang="ts">
import { CheckCircle2 } from 'lucide-vue-next'

defineProps<{
  show: boolean
}>()

defineEmits(['continue'])
</script>

<template>
  <transition
    enter-active-class="transform transition duration-300 ease-out"
    enter-from-class="translate-y-full"
    enter-to-class="translate-y-0"
    leave-active-class="transform transition duration-200 ease-in"
    leave-from-class="translate-y-0"
    leave-to-class="translate-y-full"
  >
    <div v-if="show" class="fixed bottom-0 left-0 w-full bg-[#d7ffb8] border-t-4 border-[#58cc02] py-8 px-4 md:px-8 z-50">
      <div class="max-w-4xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <div class="flex items-center gap-4 text-[#58cc02]">
          <div class="bg-white rounded-full p-1 shadow-sm">
            <CheckCircle2 :size="48" fill="currentColor" class="text-white bg-[#58cc02] rounded-full" />
          </div>
          <div>
            <h3 class="text-2xl font-black font-display uppercase tracking-tight">Excellent!</h3>
            <p class="text-sm font-bold opacity-80">You got it right.</p>
          </div>
        </div>

        <button 
          @click="$emit('continue')"
          class="w-full md:w-auto bg-[#58cc02] hover:bg-[#46a302] text-white font-black font-display uppercase tracking-wider px-12 py-4 rounded-2xl shadow-[0_4px_0_0_#46a302] transition-all active:shadow-none active:translate-y-1"
        >
          Continue
        </button>
      </div>
    </div>
  </transition>
</template>
