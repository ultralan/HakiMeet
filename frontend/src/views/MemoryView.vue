<template>
  <div class="p-10">
    <!-- Header -->
    <div class="mb-8 page-enter">
      <h1 class="text-lg font-semibold text-text">长期记忆</h1>
      <p class="text-text-secondary text-sm mt-1">AI 沉淀的技术认知地图。这里记录了您在对话中表现欠佳的知识点，并将在后续面试中持续为您进行针对性磨练。</p>
    </div>

    <!-- Empty state -->
    <div v-if="!loading && Object.keys(grouped).length === 0"
      class="card rounded-2xl p-12 text-center page-enter stagger-1">
      <div class="w-16 h-16 rounded-xl bg-success-soft flex items-center justify-center mx-auto mb-5">
        <svg class="w-7 h-7 text-success" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M9 12l2 2 4-4" /><circle cx="12" cy="12" r="10" />
        </svg>
      </div>
      <h2 class="text-base font-medium text-text mb-1.5">暂无记忆积淀</h2>
      <p class="text-[13px] text-text-secondary max-w-xs mx-auto">完成面试后，AI 将根据您的答题深度自动沉淀记忆点并显示在此。继续保持！</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin"></div>
    </div>

    <!-- Category sections -->
    <div v-for="(items, category) in grouped" :key="category" class="mb-8 page-enter stagger-1">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-8 h-8 rounded-lg bg-accent-soft flex items-center justify-center">
          <span class="text-accent text-[11px] font-bold">{{ category[0] }}</span>
        </div>
        <h2 class="text-sm font-semibold text-text">{{ category }}</h2>
        <span class="text-xs text-text-muted bg-bg px-2 py-0.5 rounded-md">{{ items.length }} 项</span>
      </div>

      <div class="card rounded-2xl overflow-hidden divide-y divide-border/60">
        <div v-for="item in items" :key="item.id"
          class="px-5 py-4 hover:bg-surface-hover transition group"
          :class="item.resolved ? 'opacity-50' : ''">
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1.5">
                <!-- Severity dots -->
                <div class="flex gap-0.5">
                  <span v-for="s in 5" :key="s"
                    class="w-1.5 h-1.5 rounded-full"
                    :class="s <= item.severity
                      ? (item.severity >= 4 ? 'bg-danger' : item.severity >= 3 ? 'bg-warning' : 'bg-accent')
                      : 'bg-border'">
                  </span>
                </div>
                <span v-if="item.resolved"
                  class="text-[10px] px-1.5 py-0.5 rounded bg-success-soft text-success font-medium">已解决</span>
              </div>
              <div class="text-sm text-text font-medium mb-1">{{ item.question_summary }}</div>
              <div class="text-xs text-text-muted leading-relaxed">{{ item.weakness_desc }}</div>
              <div class="text-[11px] text-text-muted mt-1.5">{{ formatDate(item.created_at) }}</div>
            </div>
            <div class="flex items-center gap-1.5 shrink-0 opacity-0 group-hover:opacity-100 transition">
              <button v-if="!item.resolved" @click="resolvePoint(item)"
                class="p-1.5 rounded-lg hover:bg-success-soft text-text-muted hover:text-success transition"
                title="标记已解决">
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 12l2 2 4-4" /><circle cx="12" cy="12" r="10" />
                </svg>
              </button>
              <button @click="deletePoint(item)"
                class="p-1.5 rounded-lg hover:bg-danger-soft text-text-muted hover:text-danger transition"
                title="删除">
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 6h18M8 6V4h8v2m-7 5v6m4-6v6M5 6l1 14h12l1-14" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const grouped = ref({})
const loading = ref(true)

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

async function loadData() {
  loading.value = true
  try {
    const res = await fetch('/api/memory/list')
    grouped.value = await res.json()
  } catch (e) {
    console.warn('加载长期记忆失败', e)
  } finally {
    loading.value = false
  }
}

async function resolvePoint(item) {
  try {
    await fetch(`/api/memory/${item.id}/resolve`, { method: 'PUT' })
    item.resolved = true
  } catch (e) {
    console.warn('标记失败', e)
  }
}

async function deletePoint(item) {
  try {
    await fetch(`/api/memory/${item.id}`, { method: 'DELETE' })
    // 从 grouped 中移除
    for (const cat of Object.keys(grouped.value)) {
      const idx = grouped.value[cat].findIndex(p => p.id === item.id)
      if (idx >= 0) {
        grouped.value[cat].splice(idx, 1)
        if (grouped.value[cat].length === 0) delete grouped.value[cat]
        break
      }
    }
  } catch (e) {
    console.warn('删除失败', e)
  }
}

onMounted(loadData)
</script>
