<template>
  <div class="memory-page">
    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
    </div>

    <template v-if="!loading">

      <!-- Empty State -->
      <div v-if="totalCount === 0" class="empty-state">
        <div class="empty-icon success">
          <CheckCircle :size="24" />
        </div>
        <div class="empty-title">暂无记忆积淀</div>
        <div class="empty-desc">完成面试后，AI 将根据您的答题深度自动沉淀记忆点</div>
      </div>

      <!-- Graph View (Minimalist Network) -->
      <section v-if="totalCount > 0" class="graph-section">
        <!-- Title inside graph section -->
        <div class="graph-header">
          <div>
            <h1 class="graph-title">长期记忆</h1>
            <p class="graph-subtitle">AI 沉淀的技术认知地图</p>
          </div>
        </div>
        <!-- Control Panel -->
        <div class="graph-controls">
          <div class="control-group">
            <button @click="graphScale = Math.max(0.5, graphScale - 0.1)" class="control-btn" title="缩小">
              <span>-</span>
            </button>
            <span class="scale-label">{{ Math.round(graphScale * 100) }}%</span>
            <button @click="graphScale = graphScale + 0.1" class="control-btn" title="放大">
              <span>+</span>
            </button>
            <button @click="resetView" class="control-btn reset-btn" title="归位">
              <span>⊙</span>
            </button>
          </div>
          <div class="control-group">
            <label class="toggle-label">
              <input type="checkbox" v-model="showMemoryLabels" class="toggle-input">
              <span class="toggle-text">显示记忆点标签</span>
            </label>
          </div>
        </div>

        <div
          class="network-container"
          @wheel="handleWheel"
          @mousedown="handleMouseDown"
          @mousemove="handleMouseMove"
          @mouseup="handleMouseUp"
          @mouseleave="handleMouseUp"
        >
          <div
            class="graph-content"
            :class="{ dragging: isDragging }"
            :style="{
              transform: `scale(${graphScale}) translate(${panOffset.x / graphScale}px, ${panOffset.y / graphScale}px)`
            }"
          >
          <!-- SVG for connections -->
          <svg class="network-svg" viewBox="0 0 1000 600">
            <!-- Connections -->
            <path
              v-for="(items, category, idx) in grouped"
              :key="`conn-${category}`"
              :d="getConnectionPath(idx, Object.keys(grouped).length, category)"
              class="network-line"
              :style="{ stroke: getCategoryColorHex(category) }"
            />
          </svg>

          <!-- Center node -->
          <div class="center-node">
            <div class="node-dot center"></div>
            <div class="node-label">记忆核心</div>
          </div>

          <!-- Category nodes -->
          <div
            v-for="(items, category, idx) in grouped"
            :key="category"
            class="category-node"
            :style="getNeuronPosition(idx, Object.keys(grouped).length, category)"
          >
            <div
              class="node-dot category"
              :style="{
                borderColor: getCategoryColorHex(category),
                boxShadow: `0 0 0 2px ${getCategoryColorHex(category)}20`
              }"
              @click="openColorPicker(category, $event)"
            ></div>
            <div class="node-info">
              <div class="node-title">{{ category }}</div>
              <div class="node-count">{{ items.length }}</div>
            </div>

            <!-- Memory nodes -->
            <div class="memory-nodes">
              <div
                v-for="(item, itemIdx) in items"
                :key="item.id"
                class="memory-dot-wrapper"
                :style="getSynapsePosition(itemIdx, items.length, item.id)"
              >
                <div
                  class="memory-dot"
                  :class="{ resolved: item.resolved }"
                  :style="{
                    background: getCategoryColorHex(category),
                    boxShadow: `0 0 0 1px ${getCategoryColorHex(category)}30`
                  }"
                  :title="item.question_summary"
                  @click="handleMemoryClick(item, $event)"
                ></div>
                <div
                  v-if="showMemoryLabels"
                  class="memory-label"
                  :style="{ transform: `translateX(-50%) scale(${1 / graphScale})` }"
                >
                  {{ item.question_summary }}
                </div>
              </div>
            </div>
          </div>
          </div>
        </div>
      </section>

    </template>

    <!-- Detail Card -->
    <div
      v-if="selectedItem"
      class="detail-card"
      :style="{
        left: `${cardPosition.x}px`,
        top: `${cardPosition.y}px`
      }"
      @click.stop
    >
        <div class="modal-header">
          <div class="modal-severity">
            <span
              v-for="s in 5"
              :key="s"
              class="severity-dot"
              :class="{
                active: s <= selectedItem.severity,
                high: s <= selectedItem.severity && selectedItem.severity >= 4,
                medium: s <= selectedItem.severity && selectedItem.severity >= 3
              }"
            ></span>
          </div>
          <button @click="selectedItem = null" class="modal-close">
            <X :size="16" />
          </button>
        </div>
        <div class="modal-body">
          <div class="modal-category">{{ selectedItem.category }}</div>
          <div class="modal-question">{{ selectedItem.question_summary }}</div>
          <div class="modal-weakness">{{ selectedItem.weakness_desc }}</div>
          <div class="modal-date">{{ formatDate(selectedItem.created_at) }}</div>
        </div>
        <div class="modal-footer">
          <button
            v-if="!selectedItem.resolved"
            @click="resolvePoint(selectedItem); selectedItem = null"
            class="modal-btn primary"
          >
            <CheckCircle :size="14" />
            标记已解决
          </button>
          <button @click="deletePoint(selectedItem); selectedItem = null" class="modal-btn danger">
            <Trash2 :size="14" />
            删除
          </button>
        </div>
    </div>

    <!-- Color Picker (Inside Canvas) -->
    <div
      v-if="showColorPicker"
      class="color-picker-popup"
      :style="{
        left: `${colorPickerPosition.x}px`,
        top: `${colorPickerPosition.y}px`
      }"
      @click.stop
    >
      <div class="picker-header">
        <span class="picker-category">{{ editingCategory }}</span>
        <button @click="showColorPicker = false" class="picker-close">
          <X :size="12" />
        </button>
      </div>
      <div class="color-grid">
        <div
          v-for="(color, idx) in colorPresets"
          :key="idx"
          class="color-option"
          :style="{ background: color }"
          @click="selectColor(color)"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  CheckCircle, Trash2, Brain, AlertCircle, TrendingUp,
  Calendar, X, Network, BarChart3, Clock, Grid3x3
} from 'lucide-vue-next'

const grouped = ref({})
const loading = ref(true)
const currentView = ref('graph')
const selectedItem = ref(null)
const selectedCategory = ref(null)
const graphScale = ref(1)
const showMemoryLabels = ref(false)
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const panOffset = ref({ x: 0, y: 0 })
const showColorPicker = ref(false)
const editingCategory = ref(null)
const categoryColors = ref({})
const cardPosition = ref({ x: 0, y: 0 })
const colorPickerPosition = ref({ x: 0, y: 0 })

const colorPresets = [
  '#6366f1', '#8b5cf6', '#ec4899', '#f59e0b',
  '#10b981', '#06b6d4', '#ef4444', '#14b8a6',
  '#a855f7', '#3b82f6', '#84cc16', '#f97316'
]

const views = [
  { key: 'tree', label: '树状图', icon: Network },
  { key: 'graph', label: '知识图谱', icon: Brain },
  { key: 'timeline', label: '时间轴', icon: Clock },
  { key: 'heatmap', label: '热力图', icon: Grid3x3 },
]

// Computed stats
const allItems = computed(() => {
  const items = []
  for (const [category, categoryItems] of Object.entries(grouped.value)) {
    items.push(...categoryItems.map(item => ({ ...item, category })))
  }
  return items
})

const totalCount = computed(() => allItems.value.length)
const categoryCount = computed(() => Object.keys(grouped.value).length)
const resolvedCount = computed(() => allItems.value.filter(i => i.resolved).length)
const resolveRate = computed(() =>
  totalCount.value > 0 ? Math.round((resolvedCount.value / totalCount.value) * 100) : 0
)
const highSeverityCount = computed(() => allItems.value.filter(i => i.severity >= 4 && !i.resolved).length)

const weekCount = computed(() => {
  const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
  return allItems.value.filter(i => new Date(i.created_at) > weekAgo).length
})

const weekTrend = computed(() => {
  // Mock trend calculation
  return Math.floor(Math.random() * 40) - 20
})

const timelineGroups = computed(() => {
  const groups = {}
  allItems.value.forEach(item => {
    const date = formatDate(item.created_at)
    if (!groups[date]) groups[date] = []
    groups[date].push(item)
  })
  return Object.entries(groups)
    .map(([date, items]) => ({ date, items }))
    .sort((a, b) => new Date(b.items[0].created_at) - new Date(a.items[0].created_at))
})

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

function getCategoryColor(category) {
  const colors = [
    'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)', // 蓝色
    'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)', // 紫色
    'linear-gradient(135deg, #ec4899 0%, #db2777 100%)', // 粉色
    'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)', // 橙色
    'linear-gradient(135deg, #10b981 0%, #059669 100%)', // 绿色
    'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)', // 青色
    'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)', // 红色
    'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)', // 青绿色
    'linear-gradient(135deg, #a855f7 0%, #9333ea 100%)', // 深紫色
    'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)', // 天蓝色
    'linear-gradient(135deg, #84cc16 0%, #65a30d 100%)', // 黄绿色
    'linear-gradient(135deg, #f97316 0%, #ea580c 100%)', // 深橙色
  ]
  const index = category.charCodeAt(0) % colors.length
  return colors[index]
}

function getSeverityClass(severity) {
  if (severity >= 4) return 'high'
  if (severity >= 3) return 'medium'
  return 'low'
}

// 神经元布局相关函数
function getCategoryColorHex(category) {
  // 优先使用自定义颜色
  if (categoryColors.value[category]) {
    return categoryColors.value[category]
  }

  const colors = [
    '#6366f1', // 蓝色
    '#8b5cf6', // 紫色
    '#ec4899', // 粉色
    '#f59e0b', // 橙色
    '#10b981', // 绿色
    '#06b6d4', // 青色
    '#ef4444', // 红色
    '#14b8a6', // 青绿色
    '#a855f7', // 深紫色
    '#3b82f6', // 天蓝色
    '#84cc16', // 黄绿色
    '#f97316', // 深橙色
  ]
  const index = category.charCodeAt(0) % colors.length
  return colors[index]
}

// 计算节点的实际位置（包含随机偏移）
function calculateNodePosition(index, total, category) {
  // 基础圆形排布
  const angle = (index / total) * 2 * Math.PI - Math.PI / 2
  const radius = 280

  // 使用 category 生成随机偏移
  let hash = 0
  if (category) {
    const catStr = String(category)
    for (let i = 0; i < catStr.length; i++) {
      hash = ((hash << 5) - hash) + catStr.charCodeAt(i)
      hash = hash & hash
    }
  }

  const seed = Math.abs(hash || index)
  const random1 = (seed * 9301 + 49297) % 233280 / 233280
  const random2 = (seed * 7919 + 12345) % 233280 / 233280

  // 添加随机偏移(角度偏移±30度,半径偏移±40px)
  const angleOffset = (random1 - 0.5) * Math.PI / 3
  const radiusOffset = (random2 - 0.5) * 80

  const finalAngle = angle + angleOffset
  const finalRadius = radius + radiusOffset

  const x = Math.cos(finalAngle) * finalRadius
  const y = Math.sin(finalAngle) * finalRadius

  return { x, y }
}

function getNeuronPosition(index, total, category) {
  const { x, y } = calculateNodePosition(index, total, category)
  return {
    left: `calc(50% + ${x}px)`,
    top: `calc(50% + ${y}px)`,
    transform: 'translate(-50%, -50%)'
  }
}

function getConnectionPath(index, total, category) {
  const { x, y } = calculateNodePosition(index, total, category)
  const centerX = 500
  const centerY = 300
  const endX = centerX + x
  const endY = centerY + y

  // 贝塞尔曲线控制点
  const controlX = centerX + x * 0.4
  const controlY = centerY + y * 0.4

  return `M ${centerX} ${centerY} Q ${controlX} ${controlY} ${endX} ${endY}`
}

function getSynapsePosition(index, total, id) {
  // 将 id 转换为数字哈希值
  let hash = 0
  if (id) {
    const idStr = String(id)
    for (let i = 0; i < idStr.length; i++) {
      hash = ((hash << 5) - hash) + idStr.charCodeAt(i)
      hash = hash & hash // 转换为32位整数
    }
  }

  // 使用 hash 和 index 生成伪随机数
  const seed = Math.abs(hash || index)
  const random1 = (seed * 9301 + 49297) % 233280 / 233280
  const random2 = (seed * 7919 + 12345) % 233280 / 233280

  // 随机角度
  const angle = random1 * 2 * Math.PI
  // 随机半径(在40-140px之间,更分散)
  const radius = 40 + random2 * 100

  const x = Math.cos(angle) * radius
  const y = Math.sin(angle) * radius

  return {
    left: `calc(50% + ${x}px)`,
    top: `calc(50% + ${y}px)`,
    transform: 'translate(-50%, -50%)'
  }
}

function getClusterPosition(index, total) {
  const angle = (index / total) * 2 * Math.PI - Math.PI / 2
  const radius = 140
  const x = Math.cos(angle) * radius
  const y = Math.sin(angle) * radius
  return {
    left: `calc(50% + ${x}px)`,
    top: `calc(50% + ${y}px)`,
    transform: 'translate(-50%, -50%)'
  }
}

function getAvgSeverity(items) {
  if (items.length === 0) return 0
  return items.reduce((sum, item) => sum + item.severity, 0) / items.length
}

function getHeatmapColor(items) {
  const avgSeverity = getAvgSeverity(items)
  const unresolvedRatio = items.filter(i => !i.resolved).length / items.length
  const intensity = (avgSeverity / 5) * unresolvedRatio

  if (intensity > 0.7) return 'linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)'
  if (intensity > 0.5) return 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)'
  if (intensity > 0.3) return 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)'
  return 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)'
}

async function loadData() {
  loading.value = true
  try {
    const res = await fetch('/api/memory/list')
    grouped.value = await res.json()
  } catch (e) {
    console.warn('加载长期记忆失败', e)
  } finally {
    loading.value = false
  }
}

async function resolvePoint(item) {
  try {
    await fetch(`/api/memory/${item.id}/resolve`, { method: 'PUT' })
    item.resolved = true
  } catch (e) {
    console.warn('标记失败', e)
  }
}

async function deletePoint(item) {
  try {
    await fetch(`/api/memory/${item.id}`, { method: 'DELETE' })
    for (const cat of Object.keys(grouped.value)) {
      const idx = grouped.value[cat].findIndex(p => p.id === item.id)
      if (idx >= 0) {
        grouped.value[cat].splice(idx, 1)
        if (grouped.value[cat].length === 0) delete grouped.value[cat]
        break
      }
    }
  } catch (e) {
    console.warn('删除失败', e)
  }
}

// 滚轮缩放
function handleWheel(e) {
  e.preventDefault()
  const delta = e.deltaY > 0 ? -0.1 : 0.1
  graphScale.value = Math.max(0.5, graphScale.value + delta)
}

// 拖拽开始
function handleMouseDown(e) {
  if (e.target.closest('.node-dot') || e.target.closest('.memory-dot')) return
  isDragging.value = true
  dragStart.value = { x: e.clientX - panOffset.value.x, y: e.clientY - panOffset.value.y }
}

// 拖拽中
function handleMouseMove(e) {
  if (!isDragging.value) return
  const maxOffset = 800 // 拖拽边界
  const newX = e.clientX - dragStart.value.x
  const newY = e.clientY - dragStart.value.y
  panOffset.value = {
    x: Math.max(-maxOffset, Math.min(maxOffset, newX)),
    y: Math.max(-maxOffset, Math.min(maxOffset, newY))
  }
}

// 拖拽结束
function handleMouseUp() {
  isDragging.value = false
}

// 打开颜色选择器
function openColorPicker(category, event) {
  event.stopPropagation()
  editingCategory.value = category
  colorPickerPosition.value = { x: event.clientX, y: event.clientY }
  showColorPicker.value = true
}

// 选择颜色
function selectColor(color) {
  if (editingCategory.value) {
    categoryColors.value[editingCategory.value] = color
  }
  showColorPicker.value = false
  editingCategory.value = null
}

// 点击记忆点
function handleMemoryClick(item, event) {
  event.stopPropagation()
  selectedItem.value = item
  cardPosition.value = { x: event.clientX, y: event.clientY }
}

// 重置视图
function resetView() {
  graphScale.value = 1
  panOffset.value = { x: 0, y: 0 }
}

// 2D 图谱节点位置计算
function getCategoryPosition2D(index, total) {
  const angle = (index / total) * 2 * Math.PI - Math.PI / 2
  const radius = 180
  const x = Math.cos(angle) * radius
  const y = Math.sin(angle) * radius
  return {
    left: `calc(50% + ${x}px)`,
    top: `calc(50% + ${y}px)`,
    transform: 'translate(-50%, -50%)'
  }
}

onMounted(() => {
  loadData()
  // 点击外部关闭卡片
  document.addEventListener('click', () => {
    if (selectedItem.value) {
      selectedItem.value = null
    }
  })
})
</script>

<style scoped>
.memory-page {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Header */
.page-header {
  padding: 16px 24px;
  border-bottom: 1px solid #e2e8f0;
  background: #ffffff;
  flex-shrink: 0;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.025em;
  color: #0f172a;
  margin: 0 0 4px 0;
  line-height: 1.1;
}

.page-subtitle {
  font-size: 13px;
  color: #64748b;
  margin: 0;
  font-weight: 400;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  gap: 20px;
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

/* View Switcher */
.view-switcher {
  display: flex;
  gap: 4px;
  padding: 4px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.view-button {
  padding: 6px 10px;
  border: none;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  color: #475569;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 4px;
}

.view-button:hover {
  color: #334155;
  background: #f8fafc;
}

.view-button.active {
  color: #6366f1;
  background: rgba(99, 102, 241, 0.1);
  box-shadow: 0 2px 4px rgba(99, 102, 241, 0.1);
}

/* Loading */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 2px solid #e2e8f0;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
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
}

.stat-card:hover {
  border-color: rgba(99, 102, 241, 0.2);
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  box-shadow: 0 8px 16px rgba(99, 102, 241, 0.08);
}

.stat-header {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 8px;
}

.stat-icon {
  color: #6366f1;
}

.stat-icon.success {
  color: #10b981;
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
  margin-bottom: 6px;
}

.stat-detail {
  font-size: 11px;
  color: #475569;
  padding-top: 6px;
  border-top: 1px solid #f1f5f9;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.empty-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
}

.empty-icon.success {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #16a34a;
}

.empty-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 6px;
}

.empty-desc {
  font-size: 12px;
  color: #475569;
  line-height: 1.5;
}

/* Tree Section */
.tree-section {
  margin-bottom: 20px;
}

.tree-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tree-branch {
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 14px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.tree-branch:hover {
  border-color: rgba(99, 102, 241, 0.2);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.08);
}

.branch-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
}

.branch-node {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.branch-letter {
  font-size: 13px;
  font-weight: 700;
  color: white;
}

.branch-info {
  flex: 1;
}

.branch-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 2px;
}

.branch-stats {
  font-size: 11px;
  color: #475569;
}

.branch-children {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 8px;
}

.tree-leaf {
  display: flex;
  gap: 8px;
  padding: 10px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.tree-leaf:hover {
  background: #ffffff;
  border-color: #6366f1;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(99, 102, 241, 0.1);
}

.tree-leaf.resolved {
  opacity: 0.4;
  background: #f1f5f9;
}

.tree-leaf.resolved:hover {
  opacity: 0.6;
}

.leaf-severity {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding-top: 2px;
}

.severity-bar {
  width: 3px;
  height: 8px;
  border-radius: 2px;
}

.severity-bar.low {
  background: #6366f1;
}

.severity-bar.medium {
  background: #f59e0b;
}

.severity-bar.high {
  background: #ef4444;
}

.leaf-content {
  flex: 1;
  min-width: 0;
}

.leaf-title {
  font-size: 12px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.leaf-meta {
  font-size: 10px;
  color: #64748b;
}

/* Graph Section - Minimalist Network */
.graph-section {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px;
  position: relative;
}

/* Graph Header (Floating) */
.graph-header {
  position: absolute;
  top: 24px;
  left: 24px;
  z-index: 100;
  pointer-events: none;
}

.graph-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.025em;
  color: #0f172a;
  margin: 0 0 4px 0;
  line-height: 1.1;
}

.graph-subtitle {
  font-size: 13px;
  color: #64748b;
  margin: 0;
  font-weight: 400;
}

/* Graph Controls */
.graph-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  margin-top: 70px;
  margin-bottom: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.control-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-btn {
  width: 26px;
  height: 26px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #475569;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.control-btn:hover {
  border-color: #6366f1;
  color: #6366f1;
  background: #f8f9ff;
}

.scale-label {
  font-size: 11px;
  font-weight: 600;
  color: #475569;
  min-width: 40px;
  text-align: center;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.toggle-input {
  width: 14px;
  height: 14px;
  cursor: pointer;
  accent-color: #6366f1;
}

.toggle-text {
  font-size: 11px;
  font-weight: 500;
  color: #475569;
  user-select: none;
}

.network-container {
  flex: 1;
  width: 100%;
  border-radius: 10px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  position: relative;
  overflow: hidden;
}

.graph-content {
  width: 100%;
  height: 100%;
  position: absolute;
  inset: 0;
  transition: transform 0.1s ease-out;
  transform-origin: center center;
  cursor: grab;
}

.graph-content.dragging {
  cursor: grabbing;
}

.graph-content .node-dot.category {
  cursor: pointer !important;
}

.network-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.network-line {
  fill: none;
  stroke-width: 1;
  stroke-opacity: 0.25;
  transition: stroke-opacity 0.3s ease;
}

.center-node {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  z-index: 20;
}

.node-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.node-dot.center {
  background: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.node-label {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 10px;
  font-size: 11px;
  font-weight: 600;
  color: #475569;
  white-space: nowrap;
}

.category-node {
  position: absolute;
  z-index: 10;
}

.node-dot.category {
  width: 12px;
  height: 12px;
  background: white;
  border: 2px solid;
  cursor: pointer !important;
  transition: all 0.3s ease;
}

.node-dot.category:hover {
  transform: scale(1.4);
}

.node-info {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 4px;
  text-align: center;
  white-space: nowrap;
}

.node-title {
  font-size: 11px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 2px;
}

.node-count {
  font-size: 9px;
  color: #64748b;
  font-weight: 500;
}

.memory-nodes {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.memory-dot-wrapper {
  position: absolute;
}

.memory-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  transform: translate(-50%, -50%);
  pointer-events: auto;
}

.memory-dot:hover {
  transform: translate(-50%, -50%) scale(1.6);
}

.memory-label {
  position: absolute;
  left: 50%;
  top: 100%;
  margin-top: 4px;
  font-size: 10px;
  font-weight: 500;
  color: #1e293b;
  white-space: nowrap;
  background: rgba(255, 255, 255, 0.98);
  padding: 3px 8px;
  border-radius: 6px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  pointer-events: none;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  transform-origin: top center;
}

.memory-dot.low {
  background: #6366f1;
  box-shadow: 0 0 0 1px rgba(99, 102, 241, 0.3);
}

.memory-dot.medium {
  background: #f59e0b;
  box-shadow: 0 0 0 1px rgba(245, 158, 11, 0.3);
}

.memory-dot.high {
  background: #ef4444;
  box-shadow: 0 0 0 1px rgba(239, 68, 68, 0.3);
}

.memory-dot.resolved {
  opacity: 0.25;
}

/* Timeline Section */
.timeline-section {
  margin-bottom: 20px;
}

.timeline-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.timeline-group {
  position: relative;
}

.timeline-date {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 600;
  color: #475569;
  background: #f1f5f9;
  padding: 4px 8px;
  border-radius: 6px;
  margin-bottom: 12px;
}

.timeline-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-left: 20px;
  border-left: 2px solid #e2e8f0;
}

.timeline-item {
  display: flex;
  gap: 10px;
  padding: 10px 12px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: -26px;
  top: 50%;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #6366f1;
  border: 2px solid white;
  box-shadow: 0 0 0 2px #e2e8f0;
}

.timeline-item:hover {
  border-color: rgba(99, 102, 241, 0.3);
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  box-shadow: 0 4px 8px rgba(99, 102, 241, 0.08);
}

.timeline-item.resolved {
  opacity: 0.5;
}

.timeline-item.resolved::before {
  background: #cbd5e1;
}

.timeline-marker {
  width: 4px;
  border-radius: 2px;
  flex-shrink: 0;
}

.timeline-marker.low {
  background: #6366f1;
}

.timeline-marker.medium {
  background: #f59e0b;
}

.timeline-marker.high {
  background: #ef4444;
}

.timeline-content {
  flex: 1;
  min-width: 0;
}

.timeline-category {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #6366f1;
  margin-bottom: 4px;
}

.timeline-title {
  font-size: 12px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 4px;
}

.timeline-desc {
  font-size: 11px;
  color: #475569;
  line-height: 1.5;
}

.timeline-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.timeline-item:hover .timeline-actions {
  opacity: 1;
}

.action-btn {
  width: 22px;
  height: 22px;
  border-radius: 5px;
  border: none;
  background: transparent;
  color: #475569;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.action-btn.delete:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

/* Heatmap Section */
.heatmap-section {
  margin-bottom: 20px;
}

.heatmap-container {
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.heatmap-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
}

.heatmap-title {
  font-size: 13px;
  font-weight: 600;
  color: #0f172a;
}

.heatmap-legend {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-label {
  font-size: 10px;
  color: #475569;
  font-weight: 500;
}

.legend-gradient {
  width: 80px;
  height: 12px;
  border-radius: 6px;
  background: linear-gradient(90deg, #f1f5f9 0%, #fde68a 50%, #fecaca 100%);
}

.legend-value {
  font-size: 9px;
  color: #64748b;
}

.heatmap-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 8px;
}

.heatmap-cell {
  padding: 12px;
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.heatmap-cell:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: rgba(99, 102, 241, 0.3);
}

.cell-category {
  font-size: 11px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 6px;
}

.cell-count {
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 4px;
}

.cell-severity {
  font-size: 10px;
  color: #475569;
  margin-bottom: 2px;
}

.cell-unresolved {
  font-size: 10px;
  color: #ef4444;
  font-weight: 600;
}

/* Detail Card */
.detail-card {
  position: fixed;
  background: white;
  border-radius: 8px;
  width: 320px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 0, 0, 0.05);
  z-index: 1000;
  animation: cardFadeIn 0.15s ease;
  transform: translate(-50%, 8px);
}

@keyframes cardFadeIn {
  from {
    opacity: 0;
    transform: translate(-50%, 0);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 8px);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
}

.modal-severity {
  display: flex;
  gap: 3px;
}

.severity-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #e2e8f0;
  transition: all 0.2s ease;
}

.severity-dot.active {
  background: #6366f1;
  box-shadow: 0 0 6px rgba(99, 102, 241, 0.5);
}

.severity-dot.active.medium {
  background: #f59e0b;
  box-shadow: 0 0 6px rgba(245, 158, 11, 0.5);
}

.severity-dot.active.high {
  background: #ef4444;
  box-shadow: 0 0 6px rgba(239, 68, 68, 0.5);
}

.modal-close {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #475569;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.modal-body {
  padding: 20px;
}

.modal-category {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #6366f1;
  margin-bottom: 8px;
}

.modal-question {
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 12px;
  line-height: 1.4;
}

.modal-weakness {
  font-size: 13px;
  color: #475569;
  line-height: 1.6;
  margin-bottom: 12px;
}

.modal-date {
  font-size: 11px;
  color: #64748b;
}

.modal-footer {
  display: flex;
  gap: 8px;
  padding: 16px 20px;
  border-top: 1px solid #f1f5f9;
}

.modal-btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-btn.primary {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.modal-btn.primary:hover {
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
  transform: translateY(-1px);
}

.modal-btn.danger {
  background: #f1f5f9;
  color: #475569;
}

.modal-btn.danger:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

/* Color Picker Popup (Inside Canvas) */
.color-picker-popup {
  position: fixed;
  background: white;
  border-radius: 8px;
  width: 200px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 0, 0, 0.05);
  z-index: 1000;
  animation: cardFadeIn 0.15s ease;
  transform: translate(-50%, 8px);
}

.picker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-bottom: 1px solid #f1f5f9;
}

.picker-category {
  font-size: 12px;
  font-weight: 600;
  color: #0f172a;
}

.picker-close {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: none;
  background: transparent;
  color: #475569;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.picker-close:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.color-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  padding: 12px;
}

.color-option {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.color-option:hover {
  transform: scale(1.15);
  border-color: rgba(0, 0, 0, 0.2);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>
