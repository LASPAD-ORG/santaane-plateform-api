"""
API routes for file upload/download.
Generic file handling endpoints.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from typing import Optional, List
from datetime import datetime
from pathlib import Path
import uuid
from app.modules.files.schemas import FileUploadResponse, FileDownloadResponse
from app.core.file_storage import file_storage
from app.core.permissions import get_current_user
from app.models.user import User
from app.core.logging import logger


router = APIRouter(prefix="/files", tags=["Files"])


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a file"
)
async def upload_file(
    file: UploadFile = File(..., description="File to upload"),
    subdirectory: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Upload a file to the server.

    **Requires:** Authentication

    **Parameters:**
    - **file**: File to upload (multipart/form-data)
    - **subdirectory**: Optional subdirectory path (e.g., "manuscripts/123")

    **Limitations:**
    - Max file size: 10MB
    - Allowed types: pdf, docx, doc, tex, zip, png, jpg, jpeg

    **Returns:**
    - File ID (UUID)
    - Original filename
    - Stored path
    - File size
    - Upload timestamp
    """
    try:
        # Save file using file_storage utility
        file_path, original_filename, file_size = await file_storage.save_file(
            file=file,
            subdirectory=subdirectory
        )

        # Generate unique file ID
        file_id = uuid.uuid4().hex

        # Get file extension
        file_extension = Path(original_filename).suffix.lstrip('.').lower()

        logger.info(
            f"File uploaded by user {current_user.email}: "
            f"{original_filename} ({file_size} bytes) -> {file_path}"
        )

        return FileUploadResponse(
            file_id=file_id,
            file_name=original_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_extension,
            uploaded_at=datetime.utcnow()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


@router.post(
    "/upload-multiple",
    response_model=List[FileUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload multiple files"
)
async def upload_multiple_files(
    files: List[UploadFile] = File(..., description="Files to upload"),
    subdirectory: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Upload multiple files to the server.

    **Requires:** Authentication

    **Parameters:**
    - **files**: List of files to upload (multipart/form-data)
    - **subdirectory**: Optional subdirectory path (e.g., "manuscripts/123")

    **Limitations:**
    - Max file size per file: 10MB
    - Allowed types: pdf, docx, doc, tex, zip, png, jpg, jpeg

    **Returns:**
    - List of upload responses for each file
    """
    responses = []

    for file in files:
        try:
            # Save file
            file_path, original_filename, file_size = await file_storage.save_file(
                file=file,
                subdirectory=subdirectory
            )

            # Generate unique file ID
            file_id = uuid.uuid4().hex

            # Get file extension
            file_extension = Path(original_filename).suffix.lstrip('.').lower()

            responses.append(FileUploadResponse(
                file_id=file_id,
                file_name=original_filename,
                file_path=file_path,
                file_size=file_size,
                file_type=file_extension,
                uploaded_at=datetime.utcnow()
            ))

            logger.info(
                f"File uploaded by user {current_user.email}: "
                f"{original_filename} ({file_size} bytes) -> {file_path}"
            )

        except HTTPException as e:
            # Log error but continue with other files
            logger.error(f"Failed to upload {file.filename}: {e.detail}")
            # You can choose to fail all or continue
            raise

    return responses


@router.get(
    "/download/{file_path:path}",
    response_class=FileResponse,
    summary="Download a file"
)
async def download_file(
    file_path: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download a file from the server.

    **Requires:** Authentication

    **Parameters:**
    - **file_path**: Relative path to the file (e.g., "manuscripts/123/abc123.pdf")

    **Returns:**
    - File content as download
    """
    try:
        # Get file from storage
        absolute_path, exists = await file_storage.get_file(file_path)

        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        # Get file info
        file_info = file_storage.get_file_info(file_path)

        logger.info(
            f"File downloaded by user {current_user.email}: {file_path}"
        )

        # Return file
        return FileResponse(
            path=absolute_path,
            filename=file_info['file_name'],
            media_type='application/octet-stream'
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download failed for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File download failed: {str(e)}"
        )


@router.get(
    "/info/{file_path:path}",
    response_model=FileDownloadResponse,
    summary="Get file information"
)
async def get_file_info(
    file_path: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get information about a file without downloading it.

    **Requires:** Authentication

    **Parameters:**
    - **file_path**: Relative path to the file

    **Returns:**
    - File metadata (name, size, type)
    """
    try:
        # Get file info
        file_info = file_storage.get_file_info(file_path)

        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        return FileDownloadResponse(
            file_name=file_info['file_name'],
            file_size=file_info['file_size'],
            file_type=file_info['extension']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get file info failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file info: {str(e)}"
        )


@router.delete(
    "/{file_path:path}",
    summary="Delete a file"
)
async def delete_file(
    file_path: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a file from the server.

    **Requires:** Authentication

    **Parameters:**
    - **file_path**: Relative path to the file

    **Returns:**
    - Success message
    """
    try:
        # Delete file
        success = await file_storage.delete_file(file_path)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        logger.info(
            f"File deleted by user {current_user.email}: {file_path}"
        )

        return {"message": "File deleted successfully", "filePath": file_path}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete failed for user {current_user.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File deletion failed: {str(e)}"
        )
