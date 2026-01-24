"""
Public module - Pydantic schemas for public API
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List


class PublicAuthorInfo(BaseModel):
    """Public author information"""
    id: int
    fullName: str
    orcidId: Optional[str] = None
    bio: Optional[str] = None
    position: Optional[str] = None
    institution: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class PublicManuscriptSummary(BaseModel):
    """Summary of a published manuscript for list view"""
    id: int
    title: str
    abstract: Optional[str] = None
    keywords: Optional[str] = None
    themeName: Optional[str] = None
    sectionName: str
    languageName: str
    authorName: str
    authorId: int
    publishedAt: Optional[datetime] = None
    createdAt: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PublicManuscriptDetail(BaseModel):
    """Detailed view of a published manuscript"""
    id: int
    title: str
    abstract: Optional[str] = None
    keywords: Optional[str] = None
    themeId: Optional[int] = None
    themeName: Optional[str] = None
    sectionId: int
    sectionName: str
    languageId: int
    languageName: str
    pdfFilename: str
    author: PublicAuthorInfo
    publishedAt: Optional[datetime] = None
    createdAt: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PublicManuscriptListResponse(BaseModel):
    """Response for paginated manuscript list"""
    manuscripts: List[PublicManuscriptSummary]
    total: int
    page: int
    pageSize: int
    totalPages: int


class PublicAuthorDetail(BaseModel):
    """Detailed author profile with their publications"""
    id: int
    fullName: str
    orcidId: Optional[str] = None
    bio: Optional[str] = None
    position: Optional[str] = None
    institution: Optional[str] = None
    publicationsCount: int
    manuscripts: List[PublicManuscriptSummary]
    
    model_config = ConfigDict(from_attributes=True)


class SearchFilters(BaseModel):
    """Search filters for manuscripts"""
    query: Optional[str] = Field(None, description="Search in title, abstract, keywords")
    themeId: Optional[int] = Field(None, description="Filter by theme")
    sectionId: Optional[int] = Field(None, description="Filter by section")
    languageId: Optional[int] = Field(None, description="Filter by language")
    authorId: Optional[int] = Field(None, description="Filter by author")
