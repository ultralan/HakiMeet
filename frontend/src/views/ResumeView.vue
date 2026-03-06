<template>
  <div class="resume-page">
    <!-- Header -->
    <header class="page-header">
      <div>
        <h1 class="page-title">简历管理</h1>
        <p class="page-subtitle">上传简历用于面试时的个性化提问</p>
      </div>
    </header>

    <!-- Resume Stats -->
    <section class="stats-section" v-if="resumes.length">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">
            <FileText :size="14" />
          </div>
          <div class="stat-content">
            <div class="stat-label">简历总数</div>
            <div class="stat-value">{{ resumes.length }}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <CheckCircle :size="14" />
          </div>
          <div class="stat-content">
            <div class="stat-label">已向量化</div>
            <div class="stat-value">{{ vectorizedCount }}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <Tag :size="14" />
          </div>
          <div class="stat-content">
            <div class="stat-label">关键技能</div>
            <div class="stat-value">{{ totalSkills }}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <TrendingUp :size="14" />
          </div>
          <div class="stat-content">
            <div class="stat-label">匹配度</div>
            <div class="stat-value">{{ avgMatchRate }}%</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Resume Analysis -->
    <section class="analysis-section" v-if="resumes.length && selectedResume">
      <div class="analysis-grid">
        <div class="analysis-card">
          <div class="analysis-header">
            <div class="analysis-icon">
              <Sparkles :size="16" />
            </div>
            <div>
              <h3 class="analysis-title">简历分析</h3>
              <p class="analysis-subtitle">{{ selectedResume.filename }}</p>
            </div>
          </div>
          <div class="analysis-content">
            <div class="analysis-item">
              <div class="analysis-item-label">总字数</div>
              <div class="analysis-item-value">{{ selectedResume.wordCount || 1250 }}</div>
            </div>
            <div class="analysis-item">
              <div class="analysis-item-label">工作经验</div>
              <div class="analysis-item-value">{{ selectedResume.experience || '3年' }}</div>
            </div>
            <div class="analysis-item">
              <div class="analysis-item-label">教育背景</div>
              <div class="analysis-item-value">{{ selectedResume.education || '本科' }}</div>
            </div>
            <div class="analysis-item">
              <div class="analysis-item-label">项目经验</div>
              <div class="analysis-item-value">{{ selectedResume.projects || 5 }}</div>
            </div>
          </div>
        </div>

        <div class="analysis-card">
          <div class="analysis-header">
            <div class="analysis-icon">
              <Tag :size="16" />
            </div>
            <div>
              <h3 class="analysis-title">技能标签</h3>
              <p class="analysis-subtitle">提取的关键技能</p>
            </div>
          </div>
          <div class="skills-cloud">
            <div v-for="skill in selectedResume.skills || mockSkills" :key="skill.name"
              class="skill-tag" :class="'skill-' + skill.level">
              {{ skill.name }}
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Upload Area -->
    <section class="upload-section" v-if="!up.uploading.value">
      <label
        class="upload-area"
        :class="{ dragging: dragging }"
        @dragover.prevent="dragging = true"
        @dragleave="dragging = false"
        @drop.prevent="onDrop"
      >
        <input type="file" accept=".pdf,.md" @change="onFile" class="upload-input" />
        <div class="upload-content">
          <div class="upload-icon">
            <Upload :size="20" />
          </div>
          <div class="upload-text">拖拽文件到此处，或 <span class="upload-link">点击上传</span></div>
          <div class="upload-hint">支持 PDF、Markdown 格式</div>
          <div class="upload-privacy">
            <Lock :size="10" />
            简历仅存储在本地，不会上传至任何第三方服务器
          </div>
        </div>
      </label>
    </section>

    <!-- Upload Progress -->
    <section class="progress-section" v-else>
      <div class="progress-card">
        <div class="progress-header">
          <div class="progress-icon">
            <Upload :size="14" />
          </div>
          <div class="progress-info">
            <div class="progress-name">{{ uploadName }}</div>
            <div class="progress-status">
              {{ up.phase.value === 'processing' ? '服务器处理中，正在提取文本并向量化...' : '上传中...' }}
            </div>
          </div>
          <div class="progress-percent">{{ up.progress.value }}%</div>
        </div>
        <div class="progress-bar">
          <div
            class="progress-fill"
            :class="{ processing: up.phase.value === 'processing' }"
            :style="{ width: up.progress.value + '%' }"
          ></div>
        </div>
      </div>
    </section>

    <!-- Resume List -->
    <section class="list-section" v-if="resumes.length">
      <div class="resume-list">
        <div v-for="r in resumes" :key="r.id" class="resume-item">
          <div class="resume-icon">
            <FileText :size="14" />
          </div>
          <div class="resume-info">
            <div class="resume-name">{{ r.filename }}</div>
            <div class="resume-size">{{ r.size || '—' }}</div>
          </div>
          <div class="resume-actions">
            <span class="status-badge" :class="r.vectorized ? 'success' : 'warning'">
              {{ r.vectorized ? '已向量化' : '处理中' }}
            </span>
            <button @click.prevent="remove(r.id)" class="delete-button">
              <Trash2 :size="12" />
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Empty State -->
    <section class="empty-section" v-if="!resumes.length && !up.uploading.value">
      <div class="empty-state">
        <div class="empty-icon">
          <FileText :size="24" />
        </div>
        <div class="empty-title">还没有上传简历</div>
        <div class="empty-desc">上传后可在面试中获得个性化提问</div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUpload } from '../composables/useUpload'
import { Upload, Lock, FileText, Trash2, CheckCircle, Tag, TrendingUp, Sparkles } from 'lucide-vue-next'

const API = '/api/resume'
const resumes = ref([])
const file = ref(null)
const dragging = ref(false)
const uploadName = ref('')
const up = useUpload()

// 简历统计数据
const vectorizedCount = computed(() => resumes.value.filter(r => r.vectorized).length)
const totalSkills = ref(24)
const avgMatchRate = ref(85)
const selectedResume = computed(() => resumes.value[0])

// 模拟技能数据
const mockSkills = [
  { name: 'Vue.js', level: 'high' },
  { name: 'React', level: 'high' },
  { name: 'TypeScript', level: 'high' },
  { name: 'Node.js', level: 'medium' },
  { name: 'Python', level: 'medium' },
  { name: 'Docker', level: 'medium' },
  { name: 'MySQL', level: 'medium' },
  { name: 'Redis', level: 'low' },
  { name: 'Kubernetes', level: 'low' },
]

function onFile(e) {
  file.value = e.target.files[0]
  if (file.value) upload()
}

function onDrop(e) {
  dragging.value = false
  file.value = e.dataTransfer.files[0]
  if (file.value) upload()
}

async function upload() {
  uploadName.value = file.value.name
  const form = new FormData()
  form.append('file', file.value)
  try {
    await up.send(`${API}/upload`, form)
  } catch { /* offline */ }
  file.value = null
  up.reset()
  await load()
}

async function load() {
  try {
    const res = await fetch(`${API}/list`)
    resumes.value = await res.json()
  } catch (e) {
    console.warn('Failed to load resumes', e)
  }
}

async function remove(id) {
  try { await fetch(`${API}/${id}`, { method: 'DELETE' }) } catch {}
  await load()
}

onMounted(load)
</script>

<style scoped>
.resume-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 28px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Header */
.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.025em;
  color: #0f172a;
  margin: 0 0 4px 0;
  line-height: 1.1;
}

.page-subtitle {
  font-size: 14px;
  color: #475569;
  margin: 0;
  font-weight: 400;
}

/* Stats Section */
.stats-section {
  margin-bottom: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.stat-card:hover {
  border-color: rgba(99, 102, 241, 0.2);
  box-shadow: 0 4px 8px rgba(99, 102, 241, 0.08);
}

.stat-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #475569;
  margin-bottom: 2px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1;
}

/* Analysis Section */
.analysis-section {
  margin-bottom: 20px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.analysis-card {
  padding: 14px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.analysis-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.analysis-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
  flex-shrink: 0;
}

.analysis-title {
  font-size: 13px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.analysis-subtitle {
  font-size: 11px;
  color: #475569;
  margin: 2px 0 0 0;
}

.analysis-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.analysis-item {
  padding: 8px;
  background: #f8fafc;
  border-radius: 6px;
}

.analysis-item-label {
  font-size: 10px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 4px;
}

.analysis-item-value {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
}

.skills-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.skill-tag {
  padding: 5px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  transition: all 0.2s;
  cursor: pointer;
}

.skill-high {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #16a34a;
}

.skill-medium {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #2563eb;
}

.skill-low {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  color: #475569;
}

.skill-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Upload Section */
.upload-section {
  margin-bottom: 20px;
}

.upload-area {
  display: block;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 2px dashed #e2e8f0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.upload-area:hover {
  border-color: rgba(99, 102, 241, 0.4);
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.08);
}

.upload-area.dragging {
  border-color: #6366f1;
  background: rgba(99, 102, 241, 0.05);
  transform: scale(1.01);
}

.upload-input {
  display: none;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
}

.upload-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
  margin-bottom: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.upload-area:hover .upload-icon {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

.upload-text {
  font-size: 13px;
  color: #475569;
  margin-bottom: 6px;
}

.upload-link {
  color: #6366f1;
  font-weight: 600;
}

.upload-hint {
  font-size: 11px;
  color: #475569;
  margin-bottom: 12px;
}

.upload-privacy {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  color: #64748b;
  opacity: 0.8;
}

/* Progress Section */
.progress-section {
  margin-bottom: 20px;
}

.progress-card {
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 14px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.progress-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
  flex-shrink: 0;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.progress-info {
  flex: 1;
  min-width: 0;
}

.progress-name {
  font-size: 13px;
  font-weight: 600;
  color: #0f172a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.progress-status {
  font-size: 11px;
  color: #475569;
  margin-top: 2px;
}

.progress-percent {
  font-size: 12px;
  font-weight: 700;
  color: #6366f1;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #f1f5f9;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1 0%, #4f46e5 100%);
  border-radius: 3px;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.progress-fill.processing {
  background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* List Section */
.list-section {
  margin-bottom: 20px;
}

.resume-list {
  display: flex;
  flex-direction: column;
  gap: 1px;
  background: #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
}

.resume-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.resume-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: skeletonShimmer 1.5s ease-in-out infinite, skeletonFadeOut 0.4s ease 0.3s forwards;
  z-index: 1;
}

.resume-item > * {
  position: relative;
  z-index: 2;
  animation: contentFadeIn 0.3s ease 0.3s backwards;
}

.resume-item:hover {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
}

.resume-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
  flex-shrink: 0;
}

.resume-info {
  flex: 1;
  min-width: 0;
}

.resume-name {
  font-size: 13px;
  font-weight: 600;
  color: #0f172a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.resume-size {
  font-size: 11px;
  color: #475569;
  margin-top: 2px;
}

.resume-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 5px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.status-badge.success {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #16a34a;
}

.status-badge.warning {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
}

.delete-button {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #475569;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.resume-item:hover .delete-button {
  opacity: 1;
}

.delete-button:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

/* Empty Section */
.empty-section {
  margin-bottom: 20px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  color: #475569;
}

.empty-title {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 4px;
}

.empty-desc {
  font-size: 12px;
  color: #475569;
}

/* Animations */
@keyframes skeletonShimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

@keyframes skeletonFadeOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}

@keyframes contentFadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
