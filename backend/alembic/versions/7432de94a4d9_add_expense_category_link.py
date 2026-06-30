"""add expense category link

Revision ID: 7432de94a4d9
Revises: eefe0349a3fd
Create Date: 2026-06-30 13:39:05.431416

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7432de94a4d9'
down_revision: Union[str, Sequence[str], None] = 'eefe0349a3fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("expenses", schema=None) as batch_op:
        batch_op.add_column(sa.Column("category_id", sa.Integer(), nullable=True))
        batch_op.create_index(
            batch_op.f("ix_expenses_category_id"), ["category_id"], unique=False
        )
        batch_op.create_foreign_key(
            "fk_expenses_category_id",
            "categories",
            ["category_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("expenses", schema=None) as batch_op:
        batch_op.drop_constraint("fk_expenses_category_id", type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_expenses_category_id"))
        batch_op.drop_column("category_id")
