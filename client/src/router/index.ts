import { createRouter, createWebHistory } from 'vue-router'
import DashboardHome from '../views/Dashboard/DashboardHome.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: DashboardHome
    },
    {
      path: '/lessons',
      name: 'lessons',
      component: () => import('../views/Study/LessonPath.vue')
    },
    {
      path: '/lesson/session',
      name: 'lesson-session',
      component: () => import('../views/Lesson/LessonSession.vue')
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/Profile/About.vue')
    },
    {
      path: '/shop',
      name: 'shop',
      component: () => import('../views/Shop/ShopView.vue')
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/Profile/UserProfile.vue')
    }
  ]
})

export default router
