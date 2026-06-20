import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from app.database.db import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    filename = Column(String, nullable=False)

    file_path = Column(String, nullable=False)

    status = Column(String, default="uploaded")

    uploaded_at = Column(DateTime, default=datetime.utcnow)




