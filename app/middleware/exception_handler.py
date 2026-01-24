"""
Global exception handler middleware.
Catches all exceptions and returns standardized JSON responses with error codes.

Frontend receives only error codes for programmatic handling.
Detailed error messages are logged for backend debugging.
"""
from fastapi import Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import IntegrityError, DBAPIError

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
            "errorCode": exc.detail  # detail contains the errorCode
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
            "errorCode": GeneralErrorCode.VALIDATION_ERROR
        }
    )


async def database_error_handler(request: Request, exc: IntegrityError | DBAPIError) -> JSONResponse:
    """
    Handle SQLAlchemy database errors (IntegrityError, DBAPIError)

    Logs:
        - Error level with database error details for debugging

    Response to frontend:
        - Generic DATABASE_ERROR code
        - No sensitive database details
    """
    logger.error(
        f"Database Error | "
        f"error_code={GeneralErrorCode.DATABASE_ERROR} | "
        f"path={request.url.path} | "
        f"detail={str(exc)}"
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "errorCode": GeneralErrorCode.DATABASE_ERROR
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
            "errorCode": GeneralErrorCode.INTERNAL_SERVER_ERROR
        }
    )
