import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.db import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )

    filename = Column(String, nullable=False)

    file_path = Column(String, nullable=False)

    status = Column(String, default="uploaded")

    uploaded_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="documents")

