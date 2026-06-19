from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.chat_session import ChatSession
from app.models.document import Document
from app.models.message import Message
from app.rag.vector_store import ChromaVectorStore


class ChatMemoryService:
    vector_store = ChromaVectorStore()

    @staticmethod
    def generate_title(content):
        title = " ".join(content.split())

        if len(title) <= 60:
            return title

        return f"{title[:57].rstrip()}..."

    @staticmethod
    def create_session(db):
        session = ChatSession(
            title=f"Chat {datetime.now():%H:%M}"
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return session


    @staticmethod
    def get_sessions(db):
        return (
            db.query(ChatSession).order_by(ChatSession.created_at.desc()).all()
        )

    @staticmethod
    def get_session(db, session_id):
        return (
            db.query(ChatSession).filter(ChatSession.id == session_id).first()
        )

    @staticmethod
    def rename_session(db, session_id, title):
        session = ChatMemoryService.get_session(db, session_id)

        if session is None:
            return None

        session.title = title
        db.commit()
        db.refresh(session)

        return session

    @staticmethod
    def delete_session(db: Session, session_id):
        session = ChatMemoryService.get_session(db, session_id)

        if session is None:
            return False

        # Step 1: fetch all documents in the session
        documents = (
            db.query(Document)
            .filter(Document.session_id == session_id)
            .all()
        )

        # Step 2: delete physical files for each document
        for doc in documents:
            file_path = Path(doc.file_path)
            try:
                if file_path.exists():
                    file_path.unlink()
            except OSError:
                # Keep deletion resilient if the file is already missing/locked
                pass

        # Step 3: delete Chroma vectors for each document
        for doc in documents:
            ChatMemoryService.vector_store.delete_document(doc.id)

        # Step 4: delete session (messages/documents rows cascade via ORM)
        db.delete(session)
        db.commit()

        return True

    @staticmethod
    def save_message(db, session_id, role, content):
        is_first_user_message = (
            role == "user"
            and not db.query(Message.id)
            .filter(Message.session_id == session_id, Message.role == "user")
            .first()
        )

        message = Message(session_id=session_id, role=role, content=content)

        db.add(message)

        if is_first_user_message:
            session = ChatMemoryService.get_session(db, session_id)

            if session is not None:
                session.title = ChatMemoryService.generate_title(content)

        db.commit()

    @staticmethod
    def get_recent_messages(db, session_id, limit=6):
        messages = (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )

        return list(reversed(messages))

    @staticmethod
    def get_messages(db, session_id):
        return (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
            .all()
        )
