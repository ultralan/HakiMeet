<template>
  <div class="p-10">
    <div class="mb-8 page-enter">
      <h1 class="text-lg font-semibold text-text">简历管理</h1>
      <p class="text-text-secondary text-sm mt-1">上传简历用于面试时的个性化提问</p>
    </div>

    <!-- Upload area -->
    <label v-if="!up.uploading.value" class="block card rounded-2xl border-2 border-dashed border-border hover:border-accent/40 transition-all cursor-pointer mb-8 group page-enter stagger-1"
      :class="dragging ? 'border-accent bg-accent-soft scale-[1.01]' : ''"
      @dragover.prevent="dragging = true" @dragleave="dragging = false"
      @drop.prevent="dragging = false; onDrop($event)">
      <input type="file" accept=".pdf,.md" @change="onFile" class="hidden" />
      <div class="flex flex-col items-center py-14">
        <div class="w-14 h-14 rounded-2xl bg-accent-soft flex items-center justify-center mb-4 group-hover:scale-110 group-hover:shadow-md transition-all">
          <svg class="w-6 h-6 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
        </div>
        <span class="text-sm text-text-secondary">拖拽文件到此处，或 <span class="text-accent font-semibold">点击上传</span></span>
        <span class="text-xs text-text-muted mt-1.5">支持 PDF、Markdown 格式</span>
        <span class="text-[11px] text-text-muted/60 mt-3 flex items-center gap-1">
          <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
          简历仅存储在本地，不会上传至任何第三方服务器
        </span>
      </div>
    </label>

    <!-- Upload progress -->
    <div v-else class="card rounded-2xl p-6 mb-8 page-enter">
      <div class="flex items-center gap-4 mb-3">
        <div class="w-10 h-10 rounded-xl bg-accent-soft flex items-center justify-center shrink-0">
          <svg class="w-4 h-4 text-accent animate-pulse" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <div class="text-sm text-text font-medium truncate">{{ uploadName }}</div>
          <div class="text-xs text-text-muted mt-0.5">
            {{ up.phase.value === 'processing' ? '服务器处理中，正在提取文本并向量化...' : '上传中...' }}
          </div>
        </div>
        <span class="text-xs font-semibold text-accent">{{ up.progress.value }}%</span>
      </div>
      <div class="w-full h-1.5 bg-bg rounded-full overflow-hidden">
        <div class="h-full rounded-full transition-all duration-300"
          :class="up.phase.value === 'processing' ? 'bg-warning animate-pulse' : 'bg-accent'"
          :style="{ width: up.progress.value + '%' }"></div>
      </div>
    </div>

    <!-- File list -->
    <div v-if="resumes.length" class="card rounded-2xl overflow-hidden divide-y divide-border/60 page-enter stagger-2">
      <div v-for="r in resumes" :key="r.id"
        class="flex items-center justify-between px-5 py-4 hover:bg-surface-hover transition group">
        <div class="flex items-center gap-4">
          <div class="w-10 h-10 rounded-xl bg-accent-soft flex items-center justify-center">
            <svg class="w-4 h-4 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/>
            </svg>
          </div>
          <div>
            <div class="text-sm text-text font-medium">{{ r.filename }}</div>
            <div class="text-xs text-text-muted mt-0.5">{{ r.size || '—' }}</div>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <span v-if="r.vectorized" class="text-xs font-medium px-2.5 py-1 rounded-lg bg-success-soft text-success">已向量化</span>
          <span v-else class="text-xs font-medium px-2.5 py-1 rounded-lg bg-warning-soft text-warning">处理中</span>
          <button @click.prevent="remove(r.id)"
            class="text-text-muted hover:text-danger transition p-2 rounded-xl hover:bg-danger-soft opacity-0 group-hover:opacity-100 btn-press">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>
              <path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <div v-if="!resumes.length" class="text-center py-20 page-enter stagger-2">
      <div class="w-16 h-16 rounded-2xl bg-bg flex items-center justify-center mx-auto mb-4">
        <svg class="w-7 h-7 text-text-muted" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/>
        </svg>
      </div>
      <div class="text-sm text-text-muted">还没有上传简历</div>
      <div class="text-xs text-text-muted mt-1">上传后可在面试中获得个性化提问</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUpload } from '../composables/useUpload'

const API = '/api/resume'
const resumes = ref([])
const file = ref(null)
const dragging = ref(false)
const uploadName = ref('')
const up = useUpload()

function onFile(e) {
  file.value = e.target.files[0]
  if (file.value) upload()
}

function onDrop(e) {
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
