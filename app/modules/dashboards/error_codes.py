"""
dashboards module - Error codes
"""
from enum import Enum


class DashboardErrorCode(str, Enum):
    """Dashboard module error codes"""

    DASHBOARD_NOT_FOUND = "DASHBOARD_NOT_FOUND"
    DASHBOARD_ALREADY_EXISTS = "DASHBOARD_ALREADY_EXISTS"
    INVALID_DASHBOARD_DATA = "INVALID_DASHBOARD_DATA"

    # À compléter - ajouter d'autres codes d'erreur selon les besoins
