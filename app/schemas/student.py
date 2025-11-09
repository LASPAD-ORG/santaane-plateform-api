"""
Student Pydantic schemas
"""
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.schemas.base import BaseSchema, TimestampSchema, PaginatedResponse


class StudentCreate(BaseModel):
    """Schema for creating a student"""
    first_name: str
    last_name: str
    email: EmailStr
    age: Optional[int] = None


class StudentUpdate(BaseModel):
    """Schema for updating a student"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None


class StudentResponse(TimestampSchema):
    """Schema for student response"""
    id: int
    first_name: str
    last_name: str
    email: str
    age: Optional[int] = None


class PaginatedStudentResponse(PaginatedResponse[StudentResponse]):
    """Paginated student response"""
    pass
