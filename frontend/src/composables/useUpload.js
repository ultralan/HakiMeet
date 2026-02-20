import { ref, computed } from 'vue'

export function useUpload() {
  const progress = ref(0)      // 0-100
  const phase = ref('')        // '' | 'uploading' | 'processing' | 'done' | 'error'
  const uploading = computed(() => phase.value === 'uploading' || phase.value === 'processing')

  function send(url, formData) {
    return new Promise((resolve, reject) => {
      phase.value = 'uploading'
      progress.value = 0
      const xhr = new XMLHttpRequest()

      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) progress.value = Math.round((e.loaded / e.total) * 90)
      }
      xhr.upload.onload = () => {
        progress.value = 90
        phase.value = 'processing'
      }
      xhr.onload = () => {
        progress.value = 100
        phase.value = 'done'
        try { resolve(JSON.parse(xhr.responseText)) } catch { resolve(null) }
      }
      xhr.onerror = () => { phase.value = 'error'; reject(new Error('upload failed')) }

      xhr.open('POST', url)
      xhr.send(formData)
    })
  }

  function reset() { progress.value = 0; phase.value = '' }

  return { progress, phase, uploading, send, reset }
}
