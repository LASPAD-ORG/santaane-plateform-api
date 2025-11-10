"""
Error Response Schemas
Standardized error response models for API
"""
from datetime import datetime
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """
    Standardized error response format for all API errors.

    This schema is used for all error responses (4xx, 5xx) to provide
    a consistent format for frontend error handling.

    The frontend receives only the error_code and can handle it programmatically.
    Detailed error messages are logged on the backend for debugging.

    Example:
        {
            "success": false,
            "error_code": "STUDENT_NOT_FOUND",
            "timestamp": "2025-11-09T22:30:45.123456",
            "path": "/api/v1/students/999"
        }
    """

    success: bool = Field(
        default=False,
        description="Always false for error responses"
    )

    error_code: str = Field(
        ...,
        description="Machine-readable error code for programmatic handling",
        examples=["STUDENT_NOT_FOUND", "INVALID_CREDENTIALS", "VALIDATION_ERROR"]
    )

    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO 8601 timestamp of when the error occurred"
    )

    path: str = Field(
        ...,
        description="Request path that generated the error",
        examples=["/api/v1/students/999", "/api/v1/auth/login"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": "STUDENT_NOT_FOUND",
                "timestamp": "2025-11-09T22:30:45.123456",
                "path": "/api/v1/students/999"
            }
        }
