# tests/test_full_ingestion.py

from pathlib import Path

from app.rag.chunker import DocumentChunker
from app.rag.embedder import OllamaEmbedder
from app.rag.vector_store import ChromaVectorStore
from app.services.pdf_processor import PDFProcessor

pdf_path = str(next(Path("uploads").glob("*.pdf")))

text = PDFProcessor.extract_text(pdf_path)

chunker = DocumentChunker()
chunks = chunker.chunk_text(text)

embedder = OllamaEmbedder()
embedded_chunks = embedder.generate_embeddings(chunks)

store = ChromaVectorStore()

store.add_chunks(
    document_id="attention_paper", embedded_chunks=embedded_chunks
)

print(f"Text length: {len(text)}")
print(f"Chunks: {len(chunks)}")
print("Full ingestion successful")
