import json
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from starlette.status import HTTP_204_NO_CONTENT

from app.database.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
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

ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
ERROR_CHAT_SESSION_NOT_FOUND = "Chat session not found"


@router.post("", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    ChatMemoryService.save_message(
        db=db,
        session_id=request.session_id,
        role=ROLE_USER,
        content=request.question,
        current_user_id=current_user.id,
    )

    messages = ChatMemoryService.get_recent_messages(
        db=db, session_id=request.session_id, current_user_id=current_user.id
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
        current_user_id=current_user.id,
        document_ids=request.document_ids,
        provider_override=request.provider,
    )

    ChatMemoryService.save_message(
        db=db,
        session_id=request.session_id,
        role=ROLE_ASSISTANT,
        content=result["answer"],
        current_user_id=current_user.id,
    )

    return ChatResponse(answer=result["answer"], sources=result["sources"])


def _sse_pack(event: str, data: dict) -> str:
    # SSE format: event: <name>\ndata: <json>\n\n
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.post("/stream")
def stream_chat(
    request: ChatRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    ChatMemoryService.save_message(
        db=db,
        session_id=request.session_id,
        role=ROLE_USER,
        content=request.question,
        current_user_id=current_user.id,
    )

    messages = ChatMemoryService.get_recent_messages(
        db=db, session_id=request.session_id, current_user_id=current_user.id
    )

    conversation_history = "\n".join(
        f"{message.role}: {message.content}" for message in messages
    )

    rewritten_question = query_rewriter.rewrite(
        question=request.question, conversation_history=conversation_history
    )

    def event_generator():
        full_response = ""

        for chunk in rag_service.stream_answer(
            question=rewritten_question,
            conversation_history=conversation_history,
            current_user_id=current_user.id,
            document_ids=request.document_ids,
            provider_override=request.provider,
        ):
            if chunk.get("type") == "token":
                token = chunk.get("token", "")
                if isinstance(token, str) and token:
                    full_response += token
                    yield _sse_pack("token", {"token": token})
            elif chunk.get("type") == "meta":
                # Save assistant message once streaming is done.
                ChatMemoryService.save_message(
                    db=db,
                    session_id=request.session_id,
                    role=ROLE_ASSISTANT,
                    content=full_response,
                    current_user_id=current_user.id,
                )

                meta_data = {
                    "sources": chunk.get("sources", []),
                    "final": chunk.get("final", True),
                }
                if chunk.get("provider_meta"):
                    meta_data["provider_meta"] = chunk.get("provider_meta")
                yield _sse_pack("meta", meta_data)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/sessions")
def create_session(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    session = ChatMemoryService.create_session(
        db,
        current_user_id=current_user.id,
    )

    return {
        "session_id": str(session.id),
    }


@router.get("/sessions", response_model=list[ChatSessionResponse])
def get_sessions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return ChatMemoryService.get_sessions(db, current_user_id=current_user.id)


@router.get(
    "/sessions/{session_id}",
    response_model=ChatSessionResponse,
    responses={404: {"description": ERROR_CHAT_SESSION_NOT_FOUND}},
)
def get_session(
    session_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    session = ChatMemoryService.get_session(
        db,
        session_id,
        current_user_id=current_user.id,
    )

    if session is None:
        raise HTTPException(status_code=404, detail=ERROR_CHAT_SESSION_NOT_FOUND)

    return session


@router.get(
    "/sessions/{session_id}/messages", response_model=list[MessageResponse]
)
def get_messages(
    session_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return ChatMemoryService.get_messages(
        db,
        session_id,
        current_user_id=current_user.id,
    )


@router.patch(
    "/sessions/{session_id}",
    response_model=ChatSessionResponse,
    responses={404: {"description": ERROR_CHAT_SESSION_NOT_FOUND}},
)
def rename_session(
    session_id: UUID,
    request: ChatSessionRename,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    session = ChatMemoryService.rename_session(
        db, session_id, request.title, current_user_id=current_user.id
    )

    if session is None:
        raise HTTPException(status_code=404, detail=ERROR_CHAT_SESSION_NOT_FOUND)

    return session


@router.delete(
    "/sessions/{session_id}",
    status_code=HTTP_204_NO_CONTENT,
    responses={404: {"description": ERROR_CHAT_SESSION_NOT_FOUND}},
)
def delete_session(
    session_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    deleted = ChatMemoryService.delete_session(
        db,
        session_id,
        current_user_id=current_user.id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail=ERROR_CHAT_SESSION_NOT_FOUND)

    return Response(status_code=HTTP_204_NO_CONTENT)
