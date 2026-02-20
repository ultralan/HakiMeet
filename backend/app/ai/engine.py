from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.config import settings
from app.ai.rag import RAGPipeline


class InterviewEngine:
    """Phase 1: 纯文本面试对话引擎"""

    def __init__(self, interview_id: str):
        self.interview_id = interview_id
        self.history: list = []
        self.turn_count = 0
        self.rag = RAGPipeline()
        self.llm = ChatOpenAI(
            model=settings.doubao_model_id,
            openai_api_key=settings.doubao_api_key,
            openai_api_base=settings.doubao_base_url,
            streaming=True,
            temperature=0.7,
        )

    async def initialize(self):
        """加载面试上下文（简历+岗位信息）"""
        self.rag_context = await self.rag.get_context(self.interview_id)

    def _build_system_prompt(self) -> str:
        return (
            "你是一位资深的技术面试官，正在对候选人进行模拟面试。\n\n"
            "【面试规则】\n"
            "- 每次只问一个问题\n"
            "- 根据候选人回答深度决定是否追问\n"
            "- 难度从基础逐步递进\n"
            "- 保持专业但友好的语气\n"
            "- 用中文交流\n\n"
            f"【候选人信息与岗位要求】\n{self.rag_context}\n\n"
            f"【当前进度】已问{self.turn_count}题"
        )

    async def get_opening(self) -> str:
        msgs = [
            SystemMessage(content=self._build_system_prompt()),
            HumanMessage(content="请开始面试，先做自我介绍然后问第一个问题。"),
        ]
        response = await self.llm.ainvoke(msgs)
        self.history.append(AIMessage(content=response.content))
        return response.content

    async def chat(self, user_input: str):
        """流式对话，yield每个文本块"""
        self.turn_count += 1
        self.history.append(HumanMessage(content=user_input))

        msgs = [
            SystemMessage(content=self._build_system_prompt()),
            *self.history,
        ]

        full_response = ""
        async for chunk in self.llm.astream(msgs):
            if chunk.content:
                full_response += chunk.content
                yield chunk.content

        self.history.append(AIMessage(content=full_response))

    async def end_interview(self) -> dict:
        """结束面试，生成评价报告"""
        msgs = [
            SystemMessage(content=(
                "请根据以下面试对话，生成面试评价报告。"
                "包含：总体评分(0-10)、各维度评分、优势、待改进点。"
            )),
            *self.history,
        ]
        response = await self.llm.ainvoke(msgs)
        return {"summary": response.content}
