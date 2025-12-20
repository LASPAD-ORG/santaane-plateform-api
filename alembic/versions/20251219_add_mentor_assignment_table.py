"""Add mentor assignment table

Revision ID: 20251219_add_mentor_assignment
Revises: d39bfc026878
Create Date: 2025-12-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import expression


# revision identifiers, used by Alembic.
revision = '20251219_add_mentor_assignment'
down_revision = '6499f3161f2c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create mentor_assignments table
    op.create_table(
        'mentor_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('mentor_id', sa.Integer(), nullable=False),
        sa.Column('assigned_by', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=expression.true(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['mentor_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_mentor_assignments_author_id', 'author_id'),
        sa.Index('ix_mentor_assignments_mentor_id', 'mentor_id'),
        sa.Index('ix_mentor_assignments_author_id_is_active', 'author_id', 'is_active'),
    )
    
    # Create unique index for active mentors per author (only one active mentor per author)
    op.create_index(
        'ix_mentor_assignments_author_active_unique',
        'mentor_assignments',
        ['author_id'],
        unique=True,
        postgresql_where=sa.text('is_active = true')
    )


def downgrade() -> None:
    op.drop_table('mentor_assignments')
