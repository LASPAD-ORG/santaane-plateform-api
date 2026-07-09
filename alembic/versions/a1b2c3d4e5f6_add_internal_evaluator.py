"""add internal evaluator feature

Ajoute :
- manuscripts.is_internally_validated (bool, NOT NULL, default false, indexé)
- manuscripts.internally_validated_at (datetime, nullable)
- manuscripts.internally_validated_by_id (int, nullable, FK users.id)
- manuscript_evaluators.kind (varchar(20), NOT NULL, server_default 'external', indexé)
- table external_evaluator_proposals

Revision ID: a1b2c3d4e5f6
Revises: 48fdb46bd656
Create Date: 2026-07-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '48fdb46bd656'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # --- manuscripts : 3 nouvelles colonnes ---
    # server_default='false' => les manuscrits existants en prod restent non validés, sans casser NOT NULL
    op.add_column(
        'manuscripts',
        sa.Column(
            'is_internally_validated',
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.create_index(
        op.f('ix_manuscripts_is_internally_validated'),
        'manuscripts',
        ['is_internally_validated'],
        unique=False,
    )
    op.add_column(
        'manuscripts',
        sa.Column('internally_validated_at', sa.DateTime(), nullable=True),
    )
    op.add_column(
        'manuscripts',
        sa.Column('internally_validated_by_id', sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        'fk_manuscripts_internally_validated_by_id_users',
        'manuscripts',
        'users',
        ['internally_validated_by_id'],
        ['id'],
    )

    # --- manuscript_evaluators : colonne kind ---
    # server_default='external' => tous les liens existants deviennent 'external' (rétrocompat)
    op.add_column(
        'manuscript_evaluators',
        sa.Column(
            'kind',
            sa.String(length=20),
            nullable=False,
            server_default='external',
        ),
    )
    op.create_index(
        op.f('ix_manuscript_evaluators_kind'),
        'manuscript_evaluators',
        ['kind'],
        unique=False,
    )

    # --- external_evaluator_proposals : nouvelle table ---
    op.create_table(
        'external_evaluator_proposals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('manuscript_id', sa.Integer(), nullable=False),
        sa.Column('proposed_by_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='proposed', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['manuscript_id'], ['manuscripts.id']),
        sa.ForeignKeyConstraint(['proposed_by_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_external_evaluator_proposals_manuscript_id'),
        'external_evaluator_proposals',
        ['manuscript_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_external_evaluator_proposals_proposed_by_id'),
        'external_evaluator_proposals',
        ['proposed_by_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_external_evaluator_proposals_email'),
        'external_evaluator_proposals',
        ['email'],
        unique=False,
    )
    
    op.execute(
        """
        INSERT INTO roles (name, description, created_at, updated_at)
        VALUES ('INTERNAL_EVALUATOR', 'Évaluateur interne (pré-examen avant évaluation externe)', NOW(), NOW())
        ON CONFLICT (name) DO NOTHING
        """
    )


def downgrade() -> None:
    """Downgrade schema."""

    # --- external_evaluator_proposals ---
    op.drop_index(op.f('ix_external_evaluator_proposals_email'), table_name='external_evaluator_proposals')
    op.drop_index(op.f('ix_external_evaluator_proposals_proposed_by_id'), table_name='external_evaluator_proposals')
    op.drop_index(op.f('ix_external_evaluator_proposals_manuscript_id'), table_name='external_evaluator_proposals')
    op.drop_table('external_evaluator_proposals')

    # --- manuscript_evaluators.kind ---
    op.drop_index(op.f('ix_manuscript_evaluators_kind'), table_name='manuscript_evaluators')
    op.drop_column('manuscript_evaluators', 'kind')

    # --- manuscripts : colonnes internes ---
    op.drop_constraint('fk_manuscripts_internally_validated_by_id_users', 'manuscripts', type_='foreignkey')
    op.drop_column('manuscripts', 'internally_validated_by_id')
    op.drop_column('manuscripts', 'internally_validated_at')
    op.drop_index(op.f('ix_manuscripts_is_internally_validated'), table_name='manuscripts')
    op.drop_column('manuscripts', 'is_internally_validated')
    
    op.execute("DELETE FROM roles WHERE name = 'INTERNAL_EVALUATOR'")
