"""
Main API v1 router
Aggregates all v1 endpoints
"""
from fastapi import APIRouter
from app.modules.auth import routes as auth
from app.modules.roles import routes as roles

# Create main v1 router
router = APIRouter(prefix="/api/v1")

# Include all sub-routers 

router.include_router(auth.router)
router.include_router(roles.router)