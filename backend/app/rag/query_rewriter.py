import re

import ollama

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class QueryRewriter:

    def __init__(self):
        self.client = ollama.Client(
            host=settings.OLLAMA_HOST
        )

    def rewrite(
        self,
        question: str,
        conversation_history: str
    ):
        has_reference = re.search(
            r"\b(it|they|this|that|these|those)\b",
            question,
            re.IGNORECASE
        )

        if (
            not conversation_history.strip()
            or not has_reference
        ):
            return question

        prompt = f"""
Rewrite the latest question as a standalone question.

Use conversation history only to resolve references.

Return ONLY the rewritten question.

Do NOT include:
- explanations
- markdown
- labels
- quotes
- prefixes

Conversation History:
{conversation_history}

Latest Question:
{question}
"""

        response = self.client.chat(
            model=settings.CHAT_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        rewritten = (
            response["message"]["content"]
            .strip()
        )

        logger.info(
            f"Original='{question}' "
            f"Rewritten='{rewritten}'"
        )

        return rewritten
