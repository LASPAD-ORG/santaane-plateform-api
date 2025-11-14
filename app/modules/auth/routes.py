"""
Auth module - API routes
Handles HTTP endpoints for authentication
"""
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.modules.auth.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from app.modules.auth.service import AuthService
from app.modules.auth.utils import get_auth_service
from app.core.security import get_current_user as get_current_user_dep
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=str, status_code=201)
async def register(
    user_data: UserCreate,
    service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user
    Returns a success message
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

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user_dep),
    service: AuthService = Depends(get_auth_service)
):
    """
    Get the currently authenticated user's details
    Requires valid JWT token in Authorization header
    """
    return await service.get_current_user(current_user.id) 
