from abc import ABC, abstractmethod
from typing import Any


class EmbeddingProvider(ABC):

    @abstractmethod
    def generate_embedding(self, text: str) -> Any:
        pass

    @abstractmethod
    def generate_embeddings(self, chunks: list) -> Any:
        pass
