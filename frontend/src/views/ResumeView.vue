<template>
  <div class="resume-page">
    <h2>简历管理</h2>
    <div class="upload">
      <input type="file" accept=".pdf,.md" @change="onFile" />
      <button @click="upload" :disabled="!file">上传</button>
    </div>
    <ul>
      <li v-for="r in resumes" :key="r.id">
        {{ r.filename }} <span v-if="r.vectorized">✓ 已向量化</span>
        <button @click="remove(r.id)">删除</button>
      </li>
    </ul>
    <router-link to="/">← 返回首页</router-link>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const API = 'http://localhost:8000/api/resume'
const resumes = ref([])
const file = ref(null)

const onFile = (e) => { file.value = e.target.files[0] }

async function upload() {
  const form = new FormData()
  form.append('file', file.value)
  await fetch(`${API}/upload`, { method: 'POST', body: form })
  file.value = null
  await load()
}

async function load() {
  const res = await fetch(`${API}/list`)
  resumes.value = await res.json()
}

async function remove(id) {
  await fetch(`${API}/${id}`, { method: 'DELETE' })
  await load()
}

onMounted(load)
</script>

<style scoped>
.resume-page { padding: 40px; max-width: 600px; margin: 0 auto; }
.upload { display: flex; gap: 8px; margin-bottom: 20px; }
ul { list-style: none; padding: 0; }
li { padding: 8px 0; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; }
li button { background: #ef4444; color: white; border: none; border-radius: 4px; padding: 4px 12px; cursor: pointer; }
</style>
