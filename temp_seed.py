import asyncio
import bcrypt
import random
from datetime import datetime, timedelta
from sqlalchemy import text
from app.db import AsyncSessionLocal


async def seed():
    print("🌱 Début du seed de la base de données...")

    async with AsyncSessionLocal() as session:
        try:
            # 1. Créer les rôles
            print("📋 Création des rôles...")
            roles_data = [
                {"id": 1, "name": "SUPER_ADMIN", "description": "Super administrateur avec tous les droits"},
                {"id": 2, "name": "EDITOR", "description": "Éditeur de la plateforme"},
                {"id": 3, "name": "EVALUATOR", "description": "Évaluateur de manuscrits"},
                {"id": 4, "name": "AUTHOR", "description": "Auteur de manuscrits"},
            ]

            for role_data in roles_data:
                # Check if role already exists
                result = await session.execute(
                    text(f"SELECT id FROM roles WHERE id = {role_data['id']}")
                )
                if not result.scalar_one_or_none():
                    await session.execute(
                        text(f"""INSERT INTO roles (id, name, description, created_at, updated_at)
                        VALUES ({role_data['id']}, '{role_data['name']}', '{role_data['description']}', NOW(), NOW())""")
                    )
                    print(f"  ✅ Rôle créé: {role_data['name']}")
                else:
                    print(f"  ⏭️  Rôle existe déjà: {role_data['name']}")

            # 2. Créer le super admin
            print("\n👤 Création du super administrateur...")

            # Check if super admin already exists
            result = await session.execute(
                text("SELECT id FROM users WHERE email = 'santaane@gmail.com'")
            )
            existing_user = result.scalar_one_or_none()

            if not existing_user:
                # Hash the password using bcrypt
                password = "Santaane"
                salt = bcrypt.gensalt()
                password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

                # Generate OTP
                otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
                last_otp_sent_at = datetime.utcnow()

                # Create super admin user with OTP
                await session.execute(
                    text(f"""INSERT INTO users (
                        email, email_verified, password_hash, full_name,
                        profile_photo, orcid_id, is_active, bio, position, institution,
                        otp_code, otp_expires_at, otp_send_count, last_otp_sent_at,
                        created_at, updated_at
                    ) VALUES (
                        'santaane@gmail.com', true, '{password_hash}', 'Super Admin Santaane',
                        NULL, NULL, true, 'Administrateur principal de la plateforme Santaane',
                        'Super Administrateur', 'Santaane Platform',
                        '{otp_code}', '{otp_expires_at.isoformat()}', 1, '{last_otp_sent_at.isoformat()}',
                        NOW(), NOW()
                    ) RETURNING id""")
                )
                result = await session.execute(text("SELECT id FROM users WHERE email = 'santaane@gmail.com'"))
                user_id = result.scalar_one()

                # Assign SUPER_ADMIN role
                await session.execute(
                    text(f"""INSERT INTO user_roles (user_id, role_id, assigned_at, assigned_by)
                    VALUES ({user_id}, 1, NOW(), {user_id})""")
                )

                print("  ✅ Super admin créé:")
                print(f"     📧 Email: santaane@gmail.com")
                print(f"     🔑 Mot de passe: Santaane")
                print(f"     🔢 OTP: {otp_code}")
                print(f"     ⏰ OTP expire à: {otp_expires_at.strftime('%Y-%m-%d %H:%M:%S')} UTC")
                print(f"     👑 Rôle: SUPER_ADMIN")
            else:
                print("  ⏭️  Super admin existe déjà: santaane@gmail.com")

            await session.commit()

            print("\n✨ Seed terminé avec succès!")
            print("\n📝 Credentials par défaut:")
            print("   Email: santaane@gmail.com")
            print("   Password: Santaane")
            if not existing_user:
                print(f"   OTP Code: {otp_code}")
                print(f"   OTP valide jusqu'à: {otp_expires_at.strftime('%Y-%m-%d %H:%M:%S')} UTC")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ Erreur lors du seed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise


asyncio.run(seed())