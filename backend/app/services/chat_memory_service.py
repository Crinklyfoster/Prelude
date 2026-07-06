from sqlalchemy.orm import Session

from app.models.chat_session import ChatSession
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
    def create_session(db, *, current_user_id):
        # Title will be set on the first user message.
        session = ChatSession(title="New Chat", user_id=current_user_id)



        db.add(session)
        db.commit()
        db.refresh(session)

        return session


    @staticmethod
    def get_sessions(db, *, current_user_id):
        return (
            db.query(ChatSession)
            .filter(ChatSession.user_id == current_user_id)
            .order_by(ChatSession.created_at.desc())
            .all()
        )


    @staticmethod
    def get_session(db, session_id, *, current_user_id):
        return (
            db.query(ChatSession)
            .filter(
                ChatSession.id == session_id,
                ChatSession.user_id == current_user_id,
            )
            .first()
        )


    @staticmethod
    def rename_session(db, session_id, title, *, current_user_id):
        session = ChatMemoryService.get_session(
            db, session_id, current_user_id=current_user_id
        )


        if session is None:
            return None

        session.title = title
        db.commit()
        db.refresh(session)

        return session

    @staticmethod
    def delete_session(db: Session, session_id, *, current_user_id):
        session = ChatMemoryService.get_session(
            db, session_id, current_user_id=current_user_id
        )


        if session is None:
            return False

        db.delete(session)
        db.commit()

        return True

    @staticmethod
    def save_message(db, session_id, role, content, *, current_user_id):
        is_first_user_message = (
            role == "user"
            and not db.query(Message.id)

            .join(ChatSession, Message.session_id == ChatSession.id)
            .filter(
                Message.session_id == session_id,
                Message.role == "user",
                ChatSession.user_id == current_user_id,
            )
            .first()
        )

        # Ensure session belongs to the user
        session_owned = (
            db.query(ChatSession.id)
            .filter(
                ChatSession.id == session_id,
                ChatSession.user_id == current_user_id,
            )
            .first()
        )

        if session_owned is None:
            raise ValueError("Chat session not found")



        message = Message(session_id=session_id, role=role, content=content)

        db.add(message)

        if is_first_user_message:
            session = ChatMemoryService.get_session(
                db, session_id, current_user_id=current_user_id
            )


            if session is not None:
                session.title = ChatMemoryService.generate_title(content)


        db.commit()

    @staticmethod
    def get_recent_messages(db, session_id, *, current_user_id, limit=6):
        messages = (
            db.query(Message)
            .join(ChatSession, Message.session_id == ChatSession.id)
            .filter(
                Message.session_id == session_id,
                ChatSession.user_id == current_user_id,
            )
            .order_by(Message.created_at.desc())

            .limit(limit)
            .all()
        )

        return list(reversed(messages))


    @staticmethod
    def get_messages(db, session_id, *, current_user_id):
        return (
            db.query(Message)
            .join(ChatSession, Message.session_id == ChatSession.id)
            .filter(
                Message.session_id == session_id,
                ChatSession.user_id == current_user_id,
            )
            .order_by(Message.created_at.asc())
            .all()
        )

