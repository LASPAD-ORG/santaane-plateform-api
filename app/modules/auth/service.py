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
        """Register a new user (camelCase)"""
        logger.info(f"Registration attempt for email: {user_data.email}")

        if await self.repository.user_exists(user_data.email):
            logger.warning(f"Registration failed: email '{user_data.email}' already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=AuthErrorCode.EMAIL_ALREADY_EXISTS
            )

        # Validate country_id if provided
        country_name = None
        if user_data.countryId is not None:
            country = await self.repository.get_country_by_id(user_data.countryId)
            if not country:
                logger.warning(f"Registration failed: invalid country_id {user_data.countryId}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=AuthErrorCode.INVALID_COUNTRY_ID
                )
            country_name = country.name

        # Validate city_id if provided
        city_name = None
        if user_data.cityId is not None:
            city = await self.repository.get_city_by_id(user_data.cityId)
            if not city:
                logger.warning(f"Registration failed: invalid city_id {user_data.cityId}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=AuthErrorCode.INVALID_CITY_ID
                )
            city_name = city.name

        hashed_password = hash_password(user_data.password)
        user = await self.repository.create_user(
            email=user_data.email,
            full_name=user_data.fullName,
            hashed_password=hashed_password,
            country_id=user_data.countryId,
            city_id=user_data.cityId,
            timezone=user_data.timezone,
            profile_photo=user_data.profilePhoto,
            orcid_id=user_data.orcidId
        )

        logger.info(f"User registered successfully: {user.email}")

        # Extract country and city names from loaded relationships
        country_name = user.country.name if user.country else None
        city_name = user.city.name if user.city else None

        return UserResponse(
            id=user.id,
            email=user.email,
            fullName=user.full_name,
            countryName=country_name,
            cityName=city_name,
            timezone=user.timezone,
            profilePhoto=user.profile_photo,
            orcidId=user.orcid_id,
            createdAt=user.created_at,
            updatedAt=user.updated_at
        )

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
            accessToken=access_token,
            tokenType="bearer"
        )
