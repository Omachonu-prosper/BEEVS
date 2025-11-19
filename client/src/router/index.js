import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import DashboardView from '@/views/DashboardView.vue'
import CreateElectionView from '@/views/CreateElectionView.vue'
import ElectionView from '@/views/ElectionView.vue'
import VotingView from '@/views/VotingView.vue'
import VoteAuthView from '@/views/VoteAuthView.vue'
import ResultsView from '@/views/ResultsView.vue'
import AuditAuthView from '@/views/AuditAuthView.vue'
import AuditView from '@/views/AuditView.vue'

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
    },
    {
      path: '/vote/:electionId/auth',
      component: VoteAuthView
    },
    {
      path: '/vote/:electionId',
      component: VotingView
    },
    {
      path: '/results/:electionId',
      component: ResultsView
    },
    {
      path: '/audit/:electionId/auth',
      component: AuditAuthView
    },
    {
      path: '/audit/:electionId',
      component: AuditView
    }
  ],
})

export default router