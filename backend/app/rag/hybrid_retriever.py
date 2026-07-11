from collections import defaultdict

from app.core.config import settings
from app.core.logger import get_logger
from app.rag.bm25_retriever import BM25Retriever
from app.rag.reranker import IdentityReranker
from app.rag.retriever import Retriever

logger = get_logger(__name__)


class HybridRetriever:
    def __init__(self):
        self.dense = Retriever()
        self.sparse = BM25Retriever()
        self.reranker = IdentityReranker()

        self.rrf_k = settings.RRF_K

    def user_has_documents(self, current_user_id) -> bool:
        return self.dense.user_has_documents(current_user_id)

    def retrieve(
        self,
        query: str,
        current_user_id: str | None,
        document_ids=None,
        timer=None,
        **kwargs,
    ) -> dict:
        candidate_k = max(
            settings.FINAL_TOP_K * 4,
            settings.DENSE_TOP_K,
            settings.SPARSE_TOP_K,
        )

        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=2) as executor:
            dense_future = executor.submit(
                self.dense.retrieve,
                query=query,
                current_user_id=current_user_id,
                document_ids=document_ids,
                top_k=candidate_k,
            )

            sparse_future = executor.submit(
                self.sparse.search,
                query=query,
                current_user_id=current_user_id,
                document_ids=document_ids,
                top_k=candidate_k,
            )

            dense_results = dense_future.result()
            sparse_results = sparse_future.result()
        if timer:
            timer.start("rrf")
        fused = self._rrf(
            dense_results,
            sparse_results,
        )
        if timer:
            timer.stop("rrf")
        confidence = (
            max(
                chunk["rrf_score"]
                for chunk in fused
            )
            if fused
            else 0.0
        )

        from app.rag.mmr import MMR

        if settings.ENABLE_MMR:
            if timer:
                timer.start("mmr")
            fused = MMR.select(
                fused,
                top_k=settings.FINAL_TOP_K,
                lambda_mult=settings.MMR_LAMBDA,
            )
            if timer:
                timer.stop("mmr")
        else:
            fused = fused[:settings.FINAL_TOP_K]

        if settings.ENABLE_RERANKER:
            fused = self.reranker.rerank(
                query=query,
                chunks=fused,
                top_k=settings.FINAL_TOP_K,
            )

        return {
            "chunks": fused,
            "confidence": confidence,
        }

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
