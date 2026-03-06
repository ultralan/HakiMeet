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
            <div class="stat-label">题库总数</div>
          </div>
          <div class="stat-value">{{ totalQuestions }}<span class="stat-unit">道</span></div>
          <div class="stat-detail">{{ list.length }} 个文件</div>
        </div>


        <div class="stat-card">
          <div class="stat-header">
            <div class="stat-icon success">
              <CheckCircle :size="14" />
            </div>
            <div class="stat-label">已练习</div>
          </div>
          <div class="stat-value">{{ practicedQuestions }}<span class="stat-unit">道</span></div>
          <div class="stat-detail success">{{ Math.round(practicedQuestions/totalQuestions*100) }}% 完成度</div>
        </div>

        <div class="stat-card">
          <div class="stat-header">
            <div class="stat-icon warning">
              <TrendingUp :size="14" />
            </div>
            <div class="stat-label">通过率</div>
          </div>
          <div class="stat-value">{{ overallPassRate }}<span class="stat-unit">%</span></div>
          <div class="stat-detail">平均正确率</div>
        </div>

        <div class="stat-card">
          <div class="stat-header">
            <div class="stat-icon danger">
              <Layers :size="14" />
            </div>
            <div class="stat-label">分类数量</div>
          </div>
          <div class="stat-value">{{ presetCats.length }}<span class="stat-unit">个</span></div>
          <div class="stat-detail">{{ groupedCats.length }} 个已使用</div>
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

    <!-- 难度分布 & 分类分析 -->
    <section class="analysis-section">
      <div class="analysis-grid">
        <div class="analysis-card">
          <div class="analysis-header">
            <div class="analysis-icon">
              <BarChart3 :size="16" />
            </div>
            <div>
              <h3 class="analysis-title">难度分布</h3>
              <p class="analysis-subtitle">各难度题目数量</p>
            </div>
          </div>

          <div class="difficulty-list">
            <div v-for="diff in difficultyDistribution" :key="diff.level" class="difficulty-item">
              <div class="difficulty-header">
                <div class="difficulty-info">
                  <span class="difficulty-label">{{ diff.label }}</span>
                  <span class="difficulty-count" :class="diff.level">{{ diff.count }} 道</span>
                </div>
                <span class="difficulty-percent">{{ diff.percentage }}%</span>
              </div>
              <div class="difficulty-bar">
                <div class="difficulty-bar-fill" :class="diff.level" :style="{ width: diff.percentage + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="analysis-card">
          <div class="analysis-header">
            <div class="analysis-icon category">
              <Layers :size="16" />
            </div>
            <div>
              <h3 class="analysis-title">分类分析</h3>
              <p class="analysis-subtitle">各分类题目占比</p>
            </div>
          </div>

          <div class="category-list">
            <div v-for="cat in categoryAnalysis" :key="cat.name" class="category-item">
              <div class="category-count">{{ cat.count }}</div>
              <div class="category-content">
                <div class="category-name">{{ cat.name }}</div>
                <div class="category-progress">
                  <div class="category-bar">
                    <div class="category-bar-fill" :style="{ width: cat.percentage + '%' }"></div>
                  </div>
                  <span class="category-percent">{{ cat.percentage }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 热门题目 -->
    <section class="hot-section">
      <div class="hot-card">
        <div class="hot-header">
          <div class="hot-icon">
            <Zap :size="16" />
          </div>
          <div>
            <h3 class="hot-title">热门题目</h3>
            <p class="hot-subtitle">最近被练习最多的题目</p>
          </div>
        </div>

        <div class="hot-grid">
          <div v-for="q in hotQuestions" :key="q.id" @click="startQuestionPractice(q)" class="hot-item">
            <div class="hot-rank" :class="q.difficulty">{{ q.rank }}</div>
            <div class="hot-content">
              <div class="hot-question-title">{{ q.title }}</div>
              <div class="hot-tags">
                <span class="hot-difficulty" :class="q.difficulty">
                  {{ q.difficulty === 'hard' ? '困难' : q.difficulty === 'medium' ? '中等' : '简单' }}
                </span>
                <span class="hot-category">{{ q.category }}</span>
              </div>
              <div class="hot-stats">
                <span class="hot-stat">
                  <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/>
                  </svg>
                  {{ q.attempts }}人练习
                </span>
                <span class="hot-stat">
                  <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
                    <path d="M22 4L12 14.01l-3-3"/>
                  </svg>
                  {{ q.passRate }}%通过
                </span>
              </div>
            </div>
            <div class="hot-arrow">
              <svg class="arrow-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 18l6-6-6-6"/>
              </svg>
            </div>
          </div>
        </div>
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
import { useRouter } from 'vue-router'
import { useUpload } from '../composables/useUpload'
import { Upload, BookOpen, Zap, Users, CheckCircle, Trash2, ChevronRight, TrendingUp, Layers, BarChart3 } from 'lucide-vue-next'

const router = useRouter()
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

// 题库统计数据
const totalQuestions = ref(328)
const practicedQuestions = ref(156)
const overallPassRate = ref(78)

// 难度分布
const difficultyDistribution = ref([
  { level: 'easy', label: '简单', count: 145, percentage: 44 },
  { level: 'medium', label: '中等', count: 132, percentage: 40 },
  { level: 'hard', label: '困难', count: 51, percentage: 16 },
])

// 分类分析
const categoryAnalysis = ref([
  { name: '数组与字符串', count: 68, percentage: 21, color: 'bg-gradient-to-br from-accent to-accent-hover text-white' },
  { name: '链表与树', count: 52, percentage: 16, color: 'bg-gradient-to-br from-success to-success/80 text-white' },
  { name: '动态规划', count: 45, percentage: 14, color: 'bg-gradient-to-br from-warning to-warning/80 text-white' },
  { name: '图算法', count: 38, percentage: 12, color: 'bg-gradient-to-br from-danger to-danger/80 text-white' },
  { name: '系统设计', count: 125, percentage: 37, color: 'bg-gradient-to-br from-purple-500 to-purple-600 text-white' },
])

const hotQuestions = ref([
  { id: 1, rank: 1, title: '两数之和', difficulty: 'easy', category: '数组', attempts: 1234, passRate: 85 },
  { id: 2, rank: 2, title: '反转链表', difficulty: 'easy', category: '链表', attempts: 987, passRate: 78 },
  { id: 3, rank: 3, title: '二叉树的最大深度', difficulty: 'medium', category: '树', attempts: 856, passRate: 72 },
  { id: 4, rank: 4, title: '合并两个有序数组', difficulty: 'easy', category: '数组', attempts: 745, passRate: 88 },
])

function startQuestionPractice(question) {
  // 这里可以实现题目练习的逻辑，暂时只是一个占位符
  console.log('开始练习题目:', question.title)
}

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
  padding: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.analysis-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.analysis-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
}

.analysis-icon.category {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
  color: #10b981;
}

.analysis-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.analysis-subtitle {
  font-size: 11px;
  color: #475569;
  margin: 2px 0 0 0;
}

.difficulty-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.difficulty-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.difficulty-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.difficulty-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.difficulty-label {
  font-size: 12px;
  font-weight: 600;
  color: #0f172a;
}

.difficulty-count {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 700;
}

.difficulty-count.easy {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #16a34a;
}

.difficulty-count.medium {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
}

.difficulty-count.hard {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #dc2626;
}

.difficulty-percent {
  font-size: 11px;
  font-weight: 700;
  color: #475569;
}

.difficulty-bar {
  width: 100%;
  height: 6px;
  background: #f1f5f9;
  border-radius: 3px;
  overflow: hidden;
}

.difficulty-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.difficulty-bar-fill.easy {
  background: linear-gradient(90deg, #10b981 0%, #059669 100%);
}

.difficulty-bar-fill.medium {
  background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
}

.difficulty-bar-fill.hard {
  background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);
}

/* Category List */
.category-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 10px;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border: 1px solid #e2e8f0;
  transition: all 0.2s;
  cursor: pointer;
}

.category-item:hover {
  border-color: #6366f1;
  box-shadow: 0 2px 4px rgba(99, 102, 241, 0.1);
}

.category-count {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(99, 102, 241, 0.2);
  transition: all 0.2s;
}

.category-item:hover .category-count {
  box-shadow: 0 4px 8px rgba(99, 102, 241, 0.3);
}

.category-content {
  flex: 1;
  min-width: 0;
}

.category-name {
  font-size: 12px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 4px;
}

.category-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-bar {
  flex: 1;
  height: 6px;
  background: #f1f5f9;
  border-radius: 3px;
  overflow: hidden;
}

.category-bar-fill {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, #6366f1 0%, #4f46e5 100%);
  transition: width 0.5s ease;
}

.category-percent {
  font-size: 11px;
  font-weight: 700;
  color: #475569;
}

/* Hot Section */
.hot-section {
  margin-bottom: 20px;
}

.hot-card {
  padding: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.hot-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.hot-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ef4444;
}

.hot-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.hot-subtitle {
  font-size: 11px;
  color: #475569;
  margin: 2px 0 0 0;
}

.hot-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.hot-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 10px;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border: 1px solid #e2e8f0;
  transition: all 0.2s;
  cursor: pointer;
}

.hot-item:hover {
  border-color: #6366f1;
  box-shadow: 0 4px 8px rgba(99, 102, 241, 0.1);
}

.hot-rank {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}

.hot-rank.easy {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.hot-rank.medium {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.hot-rank.hard {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.hot-item:hover .hot-rank {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.hot-content {
  flex: 1;
  min-width: 0;
}

.hot-question-title {
  font-size: 12px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 6px;
  transition: color 0.2s;
}

.hot-item:hover .hot-question-title {
  color: #6366f1;
}

.hot-tags {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.hot-difficulty {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.hot-difficulty.easy {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #16a34a;
}

.hot-difficulty.medium {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
}

.hot-difficulty.hard {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #dc2626;
}

.hot-category {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(99, 102, 241, 0.1);
  color: #6366f1;
  font-weight: 700;
}

.hot-stats {
  display: flex;
  align-items: center;
  gap: 12px;
}

.hot-stat {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #475569;
  font-weight: 500;
}

.stat-icon {
  width: 12px;
  height: 12px;
  opacity: 0.6;
}

.hot-arrow {
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.2s;
}

.hot-item:hover .hot-arrow {
  opacity: 1;
}

.arrow-icon {
  width: 20px;
  height: 20px;
  color: #6366f1;
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
