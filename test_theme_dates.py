#!/usr/bin/env python3
"""
Test script for theme date functionality
"""
import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

async def test_theme_date_logic():
    """Test the theme date filtering logic without database connection"""
    print("🧪 Test de la logique de filtrage des thèmes par date")
    
    # Simuler des données de thèmes
    current_time = datetime.now(timezone.utc).replace(tzinfo=None)
    
    # Thèmes simulés
    themes_data = [
        {
            "id": 1,
            "title": "Thème sans date limite",
            "description": "Ce thème n'a pas de date limite",
            "date_limite": None
        },
        {
            "id": 2,
            "title": "Thème actif",
            "description": "Ce thème expire dans 30 jours",
            "date_limite": current_time + timedelta(days=30)
        },
        {
            "id": 3,
            "title": "Thème expiré",
            "description": "Ce thème a expiré hier",
            "date_limite": current_time - timedelta(days=1)
        },
        {
            "id": 4,
            "title": "Thème qui expire bientôt",
            "description": "Ce thème expire dans 1 heure",
            "date_limite": current_time + timedelta(hours=1)
        }
    ]
    
    print(f"⏰ Heure actuelle: {current_time}")
    print()
    
    # Test de la logique de filtrage pour les thèmes actifs
    print("✅ Thèmes actifs (sans date limite OU date limite dans le futur):")
    active_themes = [
        theme for theme in themes_data 
        if theme["date_limite"] is None or theme["date_limite"] > current_time
    ]
    for theme in active_themes:
        date_str = "Pas de limite" if theme["date_limite"] is None else f"Expire le {theme['date_limite']}"
        print(f"  - {theme['title']} ({date_str})")
    
    print()
    
    # Test de la logique de filtrage pour les thèmes expirés
    print("❌ Thèmes expirés (avec date limite dans le passé):")
    expired_themes = [
        theme for theme in themes_data 
        if theme["date_limite"] is not None and theme["date_limite"] <= current_time
    ]
    for theme in expired_themes:
        print(f"  - {theme['title']} (Expiré le {theme['date_limite']})")
    
    print()
    print("📊 Résumé:")
    print(f"  - Total des thèmes: {len(themes_data)}")
    print(f"  - Thèmes actifs: {len(active_themes)}")
    print(f"  - Thèmes expirés: {len(expired_themes)}")
    
    # Validation
    assert len(active_themes) == 3, f"Expected 3 active themes, got {len(active_themes)}"
    assert len(expired_themes) == 1, f"Expected 1 expired theme, got {len(expired_themes)}"
    print("✅ Tous les tests logiques réussis!")

if __name__ == "__main__":
    asyncio.run(test_theme_date_logic())