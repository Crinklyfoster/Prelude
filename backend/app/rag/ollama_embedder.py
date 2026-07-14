import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import ollama

from app.core.config import settings
from app.core.logger import get_logger
from app.rag.embedding_provider import EmbeddingProvider

logger = get_logger(__name__)


class OllamaEmbedder(EmbeddingProvider):
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL):
        self.model_name = model_name
        self.client = ollama.Client(host=settings.OLLAMA_HOST)

    def generate_embedding(self, text: str):
        response = self.client.embeddings(
            model=self.model_name,
            prompt=text,
        )
        return response["embedding"]

    def _embed_chunk(self, chunk: dict):
        start = time.perf_counter()

        vector = self.generate_embedding(chunk["text"])

        elapsed = time.perf_counter() - start

        return {
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "embedding": vector,
            "latency": elapsed,
            "hash": chunk.get("hash", ""),
            "length": chunk.get("length", 0),
        }

    def generate_embeddings(self, chunks: list):

        logger.info(
            "Generating %d embeddings using %d workers",
            len(chunks),
            settings.EMBEDDING_WORKERS,
        )

        embeddings: list[dict | None] = [None] * len(chunks)

        def worker(idx, chunk):

            vector = self.generate_embedding(chunk["text"])

            return (
                idx,
                {
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["text"],
                    "embedding": vector,
                },
            )

        with ThreadPoolExecutor(
            max_workers=settings.EMBEDDING_WORKERS,
        ) as executor:

            futures = [
                executor.submit(worker, idx, chunk)
                for idx, chunk in enumerate(chunks)
            ]

            for future in as_completed(futures):

                idx, result = future.result()

                embeddings[idx] = result

        return embeddings
