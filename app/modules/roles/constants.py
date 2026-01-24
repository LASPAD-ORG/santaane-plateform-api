"""
roles module - Constants and Enums
Module-specific constants and enumerations
"""
from enum import Enum


class RoleStatus(str, Enum):
    """Role status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


# Module-specific constants
DEFAULT_ROLE_PAGE_SIZE = 20
MAX_ROLE_PAGE_SIZE = 100

# À compléter selon les besoins du module
