# 3D 数字人设计

## 技术方案

```
AI文字回复
    │
    ▼
Edge-TTS 合成音频(MP3)
    │
    ▼
rhubarb-lip-sync 分析音频 → viseme时间轴
    │
    ▼
WebSocket 推送: { audio_chunks, viseme_timeline }
    │
    ▼
前端 Three.js 渲染:
  - 播放音频
  - 根据viseme时间轴驱动模型blendshapes(口型)
  - 叠加idle动画(眨眼、微动)
```

## 1. 3D 模型

### 1.1 模型来源：Ready Player Me

- 免费生成半身像 GLB 模型
- 自带 ARKit 兼容的 52 个 blendshapes（含口型、表情）
- 模型大小约 2-5MB，浏览器加载无压力

### 1.2 关键 Blendshapes（口型相关）

| Viseme | 对应音素 | Blendshape 名称 |
|--------|---------|-----------------|
| sil | 静音 | viseme_sil |
| PP | p, b, m | viseme_PP |
| FF | f, v | viseme_FF |
| TH | th | viseme_TH |
| DD | d, t, n | viseme_DD |
| kk | k, g | viseme_kk |
| CH | ch, j, sh | viseme_CH |
| SS | s, z | viseme_SS |
| nn | n, l | viseme_nn |
| RR | r | viseme_RR |
| aa | a | viseme_aa |
| E | e | viseme_E |
| I | i | viseme_I |
| O | o | viseme_O |
| U | u | viseme_U |

## 2. 口型同步流程

### 2.1 后端：音频 → Viseme 时间轴

```python
# 使用 rhubarb-lip-sync (需预编译二进制)
# 输入: WAV音频文件
# 输出: JSON viseme时间轴

import subprocess, json

async def generate_visemes(audio_path: str) -> list[dict]:
    """调用rhubarb生成viseme时间轴"""
    result = subprocess.run(
        ["rhubarb", "-f", "json", "--machineReadable", audio_path],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    # 返回格式: [{"start": 0.0, "end": 0.15, "value": "A"}, ...]
    return data["mouthCues"]
```

### 2.2 前端：驱动 Blendshapes

```javascript
// 核心逻辑：根据当前播放时间查找对应viseme，设置blendshape权重
class LipSyncController {
  constructor(model) {
    this.mesh = model.scene.getObjectByName('Wolf3D_Head')
    this.visemes = []
    this.currentTime = 0
  }

  update(deltaTime) {
    this.currentTime += deltaTime
    const cue = this.getCurrentViseme()

    // 重置所有viseme blendshapes
    this.resetVisemes()

    if (cue) {
      const index = this.mesh.morphTargetDictionary[`viseme_${cue.value}`]
      if (index !== undefined) {
        // 平滑过渡，避免口型跳变
        this.mesh.morphTargetInfluences[index] = THREE.MathUtils.lerp(
          this.mesh.morphTargetInfluences[index], 1.0, 0.3
        )
      }
    }
  }
}
```

## 3. Idle 动画

数字人不说话时也需要"活着"的感觉：

| 动画 | 频率 | 实现方式 |
|------|------|---------|
| 眨眼 | 每3-5秒随机 | blendshape: eyeBlinkLeft/Right |
| 头部微动 | 持续 | 骨骼旋转: Head bone, 正弦波叠加噪声 |
| 呼吸 | 持续 | 骨骼缩放: Spine bone, 缓慢正弦波 |

## 4. 降级方案

如果 3D 实现遇到困难，按以下顺序降级：

```
方案A: Three.js + GLB + rhubarb口型同步 (完整版)
  ↓ 降级
方案B: Three.js + GLB + 简单口型(说话时张嘴/闭嘴交替)
  ↓ 降级
方案C: 2D头像 + CSS动画(说话时嘴部区域动画)
```
