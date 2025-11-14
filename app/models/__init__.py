# Database models
# Import all your models here

# Core models
from app.models.user import User
from app.models.city import City
from app.models.country import Country
from app.models.role import Role
from app.models.user_role import UserRole

# User profile extensions
from app.models.affiliation import Affiliation
from app.models.user_affiliation import UserAffiliation
from app.models.expertise_domain import ExpertiseDomain
from app.models.user_expertise_domain import UserExpertiseDomain
from app.models.language import Language
from app.models.user_language import UserLanguage

# Editorial structure
from app.models.laboratory import Laboratory
from app.models.editor_assignment import EditorAssignment
from app.models.journal_config import JournalConfig
from app.models.manuscript_editor import ManuscriptEditor

# Core manuscript system
from app.models.category import Category
from app.models.manuscript import Manuscript
from app.models.manuscript_file import ManuscriptFile
from app.models.manuscript_version import ManuscriptVersion
from app.models.manuscript_discussion import ManuscriptDiscussion

# Review system
from app.models.review_assignment import ReviewAssignment
from app.models.review_response import ReviewResponse
from app.models.review_comment import ReviewComment
from app.models.review_decision import ReviewDecision

# Mentorship system
from app.models.mentorship import Mentorship
from app.models.mentorship_comment import MentorshipComment
from app.models.mentorship_feedback import MentorshipFeedback
from app.models.mentorship_activity_log import MentorshipActivityLog


# Add all new models to this list and to __all__
__all__ = [
    # Core models
    "User",
    "City",
    "Country",
    "Role",
    "UserRole",
    # User profile extensions
    "Affiliation",
    "UserAffiliation",
    "ExpertiseDomain",
    "UserExpertiseDomain",
    "Language",
    "UserLanguage",
    # Editorial structure
    "Laboratory",
    "EditorAssignment",
    "JournalConfig",
    "ManuscriptEditor",
    # Core manuscript system
    "Category",
    "Manuscript",
    "ManuscriptFile",
    "ManuscriptVersion",
    "ManuscriptDiscussion",
    # Review system
    "ReviewAssignment",
    "ReviewResponse",
    "ReviewComment",
    "ReviewDecision",
    # Mentorship system
    "Mentorship",
    "MentorshipComment",
    "MentorshipFeedback",
    "MentorshipActivityLog",
]