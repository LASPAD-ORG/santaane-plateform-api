"""
dashboards module - API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.core.permissions import require_role
from app.core.roles import UserRole
from app.models.user import User
from app.modules.dashboards.schemas import (
    DashboardResponse,
    AuthorDashboardResponse,
    SuperAdminDashboardResponse,
    EditorDashboardResponse,
    EvaluatorDashboardResponse
)
from app.modules.dashboards.service import DashboardService
from app.modules.dashboards.utils import get_dashboard_service
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])


# ==================== Author Dashboard Routes ====================

@router.get("/author", response_model=AuthorDashboardResponse)
async def get_author_dashboard(
    current_user: User = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get complete dashboard for the authenticated author

    Returns:
    - Manuscript statistics (total submitted, rejected, accepted, published)
    - Bar chart data (manuscript status distribution)
    - Time series data (weekly, monthly, yearly submissions)

    Access: Any authenticated user can access their own dashboard
    """
    logger.info(f"Author dashboard requested by user_id={current_user.id}")

    # Get dashboard data for the current user (as author)
    dashboard = await service.get_author_dashboard(author_id=current_user.id)

    logger.info(f"Author dashboard returned successfully for user_id={current_user.id}")
    return dashboard


@router.get("/author/{author_id}", response_model=AuthorDashboardResponse)
async def get_author_dashboard_by_id(
    author_id: int,
    current_user: User = Depends(require_role(UserRole.EDITOR)),
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get dashboard for a specific author (by ID)

    Returns:
    - Manuscript statistics (total submitted, rejected, accepted, published)
    - Bar chart data (manuscript status distribution)
    - Time series data (weekly, monthly, yearly submissions)

    Access: EDITOR, SUPER_ADMIN only
    """
    logger.info(f"Author dashboard for author_id={author_id} requested by user_id={current_user.id}")

    # Get dashboard data for the specified author
    dashboard = await service.get_author_dashboard(author_id=author_id)

    logger.info(f"Author dashboard returned successfully for author_id={author_id}")
    return dashboard


# ==================== Super Admin Dashboard Routes ====================

@router.get("/super-admin", response_model=SuperAdminDashboardResponse)
async def get_super_admin_dashboard(
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN)),
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get complete system-wide dashboard for super admin

    Returns:
    - System statistics (manuscripts, users, rates)
    - Bar charts (status, theme, section, language distributions)
    - Time series (submissions and authors over time)

    Access: SUPER_ADMIN only

    Includes:
    1. **Statistics:**
       - Total manuscripts, submitted, rejected, accepted, published
       - Total authors, editors, evaluators
       - Manuscripts in evaluation and awaiting evaluators
       - Rejection rate, acceptance rate, publication rate, evaluation rate

    2. **Bar Charts:**
       - Manuscript status distribution
       - Submissions by theme
       - Submissions by section (rubrique)
       - Submissions by language

    3. **Time Series:**
       - Submissions per week/month/year
       - New authors per week/month/year
    """
    logger.info(f"Super admin dashboard requested by user_id={current_user.id}")

    # Get complete dashboard data
    dashboard = await service.get_super_admin_dashboard()

    logger.info("Super admin dashboard returned successfully")
    return dashboard


# ==================== Editor Dashboard Routes ====================

@router.get("/editor", response_model=EditorDashboardResponse)
async def get_editor_dashboard(
    current_user: User = Depends(require_role(UserRole.EDITOR)),
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get complete system-wide dashboard for editor

    Returns:
    - System statistics (manuscripts, users, rates)
    - Bar charts (status, theme, section, language distributions)
    - Time series (submissions and authors over time)

    Access: EDITOR, SUPER_ADMIN

    Includes:
    1. **Statistics:**
       - Total authors, editors, evaluators
       - Manuscripts: total, submitted, in evaluation, awaiting evaluators
       - Manuscripts: rejected, accepted, published
       - Rejection rate, acceptance rate, publication rate, evaluation rate

    2. **Bar Charts:**
       - Manuscript status distribution
       - Submissions by theme
       - Submissions by section (rubrique)
       - Submissions by language

    3. **Time Series:**
       - Submissions per week/month/year
       - New authors per week/month/year

    Note: Editors have the same dashboard as Super Admin as they need full
    system visibility for editorial management.
    """
    logger.info(f"Editor dashboard requested by user_id={current_user.id}")

    # Reuse the same service as super admin - editors need full system view
    dashboard = await service.get_super_admin_dashboard()

    logger.info("Editor dashboard returned successfully")

    # Convert to EditorDashboardResponse (same structure)
    return EditorDashboardResponse(**dashboard.model_dump())


# ==================== Evaluator Dashboard Routes ====================

@router.get("/evaluator", response_model=EvaluatorDashboardResponse)
async def get_evaluator_dashboard(
    current_user: User = Depends(require_role(UserRole.EVALUATOR)),
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get complete dashboard for the authenticated evaluator

    Returns:
    - Manuscript statistics (awaiting, in progress, evaluated)
    - Bar chart data (evaluation status distribution)
    - Time series data (weekly, monthly, yearly completed evaluations)

    Access: EVALUATOR, SUPER_ADMIN

    Includes:
    1. **Statistics:**
       - Manuscripts awaiting evaluation (assigned but not started)
       - Manuscripts in progress (evaluation grid started but not submitted)
       - Manuscripts evaluated (evaluation grid submitted)

    2. **Bar Chart:**
       - Evaluation status distribution (awaiting, in progress, evaluated)

    3. **Time Series:**
       - Completed evaluations per week/month/year
    """
    logger.info(f"Evaluator dashboard requested by user_id={current_user.id}")

    # Get dashboard data for the current user (as evaluator)
    dashboard = await service.get_evaluator_dashboard(evaluator_id=current_user.id)

    logger.info(f"Evaluator dashboard returned successfully for user_id={current_user.id}")
    return dashboard


@router.get("/evaluator/{evaluator_id}", response_model=EvaluatorDashboardResponse)
async def get_evaluator_dashboard_by_id(
    evaluator_id: int,
    current_user: User = Depends(require_role(UserRole.EDITOR)),
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get dashboard for a specific evaluator (by ID)

    Returns:
    - Manuscript statistics (awaiting, in progress, evaluated)
    - Bar chart data (evaluation status distribution)
    - Time series data (weekly, monthly, yearly completed evaluations)

    Access: EDITOR, SUPER_ADMIN only
    """
    logger.info(f"Evaluator dashboard for evaluator_id={evaluator_id} requested by user_id={current_user.id}")

    # Get dashboard data for the specified evaluator
    dashboard = await service.get_evaluator_dashboard(evaluator_id=evaluator_id)

    logger.info(f"Evaluator dashboard returned successfully for evaluator_id={evaluator_id}")
    return dashboard


# ==================== Generic Dashboard Routes (legacy) ====================

@router.get("/legacy", response_model=DashboardResponse)
async def get_dashboards_legacy(
    current_user: User = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Legacy endpoint - à compléter selon vos besoins
    """
    pass  # À compléter
    # return await service.get_dashboards(skip=skip, limit=limit)
