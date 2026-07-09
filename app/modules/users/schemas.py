"""
Pydantic schemas for users module.
All API request/response schemas use camelCase for field names.
"""
from pydantic import Field, EmailStr, ConfigDict, field_validator
from typing import Optional, List, Annotated
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
    role_ids: Optional[List[int]] = Field(default=[], alias="roleIds", description="List of role IDs to assign to the user")
    role_id: Optional[int] = Field(default=None, alias="roleId", description="Single role ID to assign to the user (backward compatibility)")


class EvaluatorCreate(BaseSchema):
    """Schema for creating an evaluator (by editor)."""
    email: EmailStr = Field(..., description="Evaluator email address")
    full_name: str = Field(..., min_length=1, max_length=150, description="Evaluator full name", alias="fullName")
    orcid_id: Optional[str] = Field(None, max_length=50, description="ORCID identifier", alias="orcidId")
    bio: Optional[str] = Field(None, description="Evaluator biography")
    position: Optional[str] = Field(None, max_length=150, description="Current position")
    institution: Optional[str] = Field(None, max_length=255, description="Institution name")


class UserRoleUpdate(BaseSchema):
    """Schema for updating user roles."""
    role_ids: List[int] = Field(..., min_items=1, description="List of role IDs to assign to the user", alias="roleIds")


class UserUpdate(BaseSchema):
    """Schema for updating an existing user."""
    email: Optional[EmailStr] = Field(None, description="Updated email address")
    full_name: Optional[str] = Field(None, min_length=1, max_length=150, description="Updated full name", alias="fullName")
    profile_photo: Optional[str] = Field(None, max_length=255, description="Profile photo URL", alias="profilePhoto")
    orcid_id: Optional[str] = Field(None, max_length=50, description="Updated ORCID identifier", alias="orcidId")
    bio: Optional[str] = Field(None, max_length=1000, description="Updated biography")
    position: Optional[str] = Field(None, max_length=200, description="Updated position")
    institution: Optional[str] = Field(None, max_length=300, description="Updated institution")
    role_ids: Optional[List[int]] = Field(default=None, alias="roleIds", description="List of role IDs to assign to the user")


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


class AdminPasswordReset(BaseSchema):
    """Schema for admin to reset user password."""
    new_password: Annotated[str, Field(min_length=8, max_length=100, description="New password", alias="newPassword")]


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
    bio: Optional[str] = Field(default=None, description="User biography")
    position: Optional[str] = Field(default=None, description="Current position")
    institution: Optional[str] = Field(default=None, description="Institution name")

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
    
    
class EvaluatorCreate(BaseSchema):
    """Schema for creating an evaluator (by editor)."""
    email: EmailStr = Field(..., description="Evaluator email address")
    full_name: str = Field(..., min_length=1, max_length=150, description="Evaluator full name", alias="fullName")
    orcid_id: Optional[str] = Field(None, max_length=50, description="ORCID identifier", alias="orcidId")
    bio: Optional[str] = Field(None, description="Evaluator biography")
    position: Optional[str] = Field(None, max_length=150, description="Current position")
    institution: Optional[str] = Field(None, max_length=255, description="Institution name")
    evaluator_type: str = Field(                       # ← nouveau
        default="external",
        alias="evaluatorType",
        description="Type d'évaluateur : 'external' (défaut) ou 'internal'",
    )
