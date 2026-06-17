import time

from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.models.document import Document
from app.schemas.document import DocumentCreate
from app.services.ingestion_service import IngestionService
from app.rag.vector_store import ChromaVectorStore

logger = get_logger(__name__)

ingestion_service = IngestionService()
vector_store = ChromaVectorStore()


def create_document(
    db: Session,
    document: DocumentCreate
):
    new_document = Document(
        filename=document.filename,
        file_path=document.file_path
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return new_document


def get_documents(db: Session):
    return db.query(Document).all()


def get_document_by_id(
    db: Session,
    document_id
):
    return (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )


def save_uploaded_file(file):
    upload_dir = Path("uploads")

    upload_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    unique_filename = f"{uuid4()}_{file.filename}"

    file_path = upload_dir / unique_filename

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return str(file_path), unique_filename


def upload_document(
    db,
    file
):
    start = time.time()

    file_path, filename = save_uploaded_file(file)

    document = Document(
        filename=filename,
        file_path=file_path,
        status="processing"
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    logger.info(
        f"Upload completed in "
        f"{time.time() - start:.2f}s"
    )

    return {
        "document_id": str(document.id),
        "filename": document.filename,
        "status": document.status,
        "file_path": document.file_path
    }

def delete_document(
        db: Session,
        document_id
    ):
        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if not document:
            return False

        # Delete vectors from Chroma
        vector_store.delete_document(
            document_id
        )

        # Delete uploaded PDF
        file_path = Path(document.file_path)

        if file_path.exists():
            file_path.unlink()

        # Delete database record
        db.delete(document)
        db.commit()

        return True
