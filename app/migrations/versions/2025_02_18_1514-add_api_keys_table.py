"""Add API keys table.

Revision ID: add_api_keys_table
Revises: 5a8bd25c2227
Create Date: 2025-02-18 15:14:52.123456

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "add_api_keys_table"
down_revision: Union[str, None] = "5a8bd25c2227"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database to this revision."""
    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(255), unique=True, nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("scopes", postgresql.ARRAY(sa.String()), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_api_keys_user_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_api_keys_key", "api_keys", ["key"], unique=True
    )
    op.create_index(
        "ix_api_keys_user_id", "api_keys", ["user_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade database to the previous revision."""
    op.drop_index("ix_api_keys_user_id")
    op.drop_index("ix_api_keys_key")
    op.drop_table("api_keys")
