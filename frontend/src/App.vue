<template>
  <div class="flex h-screen bg-bg" v-if="showLayout">
    <!-- Sidebar -->
    <aside class="w-56 shrink-0 bg-surface flex flex-col border-r border-border/60">
      <div class="px-5 py-6">
        <router-link to="/" class="flex items-center gap-2.5 no-underline group">
          <div class="w-8 h-8 rounded-[10px] bg-accent flex items-center justify-center shadow-sm group-hover:shadow-md transition-shadow">
            <span class="text-white text-xs font-bold tracking-tight">H</span>
          </div>
          <span class="text-text font-semibold text-[15px]">HakiMeet</span>
        </router-link>
      </div>

      <nav class="flex-1 px-3 space-y-0.5">
        <router-link v-for="item in navItems" :key="item.to" :to="item.to"
          class="nav-link" active-class="nav-active">
          <component :is="item.icon" />
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="px-4 py-4 border-t border-border/60 mx-3 mb-2">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-full bg-gradient-to-br from-accent/20 to-accent/5 flex items-center justify-center">
            <span class="text-accent text-[11px] font-semibold">U</span>
          </div>
          <div>
            <div class="text-text text-[13px] font-medium leading-tight">访客用户</div>
            <div class="text-text-muted text-[11px]">免费版</div>
          </div>
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
import { computed, h } from 'vue'
import { useRoute } from 'vue-router'
import { useConfirm } from './composables/useConfirm'

const modal = useConfirm()

const route = useRoute()
const showLayout = computed(() => !route.path.startsWith('/interview'))

const Icon = (paths) => () => h('svg', {
  class: 'w-[16px] h-[16px] shrink-0', viewBox: '0 0 24 24', fill: 'none',
  stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linecap': 'round', 'stroke-linejoin': 'round'
}, paths.map(d => h('path', { d })))

const navItems = [
  { to: '/', label: '仪表盘', icon: Icon(['M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z', 'M9 22V12h6v10']) },
  { to: '/resume', label: '简历管理', icon: Icon(['M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z', 'M14 2v6h6', 'M16 13H8', 'M16 17H8', 'M10 9H8']) },
  { to: '/question-bank', label: '题库管理', icon: Icon(['M4 19.5A2.5 2.5 0 016.5 17H20', 'M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z']) },
  { to: '/history', label: '面试记录', icon: Icon(['M12 8v4l3 3', 'M3.05 11a9 9 0 1118 2 9 9 0 01-18-2z']) },
]
</script>

<style>
.modal-enter-active, .modal-leave-active { transition: all 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from > div, .modal-leave-to > div { transform: scale(0.95); }
</style>

<style scoped>
.nav-link {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.5rem 0.85rem;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: all 0.2s ease;
}
.nav-link:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}
.nav-active {
  background: var(--color-accent-soft);
  color: var(--color-accent);
  box-shadow: inset 3px 0 0 var(--color-accent);
}
</style>
