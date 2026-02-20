import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.database import get_db, Resume
from app.schemas.models import ResumeOut

router = APIRouter()

UPLOAD_DIR = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=ResumeOut)
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = "demo-user",  # Phase 1 简化，后续接JWT
    db: AsyncSession = Depends(get_db),
):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in (".pdf", ".md"):
        raise HTTPException(status_code=400, detail="Only PDF and MD files supported")

    file_path = UPLOAD_DIR / file.filename
    content = await file.read()
    file_path.write_bytes(content)

    # 按格式提取文本
    if suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(file_path))
        raw_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        raw_text = content.decode("utf-8")

    resume = Resume(
        user_id=user_id,
        filename=file.filename,
        raw_text=raw_text,
        file_path=str(file_path),
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    # 向量化简历内容
    from app.ai.rag import get_rag
    rag = get_rag()
    metadata = {"resume_id": resume.id, "type": "resume"}
    if suffix == ".pdf":
        await rag.ingest_pdf(str(file_path), metadata=metadata)
    else:
        await rag.ingest_text(raw_text, metadata=metadata)
    resume.vectorized = True
    await db.commit()
    await db.refresh(resume)

    return resume


@router.get("/list", response_model=list[ResumeOut])
async def list_resumes(
    user_id: str = "demo-user",
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Resume).where(Resume.user_id == user_id))
    return result.scalars().all()


@router.delete("/{resume_id}")
async def delete_resume(resume_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.file_path and os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    await db.delete(resume)
    await db.commit()
    return {"status": "deleted"}
