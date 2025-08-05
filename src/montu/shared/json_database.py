"""
JSON Mock Database System

A JSON-based mock database for testing GUI-to-database connections
and validating data flows before MongoDB implementation.
Enhanced with path generation and project configuration support.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from datetime import datetime
import uuid
from functools import reduce
from operator import itemgetter

from .path_builder import PathBuilder


class JSONDatabase:
    """JSON-based mock database for testing and development with path generation support."""

    def __init__(self, data_dir: Union[str, Path] = None):
        """
        Initialize JSON database.

        Args:
            data_dir: Directory to store JSON files (defaults to data/json_db)
        """
        if data_dir is None:
            # Default to data/json_db in project root
            project_root = Path(__file__).parent.parent.parent.parent
            data_dir = project_root / "data" / "json_db"

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Collection files
        self.collections = {
            'tasks': self.data_dir / 'tasks.json',
            'project_configs': self.data_dir / 'project_configs.json',
            'media_records': self.data_dir / 'media_records.json',
            'annotations': self.data_dir / 'annotations.json',
            'directory_operations': self.data_dir / 'directory_operations.json',
            'user_sessions': self.data_dir / 'user_sessions.json',
            'system_logs': self.data_dir / 'system_logs.json',
            'versions': self.data_dir / 'versions.json'
        }

        # Path builders cache (project_id -> PathBuilder)
        self._path_builders: Dict[str, PathBuilder] = {}

        # Initialize collections if they don't exist
        self._initialize_collections()
    
    def _initialize_collections(self):
        """Initialize empty collections if they don't exist."""
        for collection_name, file_path in self.collections.items():
            if not file_path.exists():
                self._write_collection(collection_name, [])
    
    def _read_collection(self, collection: str) -> List[Dict[str, Any]]:
        """Read a collection from JSON file."""
        if collection not in self.collections:
            raise ValueError(f"Unknown collection: {collection}")
        
        file_path = self.collections[collection]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _write_collection(self, collection: str, data: List[Dict[str, Any]]):
        """Write a collection to JSON file."""
        if collection not in self.collections:
            raise ValueError(f"Unknown collection: {collection}")
        
        file_path = self.collections[collection]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """
        Insert a single document into a collection.
        
        Args:
            collection: Collection name
            document: Document to insert
            
        Returns:
            Document ID
        """
        data = self._read_collection(collection)
        
        # Ensure document has an _id
        if '_id' not in document:
            document['_id'] = str(uuid.uuid4())
        
        # Add metadata
        document['_created_at'] = datetime.now().isoformat()
        document['_updated_at'] = datetime.now().isoformat()
        
        data.append(document)
        self._write_collection(collection, data)
        
        return document['_id']
    
    def insert_many(self, collection: str, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Insert multiple documents into a collection.
        
        Args:
            collection: Collection name
            documents: List of documents to insert
            
        Returns:
            List of document IDs
        """
        data = self._read_collection(collection)
        inserted_ids = []
        
        for document in documents:
            # Ensure document has an _id
            if '_id' not in document:
                document['_id'] = str(uuid.uuid4())
            
            # Add metadata
            document['_created_at'] = datetime.now().isoformat()
            document['_updated_at'] = datetime.now().isoformat()
            
            data.append(document)
            inserted_ids.append(document['_id'])
        
        self._write_collection(collection, data)
        return inserted_ids
    
    def find(self, collection: str, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Find documents in a collection.
        
        Args:
            collection: Collection name
            query: Query filter (None for all documents)
            
        Returns:
            List of matching documents
        """
        data = self._read_collection(collection)
        
        if query is None:
            return data
        
        # Simple query matching
        results = []
        for document in data:
            if self._matches_query(document, query):
                results.append(document)
        
        return results

    def find_with_options(self, collection: str, query: Optional[Dict[str, Any]] = None,
                         sort: Optional[List[Tuple[str, int]]] = None, limit: Optional[int] = None,
                         skip: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Find documents with advanced options for pagination and sorting.

        Args:
            collection: Collection name
            query: Query dictionary (optional)
            sort: List of (field, direction) tuples for sorting. Direction: 1=asc, -1=desc
            limit: Maximum number of documents to return
            skip: Number of documents to skip (for pagination)

        Returns:
            List of matching documents with applied options
        """
        # Get base results
        if query:
            results = self.find(collection, query)
        else:
            results = self._read_collection(collection)

        # Apply sorting
        if sort:
            for field, direction in reversed(sort):  # Apply in reverse order for stable sort
                reverse = (direction == -1)
                try:
                    results.sort(key=lambda x: self._get_sort_key(x, field), reverse=reverse)
                except (KeyError, TypeError):
                    # Handle missing fields or incomparable types
                    results.sort(key=lambda x: self._get_sort_key_safe(x, field), reverse=reverse)

        # Apply pagination
        if skip:
            results = results[skip:]
        if limit:
            results = results[:limit]

        return results

    def _get_sort_key(self, item: Dict[str, Any], field: str) -> Any:
        """Get sort key for a field, handling nested fields."""
        if '.' in field:
            # Handle nested fields like 'metadata.created_at'
            keys = field.split('.')
            value = item
            for key in keys:
                value = value[key]
            return value
        else:
            return item[field]

    def _get_sort_key_safe(self, item: Dict[str, Any], field: str) -> Any:
        """Get sort key safely, handling missing fields and type errors."""
        try:
            value = self._get_sort_key(item, field)
            # Convert to string if not comparable
            if value is None:
                return ""
            elif isinstance(value, (str, int, float)):
                return value
            else:
                return str(value)
        except (KeyError, TypeError):
            return ""  # Default value for missing/incomparable fields

    def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a single document in a collection.
        
        Args:
            collection: Collection name
            query: Query filter
            
        Returns:
            First matching document or None
        """
        results = self.find(collection, query)
        return results[0] if results else None
    
    def update_one(self, collection: str, query: Dict[str, Any], 
                   update: Dict[str, Any]) -> bool:
        """
        Update a single document in a collection.
        
        Args:
            collection: Collection name
            query: Query filter
            update: Update operations
            
        Returns:
            True if document was updated
        """
        data = self._read_collection(collection)
        
        for i, document in enumerate(data):
            if self._matches_query(document, query):
                # Apply update with full operator support
                if '$set' in update:
                    document.update(update['$set'])
                elif '$unset' in update:
                    for field in update['$unset']:
                        document.pop(field, None)
                elif '$inc' in update:
                    for field, increment in update['$inc'].items():
                        current_value = self._get_nested_field(document, field) or 0
                        self._set_nested_field(document, field, current_value + increment)
                elif '$push' in update:
                    for field, value in update['$push'].items():
                        current_list = self._get_nested_field(document, field) or []
                        if isinstance(current_list, list):
                            current_list.append(value)
                            self._set_nested_field(document, field, current_list)
                elif '$pull' in update:
                    for field, value in update['$pull'].items():
                        current_list = self._get_nested_field(document, field) or []
                        if isinstance(current_list, list) and value in current_list:
                            current_list.remove(value)
                            self._set_nested_field(document, field, current_list)
                else:
                    # Direct update (no operators)
                    document.update(update)

                document['_updated_at'] = datetime.now().isoformat()
                data[i] = document

                self._write_collection(collection, data)
                return True
        
        return False
    
    def delete_one(self, collection: str, query: Dict[str, Any]) -> bool:
        """
        Delete a single document from a collection.
        
        Args:
            collection: Collection name
            query: Query filter
            
        Returns:
            True if document was deleted
        """
        data = self._read_collection(collection)
        
        for i, document in enumerate(data):
            if self._matches_query(document, query):
                del data[i]
                self._write_collection(collection, data)
                return True
        
        return False
    
    def delete_many(self, collection: str, query: Dict[str, Any]) -> int:
        """
        Delete multiple documents from a collection.
        
        Args:
            collection: Collection name
            query: Query filter
            
        Returns:
            Number of documents deleted
        """
        data = self._read_collection(collection)
        original_count = len(data)
        
        # Filter out matching documents
        data = [doc for doc in data if not self._matches_query(doc, query)]
        
        self._write_collection(collection, data)
        return original_count - len(data)
    
    def count(self, collection: str, query: Optional[Dict[str, Any]] = None) -> int:
        """
        Count documents in a collection.
        
        Args:
            collection: Collection name
            query: Query filter (None for all documents)
            
        Returns:
            Number of matching documents
        """
        return len(self.find(collection, query))
    
    def drop_collection(self, collection: str):
        """Drop (clear) a collection."""
        self._write_collection(collection, [])

    # Advanced CRUD Operations

    def find_with_options(self, collection: str, query: Optional[Dict[str, Any]] = None,
                         sort: Optional[List[tuple]] = None, limit: Optional[int] = None,
                         skip: Optional[int] = None, projection: Optional[Dict[str, int]] = None) -> List[Dict[str, Any]]:
        """
        Find documents with advanced options (sorting, pagination, projection).

        Args:
            collection: Collection name
            query: Query filter
            sort: List of (field, direction) tuples. Direction: 1 for ascending, -1 for descending
            limit: Maximum number of documents to return
            skip: Number of documents to skip
            projection: Fields to include/exclude {field: 1} to include, {field: 0} to exclude

        Returns:
            List of matching documents
        """
        # Get filtered results
        results = self.find(collection, query)

        # Apply sorting
        if sort:
            for field, direction in reversed(sort):  # Apply sorts in reverse order
                reverse = direction == -1
                try:
                    results.sort(key=lambda doc: self._get_nested_field(doc, field) or '', reverse=reverse)
                except (TypeError, KeyError):
                    # Handle cases where field doesn't exist or isn't comparable
                    results.sort(key=lambda doc: str(self._get_nested_field(doc, field) or ''), reverse=reverse)

        # Apply pagination
        if skip:
            results = results[skip:]
        if limit:
            results = results[:limit]

        # Apply projection
        if projection:
            results = [self._apply_projection(doc, projection) for doc in results]

        return results

    def _apply_projection(self, document: Dict[str, Any], projection: Dict[str, int]) -> Dict[str, Any]:
        """Apply field projection to a document."""
        if not projection:
            return document

        # Check if it's inclusion or exclusion projection
        include_fields = any(v == 1 for v in projection.values())

        if include_fields:
            # Inclusion projection - only include specified fields
            result = {}
            for field, include in projection.items():
                if include == 1:
                    value = self._get_nested_field(document, field)
                    if value is not None:
                        self._set_nested_field(result, field, value)
            # Always include _id unless explicitly excluded
            if '_id' not in projection or projection.get('_id') != 0:
                result['_id'] = document.get('_id')
            return result
        else:
            # Exclusion projection - exclude specified fields
            result = document.copy()
            for field, exclude in projection.items():
                if exclude == 0:
                    self._unset_nested_field(result, field)
            return result

    def _set_nested_field(self, document: Dict[str, Any], field: str, value: Any):
        """Set nested field value using dot notation."""
        if '.' not in field:
            document[field] = value
            return

        keys = field.split('.')
        current = document
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    def _unset_nested_field(self, document: Dict[str, Any], field: str):
        """Remove nested field using dot notation."""
        if '.' not in field:
            document.pop(field, None)
            return

        keys = field.split('.')
        current = document
        for key in keys[:-1]:
            if key not in current:
                return
            current = current[key]
        current.pop(keys[-1], None)
    
    def _matches_query(self, document: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """
        Check if a document matches a query with advanced operators support.

        Supports MongoDB-style operators:
        - $eq: equality (default)
        - $ne: not equal
        - $gt, $gte, $lt, $lte: comparison operators
        - $in, $nin: array membership
        - $regex: regular expression matching
        - $exists: field existence check
        - $and, $or: logical operators
        """
        for key, value in query.items():
            # Handle logical operators
            if key == '$and':
                return all(self._matches_query(document, sub_query) for sub_query in value)
            elif key == '$or':
                return any(self._matches_query(document, sub_query) for sub_query in value)

            # Handle field queries
            if not self._matches_field_query(document, key, value):
                return False

        return True

    def _matches_field_query(self, document: Dict[str, Any], field: str, query_value: Any) -> bool:
        """Check if a document field matches a query value with operator support."""
        # Handle nested field access (e.g., "user.name")
        field_value = self._get_nested_field(document, field)

        # If query_value is a dict, it contains operators
        if isinstance(query_value, dict):
            for operator, op_value in query_value.items():
                if not self._apply_operator(field_value, operator, op_value):
                    return False
            return True
        else:
            # Simple equality check
            return field_value == query_value

    def _get_nested_field(self, document: Dict[str, Any], field: str) -> Any:
        """Get nested field value using dot notation."""
        if '.' not in field:
            return document.get(field)

        keys = field.split('.')
        value = document
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value

    def _apply_operator(self, field_value: Any, operator: str, op_value: Any) -> bool:
        """Apply a query operator to a field value."""
        if operator == '$eq':
            return field_value == op_value
        elif operator == '$ne':
            return field_value != op_value
        elif operator == '$gt':
            return field_value is not None and field_value > op_value
        elif operator == '$gte':
            return field_value is not None and field_value >= op_value
        elif operator == '$lt':
            return field_value is not None and field_value < op_value
        elif operator == '$lte':
            return field_value is not None and field_value <= op_value
        elif operator == '$in':
            return field_value in op_value if isinstance(op_value, (list, tuple)) else False
        elif operator == '$nin':
            return field_value not in op_value if isinstance(op_value, (list, tuple)) else True
        elif operator == '$regex':
            if field_value is None:
                return False
            pattern = op_value if isinstance(op_value, str) else op_value.get('$regex', '')
            flags = 0
            if isinstance(op_value, dict) and '$options' in op_value:
                if 'i' in op_value['$options']:
                    flags |= re.IGNORECASE
            return bool(re.search(pattern, str(field_value), flags))
        elif operator == '$exists':
            return (field_value is not None) == op_value
        else:
            # Unknown operator, default to equality
            return field_value == op_value
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        stats = {
            'collections': {},
            'total_documents': 0,
            'data_directory': str(self.data_dir)
        }
        
        for collection_name in self.collections:
            count = self.count(collection_name)
            stats['collections'][collection_name] = count
            stats['total_documents'] += count
        
        return stats
    
    def export_collection(self, collection: str, file_path: Union[str, Path]):
        """Export a collection to a JSON file."""
        data = self._read_collection(collection)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    def import_collection(self, collection: str, file_path: Union[str, Path],
                         replace: bool = False):
        """
        Import data into a collection from a JSON file.

        Args:
            collection: Collection name
            file_path: Path to JSON file
            replace: If True, replace existing data; if False, append
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            import_data = json.load(f)

        if not isinstance(import_data, list):
            raise ValueError("Import data must be a list of documents")

        if replace:
            self._write_collection(collection, import_data)
        else:
            existing_data = self._read_collection(collection)
            existing_data.extend(import_data)
            self._write_collection(collection, existing_data)

    # Enhanced methods for path generation support

    def get_path_builder(self, project_id: str) -> Optional[PathBuilder]:
        """
        Get PathBuilder instance for a project.

        Args:
            project_id: Project identifier

        Returns:
            PathBuilder instance or None if project not found
        """
        if project_id in self._path_builders:
            return self._path_builders[project_id]

        # Load project config and create PathBuilder
        project_config = self.find_one('project_configs', {'_id': project_id})
        if project_config:
            path_builder = PathBuilder(project_config)
            self._path_builders[project_id] = path_builder
            return path_builder

        return None

    def clear_path_builder_cache(self, project_id: str = None):
        """
        Clear PathBuilder cache to force reload of project configuration.

        Args:
            project_id: Specific project to clear, or None to clear all
        """
        if project_id:
            self._path_builders.pop(project_id, None)
        else:
            self._path_builders.clear()

    def reload_project_config(self, project_id: str):
        """
        Reload project configuration and clear associated cache.

        Args:
            project_id: Project identifier to reload
        """
        # Clear the cached PathBuilder
        self.clear_path_builder_cache(project_id)

        # Force reload by getting PathBuilder again
        return self.get_path_builder(project_id)

    def generate_task_paths(self, task_id: str, version: str = "001",
                           file_type: str = "maya_scene") -> Optional[Dict[str, str]]:
        """
        Generate all paths for a task.

        Args:
            task_id: Task identifier
            version: Version string
            file_type: File type for filename pattern

        Returns:
            Dictionary with all generated paths or None if task/project not found
        """
        # Get task data
        task = self.find_one('tasks', {'_id': task_id})
        if not task:
            return None

        # Get path builder for project
        path_builder = self.get_path_builder(task['project'])
        if not path_builder:
            return None

        # Generate paths
        result = path_builder.generate_all_paths(task, version, file_type)

        return {
            'working_file_path': result.working_file_path,
            'render_output_path': result.render_output_path,
            'media_file_path': result.media_file_path,
            'cache_file_path': result.cache_file_path,
            'submission_path': result.submission_path,
            'filename': result.filename,
            'version_formatted': result.version_formatted,
            'sequence_clean': result.sequence_clean,
            'shot_clean': result.shot_clean,
            'episode_clean': result.episode_clean
        }

    def update_task_with_paths(self, task_id: str, version: str = "001",
                              file_type: str = "maya_scene") -> bool:
        """
        Update a task with generated path information.

        Args:
            task_id: Task identifier
            version: Version string
            file_type: File type for filename pattern

        Returns:
            True if task was updated successfully
        """
        # Generate paths
        paths = self.generate_task_paths(task_id, version, file_type)
        if not paths:
            return False

        # Update task with path information
        update_data = {
            'current_version': f"v{paths['version_formatted']}",
            'working_file_path': paths['working_file_path'],
            'render_output_path': paths['render_output_path'],
            'media_file_path': paths['media_file_path'],
            'cache_file_path': paths['cache_file_path'],
            'filename': paths['filename'],
            'sequence_clean': paths['sequence_clean'],
            'shot_clean': paths['shot_clean'],
            'episode_clean': paths['episode_clean']
        }

        return self.update_one('tasks', {'_id': task_id}, {'$set': update_data})

    # Bulk Operations

    def bulk_write(self, collection: str, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute multiple write operations in bulk.

        Args:
            collection: Collection name
            operations: List of operation dictionaries
                       Each operation should have 'operation' key with value:
                       'insert', 'update', 'delete', 'replace'

        Returns:
            Dictionary with operation results
        """
        results = {
            'inserted_count': 0,
            'updated_count': 0,
            'deleted_count': 0,
            'errors': []
        }

        for i, op in enumerate(operations):
            try:
                op_type = op.get('operation')

                if op_type == 'insert':
                    doc_id = self.insert_one(collection, op['document'])
                    results['inserted_count'] += 1

                elif op_type == 'update':
                    success = self.update_one(collection, op['filter'], op['update'])
                    if success:
                        results['updated_count'] += 1

                elif op_type == 'delete':
                    success = self.delete_one(collection, op['filter'])
                    if success:
                        results['deleted_count'] += 1

                elif op_type == 'replace':
                    # Replace entire document
                    success = self.replace_one(collection, op['filter'], op['replacement'])
                    if success:
                        results['updated_count'] += 1

            except Exception as e:
                results['errors'].append({
                    'operation_index': i,
                    'error': str(e)
                })

        return results

    def update_many(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """
        Update multiple documents in a collection.

        Args:
            collection: Collection name
            query: Query filter
            update: Update operations

        Returns:
            Number of documents updated
        """
        data = self._read_collection(collection)
        updated_count = 0

        for i, document in enumerate(data):
            if self._matches_query(document, query):
                # Apply update
                if '$set' in update:
                    document.update(update['$set'])
                elif '$unset' in update:
                    for field in update['$unset']:
                        document.pop(field, None)
                elif '$inc' in update:
                    for field, increment in update['$inc'].items():
                        current_value = self._get_nested_field(document, field) or 0
                        self._set_nested_field(document, field, current_value + increment)
                elif '$push' in update:
                    for field, value in update['$push'].items():
                        current_list = self._get_nested_field(document, field) or []
                        if isinstance(current_list, list):
                            current_list.append(value)
                            self._set_nested_field(document, field, current_list)
                elif '$pull' in update:
                    for field, value in update['$pull'].items():
                        current_list = self._get_nested_field(document, field) or []
                        if isinstance(current_list, list):
                            current_list = [item for item in current_list if item != value]
                            self._set_nested_field(document, field, current_list)
                else:
                    document.update(update)

                document['_updated_at'] = datetime.now().isoformat()
                data[i] = document
                updated_count += 1

        if updated_count > 0:
            self._write_collection(collection, data)

        return updated_count

    def replace_one(self, collection: str, query: Dict[str, Any], replacement: Dict[str, Any]) -> bool:
        """
        Replace a single document in a collection.

        Args:
            collection: Collection name
            query: Query filter
            replacement: Replacement document

        Returns:
            True if document was replaced
        """
        data = self._read_collection(collection)

        for i, document in enumerate(data):
            if self._matches_query(document, query):
                # Preserve _id and metadata
                replacement['_id'] = document.get('_id')
                replacement['_created_at'] = document.get('_created_at')
                replacement['_updated_at'] = datetime.now().isoformat()

                data[i] = replacement
                self._write_collection(collection, data)
                return True

        return False

    def upsert(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> str:
        """
        Update document if exists, insert if not (upsert operation).

        Args:
            collection: Collection name
            query: Query filter
            update: Update operations or document to insert

        Returns:
            Document ID (existing or newly created)
        """
        # Try to update first
        if self.update_one(collection, query, update):
            # Document was updated, find and return its ID
            doc = self.find_one(collection, query)
            return doc['_id'] if doc else None
        else:
            # Document doesn't exist, insert new one
            if '$set' in update:
                new_doc = query.copy()
                new_doc.update(update['$set'])
            else:
                new_doc = query.copy()
                new_doc.update(update)

            return self.insert_one(collection, new_doc)

    # Aggregation Operations

    def aggregate(self, collection: str, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Perform aggregation operations on a collection.

        Supports basic aggregation stages:
        - $match: Filter documents
        - $sort: Sort documents
        - $limit: Limit number of documents
        - $skip: Skip documents
        - $project: Select/transform fields
        - $group: Group documents and perform calculations
        - $count: Count documents

        Args:
            collection: Collection name
            pipeline: List of aggregation stages

        Returns:
            List of aggregated results
        """
        # Start with all documents
        results = self._read_collection(collection)

        for stage in pipeline:
            stage_name = list(stage.keys())[0]
            stage_params = stage[stage_name]

            if stage_name == '$match':
                results = [doc for doc in results if self._matches_query(doc, stage_params)]

            elif stage_name == '$sort':
                sort_fields = [(field, direction) for field, direction in stage_params.items()]
                for field, direction in reversed(sort_fields):
                    reverse = direction == -1
                    try:
                        results.sort(key=lambda doc: self._get_nested_field(doc, field) or '', reverse=reverse)
                    except (TypeError, KeyError):
                        results.sort(key=lambda doc: str(self._get_nested_field(doc, field) or ''), reverse=reverse)

            elif stage_name == '$limit':
                results = results[:stage_params]

            elif stage_name == '$skip':
                results = results[stage_params:]

            elif stage_name == '$project':
                results = [self._apply_projection(doc, stage_params) for doc in results]

            elif stage_name == '$group':
                results = self._perform_grouping(results, stage_params)

            elif stage_name == '$count':
                return [{'count': len(results)}]

        return results

    def _perform_grouping(self, documents: List[Dict[str, Any]], group_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform grouping operation on documents."""
        groups = {}
        group_id_spec = group_spec.get('_id')

        # Group documents
        for doc in documents:
            if group_id_spec is None:
                group_key = None
            elif isinstance(group_id_spec, str):
                group_key = self._get_nested_field(doc, group_id_spec.lstrip('$'))
            elif isinstance(group_id_spec, dict):
                group_key = {}
                for key, field_spec in group_id_spec.items():
                    if isinstance(field_spec, str) and field_spec.startswith('$'):
                        group_key[key] = self._get_nested_field(doc, field_spec.lstrip('$'))
                    else:
                        group_key[key] = field_spec
                group_key = str(group_key)  # Convert to string for dict key
            else:
                group_key = str(group_id_spec)

            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(doc)

        # Calculate aggregations for each group
        results = []
        for group_key, group_docs in groups.items():
            result = {'_id': group_key}

            for field, operation in group_spec.items():
                if field == '_id':
                    continue

                if isinstance(operation, dict):
                    op_name = list(operation.keys())[0]
                    op_field = operation[op_name]

                    if op_name == '$sum':
                        if op_field == 1:
                            result[field] = len(group_docs)
                        else:
                            field_name = op_field.lstrip('$')
                            result[field] = sum(self._get_nested_field(doc, field_name) or 0 for doc in group_docs)

                    elif op_name == '$avg':
                        field_name = op_field.lstrip('$')
                        values = [self._get_nested_field(doc, field_name) for doc in group_docs if self._get_nested_field(doc, field_name) is not None]
                        result[field] = sum(values) / len(values) if values else 0

                    elif op_name == '$min':
                        field_name = op_field.lstrip('$')
                        values = [self._get_nested_field(doc, field_name) for doc in group_docs if self._get_nested_field(doc, field_name) is not None]
                        result[field] = min(values) if values else None

                    elif op_name == '$max':
                        field_name = op_field.lstrip('$')
                        values = [self._get_nested_field(doc, field_name) for doc in group_docs if self._get_nested_field(doc, field_name) is not None]
                        result[field] = max(values) if values else None

                    elif op_name == '$first':
                        field_name = op_field.lstrip('$')
                        result[field] = self._get_nested_field(group_docs[0], field_name) if group_docs else None

                    elif op_name == '$last':
                        field_name = op_field.lstrip('$')
                        result[field] = self._get_nested_field(group_docs[-1], field_name) if group_docs else None

            results.append(result)

        return results

    # Transaction-like Operations

    def transaction(self, operations: Callable[['JSONDatabase'], Any]) -> Any:
        """
        Execute operations in a transaction-like manner with rollback support.

        Args:
            operations: Function that takes database instance and performs operations

        Returns:
            Result of operations function

        Raises:
            Exception: If operations fail, database state is rolled back
        """
        # Create backup of all collections
        backup = {}
        for collection_name in self.collections:
            backup[collection_name] = self._read_collection(collection_name).copy()

        try:
            # Execute operations
            result = operations(self)
            return result
        except Exception as e:
            # Rollback on error
            for collection_name, data in backup.items():
                self._write_collection(collection_name, data)
            raise e

    # Indexing Support (Simulated)

    def create_index(self, collection: str, keys: Union[str, List[tuple]], **kwargs) -> str:
        """
        Create an index on a collection (simulated for compatibility).

        Args:
            collection: Collection name
            keys: Field name or list of (field, direction) tuples
            **kwargs: Additional index options (ignored in JSON implementation)

        Returns:
            Index name
        """
        # In JSON implementation, this is just for compatibility
        # Real indexing would be implemented in MongoDB version
        if isinstance(keys, str):
            index_name = f"{collection}_{keys}_1"
        else:
            index_name = f"{collection}_{'_'.join([f'{field}_{direction}' for field, direction in keys])}"

        # Store index metadata (for compatibility)
        if not hasattr(self, '_indexes'):
            self._indexes = {}
        if collection not in self._indexes:
            self._indexes[collection] = []

        self._indexes[collection].append({
            'name': index_name,
            'keys': keys,
            'options': kwargs
        })

        return index_name

    def list_indexes(self, collection: str) -> List[Dict[str, Any]]:
        """List all indexes for a collection."""
        if not hasattr(self, '_indexes'):
            return []
        return self._indexes.get(collection, [])

    def drop_index(self, collection: str, index_name: str) -> bool:
        """Drop an index from a collection."""
        if not hasattr(self, '_indexes') or collection not in self._indexes:
            return False

        original_count = len(self._indexes[collection])
        self._indexes[collection] = [idx for idx in self._indexes[collection] if idx['name'] != index_name]

        return len(self._indexes[collection]) < original_count

    # Advanced Query Operations

    def distinct(self, collection: str, field: str, query: Optional[Dict[str, Any]] = None) -> List[Any]:
        """
        Get distinct values for a field in a collection.

        Args:
            collection: Collection name
            field: Field name
            query: Optional query filter

        Returns:
            List of distinct values
        """
        documents = self.find(collection, query)
        values = set()

        for doc in documents:
            value = self._get_nested_field(doc, field)
            if value is not None:
                # Handle lists by adding each element
                if isinstance(value, list):
                    values.update(value)
                else:
                    values.add(value)

        return list(values)

    def find_one_and_update(self, collection: str, query: Dict[str, Any],
                           update: Dict[str, Any], return_document: str = 'before') -> Optional[Dict[str, Any]]:
        """
        Find a document and update it atomically.

        Args:
            collection: Collection name
            query: Query filter
            update: Update operations
            return_document: 'before' or 'after' - which version to return

        Returns:
            Document before or after update, or None if not found
        """
        data = self._read_collection(collection)

        for i, document in enumerate(data):
            if self._matches_query(document, query):
                # Store original document
                original_doc = document.copy()

                # Apply update
                if '$set' in update:
                    document.update(update['$set'])
                else:
                    document.update(update)

                document['_updated_at'] = datetime.now().isoformat()
                data[i] = document

                self._write_collection(collection, data)

                return document if return_document == 'after' else original_doc

        return None

    def find_one_and_delete(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a document and delete it atomically.

        Args:
            collection: Collection name
            query: Query filter

        Returns:
            Deleted document or None if not found
        """
        data = self._read_collection(collection)

        for i, document in enumerate(data):
            if self._matches_query(document, query):
                deleted_doc = document.copy()
                del data[i]
                self._write_collection(collection, data)
                return deleted_doc

        return None

    # Data Validation and Utility Methods

    def validate_document(self, collection: str, document: Dict[str, Any],
                         schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate a document against a schema.

        Args:
            collection: Collection name
            document: Document to validate
            schema: Validation schema (optional)

        Returns:
            Validation result with 'valid' boolean and 'errors' list
        """
        errors = []

        # Basic validation
        if not isinstance(document, dict):
            errors.append("Document must be a dictionary")
            return {'valid': False, 'errors': errors}

        # Schema validation if provided
        if schema:
            required_fields = schema.get('required', [])
            for field in required_fields:
                if field not in document:
                    errors.append(f"Required field '{field}' is missing")

            properties = schema.get('properties', {})
            for field, field_schema in properties.items():
                if field in document:
                    field_errors = self._validate_field(document[field], field_schema, field)
                    errors.extend(field_errors)

        return {'valid': len(errors) == 0, 'errors': errors}

    def _validate_field(self, value: Any, field_schema: Dict[str, Any], field_name: str) -> List[str]:
        """Validate a single field against its schema."""
        errors = []

        # Type validation
        expected_type = field_schema.get('type')
        if expected_type:
            type_map = {
                'string': str,
                'number': (int, float),
                'integer': int,
                'boolean': bool,
                'array': list,
                'object': dict
            }

            expected_python_type = type_map.get(expected_type)
            if expected_python_type and not isinstance(value, expected_python_type):
                errors.append(f"Field '{field_name}' should be of type {expected_type}")

        # Enum validation
        enum_values = field_schema.get('enum')
        if enum_values and value not in enum_values:
            errors.append(f"Field '{field_name}' must be one of {enum_values}")

        # String validations
        if isinstance(value, str):
            min_length = field_schema.get('minLength')
            if min_length and len(value) < min_length:
                errors.append(f"Field '{field_name}' must be at least {min_length} characters long")

            max_length = field_schema.get('maxLength')
            if max_length and len(value) > max_length:
                errors.append(f"Field '{field_name}' must be at most {max_length} characters long")

            pattern = field_schema.get('pattern')
            if pattern and not re.match(pattern, value):
                errors.append(f"Field '{field_name}' does not match required pattern")

        # Number validations
        if isinstance(value, (int, float)):
            minimum = field_schema.get('minimum')
            if minimum is not None and value < minimum:
                errors.append(f"Field '{field_name}' must be at least {minimum}")

            maximum = field_schema.get('maximum')
            if maximum is not None and value > maximum:
                errors.append(f"Field '{field_name}' must be at most {maximum}")

        return errors

    def backup_database(self, backup_path: Union[str, Path]) -> bool:
        """
        Create a backup of the entire database.

        Args:
            backup_path: Path to backup directory

        Returns:
            True if backup was successful
        """
        try:
            backup_dir = Path(backup_path)
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Add timestamp to backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            timestamped_backup_dir = backup_dir / f"backup_{timestamp}"
            timestamped_backup_dir.mkdir(exist_ok=True)

            # Copy all collection files
            for collection_name, file_path in self.collections.items():
                if file_path.exists():
                    backup_file = timestamped_backup_dir / f"{collection_name}.json"
                    data = self._read_collection(collection_name)
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

            # Create backup metadata
            metadata = {
                'backup_timestamp': datetime.now().isoformat(),
                'collections': list(self.collections.keys()),
                'total_documents': sum(self.count(col) for col in self.collections.keys())
            }

            metadata_file = timestamped_backup_dir / "backup_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)

            return True

        except Exception as e:
            print(f"Backup failed: {e}")
            return False

    def restore_database(self, backup_path: Union[str, Path]) -> bool:
        """
        Restore database from a backup.

        Args:
            backup_path: Path to backup directory

        Returns:
            True if restore was successful
        """
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                return False

            # Read backup metadata
            metadata_file = backup_dir / "backup_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                collections_to_restore = metadata.get('collections', [])
            else:
                # Fallback: restore all JSON files found
                collections_to_restore = [f.stem for f in backup_dir.glob("*.json") if f.stem != "backup_metadata"]

            # Restore each collection
            for collection_name in collections_to_restore:
                backup_file = backup_dir / f"{collection_name}.json"
                if backup_file.exists():
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self._write_collection(collection_name, data)

            return True

        except Exception as e:
            print(f"Restore failed: {e}")
            return False

    def get_collection_info(self, collection: str) -> Dict[str, Any]:
        """
        Get detailed information about a collection.

        Args:
            collection: Collection name

        Returns:
            Dictionary with collection information
        """
        if collection not in self.collections:
            return {'exists': False}

        data = self._read_collection(collection)

        # Calculate statistics
        doc_count = len(data)
        if doc_count == 0:
            return {
                'exists': True,
                'count': 0,
                'size_bytes': 0,
                'fields': [],
                'sample_document': None
            }

        # Analyze fields
        all_fields = set()
        for doc in data:
            all_fields.update(self._get_all_field_paths(doc))

        # Calculate file size
        file_path = self.collections[collection]
        size_bytes = file_path.stat().st_size if file_path.exists() else 0

        return {
            'exists': True,
            'count': doc_count,
            'size_bytes': size_bytes,
            'fields': sorted(list(all_fields)),
            'sample_document': data[0] if data else None,
            'indexes': self.list_indexes(collection) if hasattr(self, '_indexes') else []
        }

    def _get_all_field_paths(self, document: Dict[str, Any], prefix: str = '') -> List[str]:
        """Get all field paths in a document (including nested fields)."""
        paths = []

        for key, value in document.items():
            field_path = f"{prefix}.{key}" if prefix else key
            paths.append(field_path)

            if isinstance(value, dict):
                paths.extend(self._get_all_field_paths(value, field_path))

        return paths

    def get_project_config(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project configuration by ID."""
        return self.find_one('project_configs', {'_id': project_id})

    def validate_project_config(self, project_id: str) -> Dict[str, Any]:
        """
        Validate project configuration and return validation results.

        Args:
            project_id: Project identifier

        Returns:
            Dictionary with validation results
        """
        config = self.get_project_config(project_id)
        if not config:
            return {'valid': False, 'errors': ['Project configuration not found']}

        errors = []
        warnings = []

        # Check required sections
        required_sections = [
            'drive_mapping', 'path_segments', 'templates',
            'filename_patterns', 'name_cleaning_rules'
        ]

        for section in required_sections:
            if section not in config:
                errors.append(f"Missing required section: {section}")

        # Check required templates
        required_templates = ['working_file', 'render_output']
        templates = config.get('templates', {})

        for template in required_templates:
            if template not in templates:
                errors.append(f"Missing required template: {template}")

        # Try to create PathBuilder to validate configuration
        if not errors:
            try:
                PathBuilder(config)
            except Exception as e:
                errors.append(f"PathBuilder validation failed: {str(e)}")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'config': config
        }
