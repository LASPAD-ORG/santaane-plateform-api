"""
Business logic layer for laboratories module.
Handles validation and orchestration of laboratory operations.
"""
from fastapi import HTTPException, status
from typing import List, Optional
from app.modules.laboratories.repository import LaboratoryRepository
from app.modules.laboratories.schemas import (
    LaboratoryCreate,
    LaboratoryUpdate,
    LaboratoryResponse,
    LaboratoryWithEditorsResponse,
    EditorAssignmentCreate,
    EditorAssignmentResponse,
    AvailableEditorResponse
)
from app.models.user import User
from app.core.logging import logger
from app.schemas.base import PaginatedResponse


class LaboratoryService:
    """Service for laboratory business logic."""

    def __init__(self, repository: LaboratoryRepository):
        self.repository = repository

    async def create_laboratory(
        self,
        data: LaboratoryCreate,
        current_user: User
    ) -> LaboratoryResponse:
        """
        Create a new laboratory.
        Only SUPER_ADMIN can create laboratories.
        """
        # Check if laboratory with same name already exists
        existing = await self.repository.get_by_name(data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Laboratory with name '{data.name}' already exists"
            )

        laboratory = await self.repository.create(data, created_by=current_user.id)
        return LaboratoryResponse.model_validate(laboratory)

    async def get_laboratory(self, laboratory_id: int) -> LaboratoryResponse:
        """Get laboratory by ID."""
        laboratory = await self.repository.get_by_id(laboratory_id)
        if not laboratory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Laboratory with ID {laboratory_id} not found"
            )

        return LaboratoryResponse.model_validate(laboratory)

    async def list_laboratories(
        self,
        skip: int = 0,
        limit: int = 20,
        is_active: Optional[bool] = None
    ) -> PaginatedResponse[LaboratoryResponse]:
        """List all laboratories with pagination."""
        laboratories, total = await self.repository.get_all(
            skip=skip,
            limit=limit,
            is_active=is_active
        )

        items = [LaboratoryResponse.model_validate(lab) for lab in laboratories]

        return PaginatedResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + limit) < total
        )

    async def update_laboratory(
        self,
        laboratory_id: int,
        data: LaboratoryUpdate,
        current_user: User
    ) -> LaboratoryResponse:
        """Update an existing laboratory."""
        # Check if name is being changed and if it conflicts
        if data.name:
            existing = await self.repository.get_by_name(data.name)
            if existing and existing.id != laboratory_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Laboratory with name '{data.name}' already exists"
                )

        laboratory = await self.repository.update(laboratory_id, data)
        if not laboratory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Laboratory with ID {laboratory_id} not found"
            )

        return LaboratoryResponse.model_validate(laboratory)

    async def delete_laboratory(
        self,
        laboratory_id: int,
        current_user: User
    ) -> dict:
        """Soft delete a laboratory."""
        # Don't allow deletion of LASPAD
        laboratory = await self.repository.get_by_id(laboratory_id)
        if laboratory and laboratory.name == "LASPAD":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the default LASPAD laboratory"
            )

        success = await self.repository.delete(laboratory_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Laboratory with ID {laboratory_id} not found"
            )

        return {"message": "Laboratory deleted successfully"}

    # Editor Assignment Methods

    async def assign_editor(
        self,
        laboratory_id: int,
        data: EditorAssignmentCreate,
        current_user: User
    ) -> EditorAssignmentResponse:
        """Assign an editor to a laboratory."""
        # Verify laboratory exists
        laboratory = await self.repository.get_by_id(laboratory_id)
        if not laboratory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Laboratory with ID {laboratory_id} not found"
            )

        # TODO: Verify user exists and has EDITOR role
        # This would require UserRepository - for MVP, we trust the input

        assignment = await self.repository.assign_editor(
            laboratory_id=laboratory_id,
            data=data,
            assigned_by=current_user.id
        )

        # Load editor info for response
        assignment_with_user = await self.repository.get_laboratory_with_editors(laboratory_id)
        for editor_assignment in assignment_with_user.editor_assignments:
            if editor_assignment.id == assignment.id:
                return EditorAssignmentResponse.model_validate(editor_assignment)

        return EditorAssignmentResponse.model_validate(assignment)

    async def unassign_editor(
        self,
        laboratory_id: int,
        user_id: int,
        current_user: User
    ) -> dict:
        """Remove an editor from a laboratory."""
        success = await self.repository.unassign_editor(laboratory_id, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Editor assignment not found"
            )

        return {"message": "Editor unassigned successfully"}

    async def get_laboratory_editors(
        self,
        laboratory_id: int
    ) -> List[EditorAssignmentResponse]:
        """Get all editors assigned to a laboratory."""
        # Verify laboratory exists
        laboratory = await self.repository.get_by_id(laboratory_id)
        if not laboratory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Laboratory with ID {laboratory_id} not found"
            )

        editors = await self.repository.get_laboratory_editors(laboratory_id)
        return [EditorAssignmentResponse.model_validate(editor) for editor in editors]

    async def get_laboratory_with_editors(
        self,
        laboratory_id: int
    ) -> LaboratoryWithEditorsResponse:
        """Get laboratory with all associated editors."""
        laboratory = await self.repository.get_laboratory_with_editors(laboratory_id)
        if not laboratory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Laboratory with ID {laboratory_id} not found"
            )

        return LaboratoryWithEditorsResponse.model_validate(laboratory)

    async def get_available_editors(
        self,
        laboratory_id: Optional[int] = None
    ) -> List[AvailableEditorResponse]:
        """Get users with EDITOR role available for assignment."""
        editors = await self.repository.get_available_editors(laboratory_id)
        return [AvailableEditorResponse.model_validate(editor) for editor in editors]
