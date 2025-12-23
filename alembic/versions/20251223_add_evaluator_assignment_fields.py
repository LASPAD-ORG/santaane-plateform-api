"""add evaluator assignment status fields

Revision ID: 20251223_add_eval
Revises: 5fcc0d62369c
Create Date: 2025-12-23 03:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20251223_add_eval'
down_revision: Union[str, Sequence[str], None] = '5fcc0d62369c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enum type
    op.execute("CREATE TYPE evaluatorassignmentstatus AS ENUM ('pending', 'accepted', 'declined')")
    
    # Add columns to manuscript_evaluators
    op.add_column('manuscript_evaluators', 
        sa.Column('status', sa.String(), nullable=False, server_default='pending'))
    op.add_column('manuscript_evaluators', 
        sa.Column('response_at', sa.DateTime(), nullable=True))
    op.add_column('manuscript_evaluators', 
        sa.Column('evaluation_deadline', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove added columns
    op.drop_column('manuscript_evaluators', 'evaluation_deadline')
    op.drop_column('manuscript_evaluators', 'response_at')
    op.drop_column('manuscript_evaluators', 'status')
    
    # Drop enum type
    op.execute("DROP TYPE evaluatorassignmentstatus")
