"""
Script de test rapide pour vérifier l'API d'annotations
Usage: python test_annotation_api.py
"""
import json
import uuid

# Exemple de données pour tester la validation
test_annotation_create = {
    "annotationType": "text",
    "pageNumber": 1,
    "xPosition": 146.44,
    "yPosition": 402.74,
    "positionData": json.dumps({
        "boundingRect": {
            "x1": 146.44,
            "y1": 402.74,
            "x2": 246.44,
            "y2": 422.74,
            "width": 100,
            "height": 20,
            "pageNumber": 1
        },
        "rects": [
            {
                "x1": 146.44,
                "y1": 402.74,
                "x2": 246.44,
                "y2": 422.74,
                "pageNumber": 1
            }
        ],
        "pageNumber": 1
    }),
    "comment": "Ceci est un test de commentaire",
    "contentData": json.dumps({
        "text": "Texte sélectionné pour le test"
    })
}

# Exemple de données invalides (JSON mal formé)
test_invalid_json = {
    "annotationType": "text",
    "pageNumber": 1,
    "xPosition": 146.44,
    "yPosition": 402.74,
    "positionData": "{invalid json}",  # JSON invalide
    "comment": "Test avec JSON invalide"
}

# Test de validation Pydantic
print("=" * 60)
print("TEST DE VALIDATION PYDANTIC")
print("=" * 60)

try:
    from app.modules.manuscripts.annotation_schemas import AnnotationCreate

    print("\n✓ Test 1: Validation avec données valides")
    valid_annotation = AnnotationCreate(**test_annotation_create)
    print(f"  → annotationType: {valid_annotation.annotationType}")
    print(f"  → pageNumber: {valid_annotation.pageNumber}")
    print(f"  → positionData est un JSON valide: {len(valid_annotation.positionData)} caractères")
    print(f"  → contentData est un JSON valide: {len(valid_annotation.contentData)} caractères")
    print("  ✅ SUCCÈS")

except Exception as e:
    print(f"  ❌ ÉCHEC: {e}")

try:
    print("\n✓ Test 2: Validation avec JSON invalide (devrait échouer)")
    invalid_annotation = AnnotationCreate(**test_invalid_json)
    print("  ❌ ÉCHEC: La validation aurait dû échouer!")

except ValueError as e:
    print(f"  ✅ SUCCÈS: Validation a correctement rejeté le JSON invalide")
    print(f"  → Erreur: {str(e)}")

except Exception as e:
    print(f"  ⚠️  Erreur inattendue: {e}")

# Test de génération UUID
print("\n" + "=" * 60)
print("TEST DE GÉNÉRATION UUID")
print("=" * 60)

try:
    from app.models.manuscript_annotation import ManuscriptAnnotation

    print("\n✓ Test 3: Génération automatique d'UUID")
    # Simuler la création d'une annotation
    annotation = ManuscriptAnnotation(
        manuscript_id=1,
        evaluator_id=1,
        annotation_type="text",
        page_number=1,
        x_position=100.0,
        y_position=200.0,
        position_data='{"test": "data"}',
        comment="Test comment"
    )

    print(f"  → UUID généré: {annotation.id}")
    print(f"  → Type: {type(annotation.id)}")
    print(f"  → Longueur: {len(annotation.id)}")

    # Vérifier que c'est un UUID valide
    try:
        uuid_obj = uuid.UUID(annotation.id)
        print(f"  → Version UUID: {uuid_obj.version}")
        print("  ✅ SUCCÈS: UUID valide généré")
    except ValueError:
        print("  ❌ ÉCHEC: UUID invalide")

except Exception as e:
    print(f"  ❌ ÉCHEC: {e}")

print("\n" + "=" * 60)
print("TESTS TERMINÉS")
print("=" * 60)
print("\nPour tester l'API complète:")
print("1. Démarrer le serveur: ./santaane run")
print("2. Tester avec curl ou Postman")
print("\nExemple de requête POST:")
print("curl -X POST http://localhost:8000/api/v1/manuscripts/1/annotations \\")
print("  -H 'Authorization: Bearer YOUR_TOKEN' \\")
print("  -H 'Content-Type: application/json' \\")
print("  -d '" + json.dumps(test_annotation_create, indent=2) + "'")
