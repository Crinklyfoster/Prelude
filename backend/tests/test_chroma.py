from app.rag.embedding_provider_manager import EmbeddingProviderManager
from app.rag.vector_store import ChromaVectorStore

def test_chroma_store():
    embedder = EmbeddingProviderManager.get_provider()
    store = ChromaVectorStore()

    text = "Transformers are powerful neural networks."

    embedding = embedder.generate_embedding(text)

    store.add_chunks(
        document_id="test_doc",
        current_user_id="test_user",
        embedded_chunks=[{"chunk_id": 0, "text": text, "embedding": embedding}],
    )

    print("Stored successfully")

