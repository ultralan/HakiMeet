<template>
  <canvas ref="canvas" class="avatar-canvas"></canvas>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useAvatarScene } from '../composables/useAvatarScene'

const props = defineProps({ speaking: Boolean })
const canvas = ref(null)
const avatar = useAvatarScene(canvas)

onMounted(() => {
  avatar.init()
  window.addEventListener('resize', avatar.resize)
})

onUnmounted(() => {
  window.removeEventListener('resize', avatar.resize)
})

watch(() => props.speaking, (v) => avatar.setSpeaking(v))
</script>

<style scoped>
.avatar-canvas { width: 100%; height: 100%; display: block; }
</style>
