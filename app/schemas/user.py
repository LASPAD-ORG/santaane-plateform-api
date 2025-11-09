"""
User Pydantic schemas
"""
from pydantic import BaseModel, EmailStr
from app.schemas.base import BaseSchema, TimestampSchema


class UserCreate(BaseModel):
    """Schema for user registration"""
    username: str
    password: str


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str


class UserResponse(TimestampSchema):
    """Schema for user response (without password)"""
    id: int
    username: str


class TokenResponse(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
