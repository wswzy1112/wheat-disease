<template>
  <div class="dashboard">
    <!-- ========== Top Navigation ========== -->
    <header class="top-nav">
      <div class="nav-inner">
        <div class="nav-brand">
          <span class="nav-logo">
            <svg width="32" height="32" viewBox="0 0 64 64" fill="none">
              <circle cx="32" cy="32" r="30" fill="var(--primary-lighter)" stroke="var(--primary-light)" stroke-width="2"/>
              <path d="M22 34c3-8 10-12 10-12s7 4 10 12c-3-1-7-2-10-2s-7 1-10 2z" fill="var(--primary)" opacity="0.6"/>
              <path d="M26 38c2-4 6-6 6-6s4 2 6 6c-2 0-4 1-6 1s-4-1-6-1z" fill="var(--primary)"/>
              <path d="M30 24c-4 0-8 4-8 8h16c0-4-4-8-8-8z" fill="#fbbf24" opacity="0.8"/>
            </svg>
          </span>
          <span class="nav-title">小麦病虫害识别系统</span>
        </div>
        <div class="nav-actions">
          <span class="nav-user">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
            <span>{{ username }}</span>
          </span>
          <el-button size="small" class="logout-btn" @click="logout">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            退出登录
          </el-button>
        </div>
      </div>
    </header>

    <!-- ========== Main Content ========== -->
    <main class="main-content">
      <div class="content-inner">

        <!-- ===== Upload Zone ===== -->
        <section class="section upload-section">
          <el-upload
            ref="uploadRef"
            class="upload-zone"
            name="image"
            action="#"
            :show-file-list="false"
            :auto-upload="true"
            :http-request="customUpload"
            drag
          >
            <div class="upload-placeholder">
              <div class="upload-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--primary-light)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="17 8 12 3 7 8"/>
                  <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
              </div>
              <p class="upload-title">点击或拖拽上传小麦图片</p>
              <p class="upload-hint">支持 JPG、PNG 格式，单张不超过 10MB</p>
            </div>
          </el-upload>
        </section>

        <!-- ===== Progress Overlay ===== -->
        <transition name="progress-fade">
          <div v-if="showProgress" class="progress-overlay">
            <div class="progress-card">
              <div class="progress-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
              </div>
              <h3 class="progress-title">正在识别病虫害</h3>
              <el-progress :percentage="progressValue" :stroke-width="10" color="#22c55e" class="progress-bar"/>
              <div class="progress-stages">
                <span v-for="(stage, idx) in progressStages" :key="idx" class="progress-stage" :class="{ active: currentStageIndex >= idx, done: currentStageIndex > idx }">
                  <span class="stage-dot"></span>
                  <span class="stage-label">{{ stage }}</span>
                </span>
              </div>
            </div>
          </div>
        </transition>

        <!-- ===== Recognition Result ===== -->
        <section v-if="result" class="section result-section">
          <div class="section-header">
            <h3 class="section-title">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <path d="m9 12 2 2 4-4"/>
              </svg>
              识别结果
            </h3>
          </div>

          <div class="result-card">
            <div class="result-grid">
              <div class="result-main">
                <div class="result-badge" :class="result === '健康' ? 'badge-success' : 'badge-warning'">
                  <span class="badge-dot"></span>
                  {{ result === '识别失败' ? '识别失败' : result }}
                </div>

                <div class="result-metrics">
                  <div class="metric-item">
                    <span class="metric-label">识别正确率</span>
                    <span class="metric-value">{{ (confidence * 100).toFixed(2) }}%</span>
                  </div>
                  <div class="metric-item" v-if="warning && result !== '健康' && result !== '识别失败'">
                    <span class="metric-label metric-label-warning">病害预警</span>
                    <span class="metric-value metric-value-warning">建议立即处理！</span>
                  </div>
                </div>

                <div class="result-suggestion">
                  <div class="suggestion-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <circle cx="12" cy="12" r="10"/>
                      <line x1="12" y1="16" x2="12" y2="12"/>
                      <line x1="12" y1="8" x2="12.01" y2="8"/>
                    </svg>
                  </div>
                  <div>
                    <p class="suggestion-label">防治建议</p>
                    <p class="suggestion-text">{{ suggestion }}</p>
                  </div>
                </div>
              </div>

              <div class="result-image-wrapper" v-if="showImage">
                <img :src="imageUrl" alt="识别图像" class="result-image" />
              </div>
            </div>
          </div>
        </section>

        <!-- ===== Records Table ===== -->
        <section class="section table-section">
          <div class="section-header">
            <h3 class="section-title">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <line x1="3" y1="9" x2="21" y2="9"/>
                <line x1="9" y1="21" x2="9" y2="9"/>
              </svg>
              识别记录
            </h3>
            <div class="section-toolbar">
              <el-input
                v-model="keyword"
                placeholder="输入病害名称搜索"
                clearable
                style="width: 220px;"
                size="default"
                @keyup.enter="fetchRecords"
              >
                <template #prefix>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="11" cy="11" r="8"/>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"/>
                  </svg>
                </template>
              </el-input>
              <el-button @click="fetchRecords" class="search-btn">搜索</el-button>
            </div>
          </div>

          <el-table
            :data="records"
            border
            stripe
            class="records-table"
            style="width: 100%"
            :default-sort="{ prop: 'time', order: 'descending' }"
            @sort-change="handleSortChange"
          >
            <el-table-column prop="time" label="时间" width="170" sortable="custom" />
            <el-table-column prop="result" label="识别结果" sortable="custom" />
            <el-table-column prop="confidence" label="正确率" width="100" />
            <el-table-column prop="suggestion" label="防治建议" min-width="200" />
            <el-table-column label="查看图片" width="100" align="center">
              <template #default="scope">
                <el-button
                  text
                  type="primary"
                  size="small"
                  @click="openImage(scope.row.filename)"
                >
                  查看
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-wrapper">
            <el-pagination
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              :current-page="currentPage"
              :page-sizes="[10]"
              :page-size="pageSize"
              layout="total, prev, pager, next, jumper"
              :total="total"
            />
          </div>
        </section>

        <!-- ===== Disease Cards ===== -->
        <section class="section disease-section">
          <div class="section-header">
            <h3 class="section-title">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              小麦常见病虫害与防治建议
            </h3>
          </div>

          <div class="disease-grid">
            <div
              v-for="item in diseaseList"
              :key="item.id"
              class="disease-card"
            >
              <div class="disease-card-icon">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                  <path d="M2 17l10 5 10-5"/>
                  <path d="M2 12l10 5 10-5"/>
                </svg>
              </div>
              <h4 class="disease-card-title">{{ item.name }}</h4>
              <p class="disease-card-desc">{{ item.suggestion }}</p>
            </div>
          </div>
        </section>

        <!-- ===== Footer ===== -->
        <section class="section footer-section">
          <div class="footer-card">
            <div class="footer-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 16v-4"/>
                <path d="M12 8h.01"/>
              </svg>
            </div>
            <div class="footer-text">
              <h4>系统介绍</h4>
              <p>本系统为广大农民群体提供专业的小麦病虫害识别服务，通过图像分析技术精准识别病虫害类型，减少因病虫害识别延误导致的损失</p>
              <span class="footer-author">技术支持：王志洋团队</span>
            </div>
          </div>
        </section>

      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { API_BASE_URL, getToken } from '../api.js'
import axios from 'axios'

const props = defineProps(['userId', 'username'])
const emit = defineEmits(['logout'])

const result = ref('')
const confidence = ref(0)
const warning = ref(false)
const suggestion = ref('')
const imageUrl = ref('')
const showImage = ref(true)
const records = ref([])
const diseaseList = ref([])
const keyword = ref('')
const sortProp = ref('time')
const showProgress = ref(false)
const progressValue = ref(0)
const currentStageIndex = ref(0)
const progressStages = ['上传图片', '图片预处理', '模型推理中', '结果分析', '生成结果']
let progressTimer = null
let stageTimer = null

function startProgressAnimation() {
  progressValue.value = 0
  currentStageIndex.value = 0
  const stageLimits = [20, 40, 70, 90, 100]
  stageTimer = setInterval(() => {
    if (currentStageIndex.value < stageLimits.length - 1) {
      currentStageIndex.value++
      progressValue.value = stageLimits[currentStageIndex.value - 1]
    }
  }, 3000)
  progressTimer = setInterval(() => {
    if (progressValue.value < 95) progressValue.value++
  }, 80)
}
function stopProgressAnimation() {
  if (progressTimer) { clearInterval(progressTimer); progressTimer = null }
  if (stageTimer) { clearInterval(stageTimer); stageTimer = null }
  progressValue.value = 100
  currentStageIndex.value = 4
  setTimeout(() => { showProgress.value = false }, 1000)
}
const sortOrder = ref('desc')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

function logout() {
  localStorage.clear()
  emit('logout')
}

function customUpload(option) {
  const formData = new FormData()
  formData.append('image', option.file)
  formData.append('user_id', props.userId)

  const loading = ElLoading.service({
    lock: true,
    text: '正在识别中...',
    background: 'rgba(255, 255, 255, 0.8)',
    spinner: 'el-icon-loading'
  })

  axios.post(API_BASE_URL + '/upload', formData, { headers: { 'Authorization': 'Bearer ' + getToken() } }).then(res => {
    stopProgressAnimation()
    const data = res.data

    if (data.confidence === '暂无' || data.confidence < 0.85) {
      ElMessageBox.alert('照片拍摄不清晰，请重新拍摄', '提示', {
        confirmButtonText: '确定',
        type: 'warning',
        callback: () => {
          result.value = '识别失败'
          confidence.value = 0
          warning.value = false
          suggestion.value = '无（请上传更清晰的病虫害图像以便系统准确识别）'
          showImage.value = false
          fetchRecords()
        }
      })
    } else {
      ElMessageBox.alert('已识别成功', '提示', {
        confirmButtonText: '确定',
        type: 'success',
        callback: () => {
          result.value = data.result
          confidence.value = data.confidence
          warning.value = data.warning
          suggestion.value = data.suggestion
          imageUrl.value = API_BASE_URL.replace('/api','') + '/uploads/' + data.filename
          showImage.value = true
          fetchRecords()
        }
      })
    }
  }).catch(() => {
    stopProgressAnimation()
    ElMessage.error('识别失败，服务器错误，请稍后重试')
  })
}

function fetchRecords() {
  axios.get(API_BASE_URL + '/records', {
    headers: { 'Authorization': 'Bearer ' + getToken() },
    params: {
      user_id: props.userId,
      page: currentPage.value,
      limit: pageSize.value,
      sort: sortProp.value,
      order: sortOrder.value,
      keyword: keyword.value
    }
  }).then(res => {
    records.value = res.data.records
    total.value = res.data.total
  }).catch(err => {
    if (err.response && err.response.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      logout()
    }
  })
}

function fetchDiseases() {
  axios.get(API_BASE_URL + '/diseases', { headers: { 'Authorization': 'Bearer ' + getToken() } }).then(res => {
    diseaseList.value = res.data
  })
}

function openImage(filename) {
  if (filename) {
    window.open(API_BASE_URL.replace('/api','') + '/uploads/' + filename, '_blank')
  }
}

function handleSortChange({ prop, order }) {
  sortProp.value = prop
  sortOrder.value = order === 'ascending' ? 'asc' : 'desc'
  fetchRecords()
}

function handleSizeChange(newSize) {
  pageSize.value = newSize
  fetchRecords()
}

function handleCurrentChange(newPage) {
  currentPage.value = newPage
  fetchRecords()
}

watch(() => props.userId, () => {
  fetchRecords()
})

onMounted(() => {
  fetchDiseases()
  fetchRecords()
})
</script>

<style scoped>
/* ========== Dashboard Layout ========== */
.dashboard {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0fdf4 0%, #f8fafc 100%);
}

/* ========== Top Navigation ========== */
.top-nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border);
}

.nav-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 64px;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-logo {
  display: flex;
  align-items: center;
}

.nav-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary-dark);
  letter-spacing: 1px;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--text-secondary);
}

.nav-user svg {
  color: var(--text-muted);
}

.logout-btn {
  border-radius: var(--radius-sm);
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* ========== Main Content ========== */
.main-content {
  padding: 32px 24px 60px;
}

.content-inner {
  max-width: 1200px;
  margin: 0 auto;
}

/* ========== Sections ========== */
.section {
  margin-bottom: 40px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.section-title svg {
  color: var(--primary);
}

.section-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-btn {
  border-radius: var(--radius-sm);
}

/* ========== Upload Zone ========== */
.upload-section {
  margin-top: 8px;
}

.upload-zone {
  width: 100%;
}

.upload-zone :deep(.el-upload) {
  width: 100%;
}

.upload-zone :deep(.el-upload-dragger) {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed var(--border);
  border-radius: var(--radius-md);
  background: var(--surface);
  transition: all 0.3s ease;
}

.upload-zone :deep(.el-upload-dragger:hover) {
  border-color: var(--primary-light);
  background: var(--primary-lighter);
}

.upload-zone :deep(.el-upload-dragger.is-dragover) {
  border-color: var(--primary);
  background: var(--primary-lighter);
}

.upload-placeholder {
  text-align: center;
  padding: 20px;
}

.upload-icon {
  margin-bottom: 16px;
}

.upload-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.upload-hint {
  font-size: 13px;
  color: var(--text-muted);
}

/* ========== Result Card ========== */
.result-card {
  background: var(--surface);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border);
  overflow: hidden;
  transition: box-shadow 0.3s ease;
}

.result-card:hover {
  box-shadow: var(--shadow-md);
}

.result-grid {
  display: flex;
  gap: 24px;
  padding: 28px;
}

.result-main {
  flex: 1;
  min-width: 0;
}

.result-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  border-radius: var(--radius-full);
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
}

.badge-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.badge-success {
  background: var(--primary-lighter);
  color: var(--primary-dark);
}

.badge-success .badge-dot {
  background: var(--primary);
}

.badge-warning {
  background: var(--accent-light);
  color: #92400e;
}

.badge-warning .badge-dot {
  background: var(--accent);
}

.result-metrics {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.metric-item {
  background: #f8fafc;
  padding: 12px 18px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
}

.metric-label {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.metric-label-warning {
  color: var(--accent);
}

.metric-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.metric-value-warning {
  color: #92400e;
}

.result-suggestion {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  background: #f8fafc;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
}

.suggestion-icon {
  flex-shrink: 0;
  color: var(--primary);
  margin-top: 2px;
}

.suggestion-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.suggestion-text {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.result-image-wrapper {
  flex-shrink: 0;
  width: 200px;
  height: 200px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 1px solid var(--border);
}

.result-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.result-image:hover {
  transform: scale(1.05);
}

/* ========== Records Table ========== */
.records-table {
  border-radius: var(--radius-sm);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.records-table :deep(.el-table__body tr) {
  transition: background-color 0.2s;
}

.records-table :deep(.el-table__body tr:hover td) {
  background-color: var(--primary-lighter) !important;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* ========== Disease Cards Grid ========== */
.disease-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(265px, 1fr));
  gap: 20px;
}

.disease-card {
  background: var(--surface);
  border-radius: var(--radius-md);
  padding: 24px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
  cursor: default;
}

.disease-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-md);
  border-color: var(--primary-light);
}

.disease-card-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-lighter);
  border-radius: var(--radius-sm);
  color: var(--primary);
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.disease-card:hover .disease-card-icon {
  background: var(--primary);
  color: #fff;
}

.disease-card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.disease-card-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* ========== Footer ========== */
.footer-card {
  display: flex;
  gap: 20px;
  padding: 32px;
  background: linear-gradient(135deg, var(--primary) 0%, #15803d 100%);
  border-radius: var(--radius-md);
  color: #fff;
  align-items: flex-start;
}

.footer-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.15);
  border-radius: var(--radius-sm);
}

.footer-text h4 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.footer-text p {
  font-size: 14px;
  line-height: 1.7;
  opacity: 0.9;
  margin-bottom: 12px;
}

.footer-author {
  font-size: 13px;
  opacity: 0.7;
}

/* ========== Responsive ========== */
@media (max-width: 768px) {
  .nav-inner {
    padding: 0 16px;
  }

  .nav-title {
    font-size: 16px;
  }

  .main-content {
    padding: 20px 16px 40px;
  }

  .result-grid {
    flex-direction: column;
    padding: 20px;
  }

  .result-image-wrapper {
    width: 100%;
    height: auto;
    max-height: 240px;
  }

  .disease-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }

  .footer-card {
    flex-direction: column;
    padding: 24px;
  }
}

@media (max-width: 480px) {
  .nav-user span {
    display: none;
  }

  .section-header {
    flex-direction: column;
    align-items: stretch;
  }

  .section-toolbar {
    width: 100%;
  }

  .section-toolbar .el-input {
    flex: 1;
  }

  .disease-grid {
    grid-template-columns: 1fr;
  }
}
/* ========== Progress Overlay ========== */
.progress-overlay {
  position: fixed;
  inset: 0;
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(4px);
}
.progress-card {
  background: #fff;
  border-radius: 20px;
  padding: 48px 56px 40px;
  text-align: center;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.15);
  max-width: 420px;
  width: 90%;
}
.progress-icon svg {
  animation: rotateSpinner 1.5s linear infinite;
  margin-bottom: 16px;
}
@keyframes rotateSpinner {
  to { transform: rotate(360deg); }
}
.progress-title {
  font-size: 20px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 28px;
}
.progress-bar {
  margin-bottom: 28px;
}
.progress-stages {
  display: flex;
  justify-content: space-between;
  gap: 4px;
}
.progress-stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  flex: 1;
  opacity: 0.4;
  transition: all 0.3s ease;
}
.progress-stage.active {
  opacity: 1;
}
.progress-stage.done {
  opacity: 0.6;
}
.stage-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #e2e8f0;
  transition: all 0.3s ease;
}
.progress-stage.active .stage-dot {
  background: #22c55e;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.4);
}
.progress-stage.done .stage-dot {
  background: #22c55e;
}
.stage-label {
  font-size: 11px;
  color: #475569;
  white-space: nowrap;
}
.progress-fade-enter-active, .progress-fade-leave-active {
  transition: opacity 0.3s ease;
}
.progress-fade-enter-from, .progress-fade-leave-to {
  opacity: 0;
}
</style>




