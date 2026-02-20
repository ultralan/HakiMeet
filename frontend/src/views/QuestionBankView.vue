<template>
  <div class="qb-page">
    <h2>题库管理</h2>
    <div class="upload">
      <input type="file" accept=".pdf,.md" @change="onFile" />
      <select v-model="category">
        <option v-for="c in presetCats" :key="c" :value="c">{{ c }}</option>
        <option value="__custom">自定义...</option>
      </select>
      <input v-if="category === '__custom'" v-model="customCat" placeholder="输入分类名" />
      <button @click="upload" :disabled="!file || (!finalCategory)">上传</button>
    </div>

    <div v-for="cat in groupedCats" :key="cat" class="cat-group">
      <h3>{{ cat }}</h3>
      <ul>
        <li v-for="qb in grouped[cat]" :key="qb.id">
          {{ qb.filename }}
          <span v-if="qb.vectorized">✓</span>
          <button class="btn-sm" @click="toggleChunks(qb)">{{ qb._showChunks ? '收起' : '查看文本块' }}</button>
          <button class="btn-del" @click="remove(qb.id)">删除</button>
          <div v-if="qb._showChunks && qb._chunks" class="chunks">
            <div v-for="(c, i) in qb._chunks" :key="i" class="chunk">{{ c.content }}</div>
          </div>
        </li>
      </ul>
    </div>

    <router-link to="/">← 返回首页</router-link>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const API = 'http://localhost:8000/api/qb'
const list = ref([])
const file = ref(null)
const category = ref('')
const customCat = ref('')
const presetCats = ref([])

const finalCategory = computed(() => category.value === '__custom' ? customCat.value : category.value)

const grouped = computed(() => {
  const g = {}
  for (const qb of list.value) {
    ;(g[qb.category] ||= []).push(qb)
  }
  return g
})
const groupedCats = computed(() => Object.keys(grouped.value))

const onFile = (e) => { file.value = e.target.files[0] }

async function upload() {
  const form = new FormData()
  form.append('file', file.value)
  form.append('category', finalCategory.value)
  await fetch(`${API}/upload`, { method: 'POST', body: form })
  file.value = null
  await load()
}

async function load() {
  const [listRes, catRes] = await Promise.all([
    fetch(`${API}/list`), fetch(`${API}/categories`)
  ])
  list.value = (await listRes.json()).map(q => ({ ...q, _showChunks: false, _chunks: null }))
  presetCats.value = await catRes.json()
  if (!category.value && presetCats.value.length) category.value = presetCats.value[0]
}

async function toggleChunks(qb) {
  if (qb._showChunks) { qb._showChunks = false; return }
  if (!qb._chunks) {
    const res = await fetch(`${API}/${qb.id}/chunks`)
    qb._chunks = await res.json()
  }
  qb._showChunks = true
}

async function remove(id) {
  await fetch(`${API}/${id}`, { method: 'DELETE' })
  await load()
}

onMounted(load)
</script>

<style scoped>
.qb-page { padding: 40px; max-width: 700px; margin: 0 auto; }
.upload { display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }
.cat-group { margin-bottom: 24px; }
h3 { border-bottom: 1px solid #e5e7eb; padding-bottom: 4px; }
ul { list-style: none; padding: 0; }
li { padding: 8px 0; border-bottom: 1px solid #f3f4f6; display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
.btn-sm { background: #6366f1; color: white; border: none; border-radius: 4px; padding: 2px 10px; cursor: pointer; font-size: 12px; }
.btn-del { background: #ef4444; color: white; border: none; border-radius: 4px; padding: 2px 10px; cursor: pointer; font-size: 12px; }
.chunks { width: 100%; margin-top: 8px; }
.chunk { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 4px; padding: 8px; margin-bottom: 4px; font-size: 13px; white-space: pre-wrap; }
</style>
