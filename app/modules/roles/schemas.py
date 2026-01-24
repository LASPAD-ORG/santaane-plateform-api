"""
roles module - Pydantic schemas
All fields use camelCase for client communication
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RoleCreate(BaseModel):
    """Schema for creating a role"""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class RoleUpdate(BaseModel):
    """Schema for updating a role"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None


class RoleResponse(BaseModel):
    """Schema for role response"""
    id: int
    name: str
    description: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class UserRoleAssign(BaseModel):
    """Schema for assigning a role to a user"""
    userId: int = Field(..., gt=0)
    roleId: int = Field(..., gt=0)


class UserRoleResponse(BaseModel):
    """Schema for user role response"""
    id: int
    userId: int
    roleId: int
    roleName: str
    assignedBy: Optional[int] = None
    assignedAt: datetime

    class Config:
        from_attributes = True


class PaginatedRoleResponse(BaseModel):
    """Paginated role response"""
    items: list[RoleResponse]
    total: int
    skip: int
    limit: int
    hasMore: bool
