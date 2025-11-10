"""
General Error Codes - Common to all modules
These error codes are used across the entire application
"""
from enum import Enum


class GeneralErrorCode(str, Enum):
    """
    General error codes that can be used by any module.
    These represent common HTTP errors and system-level issues.
    """

    # Server Errors (5xx)
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"

    # Client Errors (4xx)
    INVALID_REQUEST = "INVALID_REQUEST"
    VALIDATION_ERROR = "VALIDATION_ERROR"

    # Authentication & Authorization
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"

    # Resource Errors
    NOT_FOUND = "NOT_FOUND"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"

    # Other
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
    TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"
