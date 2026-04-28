<script setup lang="ts">
import { Trophy } from 'lucide-vue-next'
import PathNode from './PathNode.vue'

interface Node {
  id: number
  title: string
  status: 'completed' | 'in-progress' | 'locked'
  xOffset: number
  isCurrent?: boolean
  isMilestone?: boolean
}

defineProps<{
  nodes: Node[]
}>()
</script>

<template>
  <div class="relative flex flex-col items-center py-8 gap-24">
    <!-- SVG Connector (Conceptual simplified for now) -->
    <div class="absolute inset-0 pointer-events-none flex justify-center">
      <!-- In a real app, I'd use a dynamic SVG path here -->
    </div>

    <PathNode 
      v-for="node in nodes" 
      :key="node.id"
      v-bind="node"
    >
      <template v-if="node.isMilestone" #icon>
        <Trophy :size="40" :class="node.status === 'locked' ? 'opacity-30' : 'text-secondary-container'" />
      </template>
    </PathNode>
  </div>
</template>
