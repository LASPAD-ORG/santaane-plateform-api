"""
Async database session management
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# Convert postgresql+psycopg2:// to postgresql+asyncpg://
async_database_url = settings.DATABASE_URL.replace(
    "postgresql+psycopg2://",
    "postgresql+asyncpg://"
).replace(
    "postgresql://",
    "postgresql+asyncpg://"
)

# Create async engine
engine = create_async_engine(
    async_database_url,
    echo=False,  # Set to True only for debugging
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db():
    """Dependency to get async database session"""
    async with AsyncSessionLocal() as session:
        yield session
