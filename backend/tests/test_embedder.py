from app.rag.embedder import OllamaEmbedder

embedder = OllamaEmbedder()

embedding = embedder.generate_embedding("Attention is all you need")

print(type(embedding))
print(len(embedding))
print(embedding[:10])
