"""
Review Model

Data model for the Review Application providing media management,
annotation handling, and approval workflow operations.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from montu.shared.json_database import JSONDatabase


class ReviewModel:
    """
    Review model for managing media files, annotations, and approval workflows.
    
    Provides data access and business logic for the Review Application.
    """
    
    def __init__(self):
        """Initialize review model."""
        self.db = JSONDatabase()
        self.current_project_id: Optional[str] = None
    
    def get_available_projects(self) -> List[Dict[str, Any]]:
        """Get list of available projects."""
        try:
            projects = self.db.find('project_configs', {})
            return projects
        except Exception as e:
            print(f"Error loading projects: {e}")
            return []
    
    def set_current_project(self, project_id: str):
        """Set the current project."""
        self.current_project_id = project_id
    
    def get_media_for_project(self, project_id: str) -> List[Dict[str, Any]]:
        """Get media files for a specific project from media_records database."""
        try:
            # Get all media records from database
            all_media_records = self.db.find('media_records', {})

            # Get tasks for the project to filter media records
            tasks = self.db.find('tasks', {'project': project_id})
            task_ids = {task.get('_id', '') for task in tasks}

            # Filter media records by project tasks
            project_media_records = [
                record for record in all_media_records
                if record.get('linked_task_id', '') in task_ids
            ]

            # Transform media records to expected format
            media_items = []
            for record in project_media_records:
                media_item = self.transform_media_record_to_item(record)
                if media_item:
                    media_items.append(media_item)

            print(f"Found {len(media_items)} media records for project {project_id}")
            return media_items

        except Exception as e:
            print(f"Error loading media for project {project_id}: {e}")
            return []
    
    def transform_media_record_to_item(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Transform a media record from database to media item format."""
        try:
            # Extract basic information
            task_id = record.get('linked_task_id', '')
            file_name = record.get('file_name', '')
            media_type = record.get('media_type', 'unknown')
            file_extension = record.get('file_extension', '')

            # Get metadata
            metadata = record.get('metadata', {})
            file_size = metadata.get('file_size', 0)
            width = metadata.get('width')
            height = metadata.get('height')
            duration = metadata.get('duration')

            # Determine file type for UI
            if media_type == 'video':
                file_type = 'video'
                total_frames = int(duration * 24.0) if duration else 100  # Assume 24fps
                frame_rate = 24.0
            else:
                file_type = 'image'
                total_frames = 1
                frame_rate = None
            
            media_item = {
                'task_id': task_id,
                'file_path': main_media_file,
                'file_type': self.get_file_type(main_media_file),
                'version': 'v001',  # Default version
                'status': task.get('status', 'pending'),
                'total_frames': 100,  # Default frame count
                'frame_rate': 24.0,
                'created_date': datetime.now().isoformat(),
                'file_size': self.get_file_size(main_media_file),
                'task_info': {
                    'shot': task.get('shot', 'Unknown'),
                    'task': task.get('task', 'Unknown'),
                    'artist': task.get('artist', 'Unknown'),
                    'priority': task.get('priority', 'medium')
                }
            }
            
            # Get task information for display
            task_info = self.get_task_info_for_media(task_id)

            # Create media item in expected format
            media_item = {
                'task_id': task_id,
                'file_path': record.get('storage_url', ''),  # Use storage URL as file path
                'file_type': file_type,
                'version': record.get('linked_version', 'v001'),
                'status': record.get('approval_status', 'pending'),
                'total_frames': total_frames,
                'frame_rate': frame_rate,
                'created_date': record.get('upload_time', datetime.now().isoformat()),
                'file_size': file_size,
                'file_name': file_name,
                'media_type': media_type,
                'file_extension': file_extension,
                'author': record.get('author', 'Unknown'),
                'approval_status': record.get('approval_status', 'pending'),
                'reviewer': record.get('reviewer', ''),
                'review_notes': record.get('review_notes', ''),
                'review_date': record.get('review_date', ''),
                'description': record.get('description', ''),
                'tags': record.get('tags', []),
                'dimensions': f"{width}x{height}" if width and height else None,
                'task_info': task_info,
                'metadata': metadata,
                'record_id': record.get('_id', ''),
                'storage_key': record.get('storage_key', ''),
                'thumbnail_key': record.get('thumbnail_key', '')
            }

            return media_item

        except Exception as e:
            print(f"Error transforming media record to item: {e}")
            return None

    def get_task_info_for_media(self, task_id: str) -> Dict[str, Any]:
        """Get task information for media display."""
        try:
            task = self.db.find_one('tasks', {'_id': task_id})
            if task:
                return {
                    'shot': task.get('shot', 'Unknown'),
                    'task': task.get('task', 'Unknown'),
                    'artist': task.get('artist', 'Unknown'),
                    'priority': task.get('priority', 'medium'),
                    'episode': task.get('episode', 'Unknown'),
                    'sequence': task.get('sequence', 'Unknown'),
                    'status': task.get('status', 'unknown')
                }
            else:
                return {
                    'shot': 'Unknown',
                    'task': 'Unknown',
                    'artist': 'Unknown',
                    'priority': 'medium',
                    'episode': 'Unknown',
                    'sequence': 'Unknown',
                    'status': 'unknown'
                }
        except Exception as e:
            print(f"Error getting task info for {task_id}: {e}")
            return {
                'shot': 'Unknown',
                'task': 'Unknown',
                'artist': 'Unknown',
                'priority': 'medium',
                'episode': 'Unknown',
                'sequence': 'Unknown',
                'status': 'unknown'
            }

    def create_media_item_from_task(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a media item from a task (legacy method - kept for compatibility)."""
        try:
            task_id = task.get('_id', '')

            # Generate paths for this task
            paths = self.db.generate_task_paths(task_id, "001", "maya_scene")
            if not paths:
                return None

            # Look for media files in the media directory
            media_file_path = paths.get('media_file_path', '')
            if not media_file_path:
                return None

            # Check if media directory exists and has files
            media_dir = os.path.dirname(media_file_path)
            if not os.path.exists(media_dir):
                return None

            # Look for video/image files
            media_extensions = ['.mov', '.mp4', '.avi', '.jpg', '.jpeg', '.png', '.exr', '.tiff']
            media_files = []

            try:
                for file in os.listdir(media_dir):
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext in media_extensions:
                        media_files.append(os.path.join(media_dir, file))
            except OSError:
                pass

            # If no actual media files found, create a placeholder entry
            if not media_files:
                # Use a placeholder path
                placeholder_path = os.path.join(media_dir, f"{task_id}_v001.mov")
                media_files = [placeholder_path]

            # Create media item for the first/main media file
            main_media_file = media_files[0]

            media_item = {
                'task_id': task_id,
                'file_path': main_media_file,
                'file_type': self.get_file_type(main_media_file),
                'version': 'v001',  # Default version
                'status': task.get('status', 'pending'),
                'total_frames': 100,  # Default frame count
                'frame_rate': 24.0,
                'created_date': datetime.now().isoformat(),
                'file_size': self.get_file_size(main_media_file),
                'task_info': {
                    'shot': task.get('shot', 'Unknown'),
                    'task': task.get('task', 'Unknown'),
                    'artist': task.get('artist', 'Unknown'),
                    'priority': task.get('priority', 'medium')
                }
            }

            return media_item

        except Exception as e:
            print(f"Error creating media item from task: {e}")
            return None
    
    def get_file_type(self, file_path: str) -> str:
        """Get file type from file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.mov', '.mp4', '.avi', '.mkv']:
            return 'video'
        elif ext in ['.jpg', '.jpeg', '.png', '.tiff', '.tga']:
            return 'image'
        elif ext in ['.exr']:
            return 'render'
        else:
            return 'unknown'
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes."""
        try:
            if os.path.exists(file_path):
                return os.path.getsize(file_path)
        except OSError:
            pass
        return 0
    
    def add_annotation(self, media_item: Dict[str, Any], annotation: Dict[str, Any]):
        """Add annotation to media item."""
        try:
            # In a full implementation, this would save to database
            # For demo purposes, we'll just log the annotation
            task_id = media_item.get('task_id', 'unknown')
            annotation_text = annotation.get('text', '')
            annotation_type = annotation.get('type', 'note')
            
            print(f"Added {annotation_type} annotation to {task_id}: {annotation_text}")
            
            # Here you would typically save to a database collection like:
            # annotation_record = {
            #     'task_id': task_id,
            #     'media_file': media_item.get('file_path', ''),
            #     'annotation_data': annotation,
            #     'created_at': datetime.now().isoformat()
            # }
            # self.db.insert_one('annotations', annotation_record)
            
        except Exception as e:
            print(f"Error adding annotation: {e}")
    
    def update_approval_status(self, media_item: Dict[str, Any], approval_data: Dict[str, Any]):
        """Update approval status for media item."""
        try:
            task_id = media_item.get('task_id', 'unknown')
            status = approval_data.get('status', 'pending')
            notes = approval_data.get('supervisor_notes', '')
            
            print(f"Updated approval status for {task_id}: {status}")
            if notes:
                print(f"Supervisor notes: {notes}")
            
            # In a full implementation, this would update the database
            # For demo purposes, we'll just log the approval change
            
            # Here you would typically update the task status and save approval record:
            # self.db.update_one(
            #     'tasks',
            #     {'_id': task_id},
            #     {'$set': {'approval_status': status, 'approval_notes': notes}}
            # )
            # 
            # approval_record = {
            #     'task_id': task_id,
            #     'media_file': media_item.get('file_path', ''),
            #     'approval_data': approval_data,
            #     'updated_at': datetime.now().isoformat()
            # }
            # self.db.insert_one('approvals', approval_record)
            
        except Exception as e:
            print(f"Error updating approval status: {e}")
    
    def get_annotations_for_media(self, media_item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get annotations for a specific media item."""
        try:
            task_id = media_item.get('task_id', '')
            
            # In a full implementation, this would query the database
            # For demo purposes, return empty list
            # annotations = self.db.find('annotations', {'task_id': task_id})
            # return annotations
            
            return []
            
        except Exception as e:
            print(f"Error loading annotations: {e}")
            return []
    
    def get_approval_history(self, media_item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get approval history for a specific media item."""
        try:
            task_id = media_item.get('task_id', '')
            
            # In a full implementation, this would query the database
            # For demo purposes, return sample history
            # approvals = self.db.find('approvals', {'task_id': task_id})
            # return approvals
            
            return [
                {
                    'timestamp': datetime.now().isoformat(),
                    'status': 'pending',
                    'user': 'System',
                    'notes': 'Initial submission for review'
                }
            ]
            
        except Exception as e:
            print(f"Error loading approval history: {e}")
            return []
