"""
dashboards module - Utility functions
Helper functions and dependencies for dashboards module
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.modules.dashboards.repository import DashboardRepository
from app.modules.dashboards.service import DashboardService


def get_dashboard_service(db: AsyncSession = Depends(get_db)) -> DashboardService:
    """Dependency to get dashboard service instance"""
    repository = DashboardRepository(db)
    return DashboardService(repository)
