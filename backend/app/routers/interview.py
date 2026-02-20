from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db, Interview, InterviewTurn, QuestionBank
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
        qb_categories=data.qb_categories,
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


@router.get("/stats")
async def interview_stats(
    user_id: str = "demo-user",
    db: AsyncSession = Depends(get_db),
):
    # 总次数 + 平均分
    row = (await db.execute(
        select(func.count(), func.avg(Interview.overall_score))
        .where(Interview.user_id == user_id)
    )).one()
    total_count = row[0]
    avg_score = round(row[1], 1) if row[1] else 0

    # 题库分类覆盖：用户面试涉及的分类 / 题库总分类数
    used = (await db.execute(
        select(Interview.qb_categories).where(Interview.user_id == user_id)
    )).scalars().all()
    used_cats = {c for cats in used if cats for c in cats}
    all_cats = (await db.execute(select(func.count(func.distinct(QuestionBank.category))))).scalar() or 0
    total_cats = max(all_cats, len(used_cats))

    return {
        "total_count": total_count,
        "avg_score": avg_score,
        "category_coverage": f"{len(used_cats)}/{total_cats}" if total_cats else "0/0",
    }


@router.delete("/{interview_id}")
async def delete_interview(interview_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Interview).where(Interview.id == interview_id))
    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    await db.execute(InterviewTurn.__table__.delete().where(InterviewTurn.interview_id == interview_id))
    await db.delete(interview)
    await db.commit()
    return {"ok": True}


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
