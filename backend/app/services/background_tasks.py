from app.core.logger import get_logger
from app.database.db import SessionLocal
from app.models.document import Document
from app.services.ingestion_service import IngestionService

logger = get_logger(__name__)


def process_document_background(document_id, file_path):

    db = SessionLocal()

    try:
        ingestion_service = IngestionService()

        document = (
            db.query(Document).filter(Document.id == document_id).first()
        )
        current_user_id = document.user_id if document else None

        if current_user_id is None:
            raise ValueError(
                f"Document {document_id} not found or missing user ownership"
            )

        ingestion_service.process_document(
            document_id=document_id,
            file_path=file_path,
            current_user_id=current_user_id,
        )

        document = (
            db.query(Document).filter(Document.id == document_id).first()
        )

        if document:
            document.status = "indexed"
            db.commit()

    except Exception as e:
        logger.error(f"Background processing error: {e}")

        document = (
            db.query(Document).filter(Document.id == document_id).first()
        )

        if document:
            document.status = "failed"
            db.commit()

    finally:
        db.close()
