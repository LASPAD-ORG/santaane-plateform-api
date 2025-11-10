# 🚀 Santaane Platform API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192.svg?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-enabled-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com)

API backend moderne et performante pour la plateforme Santaane, construite avec FastAPI, SQLModel, et PostgreSQL. Architecture modulaire avec système d'authentification JWT, gestion des migrations Alembic, et CLI personnalisé pour une expérience développeur optimale.

---

## 📋 Table des matières

- [Caractéristiques](#-caractéristiques)
- [Stack Technique](#-stack-technique)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Lancement du projet](#-lancement-du-projet)
- [CLI Santaane](#-cli-santaane)
- [Gestion des dépendances](#-gestion-des-dépendances)
- [Architecture](#-architecture)
- [Créer un nouveau module](#-créer-un-nouveau-module)
- [Migrations de base de données](#-migrations-de-base-de-données)
- [API Documentation](#-api-documentation)
- [Tests](#-tests)

---

## ✨ Caractéristiques

- ⚡ **FastAPI** - Framework moderne et performant pour les APIs
- 🔐 **Authentification JWT** - Système sécurisé avec OAuth2 + Bearer tokens
- 🗄️ **PostgreSQL 16** - Base de données relationnelle performante
- 🔄 **PGBouncer** - Connection pooling pour optimiser les connexions DB
- 📦 **SQLModel** - ORM moderne combinant SQLAlchemy et Pydantic
- 🔀 **Alembic** - Gestion des migrations de base de données
- 🐳 **Docker & Docker Compose** - Containerisation complète
- 🎨 **Architecture modulaire** - Organisation claire en modules métiers
- 🛠️ **CLI personnalisé** - Outil en ligne de commande pour gérer le projet
- 📝 **Code generation** - Génération automatique de modules complets
- 🔒 **Error codes system** - Gestion standardisée des erreurs
- 📊 **Swagger UI** - Documentation interactive automatique
- 🔥 **Hot reload** - Rechargement automatique en développement

---

## 🛠️ Stack Technique

### Backend

| Technologie | Version | Description |
|------------|---------|-------------|
| **Python** | 3.10+ | Langage de programmation |
| **FastAPI** | 0.115.0 | Framework web asynchrone |
| **Uvicorn** | 0.30.0 | Serveur ASGI |
| **SQLModel** | 0.0.22 | ORM (SQLAlchemy + Pydantic) |
| **Alembic** | 1.14.0 | Gestion des migrations |
| **Pydantic** | 2.0+ | Validation de données |
| **PyJWT** | 2.8.0 | Gestion des tokens JWT |
| **Passlib** | 1.7.4 | Hashing de mots de passe (bcrypt) |
| **asyncpg** | 0.29.0 | Driver PostgreSQL asynchrone |
| **python-multipart** | 0.0.6 | Support des formulaires multipart |
| **email-validator** | 2.0.0 | Validation d'emails |

### Base de données

| Technologie | Version | Description |
|------------|---------|-------------|
| **PostgreSQL** | 16 | Base de données relationnelle |
| **PGBouncer** | Latest | Connection pooling |

### DevOps

| Technologie | Version | Description |
|------------|---------|-------------|
| **Docker** | Latest | Containerisation |
| **Docker Compose** | Latest | Orchestration des conteneurs |
| **Poetry** | Latest | Gestionnaire de dépendances Python |

### Testing

| Technologie | Version | Description |
|------------|---------|-------------|
| **Pytest** | 8.2.0 | Framework de tests |

---

## 📦 Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Git**

---

## 🚀 Installation

### 1. Cloner le repository

```bash
git clone <repository-url>
cd santaane-plateform-api
```

### 2. Copier le fichier d'environnement

```bash
cp .env.example .env
```

### 3. Configurer les variables d'environnement

Éditez le fichier `.env` et modifiez les valeurs selon vos besoins (voir section [Configuration](#-configuration))

### 4. Rendre le CLI exécutable

```bash
chmod +x santaane
```

---

## ⚙️ Configuration

Le projet utilise un fichier `.env` pour centraliser toutes les variables d'environnement.

### Variables principales

```bash
# Base de données
DATABASE_URL=postgresql+psycopg2://postgres:postgres@pgbouncer:5432/santaane
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=santaane

# JWT Authentication
SECRET_KEY=your-secret-key-here-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Application
APP_NAME=Santaane API
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# CORS (origines autorisées séparées par des virgules)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://localhost:5173

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

### 🔐 Générer une clé secrète

Vous pouvez générer une clé secrète avec :

```bash
openssl rand -hex 32
```

---

## 🎯 Lancement du projet

Le projet utilise **Docker** exclusivement pour garantir un environnement de développement cohérent.

### 1. Démarrer tous les services

```bash
./santaane start    # Mode détaché (en arrière-plan)
# ou
./santaane dev      # Mode développement avec logs en direct
```

L'API sera accessible sur :
- **API** : http://localhost:8000
- **Documentation interactive (Swagger)** : http://localhost:8000/docs
- **Documentation alternative (ReDoc)** : http://localhost:8000/redoc
- **Base de données PostgreSQL** : localhost:5432

### 2. Peupler la base de données

⚠️ **IMPORTANT** : Après le premier démarrage, vous devez soit :

#### Option A : Utiliser les seeders (recommandé pour un nouveau projet)

```bash
# 1. Peupler les pays
./santaane seed-countries
# Fournir le chemin du fichier JSON (ex: slim-2.json)

# 2. Peupler les villes
./santaane seed-cities
# Fournir le chemin du fichier JSON (ex: cities.json)
```

#### Option B : Restaurer un backup existant

```bash
./santaane db-restore
# Sélectionner le dump à restaurer dans la liste
```

### 3. Vérifier que tout fonctionne

```bash
# Voir les logs
./santaane logs

# Vérifier l'état des services
./santaane status
```

### Arrêter les services

```bash
./santaane stop
```

### Redémarrer les services

```bash
./santaane restart
```

---

## 🛠️ CLI Santaane

Le projet inclut un CLI complet avec interface colorée pour gérer toutes les opérations.

### Afficher l'aide

```bash
./santaane help
```

### Commandes disponibles

#### 🚀 Démarrage & Contrôle

| Commande | Alias | Description |
|----------|-------|-------------|
| `start` | `run`, `rd` | Démarrer en mode détaché |
| `dev` | - | Démarrer avec logs en direct |
| `stop` | - | Arrêter tous les services |
| `restart` | - | Redémarrer les services |
| `rebuild` | - | Rebuild complet |

#### 📦 Migrations Database

| Commande | Alias | Description |
|----------|-------|-------------|
| `migrate` | - | Appliquer les migrations |
| `makemigrations` | `mk` | Générer une nouvelle migration |
| `migration-history` | - | Historique des migrations |
| `migration-current` | - | Migration actuelle |
| `rollback` | - | Annuler la dernière migration |
| `clear-alembic` | - | ⚠️ Vider alembic_version (DANGER) |

#### 📊 Logs & Monitoring

| Commande | Alias | Description |
|----------|-------|-------------|
| `logs` | `voir` | Logs de l'API |
| `logs-db` | - | Logs PostgreSQL |
| `logs-all` | - | Tous les logs |

#### 🗄️ Base de données

| Commande | Alias | Description |
|----------|-------|-------------|
| `db` | `psql` | Connexion PostgreSQL |
| `db-reset` | - | Réinitialiser la DB |
| `db-dump` | - | Créer un dump de la DB |
| `db-restore` | - | Restaurer un dump de la DB |
| `seed-countries` | - | Peupler les pays depuis JSON |
| `seed-cities` | - | Peupler les villes depuis JSON |

#### 🔧 Utilitaires

| Commande | Alias | Description |
|----------|-------|-------------|
| `shell` | - | Shell dans le conteneur |
| `test` | - | Lancer les tests |
| `status` | `ps` | État des services |
| `poetry-lock` | - | Mettre à jour poetry.lock |
| `clean` | - | Nettoyage complet |
| `help` | - | Afficher l'aide |

#### 🧩 Génération de code

| Commande | Alias | Description |
|----------|-------|-------------|
| `gm` | `gen-module`, `module` | Générer un nouveau module |

### Exemples d'utilisation

```bash
# Démarrer le projet
./santaane start

# Voir les logs
./santaane logs

# Créer une migration
./santaane mk "add users table"

# Générer un nouveau module
./santaane gm

# Créer un dump de la base de données
./santaane db-dump

# Voir l'état des services
./santaane status

# Mettre à jour poetry.lock après modification de pyproject.toml
./santaane poetry-lock
```

---

## 📦 Gestion des dépendances

### Ajouter ou modifier une dépendance

Si vous devez ajouter ou modifier une dépendance Python :

1. **Modifiez `pyproject.toml`** directement dans votre éditeur

2. **Mettez à jour `poetry.lock`** :
```bash
./santaane poetry-lock
```

3. **Vérifiez les changements** :
```bash
git diff poetry.lock
```

4. **Commitez les deux fichiers** :
```bash
git add pyproject.toml poetry.lock
git commit -m "chore: update dependencies"
```

5. **Rebuilder les conteneurs** pour appliquer les changements :
```bash
./santaane rebuild
```

### ⚠️ Important

- **Aucune installation locale requise** : Poetry s'exécute dans Docker, pas besoin de l'installer sur votre machine
- **Toujours commiter `poetry.lock`** : Ce fichier garantit que tous les développeurs utilisent les mêmes versions
- **Rebuilder après mise à jour** : Les dépendances sont installées au build du conteneur

---

## 🏗️ Architecture

### Structure du projet

```
santaane-plateform-api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── router.py           # Routeur principal API v1
│   ├── core/
│   │   ├── config.py               # Configuration centralisée
│   │   ├── security.py             # JWT & authentification
│   │   ├── logging.py              # Configuration des logs
│   │   └── error_codes.py          # Codes d'erreur généraux
│   ├── middleware/
│   │   └── exception_handler.py    # Gestionnaire d'exceptions global
│   ├── models/
│   │   ├── user.py                 # Modèle User
│   │   ├── student.py              # Modèle Student
│   │   └── ...
│   ├── modules/
│   │   ├── auth/                   # Module d'authentification
│   │   │   ├── __init__.py
│   │   │   ├── routes.py           # Routes HTTP
│   │   │   ├── schemas.py          # Schémas Pydantic
│   │   │   ├── service.py          # Logique métier
│   │   │   ├── repository.py       # Accès base de données
│   │   │   ├── utils.py            # Fonctions utilitaires & dépendances
│   │   │   ├── error_codes.py      # Codes d'erreur du module
│   │   │   └── constants.py        # Constantes et énumérations
│   │   └── students/               # Module students (même structure)
│   │       ├── __init__.py
│   │       ├── routes.py
│   │       ├── schemas.py
│   │       ├── service.py
│   │       ├── repository.py
│   │       ├── utils.py
│   │       ├── error_codes.py
│   │       └── constants.py
│   ├── schemas/
│   │   └── error.py                # Schéma de réponse d'erreur
│   ├── db.py                       # Configuration database
│   └── main.py                     # Point d'entrée FastAPI
├── alembic/
│   ├── versions/                   # Fichiers de migration
│   └── env.py                      # Configuration Alembic
├── tests/
│   └── ...                         # Tests unitaires et d'intégration
├── dumps/                          # Dumps de base de données (généré)
├── .env                            # Variables d'environnement (non versionné)
├── .env.example                    # Template des variables
├── docker-compose.yml              # Configuration Docker Compose
├── Dockerfile                      # Image Docker de l'application
├── pyproject.toml                  # Dépendances Poetry
├── alembic.ini                     # Configuration Alembic
├── santaane                        # CLI personnalisé
└── README.md                       # Ce fichier
```

### Pattern d'architecture

Le projet suit une **architecture modulaire** avec séparation des responsabilités :

```
┌─────────────┐
│   Routes    │  → Gestion des requêtes HTTP
│  (routes.py)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Service   │  → Logique métier et orchestration
│ (service.py)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Repository  │  → Accès aux données (DB)
│(repository.py)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Models    │  → Modèles SQLModel
│  (models/)  │
└─────────────┘
```

#### Responsabilités des couches

1. **Routes** (`routes.py`) :
   - Définition des endpoints HTTP
   - Validation des requêtes (via Pydantic)
   - Injection de dépendances
   - Retour des réponses HTTP

2. **Service** (`service.py`) :
   - Logique métier complexe
   - Orchestration des opérations
   - Gestion des erreurs métier
   - Logging

3. **Repository** (`repository.py`) :
   - Accès à la base de données
   - Requêtes SQL via SQLModel/SQLAlchemy
   - CRUD operations
   - Transactions

4. **Utils** (`utils.py`) :
   - Fonctions utilitaires
   - Factory functions pour les dépendances
   - Helpers du module

5. **Schemas** (`schemas.py`) :
   - Modèles Pydantic pour validation
   - DTOs (Data Transfer Objects)
   - Request/Response models

6. **Error Codes** (`error_codes.py`) :
   - Énumération des codes d'erreur
   - Standardisation des erreurs

7. **Constants** (`constants.py`) :
   - Énumérations du module
   - Constantes spécifiques au module

---

## 🧩 Créer un nouveau module

Le CLI inclut un générateur de modules complets.

### Utilisation

```bash
./santaane gm
```

Le générateur vous demandera :
1. **Nom du module** (pluriel, ex: `products`)
2. **Prefix du router** (sans `/`, ex: `products`)

### Ce qui est généré

Le générateur crée automatiquement :

```
app/modules/votre_module/
├── __init__.py
├── routes.py          # Routes HTTP avec endpoint exemple
├── schemas.py         # Schémas Pydantic (Create, Update, Response, Paginated)
├── service.py         # Logique métier avec méthodes CRUD
├── repository.py      # Accès base de données
├── utils.py           # Dépendances et fonctions utilitaires
├── error_codes.py     # Codes d'erreur du module
└── constants.py       # Constantes et énumérations du module
```

### Structure d'un module généré

Chaque fichier contient :

- ✅ Imports corrects
- ✅ Structure complète
- ✅ Commentaires `# À compléter` aux endroits à implémenter
- ✅ Exemples de code commentés
- ✅ Injection de dépendances configurée
- ✅ Logging configuré
- ✅ Type hints complets

### Exemple

```bash
$ ./santaane gm

📦 Nom du module (pluriel, ex: 'products'): laboratories
🔗 Prefix du router (sans '/', ex: 'products'): laboratories

✨ Module 'laboratories' créé avec succès!

📋 À faire: Ajouter le router dans app/api/v1/router.py
```

### Enregistrer le module

Après génération, ajoutez le router dans `app/api/v1/router.py` :

```python
from app.modules.laboratories.routes import router as laboratories_router

# Enregistrer le router
router.include_router(laboratories_router)
```

### Étapes suivantes

1. **Créer le modèle** dans `app/models/laboratory.py`
2. **Compléter le repository** avec les requêtes SQL
3. **Implémenter la logique** dans le service
4. **Tester les endpoints** via Swagger UI
5. **Créer une migration** : `./santaane mk "add laboratories table"`
6. **Appliquer la migration** : `./santaane migrate`

---

## 🔄 Migrations de base de données

Le projet utilise **Alembic** pour gérer les migrations de base de données.

### Créer une migration

```bash
./santaane mk "description de la migration"
```

Alembic détecte automatiquement les changements dans vos modèles et génère le fichier de migration.

### Appliquer les migrations

```bash
./santaane migrate
```

### Voir l'historique

```bash
./santaane migration-history
```

### Voir la migration actuelle

```bash
./santaane migration-current
```

### Annuler la dernière migration

```bash
./santaane rollback
```

### ⚠️ Réinitialiser l'historique Alembic (DANGER)

Si vous devez recommencer avec des migrations propres :

```bash
./santaane clear-alembic
```

**⚠️ ATTENTION - DANGER ⚠️**

Cette commande vide la table `alembic_version` qui contient l'historique des migrations.

**Conséquences** :
- Alembic ne saura plus quelles migrations ont été appliquées
- Vous devrez recréer l'historique manuellement
- Les données de la base NE SERONT PAS supprimées
- Utile uniquement pour recommencer avec des migrations propres

**Confirmation requise** : Vous devrez taper `CLEAR-ALEMBIC` pour confirmer.

Après avoir vidé alembic_version :
1. Supprimez le dossier `alembic/versions/`
2. Créez une migration initiale : `./santaane mk "initial"`
3. Appliquez-la : `./santaane migrate`

### Workflow de migration recommandé

```bash
# 1. Modifier vos modèles dans app/models/
# 2. Générer la migration
./santaane mk "add new field to user"

# 3. Vérifier le fichier de migration généré dans alembic/versions/
# 4. Appliquer la migration
./santaane migrate

# 5. Vérifier que tout fonctionne
./santaane logs
```

---

## 📚 API Documentation

### Swagger UI (recommandé)

Documentation interactive avec possibilité de tester les endpoints :

👉 http://localhost:8000/docs

### ReDoc

Documentation alternative avec un design différent :

👉 http://localhost:8000/redoc

### Authentification dans Swagger

1. Créez un utilisateur via `/api/v1/auth/register`
2. Connectez-vous via `/api/v1/auth/login` pour obtenir un token
3. Cliquez sur le bouton **"Authorize"** en haut à droite
4. Collez le token (sans "Bearer")
5. Tous les endpoints protégés sont maintenant accessibles

### Endpoints principaux

#### Authentification

- `POST /api/v1/auth/register` - Créer un compte
- `POST /api/v1/auth/login` - Se connecter (obtenir un JWT token)

#### Students (exemple)

- `GET /api/v1/students` - Liste des étudiants (avec pagination)
- `POST /api/v1/students` - Créer un étudiant
- `GET /api/v1/students/{id}` - Détails d'un étudiant
- `PUT /api/v1/students/{id}` - Mettre à jour un étudiant
- `DELETE /api/v1/students/{id}` - Supprimer un étudiant

---

## 🧪 Tests

### Lancer les tests

```bash
# Lancer les tests
./santaane test
```

### Structure des tests

```
tests/
├── test_auth.py           # Tests d'authentification
├── test_students.py       # Tests du module students
└── conftest.py            # Fixtures pytest
```

---

## 🔒 Gestion des erreurs

Le projet utilise un système de **codes d'erreur standardisés**.

### Format des réponses d'erreur

```json
{
  "success": false,
  "error_code": "INVALID_CREDENTIALS",
  "timestamp": "2025-11-10T12:34:56.789Z",
  "path": "/api/v1/auth/login"
}
```

### Codes d'erreur généraux

- `INTERNAL_SERVER_ERROR`
- `VALIDATION_ERROR`
- `UNAUTHORIZED`
- `NOT_FOUND`

### Codes d'erreur par module

Chaque module définit ses propres codes dans `error_codes.py` :

**Auth** :
- `INVALID_CREDENTIALS`
- `TOKEN_EXPIRED`
- `TOKEN_INVALID`
- `USERNAME_ALREADY_EXISTS`
- `USER_NOT_FOUND`

**Students** :
- `STUDENT_NOT_FOUND`
- `EMAIL_ALREADY_EXISTS`
- `INVALID_STUDENT_DATA`

---

## 🗄️ Base de données

### Services

- **PostgreSQL 16** : Base de données principale (port 5432)
- **PGBouncer** : Connection pooling (port 6432)

### Connexion directe

```bash
./santaane db
```

Ou manuellement :

```bash
docker exec -it santaane_db psql -U postgres -d santaane
```

### Commandes utiles

```sql
-- Lister les tables
\dt

-- Décrire une table
\d users

-- Voir les données
SELECT * FROM users;

-- Quitter
\q
```

### Backup & Restore

#### Créer un dump

```bash
./santaane db-dump
```

Les dumps sont sauvegardés dans `dumps/YYYYMMDD_HHMMSS/santaane_dump.sql`

#### Restaurer un dump

```bash
./santaane db-restore
```

Le CLI vous proposera de sélectionner un dump disponible.

### Réinitialiser la base de données

⚠️ **ATTENTION** : Supprime toutes les données !

```bash
./santaane db-reset
```

### Seed data

#### Peupler les pays

```bash
./santaane seed-countries
# Puis fournir le chemin du fichier JSON (ex: slim-2.json)
```

#### Peupler les villes

```bash
./santaane seed-cities
# Puis fournir le chemin du fichier JSON (ex: cities.json)
```

---

## 🤝 Contribution

### Workflow Git

```bash
# Créer une branche
git checkout -b feature/nouvelle-fonctionnalite

# Faire vos modifications
# ...

# Commit
git add .
git commit -m "feat: ajout de la nouvelle fonctionnalité"

# Push
git push origin feature/nouvelle-fonctionnalite

# Créer une Pull Request
```

### Conventions de commit

Utilisez [Conventional Commits](https://www.conventionalcommits.org/) :

- `feat:` - Nouvelle fonctionnalité
- `fix:` - Correction de bug
- `docs:` - Documentation
- `style:` - Formatage du code
- `refactor:` - Refactoring
- `test:` - Tests
- `chore:` - Tâches de maintenance

---

## 📝 Licence

Ce projet est privé et propriétaire.

---

## 👥 Auteurs

- **Hamadou Ba** - Développeur principal

---

## 🆘 Support

Pour toute question ou problème :

1. Consultez la documentation : http://localhost:8000/docs
2. Vérifiez les logs : `./santaane logs`
3. Ouvrez une issue sur le repository

---

## 📚 Ressources utiles

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com)
- [Alembic Documentation](https://alembic.sqlalchemy.org)
- [Pydantic Documentation](https://docs.pydantic.dev)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Fait avec ❤️ pour la plateforme Santaane**
