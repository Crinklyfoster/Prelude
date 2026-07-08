from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatRequest(BaseModel):
    session_id: str
    question: str
    document_ids: list[str] | None = None


class Source(BaseModel):
    chunk_id: int
    document_id: str
    score: float
    preview: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


class ChatSessionRename(BaseModel):
    title: str = Field(min_length=1, max_length=255)

    @field_validator("title")
    @classmethod
    def validate_title(cls, title):
        title = title.strip()
        if not title:
            raise ValueError("Title must not be empty")
        return title


class ChatSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    created_at: datetime


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID
    role: str
    content: str
    created_at: datetime
