import logging
import time
from typing import Any

from app.core.audit_logger import (
    log_chat_event,
    log_llm_event,
    log_retrieval_event,
)
from app.core.config import settings
from app.core.metrics import CHAT_REQUESTS
from app.rag.generator import Generator
from app.rag.hybrid_retriever import HybridRetriever
from app.rag.prompt_builder import PromptBuilder
from app.rag.query_rewriter import QueryRewriter
from app.rag.retrieval_mode import RetrievalMode
from app.rag.retriever import Retriever
from app.services.benchmark_service import BenchmarkTimer

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

    def _get_retrieval_query(self, question: str, conversation_history: str) -> str:
        if settings.ENABLE_QUERY_REWRITE:
            return self.rewriter.rewrite(question, conversation_history)
        return question

    def _perform_retrieval(
        self,
        retrieval_query: str,
        current_user_id,
        document_ids: list[str] | None,
        top_k: int,
        timer=None,
    ) -> tuple[list, float, bool]:
        cache_key = (
            str(current_user_id),
            tuple(sorted(document_ids or [])),
            retrieval_query,
        )

        from app.rag.retrieval_cache import cache

        cache_hit = False
        if settings.ENABLE_RETRIEVAL_CACHE:
            cached = cache.get(cache_key)
            if cached is not None:
                cache_hit = True
                retrieval_result = cached
            else:
                retrieval_result = self.retriever.retrieve(
                    retrieval_query,
                    current_user_id=current_user_id,
                    document_ids=document_ids,
                    top_k=top_k,
                    timer=timer,
                )
                cache[cache_key] = retrieval_result
        else:
            retrieval_result = self.retriever.retrieve(
                retrieval_query,
                current_user_id=current_user_id,
                document_ids=document_ids,
                top_k=top_k,
                timer=timer,
            )

        if isinstance(retrieval_result, dict):
            retrieved_chunks = retrieval_result["chunks"]
            confidence = retrieval_result.get("confidence", 0.0)
        else:
            retrieved_chunks = retrieval_result
            confidence = 0.0

        return retrieved_chunks, confidence, cache_hit

    def _format_sources(self, retrieved_chunks: list) -> list[dict]:
        return [
            {
                "chunk_id": chunk["metadata"]["chunk_id"],
                "document_id": chunk["metadata"]["document_id"],
                "score": self._get_score(chunk),
                "preview": chunk["text"][:200],
            }
            for chunk in retrieved_chunks
        ]

    def _format_benchmark(
        self, timer, cache_hit: bool, confidence: float, provider_meta: dict | None = None
    ) -> dict[str, Any]:
        stage_times = {r.stage: r.duration_ms for r in timer.results} if timer else {}
        benchmark_data: dict[str, Any] = {
            "query_rewrite_ms": int(stage_times.get("query_rewrite", 0.0)),
            "dense_ms": int(stage_times.get("dense", 0.0)),
            "bm25_ms": int(stage_times.get("bm25", 0.0)),
            "rrf_ms": int(stage_times.get("rrf", 0.0)),
            "cache": "HIT" if cache_hit else "MISS",
            "confidence": round(confidence, 3)
        }
        if provider_meta:
            benchmark_data.update(provider_meta)
        return benchmark_data

    def answer_question(
        self,
        question: str,
        conversation_history: str = "",
        current_user_id=None,
        document_ids: list[str] | None = None,
        top_k: int = settings.TOP_K,
        provider_override: str | None = None,
    ):
        request_start = time.perf_counter()
        CHAT_REQUESTS.inc()

        timer = BenchmarkTimer()

        timer.start("query_rewrite")
        retrieval_query = self._get_retrieval_query(question, conversation_history)
        timer.stop("query_rewrite")

        timer.start("retrieval")
        retrieval_start = time.perf_counter()
        
        has_documents = self.retriever.user_has_documents(current_user_id)
        if has_documents:
            retrieved_chunks, confidence, cache_hit = self._perform_retrieval(
                retrieval_query, current_user_id, document_ids, top_k, timer
            )
        else:
            retrieved_chunks, confidence, cache_hit = [], 0.0, False
            
        retrieval_time = time.perf_counter() - retrieval_start
        timer.stop("retrieval")

        stage_times = {r.stage: r.duration_ms for r in timer.results}
        logger.info(
            "Retrieval | rewrite=%.2fms dense=%.2fms bm25=%.2fms "
            "rrf=%.2fms confidence=%.3f cache=%s",
            stage_times.get("query_rewrite", 0.0),
            stage_times.get("dense", 0.0),
            stage_times.get("bm25", 0.0),
            stage_times.get("rrf", 0.0),
            confidence,
            "HIT" if cache_hit else "MISS",
        )

        log_retrieval_event(
            action="retrieve",
            query=retrieval_query,
            user_id=str(current_user_id),
            duration=round(retrieval_time, 2),
            chunks_found=len(retrieved_chunks),
            mode=settings.RETRIEVAL_MODE.value,
        )

        if not retrieved_chunks:
            timer.start("generation")

            answer, provider_meta = self.generator.generate(
                prompt=question,
                provider_override=provider_override,
            )

            timer.stop("generation")

            response = {
                "question": question,
                "answer": answer,
                "sources": [],
            }

            if settings.ENABLE_BENCHMARKS:
                response["benchmark"] = self._format_benchmark(
                    timer,
                    cache_hit,
                    confidence,
                    provider_meta,
                )
                logger.info("Benchmark %s", response["benchmark"])

            return response

        timer.start("prompt")
        context = self.prompt_builder.build(retrieved_chunks)
        prompt = self.prompt_builder.build_prompt(context, question, conversation_history)
        timer.stop("prompt")

        timer.start("generation")
        generation_start = time.perf_counter()
        answer, provider_meta = self.generator.generate(
            prompt=prompt,
            provider_override=provider_override,
        )
        generation_time = time.perf_counter() - generation_start
        timer.stop("generation")

        log_llm_event(
            action="generate",
            session_id="N/A",  # Not passed here currently
            model=settings.CHAT_MODEL,
            duration=round(generation_time, 2),
        )

        log_chat_event(
            action="message_sent",
            session_id="N/A",
            user_id=str(current_user_id),
            duration=round(time.perf_counter() - request_start, 2),
        )

        response: dict[str, Any] = {
            "question": question,
            "answer": answer,
            "sources": self._format_sources(retrieved_chunks),
        }

        if settings.ENABLE_BENCHMARKS:
            response["benchmark"] = self._format_benchmark(
                timer, cache_hit, confidence, provider_meta
            )
            logger.info("Benchmark %s", response["benchmark"])

        return response

    def stream_answer(
        self,
        question: str,
        conversation_history: str = "",
        current_user_id=None,
        document_ids: list[str] | None = None,
        top_k: int = settings.TOP_K,
        provider_override: str | None = None,
    ):
        request_start = time.perf_counter()
        CHAT_REQUESTS.inc()

        retrieval_query = self._get_retrieval_query(question, conversation_history)

        retrieval_start = time.perf_counter()
        
        has_documents = self.retriever.user_has_documents(current_user_id)
        if has_documents:
            retrieved_chunks, _, _ = self._perform_retrieval(
                retrieval_query, current_user_id, document_ids, top_k
            )
        else:
            retrieved_chunks = []
            
        retrieval_time = time.perf_counter() - retrieval_start
        
        log_retrieval_event(
            action="retrieve_stream",
            query=retrieval_query,
            user_id=str(current_user_id),
            duration=round(retrieval_time, 2),
            chunks_found=len(retrieved_chunks),
            mode=settings.RETRIEVAL_MODE.value,
        )

        sources = self._format_sources(retrieved_chunks)

        if not retrieved_chunks:
            provider_meta = None

            for chunk in self.generator.stream_generate(
                prompt=question,
                provider_override=provider_override,
            ):
                if isinstance(chunk, dict) and chunk.get("type") == "provider_meta":
                    provider_meta = chunk
                    continue

                yield {
                    "type": "token",
                    "token": chunk,
                }

            yield {
                "type": "meta",
                "sources": [],
                "final": True,
                "provider_meta": provider_meta,
            }
            return

        context = self.prompt_builder.build(retrieved_chunks)
        prompt = self.prompt_builder.build_prompt(context, question, conversation_history)

        provider_meta = None
        for chunk in self.generator.stream_generate(
            prompt=prompt,
            provider_override=provider_override,
        ):
            if isinstance(chunk, dict) and chunk.get("type") == "provider_meta":
                provider_meta = chunk
                continue
            yield {"type": "token", "token": chunk}

        log_chat_event(
            action="message_streamed",
            session_id="N/A",
            user_id=str(current_user_id),
            duration=round(time.perf_counter() - request_start, 2),
        )
        yield {"type": "meta", "sources": sources, "final": True, "provider_meta": provider_meta}
