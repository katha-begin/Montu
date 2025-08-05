# Enhanced Database CRUD Operations

**Status**: ✅ **COMPLETED**  
**Date**: August 4, 2025  
**Version**: 2.0.0  

## 📋 Overview

The Montu Manager database system has been enhanced with comprehensive CRUD (Create, Read, Update, Delete) operations that provide MongoDB-compatible functionality while maintaining the JSON file-based architecture for development and testing.

## 🚀 Enhanced Features

### **1. Advanced Querying Operations**

#### **MongoDB-Style Query Operators**
```python
# Comparison operators
db.find('tasks', {'duration': {'$gt': 6.0}})           # Greater than
db.find('tasks', {'priority': {'$ne': 'low'}})         # Not equal
db.find('tasks', {'duration': {'$gte': 4.0, '$lte': 12.0}})  # Range

# Array operators
db.find('tasks', {'priority': {'$in': ['high', 'medium']}})   # In array
db.find('tasks', {'status': {'$nin': ['cancelled']}})         # Not in array

# Pattern matching
db.find('tasks', {'name': {'$regex': 'lighting', '$options': 'i'}})  # Regex

# Logical operators
db.find('tasks', {
    '$and': [
        {'project': 'SWA'},
        {'duration': {'$gte': 4.0}},
        {'priority': {'$ne': 'low'}}
    ]
})

db.find('tasks', {
    '$or': [
        {'priority': 'urgent'},
        {'deadline': {'$lt': '2024-12-31'}}
    ]
})
```

#### **Nested Field Access**
```python
# Query nested fields using dot notation
db.find('tasks', {'metadata.artist.name': 'John Doe'})
db.find('tasks', {'frame_range.start': {'$gte': 1001}})
```

### **2. Sorting and Pagination**

#### **Advanced Find with Options**
```python
# Sorting, pagination, and projection
results = db.find_with_options(
    collection='tasks',
    query={'project': 'SWA'},
    sort=[('priority', -1), ('created_date', 1)],  # -1 desc, 1 asc
    limit=10,
    skip=20,  # For pagination
    projection={'name': 1, 'status': 1, '_id': 0}  # Include/exclude fields
)
```

#### **Projection Examples**
```python
# Include only specific fields
db.find_with_options('tasks', projection={'name': 1, 'status': 1})

# Exclude specific fields
db.find_with_options('tasks', projection={'internal_notes': 0, 'debug_info': 0})
```

### **3. Bulk Operations**

#### **Bulk Write Operations**
```python
bulk_operations = [
    {'operation': 'insert', 'document': {'_id': 'task1', 'name': 'New Task'}},
    {'operation': 'update', 'filter': {'_id': 'task2'}, 'update': {'$set': {'status': 'completed'}}},
    {'operation': 'delete', 'filter': {'_id': 'task3'}},
    {'operation': 'replace', 'filter': {'_id': 'task4'}, 'replacement': {'name': 'Replaced Task'}}
]

results = db.bulk_write('tasks', bulk_operations)
# Returns: {'inserted_count': 1, 'updated_count': 1, 'deleted_count': 1, 'errors': []}
```

#### **Batch Updates**
```python
# Update multiple documents
updated_count = db.update_many(
    'tasks', 
    {'project': 'SWA', 'status': 'pending'}, 
    {'$set': {'status': 'in_progress', 'started_date': datetime.now().isoformat()}}
)

# Advanced update operators
db.update_many('tasks', {'project': 'SWA'}, {
    '$inc': {'version': 1},                    # Increment numeric field
    '$push': {'tags': 'updated'},              # Add to array
    '$pull': {'tags': 'deprecated'},           # Remove from array
    '$unset': {'temp_field': ''}               # Remove field
})
```

#### **Upsert Operations**
```python
# Insert if not exists, update if exists
doc_id = db.upsert(
    'tasks',
    {'_id': 'unique_task'},
    {'$set': {'name': 'Task Name', 'status': 'active'}}
)
```

### **4. Aggregation Pipeline**

#### **Supported Aggregation Stages**
```python
pipeline = [
    # Filter documents
    {'$match': {'project': 'SWA', 'status': 'completed'}},
    
    # Group and calculate
    {'$group': {
        '_id': '$task_type',
        'total_duration': {'$sum': '$duration'},
        'avg_duration': {'$avg': '$duration'},
        'min_duration': {'$min': '$duration'},
        'max_duration': {'$max': '$duration'},
        'task_count': {'$sum': 1},
        'first_task': {'$first': '$name'},
        'last_task': {'$last': '$name'}
    }},
    
    # Sort results
    {'$sort': {'total_duration': -1}},
    
    # Limit results
    {'$limit': 5},
    
    # Project fields
    {'$project': {'task_type': '$_id', 'total_hours': '$total_duration', '_id': 0}}
]

results = db.aggregate('tasks', pipeline)
```

#### **Count Aggregation**
```python
# Count documents matching criteria
count_result = db.aggregate('tasks', [
    {'$match': {'project': 'SWA'}},
    {'$count': 'swa_tasks'}
])
# Returns: [{'count': 42}]
```

### **5. Transaction-Like Operations**

#### **Atomic Operations with Rollback**
```python
def transfer_task_ownership(db_instance):
    # Multiple operations that should succeed or fail together
    db_instance.update_one('tasks', {'_id': 'task1'}, {'$set': {'owner': 'new_owner'}})
    db_instance.insert_one('task_history', {'task_id': 'task1', 'action': 'ownership_transfer'})
    db_instance.update_one('users', {'_id': 'old_owner'}, {'$inc': {'task_count': -1}})
    db_instance.update_one('users', {'_id': 'new_owner'}, {'$inc': {'task_count': 1}})
    return 'transfer_completed'

try:
    result = db.transaction(transfer_task_ownership)
    print(f"Transaction successful: {result}")
except Exception as e:
    print(f"Transaction failed and rolled back: {e}")
```

### **6. Document Validation**

#### **Schema-Based Validation**
```python
task_schema = {
    'required': ['_id', 'name', 'project', 'task_type'],
    'properties': {
        'name': {'type': 'string', 'minLength': 3, 'maxLength': 100},
        'priority': {'type': 'string', 'enum': ['low', 'medium', 'high', 'urgent']},
        'duration': {'type': 'number', 'minimum': 0.5, 'maximum': 40.0},
        'tags': {'type': 'array'},
        'metadata': {'type': 'object'}
    }
}

# Validate before insertion
validation_result = db.validate_document('tasks', document, task_schema)
if validation_result['valid']:
    db.insert_one('tasks', document)
else:
    print(f"Validation errors: {validation_result['errors']}")
```

### **7. Advanced Utility Operations**

#### **Atomic Find and Modify**
```python
# Find and update atomically
updated_doc = db.find_one_and_update(
    'tasks',
    {'_id': 'task1'},
    {'$set': {'status': 'completed'}},
    return_document='after'  # 'before' or 'after'
)

# Find and delete atomically
deleted_doc = db.find_one_and_delete('tasks', {'_id': 'task1'})
```

#### **Distinct Values**
```python
# Get unique values for a field
unique_projects = db.distinct('tasks', 'project')
unique_priorities = db.distinct('tasks', 'priority', {'status': 'active'})
```

#### **Collection Information**
```python
# Get detailed collection statistics
info = db.get_collection_info('tasks')
# Returns: {
#     'exists': True,
#     'count': 150,
#     'size_bytes': 45678,
#     'fields': ['_id', 'name', 'project', 'status', ...],
#     'sample_document': {...},
#     'indexes': [...]
# }
```

## 🗄️ Enhanced Collections

### **New Collections Added**
```python
# Available collections
collections = {
    'tasks': 'Task records and metadata',
    'project_configs': 'Project configuration settings',
    'media_records': 'Media file records and annotations',
    'directory_operations': 'Directory creation and management logs',  # NEW
    'user_sessions': 'User session and activity tracking',            # NEW
    'system_logs': 'System events and error logging'                  # NEW
}
```

## 🔧 Backup and Recovery

### **Database Backup**
```python
# Create timestamped backup
success = db.backup_database('/path/to/backups')

# Restore from backup
success = db.restore_database('/path/to/backup/backup_20240804_143022')
```

## 📊 Performance Features

### **Indexing Support (Simulated)**
```python
# Create indexes for better query performance
db.create_index('tasks', 'project')
db.create_index('tasks', [('project', 1), ('status', 1)])

# List indexes
indexes = db.list_indexes('tasks')

# Drop index
db.drop_index('tasks', 'tasks_project_1')
```

## 🎯 Usage Examples

### **Complete CRUD Workflow**
```python
from montu.shared.json_database import JSONDatabase

# Initialize database
db = JSONDatabase()

# Create with validation
task_schema = {...}  # Define schema
if db.validate_document('tasks', new_task, task_schema)['valid']:
    task_id = db.insert_one('tasks', new_task)

# Read with advanced querying
active_tasks = db.find_with_options(
    'tasks',
    query={'status': {'$in': ['active', 'in_progress']}, 'project': 'SWA'},
    sort=[('priority', -1), ('created_date', 1)],
    limit=20,
    projection={'name': 1, 'status': 1, 'priority': 1}
)

# Update with operators
db.update_many(
    'tasks',
    {'project': 'SWA', 'status': 'pending'},
    {'$set': {'status': 'active'}, '$inc': {'version': 1}}
)

# Delete with conditions
deleted_count = db.delete_many('tasks', {'status': 'cancelled', 'created_date': {'$lt': '2024-01-01'}})

# Aggregate for reporting
project_stats = db.aggregate('tasks', [
    {'$match': {'status': 'completed'}},
    {'$group': {
        '_id': '$project',
        'total_tasks': {'$sum': 1},
        'total_duration': {'$sum': '$duration'},
        'avg_duration': {'$avg': '$duration'}
    }},
    {'$sort': {'total_duration': -1}}
])
```

## ✅ Completion Status

**Database CRUD Operations**: **COMPLETED** ✅

### **Implemented Features**:
- ✅ Advanced querying with MongoDB-style operators
- ✅ Sorting, pagination, and field projection
- ✅ Bulk operations and batch processing
- ✅ Aggregation pipeline with grouping and calculations
- ✅ Transaction-like operations with rollback support
- ✅ Document validation with schema enforcement
- ✅ Atomic find-and-modify operations
- ✅ Backup and recovery functionality
- ✅ Collection management and statistics
- ✅ Index simulation for MongoDB compatibility
- ✅ Enhanced error handling and validation
- ✅ Additional collections for comprehensive data management

### **Backward Compatibility**:
- ✅ All existing CRUD operations remain unchanged
- ✅ Existing applications continue to work without modification
- ✅ Enhanced methods are additive, not breaking changes

### **Testing**:
- ✅ Comprehensive test suite covering all new features
- ✅ Integration tests with existing Montu Manager applications
- ✅ Performance validation for large datasets
- ✅ Error handling and edge case coverage

The enhanced Database CRUD Operations provide a robust, MongoDB-compatible interface while maintaining the simplicity and reliability of the JSON file-based architecture for development and testing environments.
