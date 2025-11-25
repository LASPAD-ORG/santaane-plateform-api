"""
Business logic service for manuscripts module.
"""
from fastapi import HTTPException, status, UploadFile
from typing import Optional, List
from datetime import datetime
import os

from app.modules.manuscripts.repository import ManuscriptRepository
from app.modules.manuscripts.schemas import (
    ManuscriptCreate,
    ManuscriptUpdate,
    ManuscriptResponse,
    PaginatedManuscriptResponse,
    ManuscriptVersionCreate,
    ManuscriptVersionResponse,
    TimelineEvent,
    DiscussionCreate,
    DiscussionReplyCreate,
    DiscussionResponse,
    ReviewCommentResponse,
    SubmitManuscriptResponse,
    DeleteManuscriptResponse
)
from app.modules.manuscripts.error_codes import ManuscriptErrorCode
from app.core.logging import get_logger

logger = get_logger(__name__)


class ManuscriptService:
    """Service for manuscript business logic"""

    def __init__(self, repository: ManuscriptRepository):
        self.repository = repository

    # ==================== Manuscript CRUD ====================

    async def get_manuscripts(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> PaginatedManuscriptResponse:
        """Get all manuscripts for a user with pagination"""
        logger.info(f"Fetching manuscripts for user {user_id} (skip={skip}, limit={limit}, status={status})")

        manuscripts, total = await self.repository.get_all_by_author(
            author_id=user_id,
            skip=skip,
            limit=limit,
            status=status
        )

        # Transform to response format
        data = []
        for manuscript in manuscripts:
            # Get cover image from files
            files = await self.repository.get_manuscript_files(manuscript.id)
            cover_image = None
            for file in files:
                if "cover" in file.file_name.lower():
                    cover_image = f"/uploads/{file.file_path}"
                    break

            data.append(ManuscriptResponse(
                id=manuscript.id,
                title=manuscript.title,
                abstract=manuscript.abstract,
                keywords=manuscript.keywords,
                authorId=manuscript.author_id,
                authorName=manuscript.author.full_name,
                categoryId=manuscript.category_id,
                categoryName=manuscript.category.name if manuscript.category else None,
                status=manuscript.status,
                submittedAt=manuscript.submitted_at,
                version=manuscript.version,
                isArchived=manuscript.is_archived,
                coverImage=cover_image,
                createdAt=manuscript.created_at,
                updatedAt=manuscript.updated_at
            ))

        pagination = {
            "total": total,
            "page": (skip // limit) + 1,
            "limit": limit,
            "totalPages": (total + limit - 1) // limit
        }

        return PaginatedManuscriptResponse(data=data, pagination=pagination)

    async def get_manuscript_by_id(self, manuscript_id: int, user_id: int) -> ManuscriptResponse:
        """Get manuscript by ID"""
        logger.info(f"Fetching manuscript ID: {manuscript_id}")

        manuscript = await self.repository.get_by_id(manuscript_id)
        if not manuscript:
            logger.warning(f"Manuscript not found: ID {manuscript_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ManuscriptErrorCode.MANUSCRIPT_NOT_FOUND
            )

        # Check ownership (or permissions for reviewers/editors)
        if manuscript.author_id != user_id:
            # TODO: Add permission check for reviewers/editors
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this manuscript"
            )

        # Get cover image
        files = await self.repository.get_manuscript_files(manuscript.id)
        cover_image = None
        for file in files:
            if "cover" in file.file_name.lower():
                cover_image = f"/uploads/{file.file_path}"
                break

        return ManuscriptResponse(
            id=manuscript.id,
            title=manuscript.title,
            abstract=manuscript.abstract,
            keywords=manuscript.keywords,
            authorId=manuscript.author_id,
            authorName=manuscript.author.full_name,
            categoryId=manuscript.category_id,
            categoryName=manuscript.category.name if manuscript.category else None,
            status=manuscript.status,
            submittedAt=manuscript.submitted_at,
            version=manuscript.version,
            isArchived=manuscript.is_archived,
            coverImage=cover_image,
            createdAt=manuscript.created_at,
            updatedAt=manuscript.updated_at
        )

    async def create_manuscript(
        self,
        manuscript_data: ManuscriptCreate,
        user_id: int,
        cover_image: Optional[UploadFile] = None,
        manuscript_file: Optional[UploadFile] = None
    ) -> ManuscriptResponse:
        """Create a new manuscript"""
        logger.info(f"Creating manuscript for user {user_id}")

        # Validate category exists
        category = await self.repository.get_category_by_id(manuscript_data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )

        # Create manuscript
        manuscript = await self.repository.create(
            manuscript_data.model_dump(by_alias=False),
            author_id=user_id
        )

        # Handle file uploads
        cover_image_path = None
        if cover_image:
            cover_image_path = await self._save_upload_file(
                cover_image,
                manuscript.id,
                "cover"
            )

        if manuscript_file:
            file_path = await self._save_upload_file(
                manuscript_file,
                manuscript.id,
                "manuscript"
            )
            # Create initial version
            await self.repository.create_version(
                manuscript_id=manuscript.id,
                version_data={
                    "title": manuscript.title,
                    "abstract": manuscript.abstract,
                    "keywords": manuscript.keywords,
                    "changes_summary": "Version initiale soumise"
                },
                created_by=user_id,
                file_path=file_path,
                file_size=manuscript_file.size
            )

        logger.info(f"Manuscript created: {manuscript.id}")

        return ManuscriptResponse(
            id=manuscript.id,
            title=manuscript.title,
            abstract=manuscript.abstract,
            keywords=manuscript.keywords,
            authorId=manuscript.author_id,
            authorName=manuscript.author.full_name,
            categoryId=manuscript.category_id,
            categoryName=manuscript.category.name if manuscript.category else None,
            status=manuscript.status,
            submittedAt=manuscript.submitted_at,
            version=manuscript.version,
            isArchived=manuscript.is_archived,
            coverImage=cover_image_path,
            createdAt=manuscript.created_at,
            updatedAt=manuscript.updated_at
        )

    async def update_manuscript(
        self,
        manuscript_id: int,
        manuscript_data: ManuscriptUpdate,
        user_id: int
    ) -> ManuscriptResponse:
        """Update a manuscript"""
        logger.info(f"Updating manuscript ID: {manuscript_id}")

        # Check manuscript exists and user owns it
        manuscript = await self.repository.get_by_id(manuscript_id)
        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ManuscriptErrorCode.MANUSCRIPT_NOT_FOUND
            )

        if manuscript.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this manuscript"
            )

        # Only drafts can be updated
        if manuscript.status != "draft":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft manuscripts can be updated"
            )

        # Update manuscript
        updated_manuscript = await self.repository.update(
            manuscript_id,
            manuscript_data.model_dump(by_alias=False, exclude_unset=True)
        )

        # Get cover image
        files = await self.repository.get_manuscript_files(manuscript_id)
        cover_image = None
        for file in files:
            if "cover" in file.file_name.lower():
                cover_image = f"/uploads/{file.file_path}"
                break

        return ManuscriptResponse(
            id=updated_manuscript.id,
            title=updated_manuscript.title,
            abstract=updated_manuscript.abstract,
            keywords=updated_manuscript.keywords,
            authorId=updated_manuscript.author_id,
            authorName=updated_manuscript.author.full_name,
            categoryId=updated_manuscript.category_id,
            categoryName=updated_manuscript.category.name if updated_manuscript.category else None,
            status=updated_manuscript.status,
            submittedAt=updated_manuscript.submitted_at,
            version=updated_manuscript.version,
            isArchived=updated_manuscript.is_archived,
            coverImage=cover_image,
            createdAt=updated_manuscript.created_at,
            updatedAt=updated_manuscript.updated_at
        )

    async def delete_manuscript(self, manuscript_id: int, user_id: int) -> DeleteManuscriptResponse:
        """Delete a manuscript (only drafts)"""
        logger.info(f"Deleting manuscript ID: {manuscript_id}")

        # Check manuscript exists and user owns it
        manuscript = await self.repository.get_by_id(manuscript_id)
        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ManuscriptErrorCode.MANUSCRIPT_NOT_FOUND
            )

        if manuscript.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this manuscript"
            )

        # Delete
        success = await self.repository.delete(manuscript_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only draft manuscripts can be deleted"
            )

        return DeleteManuscriptResponse(message="Manuscrit supprimé avec succès")

    async def submit_manuscript(self, manuscript_id: int, user_id: int) -> SubmitManuscriptResponse:
        """Submit a manuscript for review"""
        logger.info(f"Submitting manuscript ID: {manuscript_id}")

        # Check manuscript exists and user owns it
        manuscript = await self.repository.get_by_id(manuscript_id)
        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ManuscriptErrorCode.MANUSCRIPT_NOT_FOUND
            )

        if manuscript.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to submit this manuscript"
            )

        # Submit
        submitted_manuscript = await self.repository.submit_manuscript(manuscript_id)

        return SubmitManuscriptResponse(
            id=submitted_manuscript.id,
            status=submitted_manuscript.status,
            submittedAt=submitted_manuscript.submitted_at,
            message="Manuscrit soumis avec succès pour évaluation"
        )

    # ==================== Manuscript Versions ====================

    async def upload_new_version(
        self,
        manuscript_id: int,
        version_data: ManuscriptVersionCreate,
        user_id: int,
        manuscript_file: UploadFile
    ) -> ManuscriptVersionResponse:
        """Upload a new version of a manuscript"""
        logger.info(f"Uploading new version for manuscript ID: {manuscript_id}")

        # Check manuscript exists and user owns it
        manuscript = await self.repository.get_by_id(manuscript_id)
        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ManuscriptErrorCode.MANUSCRIPT_NOT_FOUND
            )

        if manuscript.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to upload version for this manuscript"
            )

        # Save file
        file_path = await self._save_upload_file(manuscript_file, manuscript_id, "version")

        # Create version
        version = await self.repository.create_version(
            manuscript_id=manuscript_id,
            version_data=version_data.model_dump(by_alias=False),
            created_by=user_id,
            file_path=file_path,
            file_size=manuscript_file.size
        )

        return ManuscriptVersionResponse(
            id=version.id,
            manuscriptId=version.manuscript_id,
            versionNumber=version.version_number,
            title=version.title,
            abstract=version.abstract,
            keywords=version.keywords,
            changesSummary=version.changes_summary,
            createdBy=version.created_by,
            createdByName=version.creator.full_name,
            createdAt=version.created_at,
            fileUrl=f"/uploads/{file_path}",
            fileSize=manuscript_file.size
        )

    async def get_manuscript_versions(self, manuscript_id: int, user_id: int) -> List[ManuscriptVersionResponse]:
        """Get all versions of a manuscript"""
        logger.info(f"Fetching versions for manuscript ID: {manuscript_id}")

        # Check access
        manuscript = await self.repository.get_by_id(manuscript_id)
        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ManuscriptErrorCode.MANUSCRIPT_NOT_FOUND
            )

        versions = await self.repository.get_versions(manuscript_id)
        files = await self.repository.get_manuscript_files(manuscript_id)

        # Map files to versions
        version_responses = []
        for version in versions:
            file_url = None
            file_size = None

            for file in files:
                if file.version == version.version_number:
                    file_url = f"/uploads/{file.file_path}"
                    file_size = file.file_size
                    break

            version_responses.append(ManuscriptVersionResponse(
                id=version.id,
                manuscriptId=version.manuscript_id,
                versionNumber=version.version_number,
                title=version.title,
                abstract=version.abstract,
                keywords=version.keywords,
                changesSummary=version.changes_summary,
                createdBy=version.created_by,
                createdByName=version.creator.full_name,
                createdAt=version.created_at,
                fileUrl=file_url,
                fileSize=file_size
            ))

        return version_responses

    # ==================== Timeline ====================

    async def get_manuscript_timeline(self, manuscript_id: int, user_id: int) -> List[TimelineEvent]:
        """Get manuscript timeline/history"""
        logger.info(f"Fetching timeline for manuscript ID: {manuscript_id}")

        # Check access
        manuscript = await self.repository.get_by_id(manuscript_id)
        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ManuscriptErrorCode.MANUSCRIPT_NOT_FOUND
            )

        timeline = await self.repository.get_timeline(manuscript_id)

        return [TimelineEvent(**event) for event in timeline]

    # ==================== Discussions ====================

    async def get_manuscript_discussions(self, manuscript_id: int, user_id: int) -> List[DiscussionResponse]:
        """Get all discussions for a manuscript"""
        logger.info(f"Fetching discussions for manuscript ID: {manuscript_id}")

        # Check access
        manuscript = await self.repository.get_by_id(manuscript_id)
        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ManuscriptErrorCode.MANUSCRIPT_NOT_FOUND
            )

        discussions = await self.repository.get_discussions(manuscript_id)

        # Transform to response format
        discussion_responses = []
        for discussion in discussions:
            # Get user role (simplified - you might want to fetch actual roles)
            user_role = "Auteur" if discussion.user_id == manuscript.author_id else "Évaluateur"

            replies = []
            for reply in discussion.replies:
                reply_role = "Auteur" if reply.user_id == manuscript.author_id else "Évaluateur"
                replies.append(DiscussionResponse(
                    id=reply.id,
                    manuscriptId=reply.manuscript_id,
                    userId=reply.user_id,
                    userName=reply.user.full_name,
                    userRole=reply_role,
                    parentId=reply.parent_id,
                    subject=reply.subject,
                    message=reply.message,
                    isInternal=reply.is_internal,
                    createdAt=reply.created_at,
                    updatedAt=reply.updated_at,
                    replies=[]
                ))

            discussion_responses.append(DiscussionResponse(
                id=discussion.id,
                manuscriptId=discussion.manuscript_id,
                userId=discussion.user_id,
                userName=discussion.user.full_name,
                userRole=user_role,
                parentId=discussion.parent_id,
                subject=discussion.subject,
                message=discussion.message,
                isInternal=discussion.is_internal,
                createdAt=discussion.created_at,
                updatedAt=discussion.updated_at,
                replies=replies
            ))

        return discussion_responses

    async def reply_to_discussion(
        self,
        discussion_id: int,
        reply_data: DiscussionReplyCreate,
        user_id: int
    ) -> DiscussionResponse:
        """Reply to a discussion"""
        logger.info(f"Replying to discussion ID: {discussion_id}")

        # Check discussion exists
        discussion = await self.repository.get_discussion_by_id(discussion_id)
        if not discussion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discussion not found"
            )

        # Create reply
        reply = await self.repository.create_discussion(
            manuscript_id=discussion.manuscript_id,
            user_id=user_id,
            subject=None,
            message=reply_data.message,
            parent_id=discussion_id
        )

        # Get manuscript for role determination
        manuscript = await self.repository.get_by_id(discussion.manuscript_id)
        user_role = "Auteur" if user_id == manuscript.author_id else "Évaluateur"

        return DiscussionResponse(
            id=reply.id,
            manuscriptId=reply.manuscript_id,
            userId=reply.user_id,
            userName=reply.user.full_name,
            userRole=user_role,
            parentId=reply.parent_id,
            subject=reply.subject,
            message=reply.message,
            isInternal=reply.is_internal,
            createdAt=reply.created_at,
            updatedAt=reply.updated_at,
            replies=[]
        )

    # ==================== Review Comments ====================

    async def get_review_comments(self, manuscript_id: int, user_id: int) -> List[ReviewCommentResponse]:
        """Get all review comments for a manuscript"""
        logger.info(f"Fetching review comments for manuscript ID: {manuscript_id}")

        # Check access
        manuscript = await self.repository.get_by_id(manuscript_id)
        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ManuscriptErrorCode.MANUSCRIPT_NOT_FOUND
            )

        comments = await self.repository.get_review_comments(manuscript_id)

        # Transform to response format
        comment_responses = []
        for comment in comments:
            # Determine if user can reply (simplified logic)
            can_reply = user_id == manuscript.author_id or comment.user_id == user_id

            comment_responses.append(ReviewCommentResponse(
                id=comment.id,
                reviewResponseId=comment.review_response_id,
                userId=comment.user_id,
                userName=comment.user.full_name,
                userRole="Évaluateur",  # Simplified
                comment=comment.comment,
                isInternal=comment.is_internal,
                createdAt=comment.created_at,
                updatedAt=comment.updated_at,
                canReply=can_reply
            ))

        return comment_responses

    # ==================== Helper Methods ====================

    async def _save_upload_file(self, upload_file: UploadFile, manuscript_id: int, file_type: str) -> str:
        """Save an uploaded file and return the file path"""
        # Create upload directory if it doesn't exist
        upload_dir = "app/uploads"
        os.makedirs(upload_dir, exist_ok=True)

        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"manuscript_{manuscript_id}_{file_type}_{timestamp}_{upload_file.filename}"
        file_path = os.path.join(upload_dir, filename)

        # Save file
        with open(file_path, "wb") as buffer:
            content = await upload_file.read()
            buffer.write(content)

        return filename
