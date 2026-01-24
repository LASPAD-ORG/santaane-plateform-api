# Quick Setup Guide - Coolify Deployment

Ce guide rapide vous aidera à déployer votre API Santaane sur Coolify en quelques minutes.

## Fichiers Modifiés/Créés

### Fichiers Modifiés ✏️

1. **`Dockerfile.prod`** - Optimisé avec multi-stage build
   - Image plus légère (~40% de réduction de taille)
   - Utilisateur non-root pour la sécurité
   - Healthcheck intégré

2. **`docker-compose.prod.yml`** - Adapté pour Coolify
   - Labels Traefik pour le proxy
   - Variables d'environnement avec validation
   - Healthchecks pour tous les services
   - Configuration optimale pour production

3. **`entrypoint.sh`** - Adapté pour production
   - Suppression de `poetry run` (packages installés globalement)
   - 4 workers Uvicorn pour performance
   - Gestion améliorée des erreurs

### Fichiers Créés ✨

1. **`.env.production.example`** - Template des variables d'environnement
2. **`DEPLOYMENT-COOLIFY.md`** - Guide complet de déploiement
3. **`.dockerignore`** - Optimisation du build Docker
4. **`COOLIFY-SETUP.md`** - Ce fichier (guide rapide)

---

## Démarrage Rapide (5 minutes)

### Étape 1: Préparer les Variables d'Environnement

Générez une clé secrète:
```bash
openssl rand -hex 32
```

Notez ces valeurs (vous en aurez besoin dans Coolify):
- `SECRET_KEY`: (la clé générée ci-dessus)
- `POSTGRES_PASSWORD`: (un mot de passe fort pour la base de données)
- `CORS_ORIGINS`: (le domaine de votre frontend, ex: https://app.votredomaine.com)

### Étape 2: Configurer Coolify

1. Connectez-vous à Coolify
2. Créez une nouvelle ressource → **Docker Compose**
3. Sélectionnez votre dépôt Git
4. Branche: `prod`
5. Fichier compose: `docker-compose.prod.yml`

### Étape 3: Variables d'Environnement dans Coolify

Configurez ces variables **REQUISES** dans l'UI Coolify:

```env
# Sécurité (CRITIQUE)
SECRET_KEY=votre-cle-secrete-generee
POSTGRES_PASSWORD=votre-mot-de-passe-securise

# Base de données
DATABASE_URL=postgresql+psycopg2://postgres:votre-mot-de-passe@pgbouncer:5432/santaane
POSTGRES_USER=postgres
POSTGRES_DB=santaane

# CORS (IMPORTANT)
CORS_ORIGINS=https://votre-frontend.com

# Application
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=info
```

### Étape 4: Configurer le Domaine

1. Dans Coolify, allez au service **api**
2. Cliquez sur **Domains**
3. Ajoutez votre domaine (ex: `api.votredomaine.com`)
4. Coolify s'occupe du SSL automatiquement

### Étape 5: Déployer

1. Cliquez sur **Deploy**
2. Attendez 3-5 minutes
3. Vérifiez: `https://api.votredomaine.com/health`

---

## Vérification Post-Déploiement

### 1. Tester la Santé de l'API
```bash
curl https://api.votredomaine.com/health
```

Réponse attendue:
```json
{
  "status": "healthy",
  "service": "Santaane API",
  "version": "1.0.0"
}
```

### 2. Tester la Documentation
- Swagger UI: `https://api.votredomaine.com/docs`
- ReDoc: `https://api.votredomaine.com/redoc`

### 3. Vérifier les Logs
Dans Coolify → Service api → Logs

Vous devriez voir:
```
✅ PostgreSQL is ready!
✅ PGBouncer should be ready!
✅ Migrations completed successfully!
🎯 Starting FastAPI application...
```

---

## Résolution de Problèmes Rapide

### L'API ne démarre pas
1. Vérifiez les logs dans Coolify
2. Assurez-vous que `POSTGRES_PASSWORD` est identique partout
3. Vérifiez que `SECRET_KEY` est défini

### Erreurs CORS
Mettez à jour `CORS_ORIGINS` avec votre domaine frontend exact:
```env
CORS_ORIGINS=https://app.votredomaine.com
```

### Base de données non accessible
1. Vérifiez que le service `db` est en bonne santé dans Coolify
2. Vérifiez la variable `DATABASE_URL`
3. Assurez-vous que les mots de passe correspondent

### SSL/HTTPS ne fonctionne pas
1. Attendez 2-3 minutes pour la génération du certificat
2. Vérifiez que votre DNS pointe vers Coolify
3. Utilisez `dig api.votredomaine.com` pour vérifier

---

## Architecture des Services

```
Internet (HTTPS)
    ↓
Coolify Proxy (Traefik) + Let's Encrypt
    ↓
API (FastAPI - 4 workers)
    ↓
PGBouncer (Connection pooling)
    ↓
PostgreSQL 16 (Base de données)
```

### Ports Internes
- API: 8000 (accessible via proxy)
- PGBouncer: 5432 (interne uniquement)
- PostgreSQL: 5432 (interne uniquement)

---

## Caractéristiques de Production

### Sécurité ✓
- [x] Multi-stage Docker build
- [x] Utilisateur non-root
- [x] HTTPS automatique (Let's Encrypt)
- [x] Variables d'environnement requises validées
- [x] CORS configuré
- [x] Secrets non exposés

### Performance ✓
- [x] 4 workers Uvicorn
- [x] PGBouncer pour le pooling de connexions
- [x] Healthchecks configurés
- [x] Image Docker optimisée

### Fiabilité ✓
- [x] Migrations automatiques au démarrage
- [x] Restart automatique en cas d'échec
- [x] Healthchecks sur tous les services
- [x] Logs structurés

---

## Commandes Utiles

### Voir les logs en temps réel
Dans Coolify UI → Service api → Logs (mode streaming)

### Accéder au conteneur
Dans Coolify UI → Service api → Terminal

### Redéployer
Coolify UI → Bouton "Redeploy"

---

## Prochaines Étapes

1. [ ] Configurer les sauvegardes de base de données
2. [ ] Mettre en place la surveillance (monitoring)
3. [ ] Configurer les alertes
4. [ ] Tester le workflow de déploiement continu
5. [ ] Documenter les procédures de rollback

---

## Support & Documentation

- **Guide complet**: Voir `DEPLOYMENT-COOLIFY.md`
- **Variables env**: Voir `.env.production.example`
- **Documentation Coolify**: https://coolify.io/docs

---

**Bon déploiement ! 🚀**

Si vous rencontrez des problèmes, consultez d'abord `DEPLOYMENT-COOLIFY.md` pour un guide détaillé de dépannage.
