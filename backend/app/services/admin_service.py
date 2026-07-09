from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.audit_logger import log_admin_event
from app.models.chat_session import ChatSession
from app.models.document import Document
from app.models.message import Message
from app.models.user import User
from app.rag.lexical_index import LexicalIndex
from app.rag.vector_store import ChromaVectorStore
from app.services.background_tasks import process_document_background
from app.services.health_service import HealthService

# Shared RAG store instances (loaded once at import time)
_vector_store = ChromaVectorStore()
_lexical_index = LexicalIndex()


# ── Dashboard ─────────────────────────────────────────────────────────────────

def get_dashboard_stats(db: Session) -> dict:
    health = HealthService.get_health_status()

    return {
        "users": db.query(User).count(),
        "documents": db.query(Document).count(),
        "sessions": db.query(ChatSession).count(),
        "messages": db.query(Message).count(),
        "database": health["postgres"],
        "ollama": health["ollama"],
        "status": health["status"],
    }


# ── User Management ───────────────────────────────────────────────────────────

def get_all_users(db: Session) -> list[User]:
    return (
        db.query(User)
        .order_by(User.created_at.desc())
        .all()
    )


def update_user_role(
    db: Session,
    user_id: UUID,
    role: str,
    acting_user_id: UUID,
) -> User:
    """Change a user's role with safety guards.

    Guards:
    - Cannot demote the last remaining admin (locks out all admins).
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Guard: demoting last admin
    if role == "user" and user.role == "admin":
        admin_count = db.query(User).filter(User.role == "admin").count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot demote the last remaining admin",
            )

    user.role = role
    db.commit()
    db.refresh(user)

    log_admin_event(
        action="update_role",
        admin_id=str(acting_user_id),
        target_id=str(user.id),
        new_role=role,
    )

    return user


def delete_user(
    db: Session,
    user_id: UUID,
    acting_user_id: UUID,
) -> bool:
    """Delete a user with safety guards.

    Guards:
    - Admins cannot delete themselves.
    """
    if user_id == acting_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db.delete(user)
    db.commit()

    log_admin_event(
        action="delete_user",
        admin_id=str(acting_user_id),
        target_id=str(user.id),
    )

    return True


# ── Document Management ───────────────────────────────────────────────────────

def get_all_documents(db: Session) -> list[Document]:
    return (
        db.query(Document)
        .join(User)
        .order_by(Document.uploaded_at.desc())
        .all()
    )


def admin_delete_document(
    db: Session,
    document_id: UUID,
    acting_user_id: UUID | None = None,
) -> bool:
    """Hard-delete a document: removes the file, vector embeddings,
    lexical index entries, and the DB row."""
    document = db.query(Document).filter(Document.id == document_id).first()

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Remove from vector store and lexical index
    _vector_store.delete_document(document.id)
    _lexical_index.remove_document(document.id)

    # Delete the physical file if it still exists
    file_path = Path(document.file_path)
    if file_path.exists():
        file_path.unlink()

    db.delete(document)
    db.commit()

    log_admin_event(
        action="delete_document",
        admin_id=str(acting_user_id) if acting_user_id else "system",
        target_id=str(document.id),
    )

    return True


def reindex_document(
    db: Session,
    document_id: UUID,
    acting_user_id: UUID | None = None,
) -> bool:
    """Re-trigger background ingestion for a document.

    Sets status → 'processing' immediately and kicks off the background
    task. Replace the direct call with a Celery task when available.
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    document.status = "processing"
    db.commit()

    process_document_background(
        document.id,
        document.file_path,
    )

    log_admin_event(
        action="reindex_document",
        admin_id=str(acting_user_id) if acting_user_id else "system",
        target_id=str(document.id),
    )

    return True


# ── Session Management ────────────────────────────────────────────────────────

def get_all_sessions(db: Session) -> list[dict]:
    """Return session metadata with message counts.

    Uses a correlated COUNT subquery so we never load message rows just
    to count them — keeps the list endpoint fast as chat history grows.
    """
    from sqlalchemy import func

    rows = (
        db.query(
            ChatSession,
            func.count(Message.id).label("message_count"),
        )
        .join(User, ChatSession.user_id == User.id)
        .outerjoin(Message, Message.session_id == ChatSession.id)
        .group_by(ChatSession.id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )

    return [
        {
            "id": str(session.id),
            "title": session.title,
            "owner": session.user.email,
            "created_at": session.created_at.isoformat(),
            "message_count": count,
        }
        for session, count in rows
    ]


def get_session_messages(
    db: Session,
    session_id: UUID,
) -> list[Message]:
    """Fetch the full message thread for one session."""
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id)
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at)
        .all()
    )


def delete_session(
    db: Session,
    session_id: UUID,
    acting_user_id: UUID | None = None,
) -> bool:
    """Delete a session (cascade removes all messages automatically)."""
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id)
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    db.delete(session)
    db.commit()

    log_admin_event(
        action="delete_session",
        admin_id=str(acting_user_id) if acting_user_id else "system",
        target_id=str(session.id),
    )

    return True

