import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('../views/HomeView.vue') },
  { path: '/interview/:id', name: 'interview', component: () => import('../views/InterviewView.vue') },
  { path: '/resume', name: 'resume', component: () => import('../views/ResumeView.vue') },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
