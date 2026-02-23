# HakiMeet — AI 模拟面试平台

<p align="center">
  <strong>🎙️ AI 驱动的实时语音模拟面试 · 让每一次练习都像真实面试</strong>
</p>

---

## ✨ 功能亮点

| 功能 | 说明 |
|------|------|
| 🎤 **实时语音面试** | 基于豆包语音大模型，AI 面试官以语音方式提问和点评 |
| 🧠 **RAG 题库引擎** | 上传自定义题库（Markdown/PDF），面试官参考题库精准出题 |
| 📄 **简历解析** | 上传简历，AI 针对你的项目经历进行追问 |
| 📊 **面试评价报告** | 每场面试结束后生成详细评分和改进建议 |
| 🔄 **长期记忆** | AI 自动识别薄弱知识点，后续面试优先考察 |
| ⚙️ **自定义模型** | 支持用户配置自己的文本模型（OpenAI/DeepSeek 等）和语音模型密钥 |

## 🏗️ 技术架构

```
┌─────────────────────────────────────────┐
│               Nginx (80)                │
│   静态资源 + API/WS 反向代理              │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐   ┌────────────────┐  │
│  │   Frontend   │   │    Backend     │  │
│  │   Vue 3      │──▶│   FastAPI      │  │
│  │   Vite       │   │   SQLite       │  │
│  │   Tailwind   │   │   ChromaDB     │  │
│  └──────────────┘   │   LangChain    │  │
│                     │   豆包语音 API  │  │
│                     └────────────────┘  │
└─────────────────────────────────────────┘
```

- **前端**: Vue 3 + Vue Router + Pinia + Tailwind CSS 4 + Three.js
- **后端**: FastAPI + SQLAlchemy + LangChain + ChromaDB + Sentence Transformers
- **AI**: 豆包文本大模型（火山方舟）+ 豆包语音大模型（实时对话）
- **数据库**: SQLite（轻量部署）+ ChromaDB（向量检索）

---

## 🚀 快速部署

### 方式一：Docker 一键部署（推荐）

#### 前置要求
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose

#### 步骤

```bash
# 1. 克隆项目
git clone https://github.com/your-username/hakimeet.git
cd hakimeet

# 2. 配置环境变量（可选，仅需修改 SECRET_KEY）
cp .env.example .env

# 3. 一键启动
docker compose up -d --build

# 4. 访问应用
# 前端:  http://localhost
# 后端:  http://localhost:8000/docs (API 文档)

# 5. 配置 AI 模型（首次使用）
# 打开 http://localhost/settings 填写您的模型密钥
```

#### 停止服务
```bash
docker compose down
```

#### 查看日志
```bash
docker compose logs -f backend   # 后端日志
docker compose logs -f frontend  # 前端日志
```

---

### 方式二：本地开发

#### 前置要求
- Python 3.12+
- Node.js 20+

#### 后端

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### 前端

```bash
cd frontend
npm install
npm run dev
```

前端开发服务器启动后访问 http://localhost:5173，API 请求会自动代理到后端。

---

## ⚙️ 配置说明

### 应用环境变量（`.env`）

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SECRET_KEY` | JWT 签名密钥 | `dev-secret-change-in-production` |
| `DATABASE_URL` | 数据库连接字符串 | `sqlite+aiosqlite:///./hakimeet.db` |

### AI 模型密钥（前端动态配置）

所有 AI 模型密钥（文本模型 API Key、语音模型 API Key 等）均在应用内的 **「模型配置」** 页面设置，无需写入环境变量：

1. 访问 `/settings` 页面
2. **文本模型** — 开启开关，选择供应商（OpenAI / DeepSeek / 豆包 / 自定义），填写 API Key、端点和模型名称
3. **语音模型** — 开启开关，填写豆包语音 API 的各项密钥
4. 点击「保存配置」即可生效

---

## 📁 项目结构

```
hakimeet/
├── backend/
│   ├── app/
│   │   ├── ai/              # AI 引擎（面试/语音/RAG/记忆）
│   │   ├── models/           # 数据库模型
│   │   ├── routers/          # API 路由
│   │   ├── schemas/          # Pydantic Schema
│   │   ├── config.py         # 配置管理
│   │   └── main.py           # FastAPI 入口
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/            # 页面组件
│   │   ├── composables/      # 组合式函数
│   │   ├── router/           # Vue Router
│   │   └── App.vue           # 根组件
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 📝 使用流程

1. **上传简历**（可选）— 在「简历管理」页面上传 PDF 格式简历
2. **导入题库**（可选）— 在「题库管理」页面上传 Markdown 格式的面试题库
3. **开始面试** — 在首页选择题库分类和简历，点击「开始面试」
4. **语音交互** — 允许麦克风权限后，与 AI 面试官进行实时语音对话
5. **查看报告** — 面试结束后查看评分报告和改进建议
6. **持续提升** — 在「长期记忆」页面查看 AI 自动提取的薄弱知识点

---

## 📜 License

MIT
