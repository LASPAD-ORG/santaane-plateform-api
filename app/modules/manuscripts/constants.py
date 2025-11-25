"""
manuscripts module - Constants and Enums
Module-specific constants and enumerations
"""
from enum import Enum


class ManuscriptStatus(str, Enum):
    """Manuscript status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


# Module-specific constants
DEFAULT_MANUSCRIPT_PAGE_SIZE = 20
MAX_MANUSCRIPT_PAGE_SIZE = 100

# À compléter selon les besoins du module
