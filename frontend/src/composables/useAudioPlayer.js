import { ref } from 'vue'

export function useAudioPlayer() {
  const playing = ref(false)
  let audioCtx = null
  const queue = []
  let isPlaying = false

  function getCtx() {
    if (!audioCtx) audioCtx = new AudioContext({ sampleRate: 24000 })
    return audioCtx
  }

  function enqueue(base64Audio) {
    const binary = atob(base64Audio)
    const bytes = new Uint8Array(binary.length)
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)
    // PCM 16-bit → Float32
    const int16 = new Int16Array(bytes.buffer)
    const float32 = new Float32Array(int16.length)
    for (let i = 0; i < int16.length; i++) float32[i] = int16[i] / 32768
    queue.push(float32)
    if (!isPlaying) playNext()
  }

  function playNext() {
    if (queue.length === 0) {
      isPlaying = false
      playing.value = false
      return
    }
    isPlaying = true
    playing.value = true
    const ctx = getCtx()
    const data = queue.shift()
    const buf = ctx.createBuffer(1, data.length, 24000)
    buf.getChannelData(0).set(data)
    const src = ctx.createBufferSource()
    src.buffer = buf
    src.connect(ctx.destination)
    src.onended = playNext
    src.start()
  }

  function flush() {
    queue.length = 0
    isPlaying = false
    playing.value = false
  }

  return { playing, enqueue, flush }
}
