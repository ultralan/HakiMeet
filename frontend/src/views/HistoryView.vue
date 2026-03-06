<template>
  <div class="history-page">
    <!-- Header -->
    <header class="page-header">
      <div>
        <h1 class="page-title">面试记录</h1>
        <p class="page-subtitle">查看历史面试表现和评分详情</p>
      </div>
    </header>

    <!-- Summary Stats -->
    <section class="stats-section">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-header">
            <div class="stat-icon">
              <CheckCircle :size="14" />
            </div>
            <div class="stat-label">已完成</div>
          </div>
          <div class="stat-value">{{ doneCount }}</div>
          <div class="stat-detail">共 {{ history.length }} 次面试</div>
        </div>

        <div class="stat-card">
          <div class="stat-header">
            <div class="stat-icon">
              <BarChart3 :size="14" />
            </div>
            <div class="stat-label">平均分</div>
          </div>
          <div class="stat-value">{{ avgScore }}</div>
          <div class="stat-detail" v-if="avgScore !== '—'">{{ avgScore >= 70 ? '表现良好' : '继续加油' }}</div>
        </div>

        <div class="stat-card">
          <div class="stat-header">
            <div class="stat-icon">
              <Award :size="14" />
            </div>
            <div class="stat-label">最高分</div>
          </div>
          <div class="stat-value" :class="{ 'high-score': maxScore >= 80 }">{{ maxScore }}</div>
          <div class="stat-detail" v-if="maxScore !== '—'">{{ maxScore >= 80 ? '优秀成绩' : '继续努力' }}</div>
        </div>
      </div>
    </section>

    <!-- Score Trend Chart -->
    <section class="trend-section">
      <div class="trend-card">
        <div class="trend-header">
          <div class="trend-title-group">
            <div class="trend-icon">
              <TrendingUp :size="16" />
            </div>
            <div>
              <h3 class="trend-title">分数趋势</h3>
              <p class="trend-subtitle">最近 10 次面试表现</p>
            </div>
          </div>
          <div class="trend-tabs">
            <button class="trend-tab active">分数</button>
            <button class="trend-tab">时长</button>
          </div>
        </div>
        <div class="trend-chart">
          <div class="chart-grid">
            <div v-for="i in 5" :key="i" class="grid-line"></div>
          </div>
          <div class="chart-content">
            <div v-for="(point, i) in scoreTrend" :key="i" class="chart-point-wrapper">
              <div class="chart-bar" :style="{ height: (point.score / 100 * 100) + '%' }">
                <div class="bar-fill" :class="getScoreBarClass(point.score)"></div>
                <div class="bar-tooltip">{{ point.score }}分</div>
              </div>
              <div class="chart-label">{{ point.date }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Ability Analysis -->
    <section class="ability-section">
      <div class="ability-grid">
        <div class="ability-card">
          <div class="ability-header">
            <div class="ability-icon">
              <Target :size="16" />
            </div>
            <div>
              <h3 class="ability-title">能力雷达</h3>
              <p class="ability-subtitle">各维度评分分析</p>
            </div>
          </div>
          <div class="radar-chart">
            <div class="radar-grid">
              <div v-for="i in 5" :key="i" class="radar-ring" :style="{ width: (i * 20) + '%', height: (i * 20) + '%' }"></div>
            </div>
            <div class="radar-axes">
              <div v-for="(ability, i) in abilities" :key="i" class="radar-axis" :style="{ transform: `rotate(${i * 72}deg)` }">
                <div class="axis-line"></div>
              </div>
            </div>
            <div class="radar-labels">
              <div v-for="(ability, i) in abilities" :key="i" class="radar-label" :style="getLabelPosition(i)">
                <div class="label-text">{{ ability.name }}</div>
                <div class="label-score">{{ ability.score }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="ability-card">
          <div class="ability-header">
            <div class="ability-icon">
              <BarChart3 :size="16" />
            </div>
            <div>
              <h3 class="ability-title">能力详情</h3>
              <p class="ability-subtitle">各项能力得分</p>
            </div>
          </div>
          <div class="ability-list">
            <div v-for="ability in abilities" :key="ability.name" class="ability-item">
              <div class="ability-item-header">
                <span class="ability-name">{{ ability.name }}</span>
                <span class="ability-score">{{ ability.score }}/100</span>
              </div>
              <div class="ability-bar">
                <div class="ability-bar-fill" :class="getAbilityBarClass(ability.score)" :style="{ width: ability.score + '%' }"></div>
              </div>
              <div class="ability-feedback">{{ ability.feedback }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Filter Tabs -->
    <section class="filter-section">
      <div class="filter-tabs">
        <button
          v-for="f in filters"
          :key="f.key"
          @click="activeFilter = f.key"
          class="filter-tab"
          :class="{ active: activeFilter === f.key }"
        >
          {{ f.label }}
          <span class="filter-count" v-if="f.key === 'all'">{{ history.length }}</span>
          <span class="filter-count" v-else-if="f.key === 'done'">{{ doneCount }}</span>
          <span class="filter-count" v-else>{{ history.length - doneCount }}</span>
        </button>
      </div>
    </section>

    <!-- History List -->
    <section class="list-section">
      <div class="history-list">
        <div
          v-for="item in filtered"
          :key="item.id"
          @click="$router.push(`/interview/${item.id}`)"
          class="history-item"
        >
          <div class="history-score" :class="getScoreClass(item.score)">
            <div class="score-value">{{ item.score || '—' }}</div>
            <div class="score-label">分数</div>
          </div>

          <div class="history-info">
            <div class="history-title">{{ item.title }}</div>
            <div class="history-meta">
              <span class="meta-item">
                <Calendar :size="11" />
                {{ item.date }}
              </span>
              <span class="meta-item">
                <Clock :size="11" />
                {{ item.duration }}
              </span>
              <span class="meta-item">
                <FileText :size="11" />
                {{ item.questions }} 题
              </span>
            </div>
          </div>

          <div class="history-actions">
            <span class="status-badge" :class="item.status === '已完成' ? 'completed' : 'pending'">
              {{ item.status }}
            </span>
            <button @click.stop="deleteItem(item.id)" class="delete-button">
              <Trash2 :size="12" />
            </button>
            <ChevronRight :size="14" class="chevron-icon" />
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!filtered.length" class="empty-state">
        <div class="empty-icon">
          <Clock :size="24" />
        </div>
        <div class="empty-title">暂无面试记录</div>
        <div class="empty-desc">完成面试后记录会自动出现在这里</div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useConfirm } from '../composables/useConfirm'
import {
  Trash2, ChevronRight, Clock, CheckCircle,
  BarChart3, Award, Calendar, FileText, TrendingUp, Target
} from 'lucide-vue-next'

const { confirm } = useConfirm()
const activeFilter = ref('all')
const history = ref([])

// 分数趋势数据
const scoreTrend = ref([
  { date: '1/15', score: 72 },
  { date: '1/18', score: 68 },
  { date: '1/22', score: 75 },
  { date: '1/25', score: 82 },
  { date: '1/28', score: 78 },
  { date: '2/01', score: 85 },
  { date: '2/05', score: 88 },
  { date: '2/08', score: 83 },
  { date: '2/12', score: 90 },
  { date: '2/15', score: 87 },
])

// 能力雷达数据
const abilities = ref([
  { name: '技术深度', score: 85, feedback: '对核心技术理解深入' },
  { name: '系统设计', score: 78, feedback: '架构思维清晰' },
  { name: '代码质量', score: 82, feedback: '代码规范性好' },
  { name: '沟通表达', score: 75, feedback: '表达较为清晰' },
  { name: '问题解决', score: 88, feedback: '分析问题能力强' },
])

function getScoreBarClass(score) {
  if (score >= 80) return 'bar-high'
  if (score >= 60) return 'bar-medium'
  return 'bar-low'
}

function getAbilityBarClass(score) {
  if (score >= 80) return 'ability-high'
  if (score >= 60) return 'ability-medium'
  return 'ability-low'
}

function getLabelPosition(index) {
  const angle = index * 72 - 90
  const radius = 45
  const x = 50 + radius * Math.cos(angle * Math.PI / 180)
  const y = 50 + radius * Math.sin(angle * Math.PI / 180)
  return {
    left: x + '%',
    top: y + '%',
    transform: 'translate(-50%, -50%)'
  }
}

const doneList = computed(() => history.value.filter(h => h.status === '已完成'))
const doneCount = computed(() => doneList.value.length)
const avgScore = computed(() => {
  if (!doneList.value.length) return '—'
  return Math.round(doneList.value.reduce((s, h) => s + h.score, 0) / doneList.value.length)
})
const maxScore = computed(() => doneList.value.length ? Math.max(...doneList.value.map(h => h.score)) : '—')

const filters = [
  { key: 'all', label: '全部' },
  { key: 'done', label: '已完成' },
  { key: 'incomplete', label: '未完成' },
]

function getScoreClass(score) {
  if (!score) return 'no-score'
  if (score >= 80) return 'high'
  if (score >= 60) return 'medium'
  return 'low'
}

onMounted(async () => {
  try {
    const res = await fetch('/api/interview/list')
    const list = await res.json()
    history.value = list.map(item => {
      const date = item.started_at ? new Date(item.started_at).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }) : '—'
      let duration = '—'
      if (item.started_at && item.ended_at) {
        const mins = Math.round((new Date(item.ended_at) - new Date(item.started_at)) / 60000)
        duration = `${mins}min`
      }
      const cats = item.qb_categories || []
      const report = item.report || {}
      return {
        id: item.id,
        title: cats.length ? cats.join(' + ') + ' 面试' : '模拟面试',
        date, duration,
        questions: report.turn_count || 0,
        score: item.overall_score || 0,
        status: item.status === 'completed' ? '已完成' : '未完成',
      }
    })
  } catch (e) {
    console.warn('Failed to load history', e)
  }
})

async function deleteItem(id) {
  if (!await confirm('确定删除这条面试记录吗？', true)) return
  try {
    await fetch(`/api/interview/${id}`, { method: 'DELETE' })
    history.value = history.value.filter(h => h.id !== id)
  } catch (e) {
    console.warn('Delete failed', e)
  }
}

const filtered = computed(() => {
  if (activeFilter.value === 'done') return history.value.filter(h => h.status === '已完成')
  if (activeFilter.value === 'incomplete') return history.value.filter(h => h.status !== '已完成')
  return history.value
})
</script>

<style scoped>
.history-page {
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
  grid-template-columns: repeat(3, 1fr);
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

.stat-value.high-score {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-detail {
  font-size: 11px;
  color: #475569;
  padding-top: 4px;
  border-top: 1px solid #f1f5f9;
}

/* Filter Section */
.filter-section {
  margin-bottom: 16px;
}

.filter-tabs {
  display: inline-flex;
  gap: 4px;
  padding: 4px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.filter-tab {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #475569;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 4px;
}

.filter-tab:hover {
  color: #334155;
  background: #f8fafc;
}

.filter-tab.active {
  color: #6366f1;
  background: rgba(99, 102, 241, 0.1);
  box-shadow: 0 2px 4px rgba(99, 102, 241, 0.1);
}

.filter-count {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 5px;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.05);
  line-height: 1;
}

.filter-tab.active .filter-count {
  background: rgba(99, 102, 241, 0.15);
  color: #6366f1;
}

/* List Section */
.list-section {
  margin-bottom: 20px;
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
  gap: 4px;
  min-width: 0;
}

.history-title {
  font-size: 13px;
  font-weight: 600;
  color: #0f172a;
  overflow: hidden;
  text-overflow: ellipsis;
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

.history-actions {
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

.status-badge.completed {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #16a34a;
}

.status-badge.pending {
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

.history-item:hover .delete-button {
  opacity: 1;
}

.delete-button:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.chevron-icon {
  color: #475569;
  opacity: 0;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.history-item:hover .chevron-icon {
  opacity: 1;
}

/* Empty State */
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

/* Trend Section */
.trend-section {
  margin-bottom: 20px;
}

.trend-card {
  padding: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.trend-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.trend-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.trend-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
}

.trend-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.trend-subtitle {
  font-size: 11px;
  color: #475569;
  margin: 2px 0 0 0;
}

.trend-tabs {
  display: flex;
  gap: 4px;
  padding: 3px;
  background: #f8fafc;
  border-radius: 6px;
}

.trend-tab {
  padding: 5px 12px;
  border: none;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  color: #475569;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.trend-tab:hover {
  color: #334155;
}

.trend-tab.active {
  color: #6366f1;
  background: white;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.trend-chart {
  position: relative;
  height: 180px;
}

.chart-grid {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 10px 0;
}

.grid-line {
  height: 1px;
  background: #f1f5f9;
}

.chart-content {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  padding: 10px 0 30px 0;
}

.chart-point-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.chart-bar {
  width: 100%;
  max-width: 32px;
  position: relative;
  display: flex;
  align-items: flex-end;
  cursor: pointer;
}

.bar-fill {
  width: 100%;
  border-radius: 4px 4px 0 0;
  transition: all 0.3s;
}

.bar-high {
  background: linear-gradient(180deg, #10b981 0%, #059669 100%);
}

.bar-medium {
  background: linear-gradient(180deg, #f59e0b 0%, #d97706 100%);
}

.bar-low {
  background: linear-gradient(180deg, #ef4444 0%, #dc2626 100%);
}

.chart-bar:hover .bar-fill {
  opacity: 0.8;
}

.bar-tooltip {
  position: absolute;
  top: -28px;
  left: 50%;
  transform: translateX(-50%);
  background: #0f172a;
  color: white;
  font-size: 10px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s;
}

.chart-bar:hover .bar-tooltip {
  opacity: 1;
}

.chart-label {
  font-size: 10px;
  color: #475569;
  font-weight: 500;
}

/* Ability Section */
.ability-section {
  margin-bottom: 20px;
}

.ability-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.ability-card {
  padding: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.ability-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.ability-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
}

.ability-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.ability-subtitle {
  font-size: 11px;
  color: #475569;
  margin: 2px 0 0 0;
}

.radar-chart {
  position: relative;
  width: 100%;
  padding-top: 100%;
}

.radar-grid {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.radar-ring {
  position: absolute;
  border: 1px solid #e2e8f0;
  border-radius: 50%;
}

.radar-axes {
  position: absolute;
  inset: 0;
}

.radar-axis {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 50%;
  height: 1px;
  transform-origin: left center;
}

.axis-line {
  width: 100%;
  height: 1px;
  background: #e2e8f0;
}

.radar-labels {
  position: absolute;
  inset: 0;
}

.radar-label {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.label-text {
  font-size: 11px;
  font-weight: 600;
  color: #0f172a;
  white-space: nowrap;
}

.label-score {
  font-size: 10px;
  font-weight: 700;
  color: #6366f1;
  padding: 2px 6px;
  background: rgba(99, 102, 241, 0.1);
  border-radius: 4px;
}

.ability-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.ability-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ability-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.ability-name {
  font-size: 12px;
  font-weight: 600;
  color: #0f172a;
}

.ability-score {
  font-size: 11px;
  font-weight: 700;
  color: #475569;
}

.ability-bar {
  width: 100%;
  height: 6px;
  background: #f1f5f9;
  border-radius: 3px;
  overflow: hidden;
}

.ability-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.ability-high {
  background: linear-gradient(90deg, #10b981 0%, #059669 100%);
}

.ability-medium {
  background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
}

.ability-low {
  background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);
}

.ability-feedback {
  font-size: 10px;
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
