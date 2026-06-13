from fastapi import APIRouter

from app.schemas.chat import (
    ChatRequest,
    ChatResponse
)
from app.services.rag_service import RAGService

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

rag_service = RAGService()


@router.post(
    "/",
    response_model=ChatResponse
)
def chat(
    request: ChatRequest
):
    result = rag_service.answer_question(
        question=request.question,
        document_id=request.document_id
    )

    return ChatResponse(
        answer=result["answer"],
        document_id=request.document_id
    )