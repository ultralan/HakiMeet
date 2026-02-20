<template>
  <div class="home">
    <h1>HakiMeet AI 面试官</h1>
    <div class="resume-select">
      <label>选择简历（可选）：</label>
      <select v-model="selectedResumeId">
        <option :value="null">不使用简历</option>
        <option v-for="r in resumes" :key="r.id" :value="r.id">{{ r.filename }}</option>
      </select>
    </div>
    <div class="qb-select" v-if="categories.length">
      <label>选择题库分类：</label>
      <div class="cat-checks">
        <label v-for="c in categories" :key="c">
          <input type="checkbox" :value="c" v-model="selectedCats" /> {{ c }}
        </label>
      </div>
    </div>
    <div class="actions">
      <button @click="startInterview" :disabled="!canStart">开始面试</button>
      <router-link to="/resume">管理简历</router-link>
      <router-link to="/question-bank">管理题库</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const resumes = ref([])
const categories = ref([])
const selectedResumeId = ref(null)
const selectedCats = ref([])

const canStart = computed(() => selectedResumeId.value || selectedCats.value.length > 0)

onMounted(async () => {
  const [resumeRes, catRes] = await Promise.all([
    fetch('http://localhost:8000/api/resume/list'),
    fetch('http://localhost:8000/api/qb/categories'),
  ])
  resumes.value = await resumeRes.json()
  categories.value = await catRes.json()
})

async function startInterview() {
  const res = await fetch('http://localhost:8000/api/interview/create', {
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
}
</script>

<style scoped>
.home { text-align: center; padding: 60px 20px; }
.resume-select, .qb-select { margin: 16px 0; }
.cat-checks { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 8px; }
.cat-checks label { background: #f3f4f6; padding: 4px 12px; border-radius: 6px; cursor: pointer; font-size: 14px; }
.actions { display: flex; gap: 16px; justify-content: center; margin-top: 24px; }
button, a { padding: 12px 24px; border-radius: 8px; font-size: 16px; cursor: pointer; text-decoration: none; }
button { background: #4f46e5; color: white; border: none; }
button:disabled { opacity: 0.5; cursor: not-allowed; }
a { background: #f3f4f6; color: #333; }
</style>
