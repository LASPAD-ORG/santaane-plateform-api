"""
manuscripts module - Error codes
"""
from enum import Enum


class ManuscriptErrorCode(str, Enum):
    """Manuscript module error codes"""

    MANUSCRIPT_NOT_FOUND = "MANUSCRIPT_NOT_FOUND"
    MANUSCRIPT_ALREADY_EXISTS = "MANUSCRIPT_ALREADY_EXISTS"
    INVALID_MANUSCRIPT_DATA = "INVALID_MANUSCRIPT_DATA"

    # À compléter - ajouter d'autres codes d'erreur selon les besoins
