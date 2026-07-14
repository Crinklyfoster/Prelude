from app.core.config import settings
from app.rag.gemini_embedder import GeminiEmbedder
from app.rag.ollama_embedder import OllamaEmbedder


class EmbeddingProviderManager:

    @staticmethod
    def get_provider():

        if settings.EMBEDDING_PROVIDER.lower() == "gemini":
            return GeminiEmbedder()

        return OllamaEmbedder()
