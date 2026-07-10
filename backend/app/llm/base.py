import threading
import time
from abc import ABC, abstractmethod
from typing import Any


class TokenBucket:
    def __init__(self, capacity: int, fill_rate: float):
        self.capacity = float(capacity)
        self._tokens = float(capacity)
        self.fill_rate = fill_rate
        self.last_update = time.time()
        self._lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        with self._lock:
            now = time.time()
            elapsed = now - self.last_update
            self._tokens = min(self.capacity, self._tokens + elapsed * self.fill_rate)
            self.last_update = now

            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False



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
