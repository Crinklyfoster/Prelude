from app.rag.retriever import Retriever
from app.rag.generator import Generator


class RAGService:

    def __init__(self):
        self.retriever = Retriever()
        self.generator = Generator()

    def answer_question(
        self,
        question: str,
        top_k: int = 3
    ):
        retrieved_chunks = self.retriever.retrieve(
            question,
            top_k=top_k
        )

        context = "\n\n".join(
            chunk["text"]
            for chunk in retrieved_chunks
        )

        answer = self.generator.generate(
            context=context,
            question=question
        )

        return {
            "question": question,
            "answer": answer,
            "sources": len(retrieved_chunks)
        }