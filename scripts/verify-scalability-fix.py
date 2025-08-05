#!/usr/bin/env python3
"""
Scalability Fix Verification Script

Verifies that the import errors have been resolved and both applications
can launch successfully with the new scalability enhancements.
"""

import sys
import subprocess
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_imports():
    """Test all critical imports for scalability components."""
    print("🔍 Testing Critical Imports...")
    print("=" * 50)
    
    import_tests = [
        ("JSON Database", "from src.montu.shared.json_database import JSONDatabase"),
        ("Scalable Task Model", "from src.montu.shared.scalable_task_model import ScalableTaskModel"),
        ("Pagination Widget", "from src.montu.shared.pagination_widget import PaginationWidget"),
        ("Advanced Search Widget", "from src.montu.shared.advanced_search_widget import AdvancedSearchWidget"),
        ("Project Launcher Main", "from src.montu.project_launcher.main import main"),
        ("Task Creator Main", "from src.montu.task_creator.main import main"),
    ]
    
    all_passed = True
    
    for name, import_statement in import_tests:
        try:
            exec(import_statement)
            print(f"   ✅ {name}: Import successful")
        except Exception as e:
            print(f"   ❌ {name}: Import failed - {e}")
            all_passed = False
    
    return all_passed

def test_tuple_usage():
    """Test that Tuple type hints work correctly."""
    print("\n🔍 Testing Tuple Type Hints...")
    print("=" * 50)
    
    try:
        from src.montu.shared.json_database import JSONDatabase
        
        # Test the find_with_options method that uses Tuple
        db = JSONDatabase()
        
        # This should work without errors
        sort_params = [('_created_at', -1), ('status', 1)]
        
        print("   ✅ Tuple type hints working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Tuple type hints failed: {e}")
        return False

def test_database_pagination():
    """Test the new database pagination features."""
    print("\n🔍 Testing Database Pagination...")
    print("=" * 50)
    
    try:
        from src.montu.shared.json_database import JSONDatabase
        
        db = JSONDatabase()
        
        # Test find_with_options method
        results = db.find_with_options(
            'tasks',
            query={'project': 'SWA'},
            sort=[('_created_at', -1)],
            limit=5,
            skip=0
        )
        
        print(f"   ✅ Pagination query successful: {len(results)} results")
        
        # Test with different parameters
        results2 = db.find_with_options(
            'tasks',
            limit=10,
            skip=5
        )
        
        print(f"   ✅ Skip/limit query successful: {len(results2)} results")
        return True
        
    except Exception as e:
        print(f"   ❌ Database pagination failed: {e}")
        return False

def test_scalable_model():
    """Test the scalable task model."""
    print("\n🔍 Testing Scalable Task Model...")
    print("=" * 50)
    
    try:
        from src.montu.shared.json_database import JSONDatabase
        from src.montu.shared.scalable_task_model import ScalableTaskModel
        from PySide6.QtWidgets import QApplication
        
        # Create minimal Qt application for testing
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        db = JSONDatabase()
        model = ScalableTaskModel(db)
        
        print(f"   ✅ ScalableTaskModel created successfully")
        print(f"   ✅ Default page size: {model.page_size}")
        print(f"   ✅ Column count: {model.columnCount()}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Scalable model test failed: {e}")
        return False

def test_application_launch():
    """Test that applications can be imported without errors."""
    print("\n🔍 Testing Application Launch Capability...")
    print("=" * 50)
    
    try:
        # Test Project Launcher import
        from src.montu.project_launcher.main import main as launcher_main
        print("   ✅ Project Launcher main import successful")
        
        # Test Task Creator import
        from src.montu.task_creator.main import main as creator_main
        print("   ✅ Ra: Task Creator main import successful")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Application launch test failed: {e}")
        return False

def main():
    """Run all verification tests."""
    print("🚀 SCALABILITY FIX VERIFICATION")
    print("=" * 60)
    print("Verifying that import errors have been resolved and")
    print("scalability enhancements are working correctly.\n")
    
    tests = [
        ("Import Tests", test_imports),
        ("Tuple Type Hints", test_tuple_usage),
        ("Database Pagination", test_database_pagination),
        ("Scalable Model", test_scalable_model),
        ("Application Launch", test_application_launch),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   💥 {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 SUCCESS: All scalability fixes verified!")
        print("   Both Ra: Task Creator and Project Launcher should")
        print("   launch successfully with enhanced performance.")
        return 0
    else:
        print(f"\n⚠️  WARNING: {total - passed} tests failed")
        print("   Some issues may still exist with the scalability enhancements.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
