<template>
  <div class="h-screen flex flex-col bg-bg">
    <!-- Top bar -->
    <header class="flex items-center justify-between px-6 py-4 border-b border-border glass relative">
      <!-- 背景装饰 -->
      <div class="absolute inset-0 bg-gradient-to-r from-accent-softer via-transparent to-accent-softer opacity-50"></div>

      <div class="flex items-center gap-4 relative">
        <button @click="handleExit" class="flex items-center gap-2 text-text-secondary hover:text-text text-sm font-semibold transition-all duration-200 hover:translate-x-[-2px] group">
          <ArrowLeft :size="16" class="transition-transform group-hover:translate-x-[-2px]" />
          退出
        </button>
        <div class="w-px h-5 bg-border"></div>
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-accent to-accent-hover flex items-center justify-center shadow-sm">
            <svg class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
            </svg>
          </div>
          <span class="text-sm font-bold text-text">AI 模拟面试</span>
        </div>
      </div>
      <div class="flex items-center gap-4 relative">
        <span class="text-xs font-bold px-3 py-1.5 rounded-lg shadow-sm"
          :class="{
            'bg-gradient-to-r from-success to-success/80 text-white': store.status === 'active',
            'bg-gradient-to-r from-warning to-warning/80 text-white': store.status === 'connecting' || store.status === 'initializing',
            'bg-surface border border-border-light text-text-muted': store.status === 'idle',
            'bg-gradient-to-r from-danger to-danger/80 text-white': store.status === 'ended',
          }">
          {{ statusLabel }}
        </span>
        <span v-if="store.status === 'active'" class="text-sm text-text font-mono font-semibold px-3 py-1.5 rounded-lg bg-surface border border-border-light shadow-sm">{{ elapsed }}</span>
      </div>
    </header>

    <!-- Idle / Connecting -->
    <div v-if="store.status === 'idle' || store.status === 'connecting'"
      class="flex-1 flex items-center justify-center relative overflow-hidden">
      <!-- 背景装饰 -->
      <div class="absolute inset-0 bg-gradient-to-br from-accent-softer via-transparent to-info-soft opacity-50"></div>
      <div class="absolute top-1/4 left-1/4 w-64 h-64 bg-accent-soft rounded-full blur-3xl opacity-30 animate-pulse"></div>
      <div class="absolute bottom-1/4 right-1/4 w-64 h-64 bg-info-soft rounded-full blur-3xl opacity-30 animate-pulse" style="animation-delay: 1s;"></div>

      <div class="text-center relative z-10">
        <div class="w-20 h-20 rounded-2xl bg-gradient-to-br from-accent to-accent-hover flex items-center justify-center mx-auto mb-6 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
          <Mic :size="36" class="text-white" />
        </div>
        <h2 class="text-xl font-bold text-text mb-2">准备好了吗？</h2>
        <p class="text-sm text-text-secondary mb-8 max-w-sm font-medium">面试将通过语音进行，请确保麦克风和摄像头可用</p>
        <a-button @click="startInterview" :disabled="store.status === 'connecting'"
          type="primary" size="large" class="btn-press">
          {{ store.status === 'connecting' ? '正在连接...' : '开始面试' }}
        </a-button>
      </div>
    </div>

    <!-- Active / Initializing / Error interview -->
    <template v-else-if="['initializing', 'active', 'ended', 'error'].includes(store.status)">
      <div class="flex-1 flex overflow-hidden relative">
        <!-- Initializing overlay -->
        <div v-if="store.status === 'initializing'"
          class="absolute inset-0 z-20 glass-dark flex items-center justify-center">
          <div class="text-center">
            <div class="w-16 h-16 border-4 border-accent border-t-transparent rounded-full animate-spin mx-auto mb-5 shadow-lg"></div>
            <p class="text-base font-bold text-white mb-2">正在准备面试环境...</p>
            <p class="text-sm text-white/70 font-medium">加载题库与语音引擎</p>
          </div>
        </div>

        <!-- Left panel: Avatar -->
        <div class="flex-1 relative bg-gradient-to-br from-bg-secondary to-bg">
          <!-- 已完成面试：评分详情 -->
          <div v-if="report" class="absolute inset-0 overflow-y-auto p-8 space-y-6">
            <div class="text-center mb-4">
              <div class="text-xs text-text-muted font-semibold uppercase tracking-wider mb-3">总体评分</div>
              <div class="inline-flex items-center justify-center w-32 h-32 rounded-2xl shadow-lg mb-4"
                :class="reportScoreClass.includes('success') ? 'bg-gradient-to-br from-success to-success/80' : reportScoreClass.includes('warning') ? 'bg-gradient-to-br from-warning to-warning/80' : reportScoreClass.includes('danger') ? 'bg-gradient-to-br from-danger to-danger/80' : 'bg-surface border border-border-light'">
                <div class="text-5xl font-bold text-white">{{ report.overall_score || '—' }}</div>
              </div>
            </div>
            <div v-if="report.dimensions?.length" class="grid grid-cols-2 gap-4">
              <div v-for="d in report.dimensions" :key="d.name" class="rounded-xl bg-surface border border-border-light p-5 hover:shadow-md transition-all duration-200">
                <div class="text-xs text-text-muted font-bold uppercase tracking-wider mb-2">{{ d.name }}</div>
                <div class="text-2xl font-bold text-text mb-3">{{ d.score }}</div>
                <div class="w-full h-2 bg-bg rounded-full overflow-hidden">
                  <div class="h-2 rounded-full bg-gradient-to-r from-accent to-accent-light transition-all duration-500" :style="{ width: d.score + '%' }"></div>
                </div>
              </div>
            </div>
            <div v-if="report.summary" class="rounded-xl bg-surface border border-border-light p-6 shadow-sm">
              <div class="text-xs text-text-muted font-bold uppercase tracking-wider mb-3">AI 总结</div>
              <p class="text-sm text-text-secondary leading-relaxed whitespace-pre-wrap">{{ report.summary }}</p>
            </div>
          </div>

          <!-- 进行中：3D 数字人 -->
          <template v-else>
            <AvatarCanvas :speaking="store.aiSpeaking" class="absolute inset-0" />
            <div v-if="store.aiSpeaking"
              class="absolute bottom-6 left-6 flex items-center gap-3 px-4 py-2.5 rounded-xl glass shadow-lg z-10 border border-white/20">
              <span class="flex gap-1">
                <span v-for="i in 3" :key="i" class="w-1.5 bg-accent rounded-full animate-bounce shadow-sm"
                  :style="{ height: '14px', animationDelay: i * 0.15 + 's' }"></span>
              </span>
              <span class="text-xs text-text font-semibold">面试官正在说话</span>
            </div>
            <!-- PiP 摄像头（聊天展开时） -->
            <div v-show="chatOpen" class="absolute bottom-6 right-6 w-48 aspect-video rounded-xl overflow-hidden shadow-xl border-2 border-white/30 z-10 bg-surface">
              <video ref="pipEl" autoplay muted playsinline class="h-full w-full object-cover scale-x-[-1]"></video>
              <span v-if="!cam.active.value" class="absolute inset-0 flex items-center justify-center text-xs text-text-muted font-medium bg-bg">摄像头未开启</span>
            </div>
          </template>
        </div>

        <!-- Chat toggle button -->
        <button @click="chatOpen = !chatOpen"
          class="absolute top-1/2 -translate-y-1/2 right-1/2 z-[5] w-8 h-16 flex items-center justify-center bg-surface border-2 border-border-light rounded-l-xl hover:bg-surface-hover transition-all duration-200 shadow-md hover:shadow-lg hover:w-10 group">
          <ChevronRight :size="16" class="text-text-muted transition-all duration-200 group-hover:text-accent" :class="chatOpen || 'rotate-180'" />
        </button>

        <!-- Right panel: chat or camera -->
        <div class="w-1/2 flex flex-col shrink-0 border-l border-border">
          <!-- 摄像头（聊天收起时显示） -->
          <div v-show="!chatOpen" class="flex-1 relative bg-bg">
            <video ref="videoEl" autoplay muted playsinline class="h-full w-full object-cover scale-x-[-1]"></video>
            <span v-if="!cam.active.value" class="absolute inset-0 flex items-center justify-center text-[11px] text-text-muted">摄像头未开启</span>
          </div>
          <!-- 聊天记录（聊天展开时显示） -->
          <div v-show="chatOpen" ref="chatPanel" class="flex-1 overflow-y-auto p-6 space-y-5">
            <!-- 默认问候 -->
            <div class="flex justify-start">
              <div class="max-w-[75%]">
                <div class="text-[11px] text-text-muted font-semibold mb-2">面试官</div>
                <div class="px-4 py-3 rounded-2xl text-sm leading-relaxed bg-surface border border-border-light text-text rounded-bl-md shadow-sm">
                  你好，我是今天的面试官。请先做一个简单的自我介绍吧。
                </div>
              </div>
            </div>
            <div v-for="(msg, i) in store.messages" :key="i"
              :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']">
              <div v-if="msg.role === 'system'" class="w-full text-center">
                <div class="inline-block px-5 py-2.5 rounded-xl bg-warning-soft text-warning text-xs font-semibold border border-warning/20">{{ msg.text }}</div>
              </div>
              <div v-else class="max-w-[75%]">
                <div class="text-[11px] text-text-muted font-semibold mb-2" :class="msg.role === 'user' ? 'text-right' : ''">
                  {{ msg.role === 'ai' ? '面试官' : '你' }}
                </div>
                <div class="px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm"
                  :class="msg.role === 'user'
                    ? 'bg-gradient-to-br from-accent to-accent-hover text-white rounded-br-md'
                    : 'bg-surface border border-border-light text-text rounded-bl-md'">
                  {{ msg.text }}
                </div>
              </div>
            </div>
          </div>

          <!-- Controls -->
          <div v-if="store.status === 'active' || ending"
            class="border-t border-border-light px-6 py-5 flex items-center gap-4 bg-surface">
            <a-button @click="togglePause" :disabled="ending" long size="large"
              :type="paused ? 'primary' : 'outline'" class="btn-press">
              <template #icon>
                <Play v-if="paused" :size="20" />
                <Pause v-else :size="20" />
              </template>
              {{ paused ? '继续' : '暂停' }}
            </a-button>
            <a-button @click="handleEnd" :disabled="ending" size="large"
              :status="ending ? 'warning' : 'danger'" class="btn-press">
              {{ ending ? 'AI 评分中...' : '结束' }}
            </a-button>
          </div>

          <!-- Ended / Error: back button -->
          <div v-if="store.status === 'ended' || store.status === 'error'"
            class="border-t border-border-light px-6 py-5 flex justify-center bg-surface">
            <router-link to="/"
              class="px-8 py-3 rounded-xl text-sm font-bold bg-gradient-to-r from-accent to-accent-hover text-white hover:shadow-lg transition-all duration-200 no-underline btn-press shadow-md">
              返回首页
            </router-link>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useInterviewStore } from '../stores/interview'
import { useAudioRecorder } from '../composables/useAudioRecorder'
import { useAudioPlayer } from '../composables/useAudioPlayer'
import { useCamera } from '../composables/useCamera'
import { useConfirm } from '../composables/useConfirm'
import AvatarCanvas from '../components/AvatarCanvas.vue'
import { Mic, Play, Pause, ArrowLeft, MessageSquare, ChevronRight } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const store = useInterviewStore()
const chatPanel = ref(null)
const videoEl = ref(null)
const pipEl = ref(null)
const ending = ref(false)
const report = ref(null)

// 进入页面时检查面试是否已完成
onMounted(async () => {
  try {
    const res = await fetch(`/api/interview/${route.params.id}`)
    if (!res.ok) return
    const data = await res.json()
    if (data.status === 'completed' && data.report) {
      report.value = { ...data.report, overall_score: data.overall_score }
      // 从对话轮次还原聊天记录
      for (const t of data.turns || []) {
        if (t.ai_question) store.messages.push({ role: 'ai', text: t.ai_question })
        if (t.user_answer) store.messages.push({ role: 'user', text: t.user_answer })
      }
      store.messages.push({ role: 'system', text: data.report.summary || '面试已结束' })
      store.status = 'ended'
    }
  } catch (e) { /* 网络错误则正常显示idle */ }
})

const { confirm: ask } = useConfirm()

const player = useAudioPlayer()
const recorder = useAudioRecorder((buffer) => store.sendAudio(buffer))
const cam = useCamera(videoEl)

// 同步摄像头流到 PiP
watch(() => cam.active.value, (v) => {
  if (v && pipEl.value && videoEl.value) pipEl.value.srcObject = videoEl.value.srcObject
})

const statusLabel = computed(() => ({
  idle: '等待开始', connecting: '连接中', initializing: '初始化中', active: '进行中', ended: '已结束', error: '服务异常'
}[store.status]))

const reportScoreClass = computed(() => {
  const s = report.value?.overall_score
  if (!s) return 'text-text-muted'
  if (s >= 80) return 'text-success'
  if (s >= 60) return 'text-warning'
  return 'text-danger'
})

// Timer
const startTime = ref(null)
const elapsed = ref('00:00')
let timer = null

// 统一 status watcher
watch(() => store.status, async (s, old) => {
  // 计时器
  if (s === 'active' && old !== 'active') {
    startTime.value = Date.now()
    timer = setInterval(() => {
      const d = Math.floor((Date.now() - startTime.value) / 1000)
      elapsed.value = `${String(Math.floor(d / 60)).padStart(2, '0')}:${String(d % 60).padStart(2, '0')}`
    }, 1000)
  } else if (s !== 'active' && timer) { clearInterval(timer); timer = null }

  // 摄像头 & 录音
  if (s === 'initializing') { await nextTick(); cam.start() }
  else if (s === 'active' && old === 'initializing') { recorder.start() }
  else if (['ended', 'idle', 'error'].includes(s)) { cam.stop(); recorder.stop() }

  // ending 标记
  if (s === 'ended') ending.value = false
})

watch(() => player.playing.value, (v) => { store.aiSpeaking = v })

function startInterview() {
  store.reset()
  store.setAudioPlayer(player)
  store.connect(route.params.id)
}

const paused = ref(false)
const chatOpen = ref(true)
function togglePause() {
  paused.value = !paused.value
  paused.value ? recorder.stop() : recorder.start()
}

async function handleExit() {
  if (store.status === 'active' || store.status === 'initializing') {
    if (!await ask('面试进行中，退出将丢失本次面试记录，确定退出吗？', true)) return
  }
  store.reset()
  router.push('/')
}

async function handleEnd() {
  if (!await ask('确定结束面试并进入 AI 评分吗？')) return
  ending.value = true
  store.endInterview()
}

onUnmounted(() => {
  if (timer) clearInterval(timer)
  cam.stop()
  recorder.stop()
  store.reset()
})

watch(() => store.messages.length, async () => {
  await nextTick()
  if (chatPanel.value) chatPanel.value.scrollTop = chatPanel.value.scrollHeight
})
</script>
