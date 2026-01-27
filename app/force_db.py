import asyncio
import sys
import os

# Force le chemin racine
sys.path.append(os.getcwd())

from app.db import engine
from app.models.base import Base
# Import vital pour que SQLAlchemy 'voit' la table manquante
import app.models.editorial_version

async def run():
    print('🛠️  Forçage de la création des tables...')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('✅ Tables synchronisées !')

if __name__ == '__main__':
    asyncio.run(run())
