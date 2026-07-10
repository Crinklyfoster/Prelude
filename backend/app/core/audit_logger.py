from app.core.logger import get_logger

_logger = get_logger("audit")

def log_auth_event(action: str, user_id: str, email: str, **kwargs):
    """Log an authentication event (e.g. login, logout, register)."""
    _logger.info(
        f"Auth event: {action}",
        extra={
            "event_type": "auth",
            "action": action,
            "user_id": user_id,
            "email": email,
            **kwargs,
        },
    )

def log_document_event(
    action: str,
    document_id: str,
    user_id: str,
    filename: str,
    **kwargs,
):
    """Log a document event (e.g. upload, process, delete)."""
    _logger.info(
        f"Document event: {action}",
        extra={
            "event_type": "document",
            "action": action,
            "document_id": document_id,
            "user_id": user_id,
            "doc_filename": filename,
            **kwargs,
        },
    )

def log_chat_event(action: str, session_id: str, user_id: str, **kwargs):
    """Log a chat event (e.g. new_session, message_sent, session_deleted)."""
    _logger.info(
        f"Chat event: {action}",
        extra={
            "event_type": "chat",
            "action": action,
            "session_id": session_id,
            "user_id": user_id,
            **kwargs,
        },
    )

def log_retrieval_event(action: str, query: str, user_id: str, **kwargs):
    """Log a retrieval event (e.g. retrieve_dense, retrieve_hybrid)."""
    _logger.info(
        f"Retrieval event: {action}",
        extra={
            "event_type": "retrieval",
            "action": action,
            "query": query,
            "user_id": user_id,
            **kwargs,
        },
    )

def log_llm_event(action: str, session_id: str, model: str, **kwargs):
    """Log an LLM generation event."""
    _logger.info(
        f"LLM event: {action}",
        extra={
            "event_type": "llm",
            "action": action,
            "session_id": session_id,
            "model": model,
            **kwargs,
        },
    )

def log_admin_event(action: str, admin_id: str, target_id: str, **kwargs):
    """Log an administrative event (e.g. role_change, user_delete)."""
    _logger.info(
        f"Admin event: {action}",
        extra={
            "event_type": "admin",
            "action": action,
            "admin_id": admin_id,
            "target_id": target_id,
            **kwargs,
        },
    )
