"""
API routes for manuscript attachments and attachment requests.

- Authors (manuscript owners) and editors can upload attachments.
- Authors see their own attachments + those transmitted by editors (visible_to_author=True).
- Editors see all attachments (internal + transmitted).
- Editors can create attachment requests; authors fulfill them by uploading.
"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, status, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel, Field
from sqlalchemy import and_

from app.db import get_db
from app.core.security import get_current_user
from app.core.roles import UserRole
from app.core.file_storage import file_storage
from app.core.logging import get_logger
from app.models.user import User
from app.models.manuscript import Manuscript
from app.models.manuscript_attachment import ManuscriptAttachment
from app.models.attachment_request import AttachmentRequest
from app.modules.auth.repository import AuthRepository
from app.core.email import EmailService
from app.models.role import Role
from app.models.user_role import UserRole as UserRoleModel

logger = get_logger(__name__)

router = APIRouter(prefix="/manuscripts", tags=["Attachments"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class AttachmentResponse(BaseModel):
    id: int
    manuscriptId: int
    title: str
    description: Optional[str] = None
    originalFilename: str
    contentType: Optional[str] = None
    fileSize: Optional[int] = None
    uploadedById: int
    uploadedByRole: str
    visibleToAuthor: bool
    attachmentType: str
    requestId: Optional[int] = None
    createdAt: datetime


class AttachmentRequestResponse(BaseModel):
    id: int
    manuscriptId: int
    title: str
    description: Optional[str] = None
    requestedById: int
    status: str
    fulfilledByAttachmentId: Optional[int] = None
    createdAt: datetime
    fulfilledAt: Optional[datetime] = None


class CreateAttachmentRequestBody(BaseModel):
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_manuscript_or_404(db: AsyncSession, manuscript_id: int) -> Manuscript:
    manuscript = await db.get(Manuscript, manuscript_id)
    if manuscript is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manuscrit introuvable")
    return manuscript


async def _resolve_role(db: AsyncSession, user: User, manuscript: Manuscript) -> str:
    """Retourne 'editor' | 'author' | 'other' pour ce manuscrit."""
    repo = AuthRepository(db)
    roles = await repo.get_user_roles(user.id)
    if UserRole.SUPER_ADMIN.value in roles or UserRole.EDITOR.value in roles:
        return "editor"
    if UserRole.AUTHOR.value in roles and manuscript.author_id == user.id:
        return "author"
    return "other"


async def _notify_editors_attachment(db: AsyncSession, manuscript: Manuscript, attachment_title: str, author_name: str, description: str = None):
    """Notifie tous les editeurs actifs qu'une piece a ete deposee par l'auteur."""
    try:
        query = (
            select(User)
            .join(UserRoleModel, UserRoleModel.user_id == User.id)
            .join(Role, Role.id == UserRoleModel.role_id)
            .where(and_(Role.name == "EDITOR", User.is_active == True))
            .distinct()
        )
        result = await db.execute(query)
        editors = result.scalars().all()
        for editor in editors:
            try:
                EmailService.send_attachment_uploaded_to_editor(
                    to_email=str(editor.email),
                    editor_name=str(editor.full_name),
                    manuscript_title=manuscript.title,
                    attachment_title=attachment_title,
                    author_name=author_name,
                    attachment_description=description,
                    lang="fr",
                )
            except Exception as e:
                logger.error(f"Failed to notify editor {editor.email} of attachment: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to fetch editors for attachment notification: {str(e)}")


def _to_attachment_response(att: ManuscriptAttachment) -> AttachmentResponse:
    return AttachmentResponse(
        id=att.id,
        manuscriptId=att.manuscript_id,
        title=att.title,
        description=att.description,
        originalFilename=att.original_filename,
        contentType=att.content_type,
        fileSize=att.file_size,
        uploadedById=att.uploaded_by_id,
        uploadedByRole=att.uploaded_by_role,
        visibleToAuthor=att.visible_to_author,
        attachmentType=att.attachment_type,
        requestId=att.request_id,
        createdAt=att.created_at,
    )


def _to_request_response(req: AttachmentRequest) -> AttachmentRequestResponse:
    return AttachmentRequestResponse(
        id=req.id,
        manuscriptId=req.manuscript_id,
        title=req.title,
        description=req.description,
        requestedById=req.requested_by_id,
        status=req.status,
        fulfilledByAttachmentId=req.fulfilled_by_attachment_id,
        createdAt=req.created_at,
        fulfilledAt=req.fulfilled_at,
    )


# ---------------------------------------------------------------------------
# Attachments
# ---------------------------------------------------------------------------

@router.post(
    "/{manuscript_id}/attachments",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload an attachment to a manuscript",
)
async def upload_attachment(
    manuscript_id: int,
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    visible_to_author: Optional[bool] = Form(None),
    request_id: Optional[int] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    manuscript = await _get_manuscript_or_404(db, manuscript_id)
    role = await _resolve_role(db, current_user, manuscript)
    if role == "other":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acces non autorise a ce manuscrit")

    # Determiner la visibilite et le type selon le role
    if role == "author":
        vis = True  # les pieces de l'auteur lui sont toujours visibles
        att_type = "author_upload"
    else:  # editor
        vis = True if visible_to_author is None else bool(visible_to_author)
        att_type = "editor_transmission" if vis else "editor_internal"

    # Sauvegarder le fichier
    relative_path, original_filename, file_size = await file_storage.save_file(
        file, subdirectory=f"attachments/{manuscript_id}"
    )

    attachment = ManuscriptAttachment(
        manuscript_id=manuscript_id,
        filename=relative_path,
        original_filename=original_filename,
        content_type=file.content_type,
        file_size=file_size,
        title=title,
        description=description if description else None,
        uploaded_by_id=current_user.id,
        uploaded_by_role=role,
        visible_to_author=vis,
        attachment_type=att_type,
        request_id=request_id,
    )
    db.add(attachment)
    await db.commit()
    await db.refresh(attachment)

    # Si la piece repond a une demande, marquer la demande comme fulfilled
    if request_id is not None:
        req = await db.get(AttachmentRequest, request_id)
        if req is not None and req.manuscript_id == manuscript_id:
            req.status = "fulfilled"
            req.fulfilled_by_attachment_id = attachment.id
            req.fulfilled_at = datetime.utcnow()
            db.add(req)
            await db.commit()

    # Notifications email
    try:
        if role == "author":
            # L'auteur depose -> notifier tous les editeurs
            await _notify_editors_attachment(
                db, manuscript, title, str(current_user.full_name),
                description if description else None
            )
        elif role == "editor" and vis:
            # L'editeur transmet une piece visible -> notifier l'auteur
            author = await db.get(User, manuscript.author_id)
            if author and author.email:
                EmailService.send_attachment_transmitted_to_author(
                    to_email=str(author.email),
                    author_name=str(author.full_name),
                    manuscript_title=manuscript.title,
                    attachment_title=title,
                    attachment_description=description if description else None,
                    lang="fr",
                )
        # role editor + piece interne (vis=False) -> aucune notification
    except Exception as e:
        logger.error(f"Attachment notification failed: {str(e)}")

    logger.info(f"Attachment {attachment.id} uploaded on manuscript {manuscript_id} by {role} {current_user.email}")
    return _to_attachment_response(attachment)


@router.get(
    "/{manuscript_id}/attachments",
    response_model=List[AttachmentResponse],
    summary="List attachments of a manuscript (filtered by role)",
)
async def list_attachments(
    manuscript_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    manuscript = await _get_manuscript_or_404(db, manuscript_id)
    role = await _resolve_role(db, current_user, manuscript)
    if role == "other":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acces non autorise a ce manuscrit")

    query = select(ManuscriptAttachment).where(
        ManuscriptAttachment.manuscript_id == manuscript_id
    )
    result = await db.execute(query)
    attachments = result.scalars().all()

    # Filtrage visibilite pour l'auteur : ses propres pieces + celles visible_to_author
    if role == "author":
        attachments = [
            a for a in attachments
            if a.visible_to_author or a.uploaded_by_id == current_user.id
        ]

    attachments = sorted(attachments, key=lambda a: a.created_at, reverse=True)
    return [_to_attachment_response(a) for a in attachments]


@router.get(
    "/{manuscript_id}/attachments/{attachment_id}/download",
    response_class=FileResponse,
    summary="Download an attachment",
)
async def download_attachment(
    manuscript_id: int,
    attachment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    manuscript = await _get_manuscript_or_404(db, manuscript_id)
    role = await _resolve_role(db, current_user, manuscript)
    if role == "other":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acces non autorise a ce manuscrit")

    attachment = await db.get(ManuscriptAttachment, attachment_id)
    if attachment is None or attachment.manuscript_id != manuscript_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Piece jointe introuvable")

    # Garde-fou visibilite : l'auteur ne telecharge que ses pieces ou celles visibles
    if role == "author" and not attachment.visible_to_author and attachment.uploaded_by_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Piece jointe non accessible")

    absolute_path, exists = await file_storage.get_file(attachment.filename)
    if not exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fichier introuvable sur le serveur")

    return FileResponse(
        path=absolute_path,
        filename=attachment.original_filename,
        media_type=attachment.content_type or "application/octet-stream",
    )


@router.delete(
    "/{manuscript_id}/attachments/{attachment_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an attachment (uploader, or editor for any)",
)
async def delete_attachment(
    manuscript_id: int,
    attachment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    manuscript = await _get_manuscript_or_404(db, manuscript_id)
    role = await _resolve_role(db, current_user, manuscript)
    if role == "other":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acces non autorise a ce manuscrit")

    attachment = await db.get(ManuscriptAttachment, attachment_id)
    if attachment is None or attachment.manuscript_id != manuscript_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Piece jointe introuvable")

    # Le deposant peut supprimer sa piece ; l'editeur peut tout supprimer
    if role != "editor" and attachment.uploaded_by_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous ne pouvez supprimer que vos propres pieces")

    # Supprimer le fichier physique (best effort)
    try:
        await file_storage.delete_file(attachment.filename)
    except Exception as e:
        logger.error(f"Failed to delete file {attachment.filename}: {str(e)}")

    await db.delete(attachment)
    await db.commit()
    logger.info(f"Attachment {attachment_id} deleted by {role} {current_user.email}")
    return {"deleted": True, "attachmentId": attachment_id}


# ---------------------------------------------------------------------------
# Attachment requests (editor asks the author for a document)
# ---------------------------------------------------------------------------

@router.post(
    "/{manuscript_id}/attachment-requests",
    response_model=AttachmentRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Editor creates an attachment request",
)
async def create_attachment_request(
    manuscript_id: int,
    body: CreateAttachmentRequestBody,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    manuscript = await _get_manuscript_or_404(db, manuscript_id)
    role = await _resolve_role(db, current_user, manuscript)
    if role != "editor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Seul un editeur peut demander une piece")

    req = AttachmentRequest(
        manuscript_id=manuscript_id,
        title=body.title,
        description=body.description if body.description else None,
        requested_by_id=current_user.id,
        status="pending",
    )
    db.add(req)
    await db.commit()
    await db.refresh(req)
    # Notifier l'auteur de la demande
    try:
        author = await db.get(User, manuscript.author_id)
        if author and author.email:
            EmailService.send_attachment_request_to_author(
                to_email=str(author.email),
                author_name=str(author.full_name),
                manuscript_title=manuscript.title,
                request_title=req.title,
                request_description=req.description,
                lang="fr",
            )
    except Exception as e:
        logger.error(f"Failed to notify author of attachment request: {str(e)}")

    logger.info(f"Attachment request {req.id} created on manuscript {manuscript_id} by editor {current_user.email}")
    return _to_request_response(req)


@router.get(
    "/{manuscript_id}/attachment-requests",
    response_model=List[AttachmentRequestResponse],
    summary="List attachment requests of a manuscript",
)
async def list_attachment_requests(
    manuscript_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    manuscript = await _get_manuscript_or_404(db, manuscript_id)
    role = await _resolve_role(db, current_user, manuscript)
    if role == "other":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acces non autorise a ce manuscrit")

    query = select(AttachmentRequest).where(
        AttachmentRequest.manuscript_id == manuscript_id
    )
    result = await db.execute(query)
    requests = result.scalars().all()
    requests = sorted(requests, key=lambda r: r.created_at, reverse=True)
    return [_to_request_response(r) for r in requests]