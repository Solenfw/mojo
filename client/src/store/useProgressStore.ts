import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useProgressStore = defineStore('progress', () => {
  const totalLessonsCompleted = ref(42)
  const totalKanjiMastered = ref(156)
  const averageAccuracy = ref(88)
  
  const currentPath = ref('JLPT N5')

  return {
    totalLessonsCompleted,
    totalKanjiMastered,
    averageAccuracy,
    currentPath
  }
})
