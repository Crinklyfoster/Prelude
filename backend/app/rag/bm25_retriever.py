import math
from collections import defaultdict

from app.rag.lexical_index import LexicalIndex


class BM25Retriever:
    def __init__(self):
        self.index = LexicalIndex()

        self.k1 = 1.5
        self.b = 0.75

    def search(
        self,
        query: str,
        current_user_id,
        top_k: int = 5,
    ):
        tokens = self.index.tokenize(query)

        scores = defaultdict(float)

        if self.index.total_chunks == 0:
            return []

        avg_doc_len = (
            sum(self.index.chunk_lengths.values()) / self.index.total_chunks
        )

        for token in tokens:
            postings = self.index.inverted_index.get(token)

            if postings is None:
                continue

            df = self.index.document_frequency.get(token, 0)

            idf = math.log(
                (self.index.total_chunks - df + 0.5) / (df + 0.5) + 1
            )

            for chunk_id, tf in postings.items():
                doc_len = self.index.chunk_lengths[chunk_id]

                numerator = tf * (self.k1 + 1)

                denominator = tf + self.k1 * (
                    1 - self.b + self.b * doc_len / avg_doc_len
                )

                scores[chunk_id] += idf * (numerator / denominator)

        ranked = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        results = []

        for chunk_id, score in ranked[:top_k]:
            metadata = self.index.chunk_metadata.get(chunk_id)

            if metadata is None:
                continue

            if metadata["user_id"] != str(current_user_id):
                continue

            results.append(
                {
                    "chunk_id": metadata["chunk_id"],
                    "document_id": metadata["document_id"],
                    "score": score,
                }
            )

        return results
