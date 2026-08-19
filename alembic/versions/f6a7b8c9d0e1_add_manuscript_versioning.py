"""add manuscript versioning (versions + archived evaluations)

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-08-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, Sequence[str], None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Table manuscript_versions (creee EN PREMIER : les archives la referencent)
    op.create_table(
        'manuscript_versions',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('manuscript_id', sa.Integer(), sa.ForeignKey('manuscripts.id'), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('pdf_filename', sa.String(length=255), nullable=False),
        sa.Column('docx_filename', sa.String(length=255), nullable=True),
        sa.Column('initial_docx_filename', sa.String(length=255), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('abstract', sa.Text(), nullable=True),
        sa.Column('keywords', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('archived_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_manuscript_versions_manuscript_id', 'manuscript_versions', ['manuscript_id'])
    op.create_index('ix_manuscript_versions_version_number', 'manuscript_versions', ['version_number'])

    # 2. Table archived_evaluation_grids
    op.create_table(
        'archived_evaluation_grids',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('version_id', sa.Integer(), sa.ForeignKey('manuscript_versions.id'), nullable=False),
        sa.Column('manuscript_id', sa.Integer(), nullable=False),
        sa.Column('evaluator_id', sa.Integer(), nullable=False),
        sa.Column('evaluator_kind', sa.String(length=20), nullable=True),
        sa.Column('originality_of_ideas', sa.Text(), nullable=True),
        sa.Column('methodology_rigor', sa.Text(), nullable=True),
        sa.Column('theoretical_approach', sa.Text(), nullable=True),
        sa.Column('presentation_clarity', sa.Text(), nullable=True),
        sa.Column('strengths', sa.Text(), nullable=True),
        sa.Column('weaknesses', sa.Text(), nullable=True),
        sa.Column('suggestions', sa.Text(), nullable=True),
        sa.Column('editorial_line_fit', sa.Text(), nullable=True),
        sa.Column('global_opinion', sa.Text(), nullable=True),
        sa.Column('recommendation', sa.String(length=50), nullable=True),
        sa.Column('original_created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('original_updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('original_submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('archived_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_archived_evaluation_grids_version_id', 'archived_evaluation_grids', ['version_id'])
    op.create_index('ix_archived_evaluation_grids_manuscript_id', 'archived_evaluation_grids', ['manuscript_id'])
    op.create_index('ix_archived_evaluation_grids_evaluator_id', 'archived_evaluation_grids', ['evaluator_id'])

    # 3. Table archived_annotations
    op.create_table(
        'archived_annotations',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('version_id', sa.Integer(), sa.ForeignKey('manuscript_versions.id'), nullable=False),
        sa.Column('original_annotation_id', sa.String(length=255), nullable=True),
        sa.Column('manuscript_id', sa.Integer(), nullable=False),
        sa.Column('evaluator_id', sa.Integer(), nullable=False),
        sa.Column('evaluator_kind', sa.String(length=20), nullable=True),
        sa.Column('annotation_type', sa.String(length=20), nullable=True),
        sa.Column('created_by_role', sa.String(length=20), nullable=True),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('x_position', sa.Float(), nullable=True),
        sa.Column('y_position', sa.Float(), nullable=True),
        sa.Column('position_data', sa.Text(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('content_data', sa.Text(), nullable=True),
        sa.Column('original_created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('original_updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('archived_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_archived_annotations_version_id', 'archived_annotations', ['version_id'])
    op.create_index('ix_archived_annotations_manuscript_id', 'archived_annotations', ['manuscript_id'])
    op.create_index('ix_archived_annotations_evaluator_id', 'archived_annotations', ['evaluator_id'])

    # 4. RETRO : chaque manuscrit existant devient sa version 1 (fichiers + metadonnees actuels)
    op.execute("""
        INSERT INTO manuscript_versions
            (manuscript_id, version_number, pdf_filename, docx_filename, initial_docx_filename,
             title, abstract, keywords, created_at, archived_at)
        SELECT
            id, 1, pdf_filename, docx_filename, initial_docx_filename,
            title, abstract, keywords, COALESCE(created_at, now()), now()
        FROM manuscripts
    """)


def downgrade() -> None:
    op.drop_table('archived_annotations')
    op.drop_table('archived_evaluation_grids')
    op.drop_table('manuscript_versions')