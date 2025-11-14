from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.role import Role


class UserRole(SQLModel, table=True):
    __tablename__ = "user_roles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    role_id: int = Field(foreign_key="roles.id", nullable=False, index=True)
    assigned_by: Optional[int] = Field(default=None, foreign_key="users.id")
    assigned_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    # Relationships
    user: "User" = Relationship(
        back_populates="user_roles",
        sa_relationship_kwargs={"foreign_keys": "[UserRole.user_id]"}
    )
    role: "Role" = Relationship(back_populates="user_roles")
    assigner: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[UserRole.assigned_by]"}
    )
