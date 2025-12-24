"""redesign_annotation_system_with_uuid

Revision ID: 20251224_204756
Revises: 19ba8f0efa3a
Create Date: 2025-12-24 20:47:56

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '20251224_204756'
down_revision: Union[str, Sequence[str], None] = '19ba8f0efa3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Redesign manuscript_annotations table with UUID IDs and new schema.

    Strategy: Drop and recreate (test data only exists)
    Changes:
    - ID: INTEGER -> VARCHAR(255) UUID
    - Add: annotation_type VARCHAR(20) with CHECK constraint
    - Add: position_data TEXT (JSON stringified)
    - Add: content_data TEXT (JSON stringified, nullable)
    - Remove: highlighted_text
    """

    # Drop existing table with all its indexes
    op.drop_index('ix_manuscript_annotations_manuscript_id', table_name='manuscript_annotations')
    op.drop_index('ix_manuscript_annotations_evaluator_id', table_name='manuscript_annotations')
    op.drop_table('manuscript_annotations')

    # Recreate table with new schema
    op.create_table(
        'manuscript_annotations',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('manuscript_id', sa.Integer(), nullable=False),
        sa.Column('evaluator_id', sa.Integer(), nullable=False),
        sa.Column('annotation_type', sa.String(length=20), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=False),
        sa.Column('x_position', sa.Float(), nullable=False),
        sa.Column('y_position', sa.Float(), nullable=False),
        sa.Column('position_data', sa.Text(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=False),
        sa.Column('content_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['evaluator_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['manuscript_id'], ['manuscripts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint(
            "annotation_type IN ('text', 'area', 'freetext')",
            name='check_annotation_type'
        ),
        sa.CheckConstraint(
            'page_number >= 1',
            name='check_page_number_positive'
        )
    )

    # Recreate indexes
    op.create_index('idx_manuscript_annotations_manuscript', 'manuscript_annotations', ['manuscript_id'])
    op.create_index('idx_manuscript_annotations_evaluator', 'manuscript_annotations', ['evaluator_id'])

    # Create function for updated_at trigger if it doesn't exist
    op.execute(text("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """))

    # Create trigger for updated_at
    op.execute(text("""
        CREATE TRIGGER update_manuscript_annotations_updated_at
            BEFORE UPDATE ON manuscript_annotations
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """))


def downgrade() -> None:
    """
    Rollback to old schema with INTEGER IDs.

    WARNING: This will lose any annotations created with the new schema.
    """

    # Drop new table
    op.execute(text("DROP TRIGGER IF EXISTS update_manuscript_annotations_updated_at ON manuscript_annotations;"))
    op.drop_index('idx_manuscript_annotations_evaluator', table_name='manuscript_annotations')
    op.drop_index('idx_manuscript_annotations_manuscript', table_name='manuscript_annotations')
    op.drop_table('manuscript_annotations')

    # Recreate old table schema
    op.create_table(
        'manuscript_annotations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('manuscript_id', sa.Integer(), nullable=False),
        sa.Column('evaluator_id', sa.Integer(), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=False),
        sa.Column('x_position', sa.Float(), nullable=False),
        sa.Column('y_position', sa.Float(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=False),
        sa.Column('highlighted_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['evaluator_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['manuscript_id'], ['manuscripts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Recreate old indexes
    op.create_index('ix_manuscript_annotations_evaluator_id', 'manuscript_annotations', ['evaluator_id'])
    op.create_index('ix_manuscript_annotations_manuscript_id', 'manuscript_annotations', ['manuscript_id'])
