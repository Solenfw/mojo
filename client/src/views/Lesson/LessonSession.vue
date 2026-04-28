<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { X } from 'lucide-vue-next'
import { useSessionStore, type Exercise } from '@/store/useSessionStore'
import MultipleChoice from '@/components/exercises/MultipleChoice.vue'
import CorrectBottomBar from '@/components/feedback/CorrectBottomBar.vue'
import WrongBottomBar from '@/components/feedback/WrongBottomBar.vue'
import LessonComplete from '@/views/Lesson/LessonComplete.vue'

const router = useRouter()
const sessionStore = useSessionStore()

const selectedOption = ref<string | null>(null)
const evaluationStatus = ref<'idle' | 'correct' | 'wrong'>('idle')

const mockExercises: Exercise[] = [
  {
    id: '1',
    type: 'multiple-choice',
    question: 'How do you say "Water" in Japanese?',
    options: ['Mizu', 'Hi', 'Tsuchi', 'Ki'],
    answer: 'Mizu'
  },
  {
    id: '2',
    type: 'multiple-choice',
    question: 'Which radical represents "Tree"?',
    options: ['木', '水', '火', '土'],
    answer: '木'
  }
]

onMounted(() => {
  sessionStore.startSession(mockExercises)
})

const checkAnswer = () => {
  const current = sessionStore.exercises[sessionStore.currentStep]
  if (selectedOption.value === current.answer) {
    evaluationStatus.value = 'correct'
  } else {
    evaluationStatus.value = 'wrong'
  }
}

const handleContinue = () => {
  evaluationStatus.value = 'idle'
  selectedOption.value = null
  
  if (sessionStore.currentStep < sessionStore.exercises.length - 1) {
    sessionStore.nextStep()
  } else {
    // Show completion screen or navigate
    isComplete.value = true
  }
}

const isComplete = ref(false)
const finalStats = {
  xp: 15,
  accuracy: 100,
  time: '1:24'
}

const quitSession = () => {
  if (confirm('Are you sure you want to quit? Progress will not be saved.')) {
    router.push('/')
  }
}
</script>

<template>
  <div class="fixed inset-0 bg-white z-[60] flex flex-col pt-8">
    <!-- Header -->
    <div class="max-w-4xl w-full mx-auto px-6 flex items-center gap-6">
      <button @click="quitSession" class="text-outline hover:text-primary transition-colors">
        <X :size="24" />
      </button>
      
      <div class="flex-1 h-4 bg-surface-container rounded-full overflow-hidden">
        <div 
          class="h-full bg-secondary transition-all duration-500 ease-out" 
          :style="{ width: `${sessionStore.progress}%` }"
        ></div>
      </div>
    </div>

    <!-- Content Area -->
    <div class="flex-1 flex flex-col items-center justify-center p-6 pb-40">
      <div v-if="sessionStore.exercises.length > 0" class="w-full">
        <MultipleChoice 
          v-if="sessionStore.exercises[sessionStore.currentStep].type === 'multiple-choice'"
          v-model="selectedOption"
          :question="sessionStore.exercises[sessionStore.currentStep].question"
          :options="sessionStore.exercises[sessionStore.currentStep].options || []"
        />
      </div>
    </div>

    <!-- Footer Action -->
    <div 
      class="border-t border-surface-container py-8 px-6 flex justify-center bg-white sticky bottom-0"
      v-if="evaluationStatus === 'idle'"
    >
      <button 
        @click="checkAnswer"
        :disabled="!selectedOption"
        class="max-w-md w-full py-4 rounded-2xl font-black font-display uppercase tracking-wider shadow-lg transition-all"
        :class="[
          selectedOption 
            ? 'bg-primary text-white hover:bg-primary-container shadow-primary/20' 
            : 'bg-surface-container text-outline/50 cursor-not-allowed shadow-none'
        ]"
      >
        Check Answer
      </button>
    </div>

    <!-- Feedback Bars -->
    <CorrectBottomBar 
      :show="evaluationStatus === 'correct'" 
      @continue="handleContinue" 
    />
    <WrongBottomBar 
      :show="evaluationStatus === 'wrong'" 
      :correct-answer="String(sessionStore.exercises[sessionStore.currentStep]?.answer)"
      @continue="handleContinue" 
    />

    <!-- Completion Screen -->
    <LessonComplete v-if="isComplete" :stats="finalStats" />
  </div>
</template>
