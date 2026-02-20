import { onUnmounted } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'

export function useAvatarScene(canvasEl) {
  let renderer, scene, camera, mixer, clock, frameId
  let headBone = null
  let jawBone = null
  let mesh = null
  let speaking = false

  function init() {
    clock = new THREE.Clock()
    scene = new THREE.Scene()
    scene.background = new THREE.Color(0xf0f0f0)

    camera = new THREE.PerspectiveCamera(30, 1, 0.1, 10)
    camera.position.set(0, 1.55, 0.8)
    camera.lookAt(0, 1.45, 0)

    renderer = new THREE.WebGLRenderer({ canvas: canvasEl.value, antialias: true })
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.outputColorSpace = THREE.SRGBColorSpace

    scene.add(new THREE.AmbientLight(0xffffff, 1.5))
    const dir = new THREE.DirectionalLight(0xffffff, 1)
    dir.position.set(1, 2, 1)
    scene.add(dir)

    loadModel()
    resize()
    animate()
  }

  function loadModel() {
    new GLTFLoader().load('/models/avatar.glb', (gltf) => {
      const model = gltf.scene
      scene.add(model)

      // 查找头骨骼和下巴骨骼
      model.traverse((node) => {
        if (node.isBone) {
          if (node.name === 'Head') headBone = node
          if (node.name === 'Jaw') jawBone = node
        }
        if (node.isMesh && node.morphTargetInfluences) mesh = node
      })

      // 播放内置动画（如果有）
      if (gltf.animations.length) {
        mixer = new THREE.AnimationMixer(model)
        mixer.clipAction(gltf.animations[0]).play()
      }
    }, undefined, (err) => {
      console.warn('GLB 加载失败，请确认 public/models/avatar.glb 存在', err)
    })
  }

  function animate() {
    frameId = requestAnimationFrame(animate)
    const dt = clock.getDelta()
    const t = clock.elapsedTime

    if (mixer) mixer.update(dt)

    // idle: 眨眼
    if (mesh?.morphTargetDictionary) {
      const blinkIdx = mesh.morphTargetDictionary['eyeBlinkLeft'] ?? mesh.morphTargetDictionary['eyeBlink_L']
      const blinkIdxR = mesh.morphTargetDictionary['eyeBlinkRight'] ?? mesh.morphTargetDictionary['eyeBlink_R']
      // 每3秒眨一次，持续0.15秒
      const blinkCycle = t % 3
      const blinkVal = blinkCycle < 0.15 ? 1 : 0
      if (blinkIdx !== undefined) mesh.morphTargetInfluences[blinkIdx] = blinkVal
      if (blinkIdxR !== undefined) mesh.morphTargetInfluences[blinkIdxR] = blinkVal

      // 说话时简单张嘴
      if (speaking) {
        const jawIdx = mesh.morphTargetDictionary['viseme_aa'] ?? mesh.morphTargetDictionary['jawOpen']
        if (jawIdx !== undefined) {
          mesh.morphTargetInfluences[jawIdx] = 0.3 + Math.sin(t * 8) * 0.3
        }
      }
    }

    // idle: 头部微动 + 呼吸
    if (headBone) {
      headBone.rotation.y = Math.sin(t * 0.5) * 0.03
      headBone.rotation.x = Math.sin(t * 0.3) * 0.02
    }

    renderer.render(scene, camera)
  }

  function resize() {
    if (!canvasEl.value || !renderer) return
    const w = canvasEl.value.clientWidth
    const h = canvasEl.value.clientHeight
    renderer.setSize(w, h, false)
    camera.aspect = w / h
    camera.updateProjectionMatrix()
  }

  function setSpeaking(val) { speaking = val }

  function dispose() {
    cancelAnimationFrame(frameId)
    renderer?.dispose()
    scene?.traverse((obj) => {
      if (obj.geometry) obj.geometry.dispose()
      if (obj.material) {
        if (Array.isArray(obj.material)) obj.material.forEach((m) => m.dispose())
        else obj.material.dispose()
      }
    })
  }

  onUnmounted(dispose)
  return { init, resize, setSpeaking, dispose }
}
