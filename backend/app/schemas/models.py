from datetime import datetime
from pydantic import BaseModel


class ResumeOut(BaseModel):
    id: str
    filename: str
    vectorized: bool
    created_at: datetime


class QuestionBankOut(BaseModel):
    id: str
    filename: str
    category: str
    vectorized: bool
    created_at: datetime


class ChunkOut(BaseModel):
    content: str
    metadata: dict


class InterviewCreate(BaseModel):
    resume_id: str | None = None
    job_id: str
    qb_categories: list[str] = []


class InterviewOut(BaseModel):
    id: str
    status: str
    overall_score: float | None
    report: dict | None = None
    qb_categories: list[str] = []
    resume_id: str | None = None
    started_at: datetime | None
    ended_at: datetime | None


class WeakPointOut(BaseModel):
    id: str
    category: str
    question_summary: str
    weakness_desc: str
    severity: int
    resolved: bool
    interview_id: str
    created_at: datetime | None


class AIModelConfigIn(BaseModel):
    # 文本模型
    provider_name: str = "custom"
    api_key: str | None = None
    base_url: str | None = None
    model_id: str | None = None
    llm_enabled: bool = False
    # 语音模型
    voice_ws_url: str | None = None
    voice_app_id: str | None = None
    voice_access_key: str | None = None
    voice_secret_key: str | None = None
    voice_resource_id: str | None = None
    voice_app_key: str | None = None
    voice_enabled: bool = False


class AIModelConfigOut(BaseModel):
    id: str
    provider_name: str
    api_key_preview: str
    base_url: str | None
    model_id: str | None
    llm_enabled: bool
    voice_ws_url: str | None
    voice_app_id: str | None
    voice_access_key_preview: str
    voice_enabled: bool
    created_at: datetime
