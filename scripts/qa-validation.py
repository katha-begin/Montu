#!/usr/bin/env python3
"""
Phase 1 QA Validation Script

Automated quality assurance validation for Phase 1 completion.
Runs all critical tests and provides pass/fail certification.
"""

import sys
import subprocess
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from montu.shared.json_database import JSONDatabase
from montu.shared.path_builder import PathBuilder


class QAValidator:
    """Automated QA validation for Phase 1 completion."""
    
    def __init__(self):
        self.results = {}
        self.overall_pass = True
    
    def run_test(self, test_name, test_func):
        """Run a test and record results."""
        print(f"\n🔍 {test_name}...")
        try:
            result = test_func()
            if result:
                print(f"   ✅ PASS: {test_name}")
                self.results[test_name] = "PASS"
            else:
                print(f"   ❌ FAIL: {test_name}")
                self.results[test_name] = "FAIL"
                self.overall_pass = False
        except Exception as e:
            print(f"   💥 ERROR: {test_name} - {str(e)}")
            self.results[test_name] = "ERROR"
            self.overall_pass = False
    
    def test_infrastructure(self):
        """Test Docker infrastructure."""
        try:
            # Check if docker-manager script exists
            script_path = Path(__file__).parent / "docker-manager.py"
            if not script_path.exists():
                print("   ❌ docker-manager.py not found")
                return False
            
            # Try to get status
            result = subprocess.run([
                sys.executable, str(script_path), "status"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and "Running" in result.stdout:
                print("   ✅ Docker services operational")
                return True
            else:
                print("   ⚠️  Docker services not running - attempting start...")
                # Try to start services
                start_result = subprocess.run([
                    sys.executable, str(script_path), "start"
                ], capture_output=True, text=True, timeout=60)
                
                if start_result.returncode == 0:
                    print("   ✅ Docker services started successfully")
                    return True
                else:
                    print(f"   ❌ Failed to start Docker services: {start_result.stderr}")
                    return False
                    
        except subprocess.TimeoutExpired:
            print("   ❌ Docker operations timed out")
            return False
        except Exception as e:
            print(f"   ❌ Infrastructure test error: {e}")
            return False
    
    def test_automated_suite(self):
        """Run the comprehensive automated test suite."""
        try:
            test_script = Path(__file__).parent / "test-path-generation.py"
            if not test_script.exists():
                print("   ❌ test-path-generation.py not found")
                return False
            
            result = subprocess.run([
                sys.executable, str(test_script)
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and "5/5 tests passed" in result.stdout:
                print("   ✅ All automated tests passed")
                return True
            else:
                print("   ❌ Automated tests failed")
                print(f"   Output: {result.stdout[-200:]}")  # Last 200 chars
                return False
                
        except subprocess.TimeoutExpired:
            print("   ❌ Automated tests timed out")
            return False
        except Exception as e:
            print(f"   ❌ Automated test error: {e}")
            return False
    
    def test_target_paths(self):
        """Test target path structure generation."""
        try:
            db = JSONDatabase()
            path_builder = db.get_path_builder('SWA')
            
            if not path_builder:
                print("   ❌ Failed to get PathBuilder for SWA")
                return False
            
            # Test render output path
            task_1 = {
                'project': 'SWA',
                'episode': 'Ep00',
                'sequence': 'SWA_Ep00_sq0010',
                'shot': 'SWA_Ep00_SH0020',
                'task': 'comp'
            }
            
            render_path = path_builder.generate_render_output_path(task_1, '015')
            expected_render = 'W:/SWA/all/scene/Ep00/sq0010/SH0020/comp/version/v015/'
            
            render_match = render_path.replace('\\', '/') == expected_render
            
            # Test working file path
            task_2 = {
                'project': 'SWA',
                'episode': 'Ep00',
                'sequence': 'SWA_Ep00_sq0020',
                'shot': 'SWA_Ep00_SH0090',
                'task': 'lighting'
            }
            
            working_path = path_builder.generate_working_file_path(task_2, '003', 'maya_scene')
            expected_working = 'V:/SWA/all/scene/Ep00/sq0020/SH0090/lighting/version/Ep00_sq0020_SH0090_lighting_master_v003.ma'
            
            working_match = working_path.replace('\\', '/') == expected_working
            
            if render_match and working_match:
                print("   ✅ Both target paths match exactly")
                return True
            else:
                print(f"   ❌ Path mismatches - Render: {render_match}, Working: {working_match}")
                return False
                
        except Exception as e:
            print(f"   ❌ Target path test error: {e}")
            return False
    
    def test_database_operations(self):
        """Test database operations and configuration."""
        try:
            db = JSONDatabase()
            
            # Check database stats
            stats = db.get_stats()
            if not stats or stats.get('total_documents', 0) < 40:
                print(f"   ❌ Insufficient database content: {stats}")
                return False
            
            # Check SWA configuration
            validation = db.validate_project_config('SWA')
            if not validation.get('valid', False):
                print(f"   ❌ SWA configuration invalid: {validation.get('errors', [])}")
                return False
            
            # Test CRUD operations
            test_task = {
                '_id': 'qa_validation_test',
                'project': 'SWA',
                'type': 'shot',
                'episode': 'Ep00',
                'sequence': 'SWA_Ep00_sq9999',
                'shot': 'SWA_Ep00_SH9999',
                'task': 'lighting',
                'artist': 'QA_Validator',
                'status': 'not_started',
                'milestone': 'not_started',
                'priority': 'medium',
                'frame_range': {'start': 1001, 'end': 1100}
            }
            
            # INSERT
            task_id = db.insert_one('tasks', test_task)
            if not task_id:
                print("   ❌ Failed to insert test task")
                return False
            
            # READ
            retrieved = db.find_one('tasks', {'_id': task_id})
            if not retrieved or retrieved['artist'] != 'QA_Validator':
                print("   ❌ Failed to retrieve test task")
                return False
            
            # UPDATE
            update_success = db.update_one('tasks', {'_id': task_id}, {'$set': {'status': 'in_progress'}})
            if not update_success:
                print("   ❌ Failed to update test task")
                return False
            
            # DELETE
            delete_success = db.delete_one('tasks', {'_id': task_id})
            if not delete_success:
                print("   ❌ Failed to delete test task")
                return False
            
            print("   ✅ Database operations and configuration valid")
            return True
            
        except Exception as e:
            print(f"   ❌ Database test error: {e}")
            return False
    
    def test_csv_integration(self):
        """Test CSV integration and Task Creator functionality."""
        try:
            csv_script = Path(__file__).parent / "convert-csv-to-json.py"
            if not csv_script.exists():
                print("   ❌ convert-csv-to-json.py not found")
                return False
            
            result = subprocess.run([
                sys.executable, str(csv_script)
            ], capture_output=True, text=True, timeout=60)
            
            if (result.returncode == 0 and 
                "42 valid tasks" in result.stdout and 
                "Conversion completed successfully" in result.stdout):
                print("   ✅ CSV integration working correctly")
                return True
            else:
                print("   ❌ CSV integration failed")
                print(f"   Output: {result.stdout[-200:]}")  # Last 200 chars
                return False
                
        except subprocess.TimeoutExpired:
            print("   ❌ CSV integration test timed out")
            return False
        except Exception as e:
            print(f"   ❌ CSV integration test error: {e}")
            return False
    
    def generate_report(self):
        """Generate final QA report."""
        print("\n" + "=" * 60)
        print("📊 PHASE 1 QA VALIDATION REPORT")
        print("=" * 60)
        
        for test_name, result in self.results.items():
            status_icon = "✅" if result == "PASS" else "❌" if result == "FAIL" else "💥"
            print(f"{status_icon} {test_name}: {result}")
        
        print("\n" + "-" * 60)
        
        if self.overall_pass:
            print("🎉 OVERALL RESULT: ✅ PASS")
            print("✅ Phase 1 is COMPLETE and ready for Phase 2")
            print("✅ All critical systems validated and operational")
            print("✅ Infrastructure ready for Project Launcher development")
        else:
            print("❌ OVERALL RESULT: ❌ FAIL")
            print("❌ Phase 1 has issues that must be resolved")
            print("❌ Phase 2 development should NOT proceed")
            print("❌ Review failed tests and resolve issues")
        
        print("\n" + "=" * 60)
        
        return self.overall_pass


def main():
    """Main QA validation function."""
    print("🧪 MONTU MANAGER PHASE 1 QA VALIDATION")
    print("=" * 50)
    print("Automated quality assurance validation for Phase 1 completion")
    print("This will test all critical systems and provide certification")
    
    validator = QAValidator()
    
    # Run all validation tests
    validator.run_test("Infrastructure (Docker Backend)", validator.test_infrastructure)
    validator.run_test("Automated Test Suite", validator.test_automated_suite)
    validator.run_test("Target Path Generation", validator.test_target_paths)
    validator.run_test("Database Operations", validator.test_database_operations)
    validator.run_test("CSV Integration", validator.test_csv_integration)
    
    # Generate final report
    overall_pass = validator.generate_report()
    
    # Return appropriate exit code
    return 0 if overall_pass else 1


if __name__ == '__main__':
    sys.exit(main())
