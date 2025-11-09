"""
Authentication endpoints (async refactored)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import AuthenticationError, ConflictError
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/auth")


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    logger.info(f"Registration attempt for username: {user_data.username}")

    # Check if user already exists
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        logger.warning(f"Registration failed: username '{user_data.username}' already exists")
        raise ConflictError("Username already registered")

    # Create new user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        hashed_password=hashed_password
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    logger.info(f"User registered successfully: {new_user.username}")
    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login user and return JWT token"""
    logger.info(f"Login attempt for username: {credentials.username}")

    # Find user
    result = await db.execute(
        select(User).where(User.username == credentials.username)
    )
    user = result.scalar_one_or_none()

    # Verify credentials
    if not user or not verify_password(credentials.password, user.hashed_password):
        logger.warning(f"Login failed for username: {credentials.username}")
        raise AuthenticationError("Invalid username or password")

    # Create access token
    access_token = create_access_token(data={"sub": user.username})

    logger.info(f"Login successful for username: {user.username}")
    return TokenResponse(access_token=access_token)
