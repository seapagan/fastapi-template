"""Add banned field to databas

Revision ID: 3ef701c22cf8
Revises: 1850712f171b
Create Date: 2022-10-14 18:44:02.057262

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3ef701c22cf8"
down_revision = "1850712f171b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("banned", sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "banned")
    # ### end Alembic commands ###
