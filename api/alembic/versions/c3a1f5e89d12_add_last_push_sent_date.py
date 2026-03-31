"""add_last_push_sent_date_to_users

Revision ID: c3a1f5e89d12
Revises: bb08c7dd5d4a
Create Date: 2026-03-28 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3a1f5e89d12"
down_revision: Union[str, None] = "bb08c7dd5d4a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("last_push_sent_date", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "last_push_sent_date")
