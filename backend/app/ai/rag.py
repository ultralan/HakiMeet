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

        # 题库检索
        for cat in (interview.qb_categories or []):
            docs = self.vectorstore.similarity_search(
                cat, k=5,
                filter={"$and": [{"type": "question_bank"}, {"category": cat}]},
            )
            if docs:
                parts.append(f"【{cat}题库】\n" + "\n\n".join(d.page_content for d in docs))

        return "\n\n".join(parts) if parts else "暂无面试参考资料，请进行通用技术面试。"
