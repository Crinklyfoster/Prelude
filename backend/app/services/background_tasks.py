from app.database.db import SessionLocal
from app.models.document import Document
from app.services.ingestion_service import IngestionService


def process_document_background(
    document_id,
    file_path
):
    db = SessionLocal()

    try:
        ingestion_service = IngestionService()

        ingestion_service.process_document(
            document_id=document_id,
            file_path=file_path
        )

        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if document:
            document.status = "indexed"
            db.commit()

    except Exception as e:
        print(f"Background processing error: {e}")

        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if document:
            document.status = "failed"
            db.commit()

    finally:
        db.close()