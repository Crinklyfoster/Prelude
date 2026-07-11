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
        current_user_id,
        document_ids=None,
        top_k: int = settings.TOP_K,
    ):
        start = time.time()

        query_embedding = self.embedder.generate_embedding(query)

        # Per-user filtering is enforced by Chroma metadata (user_id).

        results = self.vector_store.search(
            query_embedding=query_embedding,
            current_user_id=current_user_id,
            document_ids=document_ids,
            top_k=top_k,
        )
        assert results is not None, "vector_store.search() returned None"

        documents = results["documents"][0]  # type: ignore[index]
        distances = results["distances"][0]  # type: ignore[index]
        metadatas = results["metadatas"][0]  # type: ignore[index]
        embeddings = results["embeddings"][0]  # type: ignore[index]

        formatted_results = []
        seen_chunks = set()

        for doc, distance, metadata, emb in zip(documents, distances, metadatas, embeddings):
            chunk_preview = doc[:150]

            if chunk_preview in seen_chunks:
                continue

            seen_chunks.add(chunk_preview)

            metadata_dict: dict = dict(metadata)
            metadata_dict["embedding"] = emb

            formatted_results.append(
                {
                    "document_id": metadata_dict.get("document_id"),
                    "chunk_id": metadata_dict.get("chunk_id"),
                    "text": doc,
                    "metadata": metadata_dict,
                    "dense_distance": distance,
                    "source": "dense",
                }
            )

        latency = time.time() - start

        logger.info(
            f"Retrieved={len(formatted_results)} Latency={latency:.3f}s"
        )

        return formatted_results
