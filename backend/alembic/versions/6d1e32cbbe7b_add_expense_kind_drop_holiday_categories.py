"""add expense kind, drop holiday categories

Revision ID: 6d1e32cbbe7b
Revises: 08c46d12eb5b
Create Date: 2026-06-30 10:29:34.243157

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6d1e32cbbe7b'
down_revision: Union[str, Sequence[str], None] = '08c46d12eb5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Postgres requires the enum type to exist before a column can reference
    # it. batch_alter_table doesn't auto-emit CREATE TYPE, so do it here
    # explicitly. On SQLite this is a no-op (enums are stored as text).
    expense_kind = sa.Enum("regular", "unusual", name="expensekind")
    expense_kind.create(op.get_bind(), checkfirst=True)

    with op.batch_alter_table("expenses", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "kind",
                # create_type=False because we created it above; otherwise
                # SQLAlchemy would try to issue CREATE TYPE again on Postgres.
                sa.Enum("regular", "unusual", name="expensekind", create_type=False),
                server_default="regular",
                nullable=False,
            )
        )
        batch_op.create_index(batch_op.f("ix_expenses_kind"), ["kind"], unique=False)

    # Holiday is no longer budgeted — drop legacy categories and any budget
    # entries that referenced them. ON DELETE CASCADE removes the budget
    # entries automatically when the categories go.
    op.execute("DELETE FROM categories WHERE \"group\" = 'holiday'")


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("expenses", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_expenses_kind"))
        batch_op.drop_column("kind")

    # Drop the enum type after the column that referenced it is gone.
    sa.Enum(name="expensekind").drop(op.get_bind(), checkfirst=True)
