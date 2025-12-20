# Mentor Assignment - Documentation Technique

## 📋 Vue d'ensemble

Le module **Mentor Assignment** implémente la fonctionnalité d'assignation d'auteurs à des mentors dans la plateforme Santaane.

## 🎯 Objectifs

- ✅ Permettre aux administrateurs et éditeurs d'assigner des auteurs à des mentors
- ✅ Garantir qu'un auteur n'a qu'un seul mentor actif
- ✅ Permettre à un mentor de superviser plusieurs auteurs
- ✅ Maintenir une traçabilité complète (qui a assigné, quand, etc.)
- ✅ Implémenter une sécurité RBAC appropriée

## 🏗️ Architecture

### Modèles de Données

#### `MentorAssignment`
Table: `mentor_assignments`

```python
class MentorAssignment(SQLModel, table=True):
    id: Optional[int]                    # Primary Key
    author_id: int                       # FK to users.id
    mentor_id: int                       # FK to users.id
    assigned_by: Optional[int]           # FK to users.id (qui a assigné)
    is_active: bool = True               # Statut de l'assignation
    created_at: datetime                 # Date de création
    updated_at: datetime                 # Date de dernière modification
```

**Constraints:**
- Unique: `(author_id, is_active=True)` - Un auteur ne peut avoir qu'un seul mentor actif
- Indexes: Sur `author_id`, `mentor_id`, `(author_id, is_active)`

**Relations:**
- `author`: Relationship → User (auteur)
- `mentor`: Relationship → User (mentor)
- `assigner`: Relationship → User (qui a assigné)

### Modèle User (Adapté)

Nouvelles relations ajoutées :
```python
mentor_assignments_as_author: list["MentorAssignment"]      # Assignations de cet utilisateur comme auteur
mentor_assignments_as_mentor: list["MentorAssignment"]      # Assignations de cet utilisateur comme mentor
mentor_assignments_created: list["MentorAssignment"]        # Assignations créées par cet utilisateur
```

## 📁 Structure du Module

```
/app/modules/assign_auteur_mentor/
├── __init__.py                  # Initialisation du module
├── routes.py                    # Routes FastAPI
├── schemas.py                   # Schémas Pydantic
├── service.py                   # Logique métier
├── repository.py                # Couche données
├── error_codes.py               # Codes d'erreur
├── utils.py                     # Dépendances FastAPI
└── constants.py                 # Constantes (optionnel)
```

## 🔐 Sécurité

### Permissions

- **Création d'assignation** : Requires `SUPER_ADMIN` ou `EDITOR`
- **Modification d'assignation** : Requires `SUPER_ADMIN` ou `EDITOR`
- **Suppression d'assignation** : Requires `SUPER_ADMIN` ou `EDITOR`
- **Consultation** : Requires `Authenticated`
- **Consultation des auteurs d'un mentor** : Requires `SUPER_ADMIN`, `EDITOR`, ou le mentor lui-même

### Validations

1. **Vérification des rôles utilisateur**
   - Auteur doit avoir le rôle `AUTHOR`
   - Mentor doit avoir le rôle `MENTOR`

2. **Règles métier**
   - L'auteur et le mentor doivent être des utilisateurs différents
   - Un auteur ne peut avoir qu'un seul mentor actif (garanti par contrainte unique)
   - Les assignations précédentes sont automatiquement désactivées

3. **Traçabilité**
   - `assigned_by` enregistre qui a créé l'assignation
   - `created_at` et `updated_at` pour l'audit

## 🔌 Routes API

### 1. Créer une assignation

```
POST /api/v1/mentors/assign
Content-Type: application/json

{
  "author_id": 5,
  "mentor_id": 10
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "author_id": 5,
  "mentor_id": 10,
  "assigned_by": 1,
  "is_active": true,
  "created_at": "2025-12-19T12:30:00",
  "updated_at": "2025-12-19T12:30:00"
}
```

**Erreurs:**
- `400 Bad Request` : Auteur == Mentor, rôle invalide, utilisateur inexistant
- `403 Forbidden` : Permissions insuffisantes

---

### 2. Lister les assignations

```
GET /api/v1/mentors/assign?skip=0&limit=20
```

**Query Parameters:**
- `skip` (int, default=0) : Nombre d'éléments à ignorer
- `limit` (int, default=20, max=100) : Nombre d'éléments à retourner

**Response (200 OK):**
```json
{
  "items": [...],
  "total": 42,
  "skip": 0,
  "limit": 20,
  "has_more": true
}
```

---

### 3. Récupérer une assignation

```
GET /api/v1/mentors/assign/{assignment_id}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "author_id": 5,
  "mentor_id": 10,
  "assigned_by": 1,
  "is_active": true,
  "created_at": "2025-12-19T12:30:00",
  "updated_at": "2025-12-19T12:30:00"
}
```

**Erreurs:**
- `404 Not Found` : Assignation inexistante

---

### 4. Modifier une assignation

```
PUT /api/v1/mentors/assign/{assignment_id}
Content-Type: application/json

{
  "mentor_id": 12,
  "is_active": true
}
```

**Fields (optionnels):**
- `mentor_id` : Nouveau mentor
- `is_active` : Nouveau statut

**Response (200 OK):**
```json
{
  "id": 1,
  "author_id": 5,
  "mentor_id": 12,
  "assigned_by": 1,
  "is_active": true,
  "created_at": "2025-12-19T12:30:00",
  "updated_at": "2025-12-19T12:45:00"
}
```

---

### 5. Supprimer une assignation

```
DELETE /api/v1/mentors/assign/{assignment_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Mentor assignment deleted successfully"
}
```

---

### 6. Récupérer les auteurs d'un mentor

```
GET /api/v1/mentors/{mentor_id}/authors?skip=0&limit=20&active_only=true
```

**Query Parameters:**
- `skip` (int, default=0) : Nombre d'éléments à ignorer
- `limit` (int, default=20, max=100) : Nombre d'éléments à retourner
- `active_only` (bool, default=true) : Uniquement les assignations actives

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "author_id": 5,
      "mentor_id": 10,
      "assigned_by": 1,
      "is_active": true,
      "created_at": "2025-12-19T12:30:00",
      "updated_at": "2025-12-19T12:30:00"
    }
  ],
  "total": 3,
  "skip": 0,
  "limit": 20,
  "has_more": false
}
```

**Permissions:**
- `SUPER_ADMIN` et `EDITOR` : Accès à tous les mentors
- `MENTOR` : Accès uniquement à leurs propres auteurs
- Autres : `403 Forbidden`

---

## 🔧 Installation et Configuration

### 1. Migration de Base de Données

```bash
# Appliquer la migration
alembic upgrade head

# Ou spécifiquement
alembic upgrade 20251219_add_mentor_assignment_table
```

### 2. Vérification

```python
# Vérifier l'importation du modèle
from app.models.mentor_assignment import MentorAssignment
from app.models import MentorAssignment

# Les routes doivent être disponibles sur /api/v1/mentors/*
```

## 📊 Cas d'Utilisation

### Cas 1 : Assigner un auteur à un mentor

```python
# POST /api/v1/mentors/assign
{
  "author_id": 5,      # Jean Dupont (AUTHOR)
  "mentor_id": 10      # Marie Martin (MENTOR)
}
# Résultat: Jean Dupont est maintenant mentorné par Marie Martin
# Si Jean avait un mentor précédent, celui-ci est automatiquement désactivé
```

### Cas 2 : Changer le mentor d'un auteur

```python
# PUT /api/v1/mentors/assign/1
{
  "mentor_id": 12      # Pierre Bernard (MENTOR)
}
# Résultat: Jean Dupont est maintenant mentorné par Pierre Bernard
# L'assignation précédente avec Marie Martin est automatiquement désactivée
```

### Cas 3 : Voir tous les auteurs d'un mentor

```python
# GET /api/v1/mentors/10/authors
# Résultat: Liste de tous les auteurs mentorisés par Marie Martin
# Si l'utilisateur courant est Marie Martin, elle peut voir la liste
# Si c'est un EDITOR ou SUPER_ADMIN, il peut voir la liste
```

### Cas 4 : Désactiver une assignation (sans supprimer)

```python
# PUT /api/v1/mentors/assign/1
{
  "is_active": false
}
# Résultat: L'assignation existe toujours mais est inactive
# Jean Dupont n'a plus de mentor actif
```

## ⚠️ Gestion des Erreurs

### Codes d'Erreur Spécifiques

| Code | Description |
|------|-------------|
| `ASSIGNMENT_NOT_FOUND` | L'assignation n'existe pas |
| `AUTHOR_NOT_FOUND` | L'auteur n'existe pas |
| `MENTOR_NOT_FOUND` | Le mentor n'existe pas |
| `AUTHOR_INVALID_ROLE` | L'utilisateur n'a pas le rôle AUTHOR |
| `MENTOR_INVALID_ROLE` | L'utilisateur n'a pas le rôle MENTOR |
| `INSUFFICIENT_PERMISSIONS` | L'utilisateur n'a pas les permissions |
| `SAME_USER_ASSIGNMENT` | L'auteur et le mentor sont la même personne |
| `INVALID_ASSIGNMENT_DATA` | Les données fournies sont invalides |

## 🧪 Tests

### Tests Unitaires Recommandés

```python
# test_mentor_assignment_service.py

async def test_create_assignment_success():
    """Test création d'une assignation valide"""

async def test_create_assignment_same_user():
    """Test que auteur != mentor"""

async def test_create_assignment_insufficient_permissions():
    """Test que seul SUPER_ADMIN/EDITOR peut créer"""

async def test_create_assignment_invalid_author_role():
    """Test que l'auteur doit avoir le rôle AUTHOR"""

async def test_deactivate_previous_active():
    """Test que l'assignation précédente est désactivée"""

async def test_get_mentor_authors_permission_denied():
    """Test que seul le mentor/admin peut voir"""

async def test_update_assignment_to_new_mentor():
    """Test changement de mentor"""
```

### Commandes de Test

```bash
# Exécuter tous les tests
pytest tests/

# Exécuter les tests du module
pytest tests/modules/assign_auteur_mentor/

# Avec couverture
pytest --cov=app.modules.assign_auteur_mentor tests/modules/assign_auteur_mentor/
```

## 📝 Notes de Développement

### Points Clés d'Implémentation

1. **Déactivation automatique** : Quand on crée/modifie une assignation active, les précédentes sont désactivées
2. **Validation des rôles** : Requête DB pour vérifier les rôles à chaque création/modification
3. **Gestion des transactions** : Les opérations sont atomiques (commit ou rollback)
4. **Traçabilité** : `assigned_by` capture qui a effectué l'action

### Améliorations Futures

- [ ] Ajouter des filtres avancés (date de création, statut, etc.)
- [ ] Implémenter des webhooks pour notifier les mentors
- [ ] Ajouter un système de notifications par email
- [ ] Créer des rapports de mentorship
- [ ] Implémenter des métriques d'efficacité

## 📚 Références

- Documentation SQLModel : https://sqlmodel.tiangolo.com/
- Documentation FastAPI : https://fastapi.tiangolo.com/
- Alembic : https://alembic.sqlalchemy.org/
