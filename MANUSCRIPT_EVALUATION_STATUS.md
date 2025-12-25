# 📊 Système de Statut d'Évaluation des Manuscrits

## ✅ Implémentation complète

Le système de tracking du statut d'évaluation des manuscrits a été implémenté avec succès.

---

## 🎯 Vue d'ensemble

Ce système permet de suivre automatiquement l'état d'avancement de l'évaluation d'un manuscrit en fonction des évaluateurs assignés et des évaluations soumises.

### Fonctionnalités

✅ **Mise à jour automatique** du statut quand un évaluateur soumet son évaluation
✅ **5 statuts différents** pour tracker finement l'avancement
✅ **Endpoint dédié** pour obtenir les détails de progression
✅ **Index base de données** pour des requêtes performantes
✅ **Migration Alembic** appliquée avec succès

---

## 📋 Les 5 Statuts d'Évaluation

| Statut | Valeur | Description | Condition |
|--------|--------|-------------|-----------|
| 🔵 **Pending** | `pending` | En attente d'évaluateurs | Aucun évaluateur assigné ou accepté |
| 🟡 **In Progress** | `in_progress` | Évaluation en cours | Au moins 1 évaluateur accepté, aucune soumission |
| 🟠 **Partially Evaluated** | `partially_evaluated` | Partiellement évalué | Certains évaluateurs ont soumis, mais pas tous |
| 🟢 **Fully Evaluated** | `fully_evaluated` | Complètement évalué | Tous les évaluateurs assignés ont soumis |
| 🟣 **Decision Pending** | `decision_pending` | Décision éditoriale en attente | Évaluations complètes (usage futur) |

---

## 🔄 Workflow Automatique

### 1. État Initial
```
Manuscrit créé → evaluation_status = "pending"
```

### 2. Assignation d'Évaluateurs
```
Évaluateur accepte → evaluation_status reste "pending"
(Mise à jour manuelle si besoin via service)
```

### 3. Première Soumission
```
1er évaluateur soumet → evaluation_status = "in_progress" → "partially_evaluated"
(Si plusieurs évaluateurs assignés)
```

### 4. Soumissions Suivantes
```
Chaque soumission → Recalcul automatique
- 1/3 soumis → "partially_evaluated"
- 2/3 soumis → "partially_evaluated"
- 3/3 soumis → "fully_evaluated" ✅
```

---

## 🛠️ Implémentation Technique

### 1. Enum - `ManuscriptEvaluationStatus`

**Fichier:** [app/models/enums.py](app/models/enums.py:56-62)

```python
class ManuscriptEvaluationStatus(str, Enum):
    """Status of manuscript evaluation process"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PARTIALLY_EVALUATED = "partially_evaluated"
    FULLY_EVALUATED = "fully_evaluated"
    DECISION_PENDING = "decision_pending"
```

### 2. Champ dans Manuscript Model

**Fichier:** [app/models/manuscript.py](app/models/manuscript.py:40-45)

```python
evaluation_status: ManuscriptEvaluationStatus = Field(
    default=ManuscriptEvaluationStatus.PENDING,
    nullable=False,
    index=True,  # ← Index pour requêtes performantes
    description="Statut du processus d'évaluation par les évaluateurs"
)
```

### 3. Service - Mise à Jour Automatique

**Fichier:** [app/modules/manuscripts/evaluation_grid_service.py](app/modules/manuscripts/evaluation_grid_service.py:64-113)

La méthode `_update_manuscript_evaluation_status()` est appelée automatiquement après chaque soumission :

```python
async def _update_manuscript_evaluation_status(self, manuscript_id: int) -> None:
    """Update manuscript evaluation_status based on submitted evaluations."""

    # Compter évaluateurs assignés et acceptés
    assigned_count = ...

    # Compter évaluations soumises
    submitted_count = ...

    # Déterminer le nouveau statut
    if assigned_count == 0:
        new_status = ManuscriptEvaluationStatus.PENDING
    elif submitted_count == 0:
        new_status = ManuscriptEvaluationStatus.IN_PROGRESS
    elif submitted_count < assigned_count:
        new_status = ManuscriptEvaluationStatus.PARTIALLY_EVALUATED
    elif submitted_count == assigned_count:
        new_status = ManuscriptEvaluationStatus.FULLY_EVALUATED

    # Mettre à jour si changé
    manuscript.evaluation_status = new_status
    await self.db.commit()
```

**Appelé dans:** `submit_evaluation()` après `grid.submitted_at = datetime.utcnow()`

### 4. Nouveau Endpoint - GET Evaluation Status

**Route:** `GET /api/v1/manuscripts/{manuscript_id}/evaluation-status`

**Fichier:** [app/modules/manuscripts/evaluation_grid_routes.py](app/modules/manuscripts/evaluation_grid_routes.py:115-137)

**Exemple de requête:**

```bash
curl -X GET http://localhost:8000/api/v1/manuscripts/123/evaluation-status \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

**Réponse (200 OK):**

```json
{
  "manuscriptId": 123,
  "evaluationStatus": "partially_evaluated",
  "assignedEvaluators": 3,
  "submittedEvaluations": 2,
  "isFullyEvaluated": false,
  "progress": 66.67
}
```

**Champs de la réponse:**

| Champ | Type | Description |
|-------|------|-------------|
| `manuscriptId` | int | ID du manuscrit |
| `evaluationStatus` | string | Statut actuel (enum) |
| `assignedEvaluators` | int | Nombre d'évaluateurs assignés et acceptés |
| `submittedEvaluations` | int | Nombre d'évaluations soumises |
| `isFullyEvaluated` | boolean | `true` si tous ont soumis |
| `progress` | float | Pourcentage de complétion (0-100) |

---

## 📊 Exemples d'Utilisation

### 1. Dashboard Éditeur - Liste des Manuscrits

```typescript
// Récupérer tous les manuscrits complètement évalués
const fullyEvaluatedManuscripts = await fetch('/api/manuscripts?evaluation_status=fully_evaluated');

// Compter les manuscrits par statut
const stats = {
  pending: manuscrits.filter(m => m.evaluationStatus === 'pending').length,
  inProgress: manuscrits.filter(m => m.evaluationStatus === 'in_progress').length,
  partiallyEvaluated: manuscrits.filter(m => m.evaluationStatus === 'partially_evaluated').length,
  fullyEvaluated: manuscrits.filter(m => m.evaluationStatus === 'fully_evaluated').length
};
```

### 2. Page de Détail Manuscrit

```typescript
// Obtenir le statut d'évaluation
const status = await fetch(`/api/manuscripts/${manuscriptId}/evaluation-status`);

// Afficher la progression
<div>
  <p>Statut: {status.evaluationStatus}</p>
  <p>Progression: {status.submittedEvaluations}/{status.assignedEvaluators} évaluations soumises</p>
  <ProgressBar value={status.progress} />

  {status.isFullyEvaluated && (
    <Badge color="green">Toutes les évaluations reçues</Badge>
  )}
</div>
```

### 3. Filtrage et Tri

```typescript
// Backend query example
const fullyEvaluated = await db.query(
  'SELECT * FROM manuscripts WHERE evaluation_status = $1',
  ['fully_evaluated']
);

// Avec l'index, cette requête est ultra-rapide! 🚀
```

---

## 🗄️ Base de Données

### Table: `manuscripts`

**Nouveau champ:**

```sql
evaluation_status VARCHAR(50) NOT NULL DEFAULT 'pending'
```

**Index:**

```sql
CREATE INDEX ix_manuscripts_evaluation_status ON manuscripts(evaluation_status);
```

### Migration Alembic

**Fichier:** `alembic/versions/20251225_add_manuscript_evaluation_status.py`

```bash
# Migration appliquée avec succès ✅
./santaane migrate
```

**Actions de la migration:**

1. Ajoute le champ `evaluation_status` avec valeur par défaut `'pending'`
2. Crée l'index `ix_manuscripts_evaluation_status`
3. Les manuscrits existants auront `evaluation_status = 'pending'`
4. Leur statut sera mis à jour automatiquement lors de la prochaine soumission

---

## 🔍 Requêtes SQL Utiles

### Compter manuscrits par statut

```sql
SELECT
    evaluation_status,
    COUNT(*) as count
FROM manuscripts
GROUP BY evaluation_status
ORDER BY count DESC;
```

### Manuscrits en attente d'évaluations

```sql
SELECT
    m.id,
    m.title,
    m.evaluation_status,
    COUNT(me.id) FILTER (WHERE me.status = 'accepted') as evaluators_assigned,
    COUNT(meg.id) FILTER (WHERE meg.submitted_at IS NOT NULL) as evaluations_submitted
FROM manuscripts m
LEFT JOIN manuscript_evaluators me ON me.manuscript_id = m.id
LEFT JOIN manuscript_evaluation_grids meg ON meg.manuscript_id = m.id
WHERE m.evaluation_status IN ('in_progress', 'partially_evaluated')
GROUP BY m.id, m.title, m.evaluation_status;
```

### Manuscrits complètement évalués cette semaine

```sql
SELECT
    m.id,
    m.title,
    MAX(meg.submitted_at) as last_evaluation_date
FROM manuscripts m
JOIN manuscript_evaluation_grids meg ON meg.manuscript_id = m.id
WHERE m.evaluation_status = 'fully_evaluated'
AND meg.submitted_at >= NOW() - INTERVAL '7 days'
GROUP BY m.id, m.title
ORDER BY last_evaluation_date DESC;
```

---

## 🧪 Tests Recommandés

### Test 1: Manuscrit avec 1 évaluateur

```
1. Créer manuscrit → evaluation_status = "pending"
2. Assigner 1 évaluateur → (reste "pending" jusqu'à acceptation)
3. Évaluateur accepte → (optionnel: mettre à "in_progress")
4. Évaluateur soumet → evaluation_status = "fully_evaluated" ✅
```

### Test 2: Manuscrit avec 3 évaluateurs

```
1. Créer manuscrit → "pending"
2. Assigner 3 évaluateurs (tous acceptent)
3. 1er soumet → "partially_evaluated" (1/3)
4. 2ème soumet → "partially_evaluated" (2/3)
5. 3ème soumet → "fully_evaluated" ✅ (3/3)
```

### Test 3: Endpoint Evaluation Status

```bash
# Vérifier que le calcul est correct
GET /api/manuscripts/123/evaluation-status

# Attendu:
{
  "assignedEvaluators": 3,
  "submittedEvaluations": 2,
  "progress": 66.67,
  "isFullyEvaluated": false
}
```

---

## 🎨 UI/UX Suggestions

### Badges de Statut

```tsx
const StatusBadge = ({ status }) => {
  const badges = {
    pending: { color: 'gray', label: 'En attente', icon: '🔵' },
    in_progress: { color: 'yellow', label: 'En cours', icon: '🟡' },
    partially_evaluated: { color: 'orange', label: 'Partiellement évalué', icon: '🟠' },
    fully_evaluated: { color: 'green', label: 'Complètement évalué', icon: '🟢' },
    decision_pending: { color: 'purple', label: 'Décision en attente', icon: '🟣' }
  };

  const badge = badges[status];
  return <Badge color={badge.color}>{badge.icon} {badge.label}</Badge>;
};
```

### Barre de Progression

```tsx
<div className="evaluation-progress">
  <div className="progress-bar" style={{ width: `${progress}%` }} />
  <span>{submittedEvaluations}/{assignedEvaluators} évaluations</span>
</div>
```

---

## 📈 Avantages de Cette Approche

✅ **Performant** - Index sur evaluation_status → Requêtes ultra-rapides
✅ **Automatique** - Mise à jour sans intervention manuelle
✅ **Clair** - 5 statuts bien définis et compréhensibles
✅ **Extensible** - Facile d'ajouter de nouveaux statuts (ex: `under_review`)
✅ **Dashboard-friendly** - Filtrage et tri faciles
✅ **Temps réel** - Statut toujours à jour après chaque soumission

---

## 🚀 Prochaines Étapes Possibles

### 1. Notifications Automatiques

```python
# Quand evaluation_status devient "fully_evaluated"
if new_status == ManuscriptEvaluationStatus.FULLY_EVALUATED:
    await notify_editors(manuscript_id, "Toutes les évaluations reçues")
```

### 2. Workflow Éditorial

```python
# Bouton "Passer en décision éditoriale"
manuscript.evaluation_status = ManuscriptEvaluationStatus.DECISION_PENDING
```

### 3. Statistiques

```python
# Dashboard analytics
stats = {
    'total_manuscripts': count_all(),
    'fully_evaluated_this_month': count_by_status_and_date('fully_evaluated', month),
    'average_time_to_full_evaluation': calculate_avg_time()
}
```

---

## 📞 Support

**Documentation:**
- Ce fichier: `MANUSCRIPT_EVALUATION_STATUS.md`
- API grilles d'évaluation: `EVALUATION_GRID_API.md`
- API annotations: `ANNOTATION_API_EXAMPLES.md`

**Commandes:**

```bash
# Voir les logs
./santaane logs

# Migration actuelle
./santaane migration-current

# Rollback si besoin
./santaane rollback
```

---

**Date d'implémentation:** 2025-12-25
**Version:** 1.0
**Status:** ✅ Production Ready
