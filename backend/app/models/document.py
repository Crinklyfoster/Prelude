import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.db import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    filename = Column(String, nullable=False)

    file_path = Column(String, nullable=False)

    status = Column(String, default="uploaded")

    uploaded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship(
        "User",
        back_populates="documents",
    )
