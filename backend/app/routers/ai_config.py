"""AI 模型配置 CRUD 路由"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db, AIModelConfig
from app.schemas.models import AIModelConfigIn, AIModelConfigOut

router = APIRouter()


def _mask(secret: str | None) -> str:
    """将密钥脱敏为 ****xxxx 格式"""
    if not secret:
        return ""
    if len(secret) <= 4:
        return "****"
    return "****" + secret[-4:]


def _config_to_out(cfg: AIModelConfig) -> AIModelConfigOut:
    return AIModelConfigOut(
        id=cfg.id,
        provider_name=cfg.provider_name or "custom",
        api_key_preview=_mask(cfg.api_key),
        base_url=cfg.base_url,
        model_id=cfg.model_id,
        llm_enabled=cfg.llm_enabled,
        voice_ws_url=cfg.voice_ws_url,
        voice_app_id=cfg.voice_app_id,
        voice_access_key_preview=_mask(cfg.voice_access_key),
        voice_enabled=cfg.voice_enabled,
        created_at=cfg.created_at,
    )


@router.get("", response_model=AIModelConfigOut | None)
async def get_ai_config(
    user_id: str = "demo-user",
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的 AI 模型配置"""
    result = await db.execute(
        select(AIModelConfig).where(AIModelConfig.user_id == user_id)
    )
    cfg = result.scalar_one_or_none()
    if not cfg:
        return None
    return _config_to_out(cfg)


@router.put("", response_model=AIModelConfigOut)
async def upsert_ai_config(
    data: AIModelConfigIn,
    user_id: str = "demo-user",
    db: AsyncSession = Depends(get_db),
):
    """创建或更新用户的 AI 模型配置"""
    result = await db.execute(
        select(AIModelConfig).where(AIModelConfig.user_id == user_id)
    )
    cfg = result.scalar_one_or_none()

    if cfg:
        # 更新已有配置
        cfg.provider_name = data.provider_name
        cfg.llm_enabled = data.llm_enabled
        cfg.voice_enabled = data.voice_enabled
        # 文本模型字段（只在有新值时更新密钥）
        if data.api_key is not None:
            cfg.api_key = data.api_key
        if data.base_url is not None:
            cfg.base_url = data.base_url
        if data.model_id is not None:
            cfg.model_id = data.model_id
        # 语音模型字段
        if data.voice_ws_url is not None:
            cfg.voice_ws_url = data.voice_ws_url
        if data.voice_app_id is not None:
            cfg.voice_app_id = data.voice_app_id
        if data.voice_access_key is not None:
            cfg.voice_access_key = data.voice_access_key
        if data.voice_secret_key is not None:
            cfg.voice_secret_key = data.voice_secret_key
        if data.voice_resource_id is not None:
            cfg.voice_resource_id = data.voice_resource_id
        if data.voice_app_key is not None:
            cfg.voice_app_key = data.voice_app_key
    else:
        cfg = AIModelConfig(
            user_id=user_id,
            provider_name=data.provider_name,
            api_key=data.api_key,
            base_url=data.base_url,
            model_id=data.model_id,
            llm_enabled=data.llm_enabled,
            voice_ws_url=data.voice_ws_url,
            voice_app_id=data.voice_app_id,
            voice_access_key=data.voice_access_key,
            voice_secret_key=data.voice_secret_key,
            voice_resource_id=data.voice_resource_id,
            voice_app_key=data.voice_app_key,
            voice_enabled=data.voice_enabled,
        )
        db.add(cfg)

    await db.commit()
    await db.refresh(cfg)
    return _config_to_out(cfg)


@router.delete("")
async def delete_ai_config(
    user_id: str = "demo-user",
    db: AsyncSession = Depends(get_db),
):
    """删除用户的自定义配置（回退为系统默认值）"""
    result = await db.execute(
        select(AIModelConfig).where(AIModelConfig.user_id == user_id)
    )
    cfg = result.scalar_one_or_none()
    if not cfg:
        raise HTTPException(status_code=404, detail="没有找到自定义配置")
    await db.delete(cfg)
    await db.commit()
    return {"ok": True}


@router.post("/test")
async def test_ai_config(data: AIModelConfigIn):
    """测试文本模型连接：向 LLM 发送简单请求"""
    if not data.api_key or not data.base_url or not data.model_id:
        raise HTTPException(status_code=400, detail="请填写 API Key、端点和模型名称")

    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage

    try:
        llm = ChatOpenAI(
            model=data.model_id,
            openai_api_key=data.api_key,
            openai_api_base=data.base_url,
            temperature=0,
            max_tokens=10,
        )
        response = await llm.ainvoke([HumanMessage(content="你好，请回复OK")])
        return {"ok": True, "reply": response.content[:100]}
    except Exception as e:
        return {"ok": False, "error": str(e)[:300]}
