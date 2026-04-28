import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSoundStore = defineStore('sound', () => {
  const isMuted = ref(false)
  const volume = ref(0.8)

  function toggleMute() {
    isMuted.value = !isMuted.value
  }

  function playSfx(type: 'correct' | 'wrong' | 'click' | 'levelup') {
    if (isMuted.value) return
    console.log(`Playing SFX: ${type}`)
    // In a real app, I'd trigger an Audio element here
  }

  return {
    isMuted,
    volume,
    toggleMute,
    playSfx
  }
})
