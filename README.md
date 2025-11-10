# Santaane API

Backend **FastAPI** pour la plateforme **Santaane**, avec gestion de base de données PostgreSQL, connexion via PgBouncer, et CLI intégré pour le contrôle des services, migrations et génération de modules.

---

## Table des matières

1. [Description](#description)
2. [Branches & Workflow Git](#branches--workflow-git)
3. [Fonctionnalités](#fonctionnalités)
4. [Technologies et dépendances](#technologies-et-dépendances)
5. [Prérequis](#prérequis)
6. [Installation et lancement](#installation-et-lancement)
7. [Utilisation du CLI](#utilisation-du-cli)
8. [Structure modulaire](#structure-modulaire)

---

## Description

Santaane API est un backend **FastAPI** conçu pour gérer toutes les fonctionnalités de la plateforme Santaane. Il offre :

* API REST performante
* Gestion des utilisateurs et modules extensibles
* Système de migration de base de données avec Alembic
* CLI pour gérer facilement les services et la base de données
* Conteneurisation via **Docker** et **Docker Compose** pour un déploiement simple

---

## Branches & Workflow Git

Le projet utilise un workflow Git simple mais efficace pour gérer dev, tests et production :

| Branche     | Usage                                                                                                                                                                                                                 |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **prod**    | La branche **production**. Jamais de push direct ici ! Connectée au serveur prod. On ne touche à rien 😎                                                                                                              |
| **preprod** | La branche **intermédiaire**. Tout doit **fonctionner parfaitement**, zéro bug ! L’historique doit rester **linéaire** → utilisez `merge --squash` et tests rigoureux avant push. C’est la dernière étape avant prod. |
| **dev**     | La branche **développement**. Ici on peut expérimenter, coder en freestyle et tester de nouvelles idées. Chill 😏                                                                                                     |

**Règles importantes** :

1. On ne push jamais directement sur `prod`.
2. Tout ce qui arrive sur `preprod` doit être testé et stable.
3. Sur `dev`, amusez-vous, mais pensez à merger régulièrement dans `preprod` une fois stable.

---

## Fonctionnalités

* ⚡ API FastAPI avec documentation automatique `/docs`
* 🗄️ PostgreSQL avec connexion via PgBouncer
* 🔧 CLI complet pour gérer les services (`start`, `stop`, `logs`, `db-reset`, etc.)
* 📦 Génération de modules avec scaffolding automatique
* 🔄 Migrations de base de données via Alembic
* 🧪 Tests unitaires avec Pytest

---

## Technologies et dépendances

### Python & FastAPI

* Python `3.10`
* FastAPI `0.115.0`
* Uvicorn `0.30.0` (avec extras `standard`)
* SQLModel `0.0.22`
* Alembic `1.14.0`
* AsyncPG `0.29.0`
* PyJWT `2.8.0`
* PassLib `1.7.4` (bcrypt)
* Pydantic Settings `2.0.0`
* Python Multipart `0.0.6`
* Email Validator `2.0.0`

### Dépendances de développement

* Pytest `8.2.0`

### Base de données

* PostgreSQL `16`
* PgBouncer pour la gestion des connexions

### Conteneurs

* Docker `24+`
* Docker Compose `v2+`

---

## Prérequis

* 🐳 Docker et Docker Compose installé et prêt à rugir 😎

---

## Installation et lancement


1. **Cloner le projet** :

```bash
git clone <repo-url>
cd santaane-api
```

2. **Créer le fichier `.env`** :

Le fichier `.env` est déjà fourni avec un exemple de configuration, vérifiez les paramètres de la base de données et JWT.

---

3. **Lancer les services** : 

Voici la partie **fun et magique** 🪄 :

Avant tout, donnez au CLI le droit de jouer :

```bash
chmod +x santaane
```

Puis laissez faire la magie 😎 :

```bash
./santaane start
```

💡 Si vous aimez la vie difficile et la sueur froide, vous pouvez toujours faire :

```bash
docker-compose up --build
```

😂 (oui, ça marche aussi, mais pourquoi se compliquer la vie ?)

Une fois lancé :

* 🌐 L’API → [http://localhost:8000](http://localhost:8000)
* 📄 Docs OpenAPI → [http://localhost:8000/docs](http://localhost:8000/docs)
* 🐘 PostgreSQL → port `5432`

Si vous voulez **voir les logs en direct** :

```bash
./santaane logs
```

---

## Utilisation du CLI

Le CLI de **Santaane API** vous permet de gérer **tous les aspects** de la plateforme : démarrage des services, migrations, base de données, logs, tests et génération de modules. Il est pensé pour être **simple, modulable et fun** 🪄.

> Le CLI s’utilise avec le fichier `santaane` à la racine du projet :

```bash
chmod +x santaane   # Donner les droits d’exécution
./santaane <commande>
```

Toutes les commandes sont détaillées ci-dessous.

---

### 🚀 Démarrage & contrôle des services

| Commande             | Description                                                                                      |
| -------------------- | ------------------------------------------------------------------------------------------------ |
| `start`, `run`, `rd` | Démarre tous les services en arrière-plan (mode détaché).                                        |
| `dev`                | Démarre les services en mode développement avec logs en direct. Appuyez sur Ctrl+C pour arrêter. |
| `stop`               | Arrête tous les services en cours d’exécution.                                                   |
| `restart`            | Redémarre tous les services.                                                                     |
| `rebuild`            | Rebuild complet des services et des images Docker puis redémarrage en mode détaché.              |

> Après un démarrage réussi, le CLI affiche les URLs de l’API, de la documentation et de la base de données.

---

### 📦 Migrations de la base de données

| Commande                | Description                                                                  |
| ----------------------- | ---------------------------------------------------------------------------- |
| `mk` / `makemigrations` | Génère une nouvelle migration Alembic automatiquement ou avec un nom fourni. |
| `migrate`               | Applique toutes les migrations disponibles (upgrade head).                   |
| `rollback`              | Annule la dernière migration appliquée (downgrade -1).                       |
| `migration-history`     | Affiche l’historique complet des migrations.                                 |
| `migration-current`     | Affiche la migration actuellement appliquée.                                 |

> Le CLI s’assure que les services sont démarrés avant d’exécuter les migrations.

---

### 🧪 Tests & Shell

| Commande        | Description                                                                                  |
| --------------- | -------------------------------------------------------------------------------------------- |
| `test`          | Lance tous les tests unitaires via Pytest.                                                   |
| `shell`         | Ouvre un shell dans le conteneur API pour interagir directement avec l’environnement.        |
| `status` / `ps` | Affiche l’état de tous les services Docker Compose.                                          |
| `clean`         | Nettoie complètement l’environnement : arrêt des services et suppression des volumes Docker. |

---

### 🗄️ Base de données

| Commande          | Description                                                                       |
| ----------------- | --------------------------------------------------------------------------------- |
| `db` / `psql`     | Ouvre une connexion interactive à PostgreSQL dans le conteneur.                   |
| `db-reset`        | Réinitialise complètement la base de données (suppression de toutes les données). |
| `db-dump`         | Crée un dump de la base de données dans `dumps/YYYYMMDD_HHMMSS/`.                |
| `db-restore`      | Restaure la base de données depuis un dump (sélection interactive).               |
| `seed-countries`  | Peuple la table des pays depuis un fichier JSON.                                  |
| `seed-cities`     | Peuple la table des villes depuis un fichier JSON.                                |

> ⚠️ `db-reset` et `db-restore` sont irréversibles. Le CLI demande une confirmation explicite.
>
> 💡 Les dumps sont automatiquement sauvegardés dans le dossier `dumps/` avec horodatage et sont exclus de Git.

---

### 📊 Logs & monitoring

| Commande        | Description                                                |
| --------------- | ---------------------------------------------------------- |
| `logs` / `voir` | Affiche les logs de l’API en direct (Ctrl+C pour quitter). |
| `logs-db`       | Affiche les logs de PostgreSQL.                            |
| `logs-all`      | Affiche tous les logs des services (API + DB).             |

---

### 🧩 Génération de modules

| Commande                       | Description                                                                                                  |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| `gm` / `gen-module` / `module` | Génère automatiquement un nouveau module complet (schemas, repository, service, routes, utils, error_codes). |

Le CLI vous demande :

1. **Nom du module** (pluriel, ex: `courses`)
2. **Prefix du router** (ex: `courses`)

Le CLI crée ensuite tous les fichiers nécessaires avec le **scaffolding complet**, prêts à être utilisés et ajoutés au routeur principal (`app/api/v1/router.py`).

---

### 🌟 Notes importantes

1. Le CLI vérifie que **Docker est en cours d’exécution** avant chaque commande nécessitant les conteneurs.
2. Le CLI est conçu pour être **futur-proof** : il gère automatiquement la mise à jour du `poetry.lock` si nécessaire.
3. Il centralise **toutes les commandes utiles** au développement, à la production et à la préproduction dans un seul outil.
4. Il fonctionne parfaitement avec la stratégie **multi-branches** :

   * `dev` → branche de développement libre, tests et expérimentations.
   * `preprod` → branche intermédiaire stable, code fonctionnel, historique linéaire (`merge & squash`).
   * `prod` → branche production, jamais de push direct, uniquement du code testé et validé.

---


### Génération de module avec magie

Pourquoi perdre du temps à créer manuellement un module quand le CLI peut tout faire ? 😏

```bash
./santaane gm
```

Il vous demandera :

1. Nom du module (ex: `courses`)
2. Prefix du router (ex: `courses`)

Et **boum** 💥 : tous les fichiers `schemas.py`, `repository.py`, `service.py`, `routes.py`, `utils.py`, `error_codes.py` et `__init__.py` sont générés automatiquement.

Après ça, ajoutez simplement le router dans `app/api/v1/router.py` et vous êtes prêts à briller ⭐.

---

## Architecture du projet

```
santaane-plateform-api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── router.py           # Router principal de l'API v1
│   ├── core/
│   │   ├── config.py               # Configuration de l'application
│   │   ├── constants.py            # 🔥 Constantes communes à tous les modules
│   │   ├── error_codes.py          # Codes d'erreur globaux
│   │   ├── logging.py              # Configuration des logs
│   │   └── security.py             # Sécurité et authentification
│   ├── middleware/
│   │   ├── exception_handler.py    # Gestion globale des exceptions
│   │   ├── logging_middleware.py   # Middleware de logging
│   │   └── cors.py                 # Configuration CORS
│   ├── models/
│   │   ├── user.py                 # Modèles SQLModel
│   │   ├── country.py
│   │   └── city.py
│   ├── modules/
│   │   └── auth/                   # Module d'authentification (exemple)
│   │       ├── __init__.py
│   │       ├── schemas.py
│   │       ├── repository.py
│   │       ├── service.py
│   │       ├── routes.py
│   │       ├── utils.py
│   │       ├── error_codes.py
│   │       └── constants.py        # 🔥 Constantes spécifiques au module
│   ├── schemas/
│   │   ├── base.py                 # Schémas de base
│   │   └── error.py                # Schémas d'erreur
│   ├── db.py                       # Configuration base de données
│   └── main.py                     # Point d'entrée de l'application
├── alembic/
│   └── versions/                   # Migrations de base de données
├── tests/                          # Tests unitaires et d'intégration
├── docker-compose.yml              # Configuration Docker Compose
├── Dockerfile                      # Image Docker de l'API
├── entrypoint.sh                   # Script de démarrage du conteneur
├── pyproject.toml                  # Dépendances Poetry
├── santaane                        # 🪄 CLI de gestion du projet
└── README.md
```

---

## Script de démarrage (entrypoint.sh)

Le fichier `entrypoint.sh` est le **point d'entrée** du conteneur Docker de l'API. Il s'exécute automatiquement au démarrage du conteneur et garantit que tout est prêt avant de lancer l'application.

### Étapes d'exécution :

1. **Attente de PostgreSQL** (30 tentatives max)
   - Vérifie que PostgreSQL est accessible via `pg_isready`
   - Attend jusqu'à ce que la connexion soit établie

2. **Attente de PGBouncer**
   - Pause de 3 secondes pour s'assurer que PGBouncer est prêt

3. **Exécution des migrations**
   - Lance automatiquement `alembic upgrade head`
   - Applique toutes les migrations en attente
   - Échoue si les migrations échouent (sécurité)

4. **Démarrage de l'application**
   - Lance Uvicorn avec FastAPI
   - Mode hot-reload activé en développement (via `--reload`)

### Utilisation dans Docker

Le script est référencé dans le `Dockerfile` :
```dockerfile
ENTRYPOINT ["/app/entrypoint.sh"]
```

Et permet de passer des arguments supplémentaires via `docker-compose.yml` :
```yaml
command: ["--reload"]  # Active le hot-reload en dev
```

### Pourquoi ce script est important

✅ **Migrations automatiques** : Plus besoin de les lancer manuellement
✅ **Vérifications de santé** : S'assure que la DB est prête
✅ **Démarrage fiable** : Évite les erreurs de connexion
✅ **Zero downtime** : Applique les migrations avant de servir les requêtes

> ⚠️ **Ne supprimez pas ce fichier** - il est essentiel au fonctionnement de l'application dans Docker.

---

## Structure modulaire

Chaque module suit cette structure standardisée :

```
app/modules/<module_name>/
├── __init__.py         # Exports du module
├── schemas.py          # Schémas Pydantic (validation)
├── repository.py       # Accès à la base de données
├── service.py          # Logique métier
├── routes.py           # Endpoints FastAPI
├── utils.py            # Utilitaires spécifiques au module
├── error_codes.py      # Codes d'erreur du module
└── constants.py        # 🔥 Constantes et enums du module
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

### error_codes.py
- Définit les codes d'erreur spécifiques au module
- Utilise des enums pour garantir la cohérence
- Exemple : `AuthErrorCode.INVALID_CREDENTIALS`

### constants.py
- **Constantes** : Valeurs fixes utilisées dans le module (toujours en MAJUSCULES)
- **Enums** : Ensembles de valeurs possibles pour un champ
- Centralise toutes les valeurs "magiques" du module
- Facilite la maintenance et évite les duplications

**Exemple** :
```python
from enum import Enum

# Enums : valeurs possibles
class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

# Constantes : valeurs fixes (toujours en MAJUSCULES)
MAX_LOGIN_ATTEMPTS = 5
PASSWORD_MIN_LENGTH = 8
SESSION_TIMEOUT_MINUTES = 30
```

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
from app.module.courses.utils import get_course_service

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
7. **Constants = Valeurs fixes** (toujours en MAJUSCULES)
8. **Error Codes = Enums** (codes d'erreur standardisés)

---

## Communication Backend ↔ Frontend

### Format de communication

**IMPORTANT** : Toute la communication entre le backend et le frontend se fait en **camelCase**.

#### Requêtes (Frontend → Backend)
Le frontend envoie toutes les données en **camelCase** :
```json
{
  "email": "user@example.com",
  "fullName": "John Doe",
  "countryId": 1
}
```

#### Réponses réussies (Backend → Frontend)
Le backend retourne les données directement en **camelCase** :
```json
{
  "id": 1,
  "email": "user@example.com",
  "fullName": "John Doe",
  "countryName": "Senegal",
  "createdAt": "2025-11-10T05:00:00",
  "updatedAt": "2025-11-10T05:00:00"
}
```

#### Réponses d'erreur (Backend → Frontend)
En cas d'erreur, le backend retourne uniquement le code d'erreur en **camelCase** :
```json
{
  "errorCode": "INVALID_CREDENTIALS"
}
```

**Aucun autre champ** (`success`, `timestamp`, `path`, `message`) n'est inclus. Le frontend gère les erreurs basé uniquement sur le `errorCode`.

---

## Gestion des erreurs et exceptions

### Format standardisé des erreurs

**Toutes les erreurs** dans l'API retournent un format JSON simple et cohérent :

```json
{
  "errorCode": "INVALID_CREDENTIALS"
}
```

Pas de champ `success`, `timestamp`, `path` ou autres informations inutiles. Juste le code d'erreur en **camelCase** que le frontend peut gérer programmatiquement.

### Types d'erreurs gérées

| Type d'erreur | Status HTTP | Exemple |
|---------------|-------------|---------|
| **Validation** | 422 | `VALIDATION_ERROR` |
| **Authentification** | 401 | `INVALID_CREDENTIALS` |
| **Autorisation** | 403 | `INSUFFICIENT_PERMISSIONS` |
| **Not Found** | 404 | `USER_NOT_FOUND` |
| **Conflict** | 409 | `EMAIL_ALREADY_EXISTS` |
| **Business Logic** | 400 | `INVALID_COUNTRY_ID` |
| **Database** | 400 | `DATABASE_ERROR` |
| **Serveur** | 500 | `INTERNAL_SERVER_ERROR` |

### Hiérarchie des error codes

#### 1. Codes globaux (`app/core/error_codes.py`)
```python
class GeneralErrorCode(str, Enum):
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
```

#### 2. Codes spécifiques aux modules (`app/modules/{module}/error_codes.py`)
```python
class AuthErrorCode(str, Enum):
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    INVALID_COUNTRY_ID = "INVALID_COUNTRY_ID"
    INVALID_CITY_ID = "INVALID_CITY_ID"
```

### Comment lever une exception

Dans le **service** :
```python
from fastapi import HTTPException, status
from app.modules.auth.error_codes import AuthErrorCode

# Lever une erreur 400
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail=AuthErrorCode.INVALID_COUNTRY_ID
)

# Lever une erreur 404
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=AuthErrorCode.USER_NOT_FOUND
)

# Lever une erreur 409
raise HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail=AuthErrorCode.EMAIL_ALREADY_EXISTS
)
```

### Gestion automatique des exceptions

L'application capture automatiquement **toutes les exceptions** via les middlewares :

- **HTTPException** → Retourne le code d'erreur fourni
- **RequestValidationError** → Retourne `VALIDATION_ERROR`
- **IntegrityError / DBAPIError** → Retourne `DATABASE_ERROR`
- **Exception (toutes les autres)** → Retourne `INTERNAL_SERVER_ERROR`

Les **logs** contiennent tous les détails techniques pour le debugging, mais le client ne reçoit que le code d'erreur.

---

## Conventions de code et standards

### 1. Nommage

| Élément | Convention | Exemple |
|---------|------------|---------|
| **Variables** | snake_case | `user_id`, `email_address` |
| **Fonctions** | snake_case | `get_user_by_id()`, `create_user()` |
| **Classes** | PascalCase | `UserService`, `AuthRepository` |
| **Constantes** | MAJUSCULES | `MAX_LOGIN_ATTEMPTS`, `DEFAULT_PAGE_SIZE` |
| **Enums** | PascalCase | `UserStatus`, `AuthTokenType` |
| **Fichiers** | snake_case | `user_service.py`, `error_codes.py` |
| **Modules (dossiers)** | snake_case | `auth/`, `user_management/` |

### 2. Communication API (camelCase obligatoire)

**TOUTE la communication avec le frontend se fait en camelCase** :
- Requêtes du frontend → camelCase
- Réponses du backend → camelCase
- Erreurs → `errorCode` (camelCase)

**Le code Python utilise snake_case** en interne uniquement.

**Exemple** :
```python
# Schéma Pydantic (API - camelCase)
class UserCreate(BaseModel):
    email: EmailStr
    fullName: str          # camelCase pour l'API
    countryId: Optional[int] = None

# Modèle SQLModel (DB - snake_case)
class User(SQLModel, table=True):
    email: str
    full_name: str         # snake_case en DB
    country_id: Optional[int] = None

# Transformation automatique dans le service
UserResponse(
    id=user.id,
    email=user.email,
    fullName=user.full_name,      # snake_case → camelCase
    countryId=user.country_id      # snake_case → camelCase
)
```

### 3. Constantes

#### Constantes communes (`app/core/constants.py`)
```python
# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Password
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

# Tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
```

#### Constantes de module (`app/modules/auth/constants.py`)
```python
# JWT
JWT_ALGORITHM = "HS256"
JWT_TOKEN_PREFIX = "Bearer"

# Security
MAX_LOGIN_ATTEMPTS = 5
ACCOUNT_LOCKOUT_DURATION_MINUTES = 15
```

### 4. Enums

**Toujours hériter de `str` et `Enum`** :
```python
class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
```

### 5. Imports

**Ordre des imports** :
1. Bibliothèques standard Python
2. Bibliothèques tierces (FastAPI, SQLModel, etc.)
3. Imports locaux (app.*)

**Exemple** :
```python
# Standard library
from typing import Optional
from datetime import datetime

# Third-party
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Local
from app.modules.auth.schemas import UserCreate, UserResponse
from app.modules.auth.service import AuthService
from app.modules.auth.error_codes import AuthErrorCode
```

### 6. Validation des données

- **Validation de format** → Pydantic (dans `schemas.py`)
- **Validation métier** → Service (dans `service.py`)
- **Validation DB** → Repository ne fait AUCUNE validation

**Exemple** :
```python
# schemas.py - Validation de format
class UserCreate(BaseModel):
    email: EmailStr                           # Valide le format email
    password: str
    countryId: Optional[int] = Field(None, gt=0)  # > 0

# service.py - Validation métier
async def register_user(self, user_data: UserCreate):
    # Vérifier que l'email n'existe pas déjà
    if await self.repository.user_exists(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=AuthErrorCode.EMAIL_ALREADY_EXISTS
        )

    # Vérifier que le pays existe
    if user_data.countryId:
        country = await self.repository.get_country_by_id(user_data.countryId)
        if not country:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AuthErrorCode.INVALID_COUNTRY_ID
            )
```

### 7. Logging

Utilisez le logger dans tous les services :
```python
from app.core.logging import get_logger

logger = get_logger(__name__)

# Logs informatifs
logger.info(f"User registered successfully: {user.email}")

# Logs d'avertissement
logger.warning(f"Login failed for email: {credentials.email}")

# Logs d'erreur
logger.error(f"Database error: {str(e)}")
```

### 8. Documentation des endpoints

**Toujours documenter les endpoints** :
```python
@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user_data: UserCreate,
    service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user

    - **email**: Unique user email
    - **password**: User password (min 8 chars)
    - **fullName**: User's full name
    - **countryId**: Optional country ID (must exist)
    - **cityId**: Optional city ID (must exist)

    Returns the created user with timestamps
    """
    return await service.register_user(user_data)
```

---
