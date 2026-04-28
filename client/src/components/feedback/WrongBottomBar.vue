<script setup lang="ts">
import { XCircle } from 'lucide-vue-next'

defineProps<{
  show: boolean
  correctAnswer: string
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
    <div v-if="show" class="fixed bottom-0 left-0 w-full bg-[#ffdfe0] border-t-4 border-[#ea2b2b] py-8 px-4 md:px-8 z-50">
      <div class="max-w-4xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <div class="flex items-center gap-4 text-[#ea2b2b]">
          <div class="bg-white rounded-full p-1 shadow-sm">
            <XCircle :size="48" fill="currentColor" class="text-white bg-[#ea2b2b] rounded-full" />
          </div>
          <div>
            <h3 class="text-2xl font-black font-display uppercase tracking-tight">Hard Luck!</h3>
            <p class="text-sm font-bold">The correct answer was: <span class="underline">{{ correctAnswer }}</span></p>
          </div>
        </div>

        <button 
          @click="$emit('continue')"
          class="w-full md:w-auto bg-[#ea2b2b] hover:bg-[#c21d1d] text-white font-black font-display uppercase tracking-wider px-12 py-4 rounded-2xl shadow-[0_4px_0_0_#c21d1d] transition-all active:shadow-none active:translate-y-1"
        >
          Got it
        </button>
      </div>
    </div>
  </transition>
</template>
