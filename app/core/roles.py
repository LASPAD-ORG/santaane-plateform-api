"""
User roles enumeration
Defines all available roles in the system
"""
from enum import Enum


class UserRole(str, Enum):
    """
    User roles for role-based access control (RBAC)
    """
    SUPER_ADMIN = "SUPER_ADMIN"
    EDITOR = "EDITOR"
    EVALUATOR = "EVALUATOR"
    INTERNAL_EVALUATOR = "INTERNAL_EVALUATOR"
    MENTOR = "MENTOR"
    AUTHOR = "AUTHOR"

    @classmethod
    def get_all_roles(cls) -> list[str]:
        """Get all role values as a list"""
        return [role.value for role in cls]

    @classmethod
    def is_valid_role(cls, role: str) -> bool:
        """Check if a role name is valid"""
        return role in cls.get_all_roles()