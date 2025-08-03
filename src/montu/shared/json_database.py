"""
JSON Mock Database System

A JSON-based mock database for testing GUI-to-database connections
and validating data flows before MongoDB implementation.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid


class JSONDatabase:
    """JSON-based mock database for testing and development."""
    
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
