import time
from pathlib import Path
from uuid import uuid4

# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.core.audit_logger import log_document_event
from app.core.metrics import DOCUMENT_UPLOADS
from app.models.document import Document
from app.rag.lexical_index import LexicalIndex
from app.rag.vector_store import ChromaVectorStore
from app.schemas.document import DocumentCreate
from app.services.ingestion_service import IngestionService

ingestion_service = IngestionService()
vector_store = ChromaVectorStore()
lexical_index = LexicalIndex()


def create_document(db: Session, document: DocumentCreate, *, current_user_id):

    new_document = Document(
        filename=document.filename,
        file_path=document.file_path,
        status="uploaded",
        user_id=current_user_id,
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return new_document


def get_documents(db: Session, *, current_user_id):
    return db.query(Document).filter(Document.user_id == current_user_id).all()


def get_document_by_id(db: Session, document_id, *, current_user_id):
    return (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == current_user_id,
        )
        .first()
    )


def save_uploaded_file(file):
    upload_dir = Path("uploads")

    upload_dir.mkdir(parents=True, exist_ok=True)

    unique_filename = f"{uuid4()}.pdf"

    file_path = upload_dir / unique_filename

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return str(file_path), unique_filename


def upload_document(db, file, *, current_user_id):

    start = time.time()

    file_path, _ = save_uploaded_file(file)

    document = Document(
        filename=file.filename,
        file_path=file_path,
        status="processing",
        user_id=current_user_id,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    DOCUMENT_UPLOADS.inc()

    log_document_event(
        action="upload",
        document_id=str(document.id),
        user_id=str(current_user_id),
        filename=document.filename,
        duration=round(time.time() - start, 2),
    )

    return {
        "document_id": str(document.id),
        "filename": document.filename,
        "status": document.status,
        "file_path": document.file_path,
    }


def delete_document(db: Session, document_id, *, current_user_id):
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == current_user_id,
        )
        .first()
    )

    if not document:
        return False

    # Delete vectors from Chroma
    vector_store.delete_document(document.id)
    lexical_index.remove_document(document.id)

    # Delete uploaded PDF
    file_path = Path(str(document.file_path))

    if file_path.exists():
        file_path.unlink()

    # Delete database record
    db.delete(document)
    db.commit()

    log_document_event(
        action="delete",
        document_id=str(document_id),
        user_id=str(current_user_id),
        filename=document.filename,
    )

    return True
