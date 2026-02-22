<template>
  <div class="p-10">
    <div class="mb-8 page-enter">
      <h1 class="text-lg font-semibold text-text">面试记录</h1>
      <p class="text-text-secondary text-sm mt-1">查看历史面试表现和评分详情</p>
    </div>

    <!-- Summary stats -->
    <div class="grid grid-cols-3 gap-4 mb-8 page-enter stagger-1">
      <div class="card card-hover rounded-2xl p-4">
        <div class="text-xs text-text-muted font-medium mb-1">已完成</div>
        <div class="text-xl font-bold text-text">{{ doneCount }}</div>
      </div>
      <div class="card card-hover rounded-2xl p-4">
        <div class="text-xs text-text-muted font-medium mb-1">平均分</div>
        <div class="text-xl font-bold text-text">{{ avgScore }}</div>
      </div>
      <div class="card card-hover rounded-2xl p-4">
        <div class="text-xs text-text-muted font-medium mb-1">最高分</div>
        <div class="text-xl font-bold text-success">{{ maxScore }}</div>
      </div>
    </div>

    <!-- Filter tabs -->
    <div class="flex gap-1 mb-6 p-0.5 card rounded-xl w-fit page-enter stagger-2">
      <button v-for="f in filters" :key="f.key" @click="activeFilter = f.key"
        class="px-3.5 py-1.5 rounded-lg text-xs font-medium transition btn-press"
        :class="activeFilter === f.key
          ? 'bg-accent-soft text-accent'
          : 'text-text-muted hover:text-text'">
        {{ f.label }}
      </button>
    </div>

    <!-- List -->
    <div class="space-y-3 page-enter stagger-3">
      <div v-for="item in filtered" :key="item.id"
        class="card card-hover rounded-2xl overflow-hidden cursor-pointer"
        @click="$router.push(`/interview/${item.id}`)">

        <div class="flex items-center justify-between px-5 py-4 group">
          <div class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center text-sm font-bold"
              :class="scoreClass(item.score)">
              {{ item.score || '—' }}
            </div>
            <div>
              <div class="text-sm text-text font-medium group-hover:text-accent transition">{{ item.title }}</div>
              <div class="flex items-center gap-3 mt-0.5">
                <span class="text-xs text-text-muted">{{ item.date }}</span>
                <span class="text-xs text-text-muted">{{ item.duration }}</span>
                <span class="text-xs text-text-muted">{{ item.questions }} 题</span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <span class="text-xs font-medium px-2.5 py-1 rounded-lg"
              :class="item.status === '已完成' ? 'bg-success-soft text-success' : 'bg-warning-soft text-warning'">
              {{ item.status }}
            </span>
            <button @click.stop="deleteItem(item.id)"
              class="w-7 h-7 rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transition text-text-muted hover:text-danger hover:bg-danger-soft">
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6h14"/>
              </svg>
            </button>
            <svg class="w-4 h-4 text-text-muted opacity-0 group-hover:opacity-100 transition"
              viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!filtered.length" class="text-center py-20 page-enter stagger-3">
      <div class="w-16 h-16 rounded-2xl bg-bg flex items-center justify-center mx-auto mb-4">
        <svg class="w-7 h-7 text-text-muted" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M12 8v4l3 3"/><path d="M3.05 11a9 9 0 1118 2 9 9 0 01-18-2z"/>
        </svg>
      </div>
      <div class="text-sm text-text-muted">暂无面试记录</div>
      <div class="text-xs text-text-muted mt-1">完成面试后记录会自动出现在这里</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useConfirm } from '../composables/useConfirm'

const { confirm } = useConfirm()
const activeFilter = ref('all')

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

function scoreClass(score) {
  if (!score) return 'bg-surface text-text-muted border border-border'
  if (score >= 80) return 'bg-success-soft text-success'
  if (score >= 60) return 'bg-warning-soft text-warning'
  return 'bg-danger-soft text-danger'
}

const history = ref([])

onMounted(async () => {
  try {
    const res = await fetch('/api/interview/list')
    const list = await res.json()
    history.value = list.map(item => {
      const date = item.started_at ? new Date(item.started_at).toLocaleDateString('zh-CN') : '—'
      let duration = '—'
      if (item.started_at && item.ended_at) {
        const mins = Math.round((new Date(item.ended_at) - new Date(item.started_at)) / 60000)
        duration = `${mins} 分钟`
      }
      const cats = item.qb_categories || []
      const report = item.report || {}
      return {
        id: item.id,
        title: cats.length ? cats.join(' + ') + ' 模拟面试' : '模拟面试',
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
