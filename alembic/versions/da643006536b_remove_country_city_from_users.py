"""remove_country_city_from_users

Revision ID: da643006536b
Revises: 4b781fa4f539
Create Date: 2025-12-22 03:57:44.122035

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'da643006536b'
down_revision: Union[str, Sequence[str], None] = '4b781fa4f539'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop foreign key constraints first
    op.drop_constraint('fk_users_city_id', 'users', type_='foreignkey')
    op.drop_constraint('fk_users_country_id', 'users', type_='foreignkey')
    
    # Drop columns
    op.drop_column('users', 'city_id')
    op.drop_column('users', 'country_id')


def downgrade() -> None:
    """Downgrade schema."""
    # Re-add columns
    op.add_column('users', sa.Column('country_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('city_id', sa.Integer(), nullable=True))
    
    # Re-add foreign keys
    op.create_foreign_key('fk_users_country_id', 'users', 'countries', ['country_id'], ['id'])
    op.create_foreign_key('fk_users_city_id', 'users', 'cities', ['city_id'], ['id'])
