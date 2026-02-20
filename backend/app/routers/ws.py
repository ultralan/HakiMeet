import json
import asyncio
import base64
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.ai.engine import InterviewEngine
from app.ai.voice_engine import DoubaoVoiceEngine, AudioEvent, InterruptedEvent, SessionEndEvent

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
        await voice.connect(system_prompt)
    except (ConnectionError, TimeoutError, OSError) as e:
        logger.error("豆包语音连接失败: %s", e)
        await websocket.send_json({"type": "error", "data": {"message": "语音服务连接失败，请检查网络后重试"}})
        await websocket.close()
        return
    await voice.send_rag_context(engine.rag_context)
    await voice.say_hello("你好，我是今天的面试官。请先做一个简单的自我介绍吧。")
    logger.info("say_hello 已发送")

    async def forward_doubao_to_client():
        """后台任务：豆包返回 → 前端"""
        try:
            async for event in voice.receive_loop():
                if isinstance(event, AudioEvent):
                    audio_b64 = base64.b64encode(event.audio).decode()
                    logger.info("转发音频到前端: %d bytes (base64: %d)", len(event.audio), len(audio_b64))
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
        except Exception as e:
            logger.error("forward_doubao_to_client 异常: %s", e)

    recv_task = asyncio.create_task(forward_doubao_to_client())

    try:
        while True:
            msg = await websocket.receive()

            if msg.get("bytes"):
                # 二进制帧 = 麦克风音频，转发给豆包
                await voice.send_audio(msg["bytes"])
            elif msg.get("text"):
                data = json.loads(msg["text"])
                logger.info("收到客户端控制消息: %s", data)
                if data["type"] == "control":
                    action = data["data"]["action"]
                    if action == "end":
                        report = await engine.end_interview()
                        await websocket.send_json({"type": "report", "data": report})
                        break
    except WebSocketDisconnect:
        logger.info("客户端 WebSocket 断开")
    finally:
        recv_task.cancel()
        await voice.close()
        logger.info("面试会话清理完成")
