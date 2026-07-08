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
        current_user_id: str | None,
        document_ids=None,
        top_k: int = 5,
    ) -> list[dict]:
        dense_results = self.dense.retrieve(
            query,
            current_user_id=current_user_id,
            document_ids=document_ids,
            top_k=top_k * 2,
        )

        sparse_results = self.sparse.search(
            query=query,
            current_user_id=current_user_id,
            document_ids=document_ids,
            top_k=top_k * 2,
        )

        fused = self._rrf(
            dense_results,
            sparse_results,
        )

        return fused[:top_k]

    def _rrf(
        self,
        dense_results: list[dict],
        sparse_results: list[dict],
    ) -> list[dict]:
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
                "dense_distance": item.get("dense_distance"),
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
                    "bm25_score": item["score"],
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
                "document_id": objects[key]["document_id"],
                "chunk_id": objects[key]["chunk_id"],
                "text": objects[key]["text"],
                "metadata": objects[key]["metadata"],
                "source": objects[key]["source"],
                "rrf_score": score,
                **(
                    {"dense_distance": objects[key]["dense_distance"]}
                    if "dense_distance" in objects[key]
                    else {}
                ),
                **(
                    {"bm25_score": objects[key]["bm25_score"]}
                    if "bm25_score" in objects[key]
                    else {}
                ),
            }
            for key, score in ranked
            if key in objects
        ]
