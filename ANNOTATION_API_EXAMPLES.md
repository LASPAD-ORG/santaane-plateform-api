# =============================================================================
# Santaane Platform - Production Docker Compose for Coolify
# =============================================================================
# This compose file is optimized for deployment on Coolify.
#
# Coolify Configuration:
# 1. Set your domain in Coolify UI for the 'api' service
# 2. Configure required environment variables in Coolify UI
# 3. Coolify will automatically handle networking and proxy configuration
# =============================================================================

services:
  # ===========================================================================
  # API Service - FastAPI Application
  # ===========================================================================
  api:
    build:
      context: .
      dockerfile: Dockerfile.prod
    image: santaane-api:latest
    restart: unless-stopped

    # Environment Variables
    # Coolify will detect these and show them in the UI for configuration
    environment:
      # Database Configuration (required)
      - DATABASE_URL=${DATABASE_URL:?postgresql+psycopg2://postgres:password@pgbouncer:5432/santaane}
      - POSTGRES_USER=${POSTGRES_USER:?postgres}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:?}
      - POSTGRES_DB=${POSTGRES_DB:?santaane}

      # JWT Configuration (required)
      - SECRET_KEY=${SECRET_KEY:?}
      - ALGORITHM=${ALGORITHM:-HS256}
      - ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES:-60}

      # Application Configuration
      - APP_NAME=${APP_NAME:-Santaane API}
      - APP_VERSION=${APP_VERSION:-1.0.0}
      - ENVIRONMENT=${ENVIRONMENT:-production}
      - DEBUG=${DEBUG:-False}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}

      # CORS Configuration
      # In Coolify, set this to your frontend domain
      - CORS_ORIGINS=${CORS_ORIGINS:-*}

      # Pagination
      - DEFAULT_PAGE_SIZE=${DEFAULT_PAGE_SIZE:-20}
      - MAX_PAGE_SIZE=${MAX_PAGE_SIZE:-100}

    depends_on:
      db:
        condition: service_healthy
      pgbouncer:
        condition: service_started

    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

    labels:
      # Coolify labels
      - coolify.managed=true
      - coolify.type=application

      # Traefik labels (if using Coolify's proxy)
      - traefik.enable=true
      - traefik.http.routers.santaane-api.rule=Host(`${SERVICE_FQDN_API}`)
      - traefik.http.routers.santaane-api.entryPoints=https
      - traefik.http.routers.santaane-api.tls=true
      - traefik.http.routers.santaane-api.tls.certresolver=letsencrypt
      - traefik.http.services.santaane-api.loadbalancer.server.port=8000

  # ===========================================================================
  # Database Service - PostgreSQL 16
  # ===========================================================================
  db:
    image: postgres:16-alpine
    restart: unless-stopped

    environment:
      - POSTGRES_USER=${POSTGRES_USER:?postgres}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:?}
      - POSTGRES_DB=${POSTGRES_DB:?santaane}
      - POSTGRES_HOST_AUTH_METHOD=md5
      - POSTGRES_INITDB_ARGS=--auth-host=md5

    volumes:
      - pgdata:/var/lib/postgresql/data

    command: postgres -c password_encryption=md5

    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

    labels:
      - coolify.managed=true
      - coolify.type=database

    # Exclude from Coolify healthchecks (internal service)
    exclude_from_hc: true

  # ===========================================================================
  # PGBouncer - Connection Pooler (Bitnami Image)
  # ===========================================================================
  pgbouncer:
    image: bitnami/pgbouncer:1.25.1
    restart: unless-stopped

    environment:
      # PostgreSQL connection
      - POSTGRESQL_HOST=db
      - POSTGRESQL_PORT=5432
      - POSTGRESQL_USERNAME=${POSTGRES_USER:?postgres}
      - POSTGRESQL_PASSWORD=${POSTGRES_PASSWORD:?}
      - POSTGRESQL_DATABASE=${POSTGRES_DB:?santaane}

      # PGBouncer authentication
      - PGBOUNCER_AUTH_TYPE=md5
      - PGBOUNCER_DATABASE=${POSTGRES_DB:?santaane}

      # Pool settings
      - PGBOUNCER_POOL_MODE=transaction
      - PGBOUNCER_MAX_CLIENT_CONN=100
      - PGBOUNCER_DEFAULT_POOL_SIZE=20
      - PGBOUNCER_MIN_POOL_SIZE=10
      - PGBOUNCER_RESERVE_POOL_SIZE=10
      - PGBOUNCER_RESERVE_POOL_TIMEOUT=5

      # Ignore startup parameters (important for SQLAlchemy)
      - PGBOUNCER_IGNORE_STARTUP_PARAMETERS=extra_float_digits

    depends_on:
      db:
        condition: service_healthy

    healthcheck:
      test: ["CMD", "pg_isready", "-h", "localhost", "-p", "6432"]
      interval: 10s
      timeout: 5s
      retries: 5

    labels:
      - coolify.managed=true
      - coolify.type=service

    # Exclude from Coolify healthchecks (internal service)
    exclude_from_hc: true

# =============================================================================
# Volumes
# =============================================================================
volumes:
  pgdata:
    driver: local











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
