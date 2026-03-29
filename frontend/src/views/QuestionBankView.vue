<template>
  <div class="qb-page">
    <!-- Header -->
    <header class="page-header">
      <div>
        <h1 class="page-title">题库管理</h1>
        <p class="page-subtitle">上传面试题库，支持按分类组织</p>
      </div>
    </header>

    <!-- 题库统计概览 -->
    <section class="stats-section">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-header">
            <div class="stat-icon">
              <BookOpen :size="14" />
            </div>
            <div class="stat-label">题库文件</div>
          </div>
          <div class="stat-value">{{ list.length }}<span class="stat-unit">个</span></div>
          <div class="stat-detail">{{ list.length }} 个文件</div>
        </div>

        <div class="stat-card">
          <div class="stat-header">
            <div class="stat-icon success">
              <CheckCircle :size="14" />
            </div>
            <div class="stat-label">已向量化</div>
          </div>
          <div class="stat-value">{{ vectorizedCount }}<span class="stat-unit">个</span></div>
          <div class="stat-detail success">可用于检索与出题</div>
        </div>

        <div class="stat-card">
          <div class="stat-header">
            <div class="stat-icon warning">
              <Layers :size="14" />
            </div>
            <div class="stat-label">分类总数</div>
          </div>
          <div class="stat-value">{{ presetCats.length }}<span class="stat-unit">个</span></div>
          <div class="stat-detail">系统可选分类</div>
        </div>

        <div class="stat-card">
          <div class="stat-header">
            <div class="stat-icon danger">
              <Layers :size="14" />
            </div>
            <div class="stat-label">已使用分类</div>
          </div>
          <div class="stat-value">{{ groupedCats.length }}<span class="stat-unit">个</span></div>
          <div class="stat-detail">{{ groupedCats.length }} 个分类已有题库</div>
        </div>
      </div>
    </section>

    <!-- Upload area -->
    <section class="upload-section">
      <div class="upload-card">
        <div class="upload-form">
          <div class="form-group">
            <label class="form-label">选择文件</label>
            <label class="file-input-wrapper">
              <Upload :size="16" />
              <span class="file-input-text">{{ file ? file.name : '选择 PDF 或 MD 文件' }}</span>
              <input type="file" accept=".pdf,.md" @change="onFile" class="file-input-hidden" />
            </label>
          </div>

          <div class="form-group" ref="catDropRef">
            <label class="form-label">分类</label>
            <button @click="catDropOpen = !catDropOpen" type="button" class="category-select" :class="{ open: catDropOpen }">
              <span class="category-text">{{ category === '__custom' ? '自定义...' : (category || '选择分类') }}</span>
              <svg class="category-arrow" :class="{ rotate: catDropOpen }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M6 9l6 6 6-6"/>
              </svg>
            </button>
            <Transition name="dropdown">
              <div v-if="catDropOpen" class="category-dropdown">
                <div v-for="c in presetCats" :key="c" @click="category = c; catDropOpen = false" class="dropdown-item" :class="{ active: category === c }">
                  {{ c }}
                </div>
                <div @click="category = '__custom'; catDropOpen = false" class="dropdown-item custom" :class="{ active: category === '__custom' }">
                  自定义...
                </div>
              </div>
            </Transition>
          </div>

          <div v-if="category === '__custom'" class="form-group">
            <label class="form-label">自定义分类</label>
            <input v-model="customCat" placeholder="输入分类名" class="custom-input" />
          </div>

          <div class="form-actions">
            <button @click="upload" :disabled="!file || !finalCategory || up.uploading.value" class="upload-button">
              {{ up.uploading.value ? '上传中...' : '上传' }}
            </button>
            <button @click="downloadTemplate" class="template-button">下载模板</button>
          </div>
        </div>

        <!-- Upload progress -->
        <div v-if="up.uploading.value" class="upload-progress">
          <div class="progress-info">
            <span class="progress-text">
              {{ up.phase.value === 'processing' ? '服务器处理中，正在向量化...' : '上传中...' }}
            </span>
            <span class="progress-percent">{{ up.progress.value }}%</span>
          </div>
          <div class="progress-bar-container">
            <div class="progress-bar-fill" :class="{ processing: up.phase.value === 'processing' }" :style="{ width: up.progress.value + '%' }"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- Upload tip -->
    <section v-if="uploadTip" class="tip-section">
      <div class="tip-card">
        <span class="tip-text">上传完成，建议点击「查看文本块」检查切割结果，确认每道题是否完整。</span>
        <button @click="uploadTip = false" class="tip-close">&times;</button>
      </div>
    </section>

    <!-- Grouped list -->
    <section v-for="(cat, ci) in groupedCats" :key="cat" class="list-section">
      <div class="list-header">
        <div class="list-dot"></div>
        <h2 class="list-title">{{ cat }}</h2>
        <span class="list-count">({{ grouped[cat].length }})</span>
      </div>

      <div class="qb-list">
        <div v-for="qb in grouped[cat]" :key="qb.id" class="qb-item">
          <div class="qb-info">
            <div class="qb-icon">
              <BookOpen :size="14" />
            </div>
            <span class="qb-name">{{ qb.filename }}</span>
            <span v-if="qb.vectorized" class="qb-badge">已向量化</span>
          </div>
          <div class="qb-actions">
            <button @click="toggleChunks(qb)" class="qb-button">
              {{ qb._showChunks ? '收起' : '查看文本块' }}
            </button>
            <button @click="remove(qb.id)" class="qb-delete">
              <Trash2 :size="14" />
            </button>
          </div>

          <!-- Chunks -->
          <div v-if="qb._showChunks && qb._chunks" class="chunks-container">
            <div v-for="(c, i) in qb._chunks" :key="i" class="chunk-item">
              {{ c.content }}
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Empty State -->
    <section v-if="!groupedCats.length" class="empty-section">
      <div class="empty-state">
        <div class="empty-icon">
          <svg class="empty-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/>
          </svg>
        </div>
        <div class="empty-title">还没有上传题库</div>
        <div class="empty-desc">上传题库后可在面试中获得针对性提问</div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useUpload } from '../composables/useUpload'
import { Upload, BookOpen, CheckCircle, Trash2, Layers } from 'lucide-vue-next'

const API = '/api/qb'
const list = ref([])
const file = ref(null)
const category = ref('')
const customCat = ref('')
const presetCats = ref([])
const up = useUpload()
const uploadTip = ref(false)
const catDropOpen = ref(false)
const catDropRef = ref(null)

function onClickOutside(e) {
  if (catDropRef.value && !catDropRef.value.contains(e.target)) catDropOpen.value = false
}
onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))

const finalCategory = computed(() => category.value === '__custom' ? customCat.value : category.value)

const grouped = computed(() => {
  const g = {}
  for (const qb of list.value) (g[qb.category] ||= []).push(qb)
  return g
})
const groupedCats = computed(() => Object.keys(grouped.value))
const vectorizedCount = computed(() => list.value.filter((qb) => qb.vectorized).length)

const onFile = (e) => { file.value = e.target.files[0] }

function downloadTemplate() {
  const tpl = `# 题库模板 - 每道题以问号结尾，答案紧跟其后
# 系统会在"答案段落结束 + 新问题出现"的边界自动切割

什么是 Java 中的多态？
多态是面向对象的核心特性之一，指同一个方法调用在不同对象上有不同的行为表现。
Java 中多态通过继承和接口实现，分为编译时多态（方法重载）和运行时多态（方法重写）。
运行时多态依赖动态绑定机制，JVM 在运行时根据对象的实际类型决定调用哪个方法。

HashMap 和 ConcurrentHashMap 有什么区别？
HashMap 是非线程安全的，适合单线程场景，允许 null key 和 null value。
ConcurrentHashMap 是线程安全的，JDK8 之后采用 CAS + synchronized 实现分段锁，
读操作无锁，写操作只锁住对应的桶节点，并发性能远优于 Hashtable。

请解释 Spring 中的 IoC 和 DI？
IoC（控制反转）是一种设计思想，将对象的创建和依赖管理交给容器而非手动 new。
DI（依赖注入）是 IoC 的具体实现方式，通过构造器注入、Setter 注入或字段注入，
由 Spring 容器在运行时自动将依赖对象注入到目标 Bean 中。
`
  const blob = new Blob([tpl], { type: 'text/markdown' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = '题库模板.md'
  a.click()
  URL.revokeObjectURL(a.href)
}

async function upload() {
  const form = new FormData()
  form.append('file', file.value)
  form.append('category', finalCategory.value)
  try { await up.send(`${API}/upload`, form) } catch {}
  file.value = null
  up.reset()
  await load()
  uploadTip.value = true
  setTimeout(() => uploadTip.value = false, 6000)
}

async function load() {
  try {
    const [listRes, catRes] = await Promise.all([fetch(`${API}/list`), fetch(`${API}/categories`)])
    list.value = (await listRes.json()).map(q => ({ ...q, _showChunks: false, _chunks: null }))
    presetCats.value = await catRes.json()
  } catch (e) {
    console.warn('Failed to load question banks', e)
  }
  if (!category.value && presetCats.value.length) category.value = presetCats.value[0]
}

async function toggleChunks(qb) {
  if (qb._showChunks) { qb._showChunks = false; return }
  if (!qb._chunks) {
    try {
      const res = await fetch(`${API}/${qb.id}/chunks`)
      qb._chunks = await res.json()
    } catch (e) {
      console.warn('Failed to load chunks', e)
      qb._chunks = []
    }
  }
  qb._showChunks = true
}

async function remove(id) {
  try { await fetch(`${API}/${id}`, { method: 'DELETE' }) } catch {}
  await load()
}

onMounted(load)
</script>

<style scoped>
.qb-page {
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
  padding: 12px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
  display: flex;
  flex-direction: column;
  gap: 6px;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: skeletonShimmer 1.5s ease-in-out infinite, skeletonFadeOut 0.4s ease 0.5s forwards;
  z-index: 1;
}

.stat-card > * {
  position: relative;
  z-index: 2;
  animation: contentFadeIn 0.3s ease 0.5s backwards;
}

.stat-card:hover {
  border-color: rgba(99, 102, 241, 0.2);
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  box-shadow: 0 8px 16px rgba(99, 102, 241, 0.08), 0 4px 8px rgba(0, 0, 0, 0.02);
}

.stat-header {
  display: flex;
  align-items: center;
  gap: 5px;
}

.stat-icon {
  color: #6366f1;
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.stat-icon.success {
  color: #10b981;
}

.stat-icon.warning {
  color: #f59e0b;
}

.stat-icon.danger {
  color: #ef4444;
}

.stat-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #475569;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #0f172a;
  line-height: 1;
}

.stat-unit {
  font-size: 14px;
  color: #64748b;
  margin-left: 4px;
  font-weight: 500;
}

.stat-detail {
  font-size: 11px;
  color: #475569;
  padding-top: 4px;
  border-top: 1px solid #f1f5f9;
}

.stat-detail.success {
  color: #10b981;
  font-weight: 500;
}

/* Upload Section */
.upload-section {
  margin-bottom: 20px;
}

.upload-card {
  padding: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.upload-form {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 160px;
  position: relative;
}

.form-label {
  font-size: 11px;
  font-weight: 500;
  color: #64748b;
  display: block;
  margin-bottom: 6px;
}

.file-input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 10px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.2s;
}

.file-input-wrapper:hover {
  border-color: rgba(99, 102, 241, 0.3);
}

.file-input-text {
  font-size: 12px;
  color: #64748b;
}

.file-input-hidden {
  display: none;
}

.category-select {
  width: 100%;
  padding: 10px 14px;
  border-radius: 10px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  font-size: 12px;
  text-align: left;
  outline: none;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
}

.category-select:hover {
  border-color: #cbd5e1;
}

.category-select.open {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.category-text {
  color: #64748b;
}

.category-arrow {
  width: 16px;
  height: 16px;
  color: #94a3b8;
  flex-shrink: 0;
  transition: transform 0.2s;
}

.category-arrow.rotate {
  transform: rotate(180deg);
}

.category-dropdown {
  position: absolute;
  z-index: 10;
  margin-top: 6px;
  width: 100%;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  padding: 4px 0;
}

.dropdown-item {
  padding: 8px 14px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  color: #0f172a;
}

.dropdown-item:hover {
  background: #f8fafc;
}

.dropdown-item.active {
  background: rgba(99, 102, 241, 0.1);
  color: #6366f1;
  font-weight: 600;
}

.dropdown-item.custom {
  border-top: 1px solid rgba(226, 232, 240, 0.6);
  color: #64748b;
}

.custom-input {
  width: 100%;
  padding: 10px 14px;
  border-radius: 10px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  font-size: 12px;
  color: #0f172a;
  outline: none;
  transition: all 0.2s;
}

.custom-input:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-actions {
  display: flex;
  gap: 8px;
}

.upload-button {
  padding: 10px 20px;
  border-radius: 10px;
  background: #6366f1;
  color: white;
  border: none;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-button:hover:not(:disabled) {
  background: #4f46e5;
}

.upload-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.template-button {
  padding: 10px 20px;
  border-radius: 10px;
  background: transparent;
  color: #6366f1;
  border: 1px solid #e2e8f0;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.template-button:hover {
  background: rgba(99, 102, 241, 0.05);
  border-color: #6366f1;
}

.upload-progress {
  margin-top: 16px;
}

.progress-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.progress-text {
  font-size: 11px;
  color: #64748b;
}

.progress-percent {
  font-size: 11px;
  font-weight: 700;
  color: #6366f1;
}

.progress-bar-container {
  width: 100%;
  height: 6px;
  background: #f1f5f9;
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 3px;
  background: #6366f1;
  transition: width 0.3s;
}

.progress-bar-fill.processing {
  background: #f59e0b;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Tip Section */
.tip-section {
  margin-bottom: 20px;
}

.tip-card {
  padding: 12px 16px;
  background: rgba(99, 102, 241, 0.05);
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.tip-text {
  flex: 1;
  font-size: 12px;
  color: #0f172a;
}

.tip-close {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: transparent;
  border: none;
  color: #64748b;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tip-close:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #0f172a;
}

/* List Section */
.list-section {
  margin-bottom: 20px;
}

.list-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.list-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #6366f1;
}

.list-title {
  font-size: 12px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.list-count {
  font-size: 11px;
  color: #64748b;
}

.qb-list {
  display: flex;
  flex-direction: column;
  gap: 1px;
  background: #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
}

.qb-item {
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
}

.qb-item::before {
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

.qb-item > * {
  position: relative;
  z-index: 2;
  animation: contentFadeIn 0.3s ease 0.3s backwards;
}

.qb-item:hover {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
}

.qb-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
}

.qb-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(99, 102, 241, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
  flex-shrink: 0;
}

.qb-name {
  flex: 1;
  font-size: 12px;
  font-weight: 500;
  color: #0f172a;
}

.qb-badge {
  font-size: 10px;
  padding: 3px 8px;
  border-radius: 5px;
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #16a34a;
  font-weight: 600;
}

.qb-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
}

.qb-button {
  padding: 6px 12px;
  border-radius: 6px;
  background: transparent;
  color: #6366f1;
  border: none;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.qb-button:hover {
  background: rgba(99, 102, 241, 0.1);
}

.qb-delete {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: transparent;
  color: #64748b;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s;
}

.qb-item:hover .qb-delete {
  opacity: 1;
}

.qb-delete:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.chunks-container {
  padding: 0 16px 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chunk-item {
  font-size: 11px;
  color: #64748b;
  background: #f8fafc;
  border-radius: 8px;
  padding: 10px;
  line-height: 1.6;
  white-space: pre-wrap;
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
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.empty-svg {
  width: 28px;
  height: 28px;
  color: #475569;
}

.empty-title {
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 4px;
}

.empty-desc {
  font-size: 11px;
  color: #475569;
  margin-top: 4px;
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

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.dropdown-enter-active, .dropdown-leave-active {
  transition: all 0.15s ease;
}

.dropdown-enter-from, .dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
