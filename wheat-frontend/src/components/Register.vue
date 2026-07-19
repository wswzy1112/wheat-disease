<template>
  <div class="register-page">
    <div class="register-bg">
      <div class="bg-ornament bg-ornament-1"></div>
      <div class="bg-ornament bg-ornament-2"></div>
      <div class="bg-ornament bg-ornament-3"></div>
    </div>

    <div class="register-content">
      <div class="register-card">
        <div class="register-card-header">
          <div class="register-back">
            <a href="javascript:void(0)" @click="switchToLogin" class="back-link">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="15 18 9 12 15 6"/>
              </svg>
              返回登录
            </a>
          </div>
          <h2 class="register-card-title">创建账号</h2>
          <p class="register-card-subtitle">注册后即可使用病虫害识别服务</p>
        </div>

        <el-form
          :model="form"
          :rules="rules"
          ref="formRef"
          label-width="0"
          class="register-form"
          @keyup.enter="handleRegister"
        >
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              size="large"
              clearable
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              placeholder="请输入密码（字母+数字，至少6位）"
              show-password
              size="large"
              clearable
            />
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              placeholder="请再次输入密码确认"
              show-password
              size="large"
              clearable
            />
          </el-form-item>

          <el-form-item class="register-actions">
            <el-button
              type="primary"
              :loading="loading"
              @click="handleRegister"
              class="register-btn"
              size="large"
            >
              {{ loading ? '注册中...' : '注 册' }}
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <div class="register-bottom-bar">
      <span>© 小麦病虫害识别系统 | 成员: 王志洋</span>
    </div>
  </div>
</template>

<script setup>
import { defineEmits, ref, reactive } from 'vue'
import { API_BASE_URL, setToken } from '../api.js'
import axios from 'axios'
import { ElMessage, ElLoading } from 'element-plus'

const emit = defineEmits(['switchToLogin'])

const formRef = ref()
const form = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})
const loading = ref(false)

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名至少3个字符', trigger: 'blur' },
    { max: 20, message: '用户名最大20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { pattern: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$/, message: '密码需包含字母与数字，至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      }, trigger: 'blur'
    }
  ]
}

function handleRegister() {
  formRef.value.validate(valid => {
    if (!valid) return

    loading.value = true

    axios.post(API_BASE_URL + '/register', form).then(res => {
      if (res.data.success) {
        ElMessage.success('注册成功，请登录')
        setToken(res.data.token)
        emit('switchToLogin')
      } else {
        ElMessage.error(res.data.msg || '注册失败')
      }
    }).catch(error => {
      ElMessage.error('网络错误，请稍后重试')
      console.error('Register error:', error)
    }).finally(() => {
      loading.value = false
    })
  })
}

function switchToLogin() {
  setToken(res.data.token)
        emit('switchToLogin')
}
</script>

<style scoped>
.register-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: linear-gradient(135deg, #fefce8 0%, #f8fafc 50%, #f0fdf4 100%);
  position: relative;
  overflow: hidden;
}

/* ========== 背景装饰 ========== */
.register-bg {
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
  left: -5%;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #fbbf24, transparent);
  animation: floatOrnament 8s ease-in-out infinite;
}

.bg-ornament-2 {
  bottom: -15%;
  right: -5%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, var(--primary-light), transparent);
  animation: floatOrnament 10s ease-in-out infinite reverse;
}

.bg-ornament-3 {
  top: 50%;
  right: 40%;
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
.register-content {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 40px 20px;
  position: relative;
  z-index: 1;
}

.register-card {
  width: 440px;
  background: var(--surface);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08), 0 4px 16px rgba(0, 0, 0, 0.04);
  padding: 44px 40px 40px;
  animation: fadeUp 0.6s ease;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.register-card-header {
  text-align: center;
  margin-bottom: 36px;
}

.register-back {
  text-align: left;
  margin-bottom: 20px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: var(--text-muted);
  text-decoration: none;
  transition: color 0.2s;
}

.back-link:hover {
  color: var(--primary);
}

.register-card-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.register-card-subtitle {
  font-size: 14px;
  color: var(--text-muted);
}

.register-form .el-form-item {
  margin-bottom: 22px;
}

.register-form :deep(.el-input__wrapper) {
  padding: 4px 16px;
  height: 48px;
  border-radius: 10px !important;
}

.register-actions {
  margin-top: 8px;
}

.register-btn {
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

.register-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(22, 101, 52, 0.25);
}

.register-btn:active {
  transform: translateY(0);
}

.register-bottom-bar {
  text-align: center;
  padding: 20px;
  font-size: 13px;
  color: var(--text-muted);
  position: relative;
  z-index: 1;
}

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 600px) {
  .register-card {
    max-width: 100%;
    padding: 36px 24px 28px;
  }
}
</style>
