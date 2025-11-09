"""
Main API v1 router
Aggregates all v1 endpoints
"""
from fastapi import APIRouter
from app.api.v1 import auth, students

# Create main v1 router
router = APIRouter(prefix="/api/v1")

# Include all sub-routers
router.include_router(auth.router, tags=["Authentication"])
router.include_router(students.router, tags=["Students"])
