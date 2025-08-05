#!/usr/bin/env python3
"""
Database CRUD Operations Test Suite

Comprehensive testing of all Create, Read, Update, Delete operations
in the JSON database system with advanced features and edge cases.
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_create_operations():
    """Test all Create (Insert) operations."""
    print("🔍 Testing CREATE Operations...")
    print("=" * 50)
    
    try:
        from montu.shared.json_database import JSONDatabase
        
        db = JSONDatabase()
        
        # Test 1: Insert single document
        test_doc = {
            'name': 'Test Task',
            'project': 'TEST',
            'status': 'active',
            'priority': 'high',
            'metadata': {
                'artist': 'John Doe',
                'department': 'VFX'
            }
        }
        
        doc_id = db.insert_one('tasks', test_doc)
        print(f"   ✅ Insert one: Created document with ID {doc_id}")
        
        # Verify document was created with metadata
        created_doc = db.find_one('tasks', {'_id': doc_id})
        if created_doc and '_created_at' in created_doc and '_updated_at' in created_doc:
            print(f"   ✅ Metadata added: _created_at and _updated_at present")
        else:
            print(f"   ❌ Metadata missing in created document")
            return False
        
        # Test 2: Insert multiple documents
        test_docs = [
            {'name': 'Task 1', 'project': 'TEST', 'status': 'pending'},
            {'name': 'Task 2', 'project': 'TEST', 'status': 'active'},
            {'name': 'Task 3', 'project': 'TEST', 'status': 'completed'}
        ]
        
        doc_ids = db.insert_many('tasks', test_docs)
        print(f"   ✅ Insert many: Created {len(doc_ids)} documents")
        
        # Test 3: Upsert operation (insert)
        upsert_doc = {'unique_key': 'test_upsert', 'value': 'initial'}
        upsert_id = db.upsert('tasks', {'unique_key': 'test_upsert'}, {'$set': upsert_doc})
        print(f"   ✅ Upsert (insert): Created document with ID {upsert_id}")
        
        # Clean up test documents
        db.delete_many('tasks', {'project': 'TEST'})
        db.delete_one('tasks', {'unique_key': 'test_upsert'})
        
        return True
        
    except Exception as e:
        print(f"   ❌ CREATE operations failed: {e}")
        return False

def test_read_operations():
    """Test all Read (Find) operations."""
    print("\n🔍 Testing READ Operations...")
    print("=" * 50)
    
    try:
        from montu.shared.json_database import JSONDatabase
        
        db = JSONDatabase()
        
        # Setup test data
        test_docs = [
            {'name': 'Task A', 'project': 'READ_TEST', 'priority': 1, 'status': 'active'},
            {'name': 'Task B', 'project': 'READ_TEST', 'priority': 2, 'status': 'pending'},
            {'name': 'Task C', 'project': 'READ_TEST', 'priority': 3, 'status': 'completed'},
            {'name': 'Task D', 'project': 'OTHER', 'priority': 1, 'status': 'active'}
        ]
        doc_ids = db.insert_many('tasks', test_docs)
        
        # Test 1: Find all documents
        all_docs = db.find('tasks')
        print(f"   ✅ Find all: Retrieved {len(all_docs)} total documents")
        
        # Test 2: Find with simple query
        project_docs = db.find('tasks', {'project': 'READ_TEST'})
        if len(project_docs) == 3:
            print(f"   ✅ Simple query: Found {len(project_docs)} documents for project READ_TEST")
        else:
            print(f"   ❌ Simple query: Expected 3, got {len(project_docs)}")
            return False
        
        # Test 3: Find one document
        single_doc = db.find_one('tasks', {'name': 'Task A'})
        if single_doc and single_doc['name'] == 'Task A':
            print(f"   ✅ Find one: Retrieved specific document")
        else:
            print(f"   ❌ Find one: Failed to retrieve specific document")
            return False
        
        # Test 4: Complex query with operators
        complex_docs = db.find('tasks', {
            'project': 'READ_TEST',
            'priority': {'$gte': 2},
            'status': {'$in': ['pending', 'completed']}
        })
        if len(complex_docs) == 2:
            print(f"   ✅ Complex query: Found {len(complex_docs)} documents with operators")
        else:
            print(f"   ❌ Complex query: Expected 2, got {len(complex_docs)}")
            return False
        
        # Test 5: Find with options (sorting, pagination)
        sorted_docs = db.find_with_options(
            'tasks',
            query={'project': 'READ_TEST'},
            sort=[('priority', -1)],
            limit=2,
            skip=0
        )
        if len(sorted_docs) == 2 and sorted_docs[0]['priority'] == 3:
            print(f"   ✅ Find with options: Sorting and pagination working")
        else:
            print(f"   ❌ Find with options: Sorting/pagination failed")
            return False
        
        # Test 6: Count documents
        count = db.count('tasks', {'project': 'READ_TEST'})
        if count == 3:
            print(f"   ✅ Count: Counted {count} documents correctly")
        else:
            print(f"   ❌ Count: Expected 3, got {count}")
            return False
        
        # Clean up
        db.delete_many('tasks', {'project': {'$in': ['READ_TEST', 'OTHER']}})
        
        return True
        
    except Exception as e:
        print(f"   ❌ READ operations failed: {e}")
        return False

def test_update_operations():
    """Test all Update operations."""
    print("\n🔍 Testing UPDATE Operations...")
    print("=" * 50)
    
    try:
        from montu.shared.json_database import JSONDatabase

        db = JSONDatabase()

        # Clean up any existing test data first
        db.delete_many('tasks', {'project': 'UPDATE_TEST'})

        # Setup test data
        test_docs = [
            {'name': 'Update Task 1', 'project': 'UPDATE_TEST', 'status': 'pending', 'version': 1},
            {'name': 'Update Task 2', 'project': 'UPDATE_TEST', 'status': 'pending', 'version': 1},
            {'name': 'Update Task 3', 'project': 'UPDATE_TEST', 'status': 'active', 'version': 1}
        ]
        doc_ids = db.insert_many('tasks', test_docs)
        
        # Test 1: Update one document with $set
        success = db.update_one(
            'tasks',
            {'name': 'Update Task 1'},
            {'$set': {'status': 'completed', 'completion_date': '2024-01-01'}}
        )
        if success:
            updated_doc = db.find_one('tasks', {'name': 'Update Task 1'})
            if updated_doc['status'] == 'completed':
                print(f"   ✅ Update one ($set): Successfully updated document")
            else:
                print(f"   ❌ Update one ($set): Update not applied")
                return False
        else:
            print(f"   ❌ Update one ($set): Update operation failed")
            return False
        
        # Test 2: Update with $inc operator
        success = db.update_one(
            'tasks',
            {'name': 'Update Task 1'},
            {'$inc': {'version': 1}}
        )
        if success:
            updated_doc = db.find_one('tasks', {'name': 'Update Task 1'})
            if updated_doc and updated_doc.get('version') == 2:
                print(f"   ✅ Update one ($inc): Successfully incremented version")
            else:
                print(f"   ❌ Update one ($inc): Increment not applied (version: {updated_doc.get('version') if updated_doc else 'None'})")
                return False
        else:
            print(f"   ❌ Update one ($inc): Update operation failed")
            return False
        
        # Test 3: Update many documents
        # First check how many pending documents we have
        pending_docs = db.find('tasks', {'project': 'UPDATE_TEST', 'status': 'pending'})
        expected_updates = len(pending_docs)

        updated_count = db.update_many(
            'tasks',
            {'project': 'UPDATE_TEST', 'status': 'pending'},
            {'$set': {'status': 'active'}}
        )
        if updated_count == expected_updates:
            print(f"   ✅ Update many: Updated {updated_count} documents")
        else:
            print(f"   ❌ Update many: Expected {expected_updates}, updated {updated_count}")
            return False
        
        # Test 4: Replace one document
        replacement = {
            'name': 'Replaced Task',
            'project': 'UPDATE_TEST',
            'status': 'replaced',
            'new_field': 'new_value'
        }
        success = db.replace_one(
            'tasks',
            {'name': 'Update Task 2'},
            replacement
        )
        if success:
            replaced_doc = db.find_one('tasks', {'name': 'Replaced Task'})
            if replaced_doc and 'new_field' in replaced_doc:
                print(f"   ✅ Replace one: Successfully replaced document")
            else:
                print(f"   ❌ Replace one: Replacement not applied correctly")
                return False
        
        # Test 5: Upsert operation (update existing)
        upsert_id = db.upsert(
            'tasks',
            {'name': 'Update Task 3'},
            {'$set': {'upserted_field': 'updated_value'}}
        )
        if upsert_id:
            upserted_doc = db.find_one('tasks', {'name': 'Update Task 3'})
            if upserted_doc and 'upserted_field' in upserted_doc:
                print(f"   ✅ Upsert (update): Successfully updated existing document")
            else:
                print(f"   ❌ Upsert (update): Update not applied")
                return False
        
        # Test 6: Find and update atomically
        updated_doc = db.find_one_and_update(
            'tasks',
            {'name': 'Replaced Task'},
            {'$set': {'atomic_update': True}},
            return_document='after'
        )
        if updated_doc and updated_doc.get('atomic_update'):
            print(f"   ✅ Find and update: Atomic operation successful")
        else:
            print(f"   ❌ Find and update: Atomic operation failed")
            return False
        
        # Clean up
        db.delete_many('tasks', {'project': 'UPDATE_TEST'})
        
        return True
        
    except Exception as e:
        print(f"   ❌ UPDATE operations failed: {e}")
        return False

def test_delete_operations():
    """Test all Delete operations."""
    print("\n🔍 Testing DELETE Operations...")
    print("=" * 50)
    
    try:
        from montu.shared.json_database import JSONDatabase
        
        db = JSONDatabase()
        
        # Setup test data
        test_docs = [
            {'name': 'Delete Task 1', 'project': 'DELETE_TEST', 'status': 'pending'},
            {'name': 'Delete Task 2', 'project': 'DELETE_TEST', 'status': 'pending'},
            {'name': 'Delete Task 3', 'project': 'DELETE_TEST', 'status': 'active'},
            {'name': 'Keep Task', 'project': 'KEEP_TEST', 'status': 'active'}
        ]
        doc_ids = db.insert_many('tasks', test_docs)
        
        # Test 1: Delete one document
        success = db.delete_one('tasks', {'name': 'Delete Task 1'})
        if success:
            deleted_doc = db.find_one('tasks', {'name': 'Delete Task 1'})
            if not deleted_doc:
                print(f"   ✅ Delete one: Successfully deleted document")
            else:
                print(f"   ❌ Delete one: Document still exists")
                return False
        else:
            print(f"   ❌ Delete one: Delete operation failed")
            return False
        
        # Test 2: Delete many documents
        deleted_count = db.delete_many('tasks', {'project': 'DELETE_TEST', 'status': 'pending'})
        if deleted_count == 1:  # Only Delete Task 2 should match
            print(f"   ✅ Delete many: Deleted {deleted_count} documents")
        else:
            print(f"   ❌ Delete many: Expected 1, deleted {deleted_count}")
            return False
        
        # Test 3: Find and delete atomically
        deleted_doc = db.find_one_and_delete('tasks', {'name': 'Delete Task 3'})
        if deleted_doc and deleted_doc['name'] == 'Delete Task 3':
            # Verify it's actually deleted
            check_doc = db.find_one('tasks', {'name': 'Delete Task 3'})
            if not check_doc:
                print(f"   ✅ Find and delete: Atomic deletion successful")
            else:
                print(f"   ❌ Find and delete: Document not actually deleted")
                return False
        else:
            print(f"   ❌ Find and delete: Atomic operation failed")
            return False
        
        # Test 4: Verify non-matching documents are preserved
        keep_doc = db.find_one('tasks', {'name': 'Keep Task'})
        if keep_doc:
            print(f"   ✅ Selective delete: Non-matching documents preserved")
        else:
            print(f"   ❌ Selective delete: Non-matching document was deleted")
            return False
        
        # Clean up
        db.delete_many('tasks', {'project': 'KEEP_TEST'})
        
        return True
        
    except Exception as e:
        print(f"   ❌ DELETE operations failed: {e}")
        return False

def test_advanced_features():
    """Test advanced database features."""
    print("\n🔍 Testing ADVANCED Features...")
    print("=" * 50)
    
    try:
        from montu.shared.json_database import JSONDatabase
        
        db = JSONDatabase()
        
        # Test 1: Transaction-like operations
        def transaction_operations(db_instance):
            db_instance.insert_one('tasks', {'name': 'Transaction Test 1', 'project': 'TRANS_TEST'})
            db_instance.insert_one('tasks', {'name': 'Transaction Test 2', 'project': 'TRANS_TEST'})
            return "success"
        
        result = db.transaction(transaction_operations)
        if result == "success":
            trans_docs = db.find('tasks', {'project': 'TRANS_TEST'})
            if len(trans_docs) == 2:
                print(f"   ✅ Transaction: Successfully executed transaction")
            else:
                print(f"   ❌ Transaction: Transaction not executed properly")
                return False
        
        # Test 2: Aggregation operations
        # Insert test data for aggregation
        agg_docs = [
            {'project': 'AGG_TEST', 'status': 'active', 'priority': 1},
            {'project': 'AGG_TEST', 'status': 'active', 'priority': 2},
            {'project': 'AGG_TEST', 'status': 'completed', 'priority': 1},
            {'project': 'OTHER_AGG', 'status': 'active', 'priority': 1}
        ]
        db.insert_many('tasks', agg_docs)
        
        # Test aggregation pipeline
        pipeline = [
            {'$match': {'project': 'AGG_TEST'}},
            {'$group': {'_id': '$status', 'count': {'$sum': 1}, 'avg_priority': {'$avg': '$priority'}}}
        ]
        
        agg_results = db.aggregate('tasks', pipeline)
        if len(agg_results) == 2:  # Should have 2 groups: active and completed
            print(f"   ✅ Aggregation: Pipeline executed successfully")
        else:
            print(f"   ❌ Aggregation: Expected 2 groups, got {len(agg_results)}")
            return False
        
        # Test 3: Nested field operations
        nested_doc = {
            'name': 'Nested Test',
            'project': 'NESTED_TEST',
            'metadata': {
                'artist': {'name': 'John Doe', 'department': 'VFX'},
                'frame_range': {'start': 1001, 'end': 1100}
            }
        }
        nested_id = db.insert_one('tasks', nested_doc)
        
        # Query nested fields
        nested_results = db.find('tasks', {'metadata.artist.name': 'John Doe'})
        if len(nested_results) == 1:
            print(f"   ✅ Nested queries: Successfully queried nested fields")
        else:
            print(f"   ❌ Nested queries: Failed to query nested fields")
            return False
        
        # Clean up
        db.delete_many('tasks', {'project': {'$in': ['TRANS_TEST', 'AGG_TEST', 'OTHER_AGG', 'NESTED_TEST']}})
        
        return True
        
    except Exception as e:
        print(f"   ❌ ADVANCED features failed: {e}")
        return False

def test_performance_and_edge_cases():
    """Test performance and edge cases."""
    print("\n🔍 Testing PERFORMANCE & Edge Cases...")
    print("=" * 50)
    
    try:
        from montu.shared.json_database import JSONDatabase
        
        db = JSONDatabase()
        
        # Test 1: Large batch operations
        start_time = time.time()
        large_batch = [
            {'name': f'Perf Task {i}', 'project': 'PERF_TEST', 'index': i}
            for i in range(100)
        ]
        doc_ids = db.insert_many('tasks', large_batch)
        insert_time = time.time() - start_time
        
        if len(doc_ids) == 100:
            print(f"   ✅ Large batch insert: 100 documents in {insert_time:.3f}s")
        else:
            print(f"   ❌ Large batch insert: Expected 100, got {len(doc_ids)}")
            return False
        
        # Test 2: Complex query performance
        start_time = time.time()
        complex_results = db.find('tasks', {
            'project': 'PERF_TEST',
            'index': {'$gte': 50, '$lt': 75}
        })
        query_time = time.time() - start_time
        
        if len(complex_results) == 25:
            print(f"   ✅ Complex query: 25 results in {query_time:.3f}s")
        else:
            print(f"   ❌ Complex query: Expected 25, got {len(complex_results)}")
            return False
        
        # Test 3: Edge case - empty queries
        empty_results = db.find('tasks', {'nonexistent_field': 'nonexistent_value'})
        if len(empty_results) == 0:
            print(f"   ✅ Empty query: Correctly returned 0 results")
        else:
            print(f"   ❌ Empty query: Expected 0, got {len(empty_results)}")
            return False
        
        # Test 4: Edge case - invalid operations
        invalid_update = db.update_one('tasks', {'nonexistent_id': 'test'}, {'$set': {'field': 'value'}})
        if not invalid_update:
            print(f"   ✅ Invalid update: Correctly returned False")
        else:
            print(f"   ❌ Invalid update: Should have returned False")
            return False
        
        # Clean up
        db.delete_many('tasks', {'project': 'PERF_TEST'})
        
        return True
        
    except Exception as e:
        print(f"   ❌ PERFORMANCE & Edge cases failed: {e}")
        return False

def main():
    """Run comprehensive CRUD operations test suite."""
    print("🚀 DATABASE CRUD OPERATIONS TEST SUITE")
    print("=" * 60)
    print("Testing comprehensive Create, Read, Update, Delete operations")
    print("with advanced features, performance, and edge cases.\n")
    
    tests = [
        ("CREATE Operations", test_create_operations),
        ("READ Operations", test_read_operations),
        ("UPDATE Operations", test_update_operations),
        ("DELETE Operations", test_delete_operations),
        ("ADVANCED Features", test_advanced_features),
        ("PERFORMANCE & Edge Cases", test_performance_and_edge_cases),
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
    print("📊 CRUD OPERATIONS TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 SUCCESS: All CRUD operations working perfectly!")
        print("   ✅ CREATE: Insert operations with metadata")
        print("   ✅ READ: Find operations with complex queries")
        print("   ✅ UPDATE: Update operations with operators")
        print("   ✅ DELETE: Delete operations with atomicity")
        print("   ✅ ADVANCED: Transactions, aggregation, nested fields")
        print("   ✅ PERFORMANCE: Large batches and edge cases")
        return 0
    else:
        print(f"\n⚠️  WARNING: {total - passed} tests failed")
        print("   Some CRUD operations may have issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
