"""
Pagination utilities
"""
from typing import TypeVar, Generic, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.schemas.base import PaginatedResponse

T = TypeVar("T")


async def paginate(
    db: AsyncSession,
    query,
    skip: int = 0,
    limit: int = 20
) -> dict:
    """
    Generic pagination function for async SQLAlchemy queries.

    Args:
        db: Async database session
        query: SQLAlchemy select query
        skip: Number of items to skip
        limit: Maximum number of items to return

    Returns:
        Dict with items, total, skip, limit, has_more
    """
    # Get total count
    count_query = select(func.count()).select_from(query.alias())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated items
    paginated_query = query.offset(skip).limit(limit)
    result = await db.execute(paginated_query)
    items = result.scalars().all()

    # Check if there are more items
    has_more = (skip + limit) < total

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": has_more
    }
