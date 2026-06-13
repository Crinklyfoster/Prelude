from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.document import Document
from app.schemas.document import DocumentCreate


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

    unique_filename = f"{uuid4()}_{file.filename}"

    file_path = upload_dir / unique_filename

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return str(file_path), unique_filename