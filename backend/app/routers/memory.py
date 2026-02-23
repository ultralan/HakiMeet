"""长期记忆（薄弱点）管理 API"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db, WeakPoint
from app.schemas.models import WeakPointOut

router = APIRouter()


@router.get("/list")
async def list_weak_points(
    user_id: str = "demo-user",
    db: AsyncSession = Depends(get_db),
):
    """按分类分组返回所有薄弱点"""
    result = await db.execute(
        select(WeakPoint)
        .where(WeakPoint.user_id == user_id)
        .order_by(WeakPoint.category, WeakPoint.severity.desc())
    )
    points = result.scalars().all()

    # 按分类分组
    grouped = {}
    for p in points:
        if p.category not in grouped:
            grouped[p.category] = []
        grouped[p.category].append({
            "id": p.id,
            "question_summary": p.question_summary,
            "weakness_desc": p.weakness_desc,
            "severity": p.severity,
            "resolved": p.resolved,
            "interview_id": p.interview_id,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })

    return grouped


@router.get("/by-category", response_model=list[WeakPointOut])
async def get_by_category(
    category: str = Query(...),
    user_id: str = "demo-user",
    db: AsyncSession = Depends(get_db),
):
    """查询指定分类的薄弱点"""
    result = await db.execute(
        select(WeakPoint)
        .where(WeakPoint.user_id == user_id, WeakPoint.category == category)
        .order_by(WeakPoint.severity.desc())
    )
    return result.scalars().all()


@router.get("/suggestions")
async def get_suggestions(
    categories: str = Query("", description="逗号分隔的分类列表"),
    user_id: str = "demo-user",
    db: AsyncSession = Depends(get_db),
):
    """根据选中的分类获取建议复习的薄弱点"""
    if not categories:
        return []
    cat_list = [c.strip() for c in categories.split(",") if c.strip()]
    result = await db.execute(
        select(WeakPoint)
        .where(
            WeakPoint.user_id == user_id,
            WeakPoint.resolved == False,
            WeakPoint.category.in_(cat_list),
        )
        .order_by(WeakPoint.severity.desc())
        .limit(5)
    )
    points = result.scalars().all()
    return [
        {
            "id": p.id,
            "category": p.category,
            "question_summary": p.question_summary,
            "weakness_desc": p.weakness_desc,
            "severity": p.severity,
        }
        for p in points
    ]


@router.put("/{point_id}/resolve")
async def resolve_weak_point(
    point_id: str,
    db: AsyncSession = Depends(get_db),
):
    """标记薄弱点为已解决"""
    result = await db.execute(select(WeakPoint).where(WeakPoint.id == point_id))
    point = result.scalar_one_or_none()
    if not point:
        raise HTTPException(status_code=404, detail="薄弱点不存在")
    point.resolved = True
    await db.commit()
    return {"ok": True}


@router.delete("/{point_id}")
async def delete_weak_point(
    point_id: str,
    db: AsyncSession = Depends(get_db),
):
    """删除单条薄弱点"""
    result = await db.execute(select(WeakPoint).where(WeakPoint.id == point_id))
    point = result.scalar_one_or_none()
    if not point:
        raise HTTPException(status_code=404, detail="薄弱点不存在")
    await db.delete(point)
    await db.commit()
    return {"ok": True}
