# Module Dashboards

## Vue d'ensemble

Le module dashboards fournit des statistiques et visualisations de données pour différents rôles d'utilisateurs de la plateforme Santaane.

## Endpoints Auteur

### GET `/api/v1/dashboards/author`

Récupère le dashboard complet pour l'auteur authentifié.

**Authentification:** Requise (JWT)
**Rôle:** Tous les utilisateurs authentifiés

**Réponse:**
```json
{
  "stats": {
    "total_submitted": 15,
    "total_rejected": 2,
    "total_accepted": 8,
    "total_published": 5
  },
  "bar_chart": {
    "title": "Répartition des manuscrits par statut",
    "data": [
      {
        "label": "Soumis",
        "value": 15,
        "color": "#3B82F6"
      },
      {
        "label": "Accepté",
        "value": 8,
        "color": "#22C55E"
      },
      {
        "label": "Publié",
        "value": 5,
        "color": "#6366F1"
      },
      {
        "label": "Rejeté",
        "value": 2,
        "color": "#EF4444"
      }
    ]
  },
  "weekly_submissions": {
    "period_type": "week",
    "title": "Soumissions par semaine (12 dernières semaines)",
    "data": [
      {
        "period": "2024-W50",
        "count": 2
      },
      {
        "period": "2024-W51",
        "count": 1
      },
      {
        "period": "2024-W52",
        "count": 3
      }
    ]
  },
  "monthly_submissions": {
    "period_type": "month",
    "title": "Soumissions par mois (12 derniers mois)",
    "data": [
      {
        "period": "2024-10",
        "count": 4
      },
      {
        "period": "2024-11",
        "count": 6
      },
      {
        "period": "2024-12",
        "count": 5
      }
    ]
  },
  "yearly_submissions": {
    "period_type": "year",
    "title": "Soumissions par année (5 dernières années)",
    "data": [
      {
        "period": "2023",
        "count": 8
      },
      {
        "period": "2024",
        "count": 15
      }
    ]
  }
}
```

**Exemple de requête:**
```bash
curl -X GET "http://localhost:8000/api/v1/dashboards/author" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### GET `/api/v1/dashboards/author/{author_id}`

Récupère le dashboard pour un auteur spécifique (par ID).

**Authentification:** Requise (JWT)
**Rôle:** EDITOR, SUPER_ADMIN

**Paramètres:**
- `author_id` (path): ID de l'auteur

**Réponse:** Identique à `/api/v1/dashboards/author`

**Exemple de requête:**
```bash
curl -X GET "http://localhost:8000/api/v1/dashboards/author/123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Architecture du Module

```
app/modules/dashboards/
├── __init__.py           # Expose le router
├── routes.py             # Définition des endpoints FastAPI
├── service.py            # Logique métier
├── repository.py         # Requêtes SQL
├── schemas.py            # Schémas Pydantic
├── utils.py              # Utilitaires et dépendances
├── error_codes.py        # Codes d'erreur
├── constants.py          # Constantes
└── README.md             # Documentation (ce fichier)
```

## Schémas de Données

### `ManuscriptStatsResponse`
Statistiques de base sur les manuscrits.

### `BarChartDataPoint`
Point de données pour le graphique en barres.

### `BarChartResponse`
Données complètes pour le graphique en barres.

### `TimeSeriesDataPoint`
Point de données pour les courbes temporelles.

### `TimeSeriesResponse`
Données complètes pour les courbes temporelles.

### `AuthorDashboardResponse`
Réponse complète du dashboard auteur (agrège tous les types ci-dessus).

---

## Mapping des Couleurs

Les couleurs des statuts de manuscrits suivent cette palette :

| Statut                | Couleur   | Hex       |
|----------------------|-----------|-----------|
| Soumis               | Bleu      | #3B82F6   |
| Re-soumis            | Violet    | #8B5CF6   |
| En révision          | Orange    | #F59E0B   |
| Révisé               | Vert      | #10B981   |
| Accepté              | Vert clair| #22C55E   |
| Rejeté               | Rouge     | #EF4444   |
| Révision demandée    | Orange foncé | #F97316 |
| Publié               | Indigo    | #6366F1   |

---

---

## Endpoints Super Admin

### GET `/api/v1/dashboards/super-admin`

Récupère le dashboard complet système pour le super administrateur.

**Authentification:** Requise (JWT)
**Rôle:** SUPER_ADMIN uniquement

**Réponse:**
```json
{
  "stats": {
    "total_manuscripts": 150,
    "in_evaluation": 25,
    "total_submitted": 40,
    "total_rejected": 20,
    "total_accepted": 60,
    "total_published": 50,
    "awaiting_evaluators": 10,
    "total_authors": 85,
    "total_editors": 5,
    "total_evaluators": 20,
    "rejection_rate": 13.33,
    "acceptance_rate": 40.00,
    "publication_rate": 33.33,
    "evaluation_rate": 53.33
  },
  "status_bar_chart": {
    "title": "Répartition des manuscrits par statut",
    "data": [
      { "label": "Accepté", "value": 60, "color": "#22C55E" },
      { "label": "Publié", "value": 50, "color": "#6366F1" },
      { "label": "Soumis", "value": 40, "color": "#3B82F6" },
      { "label": "En révision", "value": 25, "color": "#F59E0B" },
      { "label": "Rejeté", "value": 20, "color": "#EF4444" }
    ]
  },
  "theme_bar_chart": {
    "title": "Soumissions par thème",
    "category_type": "theme",
    "data": [
      { "label": "Intelligence Artificielle", "count": 45 },
      { "label": "Biologie Moléculaire", "count": 38 },
      { "label": "Physique Quantique", "count": 32 }
    ]
  },
  "section_bar_chart": {
    "title": "Soumissions par rubrique",
    "category_type": "section",
    "data": [
      { "label": "Article de recherche", "count": 80 },
      { "label": "Revue de littérature", "count": 45 },
      { "label": "Note technique", "count": 25 }
    ]
  },
  "language_bar_chart": {
    "title": "Soumissions par langue",
    "category_type": "language",
    "data": [
      { "label": "Français", "count": 90 },
      { "label": "Anglais", "count": 55 },
      { "label": "Arabe", "count": 5 }
    ]
  },
  "weekly_submissions": {
    "period_type": "week",
    "title": "Soumissions par semaine (12 dernières semaines)",
    "data": [...]
  },
  "monthly_submissions": {
    "period_type": "month",
    "title": "Soumissions par mois (12 derniers mois)",
    "data": [...]
  },
  "yearly_submissions": {
    "period_type": "year",
    "title": "Soumissions par année (5 dernières années)",
    "data": [...]
  },
  "weekly_authors": {
    "period_type": "week",
    "title": "Nouveaux auteurs par semaine (12 dernières semaines)",
    "data": [...]
  },
  "monthly_authors": {
    "period_type": "month",
    "title": "Nouveaux auteurs par mois (12 derniers mois)",
    "data": [...]
  },
  "yearly_authors": {
    "period_type": "year",
    "title": "Nouveaux auteurs par année (5 dernières années)",
    "data": [...]
  }
}
```

**Exemple de requête:**
```bash
curl -X GET "http://localhost:8000/api/v1/dashboards/super-admin" \
  -H "Authorization: Bearer YOUR_SUPER_ADMIN_JWT_TOKEN"
```

**Métriques Incluses:**

1. **Statistiques Générales:**
   - Nombre total de manuscrits
   - Manuscrits en évaluation
   - Manuscrits soumis
   - Manuscrits rejetés
   - Manuscrits acceptés
   - Manuscrits publiés
   - Manuscrits en attente d'évaluateur
   - Nombre total d'auteurs
   - Nombre total d'éditeurs
   - Nombre total d'évaluateurs

2. **Taux Calculés (%):**
   - Taux de rejet = (Rejetés / Total) × 100
   - Taux d'acceptation = (Acceptés / Total) × 100
   - Taux de publication = (Publiés / Total) × 100
   - Taux d'évaluation = ((Acceptés + Rejetés) / Total) × 100

3. **Distributions (Graphiques en Barres):**
   - Répartition par statut
   - Répartition par thème
   - Répartition par rubrique (section)
   - Répartition par langue

4. **Séries Temporelles:**
   - Soumissions par semaine/mois/année
   - Nouveaux auteurs par semaine/mois/année

---

## Endpoints Éditeur

### GET `/api/v1/dashboards/editor`

Récupère le dashboard complet système pour l'éditeur.

**Authentification:** Requise (JWT)
**Rôle:** EDITOR, SUPER_ADMIN

**Réponse:**
Identique à `/api/v1/dashboards/super-admin` - Les éditeurs ont besoin de la même vue système complète pour gérer le processus éditorial.

```json
{
  "stats": {
    "total_manuscripts": 150,
    "in_evaluation": 25,
    "total_submitted": 40,
    "total_rejected": 20,
    "total_accepted": 60,
    "total_published": 50,
    "awaiting_evaluators": 10,
    "total_authors": 85,
    "total_editors": 5,
    "total_evaluators": 20,
    "rejection_rate": 13.33,
    "acceptance_rate": 40.00,
    "publication_rate": 33.33,
    "evaluation_rate": 53.33
  },
  "status_bar_chart": { ... },
  "theme_bar_chart": { ... },
  "section_bar_chart": { ... },
  "language_bar_chart": { ... },
  "weekly_submissions": { ... },
  "monthly_submissions": { ... },
  "yearly_submissions": { ... },
  "weekly_authors": { ... },
  "monthly_authors": { ... },
  "yearly_authors": { ... }
}
```

**Exemple de requête:**
```bash
curl -X GET "http://localhost:8000/api/v1/dashboards/editor" \
  -H "Authorization: Bearer YOUR_EDITOR_JWT_TOKEN"
```

**Métriques Incluses:**

Identiques au dashboard Super Admin :

1. **Statistiques Générales:**
   - Nombre total d'auteurs
   - Nombre total d'éditeurs
   - Nombre total d'évaluateurs
   - Manuscrits en attente d'évaluateur
   - Nombre total de manuscrits soumis
   - Nombre total de manuscrits en évaluation
   - Nombre total de manuscrits rejetés
   - Nombre total de manuscrits acceptés
   - Nombre total de manuscrits publiés

2. **Taux Calculés (%):**
   - Taux de rejet
   - Taux d'acceptation
   - Taux de publication
   - Taux d'évaluation

3. **Distributions (Graphiques en Barres):**
   - Répartition par statut (soumis, rejeter, accepter, publier)
   - Répartition par thème
   - Répartition par rubrique (section)
   - Répartition par langue

4. **Séries Temporelles:**
   - Soumissions par semaine/mois/année
   - Nouveaux auteurs par semaine/mois/année

**Note:** Les éditeurs ont accès aux mêmes statistiques que les super admins car ils ont besoin d'une vue complète du système pour gérer efficacement le processus de révision et de publication.

---

---

## Endpoints Évaluateur

### GET `/api/v1/dashboards/evaluator`

Récupère le dashboard complet pour l'évaluateur authentifié.

**Authentification:** Requise (JWT)
**Rôle:** EVALUATOR, SUPER_ADMIN

**Réponse:**
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
      {
        "period": "2024-W50",
        "count": 2
      },
      {
        "period": "2024-W51",
        "count": 1
      },
      {
        "period": "2024-W52",
        "count": 3
      }
    ]
  },
  "monthly_evaluations": {
    "period_type": "month",
    "title": "Évaluations complétées par mois (12 derniers mois)",
    "data": [
      {
        "period": "2024-10",
        "count": 3
      },
      {
        "period": "2024-11",
        "count": 5
      },
      {
        "period": "2024-12",
        "count": 4
      }
    ]
  },
  "yearly_evaluations": {
    "period_type": "year",
    "title": "Évaluations complétées par année (5 dernières années)",
    "data": [
      {
        "period": "2023",
        "count": 8
      },
      {
        "period": "2024",
        "count": 12
      }
    ]
  }
}
```

**Exemple de requête:**
```bash
curl -X GET "http://localhost:8000/api/v1/dashboards/evaluator" \
  -H "Authorization: Bearer YOUR_EVALUATOR_JWT_TOKEN"
```

**Métriques Incluses:**

1. **Statistiques d'Évaluation:**
   - Nombre de manuscrits en attente d'évaluation (assignés mais pas commencés)
   - Nombre de manuscrits en cours d'évaluation (grille commencée mais pas soumise)
   - Nombre de manuscrits évalués (grille soumise)

2. **Graphique en Barres:**
   - Répartition par statut d'évaluation (en attente, en cours, évalués)

3. **Séries Temporelles:**
   - Évaluations complétées par semaine (12 dernières)
   - Évaluations complétées par mois (12 derniers)
   - Évaluations complétées par année (5 dernières)

**Logique des Statuts:**
- **En attente:** Manuscrit assigné avec status ACCEPTED mais aucune grille d'évaluation créée
- **En cours:** Grille d'évaluation créée mais `submitted_at` est NULL (brouillon)
- **Évalué:** Grille d'évaluation avec `submitted_at` NOT NULL (soumise)

---

### GET `/api/v1/dashboards/evaluator/{evaluator_id}`

Récupère le dashboard pour un évaluateur spécifique (par ID).

**Authentification:** Requise (JWT)
**Rôle:** EDITOR, SUPER_ADMIN

**Paramètres:**
- `evaluator_id` (path): ID de l'évaluateur

**Réponse:** Identique à `/api/v1/dashboards/evaluator`

**Exemple de requête:**
```bash
curl -X GET "http://localhost:8000/api/v1/dashboards/evaluator/123" \
  -H "Authorization: Bearer YOUR_EDITOR_JWT_TOKEN"
```

---

## Dashboards Implémentés

- ✅ **Dashboard Auteur** - Implémenté
- ✅ **Dashboard Évaluateur** - Implémenté
- ✅ **Dashboard Éditeur** - Implémenté
- ✅ **Dashboard Super Admin** - Implémenté

---

## Notes Techniques

- **Base de données:** PostgreSQL avec requêtes asynchrones (asyncpg)
- **Fonctions temporelles:** Utilise `date_trunc()` de PostgreSQL
- **Périodes par défaut:**
  - Semaines : 12 dernières semaines
  - Mois : 12 derniers mois
  - Années : 5 dernières années
- **Format des périodes:**
  - Semaine : `YYYY-WWW` (ex: 2024-W52)
  - Mois : `YYYY-MM` (ex: 2024-12)
  - Année : `YYYY` (ex: 2024)

---

## Tests

Pour tester les endpoints, utilisez Swagger UI à : `http://localhost:8000/docs`

Ou utilisez `curl` ou `httpie` avec un token JWT valide.

**Exemple avec httpie:**
```bash
http GET http://localhost:8000/api/v1/dashboards/author \
  Authorization:"Bearer YOUR_JWT_TOKEN"
```
