"""RAG 管线 —— 统一的向量检索和文档管理

职责：
  1. 文档入库（简历 / 题库 / PDF）
  2. 相似检索（按分类过滤）
  3. 随机出题
  4. 初始化上下文（简历 + 题库预览）
"""

import logging
import random
import re

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from app.config import settings

logger = logging.getLogger("hakimeet.rag")

_rag_instance = None


def get_rag() -> "RAGPipeline | None":
    global _rag_instance
    if _rag_instance is None:
        try:
            _rag_instance = RAGPipeline()
        except Exception:
            logger.exception("RAG 初始化失败，将以无向量检索模式继续运行")
            return None
    return _rag_instance


# ─────────────────── 工具函数 ───────────────────

def _build_qb_filter(categories: list[str]) -> dict:
    """构建题库分类过滤条件（统一入口，避免各处重复构建）"""
    if len(categories) == 1:
        return {"$and": [{"type": "question_bank"}, {"category": categories[0]}]}
    return {"$and": [
        {"type": "question_bank"},
        {"category": {"$in": list(categories)}},
    ]}


# ─────────────────── 核心类 ───────────────────

class RAGPipeline:

    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-zh-v1.5",
        )
        self.vectorstore = Chroma(
            persist_directory=settings.chroma_persist_dir,
            embedding_function=self.embeddings,
        )
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=50
        )

    # ─────────── 入库 ───────────

    async def ingest_text(self, text: str, metadata: dict | None = None):
        """将文本分块后存入向量库"""
        docs = self._splitter.create_documents(
            [text], metadatas=[metadata or {}]
        )
        self.vectorstore.add_documents(docs)

    async def ingest_questions(self, text: str, metadata: dict | None = None):
        """按问答边界切割题库：含问号且前面有≥2行无问号的答案时，视为新题开始"""
        lines = text.split('\n')
        parts, buf = [], []
        for line in lines:
            has_q = '？' in line or '?' in line
            if has_q and buf:
                tail = sum(1 for prev in reversed(buf) if '？' not in prev and '?' not in prev)
                if tail >= 2:
                    parts.append('\n'.join(buf))
                    buf = []
            buf.append(line)
        if buf:
            parts.append('\n'.join(buf))
        chunks = [p.strip() for p in parts if p.strip() and len(p.strip()) > 20]
        if not chunks:
            return await self.ingest_text(text, metadata)
        docs = [Document(page_content=c, metadata=metadata or {}) for c in chunks]
        self.vectorstore.add_documents(docs)

    async def ingest_pdf(self, pdf_path: str, metadata: dict | None = None):
        """解析 PDF 并存入向量库"""
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        chunks = self._splitter.split_documents(pages)
        for chunk in chunks:
            chunk.metadata.update(metadata or {})
        self.vectorstore.add_documents(chunks)

    # ─────────── 检索 ───────────

    def search_docs(self, query: str, k: int = 3, where: dict | None = None) -> list[Document]:
        """核心检索：返回 Document 列表（所有检索的唯一入口）"""
        return self.vectorstore.similarity_search(query, k=k, filter=where)

    def search_qb(self, query: str, categories: list[str], k: int = 3) -> list[Document]:
        """从指定分类的题库中检索相关题目"""
        if not categories:
            return []
        return self.search_docs(query, k=k, where=_build_qb_filter(categories))

    def random_question(self, categories: list[str]) -> str | None:
        """从指定分类中随机抽取一道题，返回题目文本"""
        valid_cats = list(categories or [])
        random.shuffle(valid_cats)
        for cat in valid_cats:
            results = self.vectorstore._collection.get(
                where=_build_qb_filter([cat]),
                include=["documents"],
            )
            if results["documents"]:
                chosen = random.choice(results["documents"])
                return f"【{cat}】{chosen}"
        return None

    # ─────────── 元数据操作 ───────────

    def get_chunks_by_metadata(self, where: dict) -> list[dict]:
        """按 metadata 精确查询文本块"""
        results = self.vectorstore._collection.get(where=where, include=["documents", "metadatas"])
        return [
            {"content": doc, "metadata": meta}
            for doc, meta in zip(results["documents"], results["metadatas"])
        ]

    def delete_by_metadata(self, where: dict):
        """按 metadata 删除向量数据"""
        ids = self.vectorstore._collection.get(where=where)["ids"]
        if ids:
            self.vectorstore._collection.delete(ids=ids)

    # ─────────── 初始化上下文 ───────────

    async def build_init_context(self, interview_id: str, categories: list[str]) -> str:
        """构建面试初始化上下文：题库预览 + 简历摘要"""
        from app.models.database import async_session, Interview
        from sqlalchemy import select

        async with async_session() as session:
            result = await session.execute(
                select(Interview).where(Interview.id == interview_id)
            )
            interview = result.scalar_one_or_none()

        if not interview:
            return ""

        parts = []

        # 题库预览：每个分类随机抽 3 题
        if categories:
            for cat in categories:
                results = self.vectorstore._collection.get(
                    where=_build_qb_filter([cat]),
                    include=["documents"],
                )
                docs = results["documents"]
                if docs:
                    samples = random.sample(docs, min(len(docs), 3))
                    content = "\n".join(f"- {s}" for s in samples)
                    parts.append(f"【{cat}题库预览】\n{content}")

        # 简历检索
        if interview.resume_id:
            docs = self.search_docs(
                "简历 技术 经验", k=5,
                where={"resume_id": interview.resume_id},
            )
            if docs:
                parts.append("【候选人简历信息】\n" + "\n\n".join(d.page_content for d in docs))

        return "\n\n".join(parts) if parts else ""
