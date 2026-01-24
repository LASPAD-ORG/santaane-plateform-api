"""
dashboards module - Constants and Enums
Module-specific constants and enumerations
"""
from enum import Enum


class DashboardStatus(str, Enum):
    """Dashboard status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


# Module-specific constants
DEFAULT_DASHBOARD_PAGE_SIZE = 20
MAX_DASHBOARD_PAGE_SIZE = 100

# À compléter selon les besoins du module
