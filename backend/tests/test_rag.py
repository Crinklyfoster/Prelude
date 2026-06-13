from app.services.rag_service import RAGService

rag = RAGService()

result = rag.answer_question(
    "What is self attention?"
)

print("\nQUESTION:\n")
print(result["question"])

print("\nANSWER:\n")
print(result["answer"])