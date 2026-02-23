"""长期记忆分析引擎：面试结束后独立 LLM 分析并沉淀记忆点"""

import json
import logging
import re
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.config import settings

logger = logging.getLogger("hakimeet.memory")


async def _build_llm(user_id: str, **kwargs):
    """根据用户 AI 配置动态创建 LLM，无配置则使用系统默认"""
    from app.models.database import async_session, AIModelConfig
    from sqlalchemy import select

    async with async_session() as session:
        result = await session.execute(
            select(AIModelConfig).where(AIModelConfig.user_id == user_id)
        )
        cfg = result.scalar_one_or_none()

    if cfg and cfg.llm_enabled and cfg.api_key and cfg.base_url and cfg.model_id:
        logger.info("记忆分析使用用户自定义模型: %s", cfg.model_id)
        return ChatOpenAI(
            model=cfg.model_id,
            openai_api_key=cfg.api_key,
            openai_api_base=cfg.base_url,
            **kwargs,
        )

    return ChatOpenAI(
        model=settings.doubao_model_id,
        openai_api_key=settings.doubao_api_key,
        openai_api_base=settings.doubao_base_url,
        **kwargs,
    )


ANALYSIS_PROMPT = """你是一位面试评估专家。请分析以下面试对话记录，找出候选人回答**不好**的题目。

【判断标准】
- 回答有明显错误或概念混淆 → severity 4-5
- 回答不够深入、只是泛泛而谈 → severity 3
- 回答基本正确但有小瑕疵 → severity 2
- 回答得好的题目 → 不要记录

【输出格式】
请严格输出 JSON 数组（不要输出其他内容），每个元素：
```json
{
  "question_summary": "面试官问的问题的简要概括（一句话）",
  "category": "该题所属的题库分类（从可用分类中选择最匹配的）",
  "weakness_desc": "候选人答得不好的具体原因（2-3句话）",
  "severity": 3
}
```

如果候选人所有题目都答得不错，输出空数组 `[]`。

【可用题库分类】
{categories}

【面试对话记录】
{conversation}"""


async def analyze_and_save(
    interview_id: str,
    user_id: str,
    history: list,
    categories: list[str],
):
    """分析面试对话，提取长期记忆点并保存到数据库"""
    if len(history) < 2:
        logger.info("对话轮次不足，跳过记忆分析")
        return

    # 构建对话文本
    conversation_lines = []
    for msg in history:
        if isinstance(msg, AIMessage):
            conversation_lines.append(f"面试官：{msg.content}")
        elif isinstance(msg, HumanMessage):
            conversation_lines.append(f"候选人：{msg.content}")
    conversation_text = "\n\n".join(conversation_lines)

    cat_str = "、".join(categories) if categories else "通用技术"

    llm = await _build_llm(user_id, temperature=0.3)

    prompt = (
        ANALYSIS_PROMPT.replace("{categories}", cat_str)
        .replace("{conversation}", conversation_text)
    )

    try:
        response = await llm.ainvoke([
            SystemMessage(content="你是面试评估专家，只输出 JSON。"),
            HumanMessage(content=prompt),
        ])

        # 解析 JSON
        raw = response.content.strip()
        # 处理可能的 markdown 代码块包裹（```json ... ``` 或 ``` ... ```）
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', raw, re.DOTALL)
        if json_match:
            raw = json_match.group(1).strip()
        # 兜底：尝试直接找 JSON 数组或对象
        if not (raw.startswith('[') or raw.startswith('{')):
            arr_match = re.search(r'\[.*\]', raw, re.DOTALL)
            if arr_match:
                raw = arr_match.group(0)
            else:
                obj_match = re.search(r'\{.*\}', raw, re.DOTALL)
                if obj_match:
                    raw = obj_match.group(0)

        weak_points = json.loads(raw)
        if not isinstance(weak_points, list):
            logger.warning("LLM 返回非数组: %s", raw[:200])
            return

        if not weak_points:
            logger.info("面试 %s: 没有发现需要沉淀的记忆点", interview_id)
            return

        # 保存到数据库
        from app.models.database import async_session, WeakPoint
        async with async_session() as db:
            for wp in weak_points:
                # 如果 category 不在可用分类中，取第一个或标记为"其他"
                cat = wp.get("category", "")
                if cat not in categories:
                    cat = categories[0] if categories else "其他"

                point = WeakPoint(
                    user_id=user_id,
                    interview_id=interview_id,
                    category=cat,
                    question_summary=wp.get("question_summary", ""),
                    weakness_desc=wp.get("weakness_desc", ""),
                    severity=min(max(int(wp.get("severity", 3)), 1), 5),
                )
                db.add(point)
            await db.commit()
            logger.info("面试 %s: 保存了 %d 条长期记忆", interview_id, len(weak_points))

    except json.JSONDecodeError as e:
        logger.error("记忆分析 JSON 解析失败: %s, 原始响应: %s", e, response.content[:300])
    except Exception as e:
        logger.error("记忆分析异常: %s", e, exc_info=True)
