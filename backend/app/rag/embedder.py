import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import ollama

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class OllamaEmbedder:
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
        }

    def generate_embeddings(self, chunks: list[dict]):
        start = time.perf_counter()

        embedded_chunks: list[dict | None] = [None] * len(chunks)

        with ThreadPoolExecutor(
            max_workers=settings.EMBEDDING_WORKERS
        ) as executor:

            future_map = {
                executor.submit(self._embed_chunk, chunk): index
                for index, chunk in enumerate(chunks)
            }

            for future in as_completed(future_map):
                index = future_map[future]

                try:
                    embedded = future.result()
                    embedded.pop("latency", None)
                    embedded_chunks[index] = embedded

                except Exception:
                    logger.exception(
                        "Failed embedding chunk %s",
                        chunks[index]["chunk_id"],
                    )
                    raise

        elapsed = time.perf_counter() - start

        logger.info(
            "Embedded %d chunks in %.2fs (workers=%d)",
            len(chunks),
            elapsed,
            settings.EMBEDDING_WORKERS,
        )

        return embedded_chunks
