from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader

from app.config import settings


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

    async def search(self, query: str, k: int = 5) -> str:
        """检索相关文档，返回拼接文本"""
        docs = self.vectorstore.similarity_search(query, k=k)
        return "\n\n".join(doc.page_content for doc in docs)

    async def get_context(self, interview_id: str) -> str:
        """根据面试ID获取RAG上下文（按resume_id精确过滤）"""
        from app.models.database import async_session, Interview
        from sqlalchemy import select

        async with async_session() as session:
            result = await session.execute(
                select(Interview.resume_id).where(Interview.id == interview_id)
            )
            resume_id = result.scalar_one_or_none()

        if not resume_id:
            return "暂无候选人资料，请进行通用技术面试。"

        docs = self.vectorstore.similarity_search(
            "简历 技术 经验", k=5,
            filter={"resume_id": resume_id},
        )
        if not docs:
            return "暂无候选人资料，请进行通用技术面试。"
        return "\n\n".join(doc.page_content for doc in docs)
