"""
File storage utilities for handling file uploads and downloads.
Supports local filesystem storage with future extensibility for S3/cloud storage.
"""
import os
import uuid
import aiofiles
from pathlib import Path
from fastapi import UploadFile, HTTPException
from typing import Tuple, Optional
from app.core.config import settings
from app.core.logging import logger


class FileStorage:
    """
    File storage handler for manuscript files.
    Currently implements local filesystem storage.
    """

    def __init__(self, base_dir: str = None):
        """
        Initialize file storage with base directory.

        Args:
            base_dir: Base directory for file storage (defaults to settings.UPLOAD_DIR)
        """
        self.base_dir = Path(base_dir or settings.UPLOAD_DIR)
        self._ensure_directory_exists()

    def _ensure_directory_exists(self):
        """Create base directory if it doesn't exist."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"File storage initialized at: {self.base_dir.absolute()}")

    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename."""
        return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    def _validate_file_type(self, filename: str) -> bool:
        """
        Validate file type based on extension.

        Args:
            filename: Name of the file to validate

        Returns:
            bool: True if file type is allowed

        Raises:
            HTTPException: If file type is not allowed
        """
        ext = self._get_file_extension(filename)
        if ext not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type '.{ext}' is not allowed. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
            )
        return True

    def _validate_file_size(self, file_size: int) -> bool:
        """
        Validate file size.

        Args:
            file_size: Size of file in bytes

        Returns:
            bool: True if file size is within limits

        Raises:
            HTTPException: If file size exceeds limit
        """
        if file_size > settings.MAX_FILE_SIZE:
            max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {max_size_mb}MB"
            )
        return True

    def _generate_unique_filename(self, original_filename: str) -> str:
        """
        Generate a unique filename while preserving the extension.

        Args:
            original_filename: Original name of the uploaded file

        Returns:
            str: Unique filename (UUID + extension)
        """
        ext = self._get_file_extension(original_filename)
        unique_id = uuid.uuid4().hex
        return f"{unique_id}.{ext}" if ext else unique_id

    async def save_file(
        self,
        file: UploadFile,
        subdirectory: Optional[str] = None
    ) -> Tuple[str, str, int]:
        """
        Save uploaded file to storage.

        Args:
            file: FastAPI UploadFile object
            subdirectory: Optional subdirectory within base_dir (e.g., "manuscripts/123")

        Returns:
            Tuple[str, str, int]: (file_path, original_filename, file_size)

        Raises:
            HTTPException: If validation fails or save operation fails
        """
        try:
            # Read file content
            content = await file.read()
            file_size = len(content)

            # Validate
            self._validate_file_type(file.filename)
            self._validate_file_size(file_size)

            # Determine storage path
            if subdirectory:
                storage_dir = self.base_dir / subdirectory
                storage_dir.mkdir(parents=True, exist_ok=True)
            else:
                storage_dir = self.base_dir

            # Generate unique filename
            unique_filename = self._generate_unique_filename(file.filename)
            file_path = storage_dir / unique_filename

            # Save file asynchronously
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)

            # Return relative path from base_dir
            relative_path = str(file_path.relative_to(self.base_dir))

            logger.info(
                f"File saved successfully: {file.filename} -> {relative_path} ({file_size} bytes)"
            )

            return relative_path, file.filename, file_size

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error saving file {file.filename}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file: {str(e)}"
            )

    async def get_file(self, file_path: str) -> Tuple[Path, bool]:
        """
        Get file from storage.

        Args:
            file_path: Relative path to file from base_dir

        Returns:
            Tuple[Path, bool]: (absolute_path, exists)

        Raises:
            HTTPException: If file doesn't exist or path is invalid
        """
        try:
            # Construct absolute path
            absolute_path = self.base_dir / file_path

            # Security check: ensure path is within base_dir (prevent directory traversal)
            if not absolute_path.resolve().is_relative_to(self.base_dir.resolve()):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file path"
                )

            # Check if file exists
            if not absolute_path.exists() or not absolute_path.is_file():
                raise HTTPException(
                    status_code=404,
                    detail="File not found"
                )

            return absolute_path, True

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving file {file_path}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve file: {str(e)}"
            )

    async def delete_file(self, file_path: str) -> bool:
        """
        Delete file from storage.

        Args:
            file_path: Relative path to file from base_dir

        Returns:
            bool: True if file was deleted successfully

        Raises:
            HTTPException: If file doesn't exist or deletion fails
        """
        try:
            # Get file path
            absolute_path, exists = await self.get_file(file_path)

            if exists:
                # Delete file
                absolute_path.unlink()
                logger.info(f"File deleted successfully: {file_path}")
                return True

            return False

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete file: {str(e)}"
            )

    def get_file_info(self, file_path: str) -> dict:
        """
        Get file metadata.

        Args:
            file_path: Relative path to file from base_dir

        Returns:
            dict: File metadata (size, name, extension, etc.)
        """
        try:
            absolute_path = self.base_dir / file_path

            if not absolute_path.exists():
                return None

            stat = absolute_path.stat()

            return {
                "file_path": file_path,
                "file_name": absolute_path.name,
                "file_size": stat.st_size,
                "extension": self._get_file_extension(absolute_path.name),
                "created_at": stat.st_ctime,
                "modified_at": stat.st_mtime,
            }

        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {str(e)}")
            return None


# Global file storage instance
file_storage = FileStorage()


# Convenience functions for easy import
async def save_file(file: UploadFile, subdirectory: Optional[str] = None) -> Tuple[str, str, int]:
    """Save file using global file_storage instance."""
    return await file_storage.save_file(file, subdirectory)


async def get_file(file_path: str) -> Tuple[Path, bool]:
    """Get file using global file_storage instance."""
    return await file_storage.get_file(file_path)


async def delete_file(file_path: str) -> bool:
    """Delete file using global file_storage instance."""
    return await file_storage.delete_file(file_path)


def get_file_info(file_path: str) -> dict:
    """Get file info using global file_storage instance."""
    return file_storage.get_file_info(file_path)
