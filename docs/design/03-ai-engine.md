# AI 引擎设计

## 整体结构（双模型协同）

```
aiortc 接收的音视频流
        │
        ├── 音频流 ──→ VoiceEngine(豆包语音大模型)
        │                 ├─ 实时语音对话(支持打断)
        │                 ├─ 后端注入 System Prompt + RAG上下文
        │                 └─ 返回: 语音流 + 转写文本
        │
        └── 视频帧 ──→ VisionEngine(Gemini 2.0 Flash)
                          ├─ 微表情/注意力分析
                          └─ 返回: 非语言评分数据
                                        │
                                        ▼
                                  ScoringEngine
                                  (Gemini Structured Output)
                                  综合评分 + 报告生成
```

## 1. 豆包语音大模型接入（主对话引擎）

### 1.1 为什么用豆包做语音而不是 Gemini

| 对比项 | 豆包语音 | Gemini Live API |
|--------|---------|-----------------|
| 中文语音质量 | 最佳（原生中文） | 一般 |
| 国内访问 | 直连，低延迟 | 需翻墙，不稳定 |
| 打断支持 | 原生支持 | 支持 |
| 答辩现场稳定性 | 高 | 低（依赖翻墙） |

### 1.2 后端桥接架构

```
浏览器 ──WebRTC──→ aiortc ──WebSocket──→ 豆包API
                     │                       │
                     │ 注入RAG上下文          │ 返回语音流
                     │ + System Prompt        │
                     ▼                       ▼
                  后端是桥接层，不是透传，每轮对话前组装上下文
```

### 1.3 调用方式（伪代码）

```python
import websockets

class DoubaoVoiceEngine:
    """豆包语音大模型 WebSocket 客户端"""

    def __init__(self, api_key: str, app_id: str):
        self.api_key = api_key
        self.app_id = app_id
        self.ws = None

    async def connect(self, system_prompt: str):
        """建立连接并发送 System Prompt（含RAG上下文）"""
        self.ws = await websockets.connect(
            "wss://openspeech.bytedance.com/api/v3/sauc/bigmodel",
            extra_headers={"Authorization": f"Bearer {self.api_key}"}
        )
        # 发送会话配置：角色设定 + RAG检索的简历/题库
        await self.ws.send(json.dumps({
            "header": {"app_id": self.app_id},
            "payload": {"system_prompt": system_prompt}
        }))

    async def send_audio(self, audio_chunk: bytes):
        """转发用户音频帧（来自aiortc）"""
        await self.ws.send(audio_chunk)

    async def receive_audio(self):
        """接收豆包返回的语音流"""
        async for message in self.ws:
            data = json.loads(message)
            if data["type"] == "audio":
                yield data["audio"]  # 语音回复
            elif data["type"] == "text":
                yield data["text"]   # 转写文本(用于存档/评分)
            elif data["type"] == "interrupted":
                yield None           # 被用户打断

    async def interrupt(self):
        """发送打断信号"""
        await self.ws.send(json.dumps({"type": "interrupt"}))
```

---

## 2. Gemini 视觉分析引擎

Gemini 不负责语音对话，专注两件事：**视频帧分析** 和 **结构化评分**。

### 2.1 视频帧分析（微表情+注意力）

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

vision_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key="your-key",
)

async def analyze_frame(frame_b64: str, context: str) -> dict:
    """分析单帧视频，返回非语言表现评估"""
    msg = HumanMessage(content=[
        {"type": "text", "text": (
            "分析这张面试者的截图，返回JSON：\n"
            f"当前面试上下文：{context}\n"
            "判断：1.情绪(confident/nervous/confused/neutral) "
            "2.是否看向摄像头 3.面部是否可见 4.置信度0-1"
        )},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame_b64}"}},
    ])
    result = await vision_llm.ainvoke([msg])
    return json.loads(result.content)
```

### 2.2 调用频率

- 视频帧分析：每 3-5 秒一次（不需要每帧都分析，节省API额度）
- 评分：每轮对话结束后异步调用一次

---

## 3. RAG Pipeline

### 3.1 知识库构成

```
knowledge_base/
├── resumes/          # 面试者简历(PDF)
├── job_descriptions/ # 岗位JD
├── question_banks/   # 题库(按领域分类)
│   ├── frontend.md
│   ├── backend.md
│   ├── algorithm.md
│   └── ...
└── scoring_rubrics/  # 评分标准
```

### 3.2 文档处理流程

```
PDF/MD/TXT 文件
    │
    ▼ PyPDFLoader / TextLoader
原始文本
    │
    ▼ RecursiveCharacterTextSplitter(chunk_size=500, overlap=50)
文本块列表
    │
    ▼ Gemini Embedding API (models/text-embedding-004)
向量列表
    │
    ▼ ChromaDB.add()
持久化存储(本地 ./chroma_db/)
```

### 3.3 检索策略

```python
# 创建检索器
retriever = vectorstore.as_retriever(
    search_type="mmr",          # 最大边际相关性，避免重复
    search_kwargs={"k": 5},     # 返回5个最相关片段
)

# 检索时根据面试上下文构造query
query = f"岗位:{job_title} 当前话题:{current_topic} 候选人背景:{resume_summary}"
relevant_docs = await retriever.ainvoke(query)
```

---

## 4. Prompt 工程

### 4.1 System Prompt 结构

```
[角色设定]
你是一位资深的{job_title}面试官，正在对候选人进行模拟面试。

[面试规则]
- 每次只问一个问题
- 根据候选人回答深度决定是否追问
- 难度从基础逐步递进
- 保持专业但友好的语气

[候选人信息]
{resume_context}  ← RAG检索的简历片段

[岗位要求]
{jd_context}  ← RAG检索的JD片段

[参考题目]
{question_context}  ← RAG检索的题库片段

[评分维度]
内容准确性 / 逻辑清晰度 / 技术深度 / 表达能力

[当前面试进度]
已问{n}题，当前话题:{topic}，整体表现:{summary}
```

### 4.2 对话历史管理

```python
class ConversationManager:
    """管理面试对话历史，控制上下文窗口"""

    def __init__(self, max_turns: int = 20):
        self.messages: list = []
        self.max_turns = max_turns

    def add_turn(self, user_msg, ai_msg, score=None):
        self.messages.append({
            "user": user_msg,
            "ai": ai_msg,
            "score": score,
        })
        # 超出限制时，保留首尾，压缩中间
        if len(self.messages) > self.max_turns:
            self._compress()

    def get_langchain_messages(self):
        """转换为LangChain消息格式"""
        ...
```
