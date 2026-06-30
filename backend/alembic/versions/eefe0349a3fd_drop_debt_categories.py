"""drop debt categories

Revision ID: eefe0349a3fd
Revises: 6d1e32cbbe7b
Create Date: 2026-06-30 10:41:39.024699

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eefe0349a3fd'
down_revision: Union[str, Sequence[str], None] = '6d1e32cbbe7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop legacy DEBT categories. Associated budget entries cascade away
    via the categories->budget_entries FK with ON DELETE CASCADE."""
    op.execute("DELETE FROM categories WHERE \"group\" = 'debt'")


def downgrade() -> None:
    """No-op: this migration only removes data, not schema."""
    pass
