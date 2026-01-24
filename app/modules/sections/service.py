"""
Section service - Business logic for section operations
"""
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.models.section import Section
from app.modules.sections.schemas import SectionCreate, SectionUpdate


class SectionService:
    """Service class for section operations"""

    @staticmethod
    async def create_section(db: AsyncSession, section_data: SectionCreate) -> Section:
        """Create a new section"""
        section = Section(
            name=section_data.name,
            signe_min=section_data.signe_min,
            signe_max=section_data.signe_max,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(section)
        await db.commit()
        await db.refresh(section)
        return section

    @staticmethod
    async def get_section(db: AsyncSession, section_id: int) -> Optional[Section]:
        """Get a section by ID"""
        result = await db.execute(select(Section).where(Section.id == section_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_sections(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Section]:
        """Get all sections with pagination"""
        result = await db.execute(select(Section).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def update_section(db: AsyncSession, section_id: int, section_data: SectionUpdate) -> Optional[Section]:
        """Update a section"""
        section = await SectionService.get_section(db, section_id)
        if not section:
            return None

        update_data = section_data.model_dump(exclude_unset=True)
        
        # Validate signe_max > signe_min after update
        signe_min = update_data.get('signe_min', section.signe_min)
        signe_max = update_data.get('signe_max', section.signe_max)
        
        if signe_max <= signe_min:
            raise ValueError('signe_max must be greater than signe_min')
        
        for field, value in update_data.items():
            setattr(section, field, value)
        
        section.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(section)
        return section

    @staticmethod
    async def delete_section(db: AsyncSession, section_id: int) -> bool:
        """Delete a section"""
        section = await SectionService.get_section(db, section_id)
        if not section:
            return False

        await db.delete(section)
        await db.commit()
        return True
