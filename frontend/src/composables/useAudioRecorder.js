import { ref, onUnmounted } from 'vue'

export function useAudioRecorder(onAudioData) {
  const recording = ref(false)
  let stream = null
  let audioCtx = null
  let source = null
  let processor = null

  async function start() {
    stream = await navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, sampleRate: 16000 },
    })
    audioCtx = new AudioContext({ sampleRate: 16000 })
    source = audioCtx.createMediaStreamSource(stream)

    // ScriptProcessor fallback (AudioWorklet 需要单独文件)
    processor = audioCtx.createScriptProcessor(4096, 1, 1)
    processor.onaudioprocess = (e) => {
      const float32 = e.inputBuffer.getChannelData(0)
      // Float32 → Int16 PCM
      const int16 = new Int16Array(float32.length)
      for (let i = 0; i < float32.length; i++) {
        int16[i] = Math.max(-32768, Math.min(32767, float32[i] * 32768))
      }
      onAudioData(int16.buffer)
    }
    source.connect(processor)
    processor.connect(audioCtx.destination)
    recording.value = true
  }

  function stop() {
    processor?.disconnect()
    source?.disconnect()
    audioCtx?.close()
    stream?.getTracks().forEach((t) => t.stop())
    processor = null
    source = null
    audioCtx = null
    stream = null
    recording.value = false
  }

  onUnmounted(stop)

  return { recording, start, stop }
}
