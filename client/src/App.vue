<script setup lang="ts">
import { RouterView } from 'vue-router'
import Header from '@/components/common/Header.vue'
</script>

<template>
  <div class="min-h-screen flex flex-col bg-[#fbf9f8]">
    <Header />

    <main class="flex-1 max-w-7xl w-full mx-auto p-4 md:p-8">
      <RouterView v-slot="{ Component }">
        <transition 
          name="page" 
          mode="out-in"
        >
          <component :is="Component" />
        </transition>
      </RouterView>
    </main>
    
    <footer class="bg-surface-container border-t border-surface-container-highest p-8 mt-auto">
      <div class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
        <span class="text-sm text-outline font-label">© 2026 Linguasphere AI</span>
        <div class="flex gap-4 text-xs font-label text-outline uppercase tracking-wider">
          <a href="#" class="hover:text-primary transition-colors">Privacy</a>
          <a href="#" class="hover:text-primary transition-colors">Terms</a>
          <a href="#" class="hover:text-primary transition-colors">Support</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<style>
/* Page transitions */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
