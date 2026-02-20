import re

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader

from app.config import settings

_rag_instance = None


def get_rag() -> "RAGPipeline":
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGPipeline()
    return _rag_instance


class RAGPipeline:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-zh-v1.5",
        )
        self.vectorstore = Chroma(
            persist_directory=settings.chroma_persist_dir,
            embedding_function=self.embeddings,
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=50
        )

    async def ingest_text(self, text: str, metadata: dict | None = None):
        """将文本分块后存入向量库"""
        docs = self.splitter.create_documents(
            [text], metadatas=[metadata or {}]
        )
        self.vectorstore.add_documents(docs)

    async def ingest_questions(self, text: str, metadata: dict | None = None):
        """按问答边界切割题库：当含？的行前面有≥2行无？的答案内容时，视为新题开始"""
        lines = text.split('\n')
        parts, buf = [], []
        for line in lines:
            has_q = '？' in line or '?' in line
            if has_q and buf:
                # 统计 buf 末尾连续无问号的行数（即答案行数）
                tail = 0
                for prev in reversed(buf):
                    if '？' not in prev and '?' not in prev:
                        tail += 1
                    else:
                        break
                if tail >= 2:
                    parts.append('\n'.join(buf))
                    buf = []
            buf.append(line)
        if buf:
            parts.append('\n'.join(buf))
        chunks = [p.strip() for p in parts if p.strip() and len(p.strip()) > 20]
        if not chunks:
            return await self.ingest_text(text, metadata)
        from langchain_core.documents import Document
        docs = [Document(page_content=c, metadata=metadata or {}) for c in chunks]
        self.vectorstore.add_documents(docs)

    async def ingest_pdf(self, pdf_path: str, metadata: dict | None = None):
        """解析PDF并存入向量库"""
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        chunks = self.splitter.split_documents(pages)
        for chunk in chunks:
            chunk.metadata.update(metadata or {})
        self.vectorstore.add_documents(chunks)

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

    async def search(self, query: str, k: int = 5) -> str:
        """检索相关文档，返回拼接文本"""
        docs = self.vectorstore.similarity_search(query, k=k)
        return "\n\n".join(doc.page_content for doc in docs)

    async def get_context(self, interview_id: str) -> str:
        """根据面试ID获取RAG上下文（简历+题库）"""
        from app.models.database import async_session, Interview
        from sqlalchemy import select

        async with async_session() as session:
            result = await session.execute(
                select(Interview).where(Interview.id == interview_id)
            )
            interview = result.scalar_one_or_none()

        if not interview:
            return "暂无面试参考资料，请进行通用技术面试。"

        parts = []

        # 简历检索
        if interview.resume_id:
            docs = self.vectorstore.similarity_search(
                "简历 技术 经验", k=5,
                filter={"resume_id": interview.resume_id},
            )
            if docs:
                parts.append("【简历信息】\n" + "\n\n".join(d.page_content for d in docs))

        # 题库：按分类均匀抽取，限制总长度避免 prompt 过长
        import random
        categories = interview.qb_categories or []
        if categories:
            per_cat = max(3, 15 // len(categories))
            for cat in categories:
                chunks = self.get_chunks_by_metadata(
                    {"$and": [{"type": "question_bank"}, {"category": cat}]}
                )
                if chunks:
                    sampled = random.sample(chunks, min(per_cat, len(chunks)))
                    parts.append(f"【{cat}题库（抽取{len(sampled)}/{len(chunks)}题）】\n" + "\n\n".join(c["content"] for c in sampled))
            # 总长度硬上限
            full = "\n\n".join(parts)
            if len(full) > 4000:
                full = full[:4000]
            return full if parts else "暂无面试参考资料，请进行通用技术面试。"

        return "\n\n".join(parts) if parts else "暂无面试参考资料，请进行通用技术面试。"
