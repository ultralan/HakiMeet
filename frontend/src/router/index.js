import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('../views/HomeView.vue') },
  { path: '/interview/:id', name: 'interview', component: () => import('../views/InterviewView.vue') },
  { path: '/resume', name: 'resume', component: () => import('../views/ResumeView.vue') },
  { path: '/question-bank', name: 'question-bank', component: () => import('../views/QuestionBankView.vue') },
  { path: '/history', name: 'history', component: () => import('../views/HistoryView.vue') },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
