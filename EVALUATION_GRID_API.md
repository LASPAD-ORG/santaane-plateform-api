# 📋 API Contract: Manuscript Evaluation Grid System

## ✅ Implementation complète

L'API d'évaluation des manuscrits a été implémentée avec succès.

### Changements principaux:
- ✅ 3 endpoints REST (GET, PUT, POST)
- ✅ Grille d'évaluation avec 8 champs d'évaluation
- ✅ Contrainte unique: un évaluateur = une grille par manuscrit
- ✅ Système de brouillon (submitted_at NULL) / soumis (submitted_at NOT NULL)
- ✅ Validation Pydantic complète
- ✅ Table créée avec migration Alembic

---

## 🔐 Authentification

Toutes les requêtes nécessitent un token JWT Bearer:

```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

**Rôle requis**: EVALUATOR (l'évaluateur doit être assigné au manuscrit)

---

## 📝 1. Récupérer la grille d'évaluation (GET)

### Endpoint
```
GET /api/v1/manuscripts/{manuscript_id}/evaluation-grid
```

### Exemple de requête

```bash
curl -X GET http://localhost:8000/api/v1/manuscripts/123/evaluation-grid \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

### Réponse (200 OK)

```json
{
  "id": 1,
  "manuscriptId": 123,
  "evaluatorId": 456,
  "articleTitle": "Titre de l'article scientifique",
  "evaluatorName": "Dr. Jean Dupont",
  "originalityOfIdeas": "Les idées présentées sont novatrices et apportent une contribution significative...",
  "methodologyRigor": "La méthodologie utilisée est rigoureuse et bien documentée...",
  "theoreticalApproach": "L'approche théorique est solide, appuyée par des études empiriques pertinentes...",
  "presentationClarity": "La présentation est claire et bien structurée...",
  "strengths": "- Originalité du sujet\n- Méthodologie rigoureuse\n- Résultats bien présentés",
  "weaknesses": "- Manque de références récentes\n- Analyse statistique limitée",
  "suggestions": "Je suggère d'ajouter une section comparative avec les études similaires...",
  "recommendation": "accepted_with_validation",
  "createdAt": "2025-12-24T20:30:00.000Z",
  "updatedAt": "2025-12-24T21:15:00.000Z",
  "submittedAt": null
}
```

### Codes d'erreur

- **404 Not Found** - Grille d'évaluation non trouvée
- **403 Forbidden** - Évaluateur non assigné au manuscrit
- **403 Forbidden** - L'assignation n'a pas été acceptée

---

## ✏️ 2. Sauvegarder la grille (UPSERT - PUT)

### Endpoint
```
PUT /api/v1/manuscripts/{manuscript_id}/evaluation-grid
```

### Corps de la requête

```json
{
  "originalityOfIdeas": "Les idées présentées sont novatrices...",
  "methodologyRigor": "La méthodologie utilisée est rigoureuse...",
  "theoreticalApproach": "L'approche théorique est solide...",
  "presentationClarity": "La présentation est claire...",
  "strengths": "- Originalité du sujet\n- Méthodologie rigoureuse",
  "weaknesses": "- Manque de références récentes",
  "suggestions": "Je suggère d'ajouter une section comparative...",
  "recommendation": "accepted_with_validation"
}
```

### Validation des champs

| Champ | Requis | Type | Longueur | Valeurs possibles |
|-------|--------|------|----------|-------------------|
| `originalityOfIdeas` | ✅ Oui | string | 1-5000 | Texte libre |
| `methodologyRigor` | ✅ Oui | string | 1-5000 | Texte libre |
| `theoreticalApproach` | ✅ Oui | string | 1-5000 | Texte libre |
| `presentationClarity` | ✅ Oui | string | 1-5000 | Texte libre |
| `strengths` | ✅ Oui | string | 1-5000 | Texte libre |
| `weaknesses` | ✅ Oui | string | 1-5000 | Texte libre |
| `suggestions` | ⚪ Non | string | 0-5000 | Texte libre (optionnel) |
| `recommendation` | ✅ Oui | enum | - | `"accepted_with_validation"`, `"resubmission_required"`, `"rejected"` |

### Exemple de requête

```bash
curl -X PUT http://localhost:8000/api/v1/manuscripts/123/evaluation-grid \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "originalityOfIdeas": "Les idées présentées sont novatrices et apportent une contribution significative au domaine.",
    "methodologyRigor": "La méthodologie utilisée est rigoureuse et bien documentée avec des protocoles clairs.",
    "theoreticalApproach": "L approche théorique est solide, appuyée par des études empiriques pertinentes.",
    "presentationClarity": "La présentation est claire et bien structurée, facilitant la compréhension.",
    "strengths": "- Originalité du sujet\n- Méthodologie rigoureuse\n- Résultats bien présentés",
    "weaknesses": "- Manque de références récentes\n- Analyse statistique limitée",
    "suggestions": "Je suggère d ajouter une section comparative avec les études similaires.",
    "recommendation": "accepted_with_validation"
  }'
```

### Réponse (200 OK)

La même structure que la réponse GET.

### Comportement UPSERT

- Si la grille **n'existe pas** → Créer une nouvelle grille
- Si la grille **existe** ET `submitted_at IS NULL` → Mettre à jour la grille
- Si la grille **existe** ET `submitted_at IS NOT NULL` → **403 Forbidden** (déjà soumise)

### Codes d'erreur

- **200 OK** - Grille mise à jour avec succès
- **201 Created** - Nouvelle grille créée
- **400 Bad Request** - Validation échouée
- **403 Forbidden** - Grille déjà soumise (non modifiable)
- **403 Forbidden** - Évaluateur non assigné au manuscrit
- **422 Unprocessable Entity** - Erreur de validation Pydantic

---

## 🚀 3. Soumettre l'évaluation (POST)

### Endpoint
```
POST /api/v1/manuscripts/{manuscript_id}/submit-evaluation
```

### Pas de corps de requête

Cette route ne nécessite aucun corps de requête. Elle soumet la grille existante.

### Exemple de requête

```bash
curl -X POST http://localhost:8000/api/v1/manuscripts/123/submit-evaluation \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

### Réponse (200 OK)

```json
{
  "message": "Évaluation soumise avec succès",
  "manuscriptId": 123,
  "evaluatorId": 456,
  "submittedAt": "2025-12-24T22:30:00.000Z",
  "annotationsCount": 15,
  "evaluationGrid": {
    "id": 1,
    "originalityOfIdeas": "Les idées présentées sont novatrices...",
    "methodologyRigor": "La méthodologie utilisée est rigoureuse...",
    "theoreticalApproach": "L'approche théorique est solide...",
    "presentationClarity": "La présentation est claire...",
    "strengths": "- Originalité du sujet\n- Méthodologie rigoureuse",
    "weaknesses": "- Manque de références récentes",
    "suggestions": "Je suggère d'ajouter une section comparative...",
    "recommendation": "accepted_with_validation",
    "submittedAt": "2025-12-24T22:30:00.000Z"
  }
}
```

### Comportement

1. Vérifie que la grille existe (404 si non)
2. Vérifie que tous les champs requis sont remplis (400 si non)
3. Marque `submitted_at = NOW()`
4. Compte le nombre d'annotations associées
5. Retourne un résumé complet

### Codes d'erreur

- **200 OK** - Évaluation soumise avec succès
- **400 Bad Request** - Grille incomplète (champs requis manquants)
- **404 Not Found** - Grille d'évaluation non trouvée
- **403 Forbidden** - Évaluateur non assigné au manuscrit

---

## 📊 Valeurs de recommandation

Le champ `recommendation` accepte uniquement ces 3 valeurs:

| Valeur | Signification | Description |
|--------|---------------|-------------|
| `accepted_with_validation` | Accepté avec validation | Le manuscrit est accepté sous réserve de modifications mineures |
| `resubmission_required` | Re-soumission requise | Le manuscrit nécessite des révisions importantes et une nouvelle soumission |
| `rejected` | Rejeté | Le manuscrit est rejeté |

---

## 🔍 Règles métier

### Contrainte unique
- Un évaluateur ne peut avoir qu'**une seule grille** par manuscrit
- Contrainte base de données: `UNIQUE(manuscript_id, evaluator_id)`

### Système de brouillon/soumission
- **Brouillon** (`submitted_at = NULL`):
  - La grille peut être modifiée via PUT
  - Permet plusieurs sauvegardes avant soumission
- **Soumis** (`submitted_at != NULL`):
  - La grille est **verrouillée** (non modifiable)
  - Toute tentative de modification retourne 403 Forbidden

### Vérifications de sécurité
- L'évaluateur doit être **assigné** au manuscrit
- L'assignation doit être **acceptée** (`status = 'accepted'`)
- Seul l'évaluateur assigné peut voir/modifier sa propre grille

---

## ❌ Codes d'erreur détaillés

### 400 Bad Request
Grille incomplète lors de la soumission

```json
{
  "detail": "La grille d'évaluation doit être complétée avant soumission"
}
```

### 403 Forbidden - Non assigné

```json
{
  "detail": "Vous n'êtes pas assigné à ce manuscrit"
}
```

### 403 Forbidden - Assignation non acceptée

```json
{
  "detail": "Vous devez accepter l'assignation avant de pouvoir évaluer"
}
```

### 403 Forbidden - Grille déjà soumise

```json
{
  "detail": "La grille a déjà été soumise et ne peut plus être modifiée"
}
```

### 404 Not Found

```json
{
  "detail": "Grille d'évaluation non trouvée"
}
```

### 422 Unprocessable Entity
Erreur de validation Pydantic

```json
{
  "detail": [
    {
      "type": "literal_error",
      "loc": ["body", "recommendation"],
      "msg": "Input should be 'accepted_with_validation', 'resubmission_required' or 'rejected'"
    }
  ]
}
```

---

## 📊 Base de données

### Structure de la table

```sql
CREATE TABLE manuscript_evaluation_grids (
    id SERIAL PRIMARY KEY,
    manuscript_id INTEGER NOT NULL REFERENCES manuscripts(id) ON DELETE CASCADE,
    evaluator_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    originality_of_ideas TEXT NOT NULL,
    methodology_rigor TEXT NOT NULL,
    theoretical_approach TEXT NOT NULL,
    presentation_clarity TEXT NOT NULL,
    strengths TEXT NOT NULL,
    weaknesses TEXT NOT NULL,
    suggestions TEXT,

    recommendation VARCHAR(50) NOT NULL,

    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    submitted_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT uq_manuscript_evaluator UNIQUE (manuscript_id, evaluator_id)
);
```

### Index

- `idx_evaluation_grids_manuscript` sur `manuscript_id`
- `idx_evaluation_grids_evaluator` sur `evaluator_id`

### Trigger

- `update_evaluation_grids_updated_at` met à jour automatiquement `updated_at`

---

## 🧪 Tests recommandés

### Test du cycle complet

1. **Créer un brouillon** (PUT sans soumission)
   ```bash
   # PUT /api/v1/manuscripts/123/evaluation-grid
   # Vérifier: submitted_at = null
   ```

2. **Modifier le brouillon** plusieurs fois (PUT)
   ```bash
   # PUT /api/v1/manuscripts/123/evaluation-grid
   # Vérifier: updated_at change, submitted_at reste null
   ```

3. **Récupérer le brouillon** (GET)
   ```bash
   # GET /api/v1/manuscripts/123/evaluation-grid
   # Vérifier: tous les champs présents
   ```

4. **Soumettre l'évaluation** (POST)
   ```bash
   # POST /api/v1/manuscripts/123/submit-evaluation
   # Vérifier: submitted_at != null, annotationsCount présent
   ```

5. **Tentative de modification après soumission** (PUT)
   ```bash
   # PUT /api/v1/manuscripts/123/evaluation-grid
   # Résultat attendu: 403 Forbidden
   ```

### Tests de validation

- ✅ Champs requis vides → 422 Unprocessable Entity
- ✅ Champ > 5000 caractères → 422 Unprocessable Entity
- ✅ Recommendation invalide → 422 Unprocessable Entity
- ✅ Évaluateur non assigné → 403 Forbidden
- ✅ Grille inexistante (GET) → 404 Not Found
- ✅ Grille inexistante (POST submit) → 404 Not Found

---

## 🚀 Workflow Frontend recommandé

### 1. Page d'évaluation du manuscrit

```typescript
// Charger la grille existante ou créer une nouvelle
const loadEvaluationGrid = async (manuscriptId: number) => {
  try {
    const response = await fetch(
      `/api/v1/manuscripts/${manuscriptId}/evaluation-grid`,
      { headers: { Authorization: `Bearer ${token}` } }
    );

    if (response.status === 404) {
      // Pas de grille existante, formulaire vide
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Erreur chargement grille:', error);
  }
};
```

### 2. Sauvegarde automatique (auto-save)

```typescript
// Sauvegarder en brouillon toutes les 30 secondes
const autoSave = async (manuscriptId: number, formData: any) => {
  await fetch(`/api/v1/manuscripts/${manuscriptId}/evaluation-grid`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(formData)
  });
};

// Utiliser avec debounce
const debouncedSave = debounce(autoSave, 30000);
```

### 3. Soumission finale

```typescript
const submitEvaluation = async (manuscriptId: number) => {
  try {
    const response = await fetch(
      `/api/v1/manuscripts/${manuscriptId}/submit-evaluation`,
      {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      }
    );

    const result = await response.json();

    if (response.ok) {
      console.log('Évaluation soumise:', result.message);
      console.log('Annotations:', result.annotationsCount);
      // Rediriger ou afficher confirmation
    } else if (response.status === 400) {
      alert('La grille doit être complétée avant soumission');
    }
  } catch (error) {
    console.error('Erreur soumission:', error);
  }
};
```

### 4. Affichage conditionnel

```typescript
// Désactiver les champs si déjà soumis
const isSubmitted = evaluationGrid?.submittedAt !== null;

return (
  <form>
    <textarea
      name="originalityOfIdeas"
      disabled={isSubmitted}
      maxLength={5000}
    />

    {!isSubmitted && (
      <button onClick={() => submitEvaluation(manuscriptId)}>
        Soumettre l'évaluation
      </button>
    )}

    {isSubmitted && (
      <div className="alert">
        Évaluation soumise le {new Date(evaluationGrid.submittedAt).toLocaleString()}
      </div>
    )}
  </form>
);
```

---

## 📞 Support

En cas de problème:

1. Vérifier les logs: `./santaane logs`
2. Vérifier la migration: `./santaane migration-current`
3. Rollback si nécessaire: `./santaane rollback`

---

## ✅ Checklist d'implémentation frontend

- [ ] Formulaire avec 8 champs d'évaluation
- [ ] Select pour `recommendation` avec 3 options
- [ ] Validation côté client (longueurs min/max)
- [ ] Auto-save en brouillon (debounce 30s)
- [ ] Bouton "Soumettre l'évaluation"
- [ ] Désactivation des champs après soumission
- [ ] Indicateur visuel "Brouillon" vs "Soumis"
- [ ] Gestion des erreurs (400, 403, 404, 422)
- [ ] Affichage du nombre d'annotations après soumission
- [ ] Confirmation avant soumission finale

---

**Date de création**: 2025-12-24
**Version API**: v1
**Backend**: FastAPI + SQLModel + PostgreSQL
