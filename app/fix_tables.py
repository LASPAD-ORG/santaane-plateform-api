import asyncio
from app.db import engine
from app.models.base import Base
# Importe explicitement tous les modèles pour qu'ils soient enregistrés
from app.models.user import User
from app.models.role import Role
from app.models.manuscript import Manuscript
from app.models.editorial_version import EditorialVersion
from app.models.user_role import UserRole

async def create_all_tables():
    print("Connecting to database...")
    try:
        async with engine.begin() as conn:
            print("Creating missing tables...")
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Success! All tables defined in models are now in the database.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(create_all_tables())