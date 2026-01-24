"""
Auth module - API routes
Handles HTTP endpoints for authentication including OTP and Password Reset
"""
from fastapi import APIRouter, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

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
    """Register a new user and trigger initial OTP"""
    return await service.register_user(user_data)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)
):
    """Login a user and return a JWT token (Checks if is_active/OTP verified)"""
    credentials = UserLogin(email=form_data.username, password=form_data.password)
    return await service.login_user(credentials)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user_dep),
    service: AuthService = Depends(get_auth_service)
):
    """Get the currently authenticated user's details"""
    return await service.get_current_user(current_user.id)

# --- NOUVELLES ROUTES ESSENTIELLES POUR OTP ET RESET PASSWORD ---

@router.post("/verify-otp", status_code=200)
async def verify_otp(
    email: str = Body(..., embed=True),
    code: str = Body(..., embed=True),
    service: AuthService = Depends(get_auth_service)
):
    """Verify the 6-digit OTP code to activate account"""
    success = await service.verify_otp(email, code)
    return {"message": "Compte activé avec succès"}


@router.post("/resend-otp", status_code=200)
async def resend_otp(
    email: str = Body(..., embed=True),
    service: AuthService = Depends(get_auth_service)
):
    """Resend OTP code (Limited to 5 per day)"""
    message = await service.resend_otp(email)
    return {"message": message}


@router.post("/forgot-password", status_code=200)
async def forgot_password(
    email: str = Body(..., embed=True),
    service: AuthService = Depends(get_auth_service)
):
    """Request a password reset link (5-minute expiration)"""
    message = await service.request_password_reset(email)
    return {"message": message}


@router.post("/reset-password-confirm", status_code=200)
async def reset_password_confirm(
    token: str = Body(...),
    new_password: str = Body(...),
    service: AuthService = Depends(get_auth_service)
):
    """Reset password using the secure token from email"""
    await service.confirm_password_reset(token, new_password)
    return {"message": "Mot de passe modifié avec succès"}