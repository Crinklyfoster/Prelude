from pydantic import BaseModel


class ProviderStatus(BaseModel):
    ollama: bool
    gemini: bool
    groq: bool


class AdminSettingsResponse(BaseModel):
    version: str
    chat_model: str
    embedding_model: str
    retrieval_mode: str
    top_k: int
    chunk_size: int
    chunk_overlap: int
    query_rewrite: bool
    reranker: bool
    jwt_algorithm: str
    jwt_expire_minutes: int
    providers: ProviderStatus
