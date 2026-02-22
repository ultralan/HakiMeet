<template>
  <div class="h-screen flex flex-col bg-bg">
    <!-- Top bar -->
    <header class="flex items-center justify-between px-5 py-3 border-b border-border bg-surface/80 backdrop-blur-sm">
      <div class="flex items-center gap-3">
        <button @click="handleExit" class="text-text-muted hover:text-text text-xs transition">&larr; 退出</button>
        <div class="w-px h-4 bg-border"></div>
        <span class="text-[13px] text-text">AI 模拟面试</span>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-xs px-2.5 py-1 rounded-md"
          :class="{
            'bg-success-soft text-success': store.status === 'active',
            'bg-warning-soft text-warning': store.status === 'connecting' || store.status === 'initializing',
            'bg-bg text-text-muted border border-border': store.status === 'idle',
            'bg-danger-soft text-danger': store.status === 'ended',
          }">
          {{ statusLabel }}
        </span>
        <span v-if="store.status === 'active'" class="text-xs text-text-muted font-mono">{{ elapsed }}</span>
      </div>
    </header>

    <!-- Idle / Connecting -->
    <div v-if="store.status === 'idle' || store.status === 'connecting'"
      class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="w-16 h-16 rounded-xl bg-accent-soft flex items-center justify-center mx-auto mb-5">
          <svg class="w-7 h-7 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/>
            <path d="M19 10v2a7 7 0 01-14 0v-2"/>
            <line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/>
          </svg>
        </div>
        <h2 class="text-base font-medium text-text mb-1.5">准备好了吗？</h2>
        <p class="text-[13px] text-text-secondary mb-6 max-w-xs">面试将通过语音进行，请确保麦克风和摄像头可用</p>
        <button @click="startInterview" :disabled="store.status === 'connecting'"
          class="px-6 py-2.5 rounded-lg text-[13px] font-medium bg-accent text-white hover:bg-accent-hover transition disabled:opacity-50">
          {{ store.status === 'connecting' ? '正在连接...' : '开始面试' }}
        </button>
      </div>
    </div>

    <!-- Active / Initializing interview -->
    <template v-else-if="store.status === 'initializing' || store.status === 'active' || store.status === 'ended'">
      <div class="flex-1 flex overflow-hidden relative">
        <!-- Initializing overlay -->
        <div v-if="store.status === 'initializing'"
          class="absolute inset-0 z-20 bg-bg/80 backdrop-blur-sm flex items-center justify-center">
          <div class="text-center">
            <div class="w-10 h-10 border-2 border-accent border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p class="text-sm text-text">正在准备面试环境...</p>
            <p class="text-xs text-text-muted mt-1">加载题库与语音引擎</p>
          </div>
        </div>

        <!-- Left panel: Avatar -->
        <div class="flex-1 relative bg-[#f0f1f6]">
          <!-- 已完成面试：评分详情 -->
          <div v-if="report" class="absolute inset-0 overflow-y-auto p-6 space-y-5">
            <div class="text-center mb-2">
              <div class="text-xs text-text-muted mb-1">总体评分</div>
              <div class="text-4xl font-bold" :class="reportScoreClass">{{ report.overall_score || '—' }}</div>
            </div>
            <div v-if="report.dimensions?.length" class="grid grid-cols-2 gap-3">
              <div v-for="d in report.dimensions" :key="d.name" class="rounded-xl bg-bg p-3.5">
                <div class="text-xs text-text-muted font-medium mb-1">{{ d.name }}</div>
                <div class="text-lg font-bold text-text">{{ d.score }}</div>
                <div class="w-full h-1.5 bg-border/60 rounded-full mt-2">
                  <div class="h-1.5 rounded-full bg-accent" :style="{ width: d.score + '%' }"></div>
                </div>
              </div>
            </div>
            <div v-if="report.summary" class="rounded-xl bg-bg p-4">
              <div class="text-xs text-text-muted font-medium mb-2">AI 总结</div>
              <p class="text-[13px] text-text-secondary leading-relaxed whitespace-pre-wrap">{{ report.summary }}</p>
            </div>
          </div>

          <!-- 进行中：3D 数字人 -->
          <template v-else>
            <AvatarCanvas :speaking="store.aiSpeaking" class="absolute inset-0" />
            <div v-if="store.aiSpeaking"
              class="absolute bottom-4 left-4 flex items-center gap-2 px-3 py-1.5 rounded-lg bg-bg/80 backdrop-blur-sm z-10">
              <span class="flex gap-0.5">
                <span v-for="i in 3" :key="i" class="w-1 bg-accent rounded-full animate-bounce"
                  :style="{ height: '12px', animationDelay: i * 0.15 + 's' }"></span>
              </span>
              <span class="text-xs text-text-secondary">面试官正在说话</span>
            </div>
            <!-- PiP 摄像头（聊天展开时） -->
            <div v-show="chatOpen" class="absolute bottom-4 right-4 w-44 aspect-video rounded-xl overflow-hidden shadow-lg border-2 border-bg/50 z-10 bg-bg">
              <video ref="pipEl" autoplay muted playsinline class="h-full w-full object-cover scale-x-[-1]"></video>
              <span v-if="!cam.active.value" class="absolute inset-0 flex items-center justify-center text-[11px] text-text-muted">摄像头未开启</span>
            </div>
          </template>
        </div>

        <!-- Chat toggle button -->
        <button @click="chatOpen = !chatOpen"
          class="absolute top-1/2 -translate-y-1/2 right-1/2 z-[5] w-6 h-12 flex items-center justify-center bg-surface border border-border rounded-l-lg hover:bg-surface-hover transition">
          <svg class="w-3.5 h-3.5 text-text-muted transition-transform" :class="chatOpen || 'rotate-180'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
        </button>

        <!-- Right panel: chat or camera -->
        <div class="w-1/2 flex flex-col shrink-0 border-l border-border">
          <!-- 摄像头（聊天收起时显示） -->
          <div v-show="!chatOpen" class="flex-1 relative bg-bg">
            <video ref="videoEl" autoplay muted playsinline class="h-full w-full object-cover scale-x-[-1]"></video>
            <span v-if="!cam.active.value" class="absolute inset-0 flex items-center justify-center text-[11px] text-text-muted">摄像头未开启</span>
          </div>
          <!-- 聊天记录（聊天展开时显示） -->
          <div v-show="chatOpen" ref="chatPanel" class="flex-1 overflow-y-auto p-5 space-y-4">
            <!-- 默认问候 -->
            <div class="flex justify-start">
              <div class="max-w-[80%]">
                <div class="text-[10px] text-text-muted mb-1">面试官</div>
                <div class="px-3.5 py-2 rounded-xl text-[13px] leading-relaxed bg-surface border border-border text-text rounded-bl-sm">
                  你好，我是今天的面试官。请先做一个简单的自我介绍吧。
                </div>
              </div>
            </div>
            <div v-for="(msg, i) in store.messages" :key="i"
              :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']">
              <div v-if="msg.role === 'system'" class="w-full text-center">
                <div class="inline-block px-4 py-2 rounded-lg bg-warning-soft text-warning text-xs">{{ msg.text }}</div>
              </div>
              <div v-else class="max-w-[80%]">
                <div class="text-[10px] text-text-muted mb-1" :class="msg.role === 'user' ? 'text-right' : ''">
                  {{ msg.role === 'ai' ? '面试官' : '你' }}
                </div>
                <div class="px-3.5 py-2 rounded-xl text-[13px] leading-relaxed"
                  :class="msg.role === 'user'
                    ? 'bg-accent text-white rounded-br-sm'
                    : 'bg-surface border border-border text-text rounded-bl-sm'">
                  {{ msg.text }}
                </div>
              </div>
            </div>
          </div>

          <!-- Controls -->
          <div v-if="store.status === 'active' || ending"
            class="border-t border-border px-5 py-4 flex items-center gap-3">
            <button @click="togglePause" :disabled="ending"
              class="flex-1 py-2.5 rounded-lg text-[13px] font-medium transition flex items-center justify-center gap-2"
              :class="paused
                ? 'bg-accent text-white'
                : 'bg-surface border border-border text-text hover:bg-surface-hover'">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path v-if="paused" d="M5 3l14 9-14 9V3z"/>
                <template v-else><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></template>
              </svg>
              {{ paused ? '继续' : '暂停' }}
            </button>
            <button @click="handleEnd" :disabled="ending"
              class="px-4 py-2.5 rounded-lg text-[13px] transition"
              :class="ending ? 'bg-warning-soft text-warning' : 'bg-danger-soft text-danger hover:bg-danger hover:text-white'">
              {{ ending ? 'AI 评分中...' : '结束' }}
            </button>
          </div>

          <!-- Ended: back button -->
          <div v-if="store.status === 'ended'"
            class="border-t border-border px-5 py-4 flex justify-center">
            <router-link to="/"
              class="px-6 py-2.5 rounded-lg text-[13px] font-medium bg-accent text-white hover:bg-accent-hover transition no-underline">
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
      report.value = data.report
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
  idle: '等待开始', connecting: '连接中', initializing: '初始化中', active: '进行中', ended: '已结束'
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
  else if (s === 'ended' || s === 'idle') { cam.stop(); recorder.stop() }

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
