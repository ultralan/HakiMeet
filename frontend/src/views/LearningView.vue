<template>
  <div class="learning-page">
    <!-- Header -->
    <header class="page-header">
      <div>
        <h1 class="page-title">学习中心</h1>
        <p class="page-subtitle">追踪你的学习进度和成就</p>
      </div>
    </header>

    <!-- 学习统计概览 -->
    <section class="stats-section">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-header">
            <div class="stat-icon">
              <Clock :size="14" />
            </div>
            <div class="stat-label">总学习时长</div>
          </div>
          <div class="stat-value">{{ totalHours }}<span class="stat-unit">小时</span></div>
          <div class="stat-detail">+2.5h 本周</div>
        </div>


        <div class="stat-card">
          <div class="stat-header">
            <div class="stat-icon streak">
              <Flame :size="14" />
            </div>
            <div class="stat-label">连续打卡</div>
          </div>
          <div class="stat-value">{{ streakDays }}<span class="stat-unit">天</span></div>
          <div class="stat-detail">最长记录 15 天</div>
        </div>

        <div class="stat-card">
          <div class="stat-header">
            <div class="stat-icon success">
              <CheckCircle :size="14" />
            </div>
            <div class="stat-label">完成题目</div>
          </div>
          <div class="stat-value">{{ completedQuestions }}<span class="stat-unit">道</span></div>
          <div class="stat-detail success">通过率 {{ passRate }}%</div>
        </div>

        <div class="stat-card">
          <div class="stat-header">
            <div class="stat-icon danger">
              <TrendingUp :size="14" />
            </div>
            <div class="stat-label">平均分数</div>
          </div>
          <div class="stat-value">{{ avgScore }}<span class="stat-unit">分</span></div>
          <div class="stat-detail success">+5 较上周</div>
        </div>
      </div>
    </section>

    <!-- 学习进度 & 每日目标 -->
    <section class="progress-section">
      <div class="progress-grid">
        <!-- 学习进度 -->
        <div class="progress-card">
          <div class="progress-header">
            <div class="progress-title-group">
              <div class="progress-icon">
                <CheckCircle :size="16" />
              </div>
              <div>
                <h3 class="progress-title">学习进度</h3>
                <p class="progress-subtitle">本周目标完成度</p>
              </div>
            </div>
            <div class="progress-percentage">68%</div>
          </div>

          <div class="progress-list">
            <div v-for="skill in learningProgress" :key="skill.name" class="progress-item">
              <div class="progress-item-header">
                <span class="progress-item-name">{{ skill.name }}</span>
                <span class="progress-item-value">{{ skill.progress }}%</span>
              </div>
              <div class="progress-bar">
                <div class="progress-bar-fill" :class="getProgressClass(skill.progress)" :style="{ width: skill.progress + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 每日目标 -->
        <div class="goals-card">
          <div class="goals-header">
            <div class="goals-title-group">
              <div class="goals-icon">
                <Target :size="16" />
              </div>
              <div>
                <h3 class="goals-title">今日目标</h3>
                <p class="goals-subtitle">{{ dailyGoals.filter(g => g.completed).length }}/{{ dailyGoals.length }} 已完成</p>
              </div>
            </div>
            <button @click="showAddGoal = true" class="add-goal-button">
              <Plus :size="16" />
            </button>
          </div>

          <div class="goals-list">
            <div v-for="goal in dailyGoals" :key="goal.id" class="goal-item" :class="{ completed: goal.completed }">
              <button @click="toggleGoal(goal.id)" class="goal-checkbox" :class="{ checked: goal.completed }">
                <svg v-if="goal.completed" class="check-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                  <path d="M5 13l4 4L19 7"/>
                </svg>
              </button>
              <div class="goal-content">
                <div class="goal-title" :class="{ completed: goal.completed }">{{ goal.title }}</div>
                <div class="goal-desc">{{ goal.desc }}</div>
              </div>
              <button @click="deleteGoal(goal.id)" class="goal-delete">
                <svg class="delete-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 学习曲线 -->
    <section class="curve-section">
      <div class="curve-card">
        <div class="curve-header">
          <div class="curve-title-group">
            <div class="curve-icon">
              <TrendingUp :size="16" />
            </div>
            <div>
              <h3 class="curve-title">学习曲线</h3>
              <p class="curve-subtitle">最近 7 天学习时长趋势</p>
            </div>
          </div>
          <div class="curve-tabs">
            <button class="curve-tab active">7天</button>
            <button class="curve-tab">30天</button>
          </div>
        </div>

        <div class="curve-chart">
          <div class="chart-content">
            <div v-for="(day, i) in learningCurve" :key="i" class="chart-bar-wrapper">
              <div class="chart-bar" :style="{ height: (day.hours / maxHours * 100) + '%' }">
                <div class="bar-fill"></div>
                <div class="bar-tooltip">{{ day.hours }}h</div>
              </div>
              <span class="chart-label">{{ day.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 知识点掌握度 -->
    <section class="knowledge-section">
      <div class="knowledge-grid">
        <div class="knowledge-card">
          <div class="knowledge-header">
            <div class="knowledge-icon">
              <Target :size="16" />
            </div>
            <div>
              <h3 class="knowledge-title">知识点掌握</h3>
              <p class="knowledge-subtitle">各领域掌握程度</p>
            </div>
          </div>

          <div class="knowledge-list">
            <div v-for="topic in knowledgeTopics" :key="topic.name" class="knowledge-item">
              <div class="knowledge-item-header">
                <div class="knowledge-item-info">
                  <span class="knowledge-item-name">{{ topic.name }}</span>
                  <span class="knowledge-level" :class="topic.level">
                    {{ topic.level === 'expert' ? '精通' : topic.level === 'intermediate' ? '熟练' : '入门' }}
                  </span>
                </div>
                <span class="knowledge-item-value">{{ topic.mastery }}%</span>
              </div>
              <div class="knowledge-bar">
                <div class="knowledge-bar-fill" :class="getMasteryClass(topic.mastery)" :style="{ width: topic.mastery + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="weak-card">
          <div class="weak-header">
            <div class="weak-icon">
              <AlertCircle :size="16" />
            </div>
            <div>
              <h3 class="weak-title">薄弱环节</h3>
              <p class="weak-subtitle">需要加强的知识点</p>
            </div>
          </div>

          <div class="weak-list">
            <div v-for="weak in weakPoints" :key="weak.name" class="weak-item">
              <div class="weak-rate">{{ weak.errorRate }}%</div>
              <div class="weak-content">
                <div class="weak-name">{{ weak.name }}</div>
                <div class="weak-errors">错误 {{ weak.errors }} 次</div>
              </div>
              <button class="weak-practice">练习</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 成就徽章 -->
    <section class="achievements-section">
      <div class="achievements-card">
        <div class="achievements-header">
          <div class="achievements-title-group">
            <div class="achievements-icon">
              <Award :size="16" />
            </div>
            <div>
              <h3 class="achievements-title">成就徽章</h3>
              <p class="achievements-subtitle">已解锁 {{ achievements.filter(a => a.unlocked).length }}/{{ achievements.length }}</p>
            </div>
          </div>
          <button class="view-all-button">查看全部</button>
        </div>

        <div class="achievements-grid">
          <div v-for="ach in achievements" :key="ach.id" class="achievement-item" :class="{ unlocked: ach.unlocked }">
            <div class="achievement-badge" :class="{ unlocked: ach.unlocked }">
              <span class="achievement-emoji">{{ ach.icon }}</span>
            </div>
            <div class="achievement-info">
              <div class="achievement-name">{{ ach.name }}</div>
              <div class="achievement-desc">{{ ach.desc }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>

  <!-- 添加目标弹窗 -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="showAddGoal" class="modal-overlay" @click.self="showAddGoal = false">
        <div class="modal-content">
          <div class="modal-header">
            <h3 class="modal-title">添加新目标</h3>
            <button @click="showAddGoal = false" class="modal-close">
              <X :size="16" />
            </button>
          </div>

          <div class="modal-body">
            <div class="form-field">
              <label class="field-label">目标标题</label>
              <input v-model="newGoal.title" placeholder="例如：完成 3 道算法题" class="field-input" />
            </div>
            <div class="form-field">
              <label class="field-label">目标描述</label>
              <input v-model="newGoal.desc" placeholder="例如：已完成 0/3" class="field-input" />
            </div>
          </div>

          <div class="modal-footer">
            <button @click="showAddGoal = false" class="modal-button cancel">取消</button>
            <button @click="addGoal" class="modal-button primary">添加目标</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { CheckCircle, Target, Plus, X, Star, Award, Clock, Flame, TrendingUp, AlertCircle } from 'lucide-vue-next'

const showAddGoal = ref(false)
const newGoal = ref({ title: '', desc: '' })

// 学习统计数据
const totalHours = ref(42)
const streakDays = ref(7)
const completedQuestions = ref(156)
const passRate = ref(78)
const avgScore = ref(82)

// 学习曲线数据
const learningCurve = ref([
  { label: '周一', hours: 2.5 },
  { label: '周二', hours: 1.8 },
  { label: '周三', hours: 3.2 },
  { label: '周四', hours: 2.0 },
  { label: '周五', hours: 2.8 },
  { label: '周六', hours: 4.5 },
  { label: '周日', hours: 3.8 },
])
const maxHours = ref(5)

// 知识点掌握度
const knowledgeTopics = ref([
  { name: '数组与字符串', mastery: 85, level: 'expert' },
  { name: '链表与树', mastery: 72, level: 'intermediate' },
  { name: '动态规划', mastery: 58, level: 'intermediate' },
  { name: '图算法', mastery: 45, level: 'beginner' },
  { name: '系统设计', mastery: 68, level: 'intermediate' },
])

// 薄弱环节
const weakPoints = ref([
  { name: '动态规划-背包问题', errorRate: 65, errors: 8 },
  { name: '图算法-最短路径', errorRate: 58, errors: 6 },
  { name: '二叉树-遍历变种', errorRate: 52, errors: 5 },
])

const learningProgress = ref([
  { name: '算法与数据结构', progress: 75 },
  { name: '系统设计', progress: 45 },
  { name: '行为面试', progress: 88 },
  { name: '编程语言', progress: 62 },
])

const dailyGoals = ref([
  { id: 1, title: '完成 3 道算法题', desc: '已完成 2/3', completed: false },
  { id: 2, title: '模拟面试 1 次', desc: '今日未完成', completed: false },
  { id: 3, title: '复习错题 5 道', desc: '已完成', completed: true },
  { id: 4, title: '学习系统设计', desc: '已完成 30 分钟', completed: true },
])

const achievements = ref([
  { id: 1, name: '初出茅庐', desc: '完成首次面试', icon: '🎯', unlocked: true, color: 'bg-gradient-to-br from-accent to-accent-hover' },
  { id: 2, name: '百题斩', desc: '完成 100 道题', icon: '💯', unlocked: true, color: 'bg-gradient-to-br from-success to-success/80' },
  { id: 3, name: '连胜王', desc: '连续 7 天打卡', icon: '🔥', unlocked: true, color: 'bg-gradient-to-br from-warning to-warning/80' },
  { id: 4, name: '完美主义', desc: '获得满分评价', icon: '⭐', unlocked: false, color: 'bg-gradient-to-br from-warning to-warning/80' },
  { id: 5, name: '算法大师', desc: '算法题通过率 90%', icon: '🧠', unlocked: false, color: 'bg-gradient-to-br from-accent to-accent-hover' },
  { id: 6, name: '面试达人', desc: '完成 50 次面试', icon: '🎓', unlocked: false, color: 'bg-gradient-to-br from-danger to-danger/80' },
])

function toggleGoal(id) {
  const goal = dailyGoals.value.find(g => g.id === id)
  if (goal) goal.completed = !goal.completed
}

function deleteGoal(id) {
  const index = dailyGoals.value.findIndex(g => g.id === id)
  if (index !== -1) dailyGoals.value.splice(index, 1)
}

function addGoal() {
  if (!newGoal.value.title.trim()) return

  dailyGoals.value.push({
    id: Date.now(),
    title: newGoal.value.title,
    desc: newGoal.value.desc || '待完成',
    completed: false
  })

  newGoal.value = { title: '', desc: '' }
  showAddGoal.value = false
}

function getProgressClass(progress) {
  if (progress >= 80) return 'high'
  if (progress >= 50) return 'medium'
  return 'low'
}

function getMasteryClass(mastery) {
  if (mastery >= 80) return 'high'
  if (mastery >= 50) return 'medium'
  return 'low'
}
</script>

<style scoped>
.learning-page {
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
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: skeletonShimmer 1.5s ease-in-out infinite, skeletonFadeOut 0.4s ease 0.5s forwards;
  z-index: 1;
}

.stat-card > * {
  position: relative;
  z-index: 2;
  animation: contentFadeIn 0.3s ease 0.5s backwards;
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

.stat-icon.streak {
  color: #f59e0b;
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

/* Progress Section */
.progress-section {
  margin-bottom: 20px;
}

.progress-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.progress-card {
  padding: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.progress-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.progress-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #10b981;
}

.progress-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.progress-subtitle {
  font-size: 11px;
  color: #475569;
  margin: 2px 0 0 0;
}

.progress-percentage {
  font-size: 20px;
  font-weight: 700;
  color: #10b981;
}

.progress-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.progress-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.progress-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.progress-item-name {
  font-size: 12px;
  font-weight: 600;
  color: #0f172a;
}

.progress-item-value {
  font-size: 11px;
  font-weight: 700;
  color: #475569;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #f1f5f9;
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.progress-bar-fill.high {
  background: linear-gradient(90deg, #10b981 0%, #059669 100%);
}

.progress-bar-fill.medium {
  background: linear-gradient(90deg, #6366f1 0%, #4f46e5 100%);
}

.progress-bar-fill.low {
  background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
}

/* Goals Card */
.goals-card {
  padding: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.goals-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.goals-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.goals-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
}

.goals-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.goals-subtitle {
  font-size: 11px;
  color: #475569;
  margin: 2px 0 0 0;
}

.add-goal-button {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #6366f1;
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.add-goal-button:hover {
  background: #4f46e5;
  transform: scale(1.05);
}

.goals-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.goal-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 10px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  transition: all 0.2s;
}

.goal-item:hover {
  border-color: #6366f1;
}

.goal-item.completed {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  border-color: rgba(16, 185, 129, 0.2);
}

.goal-checkbox {
  width: 20px;
  height: 20px;
  border-radius: 6px;
  background: #e2e8f0;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.goal-checkbox:hover {
  background: #6366f1;
}

.goal-checkbox.checked {
  background: #10b981;
}

.check-icon {
  width: 12px;
  height: 12px;
  color: white;
}

.goal-content {
  flex: 1;
  min-width: 0;
}

.goal-title {
  font-size: 12px;
  font-weight: 600;
  color: #0f172a;
}

.goal-title.completed {
  color: #10b981;
  text-decoration: line-through;
}

.goal-desc {
  font-size: 11px;
  color: #475569;
  margin-top: 2px;
}

.goal-delete {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s;
}

.goal-item:hover .goal-delete {
  opacity: 1;
}

.goal-delete:hover {
  background: #ef4444;
  color: white;
}

.delete-icon {
  width: 14px;
  height: 14px;
}

/* Curve Section */
.curve-section {
  margin-bottom: 20px;
}

.curve-card {
  padding: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.curve-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.curve-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.curve-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
}

.curve-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.curve-subtitle {
  font-size: 11px;
  color: #475569;
  margin: 2px 0 0 0;
}

.curve-tabs {
  display: flex;
  gap: 4px;
  padding: 3px;
  background: #f8fafc;
  border-radius: 6px;
}

.curve-tab {
  padding: 5px 12px;
  border: none;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  color: #475569;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.curve-tab:hover {
  color: #334155;
}

.curve-tab.active {
  color: #6366f1;
  background: white;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.curve-chart {
  position: relative;
  height: 180px;
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
  max-width: 32px;
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

/* Knowledge Section */
.knowledge-section {
  margin-bottom: 20px;
}

.knowledge-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.knowledge-card {
  padding: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.knowledge-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.knowledge-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #10b981;
}

.knowledge-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.knowledge-subtitle {
  font-size: 11px;
  color: #475569;
  margin: 2px 0 0 0;
}

.knowledge-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.knowledge-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.knowledge-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.knowledge-item-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.knowledge-item-name {
  font-size: 12px;
  font-weight: 600;
  color: #0f172a;
}

.knowledge-level {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 700;
}

.knowledge-level.expert {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #16a34a;
}

.knowledge-level.intermediate {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #2563eb;
}

.knowledge-level.beginner {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
}

.knowledge-item-value {
  font-size: 11px;
  font-weight: 700;
  color: #475569;
}

.knowledge-bar {
  width: 100%;
  height: 6px;
  background: #f1f5f9;
  border-radius: 3px;
  overflow: hidden;
}

.knowledge-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.knowledge-bar-fill.high {
  background: linear-gradient(90deg, #10b981 0%, #059669 100%);
}

.knowledge-bar-fill.medium {
  background: linear-gradient(90deg, #6366f1 0%, #4f46e5 100%);
}

.knowledge-bar-fill.low {
  background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
}

/* Weak Card */
.weak-card {
  padding: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.weak-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.weak-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f59e0b;
}

.weak-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.weak-subtitle {
  font-size: 11px;
  color: #475569;
  margin: 2px 0 0 0;
}

.weak-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.weak-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(254, 243, 199, 0.3) 0%, transparent 100%);
  border: 1px solid rgba(245, 158, 11, 0.2);
  transition: all 0.2s;
  cursor: pointer;
}

.weak-item:hover {
  border-color: rgba(245, 158, 11, 0.4);
}

.weak-rate {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(254, 243, 199, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: #f59e0b;
  flex-shrink: 0;
}

.weak-content {
  flex: 1;
  min-width: 0;
}

.weak-name {
  font-size: 12px;
  font-weight: 600;
  color: #0f172a;
}

.weak-errors {
  font-size: 10px;
  color: #475569;
  margin-top: 2px;
}

.weak-practice {
  padding: 6px 12px;
  border-radius: 6px;
  background: #f59e0b;
  color: white;
  border: none;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s;
}

.weak-item:hover .weak-practice {
  opacity: 1;
}

.weak-practice:hover {
  background: #d97706;
}

/* Achievements Section */
.achievements-section {
  margin-bottom: 20px;
}

.achievements-card {
  padding: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.achievements-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.achievements-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.achievements-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f59e0b;
}

.achievements-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.achievements-subtitle {
  font-size: 11px;
  color: #475569;
  margin: 2px 0 0 0;
}

.view-all-button {
  padding: 6px 12px;
  border-radius: 6px;
  background: transparent;
  color: #6366f1;
  border: none;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.view-all-button:hover {
  background: rgba(99, 102, 241, 0.1);
}

.achievements-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
}

.achievement-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 10px;
  border-radius: 10px;
  transition: all 0.2s;
  cursor: pointer;
}

.achievement-item:hover {
  background: #f8fafc;
}

.achievement-item:not(.unlocked) {
  opacity: 0.4;
}

.achievement-badge {
  width: 56px;
  height: 56px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  transition: all 0.3s;
}

.achievement-badge.unlocked {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border: none;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.2);
}

.achievement-item:hover .achievement-badge {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.achievement-emoji {
  font-size: 24px;
}

.achievement-info {
  text-align: center;
}

.achievement-name {
  font-size: 11px;
  font-weight: 700;
  color: #0f172a;
}

.achievement-desc {
  font-size: 10px;
  color: #475569;
  margin-top: 2px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
}

.modal-content {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  border: 1px solid #e2e8f0;
  width: 480px;
  padding: 24px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.modal-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: transparent;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #f1f5f9;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.field-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13px;
  color: #0f172a;
  outline: none;
  transition: all 0.2s;
}

.field-input:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.field-input::placeholder {
  color: #94a3b8;
}

.modal-footer {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.modal-button {
  flex: 1;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.modal-button.cancel {
  background: #f1f5f9;
  color: #475569;
}

.modal-button.cancel:hover {
  background: #e2e8f0;
}

.modal-button.primary {
  background: #6366f1;
  color: white;
}

.modal-button.primary:hover {
  background: #4f46e5;
}

/* Animations */
@keyframes skeletonShimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

@keyframes skeletonFadeOut {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}

@keyframes contentFadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-enter-active, .modal-leave-active {
  transition: all 0.2s ease;
}

.modal-enter-from, .modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: scale(0.95);
}

</style>
