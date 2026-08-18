"""add manuscript attachments and attachment requests

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-08-15 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Table attachment_requests (creee EN PREMIER car manuscript_attachments la reference)
    op.create_table(
        'attachment_requests',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('manuscript_id', sa.Integer(), sa.ForeignKey('manuscripts.id'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('requested_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('fulfilled_by_attachment_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('fulfilled_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_attachment_requests_manuscript_id', 'attachment_requests', ['manuscript_id'])
    op.create_index('ix_attachment_requests_requested_by_id', 'attachment_requests', ['requested_by_id'])
    op.create_index('ix_attachment_requests_status', 'attachment_requests', ['status'])

    # 2. Table manuscript_attachments
    op.create_table(
        'manuscript_attachments',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('manuscript_id', sa.Integer(), sa.ForeignKey('manuscripts.id'), nullable=False),
        sa.Column('filename', sa.String(length=500), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('content_type', sa.String(length=150), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('uploaded_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('uploaded_by_role', sa.String(length=20), nullable=False),
        sa.Column('visible_to_author', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('attachment_type', sa.String(length=30), nullable=False, server_default='author_upload'),
        sa.Column('request_id', sa.Integer(), sa.ForeignKey('attachment_requests.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_manuscript_attachments_manuscript_id', 'manuscript_attachments', ['manuscript_id'])
    op.create_index('ix_manuscript_attachments_uploaded_by_id', 'manuscript_attachments', ['uploaded_by_id'])
    op.create_index('ix_manuscript_attachments_visible_to_author', 'manuscript_attachments', ['visible_to_author'])
    op.create_index('ix_manuscript_attachments_attachment_type', 'manuscript_attachments', ['attachment_type'])
    op.create_index('ix_manuscript_attachments_request_id', 'manuscript_attachments', ['request_id'])


def downgrade() -> None:
    op.drop_table('manuscript_attachments')
    op.drop_table('attachment_requests')