import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface SRSItem {
  id: string
  kanji: string
  reading: string
  meaning: string
  level: number
  nextReview: Date
}

export const useSRSStore = defineStore('srs', () => {
  const queue = ref<SRSItem[]>([
    { id: '1', kanji: '水', reading: 'mizu', meaning: 'water', level: 3, nextReview: new Date() },
    { id: '2', kanji: '火', reading: 'hi', meaning: 'fire', level: 2, nextReview: new Date() },
  ])

  const reviewsDue = ref(24)

  function completeReview(id: string, success: boolean) {
    // Logic for SRS interval adjustment would go here
    console.log(`Review for ${id}: ${success ? 'Success' : 'Fail'}`)
  }

  return {
    queue,
    reviewsDue,
    completeReview
  }
})
