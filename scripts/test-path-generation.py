#!/usr/bin/env python3
"""
Path Generation Testing Script

Comprehensive testing of the Path Builder Engine and enhanced JSON database
to validate all path generation functionality before Phase 2 development.
"""

import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from montu.shared.json_database import JSONDatabase
from montu.shared.path_builder import PathBuilder


def test_project_config_validation():
    """Test project configuration validation."""
    print("🔍 Testing Project Configuration Validation...")
    
    db = JSONDatabase()
    
    # Test SWA project config validation
    validation_result = db.validate_project_config('SWA')
    
    if validation_result['valid']:
        print("   ✅ SWA project configuration is valid")
    else:
        print("   ❌ SWA project configuration validation failed:")
        for error in validation_result['errors']:
            print(f"      • {error}")
        return False
    
    return True


def test_path_builder_direct():
    """Test PathBuilder directly with project configuration."""
    print("\n🔧 Testing PathBuilder Engine Directly...")
    
    db = JSONDatabase()
    config = db.get_project_config('SWA')
    
    if not config:
        print("   ❌ Could not load SWA project configuration")
        return False
    
    try:
        path_builder = PathBuilder(config)
        print("   ✅ PathBuilder initialized successfully")
    except Exception as e:
        print(f"   ❌ PathBuilder initialization failed: {e}")
        return False
    
    # Test sample task data
    sample_task = {
        'project': 'SWA',
        'episode': 'Ep00',
        'sequence': 'SWA_Ep00_sq0020',
        'shot': 'SWA_Ep00_SH0090',
        'task': 'lighting'
    }
    
    try:
        # Test working file path generation
        working_path = path_builder.generate_working_file_path(sample_task, "003", "maya_scene")
        print(f"   ✅ Working file path: {working_path}")
        
        # Test render output path generation
        render_path = path_builder.generate_render_output_path(sample_task, "015")
        print(f"   ✅ Render output path: {render_path}")
        
        # Test full path generation
        all_paths = path_builder.generate_all_paths(sample_task, "003", "maya_scene")
        print(f"   ✅ Generated filename: {all_paths.filename}")
        print(f"   ✅ Cleaned sequence: {all_paths.sequence_clean}")
        print(f"   ✅ Cleaned shot: {all_paths.shot_clean}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Path generation failed: {e}")
        return False


def test_target_path_structures():
    """Test generation of the specific target path structures."""
    print("\n🎯 Testing Target Path Structure Generation...")
    
    db = JSONDatabase()
    path_builder = db.get_path_builder('SWA')
    
    if not path_builder:
        print("   ❌ Could not get PathBuilder for SWA project")
        return False
    
    # Test case 1: Render output directory
    print("   📁 Testing render output directory generation...")
    task_1 = {
        'project': 'SWA',
        'episode': 'Ep00',
        'sequence': 'SWA_Ep00_sq0010',
        'shot': 'SWA_Ep00_SH0020',
        'task': 'comp'
    }
    
    render_path = path_builder.generate_render_output_path(task_1, "015")
    expected_render = "W:/SWA/all/scene/Ep00/sq0010/SH0020/comp/version/v015/"
    
    print(f"      Generated: {render_path}")
    print(f"      Expected:  {expected_render}")
    
    if render_path.replace('\\', '/') == expected_render:
        print("      ✅ Render output path matches expected structure")
    else:
        print("      ❌ Render output path does not match expected structure")
        return False
    
    # Test case 2: Working file directory
    print("\n   📄 Testing working file path generation...")
    task_2 = {
        'project': 'SWA',
        'episode': 'Ep00',
        'sequence': 'SWA_Ep00_sq0020',
        'shot': 'SWA_Ep00_SH0090',
        'task': 'lighting'
    }
    
    working_path = path_builder.generate_working_file_path(task_2, "003", "maya_scene")
    expected_working = "V:/SWA/all/scene/Ep00/sq0020/SH0090/lighting/version/Ep00_sq0020_SH0090_lighting_master_v003.ma"
    
    print(f"      Generated: {working_path}")
    print(f"      Expected:  {expected_working}")
    
    if working_path.replace('\\', '/') == expected_working:
        print("      ✅ Working file path matches expected structure")
    else:
        print("      ❌ Working file path does not match expected structure")
        return False
    
    return True


def test_database_integration():
    """Test JSON database integration with path generation."""
    print("\n🗄️ Testing Database Integration with Path Generation...")
    
    db = JSONDatabase()
    
    # Create a test task
    test_task = {
        '_id': 'ep00_sq0020_sh0090_lighting',
        'project': 'SWA',
        'type': 'shot',
        'episode': 'Ep00',
        'sequence': 'SWA_Ep00_sq0020',
        'shot': 'SWA_Ep00_SH0090',
        'task': 'lighting',
        'artist': 'TestArtist',
        'status': 'not_started',
        'milestone': 'not_started',
        'priority': 'medium',
        'frame_range': {'start': 1001, 'end': 1120}
    }
    
    # Insert test task
    task_id = db.insert_one('tasks', test_task)
    print(f"   ✅ Inserted test task: {task_id}")
    
    # Test path generation through database
    paths = db.generate_task_paths(task_id, "003", "maya_scene")
    
    if paths:
        print("   ✅ Generated paths through database:")
        print(f"      Working file: {paths['working_file_path']}")
        print(f"      Render output: {paths['render_output_path']}")
        print(f"      Filename: {paths['filename']}")
    else:
        print("   ❌ Failed to generate paths through database")
        return False
    
    # Test updating task with paths
    success = db.update_task_with_paths(task_id, "003", "maya_scene")
    
    if success:
        print("   ✅ Successfully updated task with path information")
        
        # Verify the update
        updated_task = db.find_one('tasks', {'_id': task_id})
        if updated_task and 'working_file_path' in updated_task:
            print(f"   ✅ Verified path in database: {updated_task['working_file_path']}")
        else:
            print("   ❌ Path information not found in updated task")
            return False
    else:
        print("   ❌ Failed to update task with path information")
        return False
    
    # Clean up test task
    db.delete_one('tasks', {'_id': task_id})
    print("   ✅ Cleaned up test task")
    
    return True


def test_name_cleaning():
    """Test name cleaning functionality."""
    print("\n🧹 Testing Name Cleaning Functionality...")
    
    db = JSONDatabase()
    path_builder = db.get_path_builder('SWA')
    
    if not path_builder:
        print("   ❌ Could not get PathBuilder for SWA project")
        return False
    
    # Test cases for name cleaning
    test_cases = [
        {
            'input': {'sequence': 'SWA_Ep00_sq0010', 'shot': 'SWA_Ep00_SH0020', 'episode': 'Ep00'},
            'expected': {'sequence_clean': 'sq0010', 'shot_clean': 'SH0020', 'episode_clean': 'Ep00'}
        },
        {
            'input': {'sequence': 'SWA_Ep01_sq0050', 'shot': 'SWA_Ep01_SH0100', 'episode': 'Ep01'},
            'expected': {'sequence_clean': 'sq0050', 'shot_clean': 'SH0100', 'episode_clean': 'Ep01'}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"   Test case {i}:")
        
        # Generate paths to get cleaned names
        result = path_builder.generate_all_paths(test_case['input'], "001")
        
        actual = {
            'sequence_clean': result.sequence_clean,
            'shot_clean': result.shot_clean,
            'episode_clean': result.episode_clean
        }
        
        print(f"      Input: {test_case['input']}")
        print(f"      Expected: {test_case['expected']}")
        print(f"      Actual: {actual}")
        
        if actual == test_case['expected']:
            print(f"      ✅ Name cleaning test case {i} passed")
        else:
            print(f"      ❌ Name cleaning test case {i} failed")
            return False
    
    return True


def main():
    """Main testing function."""
    print("🧪 Path Generation System Testing")
    print("=" * 50)
    
    tests = [
        test_project_config_validation,
        test_path_builder_direct,
        test_target_path_structures,
        test_database_integration,
        test_name_cleaning
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"   ❌ Test failed: {test.__name__}")
        except Exception as e:
            print(f"   💥 Test error in {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Path generation system is ready for Phase 2.")
        return 0
    else:
        print("❌ Some tests failed. Please review and fix issues before proceeding.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
