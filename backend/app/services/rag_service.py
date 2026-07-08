from app.core.config import settings
from app.core.metrics import CHAT_REQUESTS
from app.rag.generator import Generator
from app.rag.prompt_builder import PromptBuilder
from app.rag.hybrid_retriever import HybridRetriever
from app.rag.query_rewriter import QueryRewriter
from app.rag.retrieval_mode import RetrievalMode
import time
import logging

from app.rag.retriever import Retriever

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self):
        self.retriever: Retriever | HybridRetriever
        if settings.RETRIEVAL_MODE == RetrievalMode.DENSE:
            self.retriever = Retriever()
        else:
            self.retriever = HybridRetriever()
        self.generator = Generator()
        self.rewriter = QueryRewriter()
        self.prompt_builder = PromptBuilder()

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
        request_start = time.time()
        CHAT_REQUESTS.inc()

        retrieval_query = self.rewriter.rewrite(question, conversation_history)

        retrieval_start = time.time()
        retrieved_chunks = self.retriever.retrieve(
            retrieval_query,
            current_user_id=current_user_id,
            document_ids=document_ids,
            top_k=top_k,
        )
        retrieval_time = time.time() - retrieval_start
        logger.info(
            "Retrieval completed in %.3fs (%d chunks)",
            retrieval_time,
            len(retrieved_chunks),
        )
        logger.info(
            "Retrieval Mode=%s Retrieved=%d",
            settings.RETRIEVAL_MODE,
            len(retrieved_chunks),
        )

        if not retrieved_chunks:
            return {
                "question": question,
                "answer": (
                    "I could not find that information in the document."
                ),
                "sources": [],
            }

        context = self.prompt_builder.build(retrieved_chunks)

        generation_start = time.time()
        answer = self.generator.generate(
            context=context,
            question=question,
            conversation_history=conversation_history,
        )
        generation_time = time.time() - generation_start
        logger.info(
            "Generation completed in %.3fs",
            generation_time,
        )

        logger.info(
            "Total request %.3fs",
            time.time() - request_start,
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
        request_start = time.time()
        CHAT_REQUESTS.inc()

        retrieval_query = self.rewriter.rewrite(question, conversation_history)

        retrieval_start = time.time()
        retrieved_chunks = self.retriever.retrieve(
            retrieval_query,
            current_user_id=current_user_id,
            document_ids=document_ids,
            top_k=top_k,
        )
        retrieval_time = time.time() - retrieval_start
        logger.info(
            "Retrieval completed in %.3fs (%d chunks)",
            retrieval_time,
            len(retrieved_chunks),
        )
        logger.info(
            "Retrieval Mode=%s Retrieved=%d",
            settings.RETRIEVAL_MODE,
            len(retrieved_chunks),
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

        context = self.prompt_builder.build(retrieved_chunks)

        for token in self.generator.stream_generate(
            context=context,
            question=question,
            conversation_history=conversation_history,
        ):
            yield {"type": "token", "token": token}

        logger.info(
            "Total request %.3fs",
            time.time() - request_start,
        )
        yield {"type": "meta", "sources": sources, "final": True}
