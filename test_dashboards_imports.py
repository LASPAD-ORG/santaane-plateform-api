#!/usr/bin/env python3
"""
Script de test pour vérifier que les modules dashboards peuvent être importés correctement
"""
import sys

def test_imports():
    """Test all dashboard module imports"""
    errors = []

    print("Testing dashboard module imports...")
    print("=" * 60)

    # Test 1: Import schemas
    try:
        from app.modules.dashboards import schemas
        print("✓ schemas module imported successfully")
    except Exception as e:
        print(f"✗ Error importing schemas: {e}")
        errors.append(("schemas", e))

    # Test 2: Import repository
    try:
        from app.modules.dashboards import repository
        print("✓ repository module imported successfully")
    except Exception as e:
        print(f"✗ Error importing repository: {e}")
        errors.append(("repository", e))

    # Test 3: Import service
    try:
        from app.modules.dashboards import service
        print("✓ service module imported successfully")
    except Exception as e:
        print(f"✗ Error importing service: {e}")
        errors.append(("service", e))

    # Test 4: Import routes
    try:
        from app.modules.dashboards import routes
        print("✓ routes module imported successfully")
    except Exception as e:
        print(f"✗ Error importing routes: {e}")
        errors.append(("routes", e))

    # Test 5: Import router from __init__
    try:
        from app.modules.dashboards import router
        print("✓ router imported from __init__ successfully")
    except Exception as e:
        print(f"✗ Error importing router: {e}")
        errors.append(("router", e))

    print("=" * 60)

    if errors:
        print(f"\n❌ {len(errors)} errors found:")
        for module, error in errors:
            print(f"  - {module}: {error}")
        return False
    else:
        print("\n✅ All dashboard modules imported successfully!")
        return True

def test_main_app():
    """Test main FastAPI app"""
    print("\nTesting main FastAPI application...")
    print("=" * 60)

    try:
        from app.main import app
        print("✓ Main FastAPI app imported successfully")

        # Check if dashboards router is included
        routes = [route.path for route in app.routes]
        dashboard_routes = [r for r in routes if '/dashboards/' in r]

        if dashboard_routes:
            print(f"✓ Found {len(dashboard_routes)} dashboard routes:")
            for route in sorted(dashboard_routes):
                print(f"  - {route}")
        else:
            print("⚠ Warning: No dashboard routes found in app")

        return True
    except Exception as e:
        print(f"✗ Error importing main app: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()

    if success:
        success = test_main_app()

    if not success:
        sys.exit(1)

    print("\n" + "=" * 60)
    print("🎉 All tests passed!")
    print("=" * 60)
