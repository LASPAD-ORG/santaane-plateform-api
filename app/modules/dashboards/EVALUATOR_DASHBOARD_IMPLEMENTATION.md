# Dashboard Évaluateur - Implémentation

## ✅ Status: Implémenté

**Date:** 2024-12-25
**Endpoint:** `GET /api/v1/dashboards/evaluator`
**Accès:** EVALUATOR, SUPER_ADMIN

---

## 📊 Spécifications Demandées vs Implémentées

| # | Métrique Demandée | Status | Localisation dans la Réponse |
|---|-------------------|--------|------------------------------|
| 1 | Nombre total de manuscrits en attente d'évaluation | ✅ | `stats.awaiting_evaluation` |
| 2 | Nombre total de manuscrits en cours d'évaluation | ✅ | `stats.in_progress` |
| 3 | Nombre total de manuscrits évalués | ✅ | `stats.evaluated` |
| 4 | Diagramme en barre (en attente, en cours, évalués) | ✅ | `status_bar_chart` |
| 5 | Courbe du nombre de manuscrits évalués (semaine/mois/année) | ✅ | `weekly_evaluations`, `monthly_evaluations`, `yearly_evaluations` |

**Résultat:** 5/5 métriques implémentées ✅

---

## 🔧 Implémentation Technique

### Logique des Statuts

La classification des manuscrits est basée sur la table **`ManuscriptEvaluationGrid`** et **`ManuscriptEvaluatorLink`**:

```python
# 1. Récupérer tous les manuscrits assignés avec status ACCEPTED
assigned_links = get all ManuscriptEvaluatorLink where:
    - evaluator_id == current_evaluator
    - status == ACCEPTED

# 2. Pour chaque manuscrit assigné, vérifier l'état de la grille
for link in assigned_links:
    grid = get ManuscriptEvaluationGrid where:
        - manuscript_id == link.manuscript_id
        - evaluator_id == current_evaluator

    if grid is None:
        # Pas de grille créée → En attente
        awaiting_evaluation += 1

    elif grid.submitted_at is None:
        # Grille existe mais pas soumise → En cours
        in_progress += 1

    else:
        # Grille soumise (submitted_at NOT NULL) → Évalué
        evaluated += 1
```

### États Possibles

| État | Condition | Description |
|------|-----------|-------------|
| **En attente** | Assigné (ACCEPTED) + Pas de grille | Évaluateur a accepté mais n'a pas encore commencé |
| **En cours** | Grille existe + `submitted_at` NULL | Évaluateur travaille sur l'évaluation (brouillon) |
| **Évalué** | Grille existe + `submitted_at` NOT NULL | Évaluation complétée et soumise |

---

## 📁 Fichiers Modifiés/Créés

### 1. **`repository.py`** - 5 nouvelles méthodes

```python
# Méthode principale
async def get_evaluator_manuscript_stats(evaluator_id: int) -> Dict[str, int]
    """Compte les manuscrits par statut (awaiting, in_progress, evaluated)"""

# Méthode pour bar chart
async def get_evaluator_status_distribution(evaluator_id: int) -> Dict[str, int]
    """Distribution pour graphique en barres"""

# Méthodes pour time series
async def get_evaluator_evaluations_by_week(evaluator_id: int, weeks: int = 12)
async def get_evaluator_evaluations_by_month(evaluator_id: int, months: int = 12)
async def get_evaluator_evaluations_by_year(evaluator_id: int, years: int = 5)
```

**Points clés:**
- Utilise `ManuscriptEvaluationGrid.submitted_at` pour compter les évaluations complétées
- Filtre par `submitted_at.isnot(None)` pour ne compter que les évaluations soumises
- Utilise `date_trunc()` PostgreSQL pour grouper par période

### 2. **`schemas.py`**

```python
class EvaluatorStatsResponse(BaseModel):
    """Statistics for evaluator's assigned manuscripts"""
    awaiting_evaluation: int
    in_progress: int
    evaluated: int

class EvaluatorDashboardResponse(BaseModel):
    """Complete dashboard response for evaluator"""
    stats: EvaluatorStatsResponse
    status_bar_chart: BarChartResponse
    weekly_evaluations: TimeSeriesResponse
    monthly_evaluations: TimeSeriesResponse
    yearly_evaluations: TimeSeriesResponse
```

### 3. **`service.py`**

```python
async def get_evaluator_dashboard(evaluator_id: int) -> EvaluatorDashboardResponse:
    """Orchestration complète du dashboard évaluateur"""
    # Récupère toutes les données
    # Construit les réponses structurées
    # Retourne le dashboard complet

def _build_evaluator_bar_chart(distribution: Dict[str, int]) -> BarChartResponse:
    """Construction du graphique avec couleurs et labels français"""
    # Orange (#F59E0B) → En attente
    # Bleu (#3B82F6) → En cours
    # Vert (#22C55E) → Évalués
```

### 4. **`routes.py`**

```python
@router.get("/evaluator", response_model=EvaluatorDashboardResponse)
async def get_evaluator_dashboard(
    current_user: User = Depends(require_role(UserRole.EVALUATOR)),
    service: DashboardService = Depends(get_dashboard_service)
):
    """Dashboard pour l'évaluateur authentifié"""

@router.get("/evaluator/{evaluator_id}", response_model=EvaluatorDashboardResponse)
async def get_evaluator_dashboard_by_id(
    evaluator_id: int,
    current_user: User = Depends(require_role(UserRole.EDITOR)),
    service: DashboardService = Depends(get_dashboard_service)
):
    """Dashboard d'un évaluateur spécifique (EDITOR/SUPER_ADMIN)"""
```

---

## 📊 Structure de la Réponse

```json
{
  "stats": {
    "awaiting_evaluation": 5,
    "in_progress": 3,
    "evaluated": 12
  },
  "status_bar_chart": {
    "title": "Répartition des manuscrits par statut d'évaluation",
    "data": [
      {
        "label": "En attente",
        "value": 5,
        "color": "#F59E0B"
      },
      {
        "label": "En cours",
        "value": 3,
        "color": "#3B82F6"
      },
      {
        "label": "Évalués",
        "value": 12,
        "color": "#22C55E"
      }
    ]
  },
  "weekly_evaluations": {
    "period_type": "week",
    "title": "Évaluations complétées par semaine (12 dernières semaines)",
    "data": [
      { "period": "2024-W50", "count": 2 },
      { "period": "2024-W51", "count": 1 },
      { "period": "2024-W52", "count": 3 }
    ]
  },
  "monthly_evaluations": {
    "period_type": "month",
    "title": "Évaluations complétées par mois (12 derniers mois)",
    "data": [
      { "period": "2024-10", "count": 3 },
      { "period": "2024-11", "count": 5 },
      { "period": "2024-12", "count": 4 }
    ]
  },
  "yearly_evaluations": {
    "period_type": "year",
    "title": "Évaluations complétées par année (5 dernières années)",
    "data": [
      { "period": "2023", "count": 8 },
      { "period": "2024", "count": 12 }
    ]
  }
}
```

---

## 🚀 Comment Tester

### 1. Via Swagger UI

```
http://localhost:8000/docs
```

- Naviguez vers la section **"Dashboards"**
- Cliquez sur `GET /api/v1/dashboards/evaluator`
- Authentifiez-vous avec un token EVALUATOR
- Cliquez sur **"Execute"**

### 2. Via curl

```bash
# 1. Se connecter en tant qu'évaluateur
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=evaluator@example.com&password=yourpassword"

# 2. Récupérer le dashboard évaluateur
curl -X GET "http://localhost:8000/api/v1/dashboards/evaluator" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  | jq .

# 3. Filtrer pour voir seulement les stats
curl -X GET "http://localhost:8000/api/v1/dashboards/evaluator" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  | jq '.stats'

# 4. Voir le graphique en barres
curl -X GET "http://localhost:8000/api/v1/dashboards/evaluator" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  | jq '.status_bar_chart'
```

### 3. Via httpie

```bash
# Installation: pip install httpie

# Login
http POST http://localhost:8000/api/v1/auth/login \
  username=evaluator@example.com \
  password=yourpassword

# Get dashboard
http GET http://localhost:8000/api/v1/dashboards/evaluator \
  Authorization:"Bearer YOUR_TOKEN"
```

---

## 📈 Cas d'Usage pour l'Évaluateur

### 1. Gestion de la Charge de Travail
- **En attente** : Manuscrits à démarrer
- **En cours** : Brouillons à finaliser
- **Évalués** : Historique de productivité

### 2. Priorisation
- Identifier les évaluations non commencées
- Suivre la progression des évaluations en cours
- Estimer le temps disponible pour de nouvelles assignations

### 3. Analyse de Performance
- **Évaluations par semaine/mois** : Mesurer son activité
- **Tendances** : Identifier les périodes de forte activité
- **Historique** : Voir l'évolution annuelle

### 4. Reporting
- Prouver son activité d'évaluation
- Justifier son expertise (nombre d'évaluations complétées)
- Suivre ses contributions à la revue

---

## 🔐 Contrôle d'Accès

| Rôle | Accès au Dashboard Évaluateur |
|------|-------------------------------|
| AUTHOR | ❌ Non |
| EVALUATOR | ✅ Oui (son propre dashboard) |
| EDITOR | ✅ Oui (tous les évaluateurs via /{id}) |
| SUPER_ADMIN | ✅ Oui (via bypass) |

**Endpoints:**
- `/evaluator` : Accès EVALUATOR (son propre dashboard)
- `/evaluator/{id}` : Accès EDITOR/SUPER_ADMIN (n'importe quel évaluateur)

---

## 🎨 Palette de Couleurs

| Statut | Couleur | Hex | Signification |
|--------|---------|-----|---------------|
| En attente | Orange | #F59E0B | Assigné mais pas commencé |
| En cours | Bleu | #3B82F6 | Travail en progression |
| Évalués | Vert | #22C55E | Complété avec succès |

---

## 💡 Optimisations Possibles

### Performance

**Actuel:** Boucle sur chaque manuscrit assigné pour vérifier la grille
```python
for link in assigned_links:
    grid = await get_grid(link.manuscript_id, evaluator_id)
    # Classification
```

**Alternative (future):** Requête unique avec LEFT JOIN
```sql
SELECT
    COUNT(*) FILTER (WHERE grid.id IS NULL) as awaiting,
    COUNT(*) FILTER (WHERE grid.submitted_at IS NULL) as in_progress,
    COUNT(*) FILTER (WHERE grid.submitted_at IS NOT NULL) as evaluated
FROM manuscript_evaluator_link link
LEFT JOIN manuscript_evaluation_grid grid ON ...
WHERE link.evaluator_id = ?
```

**Raison de l'approche actuelle:**
- Plus lisible et maintenable
- Performance acceptable pour un nombre raisonnable d'assignations (<100)
- Facilite les tests

---

## ✨ Points Forts

✅ **Complet** - 5/5 métriques demandées
✅ **Précis** - Logique claire de classification des statuts
✅ **Performant** - Requêtes SQL optimisées pour time series
✅ **Sécurisé** - RBAC strict (EVALUATOR peut voir uniquement son dashboard)
✅ **Documenté** - README + guide complet
✅ **Extensible** - Architecture permet ajout facile de métriques
✅ **Production-ready** - Gestion d'erreurs + logging

---

## 📝 Notes Importantes

1. **Seuls les manuscrits ACCEPTED** : Ne compte que les manuscrits où l'évaluateur a accepté l'assignation
2. **Statut basé sur la grille** : Utilise `ManuscriptEvaluationGrid` comme source de vérité
3. **Brouillons comptés** : Les grilles "en cours" (submitted_at NULL) sont comptabilisées séparément
4. **Time series sur soumissions** : Compte uniquement les évaluations **complétées** (`submitted_at` NOT NULL)
5. **Pas de deadline tracking** : Non demandé, mais pourrait être ajouté facilement

---

## 🔄 Workflow Typique

```
1. Éditeur assigne manuscrit → status = PENDING
2. Évaluateur accepte → status = ACCEPTED → "En attente" (0→1)
3. Évaluateur crée grille → submitted_at = NULL → "En cours" (1→0, 0→1)
4. Évaluateur sauvegarde → submitted_at = NULL → reste "En cours"
5. Évaluateur soumet → submitted_at = NOW() → "Évalués" (1→0, 0→1)
```

**Dashboard mis à jour en temps réel** à chaque appel de l'API.

---

**Implémenté par:** Claude Sonnet 4.5
**Date:** 2024-12-25
**Version:** 1.0
**Status:** ✅ Production Ready
