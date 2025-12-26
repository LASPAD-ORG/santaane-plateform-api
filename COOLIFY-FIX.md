# 🔧 Fix PGBouncer - Guide Rapide

## Problème Identifié

PGBouncer essaie de se connecter à lui-même au lieu de PostgreSQL :
```
santaane = host=pgbouncer port=5432  ❌ INCORRECT
```

Au lieu de :
```
santaane = host=db port=5432  ✅ CORRECT
```

## 🚀 Solutions Disponibles

Vous avez **2 options** :

### Option 1 : Sans PGBouncer (⚡ RECOMMANDÉ - Plus Simple)

**Avantages** :
- ✅ Configuration simple
- ✅ Pas de problème de configuration PGBouncer
- ✅ PostgreSQL peut gérer 200 connexions directement
- ✅ Démarrage rapide

**Fichier** : `docker-compose.prod-simple.yaml`

---

### Option 2 : Avec PGBouncer (🔄 Bitnami Image)

**Avantages** :
- ✅ Meilleure gestion des connexions
- ✅ Image Bitnami plus fiable
- ✅ Optimisé pour production à grande échelle

**Fichier** : `docker-compose.prod.yaml` (corrigé)

---

## 📝 Instructions de Déploiement

### Si vous choisissez l'Option 1 (Sans PGBouncer)

1. **Dans Coolify**, allez dans votre ressource
2. Cliquez sur **Edit Compose File** ou **Settings**
3. Changez le fichier Docker Compose de :
   ```
   docker-compose.prod.yaml
   ```
   vers :
   ```
   docker-compose.prod-simple.yaml
   ```

4. **Mettez à jour la variable d'environnement** `DATABASE_URL` :
   ```env
   DATABASE_URL=postgresql+psycopg2://postgres:VOTRE_MOT_DE_PASSE@db:5432/santaane
   ```
   ⚠️ Notez le changement :
   - `@pgbouncer:5432` → `@db:5432`

5. Cliquez sur **Redeploy**

---

### Si vous choisissez l'Option 2 (Avec PGBouncer Bitnami)

1. **Commitez et pushez les modifications** :
   ```bash
   git add docker-compose.prod.yaml .env.production.example
   git commit -m "fix: Use Bitnami PGBouncer image"
   git push origin prod
   ```

2. **Dans Coolify**, vérifiez la variable `DATABASE_URL` :
   ```env
   DATABASE_URL=postgresql+psycopg2://postgres:VOTRE_MOT_DE_PASSE@pgbouncer:6432/santaane
   ```
   ⚠️ Port important : **6432** (Bitnami PGBouncer port)

3. Cliquez sur **Redeploy**

---

## ✅ Vérification Post-Déploiement

### 1. Vérifiez les logs de la base de données
Dans Coolify → Service **db** → Logs

Vous devriez voir :
```
database system is ready to accept connections
```

### 2. Vérifiez les logs de PGBouncer (si Option 2)
Dans Coolify → Service **pgbouncer** → Logs

Vous devriez voir :
```
LOG database 'santaane' defined
LOG listening on 0.0.0.0:6432
```

### 3. Vérifiez les logs de l'API
Dans Coolify → Service **api** → Logs

Vous devriez voir :
```
✅ PostgreSQL is ready!
✅ Migrations completed successfully!
🎯 Starting FastAPI application...
```

### 4. Testez l'API
```bash
curl https://votre-domaine.com/health
```

Réponse attendue :
```json
{
  "status": "healthy",
  "service": "Santaane API",
  "version": "1.0.0"
}
```

---

## 🆘 En cas de problème

### Erreur : "asyncio.exceptions.TimeoutError"

**Cause** : L'API ne peut pas se connecter à la base de données

**Solution** :
1. Vérifiez que `DATABASE_URL` utilise le bon port :
   - Sans PGBouncer : `@db:5432`
   - Avec PGBouncer : `@pgbouncer:6432`

2. Vérifiez que `POSTGRES_PASSWORD` est identique partout

3. Redémarrez tous les services dans Coolify

---

### PGBouncer toujours en erreur (Option 2)

**Solution de secours** : Passez à l'Option 1 (sans PGBouncer)

C'est une solution valide pour la plupart des cas d'usage. PostgreSQL peut gérer 200 connexions simultanées, ce qui est largement suffisant pour commencer.

---

## 🎯 Recommandation

**Pour démarrer rapidement** : Utilisez **Option 1** (sans PGBouncer)

**Avantages** :
- Configuration testée et fiable
- Moins de complexité
- Parfait pour MVP et petite/moyenne échelle
- Vous pourrez toujours ajouter PGBouncer plus tard si nécessaire

**Quand ajouter PGBouncer ?**
- Quand vous avez 100+ utilisateurs simultanés
- Quand vous voyez des problèmes de "too many connections"
- Quand vous voulez optimiser les ressources DB

---

## 📋 Checklist de Déploiement

- [ ] Choisir Option 1 ou Option 2
- [ ] Configurer le bon fichier docker-compose dans Coolify
- [ ] Mettre à jour `DATABASE_URL` avec le bon port
- [ ] Vérifier que `POSTGRES_PASSWORD` est défini
- [ ] Vérifier que `SECRET_KEY` est défini
- [ ] Redéployer dans Coolify
- [ ] Vérifier les logs de tous les services
- [ ] Tester `/health` endpoint
- [ ] Tester `/docs` (Swagger UI)

---

**Bon déploiement ! 🚀**

Si vous avez toujours des problèmes, partagez les logs complets de l'API.
