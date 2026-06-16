"""add chat session title

Revision ID: 20260615_01
Revises:
Create Date: 2026-06-15
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260615_01"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "chat_sessions",
        sa.Column(
            "title",
            sa.String(),
            nullable=False,
            server_default="New Chat"
        )
    )


def downgrade() -> None:
    op.drop_column("chat_sessions", "title")
