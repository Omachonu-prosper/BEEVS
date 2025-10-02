import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import DashboardView from '@/views/DashboardView.vue'
import CreateElectionView from '@/views/CreateElectionView.vue'
import ElectionView from '@/views/ElectionView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: HomeView
    },
    {
      path: '/login',
      component: LoginView
    },
    {
      path: '/dashboard',
      component: DashboardView
    },
    {
      path: '/create-election',
      component: CreateElectionView
    },
    {
      path: '/election/:id',
      component: ElectionView
    }
  ],
})

export default router
