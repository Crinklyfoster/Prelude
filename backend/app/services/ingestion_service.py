import time

from app.core.logger import get_logger
from app.rag.chunker import DocumentChunker
from app.rag.embedder import OllamaEmbedder
from app.rag.lexical_index import LexicalIndex
from app.rag.vector_store import ChromaVectorStore
from app.services.pdf_processor import PDFProcessor

logger = get_logger(__name__)


class IngestionService:
    def __init__(self):
        self.chunker = DocumentChunker()
        self.embedder = OllamaEmbedder()
        self.vector_store = ChromaVectorStore()
        self.lexical_index = LexicalIndex()

    def process_document(
        self,
        document_id,
        session_id,
        file_path,
        current_user_id,
    ):

        start_time = time.time()

        extract_start = time.time()
        text = PDFProcessor.extract_text(file_path)

        logger.info(
            f"Document {document_id}: "
            f"extraction took "
            f"{time.time() - extract_start:.2f}s"
        )

        chunk_start = time.time()
        chunks = self.chunker.chunk_text(text)

        logger.info(
            f"Document {document_id}: "
            f"{len(chunks)} chunks created in "
            f"{time.time() - chunk_start:.2f}s"
        )

        embedding_start = time.time()
        embedded_chunks = self.embedder.generate_embeddings(chunks)

        logger.info(
            f"Document {document_id}: "
            f"{len(embedded_chunks)} embeddings generated in "
            f"{time.time() - embedding_start:.2f}s"
        )

        storage_start = time.time()
        self.vector_store.add_chunks(
            document_id,
            session_id,
            current_user_id,
            embedded_chunks,
        )

        self.lexical_index.add_document(
            document_id=document_id,
            current_user_id=current_user_id,
            chunks=embedded_chunks,
        )

        logger.info(
            f"Document {document_id}: "
            f"stored in vector database in "
            f"{time.time() - storage_start:.2f}s"
        )

        logger.info(
            f"Document {document_id}: "
            f"ingestion completed in "
            f"{time.time() - start_time:.2f}s"
        )

        return len(chunks)
