<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="bg-ornament bg-ornament-1"></div>
      <div class="bg-ornament bg-ornament-2"></div>
      <div class="bg-ornament bg-ornament-3"></div>
    </div>

    <div class="login-content">
      <div class="login-brand">
        <div class="brand-icon">
          <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
            <circle cx="32" cy="32" r="30" fill="var(--primary-lighter)" stroke="var(--primary-light)" stroke-width="2"/>
            <path d="M18 36c4-12 14-18 14-18s10 6 14 18c-4-2-10-3-14-3s-10 1-14 3z" fill="var(--primary-light)" opacity="0.3"/>
            <path d="M22 34c3-8 10-12 10-12s7 4 10 12c-3-1-7-2-10-2s-7 1-10 2z" fill="var(--primary)" opacity="0.6"/>
            <path d="M26 38c2-4 6-6 6-6s4 2 6 6c-2 0-4 1-6 1s-4-1-6-1z" fill="var(--primary)"/>
            <path d="M30 24c-4 0-8 4-8 8h16c0-4-4-8-8-8z" fill="#fbbf24" opacity="0.8"/>
          </svg>
        </div>
        <h1 class="brand-title">
  <a href="https://www.htmtshht849.vip:9527/detail/172171" 
     target="_blank" 
     style="color: inherit; text-decoration: none;">
    小麦病虫害识别系统
  </a>
</h1>
        <p class="brand-desc">基于深度学习的智能农作物健康诊断平台</p>
      </div>

      <div class="login-card">
        <div class="login-card-header">
          <h2 class="login-card-title">欢迎登录</h2>
          <p class="login-card-subtitle">请使用您的账号登录系统</p>
        </div>

        <el-form
          :model="form"
          :rules="rules"
          ref="formRef"
          label-width="0"
          class="login-form"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              :prefix-icon="UserIcon"
              size="large"
              clearable
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              placeholder="请输入密码"
              :prefix-icon="LockIcon"
              show-password
              size="large"
              clearable
            />
          </el-form-item>

          <el-form-item class="login-options">
            <el-checkbox v-model="rememberMe">记住密码</el-checkbox>
          </el-form-item>

          <el-form-item class="login-actions">
            <el-button
              type="primary"
              :loading="loading"
              @click="handleLogin"
              class="login-btn"
              size="large"
            >
              {{ loading ? '登录中...' : '登 录' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="login-footer-text">
          还没有账号？
          <a href="javascript:void(0)" @click="switchToRegister" class="switch-link">
            立即注册
          </a>
        </div>

        <div class="login-divider">
          <span>小麦病虫害识别及预警系统</span>
        </div>
      </div>
    </div>

    <div class="login-bottom-bar">
      <span>© 小麦病虫害识别系统 | 成员: 王志洋</span>
    </div>
  </div>
</template>

<script setup>
import { defineEmits, ref, reactive, onMounted, h } from 'vue'
import { API_BASE_URL, setToken } from '../api.js'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['loginSuccess', 'switchToRegister'])

const formRef = ref()
const form = reactive({
  username: '',
  password: ''
})
const rememberMe = ref(false)
const loading = ref(false)

const UserIcon = {
  render() {
    return h('svg', {
      viewBox: '0 0 24 24',
      width: '18',
      height: '18',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '2',
      'stroke-linecap': 'round',
      'stroke-linejoin': 'round'
    }, [
      h('path', { d: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2' }),
      h('circle', { cx: '12', cy: '7', r: '4' })
    ])
  }
}

const LockIcon = {
  render() {
    return h('svg', {
      viewBox: '0 0 24 24',
      width: '18',
      height: '18',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '2',
      'stroke-linecap': 'round',
      'stroke-linejoin': 'round'
    }, [
      h('rect', { x: '3', y: '11', width: '18', height: '11', rx: '2', ry: '2' }),
      h('path', { d: 'M7 11V7a5 5 0 0 1 10 0v4' })
    ])
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { pattern: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$/,
      message: '密码需包含字母与数字，至少6位', trigger: 'blur' }
  ]
}

onMounted(() => {
  const savedUser = localStorage.getItem('savedUser')
  if (savedUser) {
    const { username, password } = JSON.parse(savedUser)
    form.username = username
    form.password = password
    rememberMe.value = true
  }
})

function handleLogin() {
  formRef.value.validate(valid => {
    if (!valid) return
    loading.value = true

    axios.post(API_BASE_URL + '/login', form).then(res => {
      if (res.data.success) {
        if (rememberMe.value) {
          localStorage.setItem('savedUser', JSON.stringify({
            username: form.username,
            password: form.password
          }))
        } else {
          localStorage.removeItem('savedUser')
        }
        ElMessage.success('登录成功')
        setToken(res.data.token)
        emit('loginSuccess', { userId: res.data.user_id, username: form.username })
      } else {
        ElMessage.error(res.data.msg || '登录失败，请检查用户名和密码')
      }
    }).catch(error => {
      ElMessage.error('网络错误，请稍后重试')
      console.error('Login error:', error)
    }).finally(() => {
      loading.value = false
    })
  })
}

function switchToRegister() {
  emit('switchToRegister')
}
</script>

<style scoped>
.login-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: linear-gradient(135deg, #f0fdf4 0%, #f8fafc 50%, #fefce8 100%);
  position: relative;
  overflow: hidden;
}

/* ========== 背景装饰 ========== */
.login-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.bg-ornament {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
}

.bg-ornament-1 {
  top: -10%;
  right: -5%;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, var(--primary-light), transparent);
  animation: floatOrnament 8s ease-in-out infinite;
}

.bg-ornament-2 {
  bottom: -15%;
  left: -5%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #fbbf24, transparent);
  animation: floatOrnament 10s ease-in-out infinite reverse;
}

.bg-ornament-3 {
  top: 40%;
  left: 60%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, #60a5fa, transparent);
  animation: floatOrnament 12s ease-in-out infinite 2s;
}

@keyframes floatOrnament {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, -30px); }
}

/* ========== 主布局 ========== */
.login-content {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  gap: 80px;
  padding: 40px 20px;
  position: relative;
  z-index: 1;
}

/* ========== 品牌区 ========== */
.login-brand {
  max-width: 380px;
  animation: slideInLeft 0.8s ease;
}

.brand-icon {
  margin-bottom: 24px;
}

.brand-title {
  font-size: 36px;
  font-weight: 700;
  color: var(--primary-dark);
  margin-bottom: 12px;
  letter-spacing: 2px;
}

.brand-desc {
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.7;
}

/* ========== 登录卡片 ========== */
.login-card {
  width: 420px;
  background: var(--surface);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08), 0 4px 16px rgba(0, 0, 0, 0.04);
  padding: 44px 40px 36px;
  animation: slideInRight 0.8s ease;
  border: 1px solid rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(20px);
}

.login-card-header {
  text-align: center;
  margin-bottom: 36px;
}

.login-card-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.login-card-subtitle {
  font-size: 14px;
  color: var(--text-muted);
}

.login-form .el-form-item {
  margin-bottom: 22px;
}

.login-form :deep(.el-input__wrapper) {
  padding: 4px 16px;
  height: 48px;
  border-radius: 10px !important;
}

.login-form :deep(.el-input__prefix) {
  margin-right: 10px;
  color: var(--text-muted);
}

.login-options {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.login-actions {
  margin-top: 8px;
}

.login-btn {
  width: 100%;
  height: 48px;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 4px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  border: none;
  transition: all 0.3s ease;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(22, 101, 52, 0.25);
}

.login-btn:active {
  transform: translateY(0);
}

.login-footer-text {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: var(--text-secondary);
}

.switch-link {
  color: var(--primary);
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s;
}

.switch-link:hover {
  color: var(--primary-light);
  text-decoration: underline;
}

.login-divider {
  margin-top: 24px;
  text-align: center;
  position: relative;
  padding-top: 20px;
}

.login-divider::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--primary-light), transparent);
  border-radius: 2px;
}

.login-divider span {
  font-size: 12px;
  color: var(--text-muted);
}

/* ========== 底部 ========== */
.login-bottom-bar {
  text-align: center;
  padding: 20px;
  font-size: 13px;
  color: var(--text-muted);
  position: relative;
  z-index: 1;
}

/* ========== 动画 ========== */
@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-40px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(40px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* ========== 响应式 ========== */
@media (max-width: 900px) {
  .login-content {
    flex-direction: column;
    gap: 40px;
    padding: 40px 16px;
  }

  .login-brand {
    max-width: 100%;
    text-align: center;
  }

  .brand-title {
    font-size: 28px;
  }

  .login-card {
    width: 100%;
    max-width: 420px;
    padding: 36px 28px 28px;
  }
}
</style>
