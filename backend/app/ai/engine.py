from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.config import settings
from app.ai.rag import get_rag


class InterviewEngine:
    """Phase 1: 纯文本面试对话引擎"""

    def __init__(self, interview_id: str):
        self.interview_id = interview_id
        self.history: list = []
        self.turn_count = 0
        self.rag = get_rag()
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
            "你是一位资深的技术面试官，正在进行模拟面试。你的目标是帮助候选人提升面试能力。\n\n"
            "【交互方式】\n"
            "候选人每次回答后，你应该自然地做以下一项或多项：\n"
            "- 简短点评：指出回答中的亮点或不足（1-2句话）\n"
            "- 知识补充：如果回答有遗漏，补充关键知识点\n"
            "- 深挖追问：回答较浅时，追问细节或原理\n"
            "- 换题过渡：回答充分后，自然过渡到下一个话题\n"
            "不要每次都追问，也不要每次都换题，根据回答质量灵活决定。\n\n"
            "【基本规则】\n"
            "- 每次只聚焦一个问题方向\n"
            "- 难度从基础逐步递进\n"
            "- 语气专业友好，像真实面试中的对话\n"
            "- 用中文交流\n\n"
            f"【面试参考资料】\n{self.rag_context}\n\n"
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
        if len(self.history) <= 1:
            return {"summary": "面试对话记录不足，无法生成评价报告。请确保完成至少一轮问答后再结束面试。"}

        msgs = [
            SystemMessage(content=(
                "你是面试评价专家。请严格根据以下真实面试对话记录生成评价报告。\n"
                "禁止编造任何不存在的对话内容，只基于实际对话进行评价。\n"
                "报告格式：总体评分(0-100)、各维度评分(0-100)、优势、待改进点。"
            )),
            *self.history,
        ]
        response = await self.llm.ainvoke(msgs)
        return {"summary": response.content}
