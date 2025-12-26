"""seed roles

Revision ID: 08184bf8474d
Revises: 275674b3b5ec
Create Date: 2025-12-26 22:33:36.303627

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = '08184bf8474d'
down_revision: Union[str, Sequence[str], None] = '275674b3b5ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed roles into the roles table."""
    roles_table = sa.table(
        "roles",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )

    now = datetime.utcnow()

    op.bulk_insert(
        roles_table,
        [
            {
                "id": 1,
                "name": "SUPER_ADMIN",
                "description": "Super administrateur avec tous les droits",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": 2,
                "name": "EDITOR",
                "description": "Éditeur de la plateforme",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": 3,
                "name": "EVALUATOR",
                "description": "Évaluateur de manuscrits",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": 4,
                "name": "AUTHOR",
                "description": "Auteur de manuscrits",
                "created_at": now,
                "updated_at": now,
            },
        ],
    )


def downgrade() -> None:
    """Remove seeded roles from the roles table."""
    op.execute(
        """
        DELETE FROM roles
        WHERE id IN (1, 2, 3, 4)
        """
    )
