"""
assign_auteur_mentor module - Business logic service for Mentor Assignment
"""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.assign_auteur_mentor.repository import MentorAssignmentRepository
from app.modules.assign_auteur_mentor.schemas import (
    MentorAssignmentCreate,
    MentorAssignmentUpdate,
    MentorAssignmentResponse,
    PaginatedMentorAssignmentResponse,
    MentorAssignmentDetailResponse
)
from app.modules.assign_auteur_mentor.error_codes import MentorAssignmentErrorCode
from app.core.logging import get_logger
from app.core.roles import UserRole
from app.models.user import User
from app.models.mentor_assignment import MentorAssignment
from app.modules.auth.repository import AuthRepository

logger = get_logger(__name__)


class MentorAssignmentService:
    """Service for mentor assignment business logic"""

    def __init__(self, repository: MentorAssignmentRepository, db: AsyncSession):
        self.repository = repository
        self.db = db
        self.auth_repo = AuthRepository(db)

    async def _get_user_by_id(self, user_id: int) -> User:
        """Get user by ID or raise exception"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            logger.warning(f"User not found: ID {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=MentorAssignmentErrorCode.AUTHOR_NOT_FOUND
            )
        return user

    async def _verify_user_role(self, user_id: int, required_role: UserRole) -> bool:
        """Verify user has a specific role"""
        user_roles = await self.auth_repo.get_user_roles(user_id)
        
        # SUPER_ADMIN always has access
        if UserRole.SUPER_ADMIN.value in user_roles:
            return True
        
        return required_role.value in user_roles

    async def _validate_assignment_permission(self, current_user: User) -> None:
        """Validate current user can assign mentors (SUPER_ADMIN or EDITOR)"""
        user_roles = await self.auth_repo.get_user_roles(current_user.id)
        
        allowed_roles = [UserRole.SUPER_ADMIN.value, UserRole.EDITOR.value]
        if not any(role in user_roles for role in allowed_roles):
            logger.warning(
                f"Insufficient permissions for assignment: {current_user.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=MentorAssignmentErrorCode.INSUFFICIENT_PERMISSIONS
            )

    async def get_all_assignments(
        self, skip: int = 0, limit: int = 20
    ) -> PaginatedMentorAssignmentResponse:
        """Get all mentor assignments with pagination"""
        logger.info(f"Fetching all mentor assignments (skip={skip}, limit={limit})")
        result = await self.repository.get_all(skip=skip, limit=limit)
        
        items = [MentorAssignmentResponse.model_validate(item) for item in result["items"]]
        return PaginatedMentorAssignmentResponse(
            items=items,
            total=result["total"],
            skip=result["skip"],
            limit=result["limit"],
            has_more=result["has_more"]
        )

    async def get_assignment_by_id(self, assignment_id: int) -> MentorAssignmentResponse:
        """Get mentor assignment by ID"""
        logger.info(f"Fetching mentor assignment ID: {assignment_id}")
        assignment = await self.repository.get_by_id(assignment_id)
        
        if not assignment:
            logger.warning(f"Mentor assignment not found: ID {assignment_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=MentorAssignmentErrorCode.ASSIGNMENT_NOT_FOUND
            )
        
        return MentorAssignmentResponse.model_validate(assignment)

    async def create_assignment(
        self,
        assignment_data: MentorAssignmentCreate,
        current_user: User
    ) -> MentorAssignmentResponse:
        """Create a new mentor assignment with full validation"""
        logger.info(
            f"Creating mentor assignment: author_id={assignment_data.author_id}, "
            f"mentor_id={assignment_data.mentor_id} by user {current_user.email}"
        )
        
        # Validate permissions
        await self._validate_assignment_permission(current_user)

        # Validate author and mentor are different
        if assignment_data.author_id == assignment_data.mentor_id:
            logger.warning(
                f"Attempted to assign author as their own mentor: {assignment_data.author_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=MentorAssignmentErrorCode.SAME_USER_ASSIGNMENT
            )

        # Verify author exists and has AUTHOR role
        author = await self._get_user_by_id(assignment_data.author_id)
        has_author_role = await self._verify_user_role(
            assignment_data.author_id, UserRole.AUTHOR
        )
        if not has_author_role:
            logger.warning(
                f"User is not an author: {assignment_data.author_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=MentorAssignmentErrorCode.AUTHOR_INVALID_ROLE
            )

        # Verify mentor exists and has MENTOR role
        try:
            mentor = await self._get_user_by_id(assignment_data.mentor_id)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=MentorAssignmentErrorCode.MENTOR_NOT_FOUND
            )
        
        has_mentor_role = await self._verify_user_role(
            assignment_data.mentor_id, UserRole.MENTOR
        )
        if not has_mentor_role:
            logger.warning(
                f"User is not a mentor: {assignment_data.mentor_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=MentorAssignmentErrorCode.MENTOR_INVALID_ROLE
            )

        # Check for existing active mentor assignment
        existing_active = await self.repository.get_active_by_author(
            assignment_data.author_id
        )
        if existing_active:
            logger.warning(
                f"Author {assignment_data.author_id} already has active mentor assignment with mentor {existing_active.mentor_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": MentorAssignmentErrorCode.ACTIVE_MENTOR_EXISTS,
                    "message": "Cet auteur possède déjà un mentor actif.",
                    "existing_assignment": {
                        "id": existing_active.id,
                        "mentor_id": existing_active.mentor_id,
                        "created_at": existing_active.created_at.isoformat()
                    },
                    "suggestion": "Veuillez désactiver l'assignation existante avant d'en créer une nouvelle."
                }
            )

        # Create new assignment
        assignment_dict = {
            "author_id": assignment_data.author_id,
            "mentor_id": assignment_data.mentor_id,
            "assigned_by": current_user.id,
            "is_active": True
        }
        
        new_assignment = await self.repository.create(assignment_dict)
        logger.info(f"Mentor assignment created successfully: ID {new_assignment.id}")
        
        return MentorAssignmentResponse.model_validate(new_assignment)

    async def update_assignment(
        self,
        assignment_id: int,
        update_data: MentorAssignmentUpdate,
        current_user: User
    ) -> MentorAssignmentResponse:
        """Update a mentor assignment"""
        logger.info(f"Updating mentor assignment ID: {assignment_id} by user {current_user.email}")
        
        # Validate permissions
        await self._validate_assignment_permission(current_user)

        # Get existing assignment
        assignment = await self.repository.get_by_id(assignment_id)
        if not assignment:
            logger.warning(f"Mentor assignment not found: ID {assignment_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=MentorAssignmentErrorCode.ASSIGNMENT_NOT_FOUND
            )

        # Prepare update data
        update_dict = {}
        
        if update_data.mentor_id is not None:
            # Validate new mentor
            if update_data.mentor_id == assignment.author_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=MentorAssignmentErrorCode.SAME_USER_ASSIGNMENT
                )
            
            # Verify mentor exists and has role
            try:
                mentor = await self._get_user_by_id(update_data.mentor_id)
            except HTTPException:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=MentorAssignmentErrorCode.MENTOR_NOT_FOUND
                )
            
            has_mentor_role = await self._verify_user_role(
                update_data.mentor_id, UserRole.MENTOR
            )
            if not has_mentor_role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=MentorAssignmentErrorCode.MENTOR_INVALID_ROLE
                )
            
            update_dict["mentor_id"] = update_data.mentor_id
        
        if update_data.is_active is not None:
            # If making active, check for existing active assignments
            if update_data.is_active and not assignment.is_active:
                existing_active = await self.repository.get_active_by_author(assignment.author_id)
                if existing_active:
                    logger.warning(
                        f"Author {assignment.author_id} already has active mentor assignment with mentor {existing_active.mentor_id}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail={
                            "error": MentorAssignmentErrorCode.ACTIVE_MENTOR_EXISTS,
                            "message": "Cet auteur possède déjà un mentor actif.",
                            "existing_assignment": {
                                "id": existing_active.id,
                                "mentor_id": existing_active.mentor_id,
                                "created_at": existing_active.created_at.isoformat()
                            },
                            "suggestion": "Veuillez désactiver l'assignation existante avant d'activer celle-ci."
                        }
                    )
            # If keeping active and changing mentor, check for conflicts
            elif update_data.is_active and assignment.is_active and update_data.mentor_id is not None:
                # Check if author already has another active assignment with different mentor
                conflict_check = await self.repository.check_active_assignment_conflict(
                    assignment.author_id, update_data.mentor_id, assignment_id
                )
                if conflict_check:
                    logger.warning(
                        f"Author {assignment.author_id} already has active assignment with different mentor"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail={
                            "error": MentorAssignmentErrorCode.ACTIVE_MENTOR_EXISTS,
                            "message": "Cet auteur possède déjà un mentor actif.",
                            "existing_assignment": {
                                "id": conflict_check.id,
                                "mentor_id": conflict_check.mentor_id,
                                "created_at": conflict_check.created_at.isoformat()
                            },
                            "suggestion": "Veuillez désactiver l'assignation existante avant de modifier le mentor."
                        }
                    )
            
            update_dict["is_active"] = update_data.is_active
        
        if not update_dict:
            logger.warning("No valid update data provided")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=MentorAssignmentErrorCode.INVALID_ASSIGNMENT_DATA
            )

        # Update assignment
        updated_assignment = await self.repository.update(assignment, update_dict)
        logger.info(f"Mentor assignment updated successfully: ID {assignment_id}")
        
        return MentorAssignmentResponse.model_validate(updated_assignment)

    async def delete_assignment(
        self, assignment_id: int, current_user: User
    ) -> dict:
        """Delete a mentor assignment"""
        logger.info(f"Deleting mentor assignment ID: {assignment_id} by user {current_user.email}")
        
        # Validate permissions
        await self._validate_assignment_permission(current_user)

        # Get assignment
        assignment = await self.repository.get_by_id(assignment_id)
        if not assignment:
            logger.warning(f"Mentor assignment not found: ID {assignment_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=MentorAssignmentErrorCode.ASSIGNMENT_NOT_FOUND
            )

        # Delete assignment
        await self.repository.delete(assignment)
        logger.info(f"Mentor assignment deleted successfully: ID {assignment_id}")
        
        return {"success": True, "message": "Mentor assignment deleted successfully"}

    async def get_mentor_authors(
        self,
        mentor_id: int,
        current_user: User,
        skip: int = 0,
        limit: int = 20,
        active_only: bool = True
    ) -> PaginatedMentorAssignmentResponse:
        """Get all authors assigned to a mentor"""
        logger.info(
            f"Fetching authors for mentor ID: {mentor_id} "
            f"by user {current_user.email} (skip={skip}, limit={limit})"
        )
        
        # Validate permission: User must be SUPER_ADMIN, EDITOR, or the mentor themselves
        user_roles = await self.auth_repo.get_user_roles(current_user.id)
        is_admin_or_editor = UserRole.SUPER_ADMIN.value in user_roles or UserRole.EDITOR.value in user_roles
        is_own_mentorship = current_user.id == mentor_id
        
        if not (is_admin_or_editor or is_own_mentorship):
            logger.warning(
                f"Insufficient permissions to view mentor authors: {current_user.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=MentorAssignmentErrorCode.INSUFFICIENT_PERMISSIONS
            )

        # Verify mentor exists
        mentor = await self._get_user_by_id(mentor_id)

        # Get mentor's authors
        result = await self.repository.get_mentor_authors(
            mentor_id=mentor_id,
            skip=skip,
            limit=limit,
            active_only=active_only
        )
        
        items = [MentorAssignmentResponse.model_validate(item) for item in result["items"]]
        return PaginatedMentorAssignmentResponse(
            items=items,
            total=result["total"],
            skip=result["skip"],
            limit=result["limit"],
            has_more=result["has_more"]
        )
