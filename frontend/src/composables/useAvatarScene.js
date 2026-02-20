import { onUnmounted } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'

export function useAvatarScene(canvasEl) {
  let renderer, scene, camera, mixer, clock, frameId
  let headBone = null
  let jawBone = null
  let mesh = null
  let speaking = false
  let fallbackJaw = null

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
      console.warn('GLB 加载失败，使用备用头像', err)
      createFallbackAvatar()
    })
  }

  function createFallbackAvatar() {
    const skin = new THREE.MeshStandardMaterial({ color: 0xf5cba7 })
    const group = new THREE.Group()
    group.position.y = 1.05

    // 头
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.18, 32, 32), skin)
    head.position.y = 0.42
    head.scale.set(1, 1.15, 1)
    group.add(head)
    headBone = head

    // 身体
    const body = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.22, 0.45, 32), new THREE.MeshStandardMaterial({ color: 0x3b82f6 }))
    body.position.y = 0.05
    group.add(body)

    // 脖子
    const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.07, 0.08, 16), skin)
    neck.position.y = 0.3
    group.add(neck)

    // 眼睛
    const eyeMat = new THREE.MeshStandardMaterial({ color: 0x333333 })
    const eyeGeo = new THREE.SphereGeometry(0.025, 16, 16)
    const eyeL = new THREE.Mesh(eyeGeo, eyeMat)
    eyeL.position.set(-0.06, 0.45, 0.15)
    const eyeR = new THREE.Mesh(eyeGeo, eyeMat)
    eyeR.position.set(0.06, 0.45, 0.15)
    group.add(eyeL, eyeR)

    // 嘴巴（用于说话动画）
    fallbackJaw = new THREE.Mesh(new THREE.SphereGeometry(0.04, 16, 8, 0, Math.PI * 2, 0, Math.PI / 2), new THREE.MeshStandardMaterial({ color: 0xc0392b }))
    fallbackJaw.position.set(0, 0.37, 0.14)
    fallbackJaw.scale.set(1, 0.3, 0.5)
    group.add(fallbackJaw)

    scene.add(group)
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

    // fallback 嘴巴说话动画
    if (fallbackJaw) {
      fallbackJaw.scale.y = speaking ? 0.3 + Math.sin(t * 8) * 0.25 : 0.3
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
