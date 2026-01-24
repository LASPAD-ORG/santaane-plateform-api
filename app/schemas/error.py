"""
Error Response Schemas
Standardized error response models for API
"""
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """
    Standardized error response format for all API errors.

    This schema is used for all error responses (4xx, 5xx) to provide
    a consistent format for frontend error handling.

    The frontend receives only the errorCode and can handle it programmatically.
    Detailed error messages are logged on the backend for debugging.

    Example:
        {
            "errorCode": "STUDENT_NOT_FOUND"
        }
    """

    errorCode: str = Field(
        ...,
        description="Machine-readable error code for programmatic handling",
        examples=["STUDENT_NOT_FOUND", "INVALID_CREDENTIALS", "VALIDATION_ERROR"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "errorCode": "STUDENT_NOT_FOUND"
            }
        }
