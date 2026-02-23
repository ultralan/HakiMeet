from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "HakiMeet"
    database_url: str = "sqlite+aiosqlite:///./hakimeet.db"
    secret_key: str = "dev-secret-change-in-production"
    # 豆包文本模型（火山方舟）
    doubao_api_key: str = "0d964ae8-626d-4d73-a0b3-5a3f858a009c"
    doubao_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    doubao_model_id: str = "doubao-1-5-lite-32k-250115"
    # 豆包语音大模型
    doubao_voice_ws_url: str = "wss://openspeech.bytedance.com/api/v3/realtime/dialogue"
    doubao_voice_app_id: str = "7720414312"
    doubao_voice_access_key: str = "-VRgLfKtKSjklM-3ZNgobJUr7fjPh5kD"
    doubao_voice_secret_key: str = "rWdy_Penc97S_PP4jLbSKyHVAzAcj9bJ"
    doubao_voice_resource_id: str = "volc.speech.dialog"
    doubao_voice_app_key: str = "PlgvMymc7f3tQnJ6"
    chroma_persist_dir: str = "./chroma_db"
    knowledge_base_dir: str = "./knowledge_base"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    class Config:
        env_file = ".env"


settings = Settings()
