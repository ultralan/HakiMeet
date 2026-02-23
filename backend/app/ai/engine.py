import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.config import settings
from app.ai.rag import get_rag


class InterviewEngine:
    """面试引擎：管理 RAG 上下文、薄弱点注入、报告生成（对话交互由语音引擎负责）"""

    def __init__(self, interview_id: str):
        self.interview_id = interview_id
        self.history: list = []
        self.turn_count = 0
        self.rag = get_rag()
        self.weak_points_text = ""
        self.voice_config = None  # 用户自定义语音配置，会在 initialize() 中加载
        self.llm = None  # 会在 initialize() 中根据用户配置创建

    async def initialize(self):
        """加载面试上下文（简历+岗位+长期记忆）并加载用户 AI 模型配置"""
        from app.models.database import async_session, Interview, WeakPoint, AIModelConfig
        from sqlalchemy import select
        async with async_session() as session:
            result = await session.execute(select(Interview).where(Interview.id == self.interview_id))
            self.interview_obj = result.scalar_one_or_none()
            
            logger = logging.getLogger("hakimeet.engine")
            logger.info("初始化面试引擎: ID=%s, 分类=%s", 
                        self.interview_id, 
                        self.interview_obj.qb_categories if self.interview_obj else "None")

            # 加载用户长期记忆
            categories = []
            if self.interview_obj:
                categories = self.interview_obj.qb_categories or []
                if categories:
                    wp_result = await session.execute(
                        select(WeakPoint).where(
                            WeakPoint.user_id == self.interview_obj.user_id,
                            WeakPoint.resolved == False,
                            WeakPoint.category.in_(categories),
                        ).order_by(WeakPoint.severity.desc()).limit(10)
                    )
                    weak_points = wp_result.scalars().all()
                    if weak_points:
                        lines = []
                        for wp in weak_points:
                            lines.append(f"- 【{wp.category}】{wp.question_summary}（{wp.weakness_desc}，严重程度{wp.severity}/5）")
                        self.weak_points_text = "\n".join(lines)

            # 加载用户 AI 模型配置
            user_id = self.interview_obj.user_id if self.interview_obj else "demo-user"
            cfg_result = await session.execute(
                select(AIModelConfig).where(
                    AIModelConfig.user_id == user_id
                )
            )
            ai_cfg = cfg_result.scalar_one_or_none()

            # 创建 LLM 实例
            if ai_cfg and ai_cfg.llm_enabled and ai_cfg.api_key and ai_cfg.base_url and ai_cfg.model_id:
                logger.info("使用用户自定义文本模型: %s @ %s", ai_cfg.model_id, ai_cfg.base_url)
                self.llm = ChatOpenAI(
                    model=ai_cfg.model_id,
                    openai_api_key=ai_cfg.api_key,
                    openai_api_base=ai_cfg.base_url,
                    streaming=True,
                    temperature=0.7,
                )
            else:
                logger.info("使用系统默认文本模型: %s", settings.doubao_model_id)
                self.llm = ChatOpenAI(
                    model=settings.doubao_model_id,
                    openai_api_key=settings.doubao_api_key,
                    openai_api_base=settings.doubao_base_url,
                    streaming=True,
                    temperature=0.7,
                )

            # 加载语音配置
            if ai_cfg and ai_cfg.voice_enabled:
                self.voice_config = {
                    "ws_url": ai_cfg.voice_ws_url,
                    "app_id": ai_cfg.voice_app_id,
                    "access_key": ai_cfg.voice_access_key,
                    "secret_key": ai_cfg.voice_secret_key,
                    "resource_id": ai_cfg.voice_resource_id,
                    "app_key": ai_cfg.voice_app_key,
                }
                logger.info("使用用户自定义语音配置")

        self.rag_context = await self.rag.get_context(self.interview_id, categories=categories)

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

    def get_interviewer_tools_context(self, user_input: str) -> str:
        """调用面试官工具，返回格式化的策略提示上下文"""
        if not self.interview_obj or not self.interview_obj.qb_categories:
            return ""

        categories = self.interview_obj.qb_categories
        parts = []

        # 工具1：相似检索 — 找到与当前话题相关的题目
        similar = self.rag.similar_search(user_input, categories, k=2)
        if similar:
            parts.append(f"【相关题目检索结果】\n{similar}")

        # 工具2：随机出题 — 准备一道备选题
        random_q = self.rag.random_question(categories)
        if random_q:
            parts.append(f"【备选随机题目】\n{random_q}")

        # 面试官策略指引
        parts.append(
            "【面试官行为指引】\n"
            "根据候选人刚才的回答，你可以选择以下策略之一：\n"
            "1. 深挖追问：如果回答不够深入，继续追问原理和细节\n"
            "2. 纠正错误：如果回答有误，先指出错误再给出正确答案\n"
            "3. 换题：如果当前话题已经充分考察，可以使用上面的相关题目或备选题目"
        )

        return "\n\n".join(parts)

    def _build_system_prompt(self) -> str:
        # 获取当前面试选择的分类
        categories = []
        if self.interview_obj and self.interview_obj.qb_categories:
            categories = self.interview_obj.qb_categories

        cat_str = "、".join(categories) if categories else "通用技术"

        prompt = (
            "你是一位犀利且专业的资深技术面试官，正在进行模拟面试。你的目标是精准发现并指出候选人的技术漏洞，帮助其在真实面试中避免失分。\n\n"
            f"【本场面试范围（重要）】\n"
            f"本次面试**仅限于**以下分类：{cat_str}。\n"
            f"你**必须严格**在这些分类范围内出题和追问，**禁止**跑到其他技术领域（如候选人选择的是 MySQL，就不要问 Redis、消息队列等无关话题）。\n"
            f"如果候选人在当前分类下的所有题目都答不上来，请对已问过的题目进行详细讲解和纠正，而不是跳到其他分类。\n\n"
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
            f"- 所有问题必须属于 {cat_str} 分类，不要偏离\n"
            "- 不要做一个只会点头的老好人，要通过质疑和纠错来模拟真实的面试压力\n"
            "- 语气专业且有压迫感，类似顶级大厂的面试风格\n"
            "- 用中文交流\n\n"
            f"【面试参考资料】\n{self.rag_context}\n\n"
        )

        # 注入长期记忆
        if self.weak_points_text:
            prompt += (
                "【用户长期记忆（重点考察）】\n"
                "以下是该候选人在之前面试中表现欠佳的知识点，请优先考察这些领域：\n"
                f"{self.weak_points_text}\n\n"
            )

        prompt += f"【当前进度】已问{self.turn_count}题"
        return prompt

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
