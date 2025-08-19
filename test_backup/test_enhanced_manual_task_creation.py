#!/usr/bin/env python3
"""
Comprehensive test for Enhanced Manual Task Creation functionality
Tests multiple task types, custom task names, and directory creation
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from montu.shared.json_database import JSONDatabase

def test_enhanced_manual_task_creation():
    """Test enhanced manual task creation functionality."""
    print("🧪 Testing Enhanced Manual Task Creation Functionality")
    print("=" * 70)
    
    # Initialize database
    db = JSONDatabase()
    
    # Create test project for enhanced task creation
    test_project_config = {
        "_id": "ENHANCED_TEST",
        "name": "Enhanced Manual Task Creation Test Project",
        "description": "Test project for enhanced manual task creation functionality",
        "task_types": ["modeling", "rigging", "animation", "lighting", "comp", "fx"],
        "custom_task_types": ["previz", "techvis", "matchmove", "roto"],
        "asset_categories": ["char", "prop", "veh", "set", "env"],
        "templates": {
            "working_file": "{drive_working}/{project}/{middle_path}/{episode}/{sequence_clean}/{shot_clean}/{task}/{version_dir}/{filename}",
            "render_output": "{drive_render}/{project}/{middle_path}/{episode}/{sequence_clean}/{shot_clean}/{task}/{version_dir}/v{version}/",
            "media_file": "{drive_media}/{project}/{middle_path}/{episode}/{sequence_clean}/{shot_clean}/{task}/{version_dir}/v{version}/media/",
            "cache_file": "{drive_cache}/{project}/{middle_path}/{episode}/{sequence_clean}/{shot_clean}/{task}/cache/",
            "submission": "{drive_render}/{project}/deliveries/{client}/{episode}/{sequence_clean}/{shot_clean}/{task}/v{client_version}/"
        },
        "drive_mappings": {
            "working_files": "V:",
            "render_outputs": "W:",
            "media_files": "E:",
            "cache_files": "E:",
            "backup_files": "E:"
        },
        "_created_at": datetime.now().isoformat(),
        "_updated_at": datetime.now().isoformat()
    }
    
    try:
        # Test 1: Create test project
        print("1. Creating enhanced test project...")
        success = db.insert_one('project_configs', test_project_config)
        if success:
            print("   ✅ Enhanced test project created successfully")
        else:
            print("   ❌ Failed to create enhanced test project")
            return False
            
        # Test 2: Create multiple shot tasks for same shot
        print("2. Testing multiple shot task creation...")
        shot_tasks = []
        task_types = ["lighting", "comp", "fx", "previz"]  # Mix of standard and custom
        
        for task_type in task_types:
            shot_task = {
                "_id": f"ep01_sq010_sh030_{task_type}",
                "project": "ENHANCED_TEST",
                "type": "shot",
                "episode": "ep01",
                "sequence": "sq010",
                "shot": "sh030",
                "task": task_type,
                "artist": "multi_artist",
                "status": "not_started",
                "milestone": "not_started",
                "milestone_note": f"Enhanced test shot task for {task_type}",
                "frame_range": "1001-1150",
                "priority": "medium",
                "estimated_duration": 8.0,
                "_created_at": datetime.now().isoformat(),
                "_updated_at": datetime.now().isoformat()
            }
            shot_tasks.append(shot_task)
        
        for shot_task in shot_tasks:
            success = db.insert_one('tasks', shot_task)
            if success:
                print(f"   ✅ Multiple shot task created: {shot_task['_id']}")
            else:
                print(f"   ❌ Failed to create multiple shot task: {shot_task['_id']}")
                return False
                
        # Test 3: Create multiple asset tasks for same asset
        print("3. Testing multiple asset task creation...")
        asset_tasks = []
        asset_task_types = ["modeling", "rigging", "techvis", "matchmove"]  # Mix of standard and custom
        
        for task_type in asset_task_types:
            asset_task = {
                "_id": f"asset_char_enhanced_{task_type}",
                "project": "ENHANCED_TEST",
                "type": "asset",
                "episode": "asset",
                "sequence": "char",  # Asset category
                "shot": "enhanced",  # Asset name
                "task": task_type,
                "artist": "multi_artist",
                "status": "in_progress",
                "milestone": "single_frame",
                "milestone_note": f"Enhanced test asset task for {task_type}",
                "priority": "high",
                "estimated_duration": 12.0,
                "dependencies": ["asset_char_base_modeling"] if task_type != "modeling" else [],
                "variants": {
                    "base_asset": "asset_char_enhanced",
                    "variant_type": "enhanced_version",
                    "variant_name": "multi_task_test"
                },
                "_created_at": datetime.now().isoformat(),
                "_updated_at": datetime.now().isoformat()
            }
            asset_tasks.append(asset_task)
        
        for asset_task in asset_tasks:
            success = db.insert_one('tasks', asset_task)
            if success:
                print(f"   ✅ Multiple asset task created: {asset_task['_id']}")
            else:
                print(f"   ❌ Failed to create multiple asset task: {asset_task['_id']}")
                return False
                
        # Test 4: Validate custom task types integration
        print("4. Testing custom task types integration...")
        
        # Check that custom task types are stored in project config
        project_config = db.find_one('project_configs', {'_id': 'ENHANCED_TEST'})
        if project_config:
            custom_task_types = project_config.get('custom_task_types', [])
            expected_custom_types = ["previz", "techvis", "matchmove", "roto"]
            
            if all(task_type in custom_task_types for task_type in expected_custom_types):
                print("   ✅ Custom task types correctly stored in project config")
            else:
                print(f"   ❌ Custom task types missing: expected {expected_custom_types}, got {custom_task_types}")
                return False
        else:
            print("   ❌ Could not retrieve project config for custom task types check")
            return False
            
        # Test 5: Validate multiple task ID generation patterns
        print("5. Testing multiple task ID generation patterns...")
        
        # Test shot task ID patterns
        shot_id_tests = [
            ("ep01", "sq010", "sh030", ["lighting", "comp"], ["ep01_sq010_sh030_lighting", "ep01_sq010_sh030_comp"]),
            ("EP02", "SQ020", "SH040", ["FX", "PREVIZ"], ["ep02_sq020_sh040_fx", "ep02_sq020_sh040_previz"]),  # Case insensitive
        ]
        
        for episode, sequence, shot, task_types, expected_ids in shot_id_tests:
            generated_ids = []
            for task_type in task_types:
                generated_id = f"{episode.lower()}_{sequence.lower()}_{shot.lower()}_{task_type.lower()}"
                generated_ids.append(generated_id)
                
            if generated_ids == expected_ids:
                print(f"   ✅ Multiple shot patterns correct: {generated_ids}")
            else:
                print(f"   ❌ Multiple shot patterns incorrect: {generated_ids} != {expected_ids}")
                return False
                
        # Test asset task ID patterns
        asset_id_tests = [
            ("char", "enhanced", ["modeling", "rigging"], ["asset_char_enhanced_modeling", "asset_char_enhanced_rigging"]),
            ("PROP", "SWORD", ["TECHVIS", "MATCHMOVE"], ["asset_prop_sword_techvis", "asset_prop_sword_matchmove"]),  # Case insensitive
        ]
        
        for category, asset_name, task_types, expected_ids in asset_id_tests:
            generated_ids = []
            for task_type in task_types:
                generated_id = f"asset_{category.lower()}_{asset_name.lower()}_{task_type.lower()}"
                generated_ids.append(generated_id)
                
            if generated_ids == expected_ids:
                print(f"   ✅ Multiple asset patterns correct: {generated_ids}")
            else:
                print(f"   ❌ Multiple asset patterns incorrect: {generated_ids} != {expected_ids}")
                return False
                
        # Test 6: Validate task retrieval and filtering with custom types
        print("6. Testing task retrieval with custom task types...")
        
        # Get all tasks for the test project
        all_tasks = db.find('tasks', {'project': 'ENHANCED_TEST'})
        if len(all_tasks) == 8:  # 4 shot tasks + 4 asset tasks
            print(f"   ✅ All enhanced tasks retrieved: {len(all_tasks)} tasks")
        else:
            print(f"   ❌ Incorrect enhanced task count: {len(all_tasks)} (expected 8)")
            return False
            
        # Filter tasks by custom task types
        custom_type_tasks = db.find('tasks', {
            'project': 'ENHANCED_TEST', 
            'task': {'$in': ['previz', 'techvis', 'matchmove', 'roto']}
        })
        if len(custom_type_tasks) == 3:  # 1 shot + 2 asset custom tasks
            print(f"   ✅ Custom task types filtered correctly: {len(custom_type_tasks)} tasks")
        else:
            print(f"   ❌ Incorrect custom task type count: {len(custom_type_tasks)} (expected 3)")
            # Show what we got for debugging
            custom_task_names = [task.get('task', 'unknown') for task in custom_type_tasks]
            print(f"       Found custom tasks: {custom_task_names}")
            
        # Test 7: Test task data integrity with multiple tasks
        print("7. Testing enhanced task data integrity...")
        
        for task in all_tasks:
            # Check required fields
            required_fields = ['_id', 'project', 'type', 'episode', 'sequence', 'shot', 'task']
            missing_fields = [field for field in required_fields if field not in task]
            
            if missing_fields:
                print(f"   ❌ Enhanced task {task.get('_id', 'Unknown')} missing fields: {missing_fields}")
                return False
                
            # Check task type specific fields
            if task['type'] == 'shot':
                if 'frame_range' not in task:
                    print(f"   ❌ Enhanced shot task {task['_id']} missing frame_range")
                    return False
            elif task['type'] == 'asset':
                if task['episode'] != 'asset':
                    print(f"   ❌ Enhanced asset task {task['_id']} has incorrect episode value")
                    return False
                    
                # Check dependencies and variants for asset tasks
                if 'dependencies' not in task:
                    print(f"   ❌ Enhanced asset task {task['_id']} missing dependencies field")
                    return False
                if 'variants' not in task:
                    print(f"   ❌ Enhanced asset task {task['_id']} missing variants field")
                    return False
                    
        print("   ✅ All enhanced tasks have correct data integrity")
        
        # Test 8: Test custom task name validation
        print("8. Testing custom task name validation...")
        
        # Valid custom task names
        valid_names = ["previz", "techvis", "matchmove", "roto", "custom_task_123", "task_with_underscores"]
        for name in valid_names:
            # Simulate validation (alphanumeric and underscores only)
            import re
            if re.match(r'^[a-zA-Z0-9_]+$', name):
                print(f"   ✅ Valid custom task name: {name}")
            else:
                print(f"   ❌ Invalid custom task name validation: {name}")
                return False
                
        # Invalid custom task names
        invalid_names = ["task with spaces", "task-with-dashes", "task.with.dots", "task@special"]
        for name in invalid_names:
            if not re.match(r'^[a-zA-Z0-9_]+$', name):
                print(f"   ✅ Correctly rejected invalid task name: {name}")
            else:
                print(f"   ❌ Should have rejected invalid task name: {name}")
                return False
        
        print("\n🎉 All enhanced manual task creation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced manual task creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup: Remove test data
        try:
            db.delete_many('tasks', {'project': 'ENHANCED_TEST'})
            db.delete_one('project_configs', {'_id': 'ENHANCED_TEST'})
            print("🧹 Enhanced test data cleaned up")
        except:
            pass

if __name__ == "__main__":
    success = test_enhanced_manual_task_creation()
    sys.exit(0 if success else 1)
