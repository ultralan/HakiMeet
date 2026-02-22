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
        from app.models.database import async_session, Interview
        from sqlalchemy import select
        async with async_session() as session:
            result = await session.execute(select(Interview).where(Interview.id == self.interview_id))
            self.interview_obj = result.scalar_one_or_none()
        self.rag_context = await self.rag.get_context(self.interview_id)

    async def get_turn_context(self, user_input: str) -> str:
        """根据用户当前的回答，去题库中匹配最相关的题目/答案"""
        if not self.interview_obj or not self.interview_obj.qb_categories:
            return ""
        
        # 构建过滤器：只在当前选中的分类中找
        categories = self.interview_obj.qb_categories
        if len(categories) == 1:
            where = {"$and": [{"type": "question_bank"}, {"category": categories[0]}]}
        else:
            where = {"$and": [
                {"type": "question_bank"},
                {"category": {"$in": categories}}
            ]}
            
        context = await self.rag.search(user_input, k=3, where=where)
        return context

    def _build_system_prompt(self) -> str:
        return (
            "你是一位犀利且专业的资深技术面试官，正在进行模拟面试。你的目标是精准发现并指出候选人的技术漏洞，帮助其在真实面试中避免失分。\n\n"
            "【核心职责】\n"
            "1. **严格参考题库**：下方提供了该面试选定的题库内容。你应该优先从中挑选题目进行提问。如果候选人的回答触及了题库中的知识点，你应该结合题库中的参考答案进行点评。\n"
            "2. **有错必究（重点）**：对于候选人回答中的任何错误、模糊不清点或逻辑漏洞，你必须毫不留情地立即明确指出。如果候选人的回答与题库中的标准答案不符，必须给出正确的纠正。\n"
            "3. **简历针对性**：参考候选人的简历信息，询问相关的项目经验或技术栈，并对其表述的真实性和深度进行考察。\n\n"
            "【交互方式】\n"
            "候选人每次回答后，你必须按以下逻辑进行反馈：\n"
            "- **纠错优先**：如果回答有错，第一句话就指出错误点并给出正确解释。\n"
            "- **深度评估**：评价回答的深度（是停留在表面还是掌握了原理），指出回答中的薄弱环节。\n"
            "- **深挖追问**：针对不确定的点进行连环追问，直到探明候选人的底细。\n"
            "- **换题过渡**：仅在当前话题已经透彻或无法继续挖掘时，才切换到题库中的下一个话题。\n\n"
            "【基本规则】\n"
            "- 不要做一个只会点头的老好人，要通过质疑和纠错来模拟真实的面试压力\n"
            "- 语气专业且有压迫感，类似顶级大厂的面试风格\n"
            "- 用中文交流\n\n"
            f"【面试参考资料（抽样预览）】\n{self.rag_context}\n\n"
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
