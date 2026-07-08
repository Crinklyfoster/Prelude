"""documents.session_id foreign key + relationships"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "20260619_01_documents_session_id"
down_revision = "000_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Since you don't need older chats/documents, we can safely reset data
    # to avoid backfill complexity for NOT NULL.
    op.execute("DELETE FROM messages")
    op.execute("DELETE FROM chat_sessions")
    op.execute("DELETE FROM documents")

    # Add documents.session_id (nullable first to avoid immediate failures)
    op.add_column(
        "documents",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # For existing rows (if any remain), set to NULL-safe value isn't possible.
    # But we already deleted all rows above.

    # Enforce NOT NULL
    op.alter_column("documents", "session_id", nullable=False)

    # Add FK with ON DELETE CASCADE
    op.create_foreign_key(
        "fk_documents_session_id_chat_sessions",
        "documents",
        "chat_sessions",
        ["session_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Drop chat_sessions.document_id from initial schema
    op.drop_constraint(
        "chat_sessions_document_id_fkey",
        "chat_sessions",
        type_="foreignkey",
    )

    op.drop_column("chat_sessions", "document_id")


def downgrade() -> None:
    # Reverse operation by recreating chat_sessions.document_id.
    op.add_column(
        "chat_sessions",
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.create_foreign_key(
        "chat_sessions_document_id_fkey",
        "chat_sessions",
        "documents",
        ["document_id"],
        ["id"],
    )

    op.drop_constraint(
        "fk_documents_session_id_chat_sessions",
        "documents",
        type_="foreignkey",
    )

    op.drop_column("documents", "session_id")
