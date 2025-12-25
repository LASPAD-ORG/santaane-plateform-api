"""add_manuscript_evaluation_status

Revision ID: 20251225_add_evaluation_status
Revises: 20251224_add_evaluation_grids
Create Date: 2025-12-25 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '20251225_add_evaluation_status'
down_revision: Union[str, Sequence[str], None] = '20251224_add_evaluation_grids'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add evaluation_status column to manuscripts table.

    This column tracks the evaluation process status:
    - pending: No evaluators assigned or accepted
    - in_progress: At least 1 evaluator assigned and accepted
    - partially_evaluated: Some evaluators submitted
    - fully_evaluated: All evaluators submitted
    - decision_pending: Evaluations complete, awaiting editorial decision
    """

    # Add evaluation_status column with default value
    op.add_column(
        'manuscripts',
        sa.Column(
            'evaluation_status',
            sa.String(length=50),
            nullable=False,
            server_default='pending'
        )
    )

    # Create index for better query performance
    op.create_index(
        'ix_manuscripts_evaluation_status',
        'manuscripts',
        ['evaluation_status']
    )

    # Note: Existing manuscripts will have their status updated automatically
    # when evaluations are submitted via the EvaluationGridService


def downgrade() -> None:
    """
    Remove evaluation_status column from manuscripts table.
    """

    # Drop index
    op.drop_index('ix_manuscripts_evaluation_status', table_name='manuscripts')

    # Drop column
    op.drop_column('manuscripts', 'evaluation_status')
