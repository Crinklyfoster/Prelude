from typing import Any

from google import genai

from app.core.config import settings
from app.llm.base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    def generate(
        self,
        context: str,
        question: str,
        conversation_history: str = "",
    ) -> str:
        prompt = self._build_prompt(
            context,
            question,
            conversation_history,
        )

        response = self.client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )

        return response.text or ""

    def stream_generate(
        self,
        context: str,
        question: str,
        conversation_history: str = "",
    ) -> Any:
        yield self.generate(
            context=context,
            question=question,
            conversation_history=conversation_history,
        )

    def health(self):
        try:
            self.client.models.list()
            return "healthy"
        except Exception:
            return "unhealthy"
