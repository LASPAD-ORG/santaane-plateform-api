"""
Santaane API - Main application entry point
Async FastAPI with proper error handling, logging, and CORS
"""
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.middleware.exception_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.cors import setup_cors
from app.api.v1.router import router as api_v1_router

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create FastAPI app with OAuth2 configuration for Swagger UI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_init_oauth={
        "clientId": "swagger-ui",
        "appName": settings.APP_NAME,
        "usePkceWithAuthorizationCodeGrant": True,
    }
)

# Setup CORS
setup_cors(app)

# Add middleware
app.add_middleware(LoggingMiddleware)

# Register exception handlers
from fastapi.exceptions import HTTPException
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API v1 router
app.include_router(api_v1_router)


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info(f"👋 Shutting down {settings.APP_NAME}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Bienvenue sur {settings.APP_NAME} 🚀",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }
