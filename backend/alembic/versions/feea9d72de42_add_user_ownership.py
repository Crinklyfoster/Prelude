"""add user ownership

Revision ID: feea9d72de42
Revises: 2fb107ae02ce
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "feea9d72de42"
down_revision: Union[str, Sequence[str], None] = "2fb107ae02ce"
branch_labels = None
depends_on = None


def upgrade() -> None:

    # Development database only
    op.execute("DELETE FROM messages")
    op.execute("DELETE FROM chat_sessions")
    op.execute("DELETE FROM documents")

    # ---------------- Documents ----------------

    op.add_column(
        "documents",
        sa.Column("user_id", sa.UUID(), nullable=True),
    )

    op.create_foreign_key(
        "fk_documents_user_id",
        "documents",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.alter_column(
        "documents",
        "user_id",
        nullable=False,
    )

    # ---------------- Chat Sessions ----------------

    op.add_column(
        "chat_sessions",
        sa.Column("user_id", sa.UUID(), nullable=True),
    )

    op.create_foreign_key(
        "fk_chat_sessions_user_id",
        "chat_sessions",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.alter_column(
        "chat_sessions",
        "user_id",
        nullable=False,
    )


def downgrade() -> None:

    op.drop_constraint(
        "fk_chat_sessions_user_id",
        "chat_sessions",
        type_="foreignkey",
    )

    op.drop_column(
        "chat_sessions",
        "user_id",
    )

    op.drop_constraint(
        "fk_documents_user_id",
        "documents",
        type_="foreignkey",
    )

    op.drop_column(
        "documents",
        "user_id",
    )

