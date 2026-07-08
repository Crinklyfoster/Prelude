from app.core.config import settings
from app.core.metrics import CHAT_REQUESTS
from app.rag.generator import Generator
from app.rag.retriever import Retriever


class RAGService:
    def __init__(self):
        self.retriever = Retriever()
        self.generator = Generator()

    def answer_question(
        self,
        question: str,
        conversation_history: str = "",
        current_user_id=None,
        top_k: int = settings.TOP_K,
    ):
        CHAT_REQUESTS.inc()

        retrieved_chunks = self.retriever.retrieve(
            question,
            current_user_id=current_user_id,
            top_k=top_k,
        )

        if not retrieved_chunks:
            return {
                "question": question,
                "answer": (
                    "I could not find that information in the document."
                ),
                "sources": [],
            }

        context = "\n\n".join(chunk["text"] for chunk in retrieved_chunks)

        answer = self.generator.generate(
            context=context,
            question=question,
            conversation_history=conversation_history,
        )

        return {
            "question": question,
            "answer": answer,
            "sources": [
                {
                    "chunk_id": chunk["metadata"]["chunk_id"],
                    "document_id": chunk["metadata"]["document_id"],
                    "score": chunk["distance"],
                    "preview": chunk["text"][:200],
                }
                for chunk in retrieved_chunks
            ],
        }

    def stream_answer(
        self,
        question: str,
        conversation_history: str = "",
        current_user_id=None,
        top_k: int = settings.TOP_K,
    ):
        CHAT_REQUESTS.inc()

        retrieved_chunks = self.retriever.retrieve(
            question,
            current_user_id=current_user_id,
            top_k=top_k,
        )

        sources = [
            {
                "chunk_id": chunk["metadata"]["chunk_id"],
                "document_id": chunk["metadata"]["document_id"],
                "score": chunk["distance"],
                "preview": chunk["text"][:200],
            }
            for chunk in retrieved_chunks
        ]

        if not retrieved_chunks:
            yield {"type": "meta", "sources": [], "final": True}
            return

        context = "\n\n".join(chunk["text"] for chunk in retrieved_chunks)

        for token in self.generator.stream_generate(
            context=context,
            question=question,
            conversation_history=conversation_history,
        ):
            yield {"type": "token", "token": token}

        yield {"type": "meta", "sources": sources, "final": True}
