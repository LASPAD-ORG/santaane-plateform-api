"""
API routes for manuscript version history (read-only).

Expose l'historique des versions archivees + leurs evaluations (grilles + annotations).
Lecture seule. L'anonymisation des evaluateurs est geree cote frontend (comme pour les
evaluations vivantes), donc on renvoie evaluator_id + evaluator_kind bruts.
"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from pydantic import BaseModel

from app.db import get_db
from app.core.permissions import get_current_user
from app.core.roles import UserRole
from app.modules.auth.repository import AuthRepository
from app.models.user import User
from app.models.manuscript import Manuscript
from app.models.manuscript_version import ManuscriptVersion
from app.models.archived_evaluation_grid import ArchivedEvaluationGrid
from app.models.archived_annotation import ArchivedAnnotation
from app.models.manuscript_evaluator_link import ManuscriptEvaluatorLink

router = APIRouter(prefix="/manuscripts", tags=["Manuscript Versions"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class VersionResponse(BaseModel):
    id: int
    manuscriptId: int
    versionNumber: int
    pdfFilename: str
    docxFilename: Optional[str] = None
    initialDocxFilename: Optional[str] = None
    title: str
    abstract: Optional[str] = None
    keywords: Optional[str] = None
    createdAt: datetime
    archivedAt: datetime


class ArchivedGridResponse(BaseModel):
    id: int
    versionId: int
    evaluatorId: int
    evaluatorKind: Optional[str] = None
    originalityOfIdeas: Optional[str] = None
    methodologyRigor: Optional[str] = None
    theoreticalApproach: Optional[str] = None
    presentationClarity: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    suggestions: Optional[str] = None
    editorialLineFit: Optional[str] = None
    globalOpinion: Optional[str] = None
    recommendation: Optional[str] = None
    submittedAt: Optional[datetime] = None


class ArchivedAnnotationResponse(BaseModel):
    id: int
    versionId: int
    evaluatorId: int
    evaluatorKind: Optional[str] = None
    annotationType: Optional[str] = None
    createdByRole: Optional[str] = None
    pageNumber: Optional[int] = None
    xPosition: Optional[float] = None
    yPosition: Optional[float] = None
    positionData: Optional[str] = None
    comment: Optional[str] = None
    contentData: Optional[str] = None
    createdAt: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_manuscript_or_404(db: AsyncSession, manuscript_id: int) -> Manuscript:
    manuscript = await db.get(Manuscript, manuscript_id)
    if manuscript is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manuscrit introuvable")
    return manuscript


async def _verify_access(db: AsyncSession, user: User, manuscript: Manuscript) -> None:
    """Editeur/super-admin, auteur proprietaire, ou evaluateur assigne."""
    repo = AuthRepository(db)
    roles = await repo.get_user_roles(user.id)
    if UserRole.SUPER_ADMIN.value in roles or UserRole.EDITOR.value in roles:
        return
    if manuscript.author_id == user.id:
        return
    # Evaluateur assigne a ce manuscrit ?
    result = await db.execute(
        select(ManuscriptEvaluatorLink).where(
            ManuscriptEvaluatorLink.manuscript_id == manuscript.id,
            ManuscriptEvaluatorLink.evaluator_id == user.id,
        )
    )
    if result.scalars().first() is not None:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acces non autorise a ce manuscrit")


async def _get_version_or_404(db: AsyncSession, manuscript_id: int, version_id: int) -> ManuscriptVersion:
    version = await db.get(ManuscriptVersion, version_id)
    if version is None or version.manuscript_id != manuscript_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version introuvable")
    return version


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get(
    "/{manuscript_id}/versions",
    response_model=List[VersionResponse],
    summary="List archived versions of a manuscript",
)
async def list_versions(
    manuscript_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    manuscript = await _get_manuscript_or_404(db, manuscript_id)
    await _verify_access(db, current_user, manuscript)

    result = await db.execute(
        select(ManuscriptVersion)
        .where(ManuscriptVersion.manuscript_id == manuscript_id)
    )
    versions = result.scalars().all()
    versions = sorted(versions, key=lambda v: v.version_number, reverse=True)
    return [
        VersionResponse(
            id=v.id,
            manuscriptId=v.manuscript_id,
            versionNumber=v.version_number,
            pdfFilename=v.pdf_filename,
            docxFilename=v.docx_filename,
            initialDocxFilename=v.initial_docx_filename,
            title=v.title,
            abstract=v.abstract,
            keywords=v.keywords,
            createdAt=v.created_at,
            archivedAt=v.archived_at,
        )
        for v in versions
    ]


@router.get(
    "/{manuscript_id}/versions/{version_id}/grids",
    response_model=List[ArchivedGridResponse],
    summary="List archived evaluation grids of a version",
)
async def list_version_grids(
    manuscript_id: int,
    version_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    manuscript = await _get_manuscript_or_404(db, manuscript_id)
    await _verify_access(db, current_user, manuscript)
    await _get_version_or_404(db, manuscript_id, version_id)

    result = await db.execute(
        select(ArchivedEvaluationGrid)
        .where(ArchivedEvaluationGrid.version_id == version_id)
    )
    grids = result.scalars().all()
    return [
        ArchivedGridResponse(
            id=g.id,
            versionId=g.version_id,
            evaluatorId=g.evaluator_id,
            evaluatorKind=g.evaluator_kind,
            originalityOfIdeas=g.originality_of_ideas,
            methodologyRigor=g.methodology_rigor,
            theoreticalApproach=g.theoretical_approach,
            presentationClarity=g.presentation_clarity,
            strengths=g.strengths,
            weaknesses=g.weaknesses,
            suggestions=g.suggestions,
            editorialLineFit=g.editorial_line_fit,
            globalOpinion=g.global_opinion,
            recommendation=g.recommendation,
            submittedAt=g.original_submitted_at,
        )
        for g in grids
    ]


@router.get(
    "/{manuscript_id}/versions/{version_id}/annotations",
    response_model=List[ArchivedAnnotationResponse],
    summary="List archived annotations of a version",
)
async def list_version_annotations(
    manuscript_id: int,
    version_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    manuscript = await _get_manuscript_or_404(db, manuscript_id)
    await _verify_access(db, current_user, manuscript)
    await _get_version_or_404(db, manuscript_id, version_id)

    result = await db.execute(
        select(ArchivedAnnotation)
        .where(ArchivedAnnotation.version_id == version_id)
    )
    annotations = result.scalars().all()
    return [
        ArchivedAnnotationResponse(
            id=a.id,
            versionId=a.version_id,
            evaluatorId=a.evaluator_id,
            evaluatorKind=a.evaluator_kind,
            annotationType=a.annotation_type,
            createdByRole=a.created_by_role,
            pageNumber=a.page_number,
            xPosition=a.x_position,
            yPosition=a.y_position,
            positionData=a.position_data,
            comment=a.comment,
            contentData=a.content_data,
            createdAt=a.original_created_at,
        )
        for a in annotations
    ]