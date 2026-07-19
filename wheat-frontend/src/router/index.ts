import { createRouter, createWebHistory } from 'vue-router'
import Login from '../src/App.vue'
import Register from '../src/App.vue'
import Main from '../src/App.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/main', component: Main }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
