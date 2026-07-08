from app.rag.retriever import Retriever

retriever = Retriever()

results = retriever.retrieve(
    query="What is quantum computing?",
    document_id="f36cca85-9157-45ad-ba72-c99bdaad3100",
    top_k=10,
)

print(f"Retrieved {len(results)} chunks")

for r in results:
    print()
    print("=" * 80)
    print(r["distance"])
    print(r["text"][:300])
