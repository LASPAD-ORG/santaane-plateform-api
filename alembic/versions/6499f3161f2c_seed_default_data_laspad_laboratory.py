"""seed_default_data_laspad_laboratory

Revision ID: 6499f3161f2c
Revises: 14829c1bc116
Create Date: 2025-11-14 16:26:07.914905

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '6499f3161f2c'
down_revision: Union[str, Sequence[str], None] = '14829c1bc116'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed default data: LASPAD laboratory and default roles."""

    # Seed default roles (idempotent - insert only if not exists)
    op.execute("""
        INSERT INTO roles (name, description, created_at, updated_at)
        VALUES
            ('SUPER_ADMIN', 'System administrator with full access', NOW(), NOW()),
            ('EDITOR', 'Editorial role for managing manuscripts', NOW(), NOW()),
            ('EVALUATOR', 'Reviewer role for evaluating manuscripts', NOW(), NOW()),
            ('MENTOR', 'Mentor role for guiding authors', NOW(), NOW()),
            ('AUTHOR', 'Author role for submitting manuscripts', NOW(), NOW())
        ON CONFLICT (name) DO NOTHING;
    """)

    # Seed LASPAD laboratory (default laboratory)
    op.execute("""
        INSERT INTO laboratories (name, description, is_active, created_at, updated_at)
        VALUES (
            'LASPAD',
            'Laboratoire d''Analyse des Systèmes de Production Agricole Durable - Default editorial laboratory',
            true,
            NOW(),
            NOW()
        )
        ON CONFLICT (name) DO NOTHING;
    """)


def downgrade() -> None:
    """Remove seeded data."""

    # Remove LASPAD laboratory
    op.execute("DELETE FROM laboratories WHERE name = 'LASPAD';")

    # Note: We don't remove roles as they might be in use
    # If you really need to remove them, uncomment the following:
    # op.execute("DELETE FROM roles WHERE name IN ('SUPER_ADMIN', 'EDITOR', 'EVALUATOR', 'MENTOR', 'AUTHOR');")
