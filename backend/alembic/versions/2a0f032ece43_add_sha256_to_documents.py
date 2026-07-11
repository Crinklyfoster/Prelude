"""add sha256 to documents

Revision ID: 2a0f032ece43
Revises: a1b2c3d4e5f6
Create Date: 2026-07-11 17:55:58.621356
"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = '2a0f032ece43'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column(
            "sha256",
            sa.String(length=64),
            nullable=True,
        ),
    )
    
    op.execute("UPDATE documents SET sha256 = REPLACE(id::text, '-', '') WHERE sha256 IS NULL")
    
    op.alter_column(
        "documents",
        "sha256",
        nullable=False,
    )
    
    op.create_unique_constraint(
        "uq_user_document_sha256",
        "documents",
        ["user_id", "sha256"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_user_document_sha256", "documents", type_="unique")
    op.drop_column("documents", "sha256")
