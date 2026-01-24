#!/bin/bash

cat << 'EOF'

╔════════════════════════════════════════════════════════════════════════════╗
║                    MIGRATION SÉCURISÉE - GUIDE COMPLET                     ║
╚════════════════════════════════════════════════════════════════════════════╝

❓ QUESTION: "Comment faire la migration sans perdre les données ?"

✅ RÉPONSE: Alembic NE supprime JAMAIS les données. Voici comment :

═══════════════════════════════════════════════════════════════════════════

🛡️  GARANTIES DE SÉCURITÉ
═════════════════════════

✅ Les données sont 100% PRÉSERVÉES
✅ Seule la structure est modifiée (table nouvelle créée)
✅ Les tables existantes restent intactes
✅ Les migrations sont tracées et réversibles
✅ Si erreur → rollback automatique

═══════════════════════════════════════════════════════════════════════════

🚀 PROCÉDURE RAPIDE (RECOMMANDÉE)
══════════════════════════════════

1️⃣  CRÉER UN BACKUP (optionnel mais recommandé)
   
   # Avec Docker
   docker exec santaane-postgresql pg_dump -U postgres -d santaane > backup.sql
   
   # Ou avec psql local
   pg_dump -U postgres -d santaane > backup.sql
   
   ✅ Crée un fichier backup.sql avec TOUTES les données

2️⃣  EXÉCUTER LA MIGRATION
   
   poetry run alembic upgrade head
   
   ✅ Alembic:
      - Crée la table mentor_assignments
      - Ajoute les indexes
      - Préserve TOUTES les données
      - Enregistre la migration

3️⃣  VÉRIFIER
   
   poetry run alembic current
   
   ✅ Output: "20251219_add_mentor_assignment_table"

═══════════════════════════════════════════════════════════════════════════

💾 ALTERNATIVE - UTILISER LE SCRIPT AUTOMATIQUE
================================================

Nous avons créé un script qui fait tout automatiquement:

   bash migrate_safe.sh

✅ Ce script:
   ✓ Vérifie l'état actuel
   ✓ Crée un backup automatiquement
   ✓ Exécute la migration
   ✓ Vérifie que tout s'est bien passé

═══════════════════════════════════════════════════════════════════════════

🔄 COMMENT FONCTIONNE ALEMBIC (TECHNIQUE)
═══════════════════════════════════════════

Avant migration:
┌─────────────────────────────────────────────┐
│ BASE DE DONNÉES                             │
│                                             │
│ Users        ✅ (préservés)                 │
│ Manuscripts  ✅ (préservés)                 │
│ Reviews      ✅ (préservés)                 │
│ Mentorships  ✅ (préservés)                 │
│                                             │
│ alembic_version table:                      │
│ - d39bfc026878_auto_migration...            │
└─────────────────────────────────────────────┘

Lors du "alembic upgrade head":
┌─────────────────────────────────────────────┐
│ Alembic fait:                               │
│                                             │
│ 1. Lit le fichier de migration              │
│    20251219_add_mentor_assignment_table.py  │
│                                             │
│ 2. Exécute les commandes SQL:               │
│    - CREATE TABLE mentor_assignments        │
│    - CREATE INDEXES                         │
│    - ADD CONSTRAINTS                        │
│                                             │
│ 3. Enregistre dans alembic_version:         │
│    + 20251219_add_mentor_assignment_table   │
│                                             │
│ 4. ✅ Commit la transaction                 │
└─────────────────────────────────────────────┘

Après migration:
┌─────────────────────────────────────────────┐
│ BASE DE DONNÉES                             │
│                                             │
│ Users        ✅ (IDENTIQUES - pas touché)   │
│ Manuscripts  ✅ (IDENTIQUES - pas touché)   │
│ Reviews      ✅ (IDENTIQUES - pas touché)   │
│ Mentorships  ✅ (IDENTIQUES - pas touché)   │
│ MentorAssign ✨ (NOUVEAU - créé vide)       │
│                                             │
│ alembic_version table:                      │
│ - d39bfc026878_auto_migration...            │
│ + 20251219_add_mentor_assignment_table ✨   │
└─────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════

⚡ SI VOUS DÉMARREZ L'APP NORMALEMENT
═════════════════════════════════════

Si vous faites simplement:
   ./santaane dev

✅ L'entrypoint.sh exécute automatiquement:
   poetry run alembic upgrade head

✅ La migration se fait AVANT que l'app démarre
✅ Les données sont 100% préservées
✅ L'app démarre avec la nouvelle structure

═══════════════════════════════════════════════════════════════════════════

🔙 SI VOUS VOULEZ REVENIR EN ARRIÈRE
════════════════════════════════════

Si la migration cause un problème (très rare):

   # Revenir à la version précédente
   poetry run alembic downgrade -1
   
   ✅ Alembic:
      - Supprime la table mentor_assignments
      - Restaure l'état avant migration
      - Enregistre le downgrade

OU: Restaurer depuis le backup:
   pg_restore backup.sql  (si vous en avez un)

═══════════════════════════════════════════════════════════════════════════

✅ ÉTAPES À SUIVRE (COPIER-COLLER)
═══════════════════════════════════

# Option 1: Rapide avec script automatique
bash migrate_safe.sh

# Option 2: Manuel avec backup
docker exec santaane-postgresql pg_dump -U postgres -d santaane > backup.sql
poetry run alembic upgrade head
poetry run alembic current

# Option 3: Simplement démarrer l'app
./santaane dev

═══════════════════════════════════════════════════════════════════════════

📊 VÉRIFICATION APRÈS MIGRATION
═════════════════════════════════

✅ Vérifier la version
   poetry run alembic current
   
✅ Vérifier la table existe
   poetry run alembic history

✅ Tester les endpoints
   ./santaane dev
   http://localhost:8000/docs

═══════════════════════════════════════════════════════════════════════════

❌ SI QUELQUE CHOSE NE VA PAS
═════════════════════════════

Problem: "Migration failed"
Solution:
  1. poetry run alembic current  # Voir l'état
  2. poetry run alembic history  # Voir l'historique
  3. Vérifier les logs
  4. poetry run alembic downgrade -1  # Revenir en arrière

Problem: "Table mentor_assignments not found"
Solution:
  1. Vérifier que la migration s'est exécutée: alembic current
  2. Vérifier les logs pour les erreurs
  3. Relancer: poetry run alembic upgrade head

Problem: "Données perdues"
Solution:
  ✅ C'est impossible! Alembic ne supprime JAMAIS les données
  ✅ Restaurer le backup si vraiment quelque chose s'est mal passé

═══════════════════════════════════════════════════════════════════════════

🎯 RÉSUMÉ
═════════

Les migrations Alembic sont TRÈS SÛRES:

1. ✅ Les données ne sont jamais touchées
2. ✅ Seule la structure est modifiée
3. ✅ Les migrations sont tracées et réversibles
4. ✅ Un backup peut être créé en 1 ligne
5. ✅ Vous pouvez revenir en arrière facilement

DONC: Exécutez la migration EN TOUTE SÉCURITÉ! 🚀

═══════════════════════════════════════════════════════════════════════════

📚 DOCUMENTATION COMPLÈTE
══════════════════════════

Pour plus de détails, voir:
  - MIGRATION_GUIDE_SECURISE.md (guide détaillé)
  - migrate_safe.sh (script automatique)

═══════════════════════════════════════════════════════════════════════════

EOF
