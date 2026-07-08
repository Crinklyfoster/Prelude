import re

import ollama

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class QueryRewriter:
    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_HOST)

    def rewrite(self, question: str, conversation_history: str):
        if not settings.ENABLE_QUERY_REWRITE:
            return question

        has_reference = re.search(
            (
                r"\b("
                r"it|its|they|them|their|"
                r"this|that|these|those|"
                r"he|she|him|her|"
                r"former|latter"
                r")\b"
            ),
            question,
            re.IGNORECASE,
        )

        if not conversation_history.strip() or not has_reference:
            logger.info(f"Rewrite skipped: '{question}'")
            return question

        prompt = f"""
You are a query rewriting system for Retrieval-Augmented Generation (RAG).

Rewrite ONLY the user's latest question into a standalone search query.

Rules:
- Resolve references like "it", "its", "they", "them", "their", "this", "that",
  "these", "those", "he", "she", "him", "her", "former", "latter".
- Preserve the user's original intent.
- Do not answer the question.
- Do not invent information.
- Do not summarize.
- Keep the rewritten query concise.
- Return ONLY the rewritten query.

Conversation History:
{conversation_history}

Latest Question:
{question}
"""

        try:
            response = self.client.chat(
                model=settings.CHAT_MODEL,
                messages=[{"role": "user", "content": prompt}],
            )

            rewritten = response["message"]["content"].strip()

            if not rewritten:
                logger.info(f"Rewrite skipped: '{question}'")
                return question

        except Exception as e:
            logger.warning(f"Query rewrite failed: {e}")
            return question

        logger.info(f"Original='{question}' Rewritten='{rewritten}'")

        return rewritten
