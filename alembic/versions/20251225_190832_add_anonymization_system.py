"""add anonymization system

Revision ID: 20251225_190832
Revises: 20251225_add_manuscript_evaluation_status
Create Date: 2025-12-25 19:08:32

Adds anonymization support to manuscripts:
- New annotation type 'redaction' for EDITOR to mask sensitive content
- Manuscript columns: is_anonymized, anonymized_at, anonymized_by_id
- ManuscriptAnnotation column: created_by_role to distinguish EDITOR vs EVALUATOR
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '20251225_190832'
down_revision = '20251225_add_evaluation_status'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add anonymization columns to manuscripts table
    op.add_column('manuscripts', sa.Column('is_anonymized', sa.Boolean(),
                                           nullable=False, server_default='false'))
    op.add_column('manuscripts', sa.Column('anonymized_at', sa.DateTime(timezone=True),
                                           nullable=True))
    op.add_column('manuscripts', sa.Column('anonymized_by_id', sa.Integer(),
                                           nullable=True))

    # Create index on is_anonymized for fast queries
    op.create_index('ix_manuscripts_is_anonymized', 'manuscripts', ['is_anonymized'])

    # Create foreign key to users table
    op.create_foreign_key('fk_manuscripts_anonymized_by',
                         'manuscripts', 'users',
                         ['anonymized_by_id'], ['id'])

    # 2. Update CheckConstraint on manuscript_annotations to include 'redaction'
    op.drop_constraint('check_annotation_type', 'manuscript_annotations', type_='check')
    op.create_check_constraint(
        'check_annotation_type',
        'manuscript_annotations',
        "annotation_type IN ('text', 'area', 'freetext', 'redaction')"
    )

    # 3. Add created_by_role column to manuscript_annotations
    op.add_column('manuscript_annotations',
                  sa.Column('created_by_role', sa.String(20), nullable=True))

    # 4. Update existing data: all existing annotations are from EVALUATOR
    op.execute(text("""
        UPDATE manuscript_annotations
        SET created_by_role = 'EVALUATOR'
        WHERE annotation_type IN ('text', 'area', 'freetext')
    """))


def downgrade() -> None:
    # Remove columns from manuscripts
    op.drop_constraint('fk_manuscripts_anonymized_by', 'manuscripts', type_='foreignkey')
    op.drop_index('ix_manuscripts_is_anonymized', 'manuscripts')
    op.drop_column('manuscripts', 'anonymized_by_id')
    op.drop_column('manuscripts', 'anonymized_at')
    op.drop_column('manuscripts', 'is_anonymized')

    # Remove created_by_role from manuscript_annotations
    op.drop_column('manuscript_annotations', 'created_by_role')

    # Restore old CheckConstraint (without 'redaction')
    op.drop_constraint('check_annotation_type', 'manuscript_annotations', type_='check')
    op.create_check_constraint(
        'check_annotation_type',
        'manuscript_annotations',
        "annotation_type IN ('text', 'area', 'freetext')"
    )
