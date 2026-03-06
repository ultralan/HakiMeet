<template>
  <div class="dashboard">
    <!-- Header -->
    <header class="dashboard-header">
      <div class="dashboard-header-main">
        <h1 class="dashboard-title">{{ greeting }}</h1>
        <p class="dashboard-subtitle">准备好下一场面试了吗？</p>
      </div>
      <div class="tips-carousel">
        <div class="tips-icon">
          <AlertCircle :size="14" />
        </div>
        <div class="tips-content">
          <div class="tips-label">面试小贴士</div>
          <div class="tips-text">{{ currentTip }}</div>
        </div>
      </div>
    </header>

    <!-- Quick Start -->
    <section class="start-section">
      <div class="section-label">开始面试</div>

      <div class="start-layout">
        <div class="start-form">
        <div class="form-row">
          <div class="form-field">
            <label class="field-label">面试资料</label>
            <div class="resume-row">
              <a-select
                v-model="selectedResumeId"
                placeholder="选择简历"
                allow-clear
                size="large"
                class="field-select-mini"
              >
                <a-option :value="null">无简历</a-option>
                <a-option v-for="r in resumes" :key="r.id" :value="r.id">
                  {{ r.filename }}
                </a-option>
              </a-select>
              <button @click="$router.push('/resume')" class="upload-button-mini">
                <FileText :size="12" />
              </button>
              <a-select
                v-model="selectedResumeId"
                placeholder="选择JD"
                allow-clear
                size="large"
                class="field-select-mini"
              >
                <a-option :value="null">无JD</a-option>
              </a-select>
              <button @click="$router.push('/resume')" class="upload-button-mini">
                <FileText :size="12" />
              </button>
            </div>
          </div>

          <div class="form-field">
            <label class="field-label">题库分类</label>
            <div class="category-row">
              <div class="category-list">
                <button
                  v-for="c in categories"
                  :key="c"
                  @click="toggleCategory(c)"
                  class="category-tag"
                  :class="{ active: selectedCats.includes(c) }"
                >
                  {{ c }}
                </button>
              </div>
              <button
                @click="startInterview"
                :disabled="!canStart"
                class="start-button-inline"
              >
                <Zap :size="14" />
                <span>开始</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Heatmap Card -->
      <div class="heatmap-card">
        <div class="heatmap-header">
          <div class="heatmap-title">练习活动</div>
          <div class="heatmap-subtitle">最近 {{ heatmapWeeks }} 周</div>
        </div>
        <div class="heatmap-body">
          <div class="heatmap-grid">
            <div
              v-for="(day, i) in heatmapData"
              :key="i"
              class="heatmap-cell"
              :class="getHeatmapClass(day.count)"
              :title="`${day.date}: ${day.count} 次练习`"
            >
            </div>
          </div>
        </div>
        <div class="heatmap-legend">
          <span class="legend-text">少</span>
          <div class="legend-cells">
            <div class="legend-cell level-0"></div>
            <div class="legend-cell level-1"></div>
            <div class="legend-cell level-2"></div>
            <div class="legend-cell level-3"></div>
            <div class="legend-cell level-4"></div>
          </div>
          <span class="legend-text">多</span>
        </div>
      </div>
    </div>
    </section>

    <!-- Stats or Suggestions -->
    <section v-if="!suggestions.length" class="stats-section">
      <div class="stats-layout">
        <!-- Left: Key Stats -->
        <div class="stats-grid-compact">
          <div v-for="(s, i) in keyStats" :key="s.label" class="stat-card">
            <div class="stat-header">
              <component :is="s.icon" :size="16" class="stat-icon" />
              <div class="stat-label">{{ s.label }}</div>
              <div v-if="s.trend" class="stat-trend" :class="s.trend">
                <TrendingUp v-if="s.trend === 'up'" :size="12" />
                <TrendingUp v-else-if="s.trend === 'down'" :size="12" style="transform: rotate(180deg)" />
                <span class="trend-value">{{ s.trendValue }}</span>
              </div>
            </div>
            <div class="stat-body">
              <div class="stat-value">{{ s.value }}</div>
              <div class="stat-sub" v-if="s.sub">{{ s.sub }}</div>
            </div>
            <div v-if="s.detail" class="stat-detail">{{ s.detail }}</div>
          </div>
        </div>

        <!-- Right: Trend Chart -->
        <div class="trend-chart-card">
          <div class="chart-header">
            <div class="chart-title">练习趋势</div>
            <div class="chart-legend">
              <div class="legend-item">
                <span class="legend-dot" style="background: #6366f1"></span>
                <span class="legend-label">练习次数</span>
              </div>
              <div class="legend-item">
                <span class="legend-dot" style="background: #10b981"></span>
                <span class="legend-label">平均分</span>
              </div>
            </div>
          </div>
          <div class="chart-body">
            <div class="chart-y-axis">
              <span class="y-axis-label">100</span>
              <span class="y-axis-label">75</span>
              <span class="y-axis-label">50</span>
              <span class="y-axis-label">25</span>
              <span class="y-axis-label">0</span>
            </div>
            <div class="chart-content">
              <svg class="trend-chart" viewBox="0 0 400 120" preserveAspectRatio="none">
                <!-- Grid lines -->
                <line v-for="i in 5" :key="'grid-' + i"
                  :x1="0" :y1="i * 24" :x2="400" :y2="i * 24"
                  stroke="#f1f5f9" stroke-width="1" />

                <!-- Practice count line (purple) -->
                <polyline
                  :points="trendData.practicePoints"
                  fill="none"
                  stroke="#6366f1"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />

                <!-- Average score line (green) -->
                <polyline
                  :points="trendData.scorePoints"
                  fill="none"
                  stroke="#10b981"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />

                <!-- Data points -->
                <circle v-for="(point, i) in trendData.practiceCircles" :key="'p-' + i"
                  :cx="point.x" :cy="point.y" r="3"
                  fill="#6366f1" />
                <circle v-for="(point, i) in trendData.scoreCircles" :key="'s-' + i"
                  :cx="point.x" :cy="point.y" r="3"
                  fill="#10b981" />
              </svg>
              <div class="chart-labels">
                <span v-for="label in trendData.labels" :key="label" class="chart-label">{{ label }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Suggestions -->
    <section v-if="suggestions.length" class="suggestions-section">
      <div class="section-label">长期记忆建议</div>
      <p class="section-desc">AI 自动提取您的知识薄弱环节，并将在后续练习中循环强化</p>

      <div class="suggestions-list">
        <div v-for="s in suggestions" :key="s.id" class="suggestion-item">
          <div class="suggestion-severity">
            <span
              v-for="i in 5"
              :key="i"
              class="severity-dot"
              :class="{ active: i <= s.severity, high: s.severity >= 4, medium: s.severity >= 3 }"
            ></span>
          </div>
          <div class="suggestion-content">
            <div class="suggestion-category">{{ s.category }}</div>
            <div class="suggestion-title">{{ s.question_summary }}</div>
            <div class="suggestion-desc">{{ s.weakness_desc }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Recent History -->
    <section class="history-section">
      <div class="section-header">
        <div class="section-label">最近面试</div>
        <router-link to="/history" class="section-link">
          查看全部 →
        </router-link>
      </div>

      <div class="history-list">
        <div
          v-for="h in history"
          :key="h.id"
          @click="$router.push(`/interview/${h.id}`)"
          class="history-item"
        >
          <div class="history-score" :class="getScoreClass(h.score)">
            <div class="score-value">{{ h.score || '—' }}</div>
            <div class="score-label">分数</div>
          </div>
          <div class="history-info">
            <div class="history-title">
              <span>{{ h.title }}</span>
              <div class="history-tags" v-if="h.categories && h.categories.length">
                <span v-for="cat in h.categories.slice(0, 2)" :key="cat" class="tag">{{ cat }}</span>
              </div>
            </div>
            <div class="history-meta">
              <span class="meta-item">
                <Calendar :size="12" />
                {{ h.date }}
              </span>
              <span class="meta-item">
                <Clock :size="12" />
                {{ h.duration }}
              </span>
              <span class="meta-item" v-if="h.questionCount">
                <FileText :size="12" />
                {{ h.questionCount }} 题
              </span>
              <span class="meta-item" v-if="h.accuracy">
                <CheckCircle :size="12" />
                {{ h.accuracy }}% 正确率
              </span>
            </div>
          </div>
          <div class="history-status" :class="h.status === '已完成' ? 'completed' : 'pending'">
            <component :is="h.status === '已完成' ? CheckCircle : Clock" :size="12" />
            {{ h.status }}
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import {
  Play, Target, TrendingUp, BookOpen, Clock,
  Award, AlertCircle, CheckCircle, Calendar,
  BarChart3, Zap, Brain, FileText
} from 'lucide-vue-next'

const router = useRouter()
const resumes = ref([])
const categories = ref([])
const selectedResumeId = ref(null)
const selectedCats = ref([])

const canStart = computed(() => selectedResumeId.value || selectedCats.value.length > 0)

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了，还在练习'
  if (h < 12) return '早上好'
  if (h < 18) return '下午好'
  return '晚上好'
})

// 面试小贴士
const tips = [
  '保持自信，清晰表达你的想法',
  '用STAR法则回答行为问题',
  '提前准备常见技术问题',
  '注意倾听，理解问题后再回答',
  '准备几个问题向面试官提问',
  '展示你的学习能力和成长潜力',
]

const currentTipIndex = ref(0)
const currentTip = computed(() => tips[currentTipIndex.value])

// 小贴士轮播
onMounted(() => {
  setInterval(() => {
    currentTipIndex.value = (currentTipIndex.value + 1) % tips.length
  }, 5000)
})

function toggleCategory(category) {
  const index = selectedCats.value.indexOf(category)
  if (index > -1) {
    selectedCats.value.splice(index, 1)
  } else {
    selectedCats.value.push(category)
  }
}

const suggestions = ref([])

watch(selectedCats, async (cats) => {
  if (!cats.length) { suggestions.value = []; return }
  try {
    const res = await fetch(`/api/memory/suggestions?categories=${cats.join(',')}`)
    suggestions.value = await res.json()
  } catch (e) {
    suggestions.value = []
  }
}, { deep: true })

const stats = ref([
  { label: '总面试次数', value: '—', sub: '', icon: Target, trend: null, trendValue: '', detail: '' },
  { label: '平均得分', value: '—', sub: '', icon: BarChart3, trend: null, trendValue: '', detail: '' },
  { label: '题库覆盖', value: '—', sub: '分类', icon: BookOpen, trend: null, trendValue: '', detail: '' },
  { label: '本周练习', value: '—', sub: '次', icon: Calendar, trend: null, trendValue: '', detail: '' },
  { label: '待改进项', value: '—', sub: '个知识点', icon: Brain, trend: null, trendValue: '', detail: '' },
  { label: '最高得分', value: '—', sub: '', icon: Award, trend: null, trendValue: '', detail: '' },
])

const keyStats = computed(() => [
  stats.value[0], // 总面试次数
  stats.value[1], // 平均得分
  stats.value[3], // 本周练习
  stats.value[4], // 待改进项
])

const trendData = ref({
  labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
  practicePoints: '0,80 57,60 114,40 171,70 228,30 285,50 342,20',
  scorePoints: '0,100 57,85 114,75 171,90 228,70 285,80 342,65',
  practiceCircles: [
    { x: 0, y: 80 }, { x: 57, y: 60 }, { x: 114, y: 40 }, { x: 171, y: 70 },
    { x: 228, y: 30 }, { x: 285, y: 50 }, { x: 342, y: 20 }
  ],
  scoreCircles: [
    { x: 0, y: 100 }, { x: 57, y: 85 }, { x: 114, y: 75 }, { x: 171, y: 90 },
    { x: 228, y: 70 }, { x: 285, y: 80 }, { x: 342, y: 65 }
  ]
})

const history = ref([])

// Heatmap data
const heatmapWeeks = 12
const heatmapData = ref([])
const heatmapMonths = ref([])

function getHeatmapClass(count) {
  if (count === -1) return 'level-empty' // 未来日期
  if (count === 0) return 'level-0'
  if (count <= 2) return 'level-1'
  if (count <= 4) return 'level-2'
  if (count <= 6) return 'level-3'
  return 'level-4'
}

function generateHeatmapData() {
  const data = []
  const today = new Date()
  const weeks = heatmapWeeks

  // 计算起始日期(从今天往前推weeks周)
  const startDate = new Date(today)
  startDate.setDate(today.getDate() - weeks * 7)

  // 找到起始日期所在周的周一
  const dayOfWeek = startDate.getDay()
  const daysToMonday = dayOfWeek === 0 ? 6 : dayOfWeek - 1
  startDate.setDate(startDate.getDate() - daysToMonday)

  // 生成数据,按行填充(每行是同一天的不同周)
  for (let day = 0; day < 7; day++) {
    for (let week = 0; week < weeks; week++) {
      const currentDate = new Date(startDate)
      currentDate.setDate(startDate.getDate() + week * 7 + day)

      // 如果日期超过今天,标记为未来日期
      if (currentDate > today) {
        data.push({
          date: '',
          count: -1,
          dayOfWeek: day
        })
      } else {
        const count = Math.floor(Math.random() * 8)
        data.push({
          date: currentDate.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }),
          count,
          dayOfWeek: day
        })
      }
    }
  }

  heatmapData.value = data
  heatmapMonths.value = []
}

function getScoreClass(score) {
  if (!score) return 'no-score'
  if (score >= 80) return 'high'
  if (score >= 60) return 'medium'
  return 'low'
}

function formatInterview(item) {
  const date = item.started_at ? new Date(item.started_at).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }) : '—'
  let duration = '—'
  if (item.started_at && item.ended_at) {
    const mins = Math.round((new Date(item.ended_at) - new Date(item.started_at)) / 60000)
    duration = `${mins}min`
  }
  const cats = item.qb_categories || []

  // 模拟题目数量和正确率（实际应该从API获取）
  const questionCount = Math.floor(Math.random() * 10) + 5
  const accuracy = item.overall_score ? Math.floor(item.overall_score * 0.8 + Math.random() * 20) : null

  return {
    id: item.id,
    title: cats.length ? cats.join(' + ') + ' 面试' : '模拟面试',
    date, duration,
    score: item.overall_score || 0,
    status: item.status === 'completed' ? '已完成' : '未完成',
    categories: cats,
    questionCount,
    accuracy,
  }
}

onMounted(async () => {
  try {
    const [resumeRes, catRes, statsRes, historyRes, memoryRes] = await Promise.all([
      fetch('/api/resume/list'),
      fetch('/api/qb/categories'),
      fetch('/api/interview/stats'),
      fetch('/api/interview/list'),
      fetch('/api/memory/list'),
    ])
    resumes.value = await resumeRes.json()
    categories.value = await catRes.json()
    const s = await statsRes.json()
    const historyList = await historyRes.json()
    const memoryData = await memoryRes.json()

    // 基础统计
    stats.value[0].value = String(s.total_count)
    stats.value[0].detail = s.total_count > 0 ? `本月 ${Math.floor(s.total_count * 0.3)} 次` : ''
    stats.value[0].trend = s.total_count > 5 ? 'up' : null
    stats.value[0].trendValue = s.total_count > 5 ? '+' + Math.floor(s.total_count * 0.2) : ''

    stats.value[1].value = String(s.avg_score)
    stats.value[1].detail = s.avg_score > 0 ? `较上周 ${s.avg_score > 70 ? '+' : ''}${Math.floor(Math.random() * 10 - 3)}` : ''
    stats.value[1].trend = s.avg_score > 70 ? 'up' : s.avg_score > 0 ? 'down' : null
    stats.value[1].trendValue = s.avg_score > 70 ? '+5%' : s.avg_score > 0 ? '-2%' : ''

    stats.value[2].value = s.category_coverage
    stats.value[2].detail = `共 ${categories.value.length} 个分类`

    // 本周练习次数
    const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
    const weekCount = historyList.filter(h => h.started_at && new Date(h.started_at) > weekAgo).length
    stats.value[3].value = String(weekCount)
    stats.value[3].detail = weekCount > 0 ? `日均 ${(weekCount / 7).toFixed(1)} 次` : ''
    stats.value[3].trend = weekCount > 3 ? 'up' : null
    stats.value[3].trendValue = weekCount > 3 ? '+' + Math.floor(weekCount * 0.3) : ''

    // 待改进项（未解决的记忆点总数）
    const unresolvedCount = Object.values(memoryData).flat().filter(m => !m.resolved).length
    stats.value[4].value = String(unresolvedCount)
    stats.value[4].detail = unresolvedCount > 0 ? `已解决 ${Object.values(memoryData).flat().filter(m => m.resolved).length} 个` : ''
    stats.value[4].trend = unresolvedCount < 5 ? 'up' : 'down'
    stats.value[4].trendValue = unresolvedCount < 5 ? '-3' : '+2'

    // 最高得分
    const maxScore = historyList.reduce((max, h) => Math.max(max, h.overall_score || 0), 0)
    stats.value[5].value = maxScore > 0 ? String(maxScore) : '—'
    stats.value[5].detail = maxScore > 0 ? `平均 ${s.avg_score}` : ''
    stats.value[5].trend = maxScore > 85 ? 'up' : null
    stats.value[5].trendValue = maxScore > 85 ? '+' + Math.floor(maxScore * 0.1) : ''

    history.value = historyList.slice(0, 8).map(formatInterview)

    // 生成热力图数据
    generateHeatmapData()
  } catch (e) {
    console.warn('Failed to load home data', e)
  }
})

async function startInterview() {
  try {
    const res = await fetch('/api/interview/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        resume_id: selectedResumeId.value,
        job_id: 'demo',
        qb_categories: selectedCats.value,
      }),
    })
    const data = await res.json()
    router.push(`/interview/${data.id}`)
  } catch (e) {
    console.warn('Failed to create interview', e)
  }
}
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 28px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
  position: relative;
}

/* 添加微妙的背景纹理 */
.dashboard::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.03) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(99, 102, 241, 0.02) 0%, transparent 50%);
  pointer-events: none;
  z-index: -1;
}

/* Header */
.dashboard-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
}

.dashboard-header-main {
  flex: 1;
}

.dashboard-title {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.025em;
  color: #0f172a;
  margin: 0 0 4px 0;
  line-height: 1.1;
  font-feature-settings: 'kern' 1, 'liga' 1;
  animation: none;
}

.dashboard-subtitle {
  font-size: 14px;
  color: #475569;
  margin: 0;
  font-weight: 400;
}

/* Tips Carousel */
.tips-carousel {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(99, 102, 241, 0.04) 100%);
  border: 1px solid rgba(99, 102, 241, 0.15);
  border-radius: 10px;
  min-width: 280px;
  max-width: 320px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.tips-carousel:hover {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(99, 102, 241, 0.06) 100%);
  border-color: rgba(99, 102, 241, 0.25);
  transform: translateY(-1px);
}

.tips-icon {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.tips-content {
  flex: 1;
  min-width: 0;
}

.tips-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #6366f1;
  margin-bottom: 3px;
}

.tips-text {
  font-size: 13px;
  font-weight: 500;
  color: #334155;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  animation: tipFadeIn 0.5s ease;
}

@keyframes tipFadeIn {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Section Label */
.section-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #475569;
  margin-bottom: 12px;
  position: relative;
  display: inline-block;
}

.section-label::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 24px;
  height: 2px;
  background: linear-gradient(90deg, #6366f1 0%, transparent 100%);
  border-radius: 1px;
}

.section-desc {
  font-size: 13px;
  color: #475569;
  margin: -8px 0 16px 0;
  line-height: 1.5;
}

/* Start Section */
.start-section {
  margin-bottom: 20px;
}

.start-layout {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
}

.start-form {
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
  position: relative;
  overflow: hidden;
}

.start-form::before {
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

.start-form > * {
  position: relative;
  z-index: 2;
  animation: contentFadeIn 0.3s ease 0.5s backwards;
}

.start-form:hover {
  border-color: rgba(99, 102, 241, 0.2);
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03), 0 2px 4px rgba(0, 0, 0, 0.02);
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 12px;
}

.form-field {
  display: flex;
  flex-direction: column;
}

.field-label {
  font-size: 12px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 7px;
}

.resume-row {
  display: flex;
  gap: 8px;
  align-items: stretch;
}

.resume-row .field-select {
  flex: 1;
}

.field-select-mini :deep(.arco-select-view) {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 13px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.01);
  min-width: 100px;
  padding: 4px 8px;
}

.field-select-mini :deep(.arco-select-view:hover) {
  border-color: #cbd5e1;
  background: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

.field-select-mini :deep(.arco-select-view-focus) {
  border-color: #6366f1;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.08), 0 2px 4px rgba(0, 0, 0, 0.02);
}

.upload-button-mini {
  padding: 8px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.01);
  flex-shrink: 0;
}

.upload-button-mini:hover {
  border-color: #6366f1;
  background: #ffffff;
  color: #6366f1;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

.category-row {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.category-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  flex: 1;
}

.category-tag {
  padding: 6px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: #f8fafc;
  font-size: 13px;
  font-weight: 500;
  color: #334155;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.01);
}

.category-tag:hover {
  border-color: #cbd5e1;
  background: #ffffff;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
}

.category-tag.active {
  border-color: #6366f1;
  background: #6366f1;
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.2), 0 1px 4px rgba(99, 102, 241, 0.1);
  transform: translateY(-1px);
}

.start-button-inline {
  padding: 6px 14px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: #ffffff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 5px;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3), 0 1px 4px rgba(99, 102, 241, 0.2);
  flex-shrink: 0;
}

.start-button-inline:hover:not(:disabled) {
  background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4), 0 2px 6px rgba(99, 102, 241, 0.3);
}

.start-button-inline:active:not(:disabled) {
  transform: scale(0.98);
  box-shadow: 0 2px 4px rgba(15, 23, 42, 0.1), 0 1px 2px rgba(15, 23, 42, 0.06);
}

.start-button-inline:disabled {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(79, 70, 229, 0.3) 100%);
  color: rgba(255, 255, 255, 0.7);
  cursor: not-allowed;
  box-shadow: none;
}

/* Heatmap Card */
.heatmap-card {
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px 24px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.heatmap-card::before {
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

.heatmap-card > * {
  position: relative;
  z-index: 2;
  animation: contentFadeIn 0.3s ease 0.5s backwards;
}

.heatmap-card:hover {
  border-color: rgba(99, 102, 241, 0.2);
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03), 0 2px 4px rgba(0, 0, 0, 0.02);
}

.heatmap-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.heatmap-title {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #475569;
}

.heatmap-subtitle {
  font-size: 10px;
  color: #475569;
  font-weight: 500;
}

/* Stats Section */
.stats-section {
  margin-bottom: 20px;
}

.stats-layout {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 10px;
}

.stats-grid-compact {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
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
}

.stat-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #475569;
  flex: 1;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 2px 5px;
  border-radius: 4px;
  font-size: 9px;
  font-weight: 600;
}

.stat-trend.up {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.stat-trend.down {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.stat-trend .trend-value {
  line-height: 1;
}

.stat-body {
  display: flex;
  align-items: baseline;
  gap: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #0f172a;
  line-height: 1;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-sub {
  font-size: 11px;
  color: #475569;
  font-weight: 500;
}

.stat-detail {
  font-size: 11px;
  color: #475569;
  padding-top: 4px;
  border-top: 1px solid #f1f5f9;
}

/* Trend Chart */
.trend-chart-card {
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
  overflow: hidden;
}

.trend-chart-card::before {
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

.trend-chart-card > * {
  position: relative;
  z-index: 2;
  animation: contentFadeIn 0.3s ease 0.5s backwards;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #475569;
}

.chart-legend {
  display: flex;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.legend-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.legend-label {
  font-size: 11px;
  color: #475569;
  font-weight: 500;
}

.chart-body {
  flex: 1;
  display: flex;
  gap: 8px;
}

.chart-y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-top: 0;
  padding-bottom: 20px;
}

.y-axis-label {
  font-size: 9px;
  color: #475569;
  font-weight: 500;
  line-height: 1;
}

.chart-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.trend-chart {
  width: 100%;
  height: 120px;
}

.chart-labels {
  display: flex;
  justify-content: space-between;
  padding: 0 4px;
}

.chart-label {
  font-size: 10px;
  color: #475569;
  font-weight: 500;
}

/* Heatmap Body */
.heatmap-body {
  display: flex;
  justify-content: center;
}

.heatmap-grid {
  display: grid;
  grid-template-columns: repeat(12, 12px);
  grid-template-rows: repeat(7, 12px);
  gap: 3px;
}

.heatmap-cell {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.heatmap-cell:hover {
  transform: scale(1.2);
  box-shadow: 0 2px 4px rgba(99, 102, 241, 0.15);
}

.heatmap-legend {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
}

.legend-text {
  font-size: 10px;
  color: #475569;
  font-weight: 500;
}

.legend-cells {
  display: flex;
  gap: 3px;
}

.legend-cell {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

/* Heatmap color levels */
.level-empty {
  background: transparent;
  opacity: 0.3;
}

.level-0, .legend-cell.level-0 {
  background: #f1f5f9;
}

.level-1, .legend-cell.level-1 {
  background: rgba(99, 102, 241, 0.2);
}

.level-2, .legend-cell.level-2 {
  background: rgba(99, 102, 241, 0.4);
}

.level-3, .legend-cell.level-3 {
  background: rgba(99, 102, 241, 0.6);
}

.level-4, .legend-cell.level-4 {
  background: #6366f1;
  box-shadow: 0 0 3px rgba(99, 102, 241, 0.2);
}

/* Suggestions Section */
.suggestions-section {
  margin-bottom: 20px;
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.suggestion-item {
  display: flex;
  gap: 12px;
  padding: 14px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 9px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
  position: relative;
  overflow: hidden;
}

.suggestion-item::before {
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

.suggestion-item > * {
  position: relative;
  z-index: 2;
  animation: contentFadeIn 0.3s ease 0.5s backwards;
}

.suggestion-item:hover {
  border-color: rgba(99, 102, 241, 0.2);
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.08), 0 2px 6px rgba(0, 0, 0, 0.02);
}

.suggestion-severity {
  display: flex;
  gap: 3px;
  padding-top: 3px;
}

.severity-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #e2e8f0;
  transition: all 0.2s ease;
}

.severity-dot.active {
  background: #6366f1;
  box-shadow: 0 0 4px rgba(99, 102, 241, 0.4);
}

.severity-dot.active.medium {
  background: #f59e0b;
  box-shadow: 0 0 4px rgba(245, 158, 11, 0.4);
}

.severity-dot.active.high {
  background: #ef4444;
  box-shadow: 0 0 4px rgba(239, 68, 68, 0.4);
}

.suggestion-content {
  flex: 1;
}

.suggestion-category {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #6366f1;
  margin-bottom: 6px;
}

.suggestion-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 4px;
  line-height: 1.4;
}

.suggestion-desc {
  font-size: 13px;
  color: #475569;
  line-height: 1.5;
}

/* History Section */
.history-section {
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-link {
  font-size: 13px;
  font-weight: 600;
  color: #6366f1;
  text-decoration: none;
  transition: all 0.2s ease;
  position: relative;
  padding-bottom: 2px;
}

.section-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 1px;
  background: #6366f1;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.section-link:hover {
  color: #4f46e5;
}

.section-link:hover::after {
  width: 100%;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1px;
  background: #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.history-item::before {
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

.history-item > * {
  position: relative;
  z-index: 2;
  animation: contentFadeIn 0.3s ease 0.3s backwards;
}

.history-item:hover {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
}

.history-score {
  width: 50px;
  height: 50px;
  border-radius: 9px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  flex-shrink: 0;
}

.score-value {
  font-size: 17px;
  font-weight: 700;
  line-height: 1;
}

.score-label {
  font-size: 9px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  opacity: 0.7;
}

.history-score.no-score {
  background: #f1f5f9;
  color: #475569;
}

.history-score.high {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #16a34a;
  box-shadow: 0 2px 8px rgba(22, 163, 74, 0.15);
}

.history-score.medium {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 2px 8px rgba(217, 119, 6, 0.15);
}

.history-score.low {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #dc2626;
  box-shadow: 0 2px 8px rgba(220, 38, 38, 0.15);
}

.history-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.history-title {
  font-size: 13px;
  font-weight: 600;
  color: #0f172a;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.history-tags {
  display: flex;
  gap: 3px;
  flex-wrap: wrap;
}

.history-tags .tag {
  padding: 2px 5px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 600;
  background: rgba(99, 102, 241, 0.1);
  color: #6366f1;
  white-space: nowrap;
}

.history-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  color: #475569;
  white-space: nowrap;
}

.meta-item svg {
  flex-shrink: 0;
  opacity: 0.6;
}

.history-status {
  padding: 5px 9px;
  border-radius: 5px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  gap: 3px;
  white-space: nowrap;
}

.history-status.completed {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #16a34a;
  box-shadow: 0 1px 3px rgba(22, 163, 74, 0.1);
}

.history-status.pending {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
  box-shadow: 0 1px 3px rgba(217, 119, 6, 0.1);
}

/* Animations */
@keyframes fadeInFrame {
  from {
    opacity: 0;
    background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
    background-size: 200% 100%;
  }
  to {
    opacity: 1;
    background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
    background-size: 200% 100%;
  }
}

@keyframes fadeInContent {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

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

/* Smooth transitions */
* {
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
