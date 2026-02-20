from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db, Interview, InterviewTurn
from app.schemas.models import InterviewCreate, InterviewOut

router = APIRouter()


@router.post("/create", response_model=InterviewOut)
async def create_interview(
    data: InterviewCreate,
    user_id: str = "demo-user",
    db: AsyncSession = Depends(get_db),
):
    interview = Interview(
        user_id=user_id,
        resume_id=data.resume_id,
        job_id=data.job_id,
        status="pending",
        started_at=datetime.utcnow(),
    )
    db.add(interview)
    await db.commit()
    await db.refresh(interview)
    return interview


@router.get("/list", response_model=list[InterviewOut])
async def list_interviews(
    user_id: str = "demo-user",
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Interview).where(Interview.user_id == user_id).order_by(Interview.started_at.desc())
    )
    return result.scalars().all()


@router.get("/{interview_id}")
async def get_interview(interview_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Interview).where(Interview.id == interview_id))
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    # 加载对话轮次
    turns_result = await db.execute(
        select(InterviewTurn)
        .where(InterviewTurn.interview_id == interview_id)
        .order_by(InterviewTurn.turn_number)
    )
    turns = turns_result.scalars().all()
    return {
        "id": interview.id,
        "status": interview.status,
        "overall_score": interview.overall_score,
        "report": interview.report,
        "started_at": interview.started_at,
        "ended_at": interview.ended_at,
        "turns": [
            {
                "turn_number": t.turn_number,
                "ai_question": t.ai_question,
                "user_answer": t.user_answer,
                "score_data": t.score_data,
            }
            for t in turns
        ],
    }
