from app.rag.embedder import OllamaEmbedder
from app.rag.vector_store import ChromaVectorStore


class Retriever:

    def __init__(self):
        self.embedder = OllamaEmbedder()
        self.vector_store = ChromaVectorStore()

    def retrieve(
        self,
        query: str,
        document_id: str,
        top_k: int = 5
    ):
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

        for doc, distance, metadata in zip(
            documents,
            distances,
            metadatas
        ):
            formatted_results.append(
                {
                    "text": doc,
                    "distance": distance,
                    "metadata": metadata
                }
            )

        return formatted_results