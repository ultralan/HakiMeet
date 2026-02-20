# 开发阶段规划

## Phase 1: 核心对话链路（文字版）

**目标**：跑通 "用户输入 → RAG检索 → Gemini回复" 的最小闭环

**后端任务：**
- FastAPI 项目骨架搭建（路由、中间件、配置）
- LangChain + Gemini API 接入（纯文本对话）
- ChromaDB 向量库搭建 + 文档导入脚本
- RAG Pipeline：简历解析 → 向量化 → 检索 → Prompt注入
- WebSocket 流式推送 AI 回复
- SQLite 数据持久化（用户、面试、轮次）

**前端任务：**
- Vue 3 + Vite 项目初始化
- 面试对话页面（文字输入 + AI回复展示）
- WebSocket 连接管理 + 流式文本渲染
- 简历上传页面
- 基础路由和布局

**交付物**：可以通过文字和 AI 面试官对话，AI 能基于简历和岗位提问

---

## Phase 2: 语音交互

**目标**：加入语音输入和语音输出，实现"说话面试"

**后端任务：**
- Edge-TTS 集成（文本 → MP3音频）
- TTS 音频通过 WebSocket 推送
- Gemini 多模态接入（音频输入替代纯文本）

**前端任务：**
- 浏览器麦克风采集（getUserMedia）
- 音频录制 + 发送到后端
- TTS 音频播放器
- 面试状态机 UI（listening → thinking → speaking）

**交付物**：可以语音对话，AI 用语音回复

---

## Phase 3: WebRTC 实时通信

**目标**：用 WebRTC 替代简单的音频上传，实现真正的实时流式通信

**后端任务：**
- aiortc 集成（Python WebRTC Peer）
- SDP/ICE 信令接口
- 音频流实时接收 + VAD 静音检测
- 视频流接收 + 帧抽取

**前端任务：**
- WebRTC PeerConnection 建立
- 信令交换逻辑
- 摄像头画面预览

**交付物**：WebRTC 音视频通道跑通，后端能实时接收处理

---

## Phase 4: 3D 数字人

**目标**：加入 3D 面试官形象 + 口型同步

**后端任务：**
- rhubarb-lip-sync 集成（音频 → viseme时间轴）
- viseme 数据随 TTS 音频一起推送

**前端任务：**
- Three.js 场景搭建
- Ready Player Me GLB 模型加载
- Blendshape 口型同步控制器
- Idle 动画（眨眼、微动）

**交付物**：3D 数字人能说话、有口型同步

---

## Phase 5: 微表情 + 评分闭环

**目标**：完成评分系统和微表情分析

**后端任务：**
- Gemini Structured Output 评分接口
- 多维度评分汇总逻辑
- 面试报告生成

**前端任务：**
- MediaPipe Face Mesh 集成
- 情绪分类 + 目光检测
- 评分结果展示页面
- 面试报告页面（雷达图等可视化）

**交付物**：完整的面试 → 评分 → 报告闭环

---

## 关键里程碑

| 阶段 | 核心验证点 |
|------|-----------|
| Phase 1 | AI能基于简历内容提出针对性问题 |
| Phase 2 | 语音对话延迟 < 3秒，体验流畅 |
| Phase 3 | WebRTC连接稳定，音视频流正常接收 |
| Phase 4 | 3D人口型与语音基本同步 |
| Phase 5 | 评分报告维度完整，分数合理 |
