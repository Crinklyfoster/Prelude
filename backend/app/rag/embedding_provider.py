from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):

    @abstractmethod
    def generate_embedding(self, text: str):
        pass

    @abstractmethod
    def generate_embeddings(self, chunks: list):
        pass
