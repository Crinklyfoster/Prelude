from pathlib import Path

from app.rag.chunker import DocumentChunker
from app.services.pdf_processor import PDFProcessor

pdf_files = list(Path("uploads").glob("*.pdf"))

pdf_path = str(pdf_files[0])

text = PDFProcessor.extract_text(pdf_path)

chunker = DocumentChunker()

chunks = chunker.chunk_text(text)

print(f"Total chunks: {len(chunks)}")

print("\nFirst chunk:\n")
print(chunks[0]["text"])

print("\nLast chunk:\n")
print(chunks[-1]["text"])

for i in range(3):
    print("\n" + "=" * 80)
    print(f"Chunk {i}")
    print("=" * 80)
    print(chunks[i]["text"])
