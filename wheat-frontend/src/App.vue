<template>
  <div class="app-wrapper">
    <transition name="fade" mode="out-in">
      <Login
        v-if="!userId && showLogin"
        key="login"
        @loginSuccess="onLoginSuccess"
        @switchToRegister="showLogin = false"
      />
      <Register
        v-else-if="!userId && !showLogin"
        key="register"
        @switchToLogin="showLogin = true"
      />
      <Main
        v-else
        key="main"
        :userId="userId"
        :username="username"
        @logout="handleLogout"
      />
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Login from './components/Login.vue'
import Register from './components/Register.vue'
import Main from './components/Main.vue'

const userId = ref(localStorage.getItem('user_id') || '')
const username = ref(localStorage.getItem('username') || '')
const showLogin = ref(true)

function onLoginSuccess(payload) {
  userId.value = payload.userId
  username.value = payload.username
  localStorage.setItem('user_id', userId.value)
  localStorage.setItem('username', username.value)
}

function handleLogout() {
  userId.value = ''
  username.value = ''
  showLogin.value = true
  localStorage.clear()
}
</script>

<style>
/* ========== Design Tokens ========== */
:root {
  --primary: #166534;
  --primary-light: #22c55e;
  --primary-lighter: #dcfce7;
  --primary-dark: #14532d;
  --accent: #f59e0b;
  --accent-light: #fef3c7;
  --danger: #ef4444;
  --danger-light: #fef2f2;
  --bg: #f0fdf4;
  --bg-page: #f8fafc;
  --surface: #ffffff;
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #94a3b8;
  --border: #e2e8f0;
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 20px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 10px 40px rgba(0, 0, 0, 0.12);
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 20px;
  --radius-full: 9999px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
    "Microsoft YaHei", "Helvetica Neue", sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: var(--bg-page);
  color: var(--text-primary);
  line-height: 1.6;
}

.app-wrapper {
  min-height: 100vh;
}

/* ========== Page Transition ========== */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}
.fade-enter-from {
  opacity: 0;
  transform: translateY(12px);
}
.fade-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}

/* ========== Element Plus Overrides ========== */
.el-button--primary {
  --el-button-bg-color: var(--primary);
  --el-button-border-color: var(--primary);
  --el-button-hover-bg-color: var(--primary-dark);
  --el-button-hover-border-color: var(--primary-dark);
  --el-button-active-bg-color: var(--primary-dark);
  --el-button-active-border-color: var(--primary-dark);
}

.el-input__wrapper {
  box-shadow: 0 0 0 1px var(--border) inset !important;
  border-radius: var(--radius-sm);
}

.el-input__wrapper.is-focus {
  box-shadow: 0 0 0 2px var(--primary-light) inset !important;
}

.el-table th.el-table__cell {
  background-color: var(--primary) !important;
  color: #fff !important;
  font-weight: 500;
}

.el-table--striped .el-table__body tr.el-table__row--striped td {
  background-color: var(--primary-lighter);
}
</style>
