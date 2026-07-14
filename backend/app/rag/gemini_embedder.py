import time

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

        return response.embeddings[0].values  # type: ignore

    def generate_embeddings(self, chunks: list):
        logger.info(
            "Generating %d Gemini embeddings using batch size %d",
            len(chunks),
            settings.GEMINI_EMBEDDING_BATCH_SIZE,
        )

        embeddings = []
        batch_size = settings.GEMINI_EMBEDDING_BATCH_SIZE

        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]
            texts = [c["text"] for c in batch]

            for attempt in range(5):
                try:
                    response = self.client.models.embed_content(
                        model=self.model,
                        contents=texts,
                    )
                    break
                except Exception as e:
                    if "429" not in str(e):
                        raise
                    time.sleep(2 ** attempt)
            else:
                raise RuntimeError("Max retries exceeded for rate limit.")

            if response.embeddings is None:
                raise RuntimeError("Gemini API returned no embeddings.")

            for chunk, emb in zip(batch, response.embeddings):
                embeddings.append(
                    {
                        "chunk_id": chunk["chunk_id"],
                        "text": chunk["text"],
                        "embedding": emb.values,
                        "hash": chunk.get("hash", ""),
                        "length": chunk.get("length", 0),
                    }
                )

        return embeddings
