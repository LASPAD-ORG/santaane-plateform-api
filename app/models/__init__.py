# Database models
# Import all your models here

# Core models
from app.models.user import User
from app.models.city import City
from app.models.country import Country
from app.models.role import Role
from app.models.user_role import UserRole

# Language model
from app.models.language import Language

# Core manuscript system
from app.models.theme import Theme
from app.models.section import Section
from app.models.manuscript_evaluator_link import ManuscriptEvaluatorLink
from app.models.manuscript import Manuscript
from app.models.manuscript_annotation import ManuscriptAnnotation
from app.models.manuscript_evaluation_grid import ManuscriptEvaluationGrid

<<<<<<< HEAD

=======
from .editorial_version import EditorialVersion
>>>>>>> feature-editorial-module
# Add all new models to this list and to __all__
__all__ = [
    # Core models
    "User",
    "City",
    "Country",
    "Role",
    "UserRole",
    # Language model
    "Language",
    # Core manuscript system
    "Theme",
    "Section",
    "ManuscriptEvaluatorLink",
    "Manuscript",
    "ManuscriptAnnotation",
    "ManuscriptEvaluationGrid",
]