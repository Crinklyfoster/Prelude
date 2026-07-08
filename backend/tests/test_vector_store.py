from app.rag.vector_store import ChromaVectorStore

store = ChromaVectorStore()

# Replace with a real document_id and chunk_id from your BM25 test output.
chunk = store.get_chunk(
    document_id="5705823b-89cc-4e20-b78c-946036eaaa2f",
    chunk_id=41,
)

print("=" * 60)
if chunk is None:
    print("No chunk found — check document_id and chunk_id.")
else:
    print("text    :", chunk["text"][:200])
    print("metadata:", chunk["metadata"])
print("=" * 60)
