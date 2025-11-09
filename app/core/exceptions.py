"""
Custom exceptions for the API.
Simple and direct exception hierarchy.
"""


class APIException(Exception):
    """Base exception for all API errors"""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(APIException):
    """Resource not found"""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationError(APIException):
    """Validation failed"""

    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=422)


class AuthenticationError(APIException):
    """Authentication failed"""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class PermissionError(APIException):
    """Permission denied"""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, status_code=403)


class ConflictError(APIException):
    """Resource conflict (e.g., duplicate entry)"""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status_code=409)
