import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const name = ref('Alex')
  const level = ref(12)
  const avatar = ref('https://api.dicebear.com/7.x/avataaars/svg?seed=Felix')
  
  const greeting = computed(() => `Good Morning, ${name.value}`)

  function updateName(newName: string) {
    name.value = newName
  }

  return {
    name,
    level,
    avatar,
    greeting,
    updateName
  }
})
