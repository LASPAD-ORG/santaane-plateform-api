"""
assign_auteur_mentor module - Error codes
"""
from enum import Enum


class Assign_auteur_mentorErrorCode(str, Enum):
    """Assign_auteur_mentor module error codes"""

    ASSIGN_AUTEUR_MENTOR_NOT_FOUND = "ASSIGN_AUTEUR_MENTOR_NOT_FOUND"
    ASSIGN_AUTEUR_MENTOR_ALREADY_EXISTS = "ASSIGN_AUTEUR_MENTOR_ALREADY_EXISTS"
    INVALID_ASSIGN_AUTEUR_MENTOR_DATA = "INVALID_ASSIGN_AUTEUR_MENTOR_DATA"

    # À compléter - ajouter d'autres codes d'erreur selon les besoins
