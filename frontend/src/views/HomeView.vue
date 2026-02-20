<template>
  <div class="home">
    <h1>HakiMeet AI 面试官</h1>
    <div class="resume-select" v-if="resumes.length">
      <label>选择简历：</label>
      <select v-model="selectedResumeId">
        <option v-for="r in resumes" :key="r.id" :value="r.id">{{ r.filename }}</option>
      </select>
    </div>
    <p v-else class="hint">请先<router-link to="/resume">上传简历</router-link></p>
    <div class="actions">
      <button @click="startInterview" :disabled="!selectedResumeId">开始面试</button>
      <router-link to="/resume">管理简历</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const resumes = ref([])
const selectedResumeId = ref(null)

onMounted(async () => {
  const res = await fetch('http://localhost:8000/api/resume/list')
  resumes.value = await res.json()
  if (resumes.value.length) selectedResumeId.value = resumes.value[0].id
})

async function startInterview() {
  const res = await fetch('http://localhost:8000/api/interview/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume_id: selectedResumeId.value, job_id: 'demo' }),
  })
  const data = await res.json()
  router.push(`/interview/${data.id}`)
}
</script>

<style scoped>
.home { text-align: center; padding: 60px 20px; }
.actions { display: flex; gap: 16px; justify-content: center; margin-top: 24px; }
button, a { padding: 12px 24px; border-radius: 8px; font-size: 16px; cursor: pointer; text-decoration: none; }
button { background: #4f46e5; color: white; border: none; }
a { background: #f3f4f6; color: #333; }
</style>
