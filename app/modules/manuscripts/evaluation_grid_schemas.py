"""
Pydantic schemas for manuscript evaluation grids
Matches the API contract for evaluation grid system
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal


class SaveEvaluationGridRequest(BaseModel):
    """Schema for creating/updating an evaluation grid"""
    originalityOfIdeas: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Originalité des idées et des conclusions"
    )
    methodologyRigor: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Pertinence et rigueur de la méthode"
    )
    theoreticalApproach: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Approche théorique et études empiriques"
    )
    presentationClarity: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Clarté de la présentation"
    )
    strengths: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Points forts"
    )
    weaknesses: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Points faibles"
    )
    suggestions: str = Field(
        default="",
        max_length=5000,
        description="Suggestions pour améliorer le texte (optionnel)"
    )
    recommendation: Literal["accepted_with_validation", "resubmission_required", "rejected"] = Field(
        ...,
        description="Avis final"
    )


class EvaluationGridResponse(BaseModel):
    """Schema for evaluation grid response"""
    id: int
    manuscriptId: int
    evaluatorId: int
    articleTitle: str
    evaluatorName: str
    originalityOfIdeas: str
    methodologyRigor: str
    theoreticalApproach: str
    presentationClarity: str
    strengths: str
    weaknesses: str
    suggestions: str
    recommendation: str
    createdAt: datetime
    updatedAt: datetime
    submittedAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubmitEvaluationResponse(BaseModel):
    """Schema for submit evaluation response"""
    message: str
    manuscriptId: int
    evaluatorId: int
    submittedAt: datetime
    annotationsCount: int
    evaluationGrid: dict
