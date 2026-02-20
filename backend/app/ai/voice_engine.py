"""豆包语音大模型 WebSocket 客户端 - 基于官方二进制协议"""

import asyncio
import gzip
import json
import logging
import uuid
from dataclasses import dataclass

import websockets

from app.ai import protocol
from app.config import settings

logger = logging.getLogger("hakimeet.voice")


def _sanitize(text: str) -> str:
    """移除控制字符和 YAML 不安全字符，保留换行和空格"""
    text = text.replace('\\', '/').replace('\t', ' ')
    return "".join(c if c >= ' ' or c == '\n' else '' for c in text)


@dataclass
class AudioEvent:
    audio: bytes

@dataclass
class TextEvent:
    text: str
    role: str = "ai"  # "ai" or "user"

@dataclass
class InterruptedEvent:
    pass

@dataclass
class SessionEndEvent:
    pass

@dataclass
class ErrorEvent:
    message: str


class DoubaoVoiceEngine:
    """管理与豆包语音大模型 WS API 的连接，遵循官方二进制协议"""

    def __init__(self):
        self.ws = None
        self.session_id = str(uuid.uuid4())
        self._closed = False
        self._reconnecting = False
        self._audio_send_count = 0
        self._system_prompt = None

    def _build_request(self, event_id: int, payload_dict: dict, session: bool = True):
        """构建带官方二进制头的请求"""
        req = bytearray(protocol.generate_header())
        req.extend(event_id.to_bytes(4, 'big'))
        payload_bytes = gzip.compress(json.dumps(payload_dict).encode())
        if session:
            req.extend(len(self.session_id).to_bytes(4, 'big'))
            req.extend(self.session_id.encode())
        req.extend(len(payload_bytes).to_bytes(4, 'big'))
        req.extend(payload_bytes)
        return req

    def _build_audio_request(self, audio: bytes):
        """构建音频帧请求"""
        req = bytearray(protocol.generate_header(
            message_type=protocol.CLIENT_AUDIO_ONLY_REQUEST,
            serial_method=protocol.NO_SERIALIZATION,
        ))
        req.extend((200).to_bytes(4, 'big'))
        req.extend(len(self.session_id).to_bytes(4, 'big'))
        req.extend(self.session_id.encode())
        payload_bytes = gzip.compress(audio)
        req.extend(len(payload_bytes).to_bytes(4, 'big'))
        req.extend(payload_bytes)
        return req

    async def connect(self, system_prompt: str, retries: int = 2):
        """建立连接，完成 StartConnection + StartSession"""
        self._system_prompt = system_prompt
        logger.info("正在连接豆包语音 API: %s", settings.doubao_voice_ws_url)
        headers = {
            "X-Api-App-ID": settings.doubao_voice_app_id,
            "X-Api-Access-Key": settings.doubao_voice_access_key,
            "X-Api-Resource-Id": settings.doubao_voice_resource_id,
            "X-Api-App-Key": settings.doubao_voice_app_key,
            "X-Api-Connect-Id": str(uuid.uuid4()),
        }
        last_err = None
        for attempt in range(1, retries + 1):
            try:
                self.ws = await websockets.connect(
                    settings.doubao_voice_ws_url,
                    additional_headers=headers,
                    ping_interval=None,
                    open_timeout=20,
                )
                logger.info("WebSocket 连接已建立 (第%d次尝试)", attempt)
                break
            except (TimeoutError, OSError) as e:
                last_err = e
                logger.warning("连接豆包超时 (第%d/%d次): %s", attempt, retries, e)
                if attempt < retries:
                    await asyncio.sleep(1)
        else:
            raise ConnectionError(f"豆包语音 API 连接失败 ({retries}次重试后): {last_err}") from last_err

        # StartConnection (event=1)
        await self.ws.send(self._build_request(1, {}, session=False))
        resp = await self.ws.recv()
        logger.info("StartConnection 响应: %s", protocol.parse_response(resp))

        # StartSession (event=100)
        session_config = {
            "asr": {
                "audio_config": {"channel": 1, "format": "pcm_s16le", "sample_rate": 16000},
                "extra": {"end_smooth_window_ms": 1500},
            },
            "tts": {
                "speaker": "zh_male_yunzhou_jupiter_bigtts",
                "audio_config": {"channel": 1, "format": "pcm_s16le", "sample_rate": 24000},
            },
            "dialog": {
                "bot_name": "面试官",
                "system_role": _sanitize(system_prompt),
                "speaking_style": "你的说话风格专业严谨，语速适中，语调自然。",
                "extra": {
                    "recv_timeout": 30,
                    "input_mod": "audio",
                },
            },
        }
        await self.ws.send(self._build_request(100, session_config))
        resp = await self.ws.recv()
        logger.info("StartSession 响应: %s", protocol.parse_response(resp))

    async def _reconnect(self):
        """出错后自动重连"""
        self._reconnecting = True
        logger.info("正在重连豆包语音...")
        try:
            await self.ws.close()
        except Exception:
            pass
        self.session_id = str(uuid.uuid4())
        self._audio_send_count = 0
        await self.connect(self._system_prompt)
        self._reconnecting = False

    async def say_hello(self, content: str):
        """发送开场白 (event=300)"""
        await self.ws.send(self._build_request(300, {"content": content}))

    async def send_audio(self, data: bytes):
        """转发音频二进制帧 (event=200)"""
        if self.ws and not self._closed and not self._reconnecting:
            self._audio_send_count += 1
            if self._audio_send_count % 50 == 1:
                logger.info("发送音频帧 #%d: %d bytes", self._audio_send_count, len(data))
            try:
                await self.ws.send(self._build_audio_request(data))
            except websockets.ConnectionClosed:
                logger.warning("send_audio: 连接已关闭，等待重连")

    async def send_rag_context(self, rag_text: str):
        """发送 RAG 外部知识 (event=502)"""
        if self.ws and not self._closed:
            logger.info("发送 RAG 上下文: %d 字符", len(rag_text))
            await self.ws.send(self._build_request(502, {"external_rag": _sanitize(rag_text)}))

    async def receive_loop(self):
        """异步生成器，解析官方二进制协议，yield 事件"""
        if not self.ws:
            logger.warning("receive_loop: ws 未连接")
            return
        logger.info("receive_loop 已启动，等待豆包消息...")
        ai_chunks = []
        last_user_text = ""
        while not self._closed:
          try:
            async for message in self.ws:
                if self._closed:
                    break
                resp = protocol.parse_response(message)
                if not resp:
                    continue

                msg_type = resp.get('message_type')
                event = resp.get('event')

                if msg_type == 'SERVER_ACK' and isinstance(resp.get('payload_msg'), bytes):
                    yield AudioEvent(audio=resp['payload_msg'])
                elif msg_type == 'SERVER_FULL_RESPONSE':
                    payload = resp.get('payload_msg', {})
                    if not isinstance(payload, dict):
                        payload = {}

                    if event == 550:
                        # AI 文本流式分词
                        chunk = payload.get('content', '')
                        if chunk:
                            ai_chunks.append(chunk)
                    elif event == 559:
                        # AI 回复结束 → yield 完整 AI 文本
                        if ai_chunks:
                            full = ''.join(ai_chunks)
                            ai_chunks.clear()
                            logger.info("AI 完整回复: %s", full[:100])
                            yield TextEvent(text=full, role='ai')
                    elif event == 451:
                        # 用户 ASR 流式更新
                        origin = payload.get('extra', {}).get('origin_text', '')
                        if origin:
                            last_user_text = origin
                    elif event == 459:
                        # 用户说完 → yield 用户文本
                        if last_user_text:
                            logger.info("用户语音转写: %s", last_user_text[:100])
                            yield TextEvent(text=last_user_text, role='user')
                            last_user_text = ""
                    elif event == 450:
                        ai_chunks.clear()
                        yield InterruptedEvent()
                    elif event in (152, 153):
                        yield SessionEndEvent()
                        return
                elif msg_type == 'SERVER_ERROR_RESPONSE':
                    logger.error("豆包错误: %s", resp)
                    yield ErrorEvent(message=resp.get('payload_msg', {}).get('error', '语音服务异常'))
                    break  # 跳出内层循环，触发重连
            else:
                return  # ws 正常结束，不重连
            # 内层 break 到这里 → 尝试重连
            if self._closed:
                return
            try:
                await self._reconnect()
                ai_chunks.clear()
                last_user_text = ""
            except Exception as e:
                logger.error("重连失败: %s", e)
                return
          except websockets.ConnectionClosed as e:
            logger.warning("豆包 WebSocket 断开: %s, 尝试重连", e)
            try:
                await self._reconnect()
                ai_chunks.clear()
                last_user_text = ""
            except Exception:
                logger.error("断线重连失败")
                return

    async def finish(self):
        """FinishSession(102) + FinishConnection(2)"""
        if not self.ws or self._closed:
            return
        self._closed = True
        try:
            await self.ws.send(self._build_request(102, {}))
            # 等待 session finished 事件
            for _ in range(50):
                try:
                    resp = protocol.parse_response(await self.ws.recv())
                    if resp.get('event') in (152, 153):
                        break
                except Exception:
                    break

            # FinishConnection (event=2)
            req = bytearray(protocol.generate_header())
            req.extend((2).to_bytes(4, 'big'))
            payload = gzip.compress(b'{}')
            req.extend(len(payload).to_bytes(4, 'big'))
            req.extend(payload)
            await self.ws.send(req)
            await self.ws.recv()
        except Exception:
            pass

    async def close(self):
        """关闭连接"""
        await self.finish()
        if self.ws:
            await self.ws.close()
