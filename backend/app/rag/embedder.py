import ollama

from app.core.config import settings


class OllamaEmbedder:

    def __init__(
        self,
        model_name: str = settings.EMBEDDING_MODEL
    ):
        self.model_name = model_name
        self.client = ollama.Client(
            host=settings.OLLAMA_HOST
        )

    def generate_embedding(
        self,
        text: str
    ):
        response = self.client.embeddings(
            model=self.model_name,
            prompt=text
        )

        return response["embedding"]

    def generate_embeddings(
        self,
        chunks: list
    ):
        embeddings = []

        for chunk in chunks:
            vector = self.generate_embedding(
                chunk["text"]
            )

            embeddings.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["text"],
                    "embedding": vector
                }
            )

        return embeddings
