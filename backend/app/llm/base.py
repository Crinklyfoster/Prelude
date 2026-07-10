from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):

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
    ):
        pass
