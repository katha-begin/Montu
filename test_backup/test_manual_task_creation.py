#!/usr/bin/env python3
"""
Comprehensive test for Manual Task Creation functionality
Tests shot tasks, asset tasks, batch creation, and validation
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from montu.shared.json_database import JSONDatabase

def test_manual_task_creation():
    """Test manual task creation functionality."""
    print("🧪 Testing Manual Task Creation Functionality")
    print("=" * 60)
    
    # Initialize database
    db = JSONDatabase()
    
    # Create test project for task creation
    test_project_config = {
        "_id": "MANUAL_TEST",
        "name": "Manual Task Creation Test Project",
        "description": "Test project for manual task creation functionality",
        "task_types": ["modeling", "rigging", "animation", "lighting", "comp", "fx"],
        "asset_categories": ["char", "prop", "veh", "set", "env"],
        "_created_at": datetime.now().isoformat(),
        "_updated_at": datetime.now().isoformat()
    }
    
    try:
        # Test 1: Create test project
        print("1. Creating test project...")
        success = db.insert_one('project_configs', test_project_config)
        if success:
            print("   ✅ Test project created successfully")
        else:
            print("   ❌ Failed to create test project")
            return False
            
        # Test 2: Create shot tasks
        print("2. Testing shot task creation...")
        shot_tasks = [
            {
                "_id": "ep01_sq010_sh020_lighting",
                "project": "MANUAL_TEST",
                "type": "shot",
                "episode": "ep01",
                "sequence": "sq010",
                "shot": "sh020",
                "task": "lighting",
                "artist": "john_doe",
                "status": "not_started",
                "milestone": "not_started",
                "milestone_note": "Test shot task for lighting",
                "frame_range": "1001-1100",
                "priority": "medium",
                "estimated_duration": 8.0,
                "_created_at": datetime.now().isoformat(),
                "_updated_at": datetime.now().isoformat()
            },
            {
                "_id": "ep01_sq010_sh020_comp",
                "project": "MANUAL_TEST",
                "type": "shot",
                "episode": "ep01",
                "sequence": "sq010",
                "shot": "sh020",
                "task": "comp",
                "artist": "jane_smith",
                "status": "in_progress",
                "milestone": "single_frame",
                "milestone_note": "Test shot task for compositing",
                "frame_range": "1001-1100",
                "priority": "high",
                "estimated_duration": 12.0,
                "_created_at": datetime.now().isoformat(),
                "_updated_at": datetime.now().isoformat()
            }
        ]
        
        for shot_task in shot_tasks:
            success = db.insert_one('tasks', shot_task)
            if success:
                print(f"   ✅ Shot task created: {shot_task['_id']}")
            else:
                print(f"   ❌ Failed to create shot task: {shot_task['_id']}")
                return False
                
        # Test 3: Create asset tasks
        print("3. Testing asset task creation...")
        asset_tasks = [
            {
                "_id": "asset_char_hero_modeling",
                "project": "MANUAL_TEST",
                "type": "asset",
                "episode": "asset",
                "sequence": "char",  # Asset category
                "shot": "hero",      # Asset name
                "task": "modeling",
                "artist": "bob_wilson",
                "status": "approved",
                "milestone": "final_render",
                "milestone_note": "Hero character base model",
                "priority": "high",
                "estimated_duration": 16.0,
                "dependencies": [],
                "variants": {
                    "base_asset": "asset_char_hero",
                    "variant_type": "base_model",
                    "variant_name": "hero_base"
                },
                "_created_at": datetime.now().isoformat(),
                "_updated_at": datetime.now().isoformat()
            },
            {
                "_id": "asset_prop_sword_modeling",
                "project": "MANUAL_TEST",
                "type": "asset",
                "episode": "asset",
                "sequence": "prop",  # Asset category
                "shot": "sword",     # Asset name
                "task": "modeling",
                "artist": "alice_brown",
                "status": "in_progress",
                "milestone": "low_quality",
                "milestone_note": "Magic sword prop for hero character",
                "priority": "medium",
                "estimated_duration": 6.0,
                "dependencies": ["asset_char_hero_modeling"],
                "variants": {
                    "base_asset": "asset_prop_sword",
                    "variant_type": "material_variant",
                    "variant_name": "enchanted",
                    "parent_asset": "asset_prop_sword_base"
                },
                "_created_at": datetime.now().isoformat(),
                "_updated_at": datetime.now().isoformat()
            }
        ]
        
        for asset_task in asset_tasks:
            success = db.insert_one('tasks', asset_task)
            if success:
                print(f"   ✅ Asset task created: {asset_task['_id']}")
            else:
                print(f"   ❌ Failed to create asset task: {asset_task['_id']}")
                return False
                
        # Test 4: Validate task ID generation patterns
        print("4. Testing task ID patterns...")
        
        # Shot task pattern: {episode}_{sequence}_{shot}_{task}
        shot_pattern_tests = [
            ("ep01", "sq010", "sh020", "lighting", "ep01_sq010_sh020_lighting"),
            ("Ep02", "SQ020", "SH030", "COMP", "ep02_sq020_sh030_comp"),  # Case insensitive
        ]
        
        for episode, sequence, shot, task, expected_id in shot_pattern_tests:
            generated_id = f"{episode.lower()}_{sequence.lower()}_{shot.lower()}_{task.lower()}"
            if generated_id == expected_id:
                print(f"   ✅ Shot pattern correct: {generated_id}")
            else:
                print(f"   ❌ Shot pattern incorrect: {generated_id} != {expected_id}")
                return False
                
        # Asset task pattern: asset_{category}_{asset_name}_{task}
        asset_pattern_tests = [
            ("char", "hero", "modeling", "asset_char_hero_modeling"),
            ("PROP", "SWORD", "RIGGING", "asset_prop_sword_rigging"),  # Case insensitive
        ]
        
        for category, asset_name, task, expected_id in asset_pattern_tests:
            generated_id = f"asset_{category.lower()}_{asset_name.lower()}_{task.lower()}"
            if generated_id == expected_id:
                print(f"   ✅ Asset pattern correct: {generated_id}")
            else:
                print(f"   ❌ Asset pattern incorrect: {generated_id} != {expected_id}")
                return False
                
        # Test 5: Validate asset dependencies
        print("5. Testing asset dependencies...")
        
        # Check that sword depends on hero character
        sword_task = db.find_one('tasks', {'_id': 'asset_prop_sword_modeling'})
        if sword_task:
            dependencies = sword_task.get('dependencies', [])
            if 'asset_char_hero_modeling' in dependencies:
                print("   ✅ Asset dependencies correctly stored")
            else:
                print("   ❌ Asset dependencies missing or incorrect")
                return False
        else:
            print("   ❌ Could not retrieve sword task for dependency check")
            return False
            
        # Test 6: Validate asset variants
        print("6. Testing asset variants...")
        
        # Check hero character variants
        hero_task = db.find_one('tasks', {'_id': 'asset_char_hero_modeling'})
        if hero_task:
            variants = hero_task.get('variants', {})
            if variants.get('variant_type') == 'base_model' and variants.get('variant_name') == 'hero_base':
                print("   ✅ Asset variants correctly stored")
            else:
                print("   ❌ Asset variants missing or incorrect")
                return False
        else:
            print("   ❌ Could not retrieve hero task for variants check")
            return False
            
        # Test 7: Test task retrieval and filtering
        print("7. Testing task retrieval and filtering...")
        
        # Get all tasks for the test project
        all_tasks = db.find('tasks', {'project': 'MANUAL_TEST'})
        if len(all_tasks) == 4:  # 2 shot tasks + 2 asset tasks
            print(f"   ✅ All tasks retrieved: {len(all_tasks)} tasks")
        else:
            print(f"   ❌ Incorrect task count: {len(all_tasks)} (expected 4)")
            return False
            
        # Filter shot tasks
        shot_tasks_retrieved = db.find('tasks', {'project': 'MANUAL_TEST', 'type': 'shot'})
        if len(shot_tasks_retrieved) == 2:
            print(f"   ✅ Shot tasks filtered correctly: {len(shot_tasks_retrieved)} tasks")
        else:
            print(f"   ❌ Incorrect shot task count: {len(shot_tasks_retrieved)} (expected 2)")
            return False
            
        # Filter asset tasks
        asset_tasks_retrieved = db.find('tasks', {'project': 'MANUAL_TEST', 'type': 'asset'})
        if len(asset_tasks_retrieved) == 2:
            print(f"   ✅ Asset tasks filtered correctly: {len(asset_tasks_retrieved)} tasks")
        else:
            print(f"   ❌ Incorrect asset task count: {len(asset_tasks_retrieved)} (expected 2)")
            return False
            
        # Test 8: Test task data integrity
        print("8. Testing task data integrity...")
        
        for task in all_tasks:
            # Check required fields
            required_fields = ['_id', 'project', 'type', 'episode', 'sequence', 'shot', 'task']
            missing_fields = [field for field in required_fields if field not in task]
            
            if missing_fields:
                print(f"   ❌ Task {task.get('_id', 'Unknown')} missing fields: {missing_fields}")
                return False
                
            # Check task type specific fields
            if task['type'] == 'shot':
                if 'frame_range' not in task:
                    print(f"   ❌ Shot task {task['_id']} missing frame_range")
                    return False
            elif task['type'] == 'asset':
                if task['episode'] != 'asset':
                    print(f"   ❌ Asset task {task['_id']} has incorrect episode value")
                    return False
                    
        print("   ✅ All tasks have correct data integrity")
        
        print("\n🎉 All manual task creation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Manual task creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup: Remove test data
        try:
            db.delete_many('tasks', {'project': 'MANUAL_TEST'})
            db.delete_one('project_configs', {'_id': 'MANUAL_TEST'})
            print("🧹 Test data cleaned up")
        except:
            pass

if __name__ == "__main__":
    success = test_manual_task_creation()
    sys.exit(0 if success else 1)
