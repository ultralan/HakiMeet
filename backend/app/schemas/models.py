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



