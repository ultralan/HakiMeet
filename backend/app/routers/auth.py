from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.database import get_db, User
from app.schemas.models import UserCreate, UserOut, Token

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode({"sub": user_id, "exp": expire}, settings.secret_key, algorithm=settings.jwt_algorithm)


async def get_current_user(token: str = Depends(), db: AsyncSession = Depends(get_db)) -> User:
    """从JWT token解析当前用户 - Phase 1简化版，后续完善"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/register", response_model=UserOut)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(username=data.username, password_hash=pwd_context.hash(data.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()
    if not user or not pwd_context.verify(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return Token(access_token=create_token(user.id))
