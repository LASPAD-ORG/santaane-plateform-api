"""
Students CRUD endpoints with pagination
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.models.student import Student
from app.models.user import User
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse, PaginatedStudentResponse
from app.core.security import get_current_user
from app.core.exceptions import NotFoundError, ConflictError
from app.core.logging import get_logger
from app.core.config import settings
from app.utils.pagination import paginate

logger = get_logger(__name__)
router = APIRouter(prefix="/students")


@router.get("", response_model=PaginatedStudentResponse)
async def list_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all students with pagination (protected route)"""
    logger.info(f"User {current_user.username} listing students (skip={skip}, limit={limit})")

    query = select(Student)
    result = await paginate(db, query, skip=skip, limit=limit)

    return result


@router.post("", response_model=StudentResponse, status_code=201)
async def create_student(
    student_data: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new student (protected route)"""
    logger.info(f"User {current_user.username} creating student: {student_data.email}")

    # Check if email already exists
    result = await db.execute(
        select(Student).where(Student.email == student_data.email)
    )
    existing_student = result.scalar_one_or_none()

    if existing_student:
        logger.warning(f"Student creation failed: email '{student_data.email}' already exists")
        raise ConflictError("Email already registered")

    # Create student
    new_student = Student(**student_data.model_dump())
    db.add(new_student)
    await db.commit()
    await db.refresh(new_student)

    logger.info(f"Student created: {new_student.id} - {new_student.email}")
    return new_student


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a student by ID (protected route)"""
    logger.info(f"User {current_user.username} fetching student ID: {student_id}")

    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar_one_or_none()

    if not student:
        logger.warning(f"Student not found: ID {student_id}")
        raise NotFoundError(f"Student with ID {student_id} not found")

    return student


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a student (protected route)"""
    logger.info(f"User {current_user.username} updating student ID: {student_id}")

    # Find student
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar_one_or_none()

    if not student:
        logger.warning(f"Student not found: ID {student_id}")
        raise NotFoundError(f"Student with ID {student_id} not found")

    # Update fields
    update_data = student_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)

    await db.commit()
    await db.refresh(student)

    logger.info(f"Student updated: {student.id}")
    return student


@router.delete("/{student_id}", status_code=204)
async def delete_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a student (protected route)"""
    logger.info(f"User {current_user.username} deleting student ID: {student_id}")

    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar_one_or_none()

    if not student:
        logger.warning(f"Student not found: ID {student_id}")
        raise NotFoundError(f"Student with ID {student_id} not found")

    await db.delete(student)
    await db.commit()

    logger.info(f"Student deleted: {student_id}")
    return None
