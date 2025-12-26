"""seed roles and super admin

Revision ID: 845aa1813350
Revises: 08184bf8474d
Create Date: 2025-12-26 22:39:02.454146
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import bcrypt

# revision identifiers, used by Alembic.
revision: str = '845aa1813350'
down_revision: Union[str, Sequence[str], None] = '08184bf8474d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    connection = op.get_bind()

    # --- 1. Seed roles ---
    roles = [
        {"id": 1, "name": "SUPER_ADMIN", "description": "Super administrateur avec tous les droits"},
        {"id": 2, "name": "EDITOR", "description": "Éditeur de la plateforme"},
        {"id": 3, "name": "EVALUATOR", "description": "Évaluateur de manuscrits"},
        {"id": 4, "name": "AUTHOR", "description": "Auteur de manuscrits"},
    ]

    for role in roles:
        result = connection.execute(
            sa.text("SELECT id FROM roles WHERE id = :id"),
            {"id": role["id"]}
        ).fetchone()

        if not result:
            connection.execute(
                sa.text("""
                    INSERT INTO roles (id, name, description, created_at, updated_at)
                    VALUES (:id, :name, :description, NOW(), NOW())
                """),
                role
            )
            print(f"✅ Rôle créé: {role['name']}")
        else:
            print(f"⏭️ Rôle existe déjà: {role['name']}")

    # --- 2. Seed super admin ---
    admin_email = "santaane@gmail.com"
    admin_name = "Amoussa"
    admin_password = "santaane@gmail.com"

    result = connection.execute(
        sa.text("SELECT id FROM users WHERE email = :email"),
        {"email": admin_email}
    ).fetchone()

    if not result:
        hashed_pw = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Insérer l'utilisateur avec tous les champs obligatoires
        connection.execute(
            sa.text("""
                INSERT INTO users (
                    email, email_verified, password_hash, full_name, is_active,
                    created_at, updated_at, otp_send_count
                )
                VALUES (
                    :email, true, :password_hash, :full_name, true,
                    NOW(), NOW(), 0
                )
            """),
            {"email": admin_email, "password_hash": hashed_pw, "full_name": admin_name}
        )

        print(f"✅ Super admin créé: {admin_email} / Mot de passe: {admin_password}")
    else:
        print(f"⏭️ Super admin existe déjà: {admin_email}")

def downgrade() -> None:
    connection = op.get_bind()
    
    connection.execute(
        sa.text("DELETE FROM user_roles WHERE role_id = 1 AND user_id IN (SELECT id FROM users WHERE email = :email)"),
        {"email": "santaane@gmail.com"}
    )
    connection.execute(
        sa.text("DELETE FROM users WHERE email = :email"),
        {"email": "santaane@gmail.com"}
    )
    connection.execute(sa.text("DELETE FROM roles WHERE id IN (1,2,3,4)"))
