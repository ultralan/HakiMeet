<template>
  <div class="interview">
    <div class="mode-select" v-if="store.status === 'idle' || store.status === 'connecting'">
      <button class="start-btn" @click="startInterview" :disabled="store.status === 'connecting'">
        <span v-if="store.status === 'connecting'" class="loading-text">正在准备面试环境<span class="dots"></span></span>
        <span v-else>开始面试</span>
      </button>
    </div>

    <!-- 视频区域 -->
    <div class="video-area" v-if="store.status === 'active'">
      <div class="avatar-box">
        <AvatarCanvas :speaking="store.aiSpeaking" />
      </div>
      <div class="camera-box">
        <video ref="videoEl" autoplay muted playsinline></video>
        <span v-if="!cam.active.value" class="cam-off">摄像头未开启</span>
      </div>
    </div>

    <!-- 聊天面板 -->
    <div class="chat-panel" ref="chatPanel">
      <div v-for="(msg, i) in store.messages" :key="i" :class="['msg', msg.role]">
        <span class="role">{{ msg.role === 'ai' ? '面试官' : msg.role === 'user' ? '你' : '系统' }}</span>
        <p>{{ msg.text }}</p>
      </div>
    </div>

    <div class="input-bar" v-if="store.status === 'active'">
      <div class="status-indicator">
        <span v-if="store.aiSpeaking" class="status speaking">AI 说话中</span>
        <span v-else-if="recorder.recording.value" class="status recording">录音中</span>
        <span v-else class="status idle">等待中</span>
      </div>
      <button :class="['mic-btn', { recording: recorder.recording.value }]" @click="toggleMic">
        {{ recorder.recording.value ? '停止说话' : '开始说话' }}
      </button>
      <button class="end-btn" @click="store.endInterview()">结束面试</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useInterviewStore } from '../stores/interview'
import { useAudioRecorder } from '../composables/useAudioRecorder'
import { useAudioPlayer } from '../composables/useAudioPlayer'
import { useCamera } from '../composables/useCamera'
import AvatarCanvas from '../components/AvatarCanvas.vue'

const route = useRoute()
const store = useInterviewStore()
const chatPanel = ref(null)
const videoEl = ref(null)

const player = useAudioPlayer()
const recorder = useAudioRecorder((buffer) => store.sendAudio(buffer))
const cam = useCamera(videoEl)

// 摄像头在面试激活且 video 元素渲染后启动
watch(() => store.status, async (s) => {
  if (s === 'active') {
    await nextTick()
    cam.start()
  } else {
    cam.stop()
  }
})

// 监听播放状态同步到 store
watch(() => player.playing.value, (v) => { store.aiSpeaking = v })

function startInterview() {
  store.reset()
  store.setAudioPlayer(player)
  store.connect(route.params.id)
}

function toggleMic() {
  if (recorder.recording.value) {
    recorder.stop()
  } else {
    recorder.start()
  }
}

watch(() => store.messages.length, async () => {
  await nextTick()
  if (chatPanel.value) chatPanel.value.scrollTop = chatPanel.value.scrollHeight
})
</script>

<style scoped>
.interview { display: flex; flex-direction: column; height: 100vh; }
.video-area { display: flex; height: 40vh; min-height: 200px; border-bottom: 1px solid #e5e7eb; }
.avatar-box { flex: 1; background: #f0f0f0; position: relative; }
.camera-box { flex: 1; background: #1a1a1a; position: relative; display: flex; align-items: center; justify-content: center; }
.camera-box video { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); }
.cam-off { color: #9ca3af; font-size: 14px; position: absolute; }
.mode-select { display: flex; gap: 8px; padding: 20px; justify-content: center; align-items: center; }
.mode-select button { padding: 10px 20px; border: 2px solid #d1d5db; border-radius: 8px; background: white; cursor: pointer; }
.start-btn { background: #4f46e5 !important; color: white; border-color: #4f46e5 !important; }
.start-btn:disabled { opacity: 0.7; cursor: wait; }
.dots::after { content: ''; animation: dots 1.5s steps(3) infinite; }
@keyframes dots { 0% { content: ''; } 33% { content: '.'; } 66% { content: '..'; } 100% { content: '...'; } }
.chat-panel { flex: 1; overflow-y: auto; padding: 20px; }
.msg { margin-bottom: 16px; }
.msg.ai { text-align: left; }
.msg.user { text-align: right; }
.role { font-size: 12px; color: #888; }
.msg p { display: inline-block; padding: 10px 16px; border-radius: 12px; max-width: 70%; text-align: left; }
.msg.ai p { background: #f3f4f6; }
.msg.user p { background: #4f46e5; color: white; }
.msg.system p { background: #fef3c7; text-align: center; max-width: 100%; }
.input-bar { display: flex; gap: 8px; padding: 16px; border-top: 1px solid #e5e7eb; align-items: center; flex-wrap: wrap; }
.input-bar button { padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; background: #4f46e5; color: white; }
.mic-btn.recording { background: #dc2626; animation: pulse 1s infinite; }
.ai-status { font-size: 13px; color: #6b7280; }
.status-indicator { width: 100%; margin-bottom: 4px; }
.status { font-size: 13px; font-weight: 500; padding: 4px 12px; border-radius: 12px; }
.status.recording { color: #dc2626; background: #fef2f2; animation: pulse 1s infinite; }
.status.speaking { color: #2563eb; background: #eff6ff; animation: pulse 1.5s infinite; }
.status.idle { color: #6b7280; background: #f3f4f6; }
.end-btn { background: #ef4444 !important; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.6; } }
</style>
