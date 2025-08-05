#!/usr/bin/env python3
"""
Database CRUD Operations Demo

Practical demonstration of all CRUD operations in the Montu Manager
JSON Database system with real-world examples.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def demo_create_operations():
    """Demonstrate CREATE operations."""
    print("🔧 CREATE Operations Demo")
    print("=" * 40)
    
    from montu.shared.json_database import JSONDatabase
    db = JSONDatabase()
    
    # 1. Create single task
    lighting_task = {
        'name': 'Lighting Shot 001',
        'project': 'DEMO_PROJECT',
        'sequence': 'sq0010',
        'shot': 'sh0010',
        'task': 'lighting',
        'status': 'pending',
        'priority': 3,
        'artist': 'John Doe',
        'estimated_hours': 8.5,
        'metadata': {
            'department': 'VFX',
            'frame_range': {'start': 1001, 'end': 1100},
            'software': ['Maya', 'Arnold']
        }
    }
    
    task_id = db.insert_one('tasks', lighting_task)
    print(f"   ✅ Created lighting task: {task_id}")
    
    # 2. Create multiple tasks (batch)
    comp_tasks = [
        {
            'name': 'Composite Shot 001',
            'project': 'DEMO_PROJECT',
            'sequence': 'sq0010',
            'shot': 'sh0010',
            'task': 'composite',
            'status': 'pending',
            'priority': 2,
            'artist': 'Jane Smith',
            'estimated_hours': 6.0
        },
        {
            'name': 'Composite Shot 002',
            'project': 'DEMO_PROJECT',
            'sequence': 'sq0010',
            'shot': 'sh0020',
            'task': 'composite',
            'status': 'pending',
            'priority': 2,
            'artist': 'Jane Smith',
            'estimated_hours': 5.5
        }
    ]
    
    comp_ids = db.insert_many('tasks', comp_tasks)
    print(f"   ✅ Created {len(comp_ids)} composite tasks")
    
    # 3. Upsert operation
    unique_task_id = db.upsert(
        'tasks',
        {'unique_identifier': 'master_scene_setup'},
        {'$set': {
            'name': 'Master Scene Setup',
            'project': 'DEMO_PROJECT',
            'status': 'active',
            'unique_identifier': 'master_scene_setup'
        }}
    )
    print(f"   ✅ Upserted unique task: {unique_task_id}")
    
    return [task_id] + comp_ids + [unique_task_id]

def demo_read_operations():
    """Demonstrate READ operations."""
    print("\n📖 READ Operations Demo")
    print("=" * 40)
    
    from montu.shared.json_database import JSONDatabase
    db = JSONDatabase()
    
    # 1. Find all project tasks
    all_demo_tasks = db.find('tasks', {'project': 'DEMO_PROJECT'})
    print(f"   📊 Total demo project tasks: {len(all_demo_tasks)}")
    
    # 2. Complex query with operators
    high_priority_tasks = db.find('tasks', {
        'project': 'DEMO_PROJECT',
        'priority': {'$gte': 3},
        'status': {'$in': ['pending', 'active']}
    })
    print(f"   🔍 High priority active/pending tasks: {len(high_priority_tasks)}")
    
    # 3. Nested field query
    vfx_tasks = db.find('tasks', {
        'project': 'DEMO_PROJECT',
        'metadata.department': 'VFX'
    })
    print(f"   🎬 VFX department tasks: {len(vfx_tasks)}")
    
    # 4. Advanced find with sorting and pagination
    sorted_tasks = db.find_with_options(
        'tasks',
        query={'project': 'DEMO_PROJECT'},
        sort=[('priority', -1), ('estimated_hours', 1)],
        limit=3,
        projection={'name': 1, 'priority': 1, 'estimated_hours': 1}
    )
    
    print(f"   📋 Top 3 tasks by priority:")
    for task in sorted_tasks:
        print(f"      - {task['name']} (Priority: {task.get('priority', 'N/A')}, Hours: {task.get('estimated_hours', 'N/A')})")
    
    # 5. Count operations
    pending_count = db.count('tasks', {'project': 'DEMO_PROJECT', 'status': 'pending'})
    print(f"   📈 Pending tasks count: {pending_count}")
    
    return all_demo_tasks

def demo_update_operations():
    """Demonstrate UPDATE operations."""
    print("\n✏️ UPDATE Operations Demo")
    print("=" * 40)
    
    from montu.shared.json_database import JSONDatabase
    db = JSONDatabase()
    
    # 1. Update single task status
    success = db.update_one(
        'tasks',
        {'project': 'DEMO_PROJECT', 'task': 'lighting'},
        {'$set': {
            'status': 'in_progress',
            'start_date': datetime.now().isoformat(),
            'notes': 'Started lighting work'
        }}
    )
    print(f"   ✅ Updated lighting task status: {success}")
    
    # 2. Increment version and add to array
    success = db.update_one(
        'tasks',
        {'project': 'DEMO_PROJECT', 'task': 'lighting'},
        {
            '$inc': {'version': 1},
            '$push': {'work_log': f'Version increment at {datetime.now().isoformat()}'}
        }
    )
    print(f"   ✅ Incremented version and added log: {success}")
    
    # 3. Update multiple tasks (batch assignment)
    updated_count = db.update_many(
        'tasks',
        {'project': 'DEMO_PROJECT', 'task': 'composite'},
        {'$set': {
            'status': 'assigned',
            'assignment_date': datetime.now().isoformat()
        }}
    )
    print(f"   ✅ Batch assigned {updated_count} composite tasks")
    
    # 4. Atomic find and update
    updated_task = db.find_one_and_update(
        'tasks',
        {'project': 'DEMO_PROJECT', 'unique_identifier': 'master_scene_setup'},
        {'$set': {'status': 'completed', 'completion_date': datetime.now().isoformat()}},
        return_document='after'
    )
    
    if updated_task:
        print(f"   ✅ Atomically completed task: {updated_task['name']}")
    
    # 5. Complex update with nested fields
    success = db.update_one(
        'tasks',
        {'project': 'DEMO_PROJECT', 'task': 'lighting'},
        {'$set': {
            'metadata.render_settings': {
                'samples': 1024,
                'resolution': '1920x1080',
                'format': 'exr'
            },
            'metadata.last_modified': datetime.now().isoformat()
        }}
    )
    print(f"   ✅ Updated nested metadata: {success}")

def demo_delete_operations():
    """Demonstrate DELETE operations."""
    print("\n🗑️ DELETE Operations Demo")
    print("=" * 40)
    
    from montu.shared.json_database import JSONDatabase
    db = JSONDatabase()
    
    # 1. Delete single task
    success = db.delete_one('tasks', {
        'project': 'DEMO_PROJECT',
        'unique_identifier': 'master_scene_setup'
    })
    print(f"   ✅ Deleted unique task: {success}")
    
    # 2. Atomic find and delete
    deleted_task = db.find_one_and_delete('tasks', {
        'project': 'DEMO_PROJECT',
        'task': 'lighting'
    })
    
    if deleted_task:
        print(f"   ✅ Atomically deleted: {deleted_task['name']}")
    
    # 3. Delete multiple tasks (cleanup)
    deleted_count = db.delete_many('tasks', {'project': 'DEMO_PROJECT'})
    print(f"   ✅ Cleaned up {deleted_count} demo tasks")

def demo_advanced_features():
    """Demonstrate advanced database features."""
    print("\n🚀 ADVANCED Features Demo")
    print("=" * 40)
    
    from montu.shared.json_database import JSONDatabase
    db = JSONDatabase()
    
    # Setup data for advanced demos
    demo_data = [
        {'name': 'Task A', 'project': 'ADV_DEMO', 'status': 'completed', 'hours': 8, 'artist': 'John'},
        {'name': 'Task B', 'project': 'ADV_DEMO', 'status': 'completed', 'hours': 6, 'artist': 'Jane'},
        {'name': 'Task C', 'project': 'ADV_DEMO', 'status': 'active', 'hours': 4, 'artist': 'John'},
        {'name': 'Task D', 'project': 'ADV_DEMO', 'status': 'pending', 'hours': 10, 'artist': 'Bob'}
    ]
    db.insert_many('tasks', demo_data)
    
    # 1. Transaction example
    def batch_update_transaction(db_instance):
        # Update all pending tasks to active
        db_instance.update_many('tasks', 
            {'project': 'ADV_DEMO', 'status': 'pending'}, 
            {'$set': {'status': 'active'}}
        )
        # Add completion bonus to completed tasks
        db_instance.update_many('tasks',
            {'project': 'ADV_DEMO', 'status': 'completed'},
            {'$inc': {'bonus_hours': 2}}
        )
        return "batch_complete"
    
    result = db.transaction(batch_update_transaction)
    print(f"   ✅ Transaction completed: {result}")
    
    # 2. Aggregation pipeline
    pipeline = [
        {'$match': {'project': 'ADV_DEMO'}},
        {'$group': {
            '_id': '$status',
            'count': {'$sum': 1},
            'total_hours': {'$sum': '$hours'},
            'avg_hours': {'$avg': '$hours'}
        }},
        {'$sort': {'total_hours': -1}}
    ]
    
    agg_results = db.aggregate('tasks', pipeline)
    print(f"   📊 Aggregation results:")
    for result in agg_results:
        print(f"      Status: {result['_id']}, Count: {result['count']}, "
              f"Total Hours: {result['total_hours']}, Avg: {result['avg_hours']:.1f}")
    
    # 3. Complex nested query
    # Add nested metadata to one task
    db.update_one('tasks',
        {'project': 'ADV_DEMO', 'name': 'Task A'},
        {'$set': {'metadata': {'quality': {'render': 'high', 'review': 'approved'}}}}
    )
    
    nested_results = db.find('tasks', {
        'project': 'ADV_DEMO',
        'metadata.quality.review': 'approved'
    })
    print(f"   🔍 Nested query results: {len(nested_results)} approved tasks")
    
    # Cleanup
    db.delete_many('tasks', {'project': 'ADV_DEMO'})

def main():
    """Run comprehensive CRUD operations demo."""
    print("🚀 DATABASE CRUD OPERATIONS DEMO")
    print("=" * 60)
    print("Demonstrating practical usage of all CRUD operations")
    print("with real-world VFX production examples.\n")
    
    try:
        # Run all demos
        created_ids = demo_create_operations()
        demo_tasks = demo_read_operations()
        demo_update_operations()
        demo_delete_operations()
        demo_advanced_features()
        
        print("\n" + "=" * 60)
        print("🎉 CRUD OPERATIONS DEMO COMPLETE")
        print("=" * 60)
        print("✅ CREATE: Inserted tasks with metadata and batch operations")
        print("✅ READ: Complex queries with sorting, pagination, and aggregation")
        print("✅ UPDATE: Status changes, increments, and nested field updates")
        print("✅ DELETE: Safe deletion with atomic operations")
        print("✅ ADVANCED: Transactions, aggregation pipelines, nested queries")
        print("\n🎯 All database CRUD operations are fully functional!")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
