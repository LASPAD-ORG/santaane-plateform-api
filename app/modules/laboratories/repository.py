"""
Data access layer for laboratories module.
Handles all database operations for laboratories and editor assignments.
"""
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List
from app.models.laboratory import Laboratory
from app.models.editor_assignment import EditorAssignment
from app.models.user import User
from app.models.user_role import UserRole
from app.models.role import Role
from app.core.logging import logger
from app.modules.laboratories.schemas import (
    LaboratoryCreate,
    LaboratoryUpdate,
    EditorAssignmentCreate
)


class LaboratoryRepository:
    """Repository for laboratory-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, laboratory_id: int) -> Optional[Laboratory]:
        """Get laboratory by ID."""
        result = await self.db.execute(
            select(Laboratory).where(Laboratory.id == laboratory_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Laboratory]:
        """Get laboratory by name."""
        result = await self.db.execute(
            select(Laboratory).where(Laboratory.name == name)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        is_active: Optional[bool] = None
    ) -> tuple[List[Laboratory], int]:
        """
        Get all laboratories with pagination and filtering.

        Returns:
            Tuple of (laboratories list, total count)
        """
        # Build query
        query = select(Laboratory)

        if is_active is not None:
            query = query.where(Laboratory.is_active == is_active)

        # Get total count
        count_query = select(func.count()).select_from(Laboratory)
        if is_active is not None:
            count_query = count_query.where(Laboratory.is_active == is_active)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(Laboratory.name)
        result = await self.db.execute(query)
        laboratories = result.scalars().all()

        return list(laboratories), total

    async def create(self, data: LaboratoryCreate, created_by: Optional[int] = None) -> Laboratory:
        """Create a new laboratory."""
        laboratory = Laboratory(
            name=data.name,
            description=data.description,
            is_active=data.is_active
        )

        self.db.add(laboratory)
        await self.db.commit()
        await self.db.refresh(laboratory)

        logger.info(f"Laboratory created: {laboratory.name} (ID: {laboratory.id})")
        return laboratory

    async def update(
        self,
        laboratory_id: int,
        data: LaboratoryUpdate
    ) -> Optional[Laboratory]:
        """Update an existing laboratory."""
        laboratory = await self.get_by_id(laboratory_id)
        if not laboratory:
            return None

        # Update fields if provided
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(laboratory, field, value)

        await self.db.commit()
        await self.db.refresh(laboratory)

        logger.info(f"Laboratory updated: {laboratory.name} (ID: {laboratory.id})")
        return laboratory

    async def delete(self, laboratory_id: int) -> bool:
        """Soft delete a laboratory (set is_active to False)."""
        laboratory = await self.get_by_id(laboratory_id)
        if not laboratory:
            return False

        laboratory.is_active = False
        await self.db.commit()

        logger.info(f"Laboratory soft deleted: {laboratory.name} (ID: {laboratory.id})")
        return True

    # Editor Assignment Methods

    async def get_laboratory_with_editors(self, laboratory_id: int) -> Optional[Laboratory]:
        """Get laboratory with all editor assignments."""
        result = await self.db.execute(
            select(Laboratory)
            .where(Laboratory.id == laboratory_id)
            .options(
                selectinload(Laboratory.editor_assignments).selectinload(EditorAssignment.user)
            )
        )
        return result.scalar_one_or_none()

    async def assign_editor(
        self,
        laboratory_id: int,
        data: EditorAssignmentCreate,
        assigned_by: int
    ) -> Optional[EditorAssignment]:
        """Assign an editor to a laboratory."""
        # Check if assignment already exists and is active
        existing = await self.db.execute(
            select(EditorAssignment).where(
                and_(
                    EditorAssignment.laboratory_id == laboratory_id,
                    EditorAssignment.user_id == data.user_id,
                    EditorAssignment.is_active == True
                )
            )
        )
        existing_assignment = existing.scalar_one_or_none()

        if existing_assignment:
            # Update existing assignment
            existing_assignment.role = data.role
            await self.db.commit()
            await self.db.refresh(existing_assignment)
            logger.info(f"Editor assignment updated: User {data.user_id} -> Lab {laboratory_id}")
            return existing_assignment

        # Create new assignment
        assignment = EditorAssignment(
            user_id=data.user_id,
            laboratory_id=laboratory_id,
            role=data.role,
            assigned_by=assigned_by,
            is_active=True
        )

        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)

        logger.info(f"Editor assigned: User {data.user_id} -> Lab {laboratory_id} as {data.role}")
        return assignment

    async def unassign_editor(self, laboratory_id: int, user_id: int) -> bool:
        """Remove an editor from a laboratory (soft delete)."""
        result = await self.db.execute(
            select(EditorAssignment).where(
                and_(
                    EditorAssignment.laboratory_id == laboratory_id,
                    EditorAssignment.user_id == user_id,
                    EditorAssignment.is_active == True
                )
            )
        )
        assignment = result.scalar_one_or_none()

        if not assignment:
            return False

        assignment.is_active = False
        await self.db.commit()

        logger.info(f"Editor unassigned: User {user_id} from Lab {laboratory_id}")
        return True

    async def get_laboratory_editors(self, laboratory_id: int) -> List[EditorAssignment]:
        """Get all active editors for a laboratory."""
        result = await self.db.execute(
            select(EditorAssignment)
            .where(
                and_(
                    EditorAssignment.laboratory_id == laboratory_id,
                    EditorAssignment.is_active == True
                )
            )
            .options(selectinload(EditorAssignment.user))
            .order_by(EditorAssignment.assigned_at.desc())
        )
        return list(result.scalars().all())

    async def get_available_editors(self, laboratory_id: Optional[int] = None) -> List[User]:
        """
        Get users with EDITOR role that are available for assignment.
        If laboratory_id is provided, exclude editors already assigned to that lab.
        """
        # Subquery for users with EDITOR role
        editor_role_subquery = (
            select(UserRole.user_id)
            .join(Role, UserRole.role_id == Role.id)
            .where(Role.name == "EDITOR")
        )

        # Base query: active users with EDITOR role
        query = select(User).where(
            and_(
                User.id.in_(editor_role_subquery),
                User.is_active == True
            )
        )

        # If laboratory_id provided, exclude already assigned editors
        if laboratory_id:
            assigned_editor_ids_subquery = (
                select(EditorAssignment.user_id)
                .where(
                    and_(
                        EditorAssignment.laboratory_id == laboratory_id,
                        EditorAssignment.is_active == True
                    )
                )
            )
            query = query.where(User.id.not_in(assigned_editor_ids_subquery))

        result = await self.db.execute(query.order_by(User.full_name))
        return list(result.scalars().all())

    async def get_laspad_lab_id(self) -> Optional[int]:
        """Get the ID of the LASPAD laboratory (default laboratory)."""
        result = await self.db.execute(
            select(Laboratory.id).where(Laboratory.name == "LASPAD")
        )
        return result.scalar_one_or_none()


# Fix missing import
from sqlalchemy import func
