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
        context,
        question,
        conversation_history="",
    ):

        prompt = f"""
Conversation:
{conversation_history}

Context:
{context}

Question:
{question}
"""

        response = self.client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )

        return response.text

    def stream_generate(
        self,
        context: str,
        question: str,
        conversation_history: str = "",
    ):
        raise NotImplementedError("Streaming not yet implemented for GeminiProvider")
