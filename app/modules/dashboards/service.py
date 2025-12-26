"""
dashboards module - Business logic service
"""
from fastapi import HTTPException, status
from typing import Dict, List

from app.modules.dashboards.repository import DashboardRepository
from app.modules.dashboards.schemas import (
    DashboardCreate, DashboardUpdate, DashboardResponse, PaginatedDashboardResponse,
    AuthorDashboardResponse, ManuscriptStatsResponse, BarChartResponse, BarChartDataPoint,
    TimeSeriesResponse, TimeSeriesDataPoint,
    SuperAdminDashboardResponse, SystemStatsResponse, CategoryDistributionResponse,
    CategoryDistributionDataPoint,
    EvaluatorDashboardResponse, EvaluatorStatsResponse
)
from app.modules.dashboards.error_codes import DashboardErrorCode
from app.core.logging import get_logger
from app.models.enums import ManuscriptStatus

logger = get_logger(__name__)


class DashboardService:
    """Service for dashboard business logic"""

    def __init__(self, repository: DashboardRepository):
        self.repository = repository

    # ==================== Author Dashboard Methods ====================

    async def get_author_dashboard(self, author_id: int) -> AuthorDashboardResponse:
        """
        Get complete dashboard data for an author
        Includes stats, bar chart, and time series data
        """
        logger.info(f"Building complete dashboard for author_id={author_id}")

        # Get all data in parallel (optimize performance)
        stats_data = await self.repository.get_author_manuscript_stats(author_id)
        distribution_data = await self.repository.get_author_status_distribution(author_id)
        weekly_data = await self.repository.get_author_submissions_by_week(author_id)
        monthly_data = await self.repository.get_author_submissions_by_month(author_id)
        yearly_data = await self.repository.get_author_submissions_by_year(author_id)

        # Build stats response
        stats = ManuscriptStatsResponse(**stats_data)

        # Build bar chart response
        bar_chart = self._build_bar_chart(distribution_data)

        # Build time series responses
        weekly_submissions = TimeSeriesResponse(
            period_type="week",
            title="Soumissions par semaine (12 dernières semaines)",
            data=[TimeSeriesDataPoint(**item) for item in weekly_data]
        )

        monthly_submissions = TimeSeriesResponse(
            period_type="month",
            title="Soumissions par mois (12 derniers mois)",
            data=[TimeSeriesDataPoint(**item) for item in monthly_data]
        )

        yearly_submissions = TimeSeriesResponse(
            period_type="year",
            title="Soumissions par année (5 dernières années)",
            data=[TimeSeriesDataPoint(**item) for item in yearly_data]
        )

        # Build complete response
        dashboard = AuthorDashboardResponse(
            stats=stats,
            bar_chart=bar_chart,
            weekly_submissions=weekly_submissions,
            monthly_submissions=monthly_submissions,
            yearly_submissions=yearly_submissions
        )

        logger.info(f"Dashboard built successfully for author_id={author_id}")
        return dashboard

    def _build_bar_chart(self, distribution: Dict[str, int]) -> BarChartResponse:
        """
        Build bar chart response from status distribution
        Maps status values to French labels and assigns colors
        """
        # Color mapping for each status
        color_map = {
            ManuscriptStatus.SUBMITTED.value: "#3B82F6",  # Blue
            ManuscriptStatus.RE_SUBMITTED.value: "#8B5CF6",  # Purple
            ManuscriptStatus.UNDER_REVIEW.value: "#F59E0B",  # Orange
            ManuscriptStatus.REVISED.value: "#10B981",  # Green
            ManuscriptStatus.ACCEPTED.value: "#22C55E",  # Light Green
            ManuscriptStatus.REJECTED.value: "#EF4444",  # Red
            ManuscriptStatus.REVISION_REQUESTED.value: "#F97316",  # Dark Orange
            ManuscriptStatus.PUBLISHED.value: "#6366F1",  # Indigo
        }

        # Label mapping (English to French)
        label_map = {
            ManuscriptStatus.SUBMITTED.value: "Soumis",
            ManuscriptStatus.RE_SUBMITTED.value: "Re-soumis",
            ManuscriptStatus.UNDER_REVIEW.value: "En révision",
            ManuscriptStatus.REVISED.value: "Révisé",
            ManuscriptStatus.ACCEPTED.value: "Accepté",
            ManuscriptStatus.REJECTED.value: "Rejeté",
            ManuscriptStatus.REVISION_REQUESTED.value: "Révision demandée",
            ManuscriptStatus.PUBLISHED.value: "Publié",
        }

        # Build data points
        data_points = []
        for status_value, count in distribution.items():
            data_points.append(
                BarChartDataPoint(
                    label=label_map.get(status_value, status_value),
                    value=count,
                    color=color_map.get(status_value)
                )
            )

        # Sort by value (descending) for better visualization
        data_points.sort(key=lambda x: x.value, reverse=True)

        return BarChartResponse(
            title="Répartition des manuscrits par statut",
            data=data_points
        )

    # ==================== Super Admin Dashboard Methods ====================

    async def get_super_admin_dashboard(self) -> SuperAdminDashboardResponse:
        """
        Get complete dashboard data for super admin
        Includes system-wide statistics, distributions, and time series
        """
        logger.info("Building complete super admin dashboard")

        # Get all data
        system_stats = await self.repository.get_system_wide_stats()
        user_counts = await self.repository.get_user_counts_by_role()
        awaiting_evaluators = await self.repository.get_manuscripts_awaiting_evaluators()
        status_distribution = await self.repository.get_system_status_distribution()

        # Distribution data
        theme_data = await self.repository.get_submissions_by_theme()
        section_data = await self.repository.get_submissions_by_section()
        language_data = await self.repository.get_submissions_by_language()

        # Time series for submissions
        weekly_submissions_data = await self.repository.get_system_submissions_by_week()
        monthly_submissions_data = await self.repository.get_system_submissions_by_month()
        yearly_submissions_data = await self.repository.get_system_submissions_by_year()

        # Time series for authors
        weekly_authors_data = await self.repository.get_authors_by_week()
        monthly_authors_data = await self.repository.get_authors_by_month()
        yearly_authors_data = await self.repository.get_authors_by_year()

        # Build stats with calculated rates
        stats = self._build_system_stats(system_stats, user_counts, awaiting_evaluators)

        # Build bar charts
        status_bar_chart = self._build_bar_chart(status_distribution)
        theme_bar_chart = self._build_category_distribution(
            "Soumissions par thème",
            "theme",
            theme_data
        )
        section_bar_chart = self._build_category_distribution(
            "Soumissions par rubrique",
            "section",
            section_data
        )
        language_bar_chart = self._build_category_distribution(
            "Soumissions par langue",
            "language",
            language_data
        )

        # Build time series for submissions
        weekly_submissions = TimeSeriesResponse(
            period_type="week",
            title="Soumissions par semaine (12 dernières semaines)",
            data=[TimeSeriesDataPoint(**item) for item in weekly_submissions_data]
        )
        monthly_submissions = TimeSeriesResponse(
            period_type="month",
            title="Soumissions par mois (12 derniers mois)",
            data=[TimeSeriesDataPoint(**item) for item in monthly_submissions_data]
        )
        yearly_submissions = TimeSeriesResponse(
            period_type="year",
            title="Soumissions par année (5 dernières années)",
            data=[TimeSeriesDataPoint(**item) for item in yearly_submissions_data]
        )

        # Build time series for authors
        weekly_authors = TimeSeriesResponse(
            period_type="week",
            title="Nouveaux auteurs par semaine (12 dernières semaines)",
            data=[TimeSeriesDataPoint(**item) for item in weekly_authors_data]
        )
        monthly_authors = TimeSeriesResponse(
            period_type="month",
            title="Nouveaux auteurs par mois (12 derniers mois)",
            data=[TimeSeriesDataPoint(**item) for item in monthly_authors_data]
        )
        yearly_authors = TimeSeriesResponse(
            period_type="year",
            title="Nouveaux auteurs par année (5 dernières années)",
            data=[TimeSeriesDataPoint(**item) for item in yearly_authors_data]
        )

        # Build complete response
        dashboard = SuperAdminDashboardResponse(
            stats=stats,
            status_bar_chart=status_bar_chart,
            theme_bar_chart=theme_bar_chart,
            section_bar_chart=section_bar_chart,
            language_bar_chart=language_bar_chart,
            weekly_submissions=weekly_submissions,
            monthly_submissions=monthly_submissions,
            yearly_submissions=yearly_submissions,
            weekly_authors=weekly_authors,
            monthly_authors=monthly_authors,
            yearly_authors=yearly_authors
        )

        logger.info("Super admin dashboard built successfully")
        return dashboard

    def _build_system_stats(
        self,
        system_stats: Dict,
        user_counts: Dict,
        awaiting_evaluators: int
    ) -> SystemStatsResponse:
        """
        Build system stats with calculated rates
        """
        total_manuscripts = system_stats["total_manuscripts"]

        # Calculate rates (avoid division by zero)
        rejection_rate = (
            (system_stats["total_rejected"] / total_manuscripts * 100)
            if total_manuscripts > 0 else 0.0
        )
        acceptance_rate = (
            (system_stats["total_accepted"] / total_manuscripts * 100)
            if total_manuscripts > 0 else 0.0
        )
        publication_rate = (
            (system_stats["total_published"] / total_manuscripts * 100)
            if total_manuscripts > 0 else 0.0
        )

        # Evaluation rate: manuscripts evaluated vs total manuscripts
        evaluated_count = (
            system_stats["total_accepted"] +
            system_stats["total_rejected"]
        )
        evaluation_rate = (
            (evaluated_count / total_manuscripts * 100)
            if total_manuscripts > 0 else 0.0
        )

        return SystemStatsResponse(
            # Manuscript stats
            total_manuscripts=total_manuscripts,
            in_evaluation=system_stats["in_evaluation"],
            total_submitted=system_stats["total_submitted"],
            total_rejected=system_stats["total_rejected"],
            total_accepted=system_stats["total_accepted"],
            total_published=system_stats["total_published"],
            awaiting_evaluators=awaiting_evaluators,
            # User stats
            total_authors=user_counts["total_authors"],
            total_editors=user_counts["total_editors"],
            total_evaluators=user_counts["total_evaluators"],
            # Rates
            rejection_rate=round(rejection_rate, 2),
            acceptance_rate=round(acceptance_rate, 2),
            publication_rate=round(publication_rate, 2),
            evaluation_rate=round(evaluation_rate, 2)
        )

    def _build_category_distribution(
        self,
        title: str,
        category_type: str,
        data: List[Dict]
    ) -> CategoryDistributionResponse:
        """
        Build category distribution response for bar chart
        """
        data_points = [
            CategoryDistributionDataPoint(
                label=item["label"],
                count=item["count"]
            )
            for item in data
        ]

        return CategoryDistributionResponse(
            title=title,
            category_type=category_type,
            data=data_points
        )

    # ==================== Evaluator Dashboard Methods ====================

    async def get_evaluator_dashboard(self, evaluator_id: int) -> EvaluatorDashboardResponse:
        """
        Get complete dashboard data for an evaluator
        Includes stats, bar chart, and time series for evaluations
        """
        logger.info(f"Building complete dashboard for evaluator_id={evaluator_id}")

        # Get all data
        stats_data = await self.repository.get_evaluator_manuscript_stats(evaluator_id)
        distribution_data = await self.repository.get_evaluator_status_distribution(evaluator_id)
        weekly_data = await self.repository.get_evaluator_evaluations_by_week(evaluator_id)
        monthly_data = await self.repository.get_evaluator_evaluations_by_month(evaluator_id)
        yearly_data = await self.repository.get_evaluator_evaluations_by_year(evaluator_id)

        # Build stats response
        stats = EvaluatorStatsResponse(**stats_data)

        # Build bar chart for evaluation status
        bar_chart = self._build_evaluator_bar_chart(distribution_data)

        # Build time series responses
        weekly_evaluations = TimeSeriesResponse(
            period_type="week",
            title="Évaluations complétées par semaine (12 dernières semaines)",
            data=[TimeSeriesDataPoint(**item) for item in weekly_data]
        )

        monthly_evaluations = TimeSeriesResponse(
            period_type="month",
            title="Évaluations complétées par mois (12 derniers mois)",
            data=[TimeSeriesDataPoint(**item) for item in monthly_data]
        )

        yearly_evaluations = TimeSeriesResponse(
            period_type="year",
            title="Évaluations complétées par année (5 dernières années)",
            data=[TimeSeriesDataPoint(**item) for item in yearly_data]
        )

        # Build complete response
        dashboard = EvaluatorDashboardResponse(
            stats=stats,
            status_bar_chart=bar_chart,
            weekly_evaluations=weekly_evaluations,
            monthly_evaluations=monthly_evaluations,
            yearly_evaluations=yearly_evaluations
        )

        logger.info(f"Dashboard built successfully for evaluator_id={evaluator_id}")
        return dashboard

    def _build_evaluator_bar_chart(self, distribution: Dict[str, int]) -> BarChartResponse:
        """
        Build bar chart response from evaluation status distribution
        Maps status values to French labels and assigns colors
        """
        # Color mapping for evaluation status
        color_map = {
            "awaiting_evaluation": "#F59E0B",  # Orange - waiting
            "in_progress": "#3B82F6",  # Blue - in progress
            "evaluated": "#22C55E"  # Green - completed
        }

        # Label mapping (English to French)
        label_map = {
            "awaiting_evaluation": "En attente",
            "in_progress": "En cours",
            "evaluated": "Évalués"
        }

        # Build data points
        data_points = []
        for status_key, count in distribution.items():
            data_points.append(
                BarChartDataPoint(
                    label=label_map.get(status_key, status_key),
                    value=count,
                    color=color_map.get(status_key)
                )
            )

        # Sort by status order: awaiting, in_progress, evaluated
        order = ["awaiting_evaluation", "in_progress", "evaluated"]
        data_points.sort(key=lambda x: order.index(
            next((k for k, v in label_map.items() if v == x.label), "")
        ))

        return BarChartResponse(
            title="Répartition des manuscrits par statut d'évaluation",
            data=data_points
        )

    # ==================== Generic Dashboard Methods (legacy) ====================

    async def get_dashboards(self, skip: int = 0, limit: int = 20) -> PaginatedDashboardResponse:
        """Get all dashboards with pagination"""
        logger.info(f"Fetching dashboards (skip={skip}, limit={limit})")
        pass  # À compléter
        # result = await self.repository.get_all(skip=skip, limit=limit)
        # return PaginatedDashboardResponse(**result)

    async def get_dashboard_by_id(self, dashboard_id: int) -> DashboardResponse:
        """Get dashboard by ID"""
        logger.info(f"Fetching dashboard ID: {dashboard_id}")
        pass  # À compléter
        # dashboard = await self.repository.get_by_id(dashboard_id)
        # if not dashboard:
        #     logger.warning(f"Dashboard not found: ID {dashboard_id}")
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=DashboardErrorCode.DASHBOARD_NOT_FOUND
        #     )
        # return DashboardResponse.model_validate(dashboard)

    async def create_dashboard(self, dashboard_data: DashboardCreate) -> DashboardResponse:
        """Create a new dashboard"""
        logger.info(f"Creating dashboard")
        pass  # À compléter
        # dashboard = await self.repository.create(dashboard_data.model_dump())
        # logger.info(f"Dashboard created: {dashboard.id}")
        # return DashboardResponse.model_validate(dashboard)

    async def update_dashboard(self, dashboard_id: int, dashboard_data: DashboardUpdate) -> DashboardResponse:
        """Update a dashboard"""
        logger.info(f"Updating dashboard ID: {dashboard_id}")
        pass  # À compléter

    async def delete_dashboard(self, dashboard_id: int) -> None:
        """Delete a dashboard"""
        logger.info(f"Deleting dashboard ID: {dashboard_id}")
        pass  # À compléter
