from openai import OpenAI

from app.core.config import settings
from app.llm.base import BaseLLMProvider


class GrokProvider(BaseLLMProvider):

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.XAI_API_KEY,
            base_url="https://api.x.ai/v1",
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

        response = self.client.chat.completions.create(
            model=settings.GROK_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content

    def stream_generate(
        self,
        context: str,
        question: str,
        conversation_history: str = "",
    ):
        raise NotImplementedError("Streaming not yet implemented for GrokProvider")
