"""add manuscript_id to review_responses

Revision ID: 15930d2cd227
Revises: 14829c1bc116
Create Date: 2025-11-25 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '15930d2cd227'
down_revision: Union[str, None] = '14829c1bc116'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add manuscript_id column to review_responses for easier queries."""
    # Add column (nullable first to allow existing data)
    op.add_column('review_responses', sa.Column('manuscript_id', sa.Integer(), nullable=True))

    # Populate manuscript_id from review_assignments
    op.execute("""
        UPDATE review_responses rr
        SET manuscript_id = ra.manuscript_id
        FROM review_assignments ra
        WHERE rr.review_assignment_id = ra.id
    """)

    # Make column non-nullable
    op.alter_column('review_responses', 'manuscript_id', nullable=False)

    # Add foreign key constraint
    op.create_foreign_key(
        'fk_review_responses_manuscript_id',
        'review_responses',
        'manuscripts',
        ['manuscript_id'],
        ['id']
    )

    # Add index
    op.create_index(
        op.f('ix_review_responses_manuscript_id'),
        'review_responses',
        ['manuscript_id'],
        unique=False
    )


def downgrade() -> None:
    """Remove manuscript_id column from review_responses."""
    op.drop_index(op.f('ix_review_responses_manuscript_id'), table_name='review_responses')
    op.drop_constraint('fk_review_responses_manuscript_id', 'review_responses', type_='foreignkey')
    op.drop_column('review_responses', 'manuscript_id')
