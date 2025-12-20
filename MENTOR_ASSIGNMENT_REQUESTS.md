"""
EXEMPLES DE REQUÊTES - MENTOR ASSIGNMENT API
==============================================

AUTHENTIFICATION :
Pour tous les endpoints, ajouter le header :
Authorization: Bearer {access_token}


1. CRÉER UNE ASSIGNATION DE MENTOR
===================================

POST /api/v1/mentors/assign
Content-Type: application/json

{
  "author_id": 5,
  "mentor_id": 10
}

Réponse (201 Created):
{
  "id": 1,
  "author_id": 5,
  "mentor_id": 10,
  "assigned_by": 1,
  "is_active": true,
  "created_at": "2025-12-19T12:30:00",
  "updated_at": "2025-12-19T12:30:00"
}

Erreurs possibles:
- 403 Forbidden : L'utilisateur n'est pas SUPER_ADMIN ou EDITOR
- 400 Bad Request : 
  * author_id == mentor_id
  * Auteur n'a pas le rôle AUTHOR
  * Mentor n'a pas le rôle MENTOR
- 404 Not Found : Auteur ou Mentor n'existe pas


2. LISTER TOUTES LES ASSIGNATIONS
==================================

GET /api/v1/mentors/assign?skip=0&limit=20
Content-Type: application/json

Réponse (200 OK):
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
    },
    {
      "id": 2,
      "author_id": 6,
      "mentor_id": 10,
      "assigned_by": 1,
      "is_active": true,
      "created_at": "2025-12-19T12:35:00",
      "updated_at": "2025-12-19T12:35:00"
    }
  ],
  "total": 25,
  "skip": 0,
  "limit": 20,
  "has_more": true
}


3. RÉCUPÉRER UNE ASSIGNATION PAR ID
====================================

GET /api/v1/mentors/assign/1
Content-Type: application/json

Réponse (200 OK):
{
  "id": 1,
  "author_id": 5,
  "mentor_id": 10,
  "assigned_by": 1,
  "is_active": true,
  "created_at": "2025-12-19T12:30:00",
  "updated_at": "2025-12-19T12:30:00"
}

Erreurs possibles:
- 404 Not Found : Assignation n'existe pas


4. MODIFIER UNE ASSIGNATION
============================

PUT /api/v1/mentors/assign/1
Content-Type: application/json

Cas 1 - Changer le mentor:
{
  "mentor_id": 12
}

Cas 2 - Désactiver l'assignation:
{
  "is_active": false
}

Cas 3 - Les deux:
{
  "mentor_id": 12,
  "is_active": true
}

Réponse (200 OK):
{
  "id": 1,
  "author_id": 5,
  "mentor_id": 12,
  "assigned_by": 1,
  "is_active": true,
  "created_at": "2025-12-19T12:30:00",
  "updated_at": "2025-12-19T12:45:00"
}

Erreurs possibles:
- 403 Forbidden : L'utilisateur n'est pas SUPER_ADMIN ou EDITOR
- 400 Bad Request :
  * mentor_id == author_id
  * Nouveau mentor n'a pas le rôle MENTOR
  * Aucune donnée valide fournie
- 404 Not Found : Assignation n'existe pas


5. SUPPRIMER UNE ASSIGNATION
=============================

DELETE /api/v1/mentors/assign/1
Content-Type: application/json

Réponse (200 OK):
{
  "success": true,
  "message": "Mentor assignment deleted successfully"
}

Erreurs possibles:
- 403 Forbidden : L'utilisateur n'est pas SUPER_ADMIN ou EDITOR
- 404 Not Found : Assignation n'existe pas


6. RÉCUPÉRER LES AUTEURS D'UN MENTOR
=====================================

GET /api/v1/mentors/10/authors?skip=0&limit=20&active_only=true

Paramètres de requête:
- skip: (optionnel, défaut: 0) Nombre d'éléments à ignorer
- limit: (optionnel, défaut: 20, max: 100) Nombre d'éléments à retourner
- active_only: (optionnel, défaut: true) Si true, retourne uniquement les assignations actives

Réponse (200 OK):
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
    },
    {
      "id": 2,
      "author_id": 6,
      "mentor_id": 10,
      "assigned_by": 1,
      "is_active": true,
      "created_at": "2025-12-19T12:35:00",
      "updated_at": "2025-12-19T12:35:00"
    }
  ],
  "total": 2,
  "skip": 0,
  "limit": 20,
  "has_more": false
}

Permissions:
- SUPER_ADMIN et EDITOR peuvent voir les auteurs de n'importe quel mentor
- Un MENTOR peut voir uniquement ses propres auteurs (si mentor_id == current_user.id)
- Les autres rôles reçoivent 403 Forbidden

Erreurs possibles:
- 403 Forbidden : Permissions insuffisantes
- 404 Not Found : Mentor n'existe pas


CAS DE TEST - ERREURS
=====================

Cas 1 - Utilisateur sans permission:
POST /api/v1/mentors/assign
Headers: Authorization: Bearer {token_author}
Body: {"author_id": 5, "mentor_id": 10}
Réponse: 403 Forbidden - "INSUFFICIENT_PERMISSIONS"

Cas 2 - Auteur = Mentor:
POST /api/v1/mentors/assign
Body: {"author_id": 5, "mentor_id": 5}
Réponse: 400 Bad Request - "SAME_USER_ASSIGNMENT"

Cas 3 - Auteur n'a pas le rôle AUTHOR:
POST /api/v1/mentors/assign
Body: {"author_id": 2, "mentor_id": 10}
(où user 2 n'a pas le rôle AUTHOR)
Réponse: 400 Bad Request - "AUTHOR_INVALID_ROLE"

Cas 4 - Mentor n'a pas le rôle MENTOR:
POST /api/v1/mentors/assign
Body: {"author_id": 5, "mentor_id": 3}
(où user 3 n'a pas le rôle MENTOR)
Réponse: 400 Bad Request - "MENTOR_INVALID_ROLE"

Cas 5 - Assignation inexistante:
GET /api/v1/mentors/assign/999
Réponse: 404 Not Found - "ASSIGNMENT_NOT_FOUND"


FLUX COMPLET D'UTILISATION
===========================

1. Login pour obtenir le token d'un éditeur
   POST /api/v1/auth/login
   Body: {"email": "editor@example.com", "password": "..."}
   → Récupérer le access_token

2. Vérifier que l'auteur a le rôle AUTHOR
   GET /api/v1/users/5
   
3. Vérifier que le mentor a le rôle MENTOR
   GET /api/v1/users/10

4. Créer l'assignation
   POST /api/v1/mentors/assign
   Body: {"author_id": 5, "mentor_id": 10}

5. Récupérer les auteurs du mentor
   GET /api/v1/mentors/10/authors

6. Modifier l'assignation (changer de mentor)
   PUT /api/v1/mentors/assign/1
   Body: {"mentor_id": 12}

7. Supprimer l'assignation
   DELETE /api/v1/mentors/assign/1


CURL EXAMPLES
=============

1. Créer une assignation:
curl -X POST http://localhost:8000/api/v1/mentors/assign \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"author_id": 5, "mentor_id": 10}'

2. Récupérer les auteurs:
curl -X GET "http://localhost:8000/api/v1/mentors/10/authors?skip=0&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"

3. Modifier une assignation:
curl -X PUT http://localhost:8000/api/v1/mentors/assign/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mentor_id": 12}'

4. Supprimer une assignation:
curl -X DELETE http://localhost:8000/api/v1/mentors/assign/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
"""
