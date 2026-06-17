import time

from app.core.config import settings
from app.core.logger import get_logger
from app.rag.embedder import OllamaEmbedder
from app.rag.vector_store import ChromaVectorStore

logger = get_logger(__name__)


class Retriever:

    def __init__(self):
        self.embedder = OllamaEmbedder()
        self.vector_store = ChromaVectorStore()

    def retrieve(
        self,
        query: str,
        document_id: str,
        top_k: int = settings.TOP_K
    ):
        start = time.time()

        query_embedding = (
            self.embedder.generate_embedding(query)
        )

        results = self.vector_store.search(
            query_embedding,
            top_k,
            document_id=document_id
        )

        documents = results["documents"][0]
        distances = results["distances"][0]
        metadatas = results["metadatas"][0]

        formatted_results = []
        seen_chunks = set()

        for doc, distance, metadata in zip(
            documents,
            distances,
            metadatas
        ):
            chunk_preview = doc[:150]

            if chunk_preview in seen_chunks:
                continue

            seen_chunks.add(chunk_preview)

            formatted_results.append(
                {
                    "text": doc,
                    "distance": distance,
                    "metadata": metadata
                }
            )

        latency = time.time() - start

        logger.info(
            f"Document={document_id} "
            f"Retrieved={len(formatted_results)} "
            f"Latency={latency:.3f}s"
        )

        return formatted_results
