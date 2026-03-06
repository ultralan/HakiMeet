<template>
  <div class="flex h-screen bg-bg" v-if="showLayout">
    <!-- Sidebar -->
    <aside class="w-64 shrink-0 bg-surface flex flex-col border-r border-border relative">
      <!-- 顶部渐变装饰 -->
      <div class="absolute top-0 left-0 right-0 h-32 bg-gradient-to-b from-accent-softer to-transparent pointer-events-none"></div>

      <div class="px-4 py-5 relative">
        <router-link to="/" class="flex items-center gap-3 no-underline group">
          <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-accent to-accent-hover flex items-center justify-center shadow-sm group-hover:shadow-md transition-all duration-300">
            <span class="text-white text-sm font-bold tracking-tight">H</span>
          </div>
          <div class="flex flex-col">
            <span class="text-text font-bold text-[15px] tracking-tight">HakiMeet</span>
            <span class="text-text-muted text-[11px] font-medium">AI 模拟面试</span>
          </div>
        </router-link>
      </div>

      <!-- Quick Stats -->
      <div class="px-4 mb-3 relative">
        <div class="stat-mini-card">
          <div class="flex items-center justify-between mb-2">
            <span class="stat-mini-label">本周练习</span>
            <span class="stat-mini-value">{{ weekStats.count }}</span>
          </div>
          <div class="flex items-center gap-3 text-[11px]">
            <div class="flex items-center gap-1 text-text-muted">
              <Target :size="11" />
              <span>{{ weekStats.avgScore }}分</span>
            </div>
            <div class="flex items-center gap-1 text-success">
              <TrendingUp :size="11" />
              <span>+{{ weekStats.improvement }}%</span>
            </div>
          </div>
        </div>
      </div>

      <nav class="flex-1 px-4 space-y-1 relative">
        <router-link v-for="item in navItems" :key="item.to" :to="item.to"
          class="nav-link" active-class="nav-active">
          <component :is="item.icon" :size="18" />
          <span class="flex-1">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="px-4 py-3 border-t border-border mx-4 mb-2 relative">
        <div class="flex items-center gap-2.5 p-2 rounded-lg hover:bg-surface-hover transition-all duration-200 cursor-pointer group">
          <div class="w-8 h-8 rounded-full bg-gradient-to-br from-accent/30 via-accent/10 to-transparent flex items-center justify-center ring-1 ring-accent-soft group-hover:ring-accent/20 transition-all">
            <span class="text-accent text-[11px] font-bold">U</span>
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-text text-[12px] font-semibold leading-tight">访客用户</div>
            <div class="text-text-muted text-[10px] font-medium">免费版 · 已用 3/10 次</div>
          </div>
          <svg class="w-3.5 h-3.5 text-text-muted opacity-0 group-hover:opacity-100 transition-opacity" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 18l6-6-6-6"/>
          </svg>
        </div>
      </div>
    </aside>

    <!-- Main -->
    <main class="flex-1 overflow-auto bg-bg">
      <router-view />
    </main>
  </div>

  <router-view v-else />

  <!-- Global confirm modal -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modal.state.show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
        <div class="bg-surface rounded-2xl shadow-xl border border-border w-80 p-6">
          <p class="text-sm text-text leading-relaxed">{{ modal.state.msg }}</p>
          <div class="flex gap-2 mt-5 justify-end">
            <button @click="modal.handle(false)"
              class="px-4 py-2 rounded-xl text-xs text-text-secondary border border-border hover:bg-surface-hover transition">取消</button>
            <button @click="modal.handle(true)"
              class="px-4 py-2 rounded-xl text-xs font-semibold transition"
              :class="modal.state.danger ? 'bg-danger text-white hover:bg-danger/80' : 'bg-accent text-white hover:bg-accent-hover'">
              确定
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useConfirm } from './composables/useConfirm'
import { Home, GraduationCap, BookOpen, History, FileText, Shield, Settings, Target, TrendingUp } from 'lucide-vue-next'

const modal = useConfirm()

const route = useRoute()
const showLayout = computed(() => !route.path.startsWith('/interview'))

const weekStats = ref({
  count: 12,
  avgScore: 78,
  improvement: 15
})

const navItems = [
  { to: '/', label: '仪表盘', icon: Home },
  { to: '/learning', label: '学习中心', icon: GraduationCap },
  { to: '/question-bank', label: '题库管理', icon: BookOpen },
  { to: '/history', label: '面试记录', icon: History },
  { to: '/resume', label: '简历管理', icon: FileText },
  { to: '/memory', label: '长期记忆', icon: Shield },
  { to: '/settings', label: '模型配置', icon: Settings },
]
</script>

<style>
.modal-enter-active, .modal-leave-active { transition: all 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from > div, .modal-leave-to > div { transform: scale(0.95); }
</style>

<style scoped>
/* Quick Stats Card */
.stat-mini-card {
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.stat-mini-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #94a3b8;
}

.stat-mini-value {
  font-size: 20px;
  font-weight: 700;
  color: #6366f1;
  line-height: 1;
}

/* Navigation */
.nav-link {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.625rem 0.875rem;
  border-radius: 0.625rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.nav-link::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--color-accent);
  transform: scaleY(0);
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 0 2px 2px 0;
}

.nav-link:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

.nav-link:hover::before {
  transform: scaleY(0.5);
}

.nav-active {
  background: linear-gradient(135deg, var(--color-accent-soft) 0%, var(--color-accent-softer) 100%);
  color: var(--color-accent);
  font-weight: 600;
  box-shadow: var(--shadow-xs);
}

.nav-active::before {
  transform: scaleY(1);
}

.nav-active:hover {
  background: linear-gradient(135deg, var(--color-accent-soft) 0%, var(--color-accent-softer) 100%);
}
</style>
