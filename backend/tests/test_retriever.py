from app.rag.retriever import Retriever

retriever = Retriever()

queries = [
    "What is self attention?",
    "What is scaled dot product attention?",
    "What is the Transformer architecture?",
]

for query in queries:
    print("\n")
    print("=" * 100)
    print(query)
    print("=" * 100)

    results = retriever.retrieve(query, top_k=3)

    print(results[0]["text"][:1000])
