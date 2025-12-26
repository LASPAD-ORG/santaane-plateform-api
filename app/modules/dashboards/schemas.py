"""
dashboards module - Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from app.schemas.base import TimestampSchema


# ==================== Author Dashboard Schemas ====================

class ManuscriptStatsResponse(BaseModel):
    """Statistics for manuscripts by status"""
    total_submitted: int = Field(description="Nombre total de manuscrits soumis")
    total_rejected: int = Field(description="Nombre total de manuscrits rejetés")
    total_accepted: int = Field(description="Nombre total de manuscrits acceptés")
    total_published: int = Field(description="Nombre total de manuscrits publiés")


class BarChartDataPoint(BaseModel):
    """Single data point for bar chart"""
    label: str = Field(description="Label de la barre (ex: 'Soumis', 'Rejetés', etc.)")
    value: int = Field(description="Valeur numérique")
    color: Optional[str] = Field(default=None, description="Couleur optionnelle (hex)")


class BarChartResponse(BaseModel):
    """Bar chart data for manuscript status distribution"""
    title: str = Field(description="Titre du graphique")
    data: List[BarChartDataPoint] = Field(description="Points de données pour le graphique en barres")


class TimeSeriesDataPoint(BaseModel):
    """Single data point for time series (line chart)"""
    period: str = Field(description="Période (date formatée selon le type)")
    count: int = Field(description="Nombre de soumissions durant cette période")


class TimeSeriesResponse(BaseModel):
    """Time series data for submissions over time"""
    period_type: str = Field(description="Type de période: 'week', 'month', 'year'")
    title: str = Field(description="Titre de la courbe")
    data: List[TimeSeriesDataPoint] = Field(description="Points de données temporelles")


class AuthorDashboardResponse(BaseModel):
    """Complete dashboard response for author"""
    stats: ManuscriptStatsResponse = Field(description="Statistiques générales")
    bar_chart: BarChartResponse = Field(description="Données pour le diagramme en barres")
    weekly_submissions: TimeSeriesResponse = Field(description="Courbe des soumissions par semaine")
    monthly_submissions: TimeSeriesResponse = Field(description="Courbe des soumissions par mois")
    yearly_submissions: TimeSeriesResponse = Field(description="Courbe des soumissions par année")


# ==================== Super Admin Dashboard Schemas ====================

class SystemStatsResponse(BaseModel):
    """System-wide statistics for super admin"""
    # Manuscript stats
    total_manuscripts: int = Field(description="Nombre total de manuscrits")
    in_evaluation: int = Field(description="Nombre de manuscrits en évaluation")
    total_submitted: int = Field(description="Nombre de manuscrits soumis")
    total_rejected: int = Field(description="Nombre de manuscrits rejetés")
    total_accepted: int = Field(description="Nombre de manuscrits acceptés")
    total_published: int = Field(description="Nombre de manuscrits publiés")
    awaiting_evaluators: int = Field(description="Nombre de manuscrits en attente d'évaluateur")

    # User stats
    total_authors: int = Field(description="Nombre total d'auteurs")
    total_editors: int = Field(description="Nombre total d'éditeurs")
    total_evaluators: int = Field(description="Nombre total d'évaluateurs")

    # Rates (calculated fields)
    rejection_rate: float = Field(description="Taux de rejet (%)")
    acceptance_rate: float = Field(description="Taux d'acceptation (%)")
    publication_rate: float = Field(description="Taux de publication (%)")
    evaluation_rate: float = Field(description="Taux d'évaluation (%)")


class CategoryDistributionDataPoint(BaseModel):
    """Data point for category distribution (theme, section, language)"""
    label: str = Field(description="Nom de la catégorie")
    count: int = Field(description="Nombre de manuscrits")


class CategoryDistributionResponse(BaseModel):
    """Category distribution for bar chart"""
    title: str = Field(description="Titre du graphique")
    category_type: str = Field(description="Type de catégorie: 'theme', 'section', 'language'")
    data: List[CategoryDistributionDataPoint] = Field(description="Points de données")


class SuperAdminDashboardResponse(BaseModel):
    """Complete dashboard response for super admin"""
    # Core stats
    stats: SystemStatsResponse = Field(description="Statistiques système complètes")

    # Distribution bar charts
    status_bar_chart: BarChartResponse = Field(description="Répartition par statut")
    theme_bar_chart: CategoryDistributionResponse = Field(description="Soumissions par thème")
    section_bar_chart: CategoryDistributionResponse = Field(description="Soumissions par rubrique")
    language_bar_chart: CategoryDistributionResponse = Field(description="Soumissions par langue")

    # Time series for submissions
    weekly_submissions: TimeSeriesResponse = Field(description="Soumissions par semaine")
    monthly_submissions: TimeSeriesResponse = Field(description="Soumissions par mois")
    yearly_submissions: TimeSeriesResponse = Field(description="Soumissions par année")

    # Time series for authors
    weekly_authors: TimeSeriesResponse = Field(description="Nouveaux auteurs par semaine")
    monthly_authors: TimeSeriesResponse = Field(description="Nouveaux auteurs par mois")
    yearly_authors: TimeSeriesResponse = Field(description="Nouveaux auteurs par année")


# ==================== Evaluator Dashboard Schemas ====================

class EvaluatorStatsResponse(BaseModel):
    """Statistics for evaluator's assigned manuscripts"""
    awaiting_evaluation: int = Field(description="Nombre de manuscrits en attente d'évaluation")
    in_progress: int = Field(description="Nombre de manuscrits en cours d'évaluation")
    evaluated: int = Field(description="Nombre de manuscrits évalués")


class EvaluatorDashboardResponse(BaseModel):
    """Complete dashboard response for evaluator"""
    stats: EvaluatorStatsResponse = Field(description="Statistiques d'évaluation")
    status_bar_chart: BarChartResponse = Field(description="Répartition par statut d'évaluation")
    weekly_evaluations: TimeSeriesResponse = Field(description="Évaluations par semaine")
    monthly_evaluations: TimeSeriesResponse = Field(description="Évaluations par mois")
    yearly_evaluations: TimeSeriesResponse = Field(description="Évaluations par année")


# ==================== Editor Dashboard Schemas ====================

class EditorDashboardResponse(BaseModel):
    """
    Complete dashboard response for editor
    Same structure as SuperAdminDashboardResponse - editors need full system view for editorial management
    """
    # Core stats
    stats: SystemStatsResponse = Field(description="Statistiques système complètes")

    # Distribution bar charts
    status_bar_chart: BarChartResponse = Field(description="Répartition par statut")
    theme_bar_chart: CategoryDistributionResponse = Field(description="Soumissions par thème")
    section_bar_chart: CategoryDistributionResponse = Field(description="Soumissions par rubrique")
    language_bar_chart: CategoryDistributionResponse = Field(description="Soumissions par langue")

    # Time series for submissions
    weekly_submissions: TimeSeriesResponse = Field(description="Soumissions par semaine")
    monthly_submissions: TimeSeriesResponse = Field(description="Soumissions par mois")
    yearly_submissions: TimeSeriesResponse = Field(description="Soumissions par année")

    # Time series for authors
    weekly_authors: TimeSeriesResponse = Field(description="Nouveaux auteurs par semaine")
    monthly_authors: TimeSeriesResponse = Field(description="Nouveaux auteurs par mois")
    yearly_authors: TimeSeriesResponse = Field(description="Nouveaux auteurs par année")


# ==================== Generic Dashboard Schemas (legacy, à supprimer si inutile) ====================

class DashboardCreate(BaseModel):
    """Schema for creating a dashboard"""
    pass  # À compléter - ajouter les champs nécessaires


class DashboardUpdate(BaseModel):
    """Schema for updating a dashboard"""
    pass  # À compléter - tous les champs optionnels


class DashboardResponse(TimestampSchema):
    """Schema for dashboard response"""
    id: int
    pass  # À compléter - ajouter les champs de réponse


class PaginatedDashboardResponse(BaseModel):
    """Paginated dashboard response"""
    items: list[DashboardResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
