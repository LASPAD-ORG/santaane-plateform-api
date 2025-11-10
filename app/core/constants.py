"""
Common Constants and Enums
Shared across all modules in the application
"""
from enum import Enum


class Environment(str, Enum):
    """Application environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class SortOrder(str, Enum):
    """Sorting order for queries"""
    ASC = "asc"
    DESC = "desc"


class DateFormat(str, Enum):
    """Common date formats"""
    ISO_8601 = "%Y-%m-%dT%H:%M:%S"
    DATE_ONLY = "%Y-%m-%d"
    TIME_ONLY = "%H:%M:%S"
    DATETIME_READABLE = "%Y-%m-%d %H:%M:%S"


# Pagination constants
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MIN_PAGE_SIZE = 1

# Password constants
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

# Token constants
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30

# File upload constants
MAX_FILE_SIZE_MB = 10
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt"}

# Email constants
EMAIL_MAX_LENGTH = 255
NAME_MAX_LENGTH = 150

# Database constants
DEFAULT_STRING_LENGTH = 255
