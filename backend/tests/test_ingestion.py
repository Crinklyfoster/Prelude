# tests/test_full_ingestion.py

from pathlib import Path

from app.rag.chunker import DocumentChunker
from app.rag.embedding_provider_manager import EmbeddingProviderManager
from app.rag.vector_store import ChromaVectorStore
from app.services.pdf_processor import PDFProcessor

def test_full_ingestion():
    try:
        pdf_path = str(next(Path("uploads").glob("*.pdf")))
    except StopIteration:
        # If no PDF exists in uploads, we skip the test or just return
        print("No PDF found, skipping test")
        return

    text = PDFProcessor.extract_text(pdf_path)

    chunker = DocumentChunker()
    chunks = chunker.chunk_text(text)

    embedder = EmbeddingProviderManager.get_provider()
    embedded_chunks = embedder.generate_embeddings(chunks)

    store = ChromaVectorStore()

    store.add_chunks(
        document_id="attention_paper", 
        current_user_id="test_user",
        embedded_chunks=embedded_chunks
    )

    assert len(text) > 0
    assert len(chunks) > 0
    print("Full ingestion successful")

