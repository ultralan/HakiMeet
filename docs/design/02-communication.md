# 通信协议设计

## 协议总览

系统使用三种通信协议，各司其职：

```
浏览器 ──WebRTC──→ 后端aiortc    (音视频媒体流，实时性最高)
浏览器 ←─WebSocket─→ 后端FastAPI  (AI回复流式推送、TTS音频、控制指令)
浏览器 ←─REST API──→ 后端FastAPI  (业务CRUD：登录、简历、历史记录)
```

---

## 1. WebRTC 通信流程

### 1.1 信令交换（通过 REST API）

```
浏览器                              后端
  │                                  │
  │  POST /api/rtc/offer             │
  │  {sdp: offer, type: "offer"}     │
  │ ──────────────────────────────→  │
  │                                  │  aiortc 创建 PeerConnection
  │                                  │  设置 remote description
  │                                  │  创建 answer
  │  {sdp: answer, type: "answer"}   │
  │ ←──────────────────────────────  │
  │                                  │
  │  浏览器设置 remote description    │
  │  ICE 候选通过 Trickle ICE 交换   │
  │                                  │
  │  POST /api/rtc/ice-candidate     │
  │  {candidate, sdpMid, ...}        │
  │ ──────────────────────────────→  │
  │                                  │
  │  WebRTC 连接建立                  │
  │ ═══════════════════════════════  │
  │  音频轨(opus) + 视频轨(vp8/h264) │
  │ ──────────────────────────────→  │
```

### 1.2 信令接口定义

```
POST /api/rtc/offer
Request:  { "sdp": string, "type": "offer", "interview_id": string }
Response: { "sdp": string, "type": "answer" }

POST /api/rtc/ice-candidate
Request:  { "candidate": string, "sdpMid": string, "sdpMLineIndex": int }
Response: { "status": "ok" }
```

### 1.3 后端媒体处理

aiortc 接收到音视频轨后的处理逻辑：

```
音频轨(AudioStreamTrack):
  → AudioBuffer 累积
  → VAD静音检测(webrtcvad)
  → 检测到语音结束 → 提取音频段
  → 转为 PCM/WAV → 发送给 Gemini API

视频轨(VideoStreamTrack):
  → 每秒抽取1帧(降低开销)
  → 转为 JPEG/PNG
  → 缓存最近5帧
  → 随音频一起发给 Gemini(多模态输入)
```

---

## 2. WebSocket 通信

### 2.1 连接建立

```
ws://localhost:8000/ws/interview/{interview_id}
```

### 2.2 消息格式

所有 WebSocket 消息使用 JSON 格式，通过 `type` 字段区分：

```json
{
  "type": "消息类型",
  "data": { ... },
  "timestamp": 1708000000000
}
```

### 2.3 消息类型定义

**服务端 → 客户端：**

| type | 说明 | data 结构 |
|------|------|----------|
| `ai_text_chunk` | AI回复文本流式块 | `{ "text": "部分文本", "done": false }` |
| `ai_text_done` | AI回复完成 | `{ "full_text": "完整回复" }` |
| `tts_audio` | TTS音频数据块 | `{ "audio": "base64编码", "format": "mp3" }` |
| `viseme` | 口型时间轴数据 | `{ "visemes": [{"time":0.1,"value":"A"},...] }` |
| `score_update` | 实时评分更新 | `{ "dimension": "content", "score": 8.5 }` |
| `interview_state` | 面试状态变更 | `{ "state": "listening|thinking|speaking" }` |
| `error` | 错误信息 | `{ "code": "E001", "message": "..." }` |

**客户端 → 服务端：**

| type | 说明 | data 结构 |
|------|------|----------|
| `user_text` | 用户文字输入(备用) | `{ "text": "用户输入" }` |
| `control` | 控制指令 | `{ "action": "pause|resume|end" }` |
| `expression` | 前端表情检测结果 | `{ "emotion": "nervous", "confidence": 0.8 }` |

---

## 3. REST API

### 3.1 接口列表

**用户模块：**
```
POST   /api/auth/register     注册
POST   /api/auth/login        登录 → 返回JWT
GET    /api/auth/me            获取当前用户信息
```

**简历模块：**
```
POST   /api/resume/upload      上传简历(PDF) → 解析+向量化
GET    /api/resume/list        简历列表
DELETE /api/resume/{id}        删除简历
```

**面试模块：**
```
POST   /api/interview/create   创建面试(选择岗位+简历)
GET    /api/interview/{id}     获取面试详情
GET    /api/interview/list     面试历史列表
GET    /api/interview/{id}/report  获取面试报告
```

**知识库模块：**
```
POST   /api/knowledge/upload   上传知识文档(PDF/TXT/MD)
GET    /api/knowledge/list     知识库文档列表
DELETE /api/knowledge/{id}     删除文档
```
