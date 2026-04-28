import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useGamificationStore = defineStore('gamification', () => {
  const hearts = ref(5)
  const gems = ref(150)
  const xp = ref(2450)
  const streak = ref(12)
  
  function addGems(amount: number) {
    gems.value += amount
  }

  function loseHeart() {
    if (hearts.value > 0) hearts.value--
  }

  function addXP(amount: number) {
    xp.value += amount
  }

  return {
    hearts,
    gems,
    xp,
    streak,
    addGems,
    loseHeart,
    addXP
  }
})
