import { onUnmounted } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'

// 15 个 viseme 名称，用于说话时随机驱动
const VISEME_KEYS = [
  'viseme_sil', 'viseme_PP', 'viseme_FF', 'viseme_TH', 'viseme_DD',
  'viseme_kk', 'viseme_CH', 'viseme_SS', 'viseme_nn', 'viseme_RR',
  'viseme_aa', 'viseme_E', 'viseme_I', 'viseme_O', 'viseme_U',
]

export function useAvatarScene(canvasEl) {
  let renderer, scene, camera, clock, frameId
  let speaking = false

  // 模型引用
  let headBone = null, spineBone = null
  let morphMesh = null   // Wolf3D_Avatar mesh
  let morphDict = null   // morphTargetDictionary 缓存

  // viseme 时间轴（未来由后端 rhubarb 推送）
  let visemeTimeline = null
  let visemeStartTime = 0

  // 当前 viseme 权重（用于 lerp 平滑）
  let currentVisemes = new Float32Array(15)

  function init() {
    clock = new THREE.Clock()
    scene = new THREE.Scene()
    scene.background = new THREE.Color(0xf0f1f6)

    camera = new THREE.PerspectiveCamera(30, 1, 0.1, 20)
    camera.position.set(0, 1.75, 1.1)
    camera.lookAt(0, 1.68, 0)

    renderer = new THREE.WebGLRenderer({ canvas: canvasEl.value, antialias: true })
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.outputColorSpace = THREE.SRGBColorSpace
    renderer.toneMapping = THREE.ACESFilmicToneMapping
    renderer.toneMappingExposure = 1.3

    setupLights()
    loadModel()
    resize()
    animate()
  }

  function setupLights() {
    scene.add(new THREE.AmbientLight(0xffffff, 1.5))
    const key = new THREE.DirectionalLight(0xffffff, 2.0)
    key.position.set(1.5, 2.5, 2)
    scene.add(key)
    const fill = new THREE.DirectionalLight(0xe8e0ff, 0.6)
    fill.position.set(-2, 1.5, 1)
    scene.add(fill)
    const rim = new THREE.DirectionalLight(0xddd6fe, 0.4)
    rim.position.set(0, 1, -2)
    scene.add(rim)
  }

  function loadModel() {
    new GLTFLoader().load('/models/avatar.glb', (gltf) => {
      const model = gltf.scene
      scene.add(model)

      model.traverse((node) => {
        if (node.isBone) {
          if (node.name === 'Head') headBone = node
          if (node.name === 'Spine') spineBone = node
        }
        if (node.isMesh && node.morphTargetInfluences) {
          morphMesh = node
          morphDict = node.morphTargetDictionary
        }
      })
    }, undefined, (err) => {
      console.warn('GLB 加载失败:', err)
    })
  }

  // ── 动画循环 ──
  function animate() {
    frameId = requestAnimationFrame(animate)
    const dt = clock.getDelta()
    const t = clock.elapsedTime
    if (!morphMesh) { renderer.render(scene, camera); return }

    animateBlink(t)
    animateIdle(t)
    animateMouth(t, dt)

    renderer.render(scene, camera)
  }

  // 眨眼：随机间隔 3~5 秒
  let nextBlink = 2
  function animateBlink(t) {
    const blinkL = morphDict['eyeBlinkLeft']
    const blinkR = morphDict['eyeBlinkRight']
    if (blinkL == null) return

    const inf = morphMesh.morphTargetInfluences
    if (t >= nextBlink) {
      inf[blinkL] = 1; inf[blinkR] = 1
      if (t >= nextBlink + 0.15) {
        inf[blinkL] = 0; inf[blinkR] = 0
        nextBlink = t + 3 + Math.random() * 2
      }
    }
  }

  // 头部微动 + 呼吸
  function animateIdle(t) {
    if (headBone) {
      headBone.rotation.y = Math.sin(t * 0.5) * 0.03
      headBone.rotation.x = Math.sin(t * 0.3) * 0.02
    }
    if (spineBone) {
      spineBone.scale.y = 1 + Math.sin(t * 1.2) * 0.003
    }
  }

  // 口型动画
  function animateMouth(t, dt) {
    const inf = morphMesh.morphTargetInfluences
    const lerpSpeed = 12 * dt  // 平滑系数

    if (speaking && visemeTimeline) {
      // 模式 A：后端推送的 viseme 时间轴
      driveFromTimeline(t, inf, lerpSpeed)
    } else if (speaking) {
      // 模式 B：无时间轴时，程序化模拟口型
      driveProceduralMouth(t, inf, lerpSpeed)
    } else {
      // 静默：所有 viseme 归零
      for (let i = 0; i < VISEME_KEYS.length; i++) {
        const idx = morphDict[VISEME_KEYS[i]]
        if (idx != null) {
          currentVisemes[i] = lerp(currentVisemes[i], 0, lerpSpeed)
          inf[idx] = currentVisemes[i]
        }
      }
    }
  }

  // 从 viseme 时间轴驱动（未来 rhubarb 接入用）
  function driveFromTimeline(t, inf, lerpSpeed) {
    const elapsed = t - visemeStartTime
    // 找当前 cue
    let cue = null
    for (const c of visemeTimeline) {
      if (elapsed >= c.start && elapsed < c.end) { cue = c; break }
    }
    for (let i = 0; i < VISEME_KEYS.length; i++) {
      const idx = morphDict[VISEME_KEYS[i]]
      if (idx == null) continue
      const target = (cue && VISEME_KEYS[i] === `viseme_${cue.value}`) ? 1 : 0
      currentVisemes[i] = lerp(currentVisemes[i], target, lerpSpeed)
      inf[idx] = currentVisemes[i]
    }
  }

  // 程序化口型模拟（说话时自然感）
  function driveProceduralMouth(t, inf, lerpSpeed) {
    // 用多个正弦波叠加模拟自然说话节奏
    const base = Math.sin(t * 7) * 0.5 + 0.5
    const vary = Math.sin(t * 11.3) * 0.3 + Math.sin(t * 4.7) * 0.2

    // 主要驱动 jawOpen + 几个元音 viseme 交替
    const jawIdx = morphDict['jawOpen']
    if (jawIdx != null) inf[jawIdx] = base * 0.5

    // 在元音 viseme 之间切换
    const vowels = ['viseme_aa', 'viseme_E', 'viseme_I', 'viseme_O', 'viseme_U']
    const pick = Math.floor((t * 5) % vowels.length)
    for (let i = 0; i < VISEME_KEYS.length; i++) {
      const idx = morphDict[VISEME_KEYS[i]]
      if (idx == null) continue
      let target = 0
      if (VISEME_KEYS[i] === vowels[pick]) target = (base + vary) * 0.6
      currentVisemes[i] = lerp(currentVisemes[i], target, lerpSpeed)
      inf[idx] = currentVisemes[i]
    }
  }

  function lerp(a, b, t) { return a + (b - a) * Math.min(t, 1) }

  // ── 公共 API ──
  function resize() {
    if (!canvasEl.value || !renderer) return
    const w = canvasEl.value.clientWidth
    const h = canvasEl.value.clientHeight
    renderer.setSize(w, h, false)
    camera.aspect = w / h
    camera.updateProjectionMatrix()
  }

  function setSpeaking(val) { speaking = val }

  // 未来接入：后端推送 viseme 时间轴时调用
  function setVisemes(timeline) {
    visemeTimeline = timeline
    visemeStartTime = clock.elapsedTime
  }

  function dispose() {
    cancelAnimationFrame(frameId)
    renderer?.dispose()
    scene?.traverse((obj) => {
      if (obj.geometry) obj.geometry.dispose()
      if (obj.material) {
        const mats = Array.isArray(obj.material) ? obj.material : [obj.material]
        mats.forEach((m) => m.dispose())
      }
    })
  }

  onUnmounted(dispose)
  return { init, resize, setSpeaking, setVisemes, dispose }
}
