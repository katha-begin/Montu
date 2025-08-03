#!/usr/bin/env python3
"""
CSV to JSON Conversion Script

Convert the sample CSV data to JSON format for testing the Task Creator
and JSON mock database system.
"""

import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from montu.task_creator.csv_parser import CSVParser
from montu.shared.json_database import JSONDatabase


def main():
    """Main conversion function."""
    # Paths
    project_root = Path(__file__).parent.parent
    csv_file = project_root / "data" / "SWA_Shotlist_Ep00 - task list.csv"
    json_output = project_root / "data" / "converted_tasks.json"
    
    print("🔄 Converting CSV to JSON...")
    print(f"   Input: {csv_file}")
    print(f"   Output: {json_output}")
    
    # Check if CSV file exists
    if not csv_file.exists():
        print(f"❌ CSV file not found: {csv_file}")
        return 1
    
    try:
        # Initialize parser
        parser = CSVParser()
        
        # Parse CSV file
        print("📊 Parsing CSV file...")
        tasks = parser.parse_csv_file(csv_file)
        
        print(f"✅ Parsed {len(tasks)} tasks from CSV")
        
        # Validate tasks
        print("🔍 Validating tasks...")
        valid_tasks, errors = parser.validate_tasks(tasks)
        
        if errors:
            print(f"⚠️  Found {len(errors)} validation errors:")
            for error in errors[:5]:  # Show first 5 errors
                print(f"   • {error}")
            if len(errors) > 5:
                print(f"   ... and {len(errors) - 5} more errors")
        
        print(f"✅ {len(valid_tasks)} valid tasks ready for conversion")
        
        # Convert to dictionaries
        task_dicts = [task.to_dict() for task in valid_tasks]
        
        # Save to JSON file
        print("💾 Saving to JSON file...")
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(task_dicts, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(task_dicts)} tasks to {json_output}")
        
        # Test JSON database integration
        print("\n🧪 Testing JSON Database integration...")
        test_json_database(task_dicts)
        
        # Display sample tasks
        print("\n📋 Sample converted tasks:")
        for i, task in enumerate(task_dicts[:3]):
            print(f"\n   Task {i+1}:")
            print(f"   • ID: {task['_id']}")
            print(f"   • Project: {task['project']}")
            print(f"   • Episode: {task['episode']}")
            print(f"   • Sequence: {task['sequence']}")
            print(f"   • Shot: {task['shot']}")
            print(f"   • Task: {task['task']}")
            print(f"   • Frame Range: {task['frame_range']['start']}-{task['frame_range']['end']}")
            print(f"   • Duration: {task['estimated_duration_hours']} hours")
        
        if len(task_dicts) > 3:
            print(f"   ... and {len(task_dicts) - 3} more tasks")
        
        print(f"\n🎉 Conversion completed successfully!")
        print(f"   • Total tasks: {len(task_dicts)}")
        print(f"   • Validation errors: {len(errors)}")
        print(f"   • Output file: {json_output}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Conversion failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def test_json_database(task_dicts):
    """Test the JSON database with converted tasks."""
    try:
        # Initialize database
        db = JSONDatabase()
        
        # Clear existing tasks
        db.drop_collection('tasks')
        
        # Insert tasks
        print("   📥 Inserting tasks into JSON database...")
        inserted_ids = db.insert_many('tasks', task_dicts)
        print(f"   ✅ Inserted {len(inserted_ids)} tasks")
        
        # Test queries
        print("   🔍 Testing database queries...")
        
        # Count all tasks
        total_count = db.count('tasks')
        print(f"   • Total tasks: {total_count}")
        
        # Count by project
        swa_tasks = db.find('tasks', {'project': 'SWA'})
        print(f"   • SWA project tasks: {len(swa_tasks)}")
        
        # Count by task type
        lighting_tasks = db.find('tasks', {'task': 'Lighting'})
        composite_tasks = db.find('tasks', {'task': 'Composite'})
        print(f"   • Lighting tasks: {len(lighting_tasks)}")
        print(f"   • Composite tasks: {len(composite_tasks)}")
        
        # Test finding by episode
        ep00_tasks = db.find('tasks', {'episode': 'Ep00'})
        print(f"   • Episode Ep00 tasks: {len(ep00_tasks)}")
        
        # Get database stats
        stats = db.get_stats()
        print(f"   📊 Database stats: {stats}")
        
        print("   ✅ JSON database test completed successfully!")
        
    except Exception as e:
        print(f"   ❌ JSON database test failed: {str(e)}")


if __name__ == '__main__':
    sys.exit(main())
