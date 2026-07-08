"""
TODO (M6 Future)

Replace IdentityReranker with:

- BAAI/bge-reranker-base
- jina-reranker-v2-base-multilingual
- bge-reranker-large

when GPU inference becomes available.
"""


class BaseReranker:
    def rerank(
        self,
        query: str,
        chunks: list[dict],
        top_k: int,
    ):
        raise NotImplementedError


class IdentityReranker(BaseReranker):
    def rerank(
        self,
        query: str,
        chunks: list[dict],
        top_k: int,
    ):
        return chunks[:top_k]
