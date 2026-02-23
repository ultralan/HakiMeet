<template>
  <div class="p-10">
    <div class="mb-8 page-enter">
      <h1 class="text-lg font-semibold text-text">模型配置</h1>
      <p class="text-text-secondary text-sm mt-1">配置您的 AI 文本模型和语音模型密钥</p>
    </div>

    <!-- 文本模型配置 -->
    <div class="card rounded-2xl p-6 mb-6 page-enter stagger-1">
      <div class="flex items-center justify-between mb-5">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-lg bg-accent-soft flex items-center justify-center">
            <svg class="w-4 h-4 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
            </svg>
          </div>
          <h2 class="text-sm font-semibold text-text">文本模型</h2>
          <span class="text-[11px] text-text-muted">面试引擎 & 记忆分析</span>
        </div>
        <label class="toggle">
          <input type="checkbox" v-model="form.llm_enabled" />
          <span class="toggle-slider"></span>
        </label>
      </div>

      <div v-if="form.llm_enabled" class="space-y-4 animate-fadeIn">
        <!-- 预设供应商 -->
        <div>
          <label class="field-label">预设供应商</label>
          <div class="flex gap-2">
            <button v-for="p in presets" :key="p.name"
              @click="applyPreset(p)"
              class="px-3.5 py-1.5 rounded-lg text-xs font-medium border transition btn-press"
              :class="form.provider_name === p.name
                ? 'bg-accent text-white border-accent shadow-sm'
                : 'bg-surface border-border text-text-secondary hover:border-accent/30 hover:text-accent'">
              {{ p.label }}
            </button>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="field-label">API Key</label>
            <input v-model="form.api_key" type="password" placeholder="sk-..." class="field-input" />
          </div>
          <div>
            <label class="field-label">模型名称</label>
            <input v-model="form.model_id" type="text" placeholder="gpt-4o / deepseek-chat" class="field-input" />
          </div>
        </div>
        <div>
          <label class="field-label">端点 URL</label>
          <input v-model="form.base_url" type="text" placeholder="https://api.openai.com/v1" class="field-input" />
        </div>

        <button @click="testConnection" :disabled="testing"
          class="px-4 py-2 rounded-xl text-xs font-semibold transition btn-press border"
          :class="testResult === null ? 'border-accent text-accent hover:bg-accent-soft'
            : testResult ? 'border-success text-success bg-success-soft'
            : 'border-danger text-danger bg-danger-soft'">
          <span v-if="testing">测试中...</span>
          <span v-else-if="testResult === true">✓ 连接成功</span>
          <span v-else-if="testResult === false">✗ 连接失败</span>
          <span v-else>测试连接</span>
        </button>
        <span v-if="testError" class="text-xs text-danger ml-2">{{ testError }}</span>
      </div>

      <div v-else class="text-xs text-text-muted py-2">
        当前使用系统默认模型。开启后可使用自定义模型（需兼容 OpenAI 格式）。
      </div>
    </div>

    <!-- 语音模型配置 -->
    <div class="card rounded-2xl p-6 mb-6 page-enter stagger-2">
      <div class="flex items-center justify-between mb-5">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-lg bg-success-soft flex items-center justify-center">
            <svg class="w-4 h-4 text-success" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z" />
              <path d="M19 10v2a7 7 0 01-14 0v-2" />
              <path d="M12 19v4M8 23h8" />
            </svg>
          </div>
          <h2 class="text-sm font-semibold text-text">语音模型</h2>
          <span class="text-[11px] text-text-muted">豆包语音大模型 API</span>
        </div>
        <label class="toggle">
          <input type="checkbox" v-model="form.voice_enabled" />
          <span class="toggle-slider"></span>
        </label>
      </div>

      <div v-if="form.voice_enabled" class="space-y-4 animate-fadeIn">
        <div>
          <label class="field-label">WebSocket URL</label>
          <input v-model="form.voice_ws_url" type="text" placeholder="wss://openspeech.bytedance.com/api/v3/realtime/dialogue" class="field-input" />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="field-label">App ID</label>
            <input v-model="form.voice_app_id" type="text" placeholder="应用 ID" class="field-input" />
          </div>
          <div>
            <label class="field-label">App Key</label>
            <input v-model="form.voice_app_key" type="password" placeholder="应用密钥" class="field-input" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="field-label">Access Key</label>
            <input v-model="form.voice_access_key" type="password" placeholder="访问密钥" class="field-input" />
          </div>
          <div>
            <label class="field-label">Secret Key</label>
            <input v-model="form.voice_secret_key" type="password" placeholder="私有密钥" class="field-input" />
          </div>
        </div>
        <div>
          <label class="field-label">Resource ID</label>
          <input v-model="form.voice_resource_id" type="text" placeholder="资源 ID" class="field-input" />
        </div>
      </div>

      <div v-else class="text-xs text-text-muted py-2">
        当前使用系统默认语音配置。开启后可使用您自己的豆包语音 API 密钥。
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="flex items-center gap-3 page-enter stagger-3">
      <button @click="save" :disabled="saving"
        class="px-6 py-2.5 rounded-xl text-sm font-semibold transition btn-press
          bg-accent text-white hover:bg-accent-hover shadow-sm hover:shadow-md
          disabled:opacity-40 disabled:cursor-not-allowed">
        {{ saving ? '保存中...' : '保存配置' }}
      </button>
      <button @click="resetConfig"
        class="px-5 py-2.5 rounded-xl text-sm font-medium transition btn-press
          border border-border text-text-secondary hover:border-danger hover:text-danger">
        重置为默认
      </button>
      <Transition name="fade">
        <span v-if="saveMsg" class="text-xs font-medium" :class="saveOk ? 'text-success' : 'text-danger'">
          {{ saveMsg }}
        </span>
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const form = ref({
  provider_name: 'custom',
  api_key: '',
  base_url: '',
  model_id: '',
  llm_enabled: false,
  voice_ws_url: '',
  voice_app_id: '',
  voice_access_key: '',
  voice_secret_key: '',
  voice_resource_id: '',
  voice_app_key: '',
  voice_enabled: false,
})

const saving = ref(false)
const saveMsg = ref('')
const saveOk = ref(false)
const testing = ref(false)
const testResult = ref(null)
const testError = ref('')
const hasExisting = ref(false)

const presets = [
  { name: 'openai', label: 'OpenAI', base_url: 'https://api.openai.com/v1', model_id: 'gpt-4o' },
  { name: 'deepseek', label: 'DeepSeek', base_url: 'https://api.deepseek.com/v1', model_id: 'deepseek-chat' },
  { name: 'doubao', label: '豆包', base_url: 'https://ark.cn-beijing.volces.com/api/v3', model_id: '' },
  { name: 'custom', label: '自定义', base_url: '', model_id: '' },
]

function applyPreset(p) {
  form.value.provider_name = p.name
  form.value.base_url = p.base_url
  if (p.model_id) form.value.model_id = p.model_id
}

onMounted(async () => {
  try {
    const res = await fetch('/api/ai-config')
    if (res.ok) {
      const data = await res.json()
      if (data) {
        hasExisting.value = true
        form.value.provider_name = data.provider_name || 'custom'
        form.value.base_url = data.base_url || ''
        form.value.model_id = data.model_id || ''
        form.value.llm_enabled = data.llm_enabled
        form.value.voice_ws_url = data.voice_ws_url || ''
        form.value.voice_app_id = data.voice_app_id || ''
        form.value.voice_enabled = data.voice_enabled
        // 密钥字段不回显（后端返回的是脱敏值）
      }
    }
  } catch (e) {
    console.warn('加载 AI 配置失败', e)
  }
})

async function save() {
  saving.value = true
  saveMsg.value = ''
  try {
    const res = await fetch('/api/ai-config', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    })
    if (res.ok) {
      saveOk.value = true
      saveMsg.value = '✓ 配置已保存'
      hasExisting.value = true
    } else {
      const err = await res.json()
      saveOk.value = false
      saveMsg.value = '保存失败: ' + (err.detail || '未知错误')
    }
  } catch (e) {
    saveOk.value = false
    saveMsg.value = '网络错误'
  } finally {
    saving.value = false
    setTimeout(() => { saveMsg.value = '' }, 3000)
  }
}

async function resetConfig() {
  if (!hasExisting.value) return
  try {
    await fetch('/api/ai-config', { method: 'DELETE' })
    form.value = {
      provider_name: 'custom',
      api_key: '', base_url: '', model_id: '',
      llm_enabled: false,
      voice_ws_url: '', voice_app_id: '', voice_access_key: '',
      voice_secret_key: '', voice_resource_id: '', voice_app_key: '',
      voice_enabled: false,
    }
    hasExisting.value = false
    saveOk.value = true
    saveMsg.value = '✓ 已重置为默认配置'
    setTimeout(() => { saveMsg.value = '' }, 3000)
  } catch (e) {
    saveOk.value = false
    saveMsg.value = '重置失败'
  }
}

async function testConnection() {
  testing.value = true
  testResult.value = null
  testError.value = ''
  try {
    const res = await fetch('/api/ai-config/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    })
    const data = await res.json()
    testResult.value = data.ok
    if (!data.ok) testError.value = data.error || '连接失败'
  } catch (e) {
    testResult.value = false
    testError.value = '网络错误'
  } finally {
    testing.value = false
    setTimeout(() => { testResult.value = null; testError.value = '' }, 5000)
  }
}
</script>

<style scoped>
.field-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-muted);
  margin-bottom: 0.375rem;
}
.field-input {
  width: 100%;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 0.625rem 0.875rem;
  font-size: 0.8125rem;
  color: var(--color-text);
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.field-input:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-accent-soft);
}
.field-input::placeholder {
  color: var(--color-text-muted);
}

/* Toggle switch */
.toggle {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 22px;
  cursor: pointer;
}
.toggle input { display: none; }
.toggle-slider {
  position: absolute;
  inset: 0;
  background: var(--color-border);
  border-radius: 11px;
  transition: all 0.25s ease;
}
.toggle-slider::before {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  left: 3px;
  top: 3px;
  background: white;
  border-radius: 50%;
  transition: transform 0.25s ease;
  box-shadow: 0 1px 3px rgba(0,0,0,0.15);
}
.toggle input:checked + .toggle-slider {
  background: var(--color-accent);
}
.toggle input:checked + .toggle-slider::before {
  transform: translateX(18px);
}

.animate-fadeIn {
  animation: fadeIn 0.25s ease both;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
