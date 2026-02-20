import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db, QuestionBank
from app.schemas.models import QuestionBankOut, ChunkOut

router = APIRouter()

UPLOAD_DIR = Path("uploads/question_banks")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=QuestionBankOut)
async def upload_question_bank(
    file: UploadFile = File(...),
    category: str = Form(...),
    user_id: str = "demo-user",
    db: AsyncSession = Depends(get_db),
):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in (".pdf", ".md"):
        raise HTTPException(status_code=400, detail="Only PDF and MD files supported")

    file_path = UPLOAD_DIR / file.filename
    content = await file.read()
    file_path.write_bytes(content)

    if suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(file_path))
        raw_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        raw_text = content.decode("utf-8")

    qb = QuestionBank(
        user_id=user_id, filename=file.filename,
        category=category, raw_text=raw_text, file_path=str(file_path),
    )
    db.add(qb)
    await db.commit()
    await db.refresh(qb)

    from app.ai.rag import get_rag
    rag = get_rag()
    metadata = {"type": "question_bank", "category": category, "qb_id": qb.id}
    await rag.ingest_questions(raw_text, metadata=metadata)
    qb.vectorized = True
    await db.commit()
    await db.refresh(qb)

    return qb


@router.get("/list", response_model=list[QuestionBankOut])
async def list_question_banks(
    category: str | None = Query(None),
    user_id: str = "demo-user",
    db: AsyncSession = Depends(get_db),
):
    stmt = select(QuestionBank).where(QuestionBank.user_id == user_id)
    if category:
        stmt = stmt.where(QuestionBank.category == category)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/categories")
async def get_categories(
    user_id: str = "demo-user",
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(QuestionBank.category).where(QuestionBank.user_id == user_id).distinct()
    )
    return [r[0] for r in result.all()]


@router.delete("/{qb_id}")
async def delete_question_bank(qb_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(QuestionBank).where(QuestionBank.id == qb_id))
    qb = result.scalar_one_or_none()
    if not qb:
        raise HTTPException(status_code=404, detail="Question bank not found")
    if qb.file_path and os.path.exists(qb.file_path):
        os.remove(qb.file_path)
    from app.ai.rag import get_rag
    get_rag().delete_by_metadata({"qb_id": qb_id})
    await db.delete(qb)
    await db.commit()
    return {"status": "deleted"}


@router.get("/{qb_id}/chunks", response_model=list[ChunkOut])
async def get_chunks(qb_id: str):
    from app.ai.rag import get_rag
    return get_rag().get_chunks_by_metadata({"qb_id": qb_id})
