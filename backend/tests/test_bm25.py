from app.rag.bm25_retriever import BM25Retriever

retriever = BM25Retriever()

user_id = next(iter(retriever.index.chunk_metadata.values()))["user_id"]

results = retriever.search(
    query="robotics",
    current_user_id=user_id,
    top_k=5,
)

print(f"Retrieved {len(results)} chunks")

for result in results:
    print(result)
