<template>
  <div class="p-10">
    <!-- Header -->
    <div class="mb-8 page-enter">
      <h1 class="text-lg font-semibold text-text">{{ greeting }}</h1>
      <p class="text-text-secondary text-sm mt-1">准备好下一场面试了吗？</p>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-3 gap-5 mb-8">
      <div v-for="(s, i) in stats" :key="s.label"
        class="card card-hover rounded-2xl p-5 page-enter" :class="'stagger-' + (i + 1)">
        <div class="flex items-center justify-between mb-3">
          <div class="text-xs text-text-muted font-medium">{{ s.label }}</div>
          <div class="w-8 h-8 rounded-lg flex items-center justify-center" :class="s.iconBg">
            <svg class="w-4 h-4" :class="s.iconColor" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path :d="s.icon" />
            </svg>
          </div>
        </div>
        <div class="text-2xl font-bold text-text">{{ s.value }}</div>
        <div class="text-xs mt-1.5 font-medium" :class="s.color">{{ s.sub }}</div>
      </div>
    </div>

    <!-- Quick Start -->
    <div class="card rounded-2xl p-6 mb-8 page-enter stagger-2">
      <h2 class="text-sm font-semibold text-text mb-5">快速开始面试</h2>

      <div class="grid grid-cols-2 gap-5 mb-5">
        <div>
          <label class="text-xs text-text-muted font-medium block mb-2">选择简历（可选）</label>
          <div class="relative" ref="dropdownRef">
            <button @click="dropOpen = !dropOpen" type="button"
              class="w-full bg-bg border border-border rounded-xl px-3.5 py-2.5 text-sm text-left outline-none transition flex items-center justify-between"
              :class="dropOpen ? 'border-accent ring-2 ring-accent-soft' : 'hover:border-border-light'">
              <span :class="selectedResumeId ? 'text-text' : 'text-text-muted'">{{ selectedResumeLabel }}</span>
              <svg class="w-4 h-4 text-text-muted shrink-0 transition-transform" :class="dropOpen && 'rotate-180'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
            </button>
            <Transition name="drop">
              <div v-if="dropOpen"
                class="absolute z-10 mt-1.5 w-full bg-surface border border-border rounded-xl shadow-md overflow-hidden py-1">
                <div v-for="opt in resumeOptions" :key="opt.value"
                  @click="selectedResumeId = opt.value; dropOpen = false"
                  class="px-3.5 py-2 text-sm cursor-pointer transition"
                  :class="selectedResumeId === opt.value ? 'bg-accent-soft text-accent font-medium' : 'text-text hover:bg-surface-hover'">
                  {{ opt.label }}
                </div>
              </div>
            </Transition>
          </div>
        </div>

        <div>
          <label class="text-xs text-text-muted font-medium block mb-2">题库分类</label>
          <div class="flex flex-wrap gap-2">
            <button v-for="c in categories" :key="c"
              @click="toggleCat(c)"
              class="px-3.5 py-1.5 rounded-lg text-xs font-medium border transition btn-press"
              :class="selectedCats.includes(c)
                ? 'bg-accent text-white border-accent shadow-sm'
                : 'bg-surface border-border text-text-secondary hover:border-accent/30 hover:text-accent'">
              {{ c }}
            </button>
          </div>
        </div>
      </div>

      <button @click="startInterview" :disabled="!canStart"
        class="px-6 py-2.5 rounded-xl text-sm font-semibold transition btn-press
          bg-accent text-white hover:bg-accent-hover shadow-sm hover:shadow-md
          disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none">
        开始面试
      </button>
    </div>

    <!-- 建议复习 -->
    <div v-if="suggestions.length" class="card rounded-2xl p-6 mb-8 page-enter stagger-2">
      <div class="flex items-center gap-2 mb-4">
        <svg class="w-4 h-4 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        </svg>
        <h2 class="text-sm font-semibold text-text">长期记忆建议</h2>
        <span class="text-[11px] text-text-muted">AI 自动提取您的知识薄弱环节，并将在后续练习中循环强化</span>
      </div>
      <div class="space-y-2.5">
        <div v-for="s in suggestions" :key="s.id"
          class="flex items-start gap-3 rounded-xl bg-bg p-3.5 group hover:bg-warning-soft/30 transition">
          <div class="flex gap-0.5 mt-1 shrink-0">
            <span v-for="i in 5" :key="i"
              class="w-1.5 h-1.5 rounded-full"
              :class="i <= s.severity
                ? (s.severity >= 4 ? 'bg-danger' : s.severity >= 3 ? 'bg-warning' : 'bg-accent')
                : 'bg-border'">
            </span>
          </div>
          <div class="min-w-0">
            <span class="text-[10px] px-1.5 py-0.5 rounded bg-accent-soft text-accent font-medium mr-1.5">{{ s.category }}</span>
            <span class="text-sm text-text font-medium">{{ s.question_summary }}</span>
            <div class="text-xs text-text-muted mt-0.5">{{ s.weakness_desc }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tips -->
    <div class="card rounded-2xl p-6 mb-8 page-enter stagger-3">
      <h2 class="text-sm font-semibold text-text mb-4">面试小贴士</h2>
      <div class="grid grid-cols-3 gap-4">
        <div v-for="tip in tips" :key="tip.title"
          class="rounded-xl bg-bg p-4 group hover:bg-accent-soft transition">
          <div class="text-sm font-medium text-text mb-1 group-hover:text-accent transition">{{ tip.title }}</div>
          <div class="text-xs text-text-muted leading-relaxed">{{ tip.desc }}</div>
        </div>
      </div>
    </div>

    <!-- Recent History -->
    <div class="page-enter stagger-4">
      <router-link to="/history" class="text-sm font-semibold text-text mb-4 inline-flex items-center gap-1.5 hover:text-accent transition no-underline group">
        最近面试
        <svg class="w-3.5 h-3.5 text-text-muted group-hover:text-accent transition translate-x-0 group-hover:translate-x-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
      </router-link>
      <div class="card rounded-2xl overflow-hidden divide-y divide-border/60">
        <div v-for="h in history" :key="h.id"
          class="flex items-center justify-between px-5 py-4 hover:bg-surface-hover transition cursor-pointer group"
          @click="$router.push(`/interview/${h.id}`)">
          <div class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xs font-bold"
              :class="!h.score ? 'bg-bg text-text-muted' : h.score >= 80 ? 'bg-success-soft text-success' : h.score >= 60 ? 'bg-warning-soft text-warning' : 'bg-danger-soft text-danger'">
              {{ h.score || '—' }}
            </div>
            <div>
              <div class="text-sm text-text font-medium group-hover:text-accent transition">{{ h.title }}</div>
              <div class="text-xs text-text-muted mt-0.5">{{ h.date }} · {{ h.duration }}</div>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-xs font-medium px-2.5 py-1 rounded-lg"
              :class="h.status === '已完成' ? 'bg-success-soft text-success' : 'bg-warning-soft text-warning'">
              {{ h.status }}
            </span>
            <svg class="w-4 h-4 text-text-muted opacity-0 group-hover:opacity-100 transition -translate-x-1 group-hover:translate-x-0"
              viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const resumes = ref([])
const categories = ref([])
const selectedResumeId = ref(null)
const selectedCats = ref([])
const dropOpen = ref(false)
const dropdownRef = ref(null)

const resumeOptions = computed(() => [
  { value: null, label: '不使用简历' },
  ...resumes.value.map(r => ({ value: r.id, label: r.filename }))
])
const selectedResumeLabel = computed(() =>
  resumeOptions.value.find(o => o.value === selectedResumeId.value)?.label || '不使用简历'
)

function onClickOutside(e) {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) dropOpen.value = false
}
onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))

const canStart = computed(() => selectedResumeId.value || selectedCats.value.length > 0)

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了，还在练习'
  if (h < 12) return '早上好'
  if (h < 18) return '下午好'
  return '晚上好'
})

function toggleCat(c) {
  const i = selectedCats.value.indexOf(c)
  i === -1 ? selectedCats.value.push(c) : selectedCats.value.splice(i, 1)
}

const suggestions = ref([])

// 选择分类后自动拉取长期记忆建议
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
  { label: '总面试次数', value: '—', sub: '', color: 'text-success', icon: 'M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4-4v2', iconBg: 'bg-accent-soft', iconColor: 'text-accent' },
  { label: '平均得分', value: '—', sub: '', color: 'text-success', icon: 'M13 17l5-5-5-5M6 17l5-5-5-5', iconBg: 'bg-success-soft', iconColor: 'text-success' },
  { label: '题库覆盖', value: '—', sub: '分类', color: 'text-accent', icon: 'M4 19.5A2.5 2.5 0 016.5 17H20', iconBg: 'bg-warning-soft', iconColor: 'text-warning' },
])

const tips = [
  { title: 'STAR 法则', desc: '用情境、任务、行动、结果的结构回答行为面试题' },
  { title: '技术深度', desc: '不只说"会用"，要能解释原理和取舍' },
  { title: '主动提问', desc: '面试结尾准备 2-3 个有深度的问题' },
]

const history = ref([])

function formatInterview(item) {
  const date = item.started_at ? new Date(item.started_at).toLocaleDateString('zh-CN') : '—'
  let duration = '—'
  if (item.started_at && item.ended_at) {
    const mins = Math.round((new Date(item.ended_at) - new Date(item.started_at)) / 60000)
    duration = `${mins} 分钟`
  }
  const cats = item.qb_categories || []
  return {
    id: item.id,
    title: cats.length ? cats.join(' + ') + ' 模拟面试' : '模拟面试',
    date, duration,
    score: item.overall_score || 0,
    status: item.status === 'completed' ? '已完成' : '未完成',
  }
}

onMounted(async () => {
  try {
    const [resumeRes, catRes, statsRes, historyRes] = await Promise.all([
      fetch('/api/resume/list'),
      fetch('/api/qb/categories'),
      fetch('/api/interview/stats'),
      fetch('/api/interview/list'),
    ])
    resumes.value = await resumeRes.json()
    categories.value = await catRes.json()
    const s = await statsRes.json()
    stats.value[0].value = String(s.total_count)
    stats.value[1].value = String(s.avg_score)
    stats.value[2].value = s.category_coverage
    history.value = (await historyRes.json()).slice(0, 4).map(formatInterview)
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
.drop-enter-active, .drop-leave-active { transition: all 0.15s ease; }
.drop-enter-from, .drop-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
