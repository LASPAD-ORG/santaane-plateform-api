# Module Manuscripts

Module complet de gestion des manuscrits pour la plateforme Santaane.

## Vue d'ensemble

Ce module gère l'intégralité du cycle de vie des manuscrits scientifiques :
- Création et modification de manuscrits
- Gestion des versions successives
- Soumission pour évaluation
- Discussions et commentaires
- Timeline et historique

## Endpoints disponibles

### Manuscrits (CRUD)

- `GET /api/v1/manuscripts` - Liste des manuscrits de l'utilisateur
- `GET /api/v1/manuscripts/{id}` - Détails d'un manuscrit
- `POST /api/v1/manuscripts` - Créer un nouveau manuscrit (multipart/form-data)
- `PUT /api/v1/manuscripts/{id}` - Mettre à jour un manuscrit (brouillon uniquement)
- `DELETE /api/v1/manuscripts/{id}` - Supprimer un manuscrit (brouillon uniquement)
- `POST /api/v1/manuscripts/{id}/submit` - Soumettre pour évaluation
- `POST /api/v1/manuscripts/{id}/archive` - Archiver un manuscrit
- `POST /api/v1/manuscripts/{id}/unarchive` - Désarchiver un manuscrit

### Versions

- `GET /api/v1/manuscripts/{id}/versions` - Liste des versions
- `POST /api/v1/manuscripts/{id}/versions` - Uploader une nouvelle version (multipart/form-data)

### Timeline et discussions

- `GET /api/v1/manuscripts/{id}/timeline` - Historique du manuscrit
- `GET /api/v1/manuscripts/{id}/discussions` - Liste des discussions
- `POST /api/v1/manuscripts/{id}/discussions` - Créer une nouvelle discussion
- `POST /api/v1/manuscripts/discussions/{discussionId}/replies` - Répondre à une discussion

### Commentaires d'évaluation

- `GET /api/v1/manuscripts/{id}/comments` - Commentaires des évaluateurs

### Catégories

- `GET /api/v1/categories` - Liste des catégories disponibles

## Architecture

```
app/modules/manuscripts/
├── routes.py          # Endpoints API
├── service.py         # Logique métier
├── repository.py      # Accès base de données
├── schemas.py         # Schémas Pydantic
├── utils.py           # Dépendances et utilitaires
├── error_codes.py     # Codes d'erreur
└── constants.py       # Constantes
```

## Modèles de données

Le module utilise les modèles suivants (dans `app/models/`) :
- `Manuscript` - Manuscrit principal
- `ManuscriptVersion` - Versions successives
- `ManuscriptFile` - Fichiers attachés
- `ManuscriptDiscussion` - Discussions
- `Category` - Catégories de manuscrits
- `ReviewComment` - Commentaires d'évaluation
- `ReviewResponse` - Réponses des évaluateurs

## Upload de fichiers

Le module supporte l'upload de fichiers via `multipart/form-data` :

### Créer un manuscrit avec fichiers

```bash
POST /api/v1/manuscripts
Content-Type: multipart/form-data

- title: string (requis)
- abstract: string (requis)
- keywords: string (requis)
- categoryId: integer (requis)
- coverImage: file (optionnel)
- manuscriptFile: file (optionnel)
```

### Uploader une nouvelle version

```bash
POST /api/v1/manuscripts/{id}/versions
Content-Type: multipart/form-data

- title: string (requis)
- abstract: string (optionnel)
- keywords: string (optionnel)
- changesSummary: string (requis)
- manuscriptFile: file (requis)
```

## Statuts des manuscrits

Les manuscrits passent par différents statuts (définis dans `app/models/enums.py`) :
- `draft` - Brouillon
- `submitted` - Soumis
- `under_review` - En cours d'évaluation
- `revision_requested` - Révision demandée
- `revised` - Révisé
- `accepted` - Accepté
- `rejected` - Rejeté
- `published` - Publié
- `withdrawn` - Retiré

## Sécurité et permissions

- Tous les endpoints nécessitent une authentification JWT
- **Auteurs** : peuvent créer, modifier, supprimer (brouillons uniquement), archiver leurs manuscrits
- **Évaluateurs** : ont accès en lecture aux manuscrits qui leur sont assignés
- **Éditeurs** : ont accès en lecture aux manuscrits qui leur sont assignés
- Seuls les brouillons peuvent être modifiés/supprimés
- L'accès aux manuscrits est vérifié pour chaque opération (auteur, évaluateur assigné, ou éditeur assigné)

## Validation des fichiers

### Formats autorisés
- **Manuscrits** : PDF (.pdf), Word (.doc, .docx)
- **Images de couverture** : JPG, PNG, GIF, WEBP

### Tailles maximales
- **Manuscrits** : 50 MB
- **Images de couverture** : 5 MB

La validation vérifie à la fois l'extension du fichier et le type MIME pour garantir la sécurité.

## Fichiers

Les fichiers uploadés sont stockés dans `app/uploads/` avec le format :
```
manuscript_{manuscript_id}_{file_type}_{timestamp}_{original_filename}
```

Lors de la suppression d'un manuscrit, tous les fichiers associés sont automatiquement supprimés du disque.

## Archivage

Les manuscrits peuvent être archivés/désarchivés via :
- `POST /api/v1/manuscripts/{id}/archive`
- `POST /api/v1/manuscripts/{id}/unarchive`

Les manuscrits archivés restent accessibles mais peuvent être filtrés dans les listes.

## TODO / Améliorations futures

- [ ] Ajouter le système de notifications complet
- [ ] Ajouter des tests unitaires et d'intégration
- [ ] Implémenter la recherche full-text
- [ ] Ajouter la génération de PDF à partir des versions Word

## Exemples d'utilisation

Voir le fichier `API_PAYLOAD_EXAMPLES.json` à la racine du projet frontend pour des exemples de payloads complets.
