#!/usr/bin/env python3
"""
Migration Testing Framework for Montu Manager Reorganization

This script provides comprehensive testing during the codebase reorganization
to ensure all functionality is preserved and no regressions are introduced.
"""

import sys
import os
import subprocess
import warnings
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class MigrationTester:
    """Comprehensive testing framework for migration validation."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_results = []
        self.warnings_captured = []
    
    def capture_warnings(self):
        """Capture deprecation warnings during testing."""
        self.warnings_captured = []
        
        def warning_handler(message, category, filename, lineno, file=None, line=None):
            self.warnings_captured.append({
                'message': str(message),
                'category': category.__name__,
                'filename': filename,
                'lineno': lineno
            })
        
        warnings.showwarning = warning_handler
    
    def test_backward_compatibility(self) -> bool:
        """Test that old import paths still work with deprecation warnings."""
        print("🔍 Testing backward compatibility...")
        
        self.capture_warnings()
        
        try:
            # Test old imports
            from montu.shared.path_builder import PathBuilder
            from montu.shared.json_database import JSONDatabase
            
            # Check that deprecation warnings were issued
            deprecation_warnings = [w for w in self.warnings_captured 
                                  if w['category'] == 'DeprecationWarning']
            
            if deprecation_warnings:
                print(f"   ✅ Backward compatibility works with {len(deprecation_warnings)} deprecation warnings")
                for warning in deprecation_warnings:
                    print(f"      ⚠️  {warning['message']}")
                return True
            else:
                print("   ⚠️  Backward compatibility works but no deprecation warnings issued")
                return True
                
        except ImportError as e:
            print(f"   ❌ Backward compatibility failed: {e}")
            return False
    
    def test_new_imports(self) -> bool:
        """Test that new import paths work correctly."""
        print("🔍 Testing new import paths...")
        
        try:
            # Test new core imports
            from montu.core.path.builder import PathBuilder
            from montu.core.data.database import JSONDatabase
            
            print("   ✅ New core imports work correctly")
            return True
            
        except ImportError as e:
            print(f"   ❌ New imports failed: {e}")
            return False
    
    def test_core_functionality(self) -> bool:
        """Test that core functionality is preserved."""
        print("🔍 Testing core functionality preservation...")
        
        try:
            from montu.core.data.database import JSONDatabase
            from montu.core.path.builder import PathBuilder
            
            # Test database functionality
            db = JSONDatabase()
            stats = db.get_stats()
            
            if stats and 'total_documents' in stats:
                print(f"   ✅ Database functionality works: {stats['total_documents']} documents")
            else:
                print("   ⚠️  Database works but stats format unexpected")
            
            # Test path generation functionality
            projects = db.find('project_configs', {})
            if projects:
                path_builder = PathBuilder(projects[0])
                
                # Test basic path generation
                task_data = {
                    'project': 'TEST',
                    'episode': 'ep01',
                    'sequence': 'sq010',
                    'shot': 'sh020',
                    'task': 'lighting'
                }
                
                result = path_builder.generate_all_paths(task_data)
                if result and result.working_file_path:
                    print("   ✅ Path generation functionality works")
                else:
                    print("   ❌ Path generation failed")
                    return False
            else:
                print("   ⚠️  No project configs found for path testing")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Core functionality test failed: {e}")
            return False
    
    def test_individual_test_files(self) -> bool:
        """Run individual test files to ensure they still pass."""
        print("🔍 Testing individual test files...")
        
        test_files = [
            "test_task_mapping_simple.py",
            "test_enhanced_manual_task_creation.py",
            "test_horizontal_scroll_fix.py"
        ]
        
        all_passed = True
        
        for test_file in test_files:
            test_path = self.project_root / test_file
            if test_path.exists():
                try:
                    result = subprocess.run(
                        ["python", str(test_path)],
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=self.project_root
                    )
                    
                    if result.returncode == 0:
                        print(f"   ✅ {test_file} passes")
                    else:
                        print(f"   ❌ {test_file} failed")
                        if result.stderr:
                            print(f"      Error: {result.stderr[:200]}...")
                        all_passed = False
                        
                except subprocess.TimeoutExpired:
                    print(f"   ⏰ {test_file} timed out")
                    all_passed = False
                except Exception as e:
                    print(f"   💥 {test_file} error: {e}")
                    all_passed = False
            else:
                print(f"   ⚠️  {test_file} not found")
        
        return all_passed
    
    def test_application_launches(self) -> bool:
        """Test that applications can still be imported and initialized."""
        print("🔍 Testing application imports...")
        
        try:
            # Test Task Creator import
            from montu.task_creator.main import main as task_creator_main
            print("   ✅ Task Creator imports successfully")
            
            # Test Project Launcher import
            from montu.project_launcher.main import main as project_launcher_main
            print("   ✅ Project Launcher imports successfully")
            
            # Test Review App import
            from montu.review_app.main import main as review_app_main
            print("   ✅ Review App imports successfully")
            
            return True
            
        except ImportError as e:
            print(f"   ❌ Application import failed: {e}")
            return False
    
    def run_comprehensive_test(self) -> bool:
        """Run all migration tests."""
        print("🚀 Montu Manager Migration Testing Framework")
        print("=" * 60)
        
        tests = [
            ("Backward Compatibility", self.test_backward_compatibility),
            ("New Import Paths", self.test_new_imports),
            ("Core Functionality", self.test_core_functionality),
            ("Individual Test Files", self.test_individual_test_files),
            ("Application Imports", self.test_application_launches)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 40)
            
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"   💥 Test framework error: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 MIGRATION TEST SUMMARY")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status:8} {test_name}")
            if result:
                passed += 1
        
        success_rate = (passed / total) * 100
        print(f"\nResult: {passed}/{total} tests passed ({success_rate:.1f}%)")
        
        if passed == total:
            print("🎉 All migration tests passed! System is ready for next phase.")
            return True
        else:
            print("⚠️  Some migration tests failed. Review issues before proceeding.")
            return False

def main():
    """Main entry point for migration testing."""
    tester = MigrationTester()
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
