import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship



from app.database.db import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    title = Column(String, default="New Chat", nullable=False)


    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship(
        "User",
        back_populates="chat_sessions",
    )

    messages = relationship(
        "Message",
        back_populates="session",
        cascade="all, delete-orphan",
    )











