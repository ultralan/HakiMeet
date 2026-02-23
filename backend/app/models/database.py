import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, Integer, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, relationship

from app.config import settings

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=gen_uuid)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resumes = relationship("Resume", back_populates="user")
    question_banks = relationship("QuestionBank", back_populates="user")
    interviews = relationship("Interview", back_populates="user")


class Resume(Base):
    __tablename__ = "resumes"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255))
    raw_text = Column(Text)
    file_path = Column(String(500))
    vectorized = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="resumes")


class QuestionBank(Base):
    __tablename__ = "question_banks"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255))
    category = Column(String(100), nullable=False)
    raw_text = Column(Text)
    file_path = Column(String(500))
    vectorized = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="question_banks")


class JobPosition(Base):
    __tablename__ = "job_positions"
    id = Column(String, primary_key=True, default=gen_uuid)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    requirements = Column(Text)
    difficulty = Column(String(20), default="mid")


class Interview(Base):
    __tablename__ = "interviews"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    resume_id = Column(String, ForeignKey("resumes.id"))
    job_id = Column(String, ForeignKey("job_positions.id"))
    qb_categories = Column(JSON, default=list)
    status = Column(String(20), default="pending")
    overall_score = Column(Float)
    report = Column(JSON)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    user = relationship("User", back_populates="interviews")
    resume = relationship("Resume")
    job = relationship("JobPosition")
    turns = relationship("InterviewTurn", back_populates="interview")


class InterviewTurn(Base):
    __tablename__ = "interview_turns"
    id = Column(String, primary_key=True, default=gen_uuid)
    interview_id = Column(String, ForeignKey("interviews.id"), nullable=False)
    turn_number = Column(Integer)
    ai_question = Column(Text)
    user_answer = Column(Text)
    score_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    interview = relationship("Interview", back_populates="turns")


class WeakPoint(Base):
    """长期记忆：用户面试薄弱点记录，按题库分类存储"""
    __tablename__ = "weak_points"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    interview_id = Column(String, ForeignKey("interviews.id"), nullable=False)
    category = Column(String(100), nullable=False)
    question_summary = Column(Text, nullable=False)
    weakness_desc = Column(Text, nullable=False)
    severity = Column(Integer, default=3)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User")
    interview = relationship("Interview")


class AIModelConfig(Base):
    """用户自定义 AI 模型配置（文本模型 + 语音模型）"""
    __tablename__ = "ai_model_configs"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    # --- 文本模型配置 ---
    provider_name = Column(String(100), default="custom")
    api_key = Column(String(500))
    base_url = Column(String(500))
    model_id = Column(String(200))
    llm_enabled = Column(Boolean, default=False)
    # --- 语音模型配置 ---
    voice_ws_url = Column(String(500))
    voice_app_id = Column(String(100))
    voice_access_key = Column(String(200))
    voice_secret_key = Column(String(200))
    voice_resource_id = Column(String(200))
    voice_app_key = Column(String(200))
    voice_enabled = Column(Boolean, default=False)
    # --- 通用 ---
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with async_session() as session:
        yield session
