from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID

from datetime import datetime
import uuid

from app.database.db import Base


class ChatSession(Base):

    __tablename__ = "chat_sessions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id"),
        nullable=False
    )

    title = Column(
        String,
        default="New Chat",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
