"""
Service d'archivage de versions de manuscrit.

Brique isolee (V2) : cree une ManuscriptVersion a partir de l'etat courant d'un manuscrit
et y copie les grilles + annotations vivantes dans les tables d'archive.
Appelee lors d'une revision (V3), AVANT que les fichiers du manuscrit soient ecrases.
"""
from typing import Optional
from datetime import datetime

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.logging import get_logger
from fastapi import HTTPException, status
from sqlalchemy import delete
from app.models.enums import ManuscriptStatus, ManuscriptEvaluationStatus
from app.models.manuscript import Manuscript
from app.models.manuscript_version import ManuscriptVersion
from app.models.manuscript_evaluation_grid import ManuscriptEvaluationGrid
from app.models.manuscript_annotation import ManuscriptAnnotation
from app.models.manuscript_evaluator_link import ManuscriptEvaluatorLink
from app.models.archived_evaluation_grid import ArchivedEvaluationGrid
from app.models.archived_annotation import ArchivedAnnotation

logger = get_logger(__name__)


async def _next_version_number(db: AsyncSession, manuscript_id: int) -> int:
    """Retourne le prochain numero de version (max existant + 1, ou 1)."""
    result = await db.execute(
        select(ManuscriptVersion.version_number)
        .where(ManuscriptVersion.manuscript_id == manuscript_id)
    )
    numbers = [row for row in result.scalars().all()]
    return (max(numbers) + 1) if numbers else 1


async def _build_kind_map(db: AsyncSession, manuscript_id: int) -> dict:
    """Map evaluator_id -> kind ('internal'/'external') pour ce manuscrit."""
    result = await db.execute(
        select(ManuscriptEvaluatorLink)
        .where(ManuscriptEvaluatorLink.manuscript_id == manuscript_id)
    )
    links = result.scalars().all()
    return {link.evaluator_id: link.kind for link in links}


async def archive_current_version(
    db: AsyncSession,
    manuscript: Manuscript,
) -> ManuscriptVersion:
    """
    Archive l'etat courant d'un manuscrit dans une nouvelle ManuscriptVersion,
    en copiant ses grilles + annotations vivantes (avec leur kind interne/externe).

    Ne commit PAS : le commit est gere par l'appelant (revise_manuscript), pour que
    l'archivage et la mise a jour du manuscrit soient dans la meme transaction.

    Retourne la ManuscriptVersion creee.
    """
    manuscript_id = manuscript.id
    version_number = await _next_version_number(db, manuscript_id)
    kind_map = await _build_kind_map(db, manuscript_id)

    # 1. Creer la version (instantane des fichiers + metadonnees)
    version = ManuscriptVersion(
        manuscript_id=manuscript_id,
        version_number=version_number,
        pdf_filename=manuscript.pdf_filename,
        docx_filename=manuscript.docx_filename,
        initial_docx_filename=manuscript.initial_docx_filename,
        title=manuscript.title,
        abstract=manuscript.abstract,
        keywords=manuscript.keywords,
    )
    db.add(version)
    await db.flush()  # pour obtenir version.id sans commit

    # 2. Copier les grilles d'evaluation
    grid_result = await db.execute(
        select(ManuscriptEvaluationGrid)
        .where(ManuscriptEvaluationGrid.manuscript_id == manuscript_id)
    )
    grids = grid_result.scalars().all()
    for g in grids:
        db.add(ArchivedEvaluationGrid(
            version_id=version.id,
            manuscript_id=manuscript_id,
            evaluator_id=g.evaluator_id,
            evaluator_kind=kind_map.get(g.evaluator_id),
            originality_of_ideas=g.originality_of_ideas,
            methodology_rigor=g.methodology_rigor,
            theoretical_approach=g.theoretical_approach,
            presentation_clarity=g.presentation_clarity,
            strengths=g.strengths,
            weaknesses=g.weaknesses,
            suggestions=g.suggestions,
            editorial_line_fit=g.editorial_line_fit,
            global_opinion=g.global_opinion,
            recommendation=g.recommendation,
            original_created_at=g.created_at,
            original_updated_at=g.updated_at,
            original_submitted_at=g.submitted_at,
        ))

    # 3. Copier les annotations
    annot_result = await db.execute(
        select(ManuscriptAnnotation)
        .where(ManuscriptAnnotation.manuscript_id == manuscript_id)
    )
    annotations = annot_result.scalars().all()
    for a in annotations:
        db.add(ArchivedAnnotation(
            version_id=version.id,
            original_annotation_id=a.id,
            manuscript_id=manuscript_id,
            evaluator_id=a.evaluator_id,
            evaluator_kind=kind_map.get(a.evaluator_id),
            annotation_type=a.annotation_type,
            created_by_role=a.created_by_role,
            page_number=a.page_number,
            x_position=a.x_position,
            y_position=a.y_position,
            position_data=a.position_data,
            comment=a.comment,
            content_data=a.content_data,
            original_created_at=a.created_at,
            original_updated_at=a.updated_at,
        ))

    logger.info(
        f"Archived manuscript {manuscript_id} as version {version_number} "
        f"({len(grids)} grids, {len(annotations)} annotations)"
    )
    return version


async def start_new_evaluation_cycle(
    db: AsyncSession,
    manuscript_id: int,
    editor_id: int,
) -> Manuscript:
    """
    Lance un nouveau cycle d'evaluation externe apres une resoumission.

    - Vide les grilles + annotations des evaluateurs EXTERNES (deja archivees par la revision).
    - Conserve les evaluations INTERNES (pre-examen reste visible).
    - Les liens externes restent inchanges (ACCEPTED).
    - Statut manuscrit -> UNDER_REVIEW, evaluation_status -> PENDING.

    Commit gere ici (action autonome de l'editeur).
    """
    manuscript = await db.get(Manuscript, manuscript_id)
    if manuscript is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manuscrit introuvable")

    # Garde-fou : on ne lance un nouveau cycle que sur un manuscrit resoumis
    if manuscript.status != ManuscriptStatus.RE_SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Le cycle d'evaluation ne peut etre lance que sur un manuscrit resoumis. Statut actuel: '{manuscript.status.value}'"
        )

    # Recuperer les evaluateurs externes
    link_result = await db.execute(
        select(ManuscriptEvaluatorLink)
        .where(ManuscriptEvaluatorLink.manuscript_id == manuscript_id)
    )
    links = link_result.scalars().all()
    external_ids = [l.evaluator_id for l in links if l.kind == "external"]

    # Vider grilles + annotations des externes (deja archivees par la revision)
    if external_ids:
        await db.execute(
            delete(ManuscriptEvaluationGrid).where(
                ManuscriptEvaluationGrid.manuscript_id == manuscript_id,
                ManuscriptEvaluationGrid.evaluator_id.in_(external_ids),
            )
        )
        await db.execute(
            delete(ManuscriptAnnotation).where(
                ManuscriptAnnotation.manuscript_id == manuscript_id,
                ManuscriptAnnotation.evaluator_id.in_(external_ids),
            )
        )

    # Passer en evaluation (nouveau cycle)
    manuscript.status = ManuscriptStatus.UNDER_REVIEW
    manuscript.evaluation_status = ManuscriptEvaluationStatus.PENDING
    db.add(manuscript)
    await db.commit()
    await db.refresh(manuscript)

    logger.info(
        f"New evaluation cycle started on manuscript {manuscript_id} by editor {editor_id} "
        f"({len(external_ids)} external evaluators reset, internal evaluations kept)"
    )
    return manuscript
