<template>
  <div class="p-10">
    <div class="mb-8 page-enter">
      <h1 class="text-lg font-semibold text-text">题库管理</h1>
      <p class="text-text-secondary text-sm mt-1">上传面试题库，支持按分类组织</p>
    </div>

    <!-- Upload area -->
    <div class="card rounded-2xl p-5 mb-8 page-enter stagger-1 relative z-10">
      <div class="flex items-end gap-3 flex-wrap">
        <label class="flex-1 min-w-[200px]">
          <span class="text-xs text-text-muted font-medium block mb-1.5">选择文件</span>
          <label class="flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-bg border border-border cursor-pointer hover:border-accent/30 transition">
            <svg class="w-4 h-4 text-text-muted" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            <span class="text-sm" :class="file ? 'text-text' : 'text-text-muted'">{{ file ? file.name : '选择 PDF 或 MD 文件' }}</span>
            <input type="file" accept=".pdf,.md" @change="onFile" class="hidden" />
          </label>
        </label>

        <div class="min-w-[160px] relative" ref="catDropRef">
          <span class="text-xs text-text-muted font-medium block mb-1.5">分类</span>
          <button @click="catDropOpen = !catDropOpen" type="button"
            class="w-full bg-bg border border-border rounded-xl px-3.5 py-2.5 text-sm text-left outline-none transition flex items-center justify-between"
            :class="catDropOpen ? 'border-accent ring-2 ring-accent-soft' : 'hover:border-border-light'">
            <span :class="category ? 'text-text' : 'text-text-muted'">{{ category === '__custom' ? '自定义...' : (category || '选择分类') }}</span>
            <svg class="w-4 h-4 text-text-muted shrink-0 transition-transform" :class="catDropOpen && 'rotate-180'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
          </button>
          <Transition name="drop">
            <div v-if="catDropOpen"
              class="absolute z-10 mt-1.5 w-full bg-surface border border-border rounded-xl shadow-md overflow-hidden py-1">
              <div v-for="c in presetCats" :key="c"
                @click="category = c; catDropOpen = false"
                class="px-3.5 py-2 text-sm cursor-pointer transition"
                :class="category === c ? 'bg-accent-soft text-accent font-medium' : 'text-text hover:bg-surface-hover'">
                {{ c }}
              </div>
              <div @click="category = '__custom'; catDropOpen = false"
                class="px-3.5 py-2 text-sm cursor-pointer transition border-t border-border/60"
                :class="category === '__custom' ? 'bg-accent-soft text-accent font-medium' : 'text-text-muted hover:bg-surface-hover'">
                自定义...
              </div>
            </div>
          </Transition>
        </div>

        <input v-if="category === '__custom'" v-model="customCat" placeholder="输入分类名"
          class="px-3.5 py-2.5 rounded-xl bg-bg border border-border text-sm text-text outline-none focus:border-accent focus:ring-2 focus:ring-accent-soft transition min-w-[140px]" />

        <button @click="upload" :disabled="!file || !finalCategory || up.uploading.value"
          class="px-5 py-2.5 rounded-xl text-sm font-semibold bg-accent text-white hover:bg-accent-hover shadow-sm hover:shadow-md transition btn-press disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none">
          {{ up.uploading.value ? '上传中...' : '上传' }}
        </button>

        <button @click="downloadTemplate"
          class="px-4 py-2.5 rounded-xl text-sm text-text-secondary border border-border hover:border-accent/30 hover:text-accent transition btn-press">
          下载模板
        </button>
      </div>

      <!-- Upload progress -->
      <div v-if="up.uploading.value" class="mt-4">
        <div class="flex items-center justify-between mb-1.5">
          <span class="text-xs text-text-secondary">
            {{ up.phase.value === 'processing' ? '服务器处理中，正在向量化...' : '上传中...' }}
          </span>
          <span class="text-xs font-semibold text-accent">{{ up.progress.value }}%</span>
        </div>
        <div class="w-full h-1.5 bg-bg rounded-full overflow-hidden">
          <div class="h-full rounded-full transition-all duration-300"
            :class="up.phase.value === 'processing' ? 'bg-warning animate-pulse' : 'bg-accent'"
            :style="{ width: up.progress.value + '%' }"></div>
        </div>
      </div>
    </div>

    <!-- Upload tip -->
    <div v-if="uploadTip" class="card rounded-2xl p-4 mb-6 border border-accent/30 bg-accent-soft/30 flex items-center gap-3 page-enter">
      <span class="text-sm text-text">上传完成，建议点击「查看文本块」检查切割结果，确认每道题是否完整。</span>
      <button @click="uploadTip = false" class="text-xs text-text-muted hover:text-text ml-auto">&times;</button>
    </div>

    <!-- Grouped list -->
    <div v-for="(cat, ci) in groupedCats" :key="cat" class="mb-8 page-enter" :class="'stagger-' + Math.min(ci + 2, 4)">
      <div class="flex items-center gap-2 mb-3">
        <div class="w-1.5 h-1.5 rounded-full bg-accent"></div>
        <h2 class="text-sm font-semibold text-text">{{ cat }}</h2>
        <span class="text-xs text-text-muted">({{ grouped[cat].length }})</span>
      </div>

      <div class="card rounded-2xl overflow-hidden divide-y divide-border/60">
        <div v-for="qb in grouped[cat]" :key="qb.id"
          class="hover:bg-surface-hover transition group">
          <div class="flex items-center justify-between px-5 py-4">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl bg-accent-soft flex items-center justify-center">
                <svg class="w-4 h-4 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/>
                </svg>
              </div>
              <span class="text-sm text-text font-medium">{{ qb.filename }}</span>
              <span v-if="qb.vectorized" class="text-xs px-2 py-0.5 rounded-lg bg-success-soft text-success font-medium">已向量化</span>
            </div>
            <div class="flex items-center gap-2">
              <button @click="toggleChunks(qb)"
                class="text-xs text-text-muted hover:text-accent transition px-2.5 py-1 rounded-lg hover:bg-accent-soft btn-press">
                {{ qb._showChunks ? '收起' : '查看文本块' }}
              </button>
              <button @click="remove(qb.id)"
                class="text-text-muted hover:text-danger transition p-1.5 rounded-xl hover:bg-danger-soft opacity-0 group-hover:opacity-100 btn-press">
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Chunks -->
          <div v-if="qb._showChunks && qb._chunks" class="px-5 pb-4 space-y-2">
            <div v-for="(c, i) in qb._chunks" :key="i"
              class="text-xs text-text-secondary bg-bg rounded-xl p-3 leading-relaxed whitespace-pre-wrap">
              {{ c.content }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!groupedCats.length" class="text-center py-20 page-enter stagger-2">
      <div class="w-16 h-16 rounded-2xl bg-bg flex items-center justify-center mx-auto mb-4">
        <svg class="w-7 h-7 text-text-muted" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/>
        </svg>
      </div>
      <div class="text-sm text-text-muted">还没有上传题库</div>
      <div class="text-xs text-text-muted mt-1">上传题库后可在面试中获得针对性提问</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useUpload } from '../composables/useUpload'

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
.drop-enter-active, .drop-leave-active { transition: all 0.15s ease; }
.drop-enter-from, .drop-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
