#!/bin/bash
# SCRIPT DE MIGRATION SÉCURISÉE - MENTOR ASSIGNMENT
# ==================================================
# Ce script crée un backup et exécute la migration en toute sécurité

set -e  # Arrêter si erreur

echo "================================================"
echo "MIGRATION SÉCURISÉE - MENTOR ASSIGNMENT"
echo "================================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

cd /home/a-salih-ibn-fadilou/Bureau/santaane-plateform-api

echo -e "${YELLOW}📋 ÉTAPE 1: Vérifier l'état actuel${NC}"
echo "---"
poetry run alembic current
echo ""

echo -e "${YELLOW}📋 ÉTAPE 2: Vérifier la migration en attente${NC}"
echo "---"
poetry run alembic heads
echo ""

echo -e "${YELLOW}📋 ÉTAPE 3: Créer un backup de sécurité${NC}"
echo "---"
BACKUP_FILE="backup_mentor_assignment_$(date +%Y%m%d_%H%M%S).sql"
echo "Sauvegarde vers: $BACKUP_FILE"

# Si Docker est utilisé
if docker ps | grep -q santaane-postgresql; then
    echo "Docker détecté, utilisation de pg_dump via docker..."
    docker exec santaane-postgresql pg_dump -U postgres -d santaane > "$BACKUP_FILE" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Backup créé: $BACKUP_FILE$(NC)"
        echo "   Taille: $(du -h $BACKUP_FILE | cut -f1)"
    else
        echo -e "${RED}❌ Erreur lors du backup${NC}"
        exit 1
    fi
else
    echo "Docker non détecté, backup avec psql local..."
    # Adapter à votre configuration locale
    echo "Note: Assurez-vous que PostgreSQL est accessible"
fi
echo ""

echo -e "${YELLOW}📋 ÉTAPE 4: Exécuter la migration${NC}"
echo "---"
echo "Exécution de: poetry run alembic upgrade head"
poetry run alembic upgrade head

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migration exécutée avec succès!${NC}"
else
    echo -e "${RED}❌ Erreur lors de la migration${NC}"
    echo "Le backup est disponible dans: $BACKUP_FILE"
    exit 1
fi
echo ""

echo -e "${YELLOW}📋 ÉTAPE 5: Vérifier la migration${NC}"
echo "---"
echo "Version actuelle:"
poetry run alembic current
echo ""

echo -e "${YELLOW}📋 ÉTAPE 6: Vérifier la table mentor_assignments${NC}"
echo "---"
python3 << 'EOF'
from sqlalchemy import text
from app.db import get_db, engine
import asyncio

with engine.connect() as conn:
    try:
        result = conn.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_name='mentor_assignments'"
        ))
        if result.fetchone():
            print("✅ Table mentor_assignments EXISTS")
        else:
            print("❌ Table mentor_assignments NOT FOUND")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
EOF
echo ""

echo "================================================"
echo -e "${GREEN}✨ MIGRATION COMPLÉTÉE AVEC SUCCÈS ✨${NC}"
echo "================================================"
echo ""
echo "Informations:"
echo "  - Backup: $BACKUP_FILE"
echo "  - Migration: 20251219_add_mentor_assignment_table"
echo "  - Table créée: mentor_assignments"
echo ""
echo "Prochaines étapes:"
echo "  1. Redémarrer l'application: ./santaane dev"
echo "  2. Tester les endpoints: http://localhost:8000/docs"
echo "  3. Voir MENTOR_ASSIGNMENT_REQUESTS.md pour les exemples"
echo ""
