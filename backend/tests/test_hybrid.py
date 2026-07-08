from app.rag.hybrid_retriever import HybridRetriever

retriever = HybridRetriever()

user_id = next(iter(retriever.sparse.index.chunk_metadata.values()))["user_id"]

results = retriever.retrieve(
    query="robotics",
    current_user_id=user_id,
    top_k=5,
)

print(f"Retrieved {len(results)} results")

for result in results:
    print(result)
