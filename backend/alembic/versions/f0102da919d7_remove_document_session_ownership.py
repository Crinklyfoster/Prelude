"""remove document session ownership

Revision ID: f0102da919d7
Revises: 20260619_01_documents_session_id
Create Date: 2026-06-20 12:57:42.752149
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "f0102da919d7"
down_revision: Union[str, Sequence[str], None] = (
    "20260619_01_documents_session_id"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "fk_documents_session_id_chat_sessions",
        "documents",
        type_="foreignkey",
    )

    op.drop_column(
        "documents",
        "session_id",
    )


def downgrade() -> None:
    op.add_column(
        "documents",
        sa.Column(
            "session_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_documents_session_id_chat_sessions",
        "documents",
        "chat_sessions",
        ["session_id"],
        ["id"],
        ondelete="CASCADE",
    )
