"""
assign_auteur_mentor module - Constants and Enums
Module-specific constants and enumerations
"""
from enum import Enum


class Assign_auteur_mentorStatus(str, Enum):
    """Assign_auteur_mentor status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


# Module-specific constants
DEFAULT_ASSIGN_AUTEUR_MENTOR_PAGE_SIZE = 20
MAX_ASSIGN_AUTEUR_MENTOR_PAGE_SIZE = 100

# À compléter selon les besoins du module
