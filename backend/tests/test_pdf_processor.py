from pathlib import Path

from app.services.pdf_processor import PDFProcessor

pdf_files = list(Path("uploads").glob("*.pdf"))

if not pdf_files:
    raise Exception("No PDF files found in uploads folder")

pdf_path = str(pdf_files[0])

print(f"Testing: {pdf_path}")

text = PDFProcessor.extract_text(pdf_path)

print(f"Characters extracted: {len(text)}")
print(text[:1000])
