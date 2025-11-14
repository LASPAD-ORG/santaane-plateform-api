"""
Main API v1 router
Aggregates all v1 endpoints
"""
from fastapi import APIRouter
from app.modules.auth import routes as auth
from app.modules.roles import routes as roles
from app.modules.laboratories import routes as laboratories
from app.modules.users import routes as users
from app.modules.files import routes as files

# Create main v1 router
router = APIRouter(prefix="/api/v1")

# Include all sub-routers

router.include_router(auth.router)
router.include_router(roles.router)
router.include_router(laboratories.router)
router.include_router(users.router)
router.include_router(files.router)