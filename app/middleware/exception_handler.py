"""
Global exception handler middleware.
Catches all exceptions and returns standardized JSON responses with error codes.

Frontend receives only error codes for programmatic handling.
Detailed error messages are logged for backend debugging.
"""
from datetime import datetime
from fastapi import Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from app.core.error_codes import GeneralErrorCode
from app.core.logging import get_logger

logger = get_logger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTPException with error codes.

    The HTTPException.detail field contains the error_code (string).

    Logs:
        - Error level with status code and error_code for debugging

    Response to frontend:
        - Only error_code (no detailed message)
        - Timestamp for request tracking
        - Request path for context
    """
    logger.error(
        f"HTTP Error | "
        f"error_code={exc.detail} | "
        f"status={exc.status_code} | "
        f"path={request.url.path}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": exc.detail,  # detail contains the error_code
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError | PydanticValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors (422 Unprocessable Entity)

    Logs:
        - Warning level with full Pydantic error details for debugging

    Response to frontend:
        - Generic VALIDATION_ERROR code
        - No detailed field errors (frontend should handle validation client-side)
    """
    logger.warning(
        f"Validation Error | "
        f"error_code={GeneralErrorCode.VALIDATION_ERROR} | "
        f"path={request.url.path} | "
        f"details={exc.errors()}"
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error_code": GeneralErrorCode.VALIDATION_ERROR,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected/unhandled exceptions (500 Internal Server Error)

    Logs:
        - Exception level with full traceback for debugging

    Response to frontend:
        - Generic INTERNAL_SERVER_ERROR code
        - No error details for security (avoid leaking implementation details)
    """
    logger.exception(
        f"Unexpected error: {str(exc)} | "
        f"error_code={GeneralErrorCode.INTERNAL_SERVER_ERROR} | "
        f"path={request.url.path}"
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error_code": GeneralErrorCode.INTERNAL_SERVER_ERROR,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )
