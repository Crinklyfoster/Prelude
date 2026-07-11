from typing import Annotated
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
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentResponse
from app.services import document_service
from app.services.background_tasks import process_document_background

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=list[DocumentResponse])
def get_documents(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return document_service.get_documents(db, current_user_id=current_user.id)


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    responses={404: {"description": "Document not found"}},
)
def get_document(
    document_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    document = document_service.get_document_by_id(
        db,
        document_id,
        current_user_id=current_user.id,
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document


@router.post("", response_model=DocumentResponse)
def create_document(
    document: DocumentCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return document_service.create_document(
        db=db, document=document, current_user_id=current_user.id
    )


@router.post(
    "/upload",
    responses={400: {"description": "Only PDF files are supported"}},
)
def upload_document(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Only PDF files are supported"
        )

    result = document_service.upload_document(
        db=db,
        file=file,
        current_user_id=current_user.id,
    )

    background_tasks.add_task(
        process_document_background,
        result["document_id"],
        result["file_path"],
    )

    return {
        "document_id": result["document_id"],
        "filename": result["filename"],
        "status": result["status"],
    }


@router.delete(
    "/{document_id}",
    responses={404: {"description": "Document not found"}},
)
def delete_document(
    document_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    deleted = document_service.delete_document(
        db,
        document_id,
        current_user_id=current_user.id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"message": "Document deleted successfully"}
