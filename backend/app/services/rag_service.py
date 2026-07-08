from app.core.config import settings
from app.core.metrics import CHAT_REQUESTS
from app.rag.generator import Generator
from app.rag.hybrid_retriever import HybridRetriever
from app.rag.query_rewriter import QueryRewriter
from app.rag.retrieval_mode import RetrievalMode
from app.rag.retriever import Retriever


class RAGService:
    def __init__(self):
        if settings.RETRIEVAL_MODE == RetrievalMode.DENSE:
            self.retriever = Retriever()
        else:
            self.retriever = HybridRetriever()
        self.generator = Generator()
        self.rewriter = QueryRewriter()

    def _get_score(self, chunk):
        return (
            chunk.get("rrf_score")
            or chunk.get("dense_distance")
            or chunk.get("bm25_score")
            or 0.0
        )

    def answer_question(
        self,
        question: str,
        conversation_history: str = "",
        current_user_id=None,
        document_ids: list[str] | None = None,
        top_k: int = settings.TOP_K,
    ):
        CHAT_REQUESTS.inc()

        retrieval_query = self.rewriter.rewrite(question, conversation_history)

        retrieved_chunks = self.retriever.retrieve(
            retrieval_query,
            current_user_id=current_user_id,
            document_ids=document_ids,
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
                    "score": self._get_score(chunk),
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
        document_ids: list[str] | None = None,
        top_k: int = settings.TOP_K,
    ):
        CHAT_REQUESTS.inc()

        retrieval_query = self.rewriter.rewrite(question, conversation_history)

        retrieved_chunks = self.retriever.retrieve(
            retrieval_query,
            current_user_id=current_user_id,
            document_ids=document_ids,
            top_k=top_k,
        )

        sources = [
            {
                "chunk_id": chunk["metadata"]["chunk_id"],
                "document_id": chunk["metadata"]["document_id"],
                "score": self._get_score(chunk),
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
