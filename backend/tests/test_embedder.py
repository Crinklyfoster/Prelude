from app.rag.embedding_provider_manager import EmbeddingProviderManager

def test_generate_embedding():
    embedder = EmbeddingProviderManager.get_provider()
    embedding = embedder.generate_embedding("Attention is all you need")

    assert embedding is not None, "Embedding should not be None"
    
    print(type(embedding))
    print(len(embedding))
    print(embedding[:10])
    
    assert len(embedding) > 0
