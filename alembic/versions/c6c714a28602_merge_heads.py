"""merge heads

Revision ID: c6c714a28602
Revises: 6499f3161f2c, 15930d2cd227
Create Date: 2025-11-25 13:28:22.800799

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'c6c714a28602'
down_revision: Union[str, Sequence[str], None] = ('6499f3161f2c', '15930d2cd227')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
