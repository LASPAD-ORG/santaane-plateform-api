"""
Auth module - API routes
Handles HTTP endpoints for authentication
"""
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.modules.auth.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from app.modules.auth.service import AuthService
from app.modules.auth.utils import get_auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user_data: UserCreate,
    service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user

    """
    return await service.register_user(user_data)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)
):
    """
    Login a user and return a JWT token (OAuth2 compatible for Swagger UI)

    """
    # Convert OAuth2PasswordRequestForm to UserLogin schema
    credentials = UserLogin(email=form_data.username, password=form_data.password)
    return await service.login_user(credentials)
