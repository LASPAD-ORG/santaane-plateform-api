"""
Manuscripts module - Error codes
"""


class ManuscriptErrorCode:
    """Error codes for manuscript operations"""
    
    # Validation errors
    INVALID_THEME_ID = "Invalid theme ID provided"
    INVALID_SECTION_ID = "Invalid section ID provided"
    INVALID_LANGUAGE_ID = "Invalid language ID provided"
    PDF_FILE_REQUIRED = "PDF file is required for manuscript submission"
    TITLE_REQUIRED = "Manuscript title is required"
    ABSTRACT_REQUIRED = "Manuscript abstract is required"
    
    # Permission errors
    AUTHOR_ROLE_REQUIRED = "Author role is required to submit a manuscript"
    NOT_MANUSCRIPT_OWNER = "You are not authorized to access this manuscript"
    
    # Resource errors
    MANUSCRIPT_NOT_FOUND = "Manuscript not found"
    
    # File errors
    FILE_UPLOAD_FAILED = "Failed to upload manuscript file"
    INVALID_FILE_FORMAT = "Only PDF files are allowed"
