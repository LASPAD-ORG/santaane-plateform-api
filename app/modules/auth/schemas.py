"""
Auth module - Pydantic schemas
All fields use camelCase for client communication
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str
    fullName: str 
    countryId: Optional[int] = Field(None, gt=0)
    cityId: Optional[int] = Field(None, gt=0)
    profilePhoto: Optional[str] = None
    orcidId: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response (without password)"""
    id: int
    email: EmailStr
    fullName: str
    countryName: Optional[str] = None
    cityName: Optional[str] = None
    profilePhoto: Optional[str] = None
    orcidId: Optional[str] = None
    roles: list[str] = []
    createdAt: datetime
    updatedAt: datetime


class TokenResponse(BaseModel):
    """Schema for JWT token response - OAuth2 compatible"""
    access_token: str
    token_type: str = "bearer"
