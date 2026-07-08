from collections import defaultdict

from app.rag.bm25_retriever import BM25Retriever
from app.rag.retriever import Retriever


class HybridRetriever:
    def __init__(self):
        self.dense = Retriever()
        self.sparse = BM25Retriever()

        self.rrf_k = 60

    def retrieve(
        self,
        query: str,
        current_user_id: str,
        top_k: int = 5,
    ):
        dense_results = self.dense.retrieve(
            query,
            top_k=top_k * 2,
            current_user_id=current_user_id,
        )

        sparse_results = self.sparse.search(
            query=query,
            current_user_id=current_user_id,
            top_k=top_k * 2,
        )

        fused = self._rrf(
            dense_results,
            sparse_results,
        )

        return fused[:top_k]

    def _rrf(
        self,
        dense_results,
        sparse_results,
    ):
        scores = defaultdict(float)
        objects = {}

        for rank, item in enumerate(dense_results):
            key = (
                item["document_id"],
                item["chunk_id"],
            )

            scores[key] += 1 / (self.rrf_k + rank + 1)

            objects[key] = {
                "document_id": item["document_id"],
                "chunk_id": item["chunk_id"],
                "text": item["text"],
                "metadata": item["metadata"],
                "score": item["score"],
                "source": "dense",
            }

        for rank, item in enumerate(sparse_results):
            key = (
                item["document_id"],
                item["chunk_id"],
            )

            scores[key] += 1 / (self.rrf_k + rank + 1)

            if key not in objects:
                chunk = self.dense.vector_store.get_chunk(
                    item["document_id"],
                    item["chunk_id"],
                )

                if chunk is None:
                    continue

                objects[key] = {
                    "document_id": item["document_id"],
                    "chunk_id": item["chunk_id"],
                    "text": chunk["text"],
                    "metadata": chunk["metadata"],
                    "score": item["score"],
                    "source": "sparse",
                }
            else:
                objects[key]["source"] = "hybrid"

        ranked = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        return [
            {
                **objects[key],
                "rrf_score": score,
            }
            for key, score in ranked
            if key in objects
        ]
