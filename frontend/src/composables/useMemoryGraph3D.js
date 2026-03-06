import { ref, shallowRef } from 'vue'
import * as THREE from 'three'
import { CSS2DRenderer, CSS2DObject } from 'three/examples/jsm/renderers/CSS2DRenderer.js'

export function useMemoryGraph3D(containerRef, data, onNodeClick) {
  const scene = shallowRef(null)
  const camera = shallowRef(null)
  const renderer = shallowRef(null)
  const labelRenderer = shallowRef(null)
  const nodes = shallowRef([])
  const isDragging = ref(false)
  const previousMousePosition = ref({ x: 0, y: 0 })

  // 颜色映射
  const getSeverityColor = (severity) => {
    if (severity >= 4) return 0xef4444 // 红色
    if (severity >= 3) return 0xf59e0b // 橙色
    return 0x6366f1 // 蓝色
  }

  const getCategoryColor = (index) => {
    const colors = [0x6366f1, 0x8b5cf6, 0xec4899, 0xf59e0b, 0x10b981, 0x06b6d4]
    return colors[index % colors.length]
  }

  // 创建星空背景
  const createStarfield = () => {
    const starsGeometry = new THREE.BufferGeometry()
    const starCount = 2000
    const positions = new Float32Array(starCount * 3)
    const colors = new Float32Array(starCount * 3)
    const sizes = new Float32Array(starCount)

    for (let i = 0; i < starCount; i++) {
      // 随机位置(球形分布)
      const radius = 50 + Math.random() * 50
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos(2 * Math.random() - 1)

      positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta)
      positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta)
      positions[i * 3 + 2] = radius * Math.cos(phi)

      // 随机颜色(蓝白紫金)
      const colorChoice = Math.random()
      if (colorChoice < 0.6) {
        colors[i * 3] = 0.8 + Math.random() * 0.2
        colors[i * 3 + 1] = 0.8 + Math.random() * 0.2
        colors[i * 3 + 2] = 1.0
      } else if (colorChoice < 0.85) {
        colors[i * 3] = 0.6 + Math.random() * 0.4
        colors[i * 3 + 1] = 0.4 + Math.random() * 0.3
        colors[i * 3 + 2] = 1.0
      } else {
        colors[i * 3] = 1.0
        colors[i * 3 + 1] = 0.8 + Math.random() * 0.2
        colors[i * 3 + 2] = 0.3
      }

      sizes[i] = Math.random() * 2 + 0.5
    }

    starsGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    starsGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))
    starsGeometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1))

    const starsMaterial = new THREE.PointsMaterial({
      size: 0.1,
      vertexColors: true,
      transparent: true,
      opacity: 0.8,
      sizeAttenuation: true,
      blending: THREE.AdditiveBlending
    })

    const starField = new THREE.Points(starsGeometry, starsMaterial)
    scene.value.add(starField)
    return starField
  }

  // 初始化场景
  const initScene = () => {
    if (!containerRef.value) return

    // 创建场景
    scene.value = new THREE.Scene()
    scene.value.background = new THREE.Color(0x0a0a1a)
    scene.value.fog = new THREE.FogExp2(0x0a0a1a, 0.015)

    // 添加星空背景
    createStarfield()

    // 创建相机
    const width = containerRef.value.clientWidth
    const height = containerRef.value.clientHeight
    camera.value = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000)
    camera.value.position.z = 15

    // 创建渲染器
    renderer.value = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    renderer.value.setSize(width, height)
    renderer.value.setPixelRatio(window.devicePixelRatio)
    containerRef.value.appendChild(renderer.value.domElement)

    // 创建标签渲染器
    labelRenderer.value = new CSS2DRenderer()
    labelRenderer.value.setSize(width, height)
    labelRenderer.value.domElement.style.position = 'absolute'
    labelRenderer.value.domElement.style.top = '0'
    labelRenderer.value.domElement.style.pointerEvents = 'none'
    containerRef.value.appendChild(labelRenderer.value.domElement)

    // 添加环境光
    const ambientLight = new THREE.AmbientLight(0x4a5f8f, 0.3)
    scene.value.add(ambientLight)

    // 添加主光源(模拟远处的恒星)
    const mainLight = new THREE.DirectionalLight(0x8fa5d4, 0.8)
    mainLight.position.set(10, 10, 10)
    scene.value.add(mainLight)

    // 添加辅助光源(紫色调)
    const accentLight = new THREE.PointLight(0x9d7bea, 0.6, 30)
    accentLight.position.set(-8, 5, -8)
    scene.value.add(accentLight)

    // 中心发光点(知识核心)
    const coreLight = new THREE.PointLight(0x6366f1, 1.5, 15)
    coreLight.position.set(0, 0, 0)
    scene.value.add(coreLight)
  }

  // 创建文字标签
  const createLabel = (text, className = 'node-label') => {
    const div = document.createElement('div')
    div.className = className
    div.textContent = text
    div.style.cssText = `
      color: #e0e7ff;
      font-size: 10px;
      font-weight: 600;
      padding: 3px 7px;
      background: rgba(15, 23, 42, 0.85);
      border-radius: 4px;
      border: 1px solid rgba(99, 102, 241, 0.4);
      box-shadow: 0 0 12px rgba(99, 102, 241, 0.3), 0 2px 8px rgba(0, 0, 0, 0.4);
      white-space: nowrap;
      pointer-events: none;
      backdrop-filter: blur(8px);
      text-shadow: 0 0 8px rgba(99, 102, 241, 0.5);
    `
    return new CSS2DObject(div)
  }

  // 创建节点
  const createNodes = () => {
    if (!scene.value || !data.value) return

    // 清除旧节点
    nodes.value.forEach(node => scene.value.remove(node.mesh))
    nodes.value = []

    // 创建中心节点(发光星球)
    const centerGeometry = new THREE.SphereGeometry(1, 32, 32)
    const centerMaterial = new THREE.MeshPhongMaterial({
      color: 0x6366f1,
      emissive: 0x6366f1,
      emissiveIntensity: 0.8,
      shininess: 100,
      transparent: true,
      opacity: 0.95
    })
    const centerMesh = new THREE.Mesh(centerGeometry, centerMaterial)
    centerMesh.userData = { type: 'center', label: '知识图谱' }
    scene.value.add(centerMesh)

    // 添加外层光晕
    const glowGeometry = new THREE.SphereGeometry(1.3, 32, 32)
    const glowMaterial = new THREE.MeshBasicMaterial({
      color: 0x6366f1,
      transparent: true,
      opacity: 0.15,
      side: THREE.BackSide
    })
    const glowMesh = new THREE.Mesh(glowGeometry, glowMaterial)
    centerMesh.add(glowMesh)

    // 添加中心节点标签(调整位置到上方)
    const centerLabel = createLabel('知识图谱', 'center-label')
    centerLabel.position.set(0, 2.0, 0)
    centerLabel.element.style.fontSize = '12px'
    centerLabel.element.style.fontWeight = '700'
    centerLabel.element.style.background = 'rgba(99, 102, 241, 0.9)'
    centerLabel.element.style.color = '#ffffff'
    centerLabel.element.style.borderColor = 'rgba(79, 70, 229, 0.8)'
    centerLabel.element.style.boxShadow = '0 0 16px rgba(99, 102, 241, 0.6), 0 2px 8px rgba(0, 0, 0, 0.4)'
    centerMesh.add(centerLabel)

    nodes.value.push({ mesh: centerMesh, type: 'center' })

    // 创建类别节点和记忆点
    const categories = Object.entries(data.value)
    const categoryCount = categories.length

    categories.forEach(([category, items], catIndex) => {
      // 类别节点位置(围绕中心)
      const angle = (catIndex / categoryCount) * Math.PI * 2
      const radius = 5
      const catX = Math.cos(angle) * radius
      const catY = Math.sin(angle) * radius
      const catZ = (Math.random() - 0.5) * 2

      // 创建类别节点(发光星球)
      const catGeometry = new THREE.SphereGeometry(0.6, 24, 24)
      const catColor = getCategoryColor(catIndex)
      const catMaterial = new THREE.MeshPhongMaterial({
        color: catColor,
        emissive: catColor,
        emissiveIntensity: 0.7,
        shininess: 80,
        transparent: true,
        opacity: 0.9
      })
      const catMesh = new THREE.Mesh(catGeometry, catMaterial)
      catMesh.position.set(catX, catY, catZ)
      catMesh.userData = { type: 'category', label: category, items }
      scene.value.add(catMesh)

      // 添加类别光晕
      const catGlowGeometry = new THREE.SphereGeometry(0.85, 24, 24)
      const catGlowMaterial = new THREE.MeshBasicMaterial({
        color: catColor,
        transparent: true,
        opacity: 0.12,
        side: THREE.BackSide
      })
      const catGlowMesh = new THREE.Mesh(catGlowGeometry, catGlowMaterial)
      catMesh.add(catGlowMesh)

      // 添加类别标签(调整到侧上方)
      const catLabel = createLabel(category, 'category-label')
      catLabel.position.set(0, 1.2, 0)
      catMesh.add(catLabel)

      nodes.value.push({ mesh: catMesh, type: 'category', category })

      // 从中心到类别的连接线(星际轨道)
      const centerLine = new THREE.Line(
        new THREE.BufferGeometry().setFromPoints([
          new THREE.Vector3(0, 0, 0),
          new THREE.Vector3(catX, catY, catZ)
        ]),
        new THREE.LineBasicMaterial({
          color: catColor,
          opacity: 0.25,
          transparent: true,
          blending: THREE.AdditiveBlending
        })
      )
      scene.value.add(centerLine)

      // 创建记忆点节点(围绕类别,限制数量优化性能)
      items.slice(0, 6).forEach((item, itemIndex) => {
        const itemAngle = (itemIndex / Math.min(items.length, 6)) * Math.PI * 2
        const itemRadius = 1.5
        const itemX = catX + Math.cos(itemAngle) * itemRadius
        const itemY = catY + Math.sin(itemAngle) * itemRadius
        const itemZ = catZ + (Math.random() - 0.5) * 1

        const itemColor = getSeverityColor(item.severity)
        const itemGeometry = new THREE.SphereGeometry(0.15, 12, 12)
        const itemMaterial = new THREE.MeshPhongMaterial({
          color: itemColor,
          emissive: itemColor,
          emissiveIntensity: item.resolved ? 0.3 : 0.6,
          opacity: item.resolved ? 0.4 : 0.95,
          transparent: true
        })
        const itemMesh = new THREE.Mesh(itemGeometry, itemMaterial)
        itemMesh.position.set(itemX, itemY, itemZ)
        itemMesh.userData = { type: 'item', data: item, category }
        scene.value.add(itemMesh)
        nodes.value.push({ mesh: itemMesh, type: 'item', item, category })

        // 从类别到记忆点的连接线(更细,更透明)
        const itemLine = new THREE.Line(
          new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(catX, catY, catZ),
            new THREE.Vector3(itemX, itemY, itemZ)
          ]),
          new THREE.LineBasicMaterial({
            color: itemColor,
            opacity: item.resolved ? 0.08 : 0.15,
            transparent: true,
            blending: THREE.AdditiveBlending
          })
        )
        scene.value.add(itemLine)
      })
    })
  }

  // 动画循环(优化性能)
  let frameCount = 0
  const animate = () => {
    if (!scene.value || !camera.value || !renderer.value) return

    requestAnimationFrame(animate)
    frameCount++

    // 自动旋转(缓慢)
    if (!isDragging.value) {
      scene.value.rotation.y += 0.0005
    }

    // 节点浮动动画(每3帧更新一次,减少计算)
    if (frameCount % 3 === 0) {
      const time = Date.now() * 0.0008
      nodes.value.forEach((node, index) => {
        if (node.type === 'item') {
          const offset = Math.sin(time + index * 0.5) * 0.002
          node.mesh.position.y += offset
        }
      })
    }

    renderer.value.render(scene.value, camera.value)
    if (labelRenderer.value) {
      labelRenderer.value.render(scene.value, camera.value)
    }
  }

  // 鼠标事件
  const onMouseDown = (e) => {
    isDragging.value = true
    previousMousePosition.value = { x: e.clientX, y: e.clientY }
  }

  const onMouseMove = (e) => {
    if (!isDragging.value || !scene.value) return

    const deltaX = e.clientX - previousMousePosition.value.x
    const deltaY = e.clientY - previousMousePosition.value.y

    scene.value.rotation.y += deltaX * 0.005
    scene.value.rotation.x += deltaY * 0.005

    previousMousePosition.value = { x: e.clientX, y: e.clientY }
  }

  const onMouseUp = () => {
    isDragging.value = false
  }

  const onMouseClick = (e) => {
    if (!camera.value || !scene.value || !containerRef.value) return

    const rect = containerRef.value.getBoundingClientRect()
    const mouse = new THREE.Vector2(
      ((e.clientX - rect.left) / rect.width) * 2 - 1,
      -((e.clientY - rect.top) / rect.height) * 2 + 1
    )

    const raycaster = new THREE.Raycaster()
    raycaster.setFromCamera(mouse, camera.value)

    const intersects = raycaster.intersectObjects(
      nodes.value.map(n => n.mesh)
    )

    if (intersects.length > 0) {
      const clickedNode = intersects[0].object
      if (clickedNode.userData.type === 'item' && onNodeClick) {
        onNodeClick(clickedNode.userData.data)
      }
    }
  }

  const onWheel = (e) => {
    if (!camera.value) return
    e.preventDefault()
    camera.value.position.z += e.deltaY * 0.01
    camera.value.position.z = Math.max(8, Math.min(25, camera.value.position.z))
  }

  // 窗口大小调整
  const onResize = () => {
    if (!containerRef.value || !camera.value || !renderer.value) return

    const width = containerRef.value.clientWidth
    const height = containerRef.value.clientHeight

    camera.value.aspect = width / height
    camera.value.updateProjectionMatrix()
    renderer.value.setSize(width, height)

    if (labelRenderer.value) {
      labelRenderer.value.setSize(width, height)
    }
  }

  // 清理
  const cleanup = () => {
    if (renderer.value && containerRef.value) {
      containerRef.value.removeChild(renderer.value.domElement)
    }
    if (labelRenderer.value && containerRef.value) {
      containerRef.value.removeChild(labelRenderer.value.domElement)
    }
    if (renderer.value) {
      renderer.value.dispose()
    }
    nodes.value = []
  }

  // 初始化函数
  const init = () => {
    if (!containerRef.value) return

    initScene()
    createNodes()
    animate()

    // 添加事件监听
    containerRef.value.addEventListener('mousedown', onMouseDown)
    containerRef.value.addEventListener('mousemove', onMouseMove)
    containerRef.value.addEventListener('mouseup', onMouseUp)
    containerRef.value.addEventListener('click', onMouseClick)
    containerRef.value.addEventListener('wheel', onWheel, { passive: false })
    window.addEventListener('resize', onResize)
  }

  // 销毁函数
  const destroy = () => {
    // 移除事件监听
    if (containerRef.value) {
      containerRef.value.removeEventListener('mousedown', onMouseDown)
      containerRef.value.removeEventListener('mousemove', onMouseMove)
      containerRef.value.removeEventListener('mouseup', onMouseUp)
      containerRef.value.removeEventListener('click', onMouseClick)
      containerRef.value.removeEventListener('wheel', onWheel)
    }
    window.removeEventListener('resize', onResize)
    cleanup()
  }

  return {
    init,
    destroy,
    createNodes,
    nodes
  }
}
