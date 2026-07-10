from app.llm.ollama_provider import OllamaProvider
from app.llm.gemini_provider import GeminiProvider


PROVIDERS = {
    "ollama": OllamaProvider,
    "gemini": GeminiProvider,
}
