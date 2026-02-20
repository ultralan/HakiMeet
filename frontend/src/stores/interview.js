import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useInterviewStore = defineStore('interview', () => {
  const messages = ref([])
  const status = ref('idle') // idle | connecting | active | ended
  const isRecording = ref(false)
  const aiSpeaking = ref(false)
  const ws = ref(null)

  // 外部注入的音频播放器
  let audioPlayer = null
  function setAudioPlayer(player) { audioPlayer = player }

  function connect(interviewId) {
    status.value = 'connecting'
    const socket = new WebSocket(`ws://localhost:8000/ws/interview/${interviewId}`)

    socket.onopen = () => {
      socket.send(JSON.stringify({ mode: 'voice' }))
      status.value = 'active'
    }

    socket.onmessage = (event) => {
      const msg = JSON.parse(event.data)
      if (msg.type === 'ai_text') {
        messages.value.push({ role: 'ai', text: msg.data.text })
      } else if (msg.type === 'ai_text_chunk') {
        if (msg.data.done) return
        const last = messages.value[messages.value.length - 1]
        if (last && last.role === 'ai' && last.streaming) {
          last.text += msg.data.text
        } else {
          messages.value.push({ role: 'ai', text: msg.data.text, streaming: true })
        }
      } else if (msg.type === 'ai_audio') {
        aiSpeaking.value = true
        if (audioPlayer) audioPlayer.enqueue(msg.data.audio)
      } else if (msg.type === 'interrupted') {
        aiSpeaking.value = false
        if (audioPlayer) audioPlayer.flush()
      } else if (msg.type === 'report') {
        status.value = 'ended'
        messages.value.push({ role: 'system', text: msg.data.summary })
      }
    }

    socket.onclose = () => { status.value = 'idle' }
    ws.value = socket
  }

  function sendAudio(buffer) {
    if (ws.value?.readyState === WebSocket.OPEN) {
      ws.value.send(buffer)
    }
  }

  function endInterview() {
    if (!ws.value) return
    ws.value.send(JSON.stringify({ type: 'control', data: { action: 'end' } }))
  }

  function reset() {
    messages.value = []
    status.value = 'idle'
    isRecording.value = false
    aiSpeaking.value = false
    ws.value = null
    audioPlayer = null
  }

  return {
    messages, status, isRecording, aiSpeaking,
    setAudioPlayer, connect, sendAudio, endInterview, reset,
  }
})
