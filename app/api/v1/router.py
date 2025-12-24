"""
Main API v1 router
Aggregates all v1 endpoints
"""
from fastapi import APIRouter
from app.modules.auth import routes as auth
from app.modules.roles import routes as roles
from app.modules.users import routes as users
from app.modules.files import routes as files
from app.modules.manuscripts import routes as manuscripts
from app.modules.manuscripts import evaluator_routes
from app.modules.manuscripts import annotation_routes
from app.modules.manuscripts import evaluation_grid_routes
from app.modules.themes import router as themes_router
from app.modules.languages import router as languages_router
from app.modules.sections import router as sections_router

# Create main v1 router
router = APIRouter(prefix="/api/v1")

# Include all sub-routers

router.include_router(auth.router)
router.include_router(roles.router)
router.include_router(users.router)
router.include_router(files.router)
router.include_router(manuscripts.router)
router.include_router(evaluator_routes.router)
router.include_router(annotation_routes.router)
router.include_router(evaluation_grid_routes.router)
router.include_router(themes_router)
router.include_router(languages_router)
router.include_router(sections_router)
