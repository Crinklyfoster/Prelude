from app.core.config import settings
from app.llm.gemini_provider import GeminiProvider
from app.llm.grok_provider import GrokProvider
from app.llm.ollama_provider import OllamaProvider


class LLMFactory:

    @staticmethod
    def create():

        provider = settings.LLM_PROVIDER.lower()

        if provider == "ollama":
            return OllamaProvider()

        if provider == "gemini":
            return GeminiProvider()

        if provider == "grok":
            return GrokProvider()

        raise ValueError(
            f"Unsupported provider: {provider}"
        )
