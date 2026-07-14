import time

from app.core.config import settings
from app.core.logger import get_logger
from app.rag.chunker import DocumentChunker
from app.rag.embedding_provider_manager import EmbeddingProviderManager
from app.rag.lexical_index import LexicalIndex
from app.rag.vector_store import ChromaVectorStore
from app.services.pdf_processor import PDFProcessor

logger = get_logger(__name__)


class IngestionService:
    def __init__(self):
        self.chunker = DocumentChunker()
        self.embedder = EmbeddingProviderManager.get_provider()
        self.vector_store = ChromaVectorStore()
        self.lexical_index = LexicalIndex()

    def process_document(
        self,
        document_id,
        file_path,
        current_user_id,
    ):
        timings = {}

        total_start = time.perf_counter()

        # -------------------------
        # PDF Extraction
        # -------------------------
        stage = time.perf_counter()
        text = PDFProcessor.extract_text(file_path)
        timings["extract"] = time.perf_counter() - stage

        # -------------------------
        # Chunking
        # -------------------------
        stage = time.perf_counter()
        chunks = self.chunker.chunk_text(text)
        
        logger.info(
            "Chunking | total=%d | avg_size=%.1f",
            len(chunks),
            sum(int(c["length"]) for c in chunks) / len(chunks) if chunks else 0,
        )
        
        timings["chunk"] = time.perf_counter() - stage

        # -------------------------
        # Embedding (parallel)
        # -------------------------
        embedding_start = time.time()

        embedded_chunks = self.embedder.generate_embeddings(chunks)

        embedding_time = time.time() - embedding_start

        logger.info(
            "Document %s: %d embeddings generated in %.2fs using %d workers",
            document_id,
            len(embedded_chunks),
            embedding_time,
            settings.EMBEDDING_WORKERS,
        )
        timings["embed"] = embedding_time

        # -------------------------
        # Vector Store
        # -------------------------
        stage = time.perf_counter()
        self.vector_store.add_chunks(
            document_id=document_id,
            current_user_id=current_user_id,
            embedded_chunks=embedded_chunks,
        )
        timings["vector_store"] = time.perf_counter() - stage

        # -------------------------
        # BM25 Index
        # -------------------------
        stage = time.perf_counter()
        self.lexical_index.add_document(
            document_id=document_id,
            current_user_id=current_user_id,
            chunks=embedded_chunks,
        )
        timings["lexical_index"] = time.perf_counter() - stage

        total_time = time.perf_counter() - total_start

        logger.info(
            (
                "Ingestion completed | "
                "doc=%s | "
                "chunks=%d | "
                "extract=%.2fs | "
                "chunk=%.2fs | "
                "embed=%.2fs | "
                "vector=%.2fs | "
                "bm25=%.2fs | "
                "total=%.2fs"
            ),
            document_id,
            len(chunks),
            timings["extract"],
            timings["chunk"],
            timings["embed"],
            timings["vector_store"],
            timings["lexical_index"],
            total_time,
        )

        return {
            "chunk_count": len(chunks),
            "timings": timings,
            "total_time": total_time,
        }
