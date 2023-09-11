"""Initial

Revision ID: 1850712f171b
Revises:
Create Date: 2022-10-12 18:44:52.351982

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1850712f171b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=True),
        sa.Column("password", sa.String(length=255), nullable=True),
        sa.Column("first_name", sa.String(length=30), nullable=True),
        sa.Column("last_name", sa.String(length=50), nullable=True),
        sa.Column(
            "role",
            sa.Enum("user", "admin", name="roletype"),
            server_default="user",
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("users")
    sa.Enum(name="roletype").drop(op.get_bind(), checkfirst=False)
    # ### end Alembic commands ###