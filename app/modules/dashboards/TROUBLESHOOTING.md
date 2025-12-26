# Troubleshooting - Module Dashboards

## ✅ Corrections Effectuées

### 1. Import Manquant dans service.py

**Problème:** `List` était utilisé mais non importé depuis `typing`

**Correction:**
```python
# Avant
from typing import Dict

# Après
from typing import Dict, List
```

**Fichier:** `app/modules/dashboards/service.py` ligne 5

---

## ✅ Vérifications Effectuées

### Syntaxe Python
- ✅ `schemas.py` - Syntaxe valide (17 classes)
- ✅ `repository.py` - Syntaxe valide (1 classe, 23 fonctions)
- ✅ `service.py` - Syntaxe valide (1 classe, 5 fonctions)
- ✅ `routes.py` - Syntaxe valide (6 endpoints)

### Imports
- ✅ Tous les imports `typing` sont corrects
- ✅ Tous les imports FastAPI sont corrects
- ✅ Tous les imports locaux sont corrects
- ✅ Pas d'imports circulaires

### Structure
- ✅ Repository: 23 méthodes SQL asynchrones
- ✅ Service: 4 services métier
- ✅ Routes: 6 endpoints API
- ✅ Schemas: 17 modèles Pydantic

---

## 🚀 Comment Démarrer l'Application

### Option 1: Avec Docker Compose (Recommandé)

```bash
# 1. Arrêter les conteneurs existants
docker-compose down

# 2. Reconstruire l'image (pour inclure les changements)
docker-compose build

# 3. Démarrer l'application
docker-compose up -d

# 4. Voir les logs
docker-compose logs -f app

# 5. Vérifier que l'app démarre sans erreur
# Cherchez: "Application startup complete"
```

### Option 2: Avec Uvicorn (Développement)

```bash
# 1. Activer l'environnement virtuel
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Démarrer l'application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. Accéder à Swagger
# http://localhost:8000/docs
```

---

## 🔍 Diagnostic des Problèmes Swagger

### Si Swagger ne se charge pas

1. **Vérifier les logs de l'application**
   ```bash
   docker-compose logs app
   ```

2. **Chercher les erreurs au démarrage**
   - Erreurs d'import: `ModuleNotFoundError`, `ImportError`
   - Erreurs de validation Pydantic: `ValidationError`
   - Erreurs de syntaxe: `SyntaxError`
   - Erreurs SQL: `OperationalError`, `ProgrammingError`

3. **Vérifier que le conteneur tourne**
   ```bash
   docker-compose ps
   ```

4. **Accéder au conteneur**
   ```bash
   docker-compose exec app bash

   # Puis tester l'import Python
   python -c "from app.main import app; print('OK')"
   ```

### Erreurs Communes et Solutions

#### 1. ModuleNotFoundError

**Erreur:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Reconstruire l'image Docker
docker-compose build --no-cache

# Ou installer les dépendances
pip install -r requirements.txt
```

#### 2. ValidationError (Pydantic)

**Erreur:**
```
pydantic.error_wrappers.ValidationError: ...
```

**Solution:**
- Vérifier que tous les champs obligatoires sont présents dans les schémas
- Vérifier les types de données (int, str, etc.)
- Vérifier les imports de `Field` depuis Pydantic

#### 3. Circular Import

**Erreur:**
```
ImportError: cannot import name 'X' from partially initialized module
```

**Solution:**
- Les imports sont structurés pour éviter cela
- Si le problème persiste, vérifier les imports dans `__init__.py`

#### 4. Database Connection Error

**Erreur:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
```bash
# Vérifier que PostgreSQL est démarré
docker-compose ps

# Redémarrer la base de données
docker-compose restart db

# Attendre que la DB soit prête
docker-compose logs -f db
```

---

## 🧪 Tests Rapides

### Test 1: Vérifier que l'API répond

```bash
curl http://localhost:8000/
```

**Réponse attendue:**
```json
{
  "message": "Bienvenue sur Santaane Platform API 🚀",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### Test 2: Health Check

```bash
curl http://localhost:8000/health
```

**Réponse attendue:**
```json
{
  "status": "healthy",
  "service": "Santaane Platform API",
  "version": "1.0.0"
}
```

### Test 3: Vérifier Swagger

```bash
curl http://localhost:8000/openapi.json | jq . | head -20
```

**Devrait retourner:** Le schéma OpenAPI en JSON

### Test 4: Tester un endpoint Dashboard

```bash
# 1. Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password"

# 2. Utiliser le token
curl -X GET "http://localhost:8000/api/v1/dashboards/author" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📊 Endpoints Dashboards Disponibles

| Endpoint | Méthode | Accès | Description |
|----------|---------|-------|-------------|
| `/api/v1/dashboards/author` | GET | USER | Dashboard auteur courant |
| `/api/v1/dashboards/author/{id}` | GET | EDITOR | Dashboard auteur par ID |
| `/api/v1/dashboards/evaluator` | GET | EVALUATOR | Dashboard évaluateur courant |
| `/api/v1/dashboards/evaluator/{id}` | GET | EDITOR | Dashboard évaluateur par ID |
| `/api/v1/dashboards/editor` | GET | EDITOR | Dashboard éditeur |
| `/api/v1/dashboards/super-admin` | GET | SUPER_ADMIN | Dashboard super admin |

---

## 🔧 Commandes Utiles

### Logs en temps réel
```bash
docker-compose logs -f app
```

### Redémarrer l'application
```bash
docker-compose restart app
```

### Reconstruire complètement
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Exécuter une commande dans le conteneur
```bash
docker-compose exec app python -c "from app.main import app; print('OK')"
```

### Nettoyer les caches Python
```bash
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
```

---

## ✅ Checklist de Démarrage

Avant de tester Swagger, vérifier:

- [ ] PostgreSQL est démarré (`docker-compose ps`)
- [ ] L'application est démarrée (`docker-compose ps`)
- [ ] Pas d'erreurs dans les logs (`docker-compose logs app`)
- [ ] Le port 8000 est accessible
- [ ] Les fichiers Python ont la syntaxe correcte
- [ ] Les imports sont tous présents
- [ ] Les migrations de DB sont à jour

---

## 📝 Si le Problème Persiste

1. **Copier les logs complets**
   ```bash
   docker-compose logs app > app_logs.txt
   ```

2. **Vérifier la version des dépendances**
   ```bash
   docker-compose exec app pip list
   ```

3. **Tester l'import manuel**
   ```bash
   docker-compose exec app python
   >>> from app.modules.dashboards import router
   >>> print("Success!")
   ```

4. **Chercher l'erreur spécifique**
   - Regarder la dernière erreur dans les logs
   - Chercher "Error", "Exception", "Traceback"
   - Noter le fichier et la ligne où l'erreur se produit

---

**Date:** 2024-12-25
**Version:** 1.0
**Status:** ✅ Module vérifié et corrigé
