# Modules Architecture

Cette architecture modulaire permet de structurer l'API de manière scalable et maintenable.

## Structure d'un Module

Chaque module suit cette structure standardisée :

```
app/modules/<module_name>/
├── __init__.py         # Exports du module
├── schemas.py          # Schémas Pydantic (validation)
├── repository.py       # Accès à la base de données
├── service.py          # Logique métier
├── routes.py           # Endpoints FastAPI
└── utils.py            # Utilitaires spécifiques au module
```

## Responsabilités

### schemas.py
- Définit les schémas Pydantic pour validation des données
- Contient les modèles de requête et de réponse
- Exemples : `UserCreate`, `UserResponse`, `TokenResponse`

### repository.py
- Gère TOUTES les opérations base de données
- Contient les requêtes SQL/ORM
- Retourne des objets SQLModel
- **Aucune logique métier ici**

### service.py
- Contient la logique métier
- Utilise le repository pour accéder aux données
- Applique les règles de validation métier
- Gère les exceptions métier
- Transforme les données entre repository et routes

### routes.py
- Définit les endpoints FastAPI
- Gère les requêtes HTTP
- Utilise le service pour la logique
- Retourne les réponses HTTP

### utils.py
- Fonctions utilitaires spécifiques au module
- Helpers, validators, formatters, etc.

## Exemple : Créer un nouveau module "courses"

### 1. Créer la structure

```bash
mkdir -p app/modules/courses
touch app/modules/courses/{__init__.py,schemas.py,repository.py,service.py,routes.py,utils.py}
```

### 2. Définir les schemas (schemas.py)

```python
from pydantic import BaseModel
from app.schemas.base import TimestampSchema

class CourseCreate(BaseModel):
    title: str
    description: str

class CourseResponse(TimestampSchema):
    id: int
    title: str
    description: str
```

### 3. Créer le repository (repository.py)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.course import Course

class CourseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, course_id: int):
        result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        return result.scalar_one_or_none()

    async def create(self, course_data: dict):
        course = Course(**course_data)
        self.db.add(course)
        await self.db.commit()
        await self.db.refresh(course)
        return course
```

### 4. Créer le service (service.py)

```python
from app.modules.courses.repository import CourseRepository
from app.modules.courses.schemas import CourseCreate, CourseResponse
from app.core.exceptions import NotFoundError

class CourseService:
    def __init__(self, repository: CourseRepository):
        self.repository = repository

    async def create_course(self, course_data: CourseCreate):
        course = await self.repository.create(course_data.model_dump())
        return CourseResponse.model_validate(course)

    async def get_course(self, course_id: int):
        course = await self.repository.get_by_id(course_id)
        if not course:
            raise NotFoundError(f"Course {course_id} not found")
        return CourseResponse.model_validate(course)
```

### 5. Créer les routes (routes.py)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.modules.courses.repository import CourseRepository
from app.modules.courses.service import CourseService
from app.modules.courses.schemas import CourseCreate, CourseResponse

router = APIRouter(prefix="/courses", tags=["Courses"])



@router.post("", response_model=CourseResponse)
async def create_course(
    course_data: CourseCreate,
    service: CourseService = Depends(get_course_service)
):
    return await service.create_course(course_data)

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: int,
    service: CourseService = Depends(get_course_service)
):
    return await service.get_course(course_id)
```

### 6. Exporter le router (__init__.py)

```python
from app.modules.courses.routes import router

__all__ = ["router"]
```

### 7. Enregistrer dans le router principal

Dans `app/api/v1/router.py` :

```python
from app.modules.courses import router as courses_router

router.include_router(courses_router)
```

## Avantages

✅ **Modulaire** : Chaque feature est indépendante
✅ **Scalable** : Facile d'ajouter de nouveaux modules
✅ **Maintenable** : Code organisé et facile à trouver
✅ **Testable** : Chaque couche peut être testée séparément
✅ **Collaborative** : Plusieurs développeurs peuvent travailler sans conflit
✅ **Clean Architecture** : Séparation claire des responsabilités

## Principes

1. **Un module = Une fonctionnalité** (auth, students, courses, etc.)
2. **Repository = DB uniquement** (pas de logique métier)
3. **Service = Logique métier** (utilise repository)
4. **Routes = HTTP uniquement** (utilise service)
5. **Schemas = Validation** (Pydantic)
6. **Utils = Helpers** (fonctions utilitaires)
