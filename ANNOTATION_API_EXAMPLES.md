# 📋 Exemples d'utilisation de l'API Annotations

## ✅ Migration effectuée avec succès

La migration `20251224_204756_redesign_annotation_system_with_uuid` a été appliquée.

### Changements principaux:
- ✅ IDs UUID (format: `f1564ad2-80b3-446d-990e-c45721224e18`)
- ✅ Type d'annotation: `text`, `area`, `freetext`
- ✅ Données JSON stringifiées: `positionData`, `contentData`
- ✅ Validation JSON automatique via Pydantic
- ✅ Fonction et trigger `update_updated_at_column()` créés

---

## 🔐 Authentification

Toutes les requêtes nécessitent un token JWT Bearer:

```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## 📝 1. Créer une annotation (POST)

### Endpoint
```
POST /api/v1/manuscripts/{manuscriptId}/annotations
```

### Exemple: Annotation de type TEXT

```bash
curl -X POST http://localhost:8000/api/v1/manuscripts/123/annotations \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "annotationType": "text",
    "pageNumber": 1,
    "xPosition": 146.44,
    "yPosition": 402.74,
    "positionData": "{\"boundingRect\":{\"x1\":146.44,\"y1\":402.74,\"x2\":246.44,\"y2\":422.74,\"width\":100,\"height\":20,\"pageNumber\":1},\"rects\":[{\"x1\":146.44,\"y1\":402.74,\"x2\":246.44,\"y2\":422.74,\"pageNumber\":1}],\"pageNumber\":1}",
    "comment": "Cette partie nécessite une clarification",
    "contentData": "{\"text\":\"Texte sélectionné dans le PDF\"}"
  }'
```

### Réponse (201 Created)

```json
{
  "id": "f1564ad2-80b3-446d-990e-c45721224e18",
  "manuscriptId": 123,
  "evaluatorId": 456,
  "evaluatorName": "Jean Dupont",
  "annotationType": "text",
  "pageNumber": 1,
  "xPosition": 146.44,
  "yPosition": 402.74,
  "positionData": "{\"boundingRect\":{\"x1\":146.44,\"y1\":402.74,\"x2\":246.44,\"y2\":422.74,\"width\":100,\"height\":20,\"pageNumber\":1},\"rects\":[{\"x1\":146.44,\"y1\":402.74,\"x2\":246.44,\"y2\":422.74,\"pageNumber\":1}],\"pageNumber\":1}",
  "comment": "Cette partie nécessite une clarification",
  "contentData": "{\"text\":\"Texte sélectionné dans le PDF\"}",
  "createdAt": "2025-12-24T20:30:00.000Z",
  "updatedAt": "2025-12-24T20:30:00.000Z"
}
```

### Exemple: Annotation de type AREA

```bash
curl -X POST http://localhost:8000/api/v1/manuscripts/123/annotations \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "annotationType": "area",
    "pageNumber": 2,
    "xPosition": 50.0,
    "yPosition": 100.0,
    "positionData": "{\"boundingRect\":{\"x1\":50.0,\"y1\":100.0,\"x2\":250.0,\"y2\":200.0,\"width\":200,\"height\":100,\"pageNumber\":2}}",
    "comment": "Cette section contient une erreur",
    "contentData": null
  }'
```

### Exemple: Annotation de type FREETEXT

```bash
curl -X POST http://localhost:8000/api/v1/manuscripts/123/annotations \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "annotationType": "freetext",
    "pageNumber": 3,
    "xPosition": 200.0,
    "yPosition": 300.0,
    "positionData": "{\"x\":200.0,\"y\":300.0,\"pageNumber\":3}",
    "comment": "Note: Ajouter une référence bibliographique ici"
  }'
```

---

## 📖 2. Récupérer toutes les annotations (GET)

### Endpoint
```
GET /api/v1/manuscripts/{manuscriptId}/annotations
```

### Exemple

```bash
curl -X GET http://localhost:8000/api/v1/manuscripts/123/annotations \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

### Réponse (200 OK)

```json
[
  {
    "id": "f1564ad2-80b3-446d-990e-c45721224e18",
    "manuscriptId": 123,
    "evaluatorId": 456,
    "evaluatorName": "Jean Dupont",
    "annotationType": "text",
    "pageNumber": 1,
    "xPosition": 146.44,
    "yPosition": 402.74,
    "positionData": "{...}",
    "comment": "Cette partie nécessite une clarification",
    "contentData": "{\"text\":\"Texte sélectionné dans le PDF\"}",
    "createdAt": "2025-12-24T20:30:00.000Z",
    "updatedAt": "2025-12-24T20:30:00.000Z"
  },
  {
    "id": "a7b8c9d0-1234-5678-90ab-cdef12345678",
    "manuscriptId": 123,
    "evaluatorId": 456,
    "evaluatorName": "Jean Dupont",
    "annotationType": "area",
    "pageNumber": 2,
    "xPosition": 50.0,
    "yPosition": 100.0,
    "positionData": "{...}",
    "comment": "Cette section contient une erreur",
    "contentData": null,
    "createdAt": "2025-12-24T20:31:00.000Z",
    "updatedAt": "2025-12-24T20:31:00.000Z"
  }
]
```

**Note:** Les annotations sont ordonnées par `pageNumber` puis `createdAt`.

---

## ✏️ 3. Modifier une annotation (PUT)

### Endpoint
```
PUT /api/v1/manuscripts/annotations/{annotationId}
```

### Exemple

```bash
curl -X PUT http://localhost:8000/api/v1/manuscripts/annotations/f1564ad2-80b3-446d-990e-c45721224e18 \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "comment": "Commentaire modifié avec plus de détails"
  }'
```

### Réponse (200 OK)

```json
{
  "id": "f1564ad2-80b3-446d-990e-c45721224e18",
  "manuscriptId": 123,
  "evaluatorId": 456,
  "evaluatorName": "Jean Dupont",
  "annotationType": "text",
  "pageNumber": 1,
  "xPosition": 146.44,
  "yPosition": 402.74,
  "positionData": "{...}",
  "comment": "Commentaire modifié avec plus de détails",
  "contentData": "{\"text\":\"Texte sélectionné dans le PDF\"}",
  "createdAt": "2025-12-24T20:30:00.000Z",
  "updatedAt": "2025-12-24T20:35:00.000Z"
}
```

**Note:** Seul le créateur de l'annotation peut la modifier.

---

## 🗑️ 4. Supprimer une annotation (DELETE)

### Endpoint
```
DELETE /api/v1/manuscripts/annotations/{annotationId}
```

### Exemple

```bash
curl -X DELETE http://localhost:8000/api/v1/manuscripts/annotations/f1564ad2-80b3-446d-990e-c45721224e18 \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

### Réponse (200 OK)

```json
{
  "message": "Annotation deleted successfully"
}
```

**Note:** Seul le créateur de l'annotation peut la supprimer.

---

## ❌ Codes d'erreur

### 400 Bad Request
Données invalides (JSON mal formé dans positionData/contentData)

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "positionData"],
      "msg": "Value error, positionData must be valid JSON: ..."
    }
  ]
}
```

### 401 Unauthorized
Token invalide ou manquant

```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
- Non assigné au manuscrit
- Assignment non acceptée
- Tentative de modifier/supprimer l'annotation d'un autre évaluateur

```json
{
  "detail": "You are not assigned to this manuscript"
}
```

```json
{
  "detail": "You must accept the evaluation assignment before annotating"
}
```

```json
{
  "detail": "You can only update your own annotations"
}
```

### 404 Not Found
Annotation ou manuscrit introuvable

```json
{
  "detail": "Annotation not found"
}
```

### 422 Unprocessable Entity
Validation échouée

```json
{
  "detail": [
    {
      "type": "literal_error",
      "loc": ["body", "annotationType"],
      "msg": "Input should be 'text', 'area' or 'freetext'"
    }
  ]
}
```

---

## 🔍 Structure des données JSON

### positionData

Structure pour annotation TEXT:
```json
{
  "boundingRect": {
    "x1": 146.44,
    "y1": 402.74,
    "x2": 246.44,
    "y2": 422.74,
    "width": 100,
    "height": 20,
    "pageNumber": 1
  },
  "rects": [
    {
      "x1": 146.44,
      "y1": 402.74,
      "x2": 246.44,
      "y2": 422.74,
      "pageNumber": 1
    }
  ],
  "pageNumber": 1
}
```

Structure pour annotation AREA:
```json
{
  "boundingRect": {
    "x1": 50.0,
    "y1": 100.0,
    "x2": 250.0,
    "y2": 200.0,
    "width": 200,
    "height": 100,
    "pageNumber": 2
  }
}
```

Structure pour annotation FREETEXT:
```json
{
  "x": 200.0,
  "y": 300.0,
  "pageNumber": 3
}
```

### contentData

Pour annotation TEXT avec texte sélectionné:
```json
{
  "text": "Texte qui a été sélectionné dans le PDF"
}
```

Pour annotation AREA (optionnel):
```json
{
  "areaType": "rectangle",
  "color": "#ff0000"
}
```

Pour annotation FREETEXT:
```
null (ou omis)
```

---

## 🧪 Tests de validation

### Test 1: Validation JSON
✅ La validation Pydantic vérifie automatiquement que `positionData` et `contentData` sont des JSON valides.

### Test 2: Types d'annotation
✅ Seuls `text`, `area`, `freetext` sont acceptés.

### Test 3: Longueur du commentaire
✅ Le commentaire doit contenir entre 1 et 5000 caractères.

### Test 4: Page number
✅ Le numéro de page doit être >= 1.

---

## 📊 Base de données

### Structure de la table

```sql
CREATE TABLE manuscript_annotations (
    id VARCHAR(255) PRIMARY KEY,
    manuscript_id INTEGER NOT NULL REFERENCES manuscripts(id),
    evaluator_id INTEGER NOT NULL REFERENCES users(id),
    annotation_type VARCHAR(20) NOT NULL
        CHECK (annotation_type IN ('text', 'area', 'freetext')),
    page_number INTEGER NOT NULL CHECK (page_number >= 1),
    x_position DOUBLE PRECISION NOT NULL,
    y_position DOUBLE PRECISION NOT NULL,
    position_data TEXT NOT NULL,
    comment TEXT NOT NULL,
    content_data TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

### Index
- `idx_manuscript_annotations_manuscript` sur `manuscript_id`
- `idx_manuscript_annotations_evaluator` sur `evaluator_id`

### Trigger
- `update_manuscript_annotations_updated_at` met à jour automatiquement `updated_at`

---

## 🚀 Prochaines étapes

1. ✅ Migration appliquée
2. ✅ Validation testée
3. ⏳ Tester avec un client (Postman/frontend)
4. ⏳ Déployer le frontend mis à jour
5. ⏳ Tests end-to-end

---

## 📞 Support

En cas de problème:
1. Vérifier les logs: `./santaane logs`
2. Vérifier la migration: `./santaane migration-current`
3. Rollback si nécessaire: `./santaane rollback`
