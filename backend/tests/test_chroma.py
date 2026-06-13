from app.rag.vector_store import ChromaVectorStore
from app.rag.embedder import OllamaEmbedder

embedder = OllamaEmbedder()
store = ChromaVectorStore()

text = "Transformers are powerful neural networks."

embedding = embedder.generate_embedding(text)

store.add_chunks(
    document_id="test_doc",
    embedded_chunks=[
        {
            "chunk_id": 0,
            "text": text,
            "embedding": embedding
        }
    ]
)

print("Stored successfully")