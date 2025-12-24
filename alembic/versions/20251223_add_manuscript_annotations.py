"""Add manuscript annotations table

Revision ID: add_manuscript_annotations
Revises: 20251223_add_eval
Create Date: 2025-12-23 06:15:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_manuscript_annotations'
down_revision = '20251223_add_eval'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create manuscript_annotations table
    op.create_table(
        'manuscript_annotations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('manuscript_id', sa.Integer(), nullable=False),
        sa.Column('evaluator_id', sa.Integer(), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=False),
        sa.Column('x_position', sa.Float(), nullable=False),
        sa.Column('y_position', sa.Float(), nullable=False),
        sa.Column('comment', sa.String(), nullable=False),
        sa.Column('highlighted_text', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['evaluator_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['manuscript_id'], ['manuscripts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index(
        'ix_manuscript_annotations_manuscript_id',
        'manuscript_annotations',
        ['manuscript_id']
    )
    op.create_index(
        'ix_manuscript_annotations_evaluator_id',
        'manuscript_annotations',
        ['evaluator_id']
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_manuscript_annotations_evaluator_id', table_name='manuscript_annotations')
    op.drop_index('ix_manuscript_annotations_manuscript_id', table_name='manuscript_annotations')
    
    # Drop table
    op.drop_table('manuscript_annotations')
