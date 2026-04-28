<script setup lang="ts">
import { Bell } from 'lucide-vue-next'
import HeartSystem from '@/components/gamification/HeartSystem.vue'
import GemCounter from '@/components/gamification/GemCounter.vue'
import StreakFlame from '@/components/gamification/StreakFlame.vue'
import { useUserStore } from '@/store/useUserStore'

const userStore = useUserStore()
</script>

<template>
  <header class="bg-white/90 backdrop-blur-md sticky top-0 z-50 border-b border-surface-container neo-shadow">
    <div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
      <div class="flex items-center gap-8">
        <router-link to="/" class="font-display text-xl font-bold tracking-tighter text-primary shrink-0">
          Linguasphere
        </router-link>
        
        <nav class="hidden lg:flex items-center gap-6">
          <router-link 
            to="/" 
            class="font-display text-sm font-semibold text-outline hover:text-primary transition-colors"
            active-class="active-nav"
          >
            Dashboard
          </router-link>
          <router-link 
            to="/lessons" 
            class="font-display text-sm font-semibold text-outline hover:text-primary transition-colors"
            active-class="active-nav"
          >
            Lessons
          </router-link>
          <router-link 
            to="/about" 
            class="font-display text-sm font-semibold text-outline hover:text-primary transition-colors"
            active-class="active-nav"
          >
            About
          </router-link>
          <router-link 
            to="/shop" 
            class="font-display text-sm font-semibold text-outline hover:text-primary transition-colors"
            active-class="active-nav"
          >
            Shop
          </router-link>
        </nav>
      </div>

      <div class="flex items-center gap-2 md:gap-6">
        <!-- Gamification Stats -->
        <div class="hidden sm:flex items-center gap-2">
          <router-link to="/shop"><StreakFlame /></router-link>
          <router-link to="/shop"><GemCounter /></router-link>
          <router-link to="/shop"><HeartSystem /></router-link>
        </div>

        <div class="flex items-center gap-4 border-l border-surface-container pl-6">
          <button class="p-2 text-outline hover:text-primary transition-colors relative">
            <span class="sr-only">Notifications</span>
            <Bell :size="20" />
            <span class="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
          </button>
          <router-link to="/profile" class="h-8 w-8 rounded-full bg-primary-container border-2 border-white shadow-sm overflow-hidden cursor-pointer hover:ring-2 hover:ring-primary/20 transition-all">
            <img :src="userStore.avatar" alt="User avatar" />
          </router-link>
        </div>
      </div>
    </div>
  </header>
</template>
