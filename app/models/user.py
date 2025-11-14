from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user_role import UserRole
    from app.models.country import Country
    from app.models.city import City
    from app.models.user_affiliation import UserAffiliation
    from app.models.user_expertise_domain import UserExpertiseDomain
    from app.models.user_language import UserLanguage
    from app.models.editor_assignment import EditorAssignment
    from app.models.manuscript import Manuscript
    from app.models.manuscript_editor import ManuscriptEditor
    from app.models.manuscript_discussion import ManuscriptDiscussion
    from app.models.review_assignment import ReviewAssignment
    from app.models.review_comment import ReviewComment
    from app.models.review_decision import ReviewDecision
    from app.models.mentorship import Mentorship
    from app.models.mentorship_comment import MentorshipComment
    from app.models.mentorship_activity_log import MentorshipActivityLog


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, unique=True, nullable=False, index=True)
    email_verified: bool = Field(default=False, nullable=False)
    password_hash: str = Field(max_length=255, nullable=False)
    full_name: str = Field(max_length=150, nullable=False)
    country_id: Optional[int] = Field(default=None, foreign_key="countries.id")
    city_id: Optional[int] = Field(default=None, foreign_key="cities.id")
    timezone: Optional[str] = Field(max_length=50, default=None)
    profile_photo: Optional[str] = Field(max_length=255, default=None)
    orcid_id: Optional[str] = Field(max_length=50, default=None)
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    # Relationships
    country: Optional["Country"] = Relationship(back_populates="users")
    city: Optional["City"] = Relationship(back_populates="users")
    user_roles: list["UserRole"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "UserRole.user_id"}
    )

    # Profile extensions
    user_affiliations: list["UserAffiliation"] = Relationship(back_populates="user")
    user_expertise_domains: list["UserExpertiseDomain"] = Relationship(back_populates="user")
    user_languages: list["UserLanguage"] = Relationship(back_populates="user")

    # Editorial relationships
    editor_assignments: list["EditorAssignment"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "EditorAssignment.user_id"}
    )
    editor_assignments_made: list["EditorAssignment"] = Relationship(
        back_populates="assigner",
        sa_relationship_kwargs={"foreign_keys": "EditorAssignment.assigned_by"}
    )

    # Manuscript relationships
    manuscripts: list["Manuscript"] = Relationship(
        back_populates="author",
        sa_relationship_kwargs={"foreign_keys": "Manuscript.author_id"}
    )
    manuscript_editors: list["ManuscriptEditor"] = Relationship(
        back_populates="editor",
        sa_relationship_kwargs={"foreign_keys": "ManuscriptEditor.editor_id"}
    )
    manuscript_editor_assignments_made: list["ManuscriptEditor"] = Relationship(
        back_populates="assigner",
        sa_relationship_kwargs={"foreign_keys": "ManuscriptEditor.assigned_by"}
    )
    manuscript_discussions: list["ManuscriptDiscussion"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "ManuscriptDiscussion.user_id"}
    )

    # Review relationships
    review_assignments: list["ReviewAssignment"] = Relationship(
        back_populates="reviewer",
        sa_relationship_kwargs={"foreign_keys": "ReviewAssignment.reviewer_id"}
    )
    review_assignments_made: list["ReviewAssignment"] = Relationship(
        back_populates="assigner",
        sa_relationship_kwargs={"foreign_keys": "ReviewAssignment.assigned_by"}
    )
    review_comments: list["ReviewComment"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "ReviewComment.user_id"}
    )
    review_decisions: list["ReviewDecision"] = Relationship(
        back_populates="editor",
        sa_relationship_kwargs={"foreign_keys": "ReviewDecision.decided_by"}
    )

    # Mentorship relationships
    mentorships_as_mentor: list["Mentorship"] = Relationship(
        back_populates="mentor",
        sa_relationship_kwargs={"foreign_keys": "Mentorship.mentor_id"}
    )
    mentorships_assigned: list["Mentorship"] = Relationship(
        back_populates="assigner",
        sa_relationship_kwargs={"foreign_keys": "Mentorship.assigned_by"}
    )
    mentorship_comments: list["MentorshipComment"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "MentorshipComment.user_id"}
    )
    mentorship_activity_logs: list["MentorshipActivityLog"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "MentorshipActivityLog.user_id"}
    )

