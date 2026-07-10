from app.core.config import settings
from app.schemas.admin_settings import (
    AdminSettingsResponse,
    ProviderStatus,
)


class SettingsService:
    _provider = settings.LLM_PROVIDER
    _model = settings.CHAT_MODEL

    @classmethod
    def get_provider(cls) -> str:
        return cls._provider

    @classmethod
    def get_model(cls) -> str:
        return cls._model

    @classmethod
    def set_provider(cls, provider: str, model: str):
        cls._provider = provider
        cls._model = model


def get_admin_settings() -> AdminSettingsResponse:
    return AdminSettingsResponse(
        version="2.0.0",
        chat_model=SettingsService.get_model(),
        embedding_model=settings.EMBEDDING_MODEL,
        retrieval_mode=settings.RETRIEVAL_MODE,
        top_k=settings.TOP_K,
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        query_rewrite=settings.ENABLE_QUERY_REWRITE,
        reranker=False,
        jwt_algorithm=settings.JWT_ALGORITHM,
        jwt_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        providers=ProviderStatus(
            ollama=True,
            gemini=False,
            groq=False,
        ),
    )
