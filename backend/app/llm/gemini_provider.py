from typing import Any

from google import genai

from app.core.config import settings
from app.llm.base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):

    def __init__(self, model: str):
        self.model = model
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
            model=self.model,
            contents=prompt,
        )

        return response.text or ""

    def stream_generate(
        self,
        context: str,
        question: str,
        conversation_history: str = "",
    ) -> Any:
        prompt = self._build_prompt(
            context,
            question,
            conversation_history,
        )

        response = self.client.models.generate_content_stream(
            model=self.model,
            contents=prompt,
        )

        for chunk in response:
            if chunk.text:
                yield chunk.text

    def health(self):
        try:
            self.client.models.list()
            return "healthy"
        except Exception as e:
            if "503" in str(e):
                return "degraded"
            return "unhealthy"
