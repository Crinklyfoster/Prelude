from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import File

from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.document import DocumentCreate
from app.schemas.document import DocumentResponse
from app.services import document_service
from app.models.document import Document

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.get("/", response_model=list[DocumentResponse])
def get_documents(
    db: Session = Depends(get_db)
):
    return document_service.get_documents(db)


@router.get("/{document_id}",
            response_model=DocumentResponse)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    document = document_service.get_document_by_id(
        db,
        document_id
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document


@router.post("/", response_model=DocumentResponse)
def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db)
):
    return document_service.create_document(
        db=db,
        document=document
    )

@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    file_path, filename = (
        document_service.save_uploaded_file(file)
    )

    document = Document(
        filename=filename,
        file_path=file_path,
        status="processing"
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "message": "File uploaded successfully",
        "document_id": document.id,
        "filename": document.filename
    }