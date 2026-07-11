from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: str,
    ) -> str:
        pass

    @abstractmethod
    def stream_generate(
        self,
        prompt: str,
    ) -> Any:
        pass

    def health(self) -> str:
        return "healthy"
