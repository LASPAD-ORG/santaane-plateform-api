"""
Request/Response logging middleware.
Logs every HTTP request and response with execution time.
"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses"""

    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.time()

        # Log incoming request
        logger.info(
            f"→ {request.method} {request.url.path} | "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )

        # Process request
        response: Response = await call_next(request)

        # Calculate execution time
        process_time = time.time() - start_time

        # Log response
        logger.info(
            f"← {request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Time: {process_time:.3f}s"
        )

        # Add custom header with process time
        response.headers["X-Process-Time"] = str(process_time)

        return response
