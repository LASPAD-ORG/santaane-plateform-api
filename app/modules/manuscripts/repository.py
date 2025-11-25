"""
Data access layer for manuscripts module.
Handles all database operations for manuscripts.
"""
from sqlalchemy import select, func, or_, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional, List, Tuple
from datetime import datetime
from app.models.manuscript import Manuscript
from app.models.manuscript_version import ManuscriptVersion
from app.models.manuscript_discussion import ManuscriptDiscussion
from app.models.manuscript_file import ManuscriptFile
from app.models.review_comment import ReviewComment
from app.models.review_response import ReviewResponse
from app.models.user import User
from app.models.category import Category
from app.models.enums import ManuscriptStatus, ManuscriptFileType
from app.core.logging import get_logger

logger = get_logger(__name__)


class ManuscriptRepository:
    """Repository for manuscript-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== Manuscript CRUD ====================

    async def get_by_id(self, manuscript_id: int) -> Optional[Manuscript]:
        """Get manuscript by ID with author and category."""
        result = await self.db.execute(
            select(Manuscript)
            .where(Manuscript.id == manuscript_id)
            .options(
                joinedload(Manuscript.author),
                joinedload(Manuscript.category)
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_author(
        self,
        author_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> Tuple[List[Manuscript], int]:
        """
        Get all manuscripts by author with pagination and optional status filter.

        Returns:
            Tuple of (manuscripts list, total count)
        """
        # Build base query
        query = (
            select(Manuscript)
            .where(Manuscript.author_id == author_id)
            .options(
                joinedload(Manuscript.author),
                joinedload(Manuscript.category)
            )
        )

        # Apply status filter
        if status:
            query = query.where(Manuscript.status == status)

        # Count total
        count_query = select(func.count()).select_from(Manuscript).where(Manuscript.author_id == author_id)
        if status:
            count_query = count_query.where(Manuscript.status == status)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Apply pagination and ordering
        query = query.order_by(desc(Manuscript.updated_at)).offset(skip).limit(limit)

        result = await self.db.execute(query)
        manuscripts = result.scalars().unique().all()

        return list(manuscripts), total

    async def create(self, manuscript_data: dict, author_id: int) -> Manuscript:
        """Create a new manuscript."""
        manuscript = Manuscript(
            **manuscript_data,
            author_id=author_id,
            status=ManuscriptStatus.DRAFT,
            version=1
        )
        self.db.add(manuscript)
        await self.db.commit()
        await self.db.refresh(manuscript)

        # Load relationships
        await self.db.refresh(manuscript, ["author", "category"])
        return manuscript

    async def update(self, manuscript_id: int, manuscript_data: dict) -> Optional[Manuscript]:
        """Update a manuscript."""
        result = await self.db.execute(
            select(Manuscript).where(Manuscript.id == manuscript_id)
        )
        manuscript = result.scalar_one_or_none()

        if not manuscript:
            return None

        for key, value in manuscript_data.items():
            if value is not None:
                setattr(manuscript, key, value)

        manuscript.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(manuscript, ["author", "category"])
        return manuscript

    async def delete(self, manuscript_id: int) -> bool:
        """Delete a manuscript (only if it's a draft)."""
        result = await self.db.execute(
            select(Manuscript).where(
                and_(
                    Manuscript.id == manuscript_id,
                    Manuscript.status == ManuscriptStatus.DRAFT
                )
            )
        )
        manuscript = result.scalar_one_or_none()

        if not manuscript:
            return False

        await self.db.delete(manuscript)
        await self.db.commit()
        return True

    async def submit_manuscript(self, manuscript_id: int) -> Optional[Manuscript]:
        """Submit a manuscript for review."""
        result = await self.db.execute(
            select(Manuscript).where(Manuscript.id == manuscript_id)
        )
        manuscript = result.scalar_one_or_none()

        if not manuscript:
            return None

        manuscript.status = ManuscriptStatus.SUBMITTED
        manuscript.submitted_at = datetime.utcnow()
        manuscript.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(manuscript)
        return manuscript

    # ==================== Manuscript Version ====================

    async def create_version(
        self,
        manuscript_id: int,
        version_data: dict,
        created_by: int,
        file_path: Optional[str] = None,
        file_size: Optional[int] = None
    ) -> ManuscriptVersion:
        """Create a new manuscript version."""
        # Get current max version number
        result = await self.db.execute(
            select(func.max(ManuscriptVersion.version_number))
            .where(ManuscriptVersion.manuscript_id == manuscript_id)
        )
        max_version = result.scalar_one_or_none() or 0

        # Create new version
        version = ManuscriptVersion(
            manuscript_id=manuscript_id,
            version_number=max_version + 1,
            created_by=created_by,
            **version_data
        )
        self.db.add(version)

        # Update manuscript version number
        manuscript_result = await self.db.execute(
            select(Manuscript).where(Manuscript.id == manuscript_id)
        )
        manuscript = manuscript_result.scalar_one_or_none()
        if manuscript:
            manuscript.version = max_version + 1
            manuscript.updated_at = datetime.utcnow()

        # Create file record if file was uploaded
        if file_path:
            manuscript_file = ManuscriptFile(
                manuscript_id=manuscript_id,
                file_path=file_path,
                file_name=file_path.split('/')[-1],
                file_type=ManuscriptFileType.PDF,
                file_size=file_size,
                uploaded_by=created_by,
                version=max_version + 1
            )
            self.db.add(manuscript_file)

        await self.db.commit()
        await self.db.refresh(version, ["creator"])
        return version

    async def get_versions(self, manuscript_id: int) -> List[ManuscriptVersion]:
        """Get all versions of a manuscript."""
        result = await self.db.execute(
            select(ManuscriptVersion)
            .where(ManuscriptVersion.manuscript_id == manuscript_id)
            .options(joinedload(ManuscriptVersion.creator))
            .order_by(desc(ManuscriptVersion.version_number))
        )
        return list(result.scalars().unique().all())

    async def get_manuscript_files(self, manuscript_id: int, version: Optional[int] = None) -> List[ManuscriptFile]:
        """Get manuscript files, optionally filtered by version."""
        query = (
            select(ManuscriptFile)
            .where(
                and_(
                    ManuscriptFile.manuscript_id == manuscript_id,
                    ManuscriptFile.is_active == True
                )
            )
        )

        if version is not None:
            query = query.where(ManuscriptFile.version == version)

        query = query.order_by(desc(ManuscriptFile.uploaded_at))

        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ==================== Timeline ====================

    async def get_timeline(self, manuscript_id: int) -> List[dict]:
        """Get manuscript timeline/history."""
        # This would typically query a dedicated timeline/audit table
        # For now, we'll construct from manuscript data
        result = await self.db.execute(
            select(Manuscript)
            .where(Manuscript.id == manuscript_id)
            .options(joinedload(Manuscript.author))
        )
        manuscript = result.scalar_one_or_none()

        if not manuscript:
            return []

        timeline = []

        # Created event
        timeline.append({
            "id": 1,
            "type": "status_change",
            "title": "Manuscrit créé",
            "description": "Brouillon initial créé",
            "date": manuscript.created_at,
            "status": "draft"
        })

        # Submitted event
        if manuscript.submitted_at:
            timeline.append({
                "id": 2,
                "type": "status_change",
                "title": "Manuscrit soumis",
                "description": "Le manuscrit a été soumis pour évaluation",
                "date": manuscript.submitted_at,
                "status": "submitted",
                "userId": manuscript.author_id,
                "userName": manuscript.author.full_name
            })

        return timeline

    # ==================== Discussions ====================

    async def create_discussion(
        self,
        manuscript_id: int,
        user_id: int,
        subject: Optional[str],
        message: str,
        parent_id: Optional[int] = None,
        is_internal: bool = False
    ) -> ManuscriptDiscussion:
        """Create a new discussion or reply."""
        discussion = ManuscriptDiscussion(
            manuscript_id=manuscript_id,
            user_id=user_id,
            parent_id=parent_id,
            subject=subject,
            message=message,
            is_internal=is_internal
        )
        self.db.add(discussion)
        await self.db.commit()
        await self.db.refresh(discussion, ["user"])
        return discussion

    async def get_discussions(self, manuscript_id: int) -> List[ManuscriptDiscussion]:
        """Get all discussions for a manuscript (only top-level, replies loaded separately)."""
        result = await self.db.execute(
            select(ManuscriptDiscussion)
            .where(
                and_(
                    ManuscriptDiscussion.manuscript_id == manuscript_id,
                    ManuscriptDiscussion.parent_id.is_(None)
                )
            )
            .options(
                joinedload(ManuscriptDiscussion.user),
                selectinload(ManuscriptDiscussion.replies).joinedload(ManuscriptDiscussion.user)
            )
            .order_by(desc(ManuscriptDiscussion.created_at))
        )
        return list(result.scalars().unique().all())

    async def get_discussion_by_id(self, discussion_id: int) -> Optional[ManuscriptDiscussion]:
        """Get a discussion by ID."""
        result = await self.db.execute(
            select(ManuscriptDiscussion)
            .where(ManuscriptDiscussion.id == discussion_id)
            .options(joinedload(ManuscriptDiscussion.user))
        )
        return result.scalar_one_or_none()

    # ==================== Review Comments ====================

    async def get_review_comments(self, manuscript_id: int) -> List[ReviewComment]:
        """Get all review comments for a manuscript."""
        # Get review responses for this manuscript first
        result = await self.db.execute(
            select(ReviewComment)
            .join(ReviewResponse, ReviewComment.review_response_id == ReviewResponse.id)
            .where(ReviewResponse.manuscript_id == manuscript_id)
            .options(
                joinedload(ReviewComment.user),
                joinedload(ReviewComment.review_response)
            )
            .order_by(desc(ReviewComment.created_at))
        )
        return list(result.scalars().unique().all())

    # ==================== Permissions ====================

    async def user_has_access_to_manuscript(self, manuscript_id: int, user_id: int) -> bool:
        """
        Check if user has access to a manuscript.
        Access is granted if user is:
        - The author
        - An assigned reviewer
        - An assigned editor
        """
        from app.models.review_assignment import ReviewAssignment
        from app.models.manuscript_editor import ManuscriptEditor

        # Check if user is the author
        result = await self.db.execute(
            select(Manuscript).where(
                and_(
                    Manuscript.id == manuscript_id,
                    Manuscript.author_id == user_id
                )
            )
        )
        if result.scalar_one_or_none():
            return True

        # Check if user is an assigned reviewer
        result = await self.db.execute(
            select(ReviewAssignment).where(
                and_(
                    ReviewAssignment.manuscript_id == manuscript_id,
                    ReviewAssignment.reviewer_id == user_id
                )
            )
        )
        if result.scalar_one_or_none():
            return True

        # Check if user is an assigned editor
        result = await self.db.execute(
            select(ManuscriptEditor).where(
                and_(
                    ManuscriptEditor.manuscript_id == manuscript_id,
                    ManuscriptEditor.editor_id == user_id
                )
            )
        )
        if result.scalar_one_or_none():
            return True

        return False

    # ==================== Categories ====================

    async def get_all_categories(self) -> List[Category]:
        """Get all active categories."""
        result = await self.db.execute(
            select(Category)
            .where(Category.is_active == True)
            .order_by(Category.name)
        )
        return list(result.scalars().all())

    async def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID."""
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()
