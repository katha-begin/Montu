"""
JSON Mock Database System

A JSON-based mock database for testing GUI-to-database connections
and validating data flows before MongoDB implementation.
Enhanced with path generation and project configuration support.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid

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
            'media_records': self.data_dir / 'media_records.json'
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
                # Apply update
                if '$set' in update:
                    document.update(update['$set'])
                else:
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
    
    def _matches_query(self, document: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """Check if a document matches a query."""
        for key, value in query.items():
            if key not in document:
                return False
            
            # Simple equality check
            if document[key] != value:
                return False
        
        return True
    
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
