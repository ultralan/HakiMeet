import { ref, onUnmounted } from 'vue'

export function useCamera(videoEl) {
  const active = ref(false)
  let stream = null

  async function start() {
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 320, height: 240, facingMode: 'user' },
        audio: false,
      })
      if (videoEl.value) {
        videoEl.value.srcObject = stream
      }
      active.value = true
    } catch (e) {
      console.warn('摄像头获取失败，面试继续', e)
    }
  }

  function stop() {
    stream?.getTracks().forEach((t) => t.stop())
    stream = null
    active.value = false
  }

  onUnmounted(stop)
  return { active, start, stop }
}
