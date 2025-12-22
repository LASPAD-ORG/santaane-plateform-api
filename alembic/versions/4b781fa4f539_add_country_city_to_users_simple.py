"""add_country_city_to_users_simple

Revision ID: 4b781fa4f539
Revises: afc265a757a5
Create Date: 2025-12-22 02:20:46.952072

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '4b781fa4f539'
down_revision: Union[str, Sequence[str], None] = 'afc265a757a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add country_id and city_id columns to users table
    op.add_column('users', sa.Column('country_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('city_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_users_country_id', 'users', 'countries', ['country_id'], ['id'])
    op.create_foreign_key('fk_users_city_id', 'users', 'cities', ['city_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_users_city_id', 'users', type_='foreignkey')
    op.drop_constraint('fk_users_country_id', 'users', type_='foreignkey')
    op.drop_column('users', 'city_id')
    op.drop_column('users', 'country_id')
