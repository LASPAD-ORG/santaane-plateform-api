"""
Business logic layer for users module.
Handles validation and orchestration of user operations.
"""
from fastapi import HTTPException, status
from typing import List, Optional
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import (
    UserCreate,
    UserUpdate,
    UserRoleUpdate,
    ProfileUpdate,
    UserResponse,
    UserWithRolesResponse,
    UserDetailResponse,
    PasswordChange,
    AdminPasswordReset,
    UserActivation,
    RoleInfo,
    EvaluatorCreate
)
from app.models.user import User
from app.core.security import hash_password, verify_password
from app.core.logging import logger
from app.schemas.base import PaginatedResponse



class UserService:
    """Service for user business logic."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def hard_delete_user(
        self,
        user_id: int,
        current_user: User
     ) -> dict:
        """Hard delete a user (permanent removal)."""
        # Prevent self-deletion
        if user_id == current_user.id:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        success = await self.repository.hard_delete(user_id)
        if not success:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        return {"message": "User permanently deleted"}

    async def create_user(
        self,
        data: UserCreate,
        current_user: User
     ) -> UserResponse:
        """
        Create a new user.
        Only SUPER_ADMIN can create users.
        """
        # Check if user with email already exists
        existing = await self.repository.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email '{data.email}' already exists"
            )

        # Hash password
        password_hash = hash_password(data.password)

        # Create user
        user = await self.repository.create(data, password_hash)
        
        # Assign roles if provided
        roles_to_assign = []
        
        # DEBUG: Log what we received
        logger.info(f"Received data - role_ids: {data.role_ids}, role_id: {data.role_id}")
        
        # Handle both role_ids (array) and role_id (single) for backward compatibility
        if data.role_ids:
            roles_to_assign.extend(data.role_ids)
            logger.info(f"Using role_ids array: {roles_to_assign}")
        elif data.role_id:
            roles_to_assign.append(data.role_id)
            logger.info(f"Using single role_id: {roles_to_assign}")
        else:
            logger.warning("No roles provided in user creation request")
        
        # Assign all roles
        for role_id in roles_to_assign:
            await self.repository.assign_role(user.id, role_id, current_user.id)
            logger.info(f"Role {role_id} assigned to user {user.id}")
        
        # Send welcome email with all assigned roles
        from app.core.email import EmailService
        
        # Get user with roles loaded
        user_with_roles = await self.repository.get_with_roles(user.id)
        
        # Extract all role names from user roles
        roles = []
        if user_with_roles and user_with_roles.user_roles:
            roles = [
                ur.role.name
                for ur in user_with_roles.user_roles
                if ur.role and ur.role.name
            ]
        
        roles_display = ", ".join(roles) if roles else "User"
        
        # Send email in background task to avoid blocking
        EmailService.send_new_user_credentials(
            to_email=user.email,
            full_name=user.full_name,
            password=data.password,  # Use the plain password before hashing
            roles=roles_display
        )
        
        return UserResponse.model_validate(user)

    async def create_evaluator(
        self,
        data: EvaluatorCreate,
        current_user: User
     ) -> UserWithRolesResponse:
        """
        Enrole un evaluateur (interne ou externe).
        - Si aucun compte : cree le compte (role evaluateur + AUTHOR), mot de passe aleatoire, email avec identifiants.
        - Si compte existant sans le role : ajoute le role, email d'invitation sans identifiants.
        - Si compte existant avec le role : ne fait rien (message 'deja evaluateur').
        Seuls EDITOR et SUPER_ADMIN peuvent enroler.
        """
        import secrets
        import string
        from app.core.email import EmailService
        from app.models.user import User as UserModel

        AUTHOR_ROLE_NAME = "AUTHOR"

        # Resoudre le role selon le type ('internal' ou 'external')
        evaluator_type = (data.evaluator_type or "external").lower()
        if evaluator_type not in ("internal", "external"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="evaluatorType must be 'internal' or 'external'"
            )
        role_name = "INTERNAL_EVALUATOR" if evaluator_type == "internal" else "EVALUATOR"
        role = await self.repository.get_role_by_name(role_name)
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Role '{role_name}' introuvable en base. Seed-le d'abord."
            )

        existing = await self.repository.get_by_email(data.email)

        if existing is not None:
            # Compte existant : verifier s'il a deja le role demande
            user_with_roles = await self.repository.get_with_roles(existing.id)
            existing_role_ids = []
            if user_with_roles and getattr(user_with_roles, "user_roles", None):
                existing_role_ids = [ur.role_id for ur in user_with_roles.user_roles]

            if role.id in existing_role_ids:
                # CAS C : deja le role → ne rien faire
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cet utilisateur possede deja le role {role_name} (deja evaluateur)."
                )

            # CAS B : compte existant sans le role → ajouter le role
            await self.repository.assign_role(existing.id, role.id, current_user.id)

            # Email d'invitation SANS identifiants (le compte existe deja)
            try:
                EmailService.send_evaluator_enrollment_email(
                    to_email=existing.email,
                    full_name=existing.full_name,
                    evaluator_type=evaluator_type,
                    login_email=existing.email,
                    password=None,
                    lang="fr",
                )
            except Exception as e:
                logger.warning(f"Failed to send enrollment invitation to {existing.email}: {str(e)}")

            refreshed = await self.repository.get_with_roles(existing.id)
            roles = []
            if hasattr(refreshed, 'user_roles') and refreshed.user_roles:
                for ur in refreshed.user_roles:
                    if hasattr(ur, 'role') and ur.role:
                        roles.append(RoleInfo.model_validate(ur.role))
            user_dict = UserResponse.model_validate(refreshed).model_dump()
            user_dict['roles'] = roles
            return UserWithRolesResponse(**user_dict)

        # CAS A : aucun compte → creer le compte + role evaluateur + AUTHOR
        alphabet = string.ascii_letters + string.digits + "!@#$%&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(12))
        password_hash = hash_password(password)

        user_data = UserModel(
            email=data.email,
            email_verified=False,
            password_hash=password_hash,
            full_name=data.full_name,
            orcid_id=data.orcid_id,
            bio=data.bio,
            position=data.position,
            institution=data.institution,
            is_active=True
        )
        user = await self.repository.create_user_model(user_data)

        # Role evaluateur
        await self.repository.assign_role(user.id, role.id, current_user.id)
        # Role AUTHOR (en plus)
        author_role = await self.repository.get_role_by_name(AUTHOR_ROLE_NAME)
        if author_role is not None:
            await self.repository.assign_role(user.id, author_role.id, current_user.id)

        # Email de bienvenue avec identifiants
        email_sent = EmailService.send_evaluator_enrollment_email(
            to_email=data.email,
            full_name=data.full_name,
            evaluator_type=evaluator_type,
            login_email=data.email,
            password=password,
            lang="fr",
        )
        if not email_sent:
            logger.warning(f"Failed to send welcome email to {data.email}")

        user_with_roles = await self.repository.get_with_roles(user.id)
        roles = []
        if hasattr(user_with_roles, 'user_roles') and user_with_roles.user_roles:
            for ur in user_with_roles.user_roles:
                if hasattr(ur, 'role') and ur.role:
                    roles.append(RoleInfo.model_validate(ur.role))
        user_dict = UserResponse.model_validate(user_with_roles).model_dump()
        user_dict['roles'] = roles
        return UserWithRolesResponse(**user_dict)

    async def get_user(self, user_id: int, current_user: User) -> UserWithRolesResponse:
        """
        Get user by ID with roles.
        Users can view their own profile, SUPER_ADMIN can view any.
        """
        user = await self.repository.get_with_roles(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Convert user_roles to roles list
        roles = []
        if hasattr(user, 'user_roles') and user.user_roles:
            for ur in user.user_roles:
                if hasattr(ur, 'role') and ur.role:
                    roles.append(RoleInfo.model_validate(ur.role))

        # Create response with roles
        user_dict = UserResponse.model_validate(user).model_dump()
        user_dict['roles'] = roles

        return UserWithRolesResponse(**user_dict)

    async def list_evaluators(
        self,
        skip: int = 0,
        limit: int = 100,
        role_name: str = "EVALUATOR",
        search: str = None,
     ) -> PaginatedResponse[UserWithRolesResponse]:
        """List all evaluators with pagination."""
        evaluators, total = await self.repository.get_all_evaluators(
            skip=skip,
            limit=limit,
            role_name=role_name,
            search=search,
        )

        # Convert evaluators with roles
        items = []
        for evaluator in evaluators:
            # Safely extract roles
            roles = []
            if hasattr(evaluator, 'user_roles') and evaluator.user_roles:
                for ur in evaluator.user_roles:
                    if hasattr(ur, 'role') and ur.role:
                        roles.append(RoleInfo.model_validate(ur.role))

            # Create user response
            user_dict = UserResponse.model_validate(evaluator).model_dump()
            user_dict['roles'] = roles

            items.append(UserWithRolesResponse(**user_dict))

        return PaginatedResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + limit) < total
        )
        
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 20,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
     ) -> PaginatedResponse[UserWithRolesResponse]:
        """List all users with pagination and filtering."""
        users, total = await self.repository.get_all(
            skip=skip,
            limit=limit,
            email=email,
            full_name=full_name,
            role=role,
            is_active=is_active
        )

        # Convert users with roles
        items = []
        for user in users:
            # Safely extract roles
            roles = []
            if hasattr(user, 'user_roles') and user.user_roles:
                for ur in user.user_roles:
                    if hasattr(ur, 'role') and ur.role:
                        roles.append(RoleInfo.model_validate(ur.role))
            
            user_dict = UserResponse.model_validate(user).model_dump()
            user_dict['roles'] = roles
            items.append(UserWithRolesResponse(**user_dict))

        return PaginatedResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + limit) < total
        )

    async def update_user_roles(
        self,
        user_id: int,
        role_ids: List[int],
        current_user: User
     ) -> UserWithRolesResponse:
        """
        Update user roles (remove all existing roles and assign new ones).
        Only SUPER_ADMIN can update roles.
        """
        # Get user with current roles
        user = await self.repository.get_with_roles(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Get current role names for comparison
        current_roles = []
        if hasattr(user, 'user_roles') and user.user_roles:
            current_roles = [
                ur.role.name
                for ur in user.user_roles
                if ur.role and ur.role.name
            ]

        # Remove all existing roles
        await self.repository.remove_all_user_roles(user_id)

        # Assign new roles
        new_role_names = []
        for role_id in role_ids:
            await self.repository.assign_role(user_id, role_id, current_user.id)
            # Get role name for notification
            role = await self.repository.get_role_by_id(role_id)
            if role:
                new_role_names.append(role.name)

        # Send notification email about role change
        from app.core.email import EmailService
        
        EmailService.send_User_update(
            to_email=user.email,
            full_name=user.full_name,
            updated_fields={'roles': new_role_names},
            admin_name=current_user.full_name
        )

        logger.info(f"Roles updated for user {user_id}: {new_role_names} by {current_user.id}")

        # Get updated user with roles
        updated_user = await self.repository.get_with_roles(user_id)
        
        # Convert to response
        roles = []
        if hasattr(updated_user, 'user_roles') and updated_user.user_roles:
            for ur in updated_user.user_roles:
                if hasattr(ur, 'role') and ur.role:
                    roles.append(RoleInfo.model_validate(ur.role))

        user_dict = UserResponse.model_validate(updated_user).model_dump()
        user_dict['roles'] = roles

        return UserWithRolesResponse(**user_dict)

    async def update_user(
        self,
        user_id: int,
        data: UserUpdate,
        current_user: User
     ) -> UserResponse:
        """Update an existing user."""
        # Check if email is being changed and if it conflicts
        if data.email:
            existing = await self.repository.get_by_email(data.email)
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with email '{data.email}' already exists"
                )

        # Get user before update for notification
        user_before = await self.repository.get_by_id(user_id)
        if not user_before:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        logger.info(f"User BEFORE update from DB: ID={user_before.id}, full_name='{user_before.full_name}', email='{user_before.email}'")

        # Extract updated fields for notification BEFORE the update
        from app.core.email import EmailService
        
        updated_fields = {}
        update_data = data.model_dump(exclude_unset=True)
        
        logger.info(f"Update data received: {update_data}")
        logger.info(f"Raw data object: {data}")
        logger.info(f"Data model_dump(exclude_none): {data.model_dump(exclude_none=True)}")
        logger.info(f"User being updated: ID {user_id}, Current user: ID {current_user.id}")
        
        # Handle roles separately if provided
        role_ids = update_data.pop('role_ids', None)
        roles_updated = False
        new_role_names = []
        
        if role_ids is not None:
            # Get current roles for comparison
            user_with_roles = await self.repository.get_with_roles(user_id)
            current_roles = []
            if hasattr(user_with_roles, 'user_roles') and user_with_roles.user_roles:
                current_roles = [
                    ur.role.name
                    for ur in user_with_roles.user_roles
                    if ur.role and ur.role.name
                ]
            
            # Remove all existing roles and assign new ones
            await self.repository.remove_all_user_roles(user_id)
            
            # Assign new roles
            for role_id in role_ids:
                await self.repository.assign_role(user_id, role_id, current_user.id)
                # Get role name for notification
                role = await self.repository.get_role_by_id(role_id)
                if role:
                    new_role_names.append(role.name)
            
            # Check if roles actually changed
            if set(current_roles) != set(new_role_names):
                roles_updated = True
                updated_fields['roles'] = new_role_names
            
            logger.info(f"Roles updated: {current_roles} -> {new_role_names}, changed={roles_updated}")
        
        # Compare with the ORIGINAL values before update for other fields
        for field, new_value in update_data.items():
            old_value = getattr(user_before, field, None)
            logger.info(f"Field {field}: old='{old_value}', new='{new_value}', changed={old_value != new_value}")
            if old_value != new_value:
                updated_fields[field] = new_value
        
        logger.info(f"Final updated_fields: {updated_fields}")

        user = await self.repository.update(user_id, data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        logger.info(f"User AFTER update from DB: ID={user.id}, full_name='{user.full_name}', email='{user.email}'")
        
        # Send email if there are actual changes and it's not the user updating their own profile
        if updated_fields and user_id != current_user.id:
            logger.info(f"Sending email notification to {user.email}")
            EmailService.send_User_update(
                to_email=user.email,
                full_name=user.full_name,
                updated_fields=updated_fields,
                admin_name=current_user.full_name
            )
            logger.info(f"Update notification sent to user {user.email} for changes: {list(updated_fields.keys())}")
        else:
            if not updated_fields:
                logger.info("No actual changes detected, skipping email notification")
            elif user_id == current_user.id:
                logger.info("User updating their own profile, skipping email notification")
            else:
                logger.info("Unknown reason for skipping email notification")

        return UserResponse.model_validate(user)

    async def update_own_profile(
        self,
        user_id: int,
        data: ProfileUpdate
     ) -> UserResponse:
        """Update own profile (users cannot change email)."""
        # Get user first
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Update all fields manually
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.profile_photo is not None:
            user.profile_photo = data.profile_photo
        if data.orcid_id is not None:
            user.orcid_id = data.orcid_id
        if data.bio is not None:
            user.bio = data.bio
        if data.position is not None:
            user.position = data.position
        if data.institution is not None:
            user.institution = data.institution
        
        # Commit changes
        await self.repository.db.commit()
        await self.repository.db.refresh(user)

        logger.info(f"Profile updated for user: {user.email} (ID: {user.id})")
        return UserResponse.model_validate(user)

    async def change_password(
        self,
        user_id: int,
        data: PasswordChange,
        current_user: User
      ) -> dict:
        """Change user password."""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Verify current password
        if not verify_password(data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Hash new password
        new_password_hash = hash_password(data.new_password)

        # Update password
        success = await self.repository.update_password(user_id, new_password_hash)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password"
            )

        return {"message": "Password updated successfully"}

    async def reset_user_password(
        self,
        user_id: int,
        data: AdminPasswordReset,
        current_user: User
      ) -> dict:
        """
        Reset user password (admin only).
        Admin does not need to know current password.
        """
        # Get target user
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Hash new password
        new_password_hash = hash_password(data.new_password)

        # Update password
        success = await self.repository.update_password(user_id, new_password_hash)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset password"
            )

        # Send notification email about password reset with the new password
        from app.core.email import EmailService
        
        EmailService.send_User_update(
            to_email=user.email,
            full_name=user.full_name,
            updated_fields={'password': data.new_password},  # Send the actual password
            admin_name=current_user.full_name
        )

        logger.info(f"Admin {current_user.id} reset password for user {user_id}")
        return {"message": "Password reset successfully"}

    async def activate_user(
        self,
        user_id: int,
        data: UserActivation,
        current_user: User
     ) -> UserResponse:
        """Activate or deactivate a user."""
        # Prevent self-deactivation
        if user_id == current_user.id and data.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot deactivate your own account."
            )
        user = await self.repository.set_active_status(user_id, data.is_active)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        status_text = "activated" if data.is_active else "deactivated"
        logger.info(f"User {status_text}: {user.email} by {current_user.email}")

        # Send notification email about status change
        from app.core.email import EmailService
        
        EmailService.send_User_update(
            to_email=user.email,
            full_name=user.full_name,
            updated_fields={'is_active': data.is_active},
            admin_name=current_user.full_name
        )

        return UserResponse.model_validate(user)

    async def delete_user(
        self,
        user_id: int,
        current_user: User
     ) -> dict:
        """Soft delete a user."""
        # Prevent self-deletion
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )

        # Get user info before deletion for notification
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        success = await self.repository.delete(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )

        # Send notification email about account deactivation
        from app.core.email import EmailService
        
        EmailService.send_inactive_user(
            to_email=user.email,
            full_name=user.full_name,
            admin_name=current_user.full_name,
            admin_email=current_user.email
        )

        logger.info(f"User {user_id} deactivated and notification sent to {user.email}")
        return {"message": "User deleted successfully"}
