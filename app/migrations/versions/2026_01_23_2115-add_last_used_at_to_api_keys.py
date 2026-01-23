"""Add last_used_at column to api_keys table.

Revision ID: add_last_used_at
Revises: add_api_keys_table
Create Date: 2026-01-23 21:15:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_last_used_at"
down_revision: Union[str, None] = "add_api_keys_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add last_used_at column to api_keys table."""
    op.add_column(
        "api_keys",
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Remove last_used_at column from api_keys table."""
    op.drop_column("api_keys", "last_used_at")
