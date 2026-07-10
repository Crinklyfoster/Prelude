from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):

    def _build_prompt(
        self,
        context: str,
        question: str,
        conversation_history: str,
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

    @abstractmethod
    def generate(
        self,
        context: str,
        question: str,
        conversation_history: str = "",
    ) -> str:
        pass

    @abstractmethod
    def stream_generate(
        self,
        context: str,
        question: str,
        conversation_history: str = "",
    ) -> Any:
        pass

    def health(self) -> str:
        return "healthy"
