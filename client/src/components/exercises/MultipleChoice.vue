<script setup lang="ts">
defineProps<{
  question: string
  options: string[]
  modelValue: string | null
}>()

defineEmits(['update:modelValue'])
</script>

<template>
  <div class="flex flex-col gap-8 w-full max-w-xl mx-auto">
    <h2 class="font-display text-2xl font-bold text-primary text-center">
      {{ question }}
    </h2>

    <div class="grid grid-cols-1 gap-4">
      <button
        v-for="option in options"
        :key="option"
        @click="$emit('update:modelValue', option)"
        class="p-6 rounded-2xl border-2 transition-all text-left font-body font-medium flex items-center justify-between group"
        :class="[
          modelValue === option 
            ? 'border-primary bg-primary/5 text-primary ring-4 ring-primary/5' 
            : 'border-surface-container hover:border-outline/30 bg-white'
        ]"
      >
        <span>{{ option }}</span>
        <div 
          class="w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors"
          :class="modelValue === option ? 'border-primary bg-primary' : 'border-surface-container'"
        >
          <div v-if="modelValue === option" class="w-2 h-2 bg-white rounded-full"></div>
        </div>
      </button>
    </div>
  </div>
</template>
