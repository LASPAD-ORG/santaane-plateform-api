"""add_evaluation_grids_table

Revision ID: 20251224_add_evaluation_grids
Revises: 20251224_204756
Create Date: 2025-12-24 22:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '20251224_add_evaluation_grids'
down_revision: Union[str, Sequence[str], None] = '20251224_204756'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create manuscript_evaluation_grids table.

    This table stores evaluation grids filled by evaluators for manuscripts.
    One evaluator can have only one grid per manuscript (UNIQUE constraint).
    """

    # Create manuscript_evaluation_grids table
    op.create_table(
        'manuscript_evaluation_grids',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('manuscript_id', sa.Integer(), nullable=False),
        sa.Column('evaluator_id', sa.Integer(), nullable=False),
        sa.Column('originality_of_ideas', sa.Text(), nullable=False),
        sa.Column('methodology_rigor', sa.Text(), nullable=False),
        sa.Column('theoretical_approach', sa.Text(), nullable=False),
        sa.Column('presentation_clarity', sa.Text(), nullable=False),
        sa.Column('strengths', sa.Text(), nullable=False),
        sa.Column('weaknesses', sa.Text(), nullable=False),
        sa.Column('suggestions', sa.Text(), nullable=True),
        sa.Column('recommendation', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['evaluator_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['manuscript_id'], ['manuscripts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('manuscript_id', 'evaluator_id', name='uq_manuscript_evaluator')
    )

    # Create indexes
    op.create_index('idx_evaluation_grids_manuscript', 'manuscript_evaluation_grids', ['manuscript_id'])
    op.create_index('idx_evaluation_grids_evaluator', 'manuscript_evaluation_grids', ['evaluator_id'])

    # Create trigger for updated_at (reuse existing function from annotations migration)
    op.execute(text("""
        CREATE TRIGGER update_evaluation_grids_updated_at
            BEFORE UPDATE ON manuscript_evaluation_grids
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """))


def downgrade() -> None:
    """
    Drop manuscript_evaluation_grids table.

    WARNING: This will delete all evaluation grids data.
    """

    # Drop trigger
    op.execute(text("DROP TRIGGER IF EXISTS update_evaluation_grids_updated_at ON manuscript_evaluation_grids;"))

    # Drop indexes
    op.drop_index('idx_evaluation_grids_evaluator', table_name='manuscript_evaluation_grids')
    op.drop_index('idx_evaluation_grids_manuscript', table_name='manuscript_evaluation_grids')

    # Drop table
    op.drop_table('manuscript_evaluation_grids')
