"""add evaluations validated fields

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-08-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'manuscripts',
        sa.Column('evaluations_validated', sa.Boolean(), nullable=False, server_default=sa.false())
    )
    op.create_index(
        'ix_manuscripts_evaluations_validated', 'manuscripts', ['evaluations_validated']
    )
    op.add_column(
        'manuscripts',
        sa.Column('evaluations_validated_at', sa.DateTime(), nullable=True)
    )
    op.add_column(
        'manuscripts',
        sa.Column('evaluations_validated_by_id', sa.Integer(), nullable=True)
    )
    op.add_column(
        'manuscripts',
        sa.Column('evaluations_editor_message', sa.Text(), nullable=True)
    )
    op.create_foreign_key(
        'fk_manuscripts_evaluations_validated_by_id_users',
        'manuscripts', 'users',
        ['evaluations_validated_by_id'], ['id']
    )


def downgrade() -> None:
    op.drop_constraint(
        'fk_manuscripts_evaluations_validated_by_id_users', 'manuscripts', type_='foreignkey'
    )
    op.drop_index('ix_manuscripts_evaluations_validated', table_name='manuscripts')
    op.drop_column('manuscripts', 'evaluations_editor_message')
    op.drop_column('manuscripts', 'evaluations_validated_by_id')
    op.drop_column('manuscripts', 'evaluations_validated_at')
    op.drop_column('manuscripts', 'evaluations_validated')