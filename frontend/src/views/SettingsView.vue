<template>
  <div class="settings-page">
    <!-- Header -->
    <header class="page-header">
      <div>
        <h1 class="page-title">模型配置</h1>
        <p class="page-subtitle">配置您的 AI 文本模型和语音模型密钥</p>
      </div>
    </header>

    <!-- 使用统计 -->
    <section class="stats-section">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-header">
            <div class="stat-icon">
              <Activity :size="14" />
            </div>
            <div class="stat-label">API调用</div>
          </div>
          <div class="stat-value">{{ apiCalls }}<span class="stat-unit">次</span></div>
          <div class="stat-detail success">+128 今日</div>
        </div>


        <div class="stat-card">
          <div class="stat-header">
            <div class="stat-icon success">
              <CheckCircle :size="14" />
            </div>
            <div class="stat-label">成功率</div>
          </div>
          <div class="stat-value">{{ successRate }}<span class="stat-unit">%</span></div>
          <div class="stat-detail">{{ failedCalls }} 次失败</div>
        </div>

        <div class="stat-card">
          <div class="stat-header">
            <div class="stat-icon warning">
              <Zap :size="14" />
            </div>
            <div class="stat-label">响应时间</div>
          </div>
          <div class="stat-value">{{ avgResponseTime }}<span class="stat-unit">ms</span></div>
          <div class="stat-detail success">-50ms 较昨日</div>
        </div>

        <div class="stat-card">
          <div class="stat-header">
            <div class="stat-icon danger">
              <DollarSign :size="14" />
            </div>
            <div class="stat-label">本月成本</div>
          </div>
          <div class="stat-value">¥{{ monthlyCost }}</div>
          <div class="stat-detail">预估 ¥{{ estimatedCost }}</div>
        </div>
      </div>
    </section>

    <!-- 性能监控 & 成本分析 -->
    <section class="analysis-section">
      <div class="analysis-grid">
        <div class="analysis-card">
          <div class="analysis-header">
            <div class="analysis-icon">
              <TrendingUp :size="16" />
            </div>
            <div>
              <h3 class="analysis-title">响应时间趋势</h3>
              <p class="analysis-subtitle">最近 7 天平均响应时间</p>
            </div>
          </div>

          <div class="trend-chart">
            <div class="chart-content">
              <div v-for="(day, i) in responseTrend" :key="i" class="chart-bar-wrapper">
                <div class="chart-bar" :style="{ height: (day.time / maxResponseTime * 100) + '%' }">
                  <div class="bar-fill"></div>
                  <div class="bar-tooltip">{{ day.time }}ms</div>
                </div>
                <span class="chart-label">{{ day.label }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="analysis-card">
          <div class="analysis-header">
            <div class="analysis-icon model">
              <PieChart :size="16" />
            </div>
            <div>
              <h3 class="analysis-title">模型使用占比</h3>
              <p class="analysis-subtitle">各模型调用分布</p>
            </div>
          </div>

          <div class="model-list">
            <div v-for="model in modelUsage" :key="model.name" class="model-item">
              <div class="model-header">
                <div class="model-info">
                  <span class="model-name">{{ model.name }}</span>
                  <span class="model-calls">{{ model.calls }} 次</span>
                </div>
                <span class="model-percent">{{ model.percentage }}%</span>
              </div>
              <div class="model-bar">
                <div class="model-bar-fill" :style="{ width: model.percentage + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 文本模型配置 -->
    <section class="config-section">
      <div class="config-card">
        <div class="config-header">
          <div class="config-title-group">
            <div class="config-icon">
              <MessageSquare :size="16" />
            </div>
            <h2 class="config-title">文本模型</h2>
            <span class="config-subtitle">面试引擎 & 记忆分析</span>
          </div>
          <label class="toggle">
            <input type="checkbox" v-model="form.llm_enabled" />
            <span class="toggle-slider"></span>
          </label>
        </div>

        <div v-if="form.llm_enabled" class="config-content">
          <!-- 预设供应商 -->
          <div class="form-group">
            <label class="form-label">预设供应商</label>
            <div class="preset-buttons">
              <button v-for="p in presets" :key="p.name"
                @click="applyPreset(p)"
                class="preset-button"
                :class="{ active: form.provider_name === p.name }">
                {{ p.label }}
              </button>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">API Key</label>
              <input v-model="form.api_key" type="password" placeholder="sk-..." class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">模型名称</label>
              <input v-model="form.model_id" type="text" placeholder="gpt-4o / deepseek-chat" class="form-input" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">端点 URL</label>
            <input v-model="form.base_url" type="text" placeholder="https://api.openai.com/v1" class="form-input" />
          </div>

          <div class="test-section">
            <button @click="testConnection" :disabled="testing"
              class="test-button"
              :class="testResult === null ? 'default' : testResult ? 'success' : 'error'">
              <span v-if="testing">测试中...</span>
              <span v-else-if="testResult === true">✓ 连接成功</span>
              <span v-else-if="testResult === false">✗ 连接失败</span>
              <span v-else>测试连接</span>
            </button>
            <span v-if="testError" class="test-error">{{ testError }}</span>
          </div>
        </div>

        <div v-else class="config-disabled">
          当前使用系统默认模型。开启后可使用自定义模型（需兼容 OpenAI 格式）。
        </div>
      </div>
    </section>

    <!-- 语音模型配置 -->
    <section class="config-section">
      <div class="config-card">
        <div class="config-header">
          <div class="config-title-group">
            <div class="config-icon voice">
              <Mic :size="16" />
            </div>
            <h2 class="config-title">语音模型</h2>
            <span class="config-subtitle">豆包语音大模型 API</span>
          </div>
          <label class="toggle">
            <input type="checkbox" v-model="form.voice_enabled" />
            <span class="toggle-slider"></span>
          </label>
        </div>

        <div v-if="form.voice_enabled" class="config-content">
          <div class="form-group">
            <label class="form-label">WebSocket URL</label>
            <input v-model="form.voice_ws_url" type="text" placeholder="wss://openspeech.bytedance.com/api/v3/realtime/dialogue" class="form-input" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">App ID</label>
              <input v-model="form.voice_app_id" type="text" placeholder="应用 ID" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">App Key</label>
              <input v-model="form.voice_app_key" type="password" placeholder="应用密钥" class="form-input" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Access Key</label>
              <input v-model="form.voice_access_key" type="password" placeholder="访问密钥" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Secret Key</label>
              <input v-model="form.voice_secret_key" type="password" placeholder="私有密钥" class="form-input" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Resource ID</label>
            <input v-model="form.voice_resource_id" type="text" placeholder="资源 ID" class="form-input" />
          </div>
        </div>

        <div v-else class="config-disabled">
          当前使用系统默认语音配置。开启后可使用您自己的豆包语音 API 密钥。
        </div>
      </div>
    </section>

    <!-- 操作按钮 -->
    <section class="actions-section">
      <button @click="save" :disabled="saving" class="save-button">
        {{ saving ? '保存中...' : '保存配置' }}
      </button>
      <button @click="resetConfig" class="reset-button">
        重置为默认
      </button>
      <Transition name="fade">
        <span v-if="saveMsg" class="save-message" :class="saveOk ? 'success' : 'error'">
          {{ saveMsg }}
        </span>
      </Transition>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { MessageSquare, Mic, Activity, CheckCircle, Zap, DollarSign, TrendingUp, PieChart } from 'lucide-vue-next'

// 使用统计数据
const apiCalls = ref(2456)
const successRate = ref(98.5)
const failedCalls = ref(37)
const avgResponseTime = ref(850)
const monthlyCost = ref(128)
const estimatedCost = ref(380)

// 响应时间趋势
const responseTrend = ref([
  { label: '周一', time: 920 },
  { label: '周二', time: 880 },
  { label: '周三', time: 850 },
  { label: '周四', time: 790 },
  { label: '周五', time: 820 },
  { label: '周六', time: 760 },
  { label: '周日', time: 850 },
])
const maxResponseTime = ref(1000)

// 模型使用占比
const modelUsage = ref([
  { name: 'GPT-4o', calls: 1245, percentage: 51 },
  { name: 'DeepSeek', calls: 732, percentage: 30 },
  { name: '豆包', calls: 479, percentage: 19 },
])

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
.settings-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 28px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Header */
.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.025em;
  color: #0f172a;
  margin: 0 0 4px 0;
  line-height: 1.1;
}

.page-subtitle {
  font-size: 14px;
  color: #475569;
  margin: 0;
  font-weight: 400;
}

/* Config Section */
.config-section {
  margin-bottom: 20px;
}

.config-card {
  padding: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.config-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.config-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.config-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
  flex-shrink: 0;
}

.config-icon.voice {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
  color: #10b981;
}

.config-title {
  font-size: 13px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.config-subtitle {
  font-size: 11px;
  color: #475569;
}

.config-content {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.config-disabled {
  font-size: 11px;
  color: #475569;
  padding: 8px 0;
}

/* Form Styles */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 11px;
  font-weight: 600;
  color: #475569;
}

.form-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 12px;
  color: #0f172a;
  background: #f8fafc;
  outline: none;
  transition: all 0.2s;
}

.form-input:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  background: #ffffff;
}

.form-input::placeholder {
  color: #94a3b8;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

/* Preset Buttons */
.preset-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.preset-button {
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-button:hover {
  border-color: rgba(99, 102, 241, 0.3);
  color: #6366f1;
}

.preset-button.active {
  background: #6366f1;
  color: white;
  border-color: #6366f1;
  box-shadow: 0 2px 4px rgba(99, 102, 241, 0.2);
}

/* Test Section */
.test-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.test-button {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.2s;
}

.test-button.default {
  background: transparent;
  color: #6366f1;
  border-color: #6366f1;
}

.test-button.default:hover:not(:disabled) {
  background: rgba(99, 102, 241, 0.1);
}

.test-button.success {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #16a34a;
  border-color: rgba(16, 185, 129, 0.3);
}

.test-button.error {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #dc2626;
  border-color: rgba(220, 38, 38, 0.3);
}

.test-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.test-error {
  font-size: 11px;
  color: #ef4444;
}

/* Actions Section */
.actions-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.save-button {
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  background: #6366f1;
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(99, 102, 241, 0.2);
}

.save-button:hover:not(:disabled) {
  background: #4f46e5;
  box-shadow: 0 4px 8px rgba(99, 102, 241, 0.3);
}

.save-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.reset-button {
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  background: transparent;
  color: #475569;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.2s;
}

.reset-button:hover {
  border-color: #ef4444;
  color: #ef4444;
}

.save-message {
  font-size: 11px;
  font-weight: 600;
}

.save-message.success {
  color: #10b981;
}

.save-message.error {
  color: #ef4444;
}

/* Toggle switch */
.toggle {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 22px;
  cursor: pointer;
}

.toggle input {
  display: none;
}

.toggle-slider {
  position: absolute;
  inset: 0;
  background: #e2e8f0;
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
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
}

.toggle input:checked + .toggle-slider {
  background: #6366f1;
}

.toggle input:checked + .toggle-slider::before {
  transform: translateX(18px);
}

/* Stats Section */
.stats-section {
  margin-bottom: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.stat-card {
  padding: 12px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-card:hover {
  border-color: rgba(99, 102, 241, 0.2);
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  box-shadow: 0 8px 16px rgba(99, 102, 241, 0.08), 0 4px 8px rgba(0, 0, 0, 0.02);
}

.stat-header {
  display: flex;
  align-items: center;
  gap: 5px;
}

.stat-icon {
  color: #6366f1;
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.stat-icon.success {
  color: #10b981;
}

.stat-icon.warning {
  color: #f59e0b;
}

.stat-icon.danger {
  color: #ef4444;
}

.stat-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #475569;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #0f172a;
  line-height: 1;
}

.stat-unit {
  font-size: 14px;
  color: #64748b;
  margin-left: 4px;
  font-weight: 500;
}

.stat-detail {
  font-size: 11px;
  color: #475569;
  padding-top: 4px;
  border-top: 1px solid #f1f5f9;
}

.stat-detail.success {
  color: #10b981;
  font-weight: 500;
}

/* Analysis Section */
.analysis-section {
  margin-bottom: 20px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.analysis-card {
  padding: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.analysis-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.analysis-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
  flex-shrink: 0;
}

.analysis-icon.model {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
  color: #10b981;
}

.analysis-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.analysis-subtitle {
  font-size: 11px;
  color: #475569;
  margin: 2px 0 0 0;
}

/* Trend Chart */
.trend-chart {
  position: relative;
  height: 140px;
}

.chart-content {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  padding: 10px 0 30px 0;
}

.chart-bar-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.chart-bar {
  width: 100%;
  max-width: 28px;
  position: relative;
  display: flex;
  align-items: flex-end;
  cursor: pointer;
  min-height: 8px;
}

.bar-fill {
  width: 100%;
  height: 100%;
  border-radius: 4px 4px 0 0;
  background: linear-gradient(180deg, #6366f1 0%, #4f46e5 100%);
  transition: all 0.3s;
}

.chart-bar:hover .bar-fill {
  opacity: 0.8;
}

.bar-tooltip {
  position: absolute;
  top: -28px;
  left: 50%;
  transform: translateX(-50%);
  background: #0f172a;
  color: white;
  font-size: 10px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s;
}

.chart-bar:hover .bar-tooltip {
  opacity: 1;
}

.chart-label {
  font-size: 10px;
  color: #475569;
  font-weight: 500;
}

/* Model List */
.model-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.model-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.model-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.model-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.model-name {
  font-size: 12px;
  font-weight: 600;
  color: #0f172a;
}

.model-calls {
  font-size: 10px;
  color: #475569;
}

.model-percent {
  font-size: 11px;
  font-weight: 700;
  color: #475569;
}

.model-bar {
  width: 100%;
  height: 6px;
  background: #f1f5f9;
  border-radius: 3px;
  overflow: hidden;
}

.model-bar-fill {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, #6366f1 0%, #4f46e5 100%);
  transition: width 0.5s ease;
}

/* Animations */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
