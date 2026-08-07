"""
Pydantic schemas for manuscript evaluation grids
Matches the API contract for evaluation grid system
"""
from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Optional, Literal


class SaveEvaluationGridRequest(BaseModel):
    """Schema for creating/updating an evaluation grid (interne ou externe)"""
    evaluatorType: Literal["internal", "external"] = Field(
        default="external",
        description="Type d'évaluateur: 'internal' ou 'external' (détermine les champs requis)"
    )

    # --- Champs communs / externes (optionnels au niveau Pydantic, validés selon le type) ---
    originalityOfIdeas: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Originalité des idées et des conclusions"
    )
    methodologyRigor: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Pertinence et rigueur de la méthode"
    )
    theoreticalApproach: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Approche théorique et études empiriques"
    )
    presentationClarity: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Clarté de la présentation"
    )
    strengths: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Points forts"
    )
    weaknesses: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Points faibles"
    )
    suggestions: str = Field(
        default="",
        max_length=5000,
        description="Suggestions pour améliorer le texte (optionnel)"
    )

    # --- Champs spécifiques à la grille interne ---
    editorialLineFit: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Adéquation à la ligne éditoriale (grille interne)"
    )
    globalOpinion: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Avis global sur le manuscrit (grille interne)"
    )

    recommendation: str = Field(
        ...,
        description="Avis final (valeurs différentes selon le type d'évaluateur)"
    )

    @model_validator(mode="after")
    def validate_by_type(self):
        external_decisions = {
            "accepted_with_validation",
            "resubmission_required",
            "rejected",
        }
        internal_decisions = {
            "internal_accepted_after_revision",
            "internal_to_external",
            "internal_rejected",
        }

        def require(value, label):
            if value is None or (isinstance(value, str) and value.strip() == ""):
                raise ValueError(f"Le champ '{label}' est requis.")

        if self.evaluatorType == "external":
            require(self.originalityOfIdeas, "originalityOfIdeas")
            require(self.methodologyRigor, "methodologyRigor")
            require(self.theoreticalApproach, "theoreticalApproach")
            require(self.presentationClarity, "presentationClarity")
            require(self.strengths, "strengths")
            require(self.weaknesses, "weaknesses")
            if self.recommendation not in external_decisions:
                raise ValueError(
                    "Décision invalide pour un évaluateur externe. "
                    f"Valeurs attendues: {sorted(external_decisions)}"
                )
        else:  # internal
            require(self.editorialLineFit, "editorialLineFit")
            require(self.originalityOfIdeas, "originalityOfIdeas")
            require(self.theoreticalApproach, "theoreticalApproach")
            require(self.globalOpinion, "globalOpinion")
            if self.recommendation not in internal_decisions:
                raise ValueError(
                    "Décision invalide pour un évaluateur interne. "
                    f"Valeurs attendues: {sorted(internal_decisions)}"
                )
        return self


class EvaluationGridResponse(BaseModel):
    """Schema for evaluation grid response"""
    id: int
    manuscriptId: int
    evaluatorId: int
    articleTitle: str
    evaluatorName: str
    originalityOfIdeas: Optional[str] = None
    methodologyRigor: Optional[str] = None
    theoreticalApproach: Optional[str] = None
    presentationClarity: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    suggestions: Optional[str] = None
    editorialLineFit: Optional[str] = None
    globalOpinion: Optional[str] = None
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


class ManuscriptEvaluationStatusResponse(BaseModel):
    """Schema for manuscript evaluation status response"""
    manuscriptId: int
    evaluationStatus: str
    assignedEvaluators: int
    submittedEvaluations: int
    isFullyEvaluated: bool
    progress: float = Field(description="Pourcentage de complétion (0-100)")

    class Config:
        from_attributes = True