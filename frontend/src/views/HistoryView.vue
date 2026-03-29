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
  BarChart3, Award, Calendar, FileText
} from 'lucide-vue-next'

const { confirm } = useConfirm()
const activeFilter = ref('all')
const history = ref([])

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
