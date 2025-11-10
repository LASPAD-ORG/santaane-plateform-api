"""
Auth module - Utility functions
Helper functions and dependencies for authentication module
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db import get_db
from app.modules.auth.repository import AuthRepository
from app.modules.auth.service import AuthService


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Dependency to get auth service instance"""
    repository = AuthRepository(db)
    return AuthService(repository)


def get_default_timezone(country_name: Optional[str] = None, city_name: Optional[str] = None) -> str:
    """
    Get default timezone based on country or city
    Returns UTC as fallback
    """
    # Mapping des pays vers leurs timezones principales
    country_timezones = {
        "Senegal": "Africa/Dakar",
        "France": "Europe/Paris",
        "United States": "America/New_York",
        "Canada": "America/Toronto",
        "United Kingdom": "Europe/London",
        "Germany": "Europe/Berlin",
        "Spain": "Europe/Madrid",
        "Italy": "Europe/Rome",
        "Morocco": "Africa/Casablanca",
        "Algeria": "Africa/Algiers",
        "Tunisia": "Africa/Tunis",
        "Egypt": "Africa/Cairo",
        "South Africa": "Africa/Johannesburg",
        "Nigeria": "Africa/Lagos",
        "Kenya": "Africa/Nairobi",
        "Ghana": "Africa/Accra",
        "Ivory Coast": "Africa/Abidjan",
        "Cameroon": "Africa/Douala",
        "Japan": "Asia/Tokyo",
        "China": "Asia/Shanghai",
        "India": "Asia/Kolkata",
        "Australia": "Australia/Sydney",
        "Brazil": "America/Sao_Paulo",
        "Argentina": "America/Argentina/Buenos_Aires",
        "Mexico": "America/Mexico_City",
    }

    if country_name and country_name in country_timezones:
        return country_timezones[country_name]

    # Fallback à UTC
    return "UTC"
