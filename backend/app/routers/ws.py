import json
import re
import asyncio
import base64
import logging
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from langchain_core.messages import HumanMessage, AIMessage
from app.ai.engine import InterviewEngine
from app.ai.voice_engine import DoubaoVoiceEngine, AudioEvent, TextEvent, InterruptedEvent, SessionEndEvent, ErrorEvent
from app.models.database import async_session, Interview

logger = logging.getLogger("hakimeet.ws")
router = APIRouter()


@router.websocket("/ws/interview/{interview_id}")
async def interview_ws(websocket: WebSocket, interview_id: str):
    await websocket.accept()
    logger.info("WebSocket 已连接, interview_id=%s", interview_id)

    # 等待首条初始化消息
    init_msg = await websocket.receive_text()
    logger.info("收到初始化消息: %s", init_msg)

    engine = InterviewEngine(interview_id)
    await engine.initialize()
    system_prompt = engine._build_system_prompt()
    logger.info("System prompt 长度: %d, RAG上下文: %s", len(system_prompt), engine.rag_context[:100])

    voice = DoubaoVoiceEngine()
    try:
        await voice.connect(system_prompt, voice_config=engine.voice_config)
    except Exception as e:
        error_str = str(e)
        user_msg = "语音服务连接失败，请检查网络后重试"
        if "quota exceeded" in error_str.lower():
            user_msg = "AI 语音服务配额已用尽 (Quota Exceeded)，请检查您的豆包 API 账户余额或配额设置。"
        elif "Code:" in error_str:
            user_msg = f"语音服务启动失败: {error_str}"
            
        logger.error("豆包语音连接失败: %s", error_str)
        await websocket.send_json({"type": "error", "data": {"message": user_msg}})
        await websocket.close()
        return
    greeting = "你好，我是今天的面试官。请先做一个简单的自我介绍吧。"
    await voice.say_hello(greeting)
    engine.history.append(AIMessage(content=greeting))
    logger.info("say_hello 已发送")

    async def forward_doubao_to_client():
        """后台任务：豆包返回 → 前端"""
        try:
            async for event in voice.receive_loop():
                if isinstance(event, TextEvent):
                    logger.info("收到对话文本 [%s]: %s", event.role, event.text[:100])
                    if event.role == 'user':
                        engine.history.append(HumanMessage(content=event.text))
                        await websocket.send_json({
                            "type": "user_text",
                            "data": {"text": event.text},
                        })
                        
                        # 动态 RAG 注入 + 面试官工具调用
                        try:
                            engine.turn_count += 1
                            # 工具1：相似检索 + 随机出题 + 策略指引
                            tools_context = engine.get_interviewer_tools_context(event.text)
                            # 工具2：基础 RAG 检索
                            turn_context = await engine.get_turn_context(event.text)
                            # 合并注入
                            combined = "\n\n".join(filter(None, [turn_context, tools_context]))
                            if combined:
                                logger.info("触发动态 RAG + 工具注入, 长度: %d", len(combined))
                                await voice.send_rag_context(combined)
                        except Exception as e:
                            logger.error("动态 RAG/工具注入失败: %s", e)
                    else:
                        engine.history.append(AIMessage(content=event.text))
                        await websocket.send_json({
                            "type": "ai_text",
                            "data": {"text": event.text},
                        })
                elif isinstance(event, AudioEvent):
                    audio_b64 = base64.b64encode(event.audio).decode()
                    await websocket.send_json({
                        "type": "ai_audio",
                        "data": {"audio": audio_b64},
                    })
                elif isinstance(event, InterruptedEvent):
                    logger.info("转发打断事件到前端")
                    await websocket.send_json({"type": "interrupted", "data": {}})
                elif isinstance(event, SessionEndEvent):
                    logger.info("会话结束事件")
                    break
                elif isinstance(event, ErrorEvent):
                    await websocket.send_json({"type": "error", "data": {"message": event.message}})
        except Exception as e:
            logger.error("forward_doubao_to_client 异常: %s", e)

    recv_task = asyncio.create_task(forward_doubao_to_client())

    try:
        while True:
            msg = await websocket.receive()

            if msg.get("bytes"):
                await voice.send_audio(msg["bytes"])
            elif msg.get("text"):
                data = json.loads(msg["text"])
                logger.info("收到客户端控制消息: %s", data)
                if data["type"] == "control":
                    action = data["data"]["action"]
                    if action == "end":
                        # 先关闭语音引擎，避免 recv_task 干扰
                        recv_task.cancel()
                        try:
                            await recv_task
                        except asyncio.CancelledError:
                            pass
                        await voice.close()
                        logger.info("语音引擎已关闭，开始生成报告")

                        report = await engine.end_interview()
                        await websocket.send_json({"type": "report", "data": report})

                        # 持久化到数据库
                        user_id = engine.interview_obj.user_id if engine.interview_obj else "demo-user"
                        categories = engine.interview_obj.qb_categories if engine.interview_obj else []
                        await _save_report(interview_id, report, engine.history, user_id, categories)
                        break
    except WebSocketDisconnect:
        logger.info("客户端 WebSocket 断开")
    finally:
        if not recv_task.done():
            recv_task.cancel()
            try:
                await recv_task
            except asyncio.CancelledError:
                pass
        try:
            await voice.close()
        except Exception:
            pass
        logger.info("面试会话清理完成")


async def _save_report(interview_id: str, report: dict, history: list, user_id: str = "demo-user", categories: list = None):
    """将报告和对话轮次持久化到数据库，并触发长期记忆分析"""
    try:
        summary = report.get("summary", "")
        score = None
        m = re.search(r'(?:总体评分|总体成绩|综合评分|评分|得分)[*\s]*[（(：:\s-]*(\d+(?:\.\d+)?)', summary)
        if m:
            score = float(m.group(1))

        # 从 history 提取问答轮次
        turns = []
        turn_num = 0
        pending_q = None
        for msg in history:
            if isinstance(msg, AIMessage):
                pending_q = msg.content
            elif isinstance(msg, HumanMessage) and pending_q:
                turn_num += 1
                turns.append({
                    "interview_id": interview_id,
                    "turn_number": turn_num,
                    "ai_question": pending_q,
                    "user_answer": msg.content,
                })
                pending_q = None

        report["turn_count"] = turn_num

        async with async_session() as db:
            await db.execute(
                Interview.__table__.update()
                .where(Interview.id == interview_id)
                .values(
                    status="completed",
                    report=report,
                    overall_score=score,
                    ended_at=datetime.utcnow(),
                )
            )
            if turns:
                from app.models.database import InterviewTurn
                await db.execute(InterviewTurn.__table__.insert(), turns)
            await db.commit()
            logger.info("报告已保存, interview_id=%s, score=%s, turns=%d", interview_id, score, turn_num)

        # 异步触发长期记忆分析（不阻塞报告返回）
        asyncio.create_task(_analyze_memory(interview_id, user_id, history, categories or []))

    except Exception as e:
        logger.error("保存报告失败: %s", e)


async def _analyze_memory(interview_id: str, user_id: str, history: list, categories: list):
    """异步分析面试薄弱点并保存到长期记忆"""
    try:
        from app.ai.memory import analyze_and_save
        await analyze_and_save(interview_id, user_id, history, categories)
    except Exception as e:
        logger.error("长期记忆分析失败: %s", e)
