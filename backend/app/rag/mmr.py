import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class MMR:

    @staticmethod
    def select(chunks, top_k, lambda_mult=0.5):

        if len(chunks) <= top_k:
            return chunks

        embeddings = np.array(
            [
                c["metadata"]["embedding"]
                for c in chunks
            ]
        )

        query = embeddings.mean(axis=0).reshape(1, -1)

        relevance = cosine_similarity(
            query,
            embeddings,
        )[0]

        selected = [int(np.argmax(relevance))]

        remaining = set(range(len(chunks))) - set(selected)

        while len(selected) < top_k:

            best = None
            best_score = -1e9

            for idx in remaining:

                diversity = max(
                    cosine_similarity(
                        embeddings[idx].reshape(1, -1),
                        embeddings[selected],
                    )[0]
                )

                score = (
                    lambda_mult * relevance[idx]
                    - (1 - lambda_mult) * diversity
                )

                if score > best_score:
                    best_score = score
                    best = idx

            assert best is not None
            selected.append(best)
            remaining.remove(best)

        return [chunks[i] for i in selected]
