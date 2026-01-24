"""
dashboards module - Database repository
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Dict, List
from datetime import datetime, timedelta, timezone

from app.core.logging import get_logger
from app.models.manuscript import Manuscript
from app.models.enums import ManuscriptStatus

logger = get_logger(__name__)


class DashboardRepository:
    """Repository for dashboard database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== Author Dashboard Methods ====================

    async def get_author_manuscript_stats(self, author_id: int) -> Dict[str, int]:
        """
        Get manuscript statistics for an author
        Returns counts for: submitted, rejected, accepted, published
        """
        logger.info(f"Fetching manuscript stats for author_id={author_id}")

        # Count total submitted (all manuscripts by this author)
        total_submitted_query = select(func.count()).select_from(Manuscript).where(
            Manuscript.author_id == author_id
        )
        total_submitted = await self.db.scalar(total_submitted_query) or 0

        # Count rejected
        total_rejected_query = select(func.count()).select_from(Manuscript).where(
            and_(
                Manuscript.author_id == author_id,
                Manuscript.status == ManuscriptStatus.REJECTED
            )
        )
        total_rejected = await self.db.scalar(total_rejected_query) or 0

        # Count accepted
        total_accepted_query = select(func.count()).select_from(Manuscript).where(
            and_(
                Manuscript.author_id == author_id,
                Manuscript.status == ManuscriptStatus.ACCEPTED
            )
        )
        total_accepted = await self.db.scalar(total_accepted_query) or 0

        # Count published
        total_published_query = select(func.count()).select_from(Manuscript).where(
            and_(
                Manuscript.author_id == author_id,
                Manuscript.status == ManuscriptStatus.PUBLISHED
            )
        )
        total_published = await self.db.scalar(total_published_query) or 0

        return {
            "total_submitted": total_submitted,
            "total_rejected": total_rejected,
            "total_accepted": total_accepted,
            "total_published": total_published
        }

    async def get_author_status_distribution(self, author_id: int) -> Dict[str, int]:
        """
        Get manuscript count by status for bar chart
        Returns a dictionary with all status counts
        """
        logger.info(f"Fetching status distribution for author_id={author_id}")

        # Get all manuscripts grouped by status
        query = select(
            Manuscript.status,
            func.count(Manuscript.id).label('count')
        ).where(
            Manuscript.author_id == author_id
        ).group_by(Manuscript.status)

        result = await self.db.execute(query)
        rows = result.all()

        # Convert to dictionary
        distribution = {row.status.value: row.count for row in rows}

        logger.info(f"Status distribution: {distribution}")
        return distribution

    async def get_author_submissions_by_week(self, author_id: int, weeks: int = 12) -> List[Dict]:
        """
        Get submission count by week for the last N weeks
        Returns list of {period, count}
        """
        logger.info(f"Fetching weekly submissions for author_id={author_id}, last {weeks} weeks")

        # Calculate start date (N weeks ago)
        start_date = datetime.utcnow() - timedelta(weeks=weeks)

        # PostgreSQL-specific: extract year and week
        query = select(
            func.date_trunc('week', Manuscript.created_at).label('week_start'),
            func.count(Manuscript.id).label('count')
        ).where(
            and_(
                Manuscript.author_id == author_id,
                Manuscript.created_at >= start_date
            )
        ).group_by('week_start').order_by('week_start')

        result = await self.db.execute(query)
        rows = result.all()

        # Format results
        submissions = []
        for row in rows:
            submissions.append({
                "period": row.week_start.strftime("%Y-W%W"),  # Format: 2024-W52
                "count": row.count
            })

        logger.info(f"Found {len(submissions)} weeks with submissions")
        return submissions

    async def get_author_submissions_by_month(self, author_id: int, months: int = 12) -> List[Dict]:
        """
        Get submission count by month for the last N months
        Returns list of {period, count}
        """
        logger.info(f"Fetching monthly submissions for author_id={author_id}, last {months} months")

        # Calculate start date (N months ago)
        start_date = datetime.utcnow() - timedelta(days=months * 30)

        # PostgreSQL-specific: date_trunc to month
        query = select(
            func.date_trunc('month', Manuscript.created_at).label('month_start'),
            func.count(Manuscript.id).label('count')
        ).where(
            and_(
                Manuscript.author_id == author_id,
                Manuscript.created_at >= start_date
            )
        ).group_by('month_start').order_by('month_start')

        result = await self.db.execute(query)
        rows = result.all()

        # Format results
        submissions = []
        for row in rows:
            submissions.append({
                "period": row.month_start.strftime("%Y-%m"),  # Format: 2024-12
                "count": row.count
            })

        logger.info(f"Found {len(submissions)} months with submissions")
        return submissions

    async def get_author_submissions_by_year(self, author_id: int, years: int = 5) -> List[Dict]:
        """
        Get submission count by year for the last N years
        Returns list of {period, count}
        """
        logger.info(f"Fetching yearly submissions for author_id={author_id}, last {years} years")

        # Calculate start date (N years ago)
        start_date = datetime.utcnow() - timedelta(days=years * 365)

        # PostgreSQL-specific: extract year
        query = select(
            func.date_trunc('year', Manuscript.created_at).label('year_start'),
            func.count(Manuscript.id).label('count')
        ).where(
            and_(
                Manuscript.author_id == author_id,
                Manuscript.created_at >= start_date
            )
        ).group_by('year_start').order_by('year_start')

        result = await self.db.execute(query)
        rows = result.all()

        # Format results
        submissions = []
        for row in rows:
            submissions.append({
                "period": row.year_start.strftime("%Y"),  # Format: 2024
                "count": row.count
            })

        logger.info(f"Found {len(submissions)} years with submissions")
        return submissions

    # ==================== Super Admin Dashboard Methods ====================

    async def get_system_wide_stats(self) -> Dict[str, int]:
        """
        Get system-wide statistics for super admin
        Returns manuscript counts, user counts, and rates
        """
        logger.info("Fetching system-wide statistics")

        # Total manuscripts
        total_manuscripts_query = select(func.count()).select_from(Manuscript)
        total_manuscripts = await self.db.scalar(total_manuscripts_query) or 0

        # Manuscripts in evaluation (UNDER_REVIEW)
        in_evaluation_query = select(func.count()).select_from(Manuscript).where(
            Manuscript.status == ManuscriptStatus.UNDER_REVIEW
        )
        in_evaluation = await self.db.scalar(in_evaluation_query) or 0

        # Manuscripts submitted (all submitted statuses)
        submitted_query = select(func.count()).select_from(Manuscript).where(
            Manuscript.status.in_([
                ManuscriptStatus.SUBMITTED,
                ManuscriptStatus.RE_SUBMITTED
            ])
        )
        total_submitted = await self.db.scalar(submitted_query) or 0

        # Manuscripts rejected
        rejected_query = select(func.count()).select_from(Manuscript).where(
            Manuscript.status == ManuscriptStatus.REJECTED
        )
        total_rejected = await self.db.scalar(rejected_query) or 0

        # Manuscripts accepted
        accepted_query = select(func.count()).select_from(Manuscript).where(
            Manuscript.status == ManuscriptStatus.ACCEPTED
        )
        total_accepted = await self.db.scalar(accepted_query) or 0

        # Manuscripts published
        published_query = select(func.count()).select_from(Manuscript).where(
            Manuscript.status == ManuscriptStatus.PUBLISHED
        )
        total_published = await self.db.scalar(published_query) or 0

        return {
            "total_manuscripts": total_manuscripts,
            "in_evaluation": in_evaluation,
            "total_submitted": total_submitted,
            "total_rejected": total_rejected,
            "total_accepted": total_accepted,
            "total_published": total_published
        }

    async def get_user_counts_by_role(self) -> Dict[str, int]:
        """
        Get count of users by role (authors, editors, evaluators)
        """
        from app.models.user import User
        from app.models.user_role import UserRole
        from app.models.role import Role

        logger.info("Fetching user counts by role")

        # Count distinct authors (users who have submitted manuscripts)
        authors_query = select(func.count(func.distinct(Manuscript.author_id))).select_from(Manuscript)
        total_authors = await self.db.scalar(authors_query) or 0

        # Count editors (users with EDITOR role)
        editors_query = select(func.count(func.distinct(UserRole.user_id))).select_from(UserRole).join(
            Role, UserRole.role_id == Role.id
        ).where(Role.name == "EDITOR")
        total_editors = await self.db.scalar(editors_query) or 0

        # Count evaluators (users with EVALUATOR role)
        evaluators_query = select(func.count(func.distinct(UserRole.user_id))).select_from(UserRole).join(
            Role, UserRole.role_id == Role.id
        ).where(Role.name == "EVALUATOR")
        total_evaluators = await self.db.scalar(evaluators_query) or 0

        return {
            "total_authors": total_authors,
            "total_editors": total_editors,
            "total_evaluators": total_evaluators
        }

    async def get_manuscripts_awaiting_evaluators(self) -> int:
        """
        Get count of manuscripts awaiting evaluator assignment
        """
        from app.models.manuscript_evaluator_link import ManuscriptEvaluatorLink
        from app.models.enums import ManuscriptEvaluationStatus

        logger.info("Fetching manuscripts awaiting evaluators")

        # Manuscripts with evaluation_status PENDING (no evaluators assigned yet)
        query = select(func.count()).select_from(Manuscript).where(
            Manuscript.evaluation_status == ManuscriptEvaluationStatus.PENDING
        )
        count = await self.db.scalar(query) or 0

        return count

    async def get_submissions_by_theme(self) -> List[Dict]:
        """
        Get manuscript count grouped by theme for bar chart
        """
        from app.models.theme import Theme

        logger.info("Fetching submissions by theme")

        query = select(
            Theme.title,
            func.count(Manuscript.id).label('count')
        ).join(
            Manuscript, Manuscript.theme_id == Theme.id, isouter=True
        ).group_by(Theme.id, Theme.title).order_by(func.count(Manuscript.id).desc())

        result = await self.db.execute(query)
        rows = result.all()

        submissions = []
        for row in rows:
            submissions.append({
                "label": row.title,
                "count": row.count
            })

        logger.info(f"Found {len(submissions)} themes")
        return submissions

    async def get_submissions_by_section(self) -> List[Dict]:
        """
        Get manuscript count grouped by section (rubrique) for bar chart
        """
        from app.models.section import Section

        logger.info("Fetching submissions by section")

        query = select(
            Section.name,
            func.count(Manuscript.id).label('count')
        ).join(
            Manuscript, Manuscript.section_id == Section.id
        ).group_by(Section.id, Section.name).order_by(func.count(Manuscript.id).desc())

        result = await self.db.execute(query)
        rows = result.all()

        submissions = []
        for row in rows:
            submissions.append({
                "label": row.name,
                "count": row.count
            })

        logger.info(f"Found {len(submissions)} sections")
        return submissions

    async def get_submissions_by_language(self) -> List[Dict]:
        """
        Get manuscript count grouped by language for bar chart
        """
        from app.models.language import Language

        logger.info("Fetching submissions by language")

        query = select(
            Language.name,
            func.count(Manuscript.id).label('count')
        ).join(
            Manuscript, Manuscript.language_id == Language.id
        ).group_by(Language.id, Language.name).order_by(func.count(Manuscript.id).desc())

        result = await self.db.execute(query)
        rows = result.all()

        submissions = []
        for row in rows:
            submissions.append({
                "label": row.name,
                "count": row.count
            })

        logger.info(f"Found {len(submissions)} languages")
        return submissions

    async def get_system_status_distribution(self) -> Dict[str, int]:
        """
        Get manuscript count by status for the entire system
        """
        logger.info("Fetching system-wide status distribution")

        query = select(
            Manuscript.status,
            func.count(Manuscript.id).label('count')
        ).group_by(Manuscript.status)

        result = await self.db.execute(query)
        rows = result.all()

        distribution = {row.status.value: row.count for row in rows}

        logger.info(f"Status distribution: {distribution}")
        return distribution

    async def get_system_submissions_by_week(self, weeks: int = 12) -> List[Dict]:
        """
        Get submission count by week for the entire system
        """
        logger.info(f"Fetching system-wide weekly submissions, last {weeks} weeks")

        start_date = datetime.utcnow() - timedelta(weeks=weeks)

        query = select(
            func.date_trunc('week', Manuscript.created_at).label('week_start'),
            func.count(Manuscript.id).label('count')
        ).where(
            Manuscript.created_at >= start_date
        ).group_by('week_start').order_by('week_start')

        result = await self.db.execute(query)
        rows = result.all()

        submissions = []
        for row in rows:
            submissions.append({
                "period": row.week_start.strftime("%Y-W%W"),
                "count": row.count
            })

        logger.info(f"Found {len(submissions)} weeks with submissions")
        return submissions

    async def get_system_submissions_by_month(self, months: int = 12) -> List[Dict]:
        """
        Get submission count by month for the entire system
        """
        logger.info(f"Fetching system-wide monthly submissions, last {months} months")

        start_date = datetime.utcnow() - timedelta(days=months * 30)

        query = select(
            func.date_trunc('month', Manuscript.created_at).label('month_start'),
            func.count(Manuscript.id).label('count')
        ).where(
            Manuscript.created_at >= start_date
        ).group_by('month_start').order_by('month_start')

        result = await self.db.execute(query)
        rows = result.all()

        submissions = []
        for row in rows:
            submissions.append({
                "period": row.month_start.strftime("%Y-%m"),
                "count": row.count
            })

        logger.info(f"Found {len(submissions)} months with submissions")
        return submissions

    async def get_system_submissions_by_year(self, years: int = 5) -> List[Dict]:
        """
        Get submission count by year for the entire system
        """
        logger.info(f"Fetching system-wide yearly submissions, last {years} years")

        start_date = datetime.utcnow() - timedelta(days=years * 365)

        query = select(
            func.date_trunc('year', Manuscript.created_at).label('year_start'),
            func.count(Manuscript.id).label('count')
        ).where(
            Manuscript.created_at >= start_date
        ).group_by('year_start').order_by('year_start')

        result = await self.db.execute(query)
        rows = result.all()

        submissions = []
        for row in rows:
            submissions.append({
                "period": row.year_start.strftime("%Y"),
                "count": row.count
            })

        logger.info(f"Found {len(submissions)} years with submissions")
        return submissions

    async def get_authors_by_week(self, weeks: int = 12) -> List[Dict]:
        """
        Get new author count by week (users who submitted their first manuscript)
        """
        from app.models.user import User

        logger.info(f"Fetching new authors by week, last {weeks} weeks")

        start_date = datetime.utcnow() - timedelta(weeks=weeks)

        # Get earliest submission date for each author who joined in the period
        query = select(
            func.date_trunc('week', func.min(Manuscript.created_at)).label('week_start'),
            func.count(func.distinct(Manuscript.author_id)).label('count')
        ).where(
            Manuscript.created_at >= start_date
        ).group_by(
            func.date_trunc('week', Manuscript.created_at)
        ).order_by('week_start')

        result = await self.db.execute(query)
        rows = result.all()

        authors = []
        for row in rows:
            authors.append({
                "period": row.week_start.strftime("%Y-W%W"),
                "count": row.count
            })

        logger.info(f"Found {len(authors)} weeks with new authors")
        return authors

    async def get_authors_by_month(self, months: int = 12) -> List[Dict]:
        """
        Get new author count by month
        """
        logger.info(f"Fetching new authors by month, last {months} months")

        start_date = datetime.utcnow() - timedelta(days=months * 30)

        query = select(
            func.date_trunc('month', func.min(Manuscript.created_at)).label('month_start'),
            func.count(func.distinct(Manuscript.author_id)).label('count')
        ).where(
            Manuscript.created_at >= start_date
        ).group_by(
            func.date_trunc('month', Manuscript.created_at)
        ).order_by('month_start')

        result = await self.db.execute(query)
        rows = result.all()

        authors = []
        for row in rows:
            authors.append({
                "period": row.month_start.strftime("%Y-%m"),
                "count": row.count
            })

        logger.info(f"Found {len(authors)} months with new authors")
        return authors

    async def get_authors_by_year(self, years: int = 5) -> List[Dict]:
        """
        Get new author count by year
        """
        logger.info(f"Fetching new authors by year, last {years} years")

        start_date = datetime.utcnow() - timedelta(days=years * 365)

        query = select(
            func.date_trunc('year', func.min(Manuscript.created_at)).label('year_start'),
            func.count(func.distinct(Manuscript.author_id)).label('count')
        ).where(
            Manuscript.created_at >= start_date
        ).group_by(
            func.date_trunc('year', Manuscript.created_at)
        ).order_by('year_start')

        result = await self.db.execute(query)
        rows = result.all()

        authors = []
        for row in rows:
            authors.append({
                "period": row.year_start.strftime("%Y"),
                "count": row.count
            })

        logger.info(f"Found {len(authors)} years with new authors")
        return authors

    # ==================== Evaluator Dashboard Methods ====================

    async def get_evaluator_manuscript_stats(self, evaluator_id: int) -> Dict[str, int]:
        """
        Get manuscript statistics for an evaluator
        Returns counts for: awaiting, in_progress, evaluated
        """
        from app.models.manuscript_evaluator_link import ManuscriptEvaluatorLink
        from app.models.manuscript_evaluation_grid import ManuscriptEvaluationGrid
        from app.models.enums import EvaluatorAssignmentStatus

        logger.info(f"Fetching manuscript stats for evaluator_id={evaluator_id}")

        # Get all manuscripts assigned to this evaluator with ACCEPTED status
        assigned_query = select(ManuscriptEvaluatorLink).where(
            and_(
                ManuscriptEvaluatorLink.evaluator_id == evaluator_id,
                ManuscriptEvaluatorLink.status == EvaluatorAssignmentStatus.ACCEPTED
            )
        )
        result = await self.db.execute(assigned_query)
        assigned_links = result.scalars().all()

        awaiting = 0
        in_progress = 0
        evaluated = 0

        for link in assigned_links:
            # Check if evaluation grid exists
            grid_query = select(ManuscriptEvaluationGrid).where(
                and_(
                    ManuscriptEvaluationGrid.manuscript_id == link.manuscript_id,
                    ManuscriptEvaluationGrid.evaluator_id == evaluator_id
                )
            )
            grid_result = await self.db.execute(grid_query)
            grid = grid_result.scalar_one_or_none()

            if grid is None:
                # No grid created yet - awaiting evaluation
                awaiting += 1
            elif grid.submitted_at is None:
                # Grid exists but not submitted - in progress
                in_progress += 1
            else:
                # Grid submitted - evaluated
                evaluated += 1

        return {
            "awaiting_evaluation": awaiting,
            "in_progress": in_progress,
            "evaluated": evaluated
        }

    async def get_evaluator_status_distribution(self, evaluator_id: int) -> Dict[str, int]:
        """
        Get manuscript count by evaluation status for bar chart
        Returns a dictionary with awaiting, in_progress, evaluated counts
        """
        logger.info(f"Fetching status distribution for evaluator_id={evaluator_id}")

        stats = await self.get_evaluator_manuscript_stats(evaluator_id)

        return {
            "awaiting_evaluation": stats["awaiting_evaluation"],
            "in_progress": stats["in_progress"],
            "evaluated": stats["evaluated"]
        }

    async def get_evaluator_evaluations_by_week(self, evaluator_id: int, weeks: int = 12) -> List[Dict]:
        """
        Get evaluation completion count by week for the last N weeks
        Returns list of {period, count}
        """
        from app.models.manuscript_evaluation_grid import ManuscriptEvaluationGrid

        logger.info(f"Fetching weekly evaluations for evaluator_id={evaluator_id}, last {weeks} weeks")

        start_date = datetime.utcnow() - timedelta(weeks=weeks)

        # Count evaluations submitted per week
        query = select(
            func.date_trunc('week', ManuscriptEvaluationGrid.submitted_at).label('week_start'),
            func.count(ManuscriptEvaluationGrid.id).label('count')
        ).where(
            and_(
                ManuscriptEvaluationGrid.evaluator_id == evaluator_id,
                ManuscriptEvaluationGrid.submitted_at.isnot(None),
                ManuscriptEvaluationGrid.submitted_at >= start_date
            )
        ).group_by('week_start').order_by('week_start')

        result = await self.db.execute(query)
        rows = result.all()

        evaluations = []
        for row in rows:
            evaluations.append({
                "period": row.week_start.strftime("%Y-W%W"),
                "count": row.count
            })

        logger.info(f"Found {len(evaluations)} weeks with evaluations")
        return evaluations

    async def get_evaluator_evaluations_by_month(self, evaluator_id: int, months: int = 12) -> List[Dict]:
        """
        Get evaluation completion count by month for the last N months
        Returns list of {period, count}
        """
        from app.models.manuscript_evaluation_grid import ManuscriptEvaluationGrid

        logger.info(f"Fetching monthly evaluations for evaluator_id={evaluator_id}, last {months} months")

        start_date = datetime.utcnow() - timedelta(days=months * 30)

        # Count evaluations submitted per month
        query = select(
            func.date_trunc('month', ManuscriptEvaluationGrid.submitted_at).label('month_start'),
            func.count(ManuscriptEvaluationGrid.id).label('count')
        ).where(
            and_(
                ManuscriptEvaluationGrid.evaluator_id == evaluator_id,
                ManuscriptEvaluationGrid.submitted_at.isnot(None),
                ManuscriptEvaluationGrid.submitted_at >= start_date
            )
        ).group_by('month_start').order_by('month_start')

        result = await self.db.execute(query)
        rows = result.all()

        evaluations = []
        for row in rows:
            evaluations.append({
                "period": row.month_start.strftime("%Y-%m"),
                "count": row.count
            })

        logger.info(f"Found {len(evaluations)} months with evaluations")
        return evaluations

    async def get_evaluator_evaluations_by_year(self, evaluator_id: int, years: int = 5) -> List[Dict]:
        """
        Get evaluation completion count by year for the last N years
        Returns list of {period, count}
        """
        from app.models.manuscript_evaluation_grid import ManuscriptEvaluationGrid

        logger.info(f"Fetching yearly evaluations for evaluator_id={evaluator_id}, last {years} years")

        start_date = datetime.utcnow() - timedelta(days=years * 365)

        # Count evaluations submitted per year
        query = select(
            func.date_trunc('year', ManuscriptEvaluationGrid.submitted_at).label('year_start'),
            func.count(ManuscriptEvaluationGrid.id).label('count')
        ).where(
            and_(
                ManuscriptEvaluationGrid.evaluator_id == evaluator_id,
                ManuscriptEvaluationGrid.submitted_at.isnot(None),
                ManuscriptEvaluationGrid.submitted_at >= start_date
            )
        ).group_by('year_start').order_by('year_start')

        result = await self.db.execute(query)
        rows = result.all()

        evaluations = []
        for row in rows:
            evaluations.append({
                "period": row.year_start.strftime("%Y"),
                "count": row.count
            })

        logger.info(f"Found {len(evaluations)} years with evaluations")
        return evaluations
