"""
Pydantic schemas for users module.
All API request/response schemas use camelCase for field names.
"""
from pydantic import Field, EmailStr, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from app.schemas.base import BaseSchema, TimestampSchema


# User Base Schemas

class UserBase(BaseSchema):
    """Base user schema with common fields."""
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., min_length=1, max_length=150, description="User full name", alias="fullName")
    orcid_id: Optional[str] = Field(None, max_length=50, description="ORCID identifier", alias="orcidId")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100, description="User password")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseSchema):
    """Schema for updating an existing user."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=150, alias="fullName")
    profile_photo: Optional[str] = Field(None, max_length=255, alias="profilePhoto")
    orcid_id: Optional[str] = Field(None, max_length=50, alias="orcidId")


class ProfileUpdate(BaseSchema):
    """Schema for updating own profile (users cannot change their own email)."""
    full_name: str | None = Field(default=None, min_length=1, max_length=150, alias="fullName")
    profile_photo: str | None = Field(default=None, max_length=255, alias="profilePhoto")
    orcid_id: str | None = Field(default=None, max_length=50, alias="orcidId")
    bio: str | None = Field(default=None, description="User biography")
    position: str | None = Field(default=None, max_length=150, description="Current position")
    institution: str | None = Field(default=None, max_length=255, description="Institution name")


class PasswordChange(BaseSchema):
    """Schema for changing user password."""
    current_password: str = Field(..., description="Current password", alias="currentPassword")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password", alias="newPassword")

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserActivation(BaseSchema):
    """Schema for activating/deactivating user."""
    is_active: bool = Field(..., description="Active status", alias="isActive")


# Response Schemas

class RoleInfo(BaseSchema):
    """Basic role information."""
    id: int
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase, TimestampSchema):
    """Schema for user response."""
    id: int
    email_verified: bool = Field(..., alias="emailVerified")
    is_active: bool = Field(..., alias="isActive")
    profile_photo: Optional[str] = Field(None, alias="profilePhoto")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UserWithRolesResponse(UserResponse):
    """User response with associated roles."""
    roles: List[RoleInfo] = Field(default_factory=list, description="User roles")


class UserDetailResponse(UserWithRolesResponse):
    """Detailed user response with all relationships."""
    # Add more fields as needed for detailed view
    pass


# Filter Schemas

class UserFilters(BaseSchema):
    """Filters for user list queries."""
    email: Optional[str] = Field(None, description="Filter by email (partial match)")
    full_name: Optional[str] = Field(None, description="Filter by name (partial match)", alias="fullName")
    role: Optional[str] = Field(None, description="Filter by role name")
    is_active: Optional[bool] = Field(None, description="Filter by active status", alias="isActive")
