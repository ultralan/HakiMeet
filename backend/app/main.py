import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.database import init_db
from app.routers import interview, question_bank, resume, ws, memory, ai_config

# 日志配置：同时输出到文件和终端
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "interview.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
# 降低第三方库日志级别
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("websockets").setLevel(logging.WARNING)
logging.getLogger("aiosqlite").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="HakiMeet", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume.router, prefix="/api/resume", tags=["resume"])
app.include_router(question_bank.router, prefix="/api/qb", tags=["question_bank"])
app.include_router(interview.router, prefix="/api/interview", tags=["interview"])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"])
app.include_router(ai_config.router, prefix="/api/ai-config", tags=["ai_config"])
app.include_router(ws.router, tags=["websocket"])


