"""
roles module - Business logic service
Handles roles business logic
"""
from fastapi import HTTPException, status
from typing import Optional

from app.modules.roles.repository import RoleRepository
from app.modules.roles.schemas import (
    RoleCreate, RoleUpdate, RoleResponse,
    UserRoleAssign, UserRoleResponse, PaginatedRoleResponse
)
from app.modules.roles.error_codes import RoleErrorCode
from app.core.logging import get_logger

logger = get_logger(__name__)


class RoleService:
    """Service for roles business logic"""

    def __init__(self, repository: RoleRepository):
        self.repository = repository

    async def get_all_roles(self, skip: int = 0, limit: int = 20) -> PaginatedRoleResponse:
        """Get all roles with pagination"""
        logger.info(f"Fetching roles: skip={skip}, limit={limit}")

        data = await self.repository.get_all(skip, limit)

        return PaginatedRoleResponse(
            items=[
                RoleResponse(
                    id=role.id,
                    name=role.name,
                    description=role.description,
                    createdAt=role.created_at,
                    updatedAt=role.updated_at
                ) for role in data["items"]
            ],
            total=data["total"],
            skip=data["skip"],
            limit=data["limit"],
            hasMore=data["has_more"]
        )

    async def get_role_by_id(self, role_id: int) -> RoleResponse:
        """Get role by ID"""
        logger.info(f"Fetching role by ID: {role_id}")

        role = await self.repository.get_by_id(role_id)
        if not role:
            logger.warning(f"Role not found: {role_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=RoleErrorCode.ROLE_NOT_FOUND
            )

        return RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            createdAt=role.created_at,
            updatedAt=role.updated_at
        )

    async def create_role(self, role_data: RoleCreate) -> RoleResponse:
        """Create a new role"""
        logger.info(f"Creating role: {role_data.name}")

        # Check if role already exists
        if await self.repository.role_exists(role_data.name):
            logger.warning(f"Role already exists: {role_data.name}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=RoleErrorCode.ROLE_ALREADY_EXISTS
            )

        role = await self.repository.create(role_data.model_dump())

        logger.info(f"Role created successfully: {role.name}")

        return RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            createdAt=role.created_at,
            updatedAt=role.updated_at
        )

    async def update_role(self, role_id: int, role_data: RoleUpdate) -> RoleResponse:
        """Update an existing role"""
        logger.info(f"Updating role: {role_id}")

        role = await self.repository.get_by_id(role_id)
        if not role:
            logger.warning(f"Role not found: {role_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=RoleErrorCode.ROLE_NOT_FOUND
            )

        # Check if new name already exists (if name is being updated)
        if role_data.name and role_data.name != role.name:
            if await self.repository.role_exists(role_data.name):
                logger.warning(f"Role name already exists: {role_data.name}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=RoleErrorCode.ROLE_ALREADY_EXISTS
                )

        update_dict = role_data.model_dump(exclude_unset=True)
        role = await self.repository.update(role, update_dict)

        logger.info(f"Role updated successfully: {role.name}")

        return RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            createdAt=role.created_at,
            updatedAt=role.updated_at
        )

    async def delete_role(self, role_id: int):
        """Delete a role"""
        logger.info(f"Deleting role: {role_id}")

        role = await self.repository.get_by_id(role_id)
        if not role:
            logger.warning(f"Role not found: {role_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=RoleErrorCode.ROLE_NOT_FOUND
            )

        # Check if role is assigned to any users
        # TODO: Add check to prevent deletion if users have this role

        await self.repository.delete(role)

        logger.info(f"Role deleted successfully: {role_id}")

    async def assign_role_to_user(
        self,
        assign_data: UserRoleAssign,
        assigned_by: Optional[int] = None
    ) -> UserRoleResponse:
        """Assign a role to a user"""
        logger.info(f"Assigning role {assign_data.roleId} to user {assign_data.userId}")

        # Check if user exists
        user = await self.repository.get_user_by_id(assign_data.userId)
        if not user:
            logger.warning(f"User not found: {assign_data.userId}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=RoleErrorCode.USER_NOT_FOUND
            )

        # Check if role exists
        role = await self.repository.get_by_id(assign_data.roleId)
        if not role:
            logger.warning(f"Role not found: {assign_data.roleId}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=RoleErrorCode.ROLE_NOT_FOUND
            )

        # Check if user already has this role
        if await self.repository.user_has_role(assign_data.userId, assign_data.roleId):
            logger.warning(f"User {assign_data.userId} already has role {assign_data.roleId}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=RoleErrorCode.USER_ALREADY_HAS_ROLE
            )

        user_role = await self.repository.assign_role_to_user(
            assign_data.userId,
            assign_data.roleId,
            assigned_by
        )

        logger.info(f"Role assigned successfully")

        return UserRoleResponse(
            id=user_role.id,
            userId=user_role.user_id,
            roleId=user_role.role_id,
            roleName=user_role.role.name,
            assignedBy=user_role.assigned_by,
            assignedAt=user_role.assigned_at
        )

    async def remove_role_from_user(self, user_id: int, role_id: int):
        """Remove a role from a user"""
        logger.info(f"Removing role {role_id} from user {user_id}")

        # Check if user has this role
        if not await self.repository.user_has_role(user_id, role_id):
            logger.warning(f"User {user_id} does not have role {role_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=RoleErrorCode.USER_DOES_NOT_HAVE_ROLE
            )

        await self.repository.remove_role_from_user(user_id, role_id)

        logger.info(f"Role removed successfully")

    async def get_user_roles(self, user_id: int) -> list[UserRoleResponse]:
        """Get all roles for a user"""
        logger.info(f"Fetching roles for user: {user_id}")

        # Check if user exists
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=RoleErrorCode.USER_NOT_FOUND
            )

        user_roles = await self.repository.get_user_roles(user_id)

        return [
            UserRoleResponse(
                id=ur.id,
                userId=ur.user_id,
                roleId=ur.role_id,
                roleName=ur.role.name,
                assignedBy=ur.assigned_by,
                assignedAt=ur.assigned_at
            ) for ur in user_roles
        ]
