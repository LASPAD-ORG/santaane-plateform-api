from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime 
import shutil
import os
from .schemas import EditorialVersionResponse # Ajoute l'import
from sqlalchemy.orm import joinedload
# --- IMPORTS ALIGNÉS SUR TA STRUCTURE ---
try:
    from app.db import get_db as get_session
    from app.models.editorial_version import EditorialVersion
    from app.models.manuscript import Manuscript
    # On essaie de trouver get_current_user là où il est probable qu'il soit
    try:
        from app.modules.auth.service import get_current_user
    except ImportError:
        from app.core.security import get_current_user
except ImportError as e:
    # Si l'import échoue encore, on affiche l'erreur précise pour débugger
    print(f"DEBUG IMPORT ERROR: {e}")
    raise

router = APIRouter(prefix="/manuscripts/detail", tags=["editorial"])

# --- CONFIGURATION ---
UPLOAD_DIR = "/app/uploads/editorial"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/{id}/editorial-versions", response_model=list[EditorialVersionResponse])
async def get_editorial_versions(
    id: int, 
    db: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    query = (
        select(EditorialVersion)
        .where(EditorialVersion.manuscript_id == id)
        .options(joinedload(EditorialVersion.editor))
        .order_by(EditorialVersion.version_number.desc())
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/{id}/editorial-upload", response_model=EditorialVersionResponse) # Ajoute le response_model
async def upload_editorial_version(
    id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """Télécharge une nouvelle version éditoriale"""

    # 1. Vérifier si le manuscrit existe
    manuscript = await db.get(Manuscript, id)
    if not manuscript:
        raise HTTPException(status_code=404, detail="Manuscrit non trouvé")

    # 2. Calcul du numéro de version (avant de créer le nom du fichier)
    query = (
        select(EditorialVersion)
        .where(EditorialVersion.manuscript_id == id)
        .order_by(EditorialVersion.version_number.desc())
    )
    result = await db.execute(query)
    last_v = result.scalars().first()
    next_v = (last_v.version_number + 1) if last_v else 1

    # 3. Préparation du nom de fichier avec le nom de l'éditeur
    file_extension = os.path.splitext(file.filename)[1]
    # Nettoyer le nom de l'éditeur (enlever espaces et caractères spéciaux)
    editor_name_clean = current_user.full_name.replace(" ", "_").replace("'", "").replace('"', '')
    # Format: editorial_ms_{id}_version_{numero}_nomEditeur.docx
    filename = f"editorial_ms_{id}_version_{next_v}_{editor_name_clean}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # 4. Sauvegarde physique
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'écriture: {str(e)}")

    # 5. Enregistrement en base
    new_version = EditorialVersion(
        manuscript_id=id,
        version_number=next_v,
        filename=filename,
        editor_id=current_user.id
    )

    db.add(new_version)
    try:
        await db.commit()
        await db.refresh(new_version)

        # Charger la relation editor pour avoir le nom dans la réponse
        query = (
            select(EditorialVersion)
            .where(EditorialVersion.id == new_version.id)
            .options(joinedload(EditorialVersion.editor))
        )
        result = await db.execute(query)
        new_version = result.scalar_one()
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Erreur DB: {str(e)}")

    return new_version

from fastapi.responses import FileResponse
@router.get("/{id}/editorial-download/{version_id}")
async def download_editorial_version(
    id: int,
    version_id: int,
    db: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    # Sécurité : on vérifie que la version appartient bien au manuscrit spécifié
    # On charge aussi l'éditeur pour avoir son nom
    query = (
        select(EditorialVersion)
        .where(
            EditorialVersion.id == version_id,
            EditorialVersion.manuscript_id == id
        )
        .options(joinedload(EditorialVersion.editor))
    )
    result = await db.execute(query)
    version = result.scalar_one_or_none()

    if not version:
        raise HTTPException(status_code=404, detail="Version non trouvée pour ce manuscrit")

    file_path = os.path.join(UPLOAD_DIR, version.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Le fichier n'existe pas sur le serveur")

    # Utiliser le nom de fichier qui contient déjà la version et le nom de l'éditeur
    return FileResponse(
        path=file_path,
        filename=version.filename, # Le nom contient déjà version_X_nomEditeur.docx
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )