"""add_re_submitted_to_manuscript_status

Revision ID: 5fcc0d62369c
Revises: da643006536b
Create Date: 2025-12-23 00:07:09.876519

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '5fcc0d62369c'
down_revision: Union[str, Sequence[str], None] = 'da643006536b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add 're_submitted' value to manuscriptstatus enum (after SUBMITTED which is uppercase)
    op.execute("ALTER TYPE manuscriptstatus ADD VALUE IF NOT EXISTS 're_submitted'")


def downgrade() -> None:
    """Downgrade schema."""
    # Note: PostgreSQL doesn't support removing enum values directly
    # You would need to recreate the enum type if you want to remove the value
    pass
