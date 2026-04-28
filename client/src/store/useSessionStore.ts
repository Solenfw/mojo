import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Exercise {
  id: string
  type: 'multiple-choice' | 'tap-pair' | 'fill-blank'
  question: string
  options?: string[]
  answer: string | string[]
  explanation?: string
}

export const useSessionStore = defineStore('session', () => {
  const isActive = ref(false)
  const currentStep = ref(0)
  const exercises = ref<Exercise[]>([])
  const progress = computed(() => {
    if (exercises.value.length === 0) return 0
    return (currentStep.value / exercises.value.length) * 100
  })

  function startSession(newExercises: Exercise[]) {
    exercises.value = newExercises
    currentStep.value = 0
    isActive.value = true
  }

  function nextStep() {
    if (currentStep.value < exercises.value.length) {
      currentStep.value++
    }
  }

  function endSession() {
    isActive.value = false
    exercises.value = []
    currentStep.value = 0
  }

  return {
    isActive,
    currentStep,
    exercises,
    progress,
    startSession,
    nextStep,
    endSession
  }
})
