from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from starlette.status import HTTP_204_NO_CONTENT

from app.database.db import get_db
from app.rag.query_rewriter import QueryRewriter
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatSessionRename,
    ChatSessionResponse,
    MessageResponse,
)
from app.services.chat_memory_service import ChatMemoryService
from app.services.rag_service import RAGService

router = APIRouter(prefix="/chat", tags=["Chat"])

rag_service = RAGService()
query_rewriter = QueryRewriter()


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    ChatMemoryService.save_message(
        db=db,
        session_id=request.session_id,
        role="user",
        content=request.question,
    )

    messages = ChatMemoryService.get_recent_messages(
        db=db, session_id=request.session_id
    )

    conversation_history = "\n".join(
        f"{message.role}: {message.content}" for message in messages
    )

    rewritten_question = query_rewriter.rewrite(
        question=request.question, conversation_history=conversation_history
    )

    result = rag_service.answer_question(
        question=rewritten_question,
        conversation_history=conversation_history,
    )


    ChatMemoryService.save_message(
        db=db,
        session_id=request.session_id,
        role="assistant",
        content=result["answer"],
    )

    return ChatResponse(answer=result["answer"], sources=result["sources"])


@router.post("/sessions")
def create_session(db: Session = Depends(get_db)):
    session = ChatMemoryService.create_session(db)

    return {
        "session_id": str(session.id),
    }



@router.get("/sessions", response_model=list[ChatSessionResponse])
def get_sessions(db: Session = Depends(get_db)):
    return ChatMemoryService.get_sessions(db)


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_session(session_id: UUID, db: Session = Depends(get_db)):
    session = ChatMemoryService.get_session(db, session_id)

    if session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")

    return session


@router.get(
    "/sessions/{session_id}/messages", response_model=list[MessageResponse]
)
def get_messages(session_id: UUID, db: Session = Depends(get_db)):
    return ChatMemoryService.get_messages(db, session_id)


@router.patch("/sessions/{session_id}", response_model=ChatSessionResponse)
def rename_session(
    session_id: UUID, request: ChatSessionRename, db: Session = Depends(get_db)
):
    session = ChatMemoryService.rename_session(db, session_id, request.title)

    if session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")

    return session


@router.delete("/sessions/{session_id}", status_code=HTTP_204_NO_CONTENT)
def delete_session(session_id: UUID, db: Session = Depends(get_db)):
    deleted = ChatMemoryService.delete_session(db, session_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Chat session not found")

    return Response(status_code=HTTP_204_NO_CONTENT)
