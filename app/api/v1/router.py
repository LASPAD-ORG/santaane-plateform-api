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
from app.modules.manuscripts import redaction_routes
from app.modules.manuscripts import editorial_routes # Import de votre nouvelle partie
from app.modules.manuscripts import attachment_routes
from app.modules.manuscripts import version_routes
from app.modules.themes import router as themes_router
from app.modules.languages import router as languages_router
from app.modules.sections import router as sections_router
from app.modules.dashboards import router as dashboards_router
from app.modules.public import routes as public_routes
from app.modules.manuscripts import proposal_routes

# Create main v1 router
router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(roles.router)
router.include_router(users.router)
router.include_router(files.router)
router.include_router(manuscripts.router)
router.include_router(evaluator_routes.router)
router.include_router(annotation_routes.router)
router.include_router(evaluation_grid_routes.router)
router.include_router(redaction_routes.router)
router.include_router(editorial_routes.router) # Inclusion de votre module éditorial
router.include_router(attachment_routes.router)
router.include_router(version_routes.router)
router.include_router(proposal_routes.router)
# --- Bloc Configuration & Dashboards ---
router.include_router(themes_router)
router.include_router(languages_router)
router.include_router(sections_router)
router.include_router(dashboards_router)
router.include_router(public_routes.router)