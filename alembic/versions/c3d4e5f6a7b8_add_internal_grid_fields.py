"""add internal grid fields (editorial_line_fit, global_opinion)

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-08-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'manuscript_evaluation_grids',
        sa.Column('editorial_line_fit', sa.Text(), nullable=True)
    )
    op.add_column(
        'manuscript_evaluation_grids',
        sa.Column('global_opinion', sa.Text(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('manuscript_evaluation_grids', 'global_opinion')
    op.drop_column('manuscript_evaluation_grids', 'editorial_line_fit')