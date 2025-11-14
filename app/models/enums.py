"""
Enumerations for the Santaane Platform API
All status and type enums used across the application models
"""
from enum import Enum


# ==================== Manuscript Related Enums ====================

class ManuscriptStatus(str, Enum):
    """Manuscript lifecycle status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    REVISION_REQUESTED = "revision_requested"
    REVISED = "revised"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PUBLISHED = "published"
    WITHDRAWN = "withdrawn"


class ManuscriptFileType(str, Enum):
    """Types of files attached to manuscripts"""
    PDF = "pdf"
    DOCX = "docx"
    TEX = "tex"
    SUPPLEMENTARY = "supplementary"
    COVER_LETTER = "cover_letter"
    FIGURE = "figure"
    TABLE = "table"
    DATA = "data"
    OTHER = "other"


# ==================== Editor Related Enums ====================

class EditorRole(str, Enum):
    """Roles for editors in laboratories and manuscripts"""
    CHIEF_EDITOR = "chief_editor"
    ASSOCIATE_EDITOR = "associate_editor"
    HANDLING_EDITOR = "handling_editor"
    SECTION_EDITOR = "section_editor"
    GUEST_EDITOR = "guest_editor"


# ==================== Review Related Enums ====================

class ReviewAssignmentStatus(str, Enum):
    """Status of review assignments"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class ReviewRecommendation(str, Enum):
    """Reviewer's recommendation on manuscript"""
    ACCEPT = "accept"
    MINOR_REVISION = "minor_revision"
    MAJOR_REVISION = "major_revision"
    REJECT = "reject"


class ReviewDecisionType(str, Enum):
    """Editorial decision on manuscript"""
    ACCEPT = "accept"
    MINOR_REVISION = "minor_revision"
    MAJOR_REVISION = "major_revision"
    REJECT = "reject"
    WITHDRAWN = "withdrawn"


# ==================== Mentorship Related Enums ====================

class MentorshipStatus(str, Enum):
    """Status of mentorship relationships"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class MentorshipFeedbackType(str, Enum):
    """Types of mentorship feedback"""
    MILESTONE = "milestone"
    PROGRESS_CHECK = "progress_check"
    FINAL_EVALUATION = "final_evaluation"
    INTERIM_REVIEW = "interim_review"
    IMPROVEMENT_PLAN = "improvement_plan"


class MentorshipActivityType(str, Enum):
    """Types of mentorship activities"""
    COMMENT_ADDED = "comment_added"
    FEEDBACK_GIVEN = "feedback_given"
    MILESTONE_REACHED = "milestone_reached"
    STATUS_CHANGED = "status_changed"
    MEETING_SCHEDULED = "meeting_scheduled"
    MEETING_COMPLETED = "meeting_completed"
    DOCUMENT_REVIEWED = "document_reviewed"
    GOAL_SET = "goal_set"
    GOAL_ACHIEVED = "goal_achieved"


# ==================== User Related Enums ====================

class LanguageProficiency(str, Enum):
    """Language proficiency levels"""
    NATIVE = "native"
    FLUENT = "fluent"
    ADVANCED = "advanced"
    INTERMEDIATE = "intermediate"
    BASIC = "basic"


# ==================== System Related Enums ====================

class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
