from concurrent.futures import ThreadPoolExecutor, as_completed

from google import genai

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class GeminiEmbedder:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_EMBEDDING_MODEL

    def generate_embedding(self, text: str):
        response = self.client.models.embed_content(
            model=self.model,
            contents=text,
        )

        assert response.embeddings is not None, "Embeddings should not be None"
        return response.embeddings[0].values

    def generate_embeddings(self, chunks: list):

        logger.info(
            "Generating %d Gemini embeddings using %d workers",
            len(chunks),
            settings.EMBEDDING_WORKERS,
        )

        embeddings: list[dict | None] = [None] * len(chunks)

        def worker(idx, chunk):
            vector = self.generate_embedding(chunk["text"])

            return idx, {
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "embedding": vector,
            }

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
