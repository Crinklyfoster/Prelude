from app.services.pdf_processor import PDFProcessor
from app.rag.chunker import DocumentChunker
from app.rag.embedder import OllamaEmbedder
from app.rag.vector_store import ChromaVectorStore


class IngestionService:

    def __init__(self):
        self.chunker = DocumentChunker()
        self.embedder = OllamaEmbedder()
        self.vector_store = ChromaVectorStore()

    def process_document(
        self,
        document_id,
        file_path
    ):
        text = PDFProcessor.extract_text(file_path)

        chunks = self.chunker.chunk_text(text)

        embedded_chunks = self.embedder.generate_embeddings(
            chunks
        )

        self.vector_store.add_chunks(
            document_id,
            embedded_chunks
        )

        return len(chunks)