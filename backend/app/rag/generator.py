import time

import ollama

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class Generator:
    def __init__(self, model_name: str = settings.CHAT_MODEL):
        self.model_name = model_name
        self.client = ollama.Client(host=settings.OLLAMA_HOST)

    def _build_prompt(
        self, context: str, question: str, conversation_history: str
    ) -> str:
        return f"""
You are a helpful assistant.

Use the provided document context and conversation history
to answer the user's question.

If the conversation contains references such as:
"it", "that", "this", "they"
use the conversation history to determine what those
references mean.

Only respond with:
"I could not find that information in the document."

when the document context contains no relevant information.

Conversation History:
{conversation_history}

Document Context:
{context}

Current Question:
{question}

Answer:
"""

    def generate(
        self, context: str, question: str, conversation_history: str = ""
    ):
        prompt = self._build_prompt(
            context=context,
            question=question,
            conversation_history=conversation_history,
        )

        start = time.time()

        response = self.client.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
        )

        generation_time = time.time() - start

        logger.info(
            f"Model={self.model_name} GenerationLatency={generation_time:.3f}s"
        )

        return response["message"]["content"]

    def stream_generate(
        self,
        context: str,
        question: str,
        conversation_history: str = "",
    ):
        prompt = self._build_prompt(
            context=context,
            question=question,
            conversation_history=conversation_history,
        )

        start = time.time()

        response = self.client.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        for chunk in response:
            token = chunk["message"].get("content")
            if token:
                yield token

        generation_time = time.time() - start
        logger.info(
            f"Model={self.model_name} GenerationLatency={generation_time:.3f}s"
        )

