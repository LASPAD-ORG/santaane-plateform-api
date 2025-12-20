"""
GUIDE SÉCURISÉ - MIGRATION DB MENTOR ASSIGNMENT
================================================

⚠️  IMPORTANT: Comment ne pas perdre les données

Alembic ne supprime PAS les données, il crée/modifie seulement la structure de la base.

PROCÉDURE SÉCURISÉE :
====================

OPTION 1 : MIGRATION EN LOCAL (RECOMMANDÉE)
============================================

1. Vérifier le statut actuel
   $ cd /home/a-salih-ibn-fadilou/Bureau/santaane-plateform-api
   $ poetry run alembic current
   
   ✅ Output: "d39bfc026878_auto_migration_20251110_060724" (dernière version appliquée)

2. Voir les migrations en attente
   $ poetry run alembic heads
   
   ✅ Output: "20251219_add_mentor_assignment_table" (la nouvelle migration)

3. BACKUP DE SÉCURITÉ (optionnel mais recommandé)
   $ docker exec santaane-postgresql pg_dump -U postgres -d santaane > backup_before_migration.sql
   
   Cela crée un fichier backup_before_migration.sql avec toutes les données

4. Exécuter la migration
   $ poetry run alembic upgrade head
   
   ✅ Output: 
   "INFO  [alembic.runtime.migration] Running upgrade d39bfc0268... "
   "INFO  [alembic.runtime.migration] Running upgrade 202512... "
   "Running upgrade 20251219_add_mentor_assignment_table"
   "Done!"

5. Vérifier que ça a marché
   $ poetry run alembic current
   
   ✅ Output: "20251219_add_mentor_assignment_table" (nouvelle version)

6. Vérifier les tables
   $ poetry run python3 -c "
     from sqlalchemy import text, create_engine
     from app.db import DATABASE_URL
     engine = create_engine(DATABASE_URL)
     with engine.connect() as conn:
         result = conn.execute(text('SELECT * FROM information_schema.tables WHERE table_name=\'mentor_assignments\''))
         print('mentor_assignments table:', 'EXISTS' if result.fetchone() else 'NOT FOUND')
   "
   
   ✅ Output: "mentor_assignments table: EXISTS"


OPTION 2 : MIGRATION AVEC DOCKER (SI VOUS UTILISEZ DOCKER)
===========================================================

1. Vérifier le conteneur
   $ docker ps
   
   ✅ Output: santaane-postgresql ou santaane-api en running

2. Backup avant migration (important!)
   $ docker exec santaane-postgresql pg_dump -U postgres -d santaane > backup_$(date +%Y%m%d_%H%M%S).sql
   
   Cela crée un fichier backup_20251219_123456.sql

3. Exécuter migration dans le conteneur
   $ docker exec santaane-api poetry run alembic upgrade head
   
   ✅ Output: [alembic migration output]

4. Vérifier
   $ docker exec santaane-api poetry run alembic current
   
   ✅ Output: "20251219_add_mentor_assignment_table"


OPTION 3 : MIGRATION AUTOMATIQUE AU DÉMARRAGE
==============================================

Le script entrypoint.sh exécute déjà:
   poetry run alembic upgrade head

Donc si vous démarrez l'application normalement:
   $ ./santaane dev
   
✅ La migration se fera automatiquement SANS perdre les données!

Output attendu:
   "📦 Running database migrations..."
   "INFO  [alembic.runtime.migration] Running upgrade..."
   "✅ Migrations completed successfully!"


⚠️  IMPORTANT - CE QUI SE PASSE LORS D'UNE MIGRATION ALEMBIC
===========================================================

✅ CES DONNÉES SONT PRÉSERVÉES:
   - Tous les utilisateurs
   - Tous les manuscrits
   - Tous les rôles et permissions
   - Toutes les relations existantes
   - Tous les reviews, mentorships, etc.

✅ CES STRUCTURES SONT CRÉÉES:
   - Nouvelle table: mentor_assignments
   - Nouveaux indexes sur mentor_assignments
   - Nouvelles contraintes (unique, foreign keys)

❌ CES DONNÉES NE SONT PAS SUPPRIMÉES:
   - Rien n'est supprimé automatiquement
   - Les anciennes tables restent intactes
   - Les données existantes ne changent pas

✅ LA MIGRATION EST IDEMPOTENTE:
   - Vous pouvez la relancer plusieurs fois
   - Elle ne refait pas ce qui est déjà fait
   - Alembic garde trace des migrations appliquées


COMMENT FONCTIONNE ALEMBIC
===========================

Alembic utilise une table spéciale pour tracker les migrations:

   alembic_version
   ===============
   version_num
   -----------
   d39bfc026878_auto_migration_20251110_060724
   20251219_add_mentor_assignment_table  ← ajoutée lors du upgrade

Quand vous executez "alembic upgrade head":
1. Alembic vérifie quelle est la dernière migration appliquée (dans alembic_version)
2. Alembic compare avec la liste des fichiers de migration (/alembic/versions/)
3. Alembic exécute UNIQUEMENT les migrations manquantes
4. Pour chaque nouvelle migration, Alembic:
   - Exécute les commandes du fichier de migration
   - Enregistre la migration dans alembic_version
5. Si un problème survient, la transaction est ANNULÉE (rollback automatique)


VÉRIFICATION APRÈS MIGRATION
============================

1. Vérifier la version
   $ poetry run alembic current
   ✅ Doit afficher: "20251219_add_mentor_assignment_table"

2. Vérifier la table
   $ poetry run python3 -c "
     from app.models import MentorAssignment
     print('MentorAssignment model OK')
   "
   ✅ Doit afficher: "MentorAssignment model OK"

3. Vérifier les données existantes
   $ poetry run python3 -c "
     from app.models import User
     print('Nombre d\'utilisateurs:', User.__table__.select().with_only_columns(User.id).distinct())
   "
   ✅ Doit afficher: le nombre d'utilisateurs existants

4. Vérifier la nouvelle table
   $ poetry run python3 -c "
     from app.models import MentorAssignment
     from sqlalchemy import text
     from app.db import engine
     with engine.connect() as conn:
         result = conn.execute(text('SELECT COUNT(*) FROM mentor_assignments'))
         print('Nombre de mentor_assignments:', result.scalar())
   "
   ✅ Doit afficher: "Nombre de mentor_assignments: 0" (vide initialement)


SI QUELQUE CHOSE SE PASSE MAL
=============================

❌ Erreur: "Migration failed"

Solution:
1. Vérifier les logs
   $ poetry run alembic history
   
2. Voir quelle migration est bloquée
   $ poetry run alembic downgrade -1  # Revenir à la version précédente
   
3. Vérifier la migration (fichier /alembic/versions/20251219_*.py)
   - S'assurer qu'il n'y a pas d'erreurs SQL
   - S'assurer que le down() est correct

4. Réessayer
   $ poetry run alembic upgrade head


RÉCUPÉRATION AVEC UN BACKUP
============================

Si vraiment ça ne marche pas:

1. Vous avez un backup (si vous avez suivi l'étape 3 plus haut)
   $ ls -la backup_*.sql

2. Restaurer le backup
   $ docker exec santaane-postgresql psql -U postgres -d santaane < backup_20251219_123456.sql
   
   ✅ Toutes les données sont restaurées !

3. Revenir à la version précédente
   $ poetry run alembic downgrade -1
   
   ✅ Tout est comme avant


RÉSUMÉ SÉCURITÉ
===============

La migration Alembic est TRÈS SÛRE:

✅ Les données ne sont JAMAIS supprimées
✅ Les tables existantes ne sont PAS modifiées
✅ Seules des NOUVELLES structures sont créées
✅ La migration est enregistrée pour pouvoir revenir en arrière (downgrade)
✅ Si erreur, transaction ANNULÉE automatiquement
✅ Vous pouvez avoir un backup en 1 commande

DONC: Vous pouvez exécuter la migration EN TOUTE SÉCURITÉ! 🎯
"""
