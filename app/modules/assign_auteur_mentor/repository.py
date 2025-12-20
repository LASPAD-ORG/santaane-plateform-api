"""
assign_auteur_mentor module - Database repository for Mentor Assignment
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, update
from typing import Optional, List

from app.core.logging import get_logger
from app.models.mentor_assignment import MentorAssignment
from app.models.user import User

logger = get_logger(__name__)


class MentorAssignmentRepository:
    """Repository for mentor assignment database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 20) -> dict:
        """Get all mentor assignments with pagination"""
        logger.debug(f"Fetching mentor assignments (skip={skip}, limit={limit})")
        
        # Get total count
        total_query = select(func.count()).select_from(MentorAssignment)
        total = await self.db.scalar(total_query)

        # Get paginated items
        query = (
            select(MentorAssignment)
            .order_by(MentorAssignment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        items = result.scalars().all()

        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }

    async def get_by_id(self, assignment_id: int) -> Optional[MentorAssignment]:
        """Get mentor assignment by ID"""
        logger.debug(f"Fetching mentor assignment ID: {assignment_id}")
        result = await self.db.execute(
            select(MentorAssignment).where(MentorAssignment.id == assignment_id)
        )
        return result.scalar_one_or_none()

    async def get_active_by_author(self, author_id: int) -> Optional[MentorAssignment]:
        """Get active mentor assignment for an author"""
        logger.debug(f"Fetching active mentor assignment for author ID: {author_id}")
        result = await self.db.execute(
            select(MentorAssignment).where(
                and_(
                    MentorAssignment.author_id == author_id,
                    MentorAssignment.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_author_and_mentor(
        self, author_id: int, mentor_id: int, exclude_id: Optional[int] = None
    ) -> Optional[MentorAssignment]:
        """Get assignment by author and mentor, optionally excluding an ID"""
        logger.debug(f"Checking assignment: author={author_id}, mentor={mentor_id}")
        query = select(MentorAssignment).where(
            and_(
                MentorAssignment.author_id == author_id,
                MentorAssignment.mentor_id == mentor_id
            )
        )
        
        if exclude_id:
            query = query.where(MentorAssignment.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def check_active_assignment_conflict(
        self, author_id: int, mentor_id: int, exclude_id: Optional[int] = None
    ) -> Optional[MentorAssignment]:
        """Check if author has active assignment with different mentor"""
        logger.debug(f"Checking active assignment conflict: author={author_id}, mentor={mentor_id}")
        query = select(MentorAssignment).where(
            and_(
                MentorAssignment.author_id == author_id,
                MentorAssignment.mentor_id != mentor_id,
                MentorAssignment.is_active == True
            )
        )
        
        if exclude_id:
            query = query.where(MentorAssignment.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_mentor_authors(
        self, mentor_id: int, skip: int = 0, limit: int = 20, active_only: bool = True
    ) -> dict:
        """Get all authors assigned to a mentor"""
        logger.debug(f"Fetching authors for mentor ID: {mentor_id}")
        
        # Build query
        base_query = select(MentorAssignment).where(
            MentorAssignment.mentor_id == mentor_id
        )
        
        if active_only:
            base_query = base_query.where(MentorAssignment.is_active == True)
        
        # Get total count
        total_query = select(func.count()).select_from(MentorAssignment).where(
            MentorAssignment.mentor_id == mentor_id
        )
        if active_only:
            total_query = total_query.where(MentorAssignment.is_active == True)
        
        total = await self.db.scalar(total_query)

        # Get paginated items
        query = base_query.order_by(MentorAssignment.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        items = result.scalars().all()

        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }

    async def create(self, assignment_data: dict) -> MentorAssignment:
        """Create a new mentor assignment"""
        logger.info(f"Creating mentor assignment: author_id={assignment_data.get('author_id')}, "
                   f"mentor_id={assignment_data.get('mentor_id')}")
        
        assignment = MentorAssignment(**assignment_data)
        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)
        
        logger.info(f"Mentor assignment created: ID {assignment.id}")
        return assignment

    async def update(self, assignment: MentorAssignment, update_data: dict) -> MentorAssignment:
        """Update an existing mentor assignment"""
        logger.info(f"Updating mentor assignment ID: {assignment.id}")
        
        for key, value in update_data.items():
            if value is not None:
                setattr(assignment, key, value)
        
        await self.db.commit()
        await self.db.refresh(assignment)
        
        logger.info(f"Mentor assignment updated: ID {assignment.id}")
        return assignment

    async def deactivate_previous_active(self, author_id: int) -> Optional[MentorAssignment]:
        """Deactivate previous active assignment for an author"""
        logger.info(f"Deactivating previous active assignment for author ID: {author_id}")
        
        previous = await self.get_active_by_author(author_id)
        if previous:
            previous.is_active = False
            await self.db.commit()
            await self.db.refresh(previous)
            logger.info(f"Previous assignment deactivated: ID {previous.id}")
            return previous
        
        return None

    async def delete(self, assignment: MentorAssignment) -> None:
        """Delete a mentor assignment"""
        logger.info(f"Deleting mentor assignment ID: {assignment.id}")
        
        await self.db.delete(assignment)
        await self.db.commit()
        
        logger.info(f"Mentor assignment deleted: ID {assignment.id}")
