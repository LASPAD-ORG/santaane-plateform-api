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

    async def register_user(self, user_data: UserCreate) -> str:
        """Register a new user (camelCase)"""
        logger.info(f"Registration attempt for email: {user_data.email}")

        if await self.repository.user_exists(user_data.email):
            logger.warning(f"Registration failed: email '{user_data.email}' already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=AuthErrorCode.EMAIL_ALREADY_EXISTS
            )

        hashed_password = hash_password(user_data.password)
        user = await self.repository.create_user(
            email=user_data.email,
            full_name=user_data.fullName,
            hashed_password=hashed_password,
            profile_photo=user_data.profilePhoto,
            orcid_id=user_data.orcidId
        )

        logger.info(f"User registered successfully: {user.email}")
        await self.set_default_user_role(user.id)
        return "User created successfully"

    async def login_user(self, credentials: UserLogin) -> TokenResponse:
        """Authenticate user and return JWT token (camelCase)"""
        logger.info(f"Login attempt for email: {credentials.email}")

        user = await self.repository.get_user_by_email(credentials.email)

        if not user or not verify_password(credentials.password, user.password_hash):
            logger.warning(f"Login failed for email: {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AuthErrorCode.INVALID_CREDENTIALS
            )

        access_token = create_access_token(data={"sub": user.email})

        logger.info(f"Login successful for email: {user.email}")
        return TokenResponse(
            access_token=access_token,
            token_type="bearer"
        )

    async def set_default_user_role(self, user_id: int):
        """Assign default role to newly registered user"""
        logger.info(f"Assigning default role to user_id: {user_id}")

        default_role_id = 5 
        await self.repository.assign_default_role_to_user(user_id, default_role_id)

        logger.info(f"Default role assigned to user_id: {user_id}")
    async def get_current_user(self, user_id: int) -> UserResponse:
        """Get current authenticated user details (camelCase)"""
        logger.info(f"Fetching user details for user_id: {user_id}")

        user = await self.repository.get_user_by_id(user_id)

        if not user:
            logger.warning(f"User not found: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=AuthErrorCode.USER_NOT_FOUND
            )

        # Get user roles
        roles = await self.repository.get_user_roles(user_id)

        return UserResponse(
            id=user.id,
            email=user.email,
            fullName=user.full_name,
            profilePhoto=user.profile_photo,
            orcidId=user.orcid_id,
            bio=user.bio,
            position=user.position,
            institution=user.institution,
            roles=roles,
            createdAt=user.created_at,
            updatedAt=user.updated_at
        )
