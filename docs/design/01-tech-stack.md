# 技术栈选型

## 前端

| 技术 | 版本 | 用途 | 选型理由 |
|------|------|------|---------|
| Vue 3 | 3.4+ | UI框架 | 组合式API，生态成熟 |
| Vite | 5.x | 构建工具 | 快速HMR，Vue官方推荐 |
| Pinia | 2.x | 状态管理 | 面试状态、对话历史、评分数据 |
| Three.js | r160+ | 3D渲染 | 数字人渲染，生态最大 |
| @mediapipe/face_mesh | 0.4 | 面部检测 | 前端备用方案，浏览器端运行 |

## 后端

| 技术 | 版本 | 用途 | 选型理由 |
|------|------|------|---------|
| Python | 3.11+ | 运行时 | LangChain/AI生态最好 |
| FastAPI | 0.110+ | Web框架 | 原生async，WebSocket支持，自动文档 |
| aiortc | 1.9+ | WebRTC | 纯Python WebRTC实现，可直接处理媒体流 |
| LangChain | 0.2+ | AI编排 | RAG pipeline + 多模型切换 |
| ChromaDB | 0.5+ | 向量数据库 | 本地运行，零配置，免费 |
| edge-tts | 6.1+ | 语音合成(备用) | 降级方案：当豆包不可用时用Edge-TTS替代 |
| SQLAlchemy | 2.0+ | ORM | 数据持久化 |
| SQLite / PostgreSQL | - | 数据库 | 开发用SQLite，生产可切PostgreSQL |

## AI模型（双模型架构）

| 模型 | 职责 | 协议 | 免费额度 |
|------|------|------|---------|
| **豆包语音大模型** | 实时语音对话（语音输入→语音输出，支持打断） | WebSocket双向流式 | 有试用额度，正式价格极便宜 |
| **Gemini 2.0 Flash** | 视频帧视觉分析、RAG评分、面试报告生成 | REST / WebSocket | 15RPM / 100万token/天 |
| Gemini Embedding | 文本向量化（RAG用） | REST | 1500RPM 免费 |
| DeepSeek Chat | 备选LLM（纯文本，当Gemini不可用时） | REST | ~1元/百万token |

### 豆包语音大模型选型依据

1. **端到端语音对话**：语音输入→语音输出，无需单独STT/TTS
2. **支持打断**：用户可随时打断AI说话，体验像打电话
3. **中文语音质量最佳**：原生中文优化，音色自然
4. **国内直连**：答辩现场不需要翻墙，延迟低且稳定
5. **价格极低**：毕设演示成本可忽略

### Gemini 2.0 Flash 选型依据

1. **多模态视觉**：支持视频帧输入，用于微表情/非语言分析
2. **Structured Output**：支持 JSON Schema 约束输出格式（评分用）
3. **免费额度充足**：视觉分析调用频率低(~1fps)，免费档够用
4. **LangChain集成**：`langchain-google-genai` 官方包

## 3D数字人

| 组件 | 方案 | 说明 |
|------|------|------|
| 3D模型 | Ready Player Me | 免费生成半身像GLB，自带52个blendshapes |
| 渲染 | Three.js (GLTFLoader) | 加载GLB模型，控制morph targets |
| 口型同步 | rhubarb-lip-sync | 开源，音频→viseme时间轴映射 |
| 表情 | Morph Target 动画 | 通过blendshapes控制眉毛、眼睛、嘴型 |

## 通信协议

| 协议 | 场景 | 实现 |
|------|------|------|
| WebRTC | 用户音视频采集与传输 | 前端原生API + 后端aiortc |
| WebSocket | AI语音回复推送、viseme数据、控制信令 | FastAPI WebSocket |
| WebSocket(出站) | 后端→豆包语音API双向流式通信 | asyncio + websockets |
| REST API | 用户登录、简历上传、面试记录CRUD | FastAPI Router |
