"""
Auth module - Business logic service
Handles authentication business logic
"""
from fastapi import HTTPException, status

from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from app.modules.auth.error_codes import AuthErrorCode
from app.core.security import hash_password, verify_password, create_access_token
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    """Service for authentication business logic"""

    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """
        Register a new user

        Args:
            user_data: User registration data

        Returns:
            UserResponse: Created user data

        Raises:
            ConflictError: If username already exists
        """
        logger.info(f"Registration attempt for username: {user_data.username}")

        # Check if user already exists
        if await self.repository.user_exists(user_data.username):
            logger.warning(f"Registration failed: username '{user_data.username}' already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=AuthErrorCode.USERNAME_ALREADY_EXISTS
            )

        # Hash password and create user
        hashed_password = hash_password(user_data.password)
        user = await self.repository.create_user(user_data.username, hashed_password)

        logger.info(f"User registered successfully: {user.username}")
        return UserResponse(
            id=user.id,
            username=user.username,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    async def login_user(self, credentials: UserLogin) -> TokenResponse:
        """
        Authenticate user and return JWT token

        Args:
            credentials: User login credentials

        Returns:
            TokenResponse: JWT access token

        Raises:
            AuthenticationError: If credentials are invalid
        """
        logger.info(f"Login attempt for username: {credentials.username}")

        # Find user
        user = await self.repository.get_user_by_username(credentials.username)

        # Verify credentials
        if not user or not verify_password(credentials.password, user.hashed_password):
            logger.warning(f"Login failed for username: {credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AuthErrorCode.INVALID_CREDENTIALS
            )

        # Create access token
        access_token = create_access_token(data={"sub": user.username})

        logger.info(f"Login successful for username: {user.username}")
        return TokenResponse(access_token=access_token)
