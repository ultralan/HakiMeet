from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: str
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


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
    started_at: datetime | None
    ended_at: datetime | None


class JobPositionCreate(BaseModel):
    title: str
    description: str
    requirements: str
    difficulty: str = "mid"


class JobPositionOut(BaseModel):
    id: str
    title: str
    difficulty: str
