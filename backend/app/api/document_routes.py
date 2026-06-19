from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.document import DocumentCreate, DocumentResponse
from app.services import document_service
from app.services.background_tasks import process_document_background

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=list[DocumentResponse])
def get_documents(db: Session = Depends(get_db)):
    return document_service.get_documents(db)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: UUID, db: Session = Depends(get_db)):
    document = document_service.get_document_by_id(db, document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document


@router.post("", response_model=DocumentResponse)
def create_document(
    document: DocumentCreate,
    session_id: UUID,
    db: Session = Depends(get_db),
):
    return document_service.create_document(
        db=db, session_id=session_id, document=document
    )



@router.post("/sessions/{session_id}/documents")
def upload_document(
    session_id: UUID,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Only PDF files are supported"
        )

    result = document_service.upload_document(
        db=db,
        session_id=session_id,
        file=file,
    )



    background_tasks.add_task(
        process_document_background, result["document_id"], result["file_path"]
    )

    return {
        "document_id": result["document_id"],
        "filename": result["filename"],
        "status": result["status"],
    }



@router.delete("/{document_id}")
def delete_document(document_id: UUID, db: Session = Depends(get_db)):
    deleted = document_service.delete_document(db, document_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"message": "Document deleted successfully"}
