"""
Schemas for evaluator assignment management
"""
from pydantic import Field
from datetime import datetime
from typing import Optional
from app.schemas.base import BaseSchema
from app.models.enums import EvaluatorAssignmentStatus


class EvaluatorAssignRequest(BaseSchema):
    """Schema for assigning an evaluator to a manuscript"""
    evaluator_id: int = Field(..., description="ID of the evaluator to assign", alias="evaluatorId")
    evaluation_deadline: datetime = Field(..., description="Deadline for evaluation", alias="evaluationDeadline")


class EvaluatorAssignmentResponse(BaseSchema):
    """Schema for evaluator assignment response"""
    manuscript_id: int = Field(..., alias="manuscriptId")
    evaluator_id: int = Field(..., alias="evaluatorId")
    evaluator_name: str = Field(..., alias="evaluatorName")
    evaluator_email: str = Field(..., alias="evaluatorEmail")
    assigned_by_id: int = Field(..., alias="assignedById")
    assigned_at: datetime = Field(..., alias="assignedAt")
    status: EvaluatorAssignmentStatus
    response_at: Optional[datetime] = Field(None, alias="responseAt")
    evaluation_deadline: datetime = Field(..., alias="evaluationDeadline")


class EvaluatorResponseRequest(BaseSchema):
    """Schema for evaluator accepting or declining assignment"""
    accept: bool = Field(..., description="True to accept, False to decline")
