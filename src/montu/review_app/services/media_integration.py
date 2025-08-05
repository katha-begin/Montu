"""
Media Integration Service

Integration layer connecting the Review Application with the comprehensive
media service CRUD operations for enhanced media management capabilities.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from ...shared.json_database import JSONDatabase
from ...shared.media_service import MediaService, LocalFileSystemBackend


class ReviewMediaService:
    """
    Enhanced media service for the Review Application.
    
    Provides high-level media operations specifically designed for
    review workflows, annotation management, and approval processes.
    """
    
    def __init__(self, db: JSONDatabase = None, media_storage_path: str = None):
        """Initialize review media service."""
        self.db = db or JSONDatabase()
        
        # Initialize media storage
        if not media_storage_path:
            # Default to data directory
            data_dir = Path(__file__).parent.parent.parent.parent.parent / "data"
            media_storage_path = str(data_dir / "media_storage")
        
        self.storage_backend = LocalFileSystemBackend(media_storage_path)
        self.media_service = MediaService(self.db, self.storage_backend)
    
    def get_media_for_review(self, project_id: str, status_filter: str = None) -> List[Dict[str, Any]]:
        """
        Get media files ready for review.
        
        Args:
            project_id: Project identifier
            status_filter: Optional status filter ('pending', 'approved', 'rejected')
            
        Returns:
            List of media records with enhanced review information
        """
        try:
            # Get all tasks for the project
            tasks = self.db.find('tasks', {'project': project_id})
            task_ids = [task['_id'] for task in tasks]
            
            if not task_ids:
                return []
            
            # Get media records for these tasks
            query = {'linked_task_id': {'$in': task_ids}}
            
            if status_filter:
                query['approval_status'] = status_filter
            
            media_records = self.db.find('media_records', query)
            
            # Enhance records with review information
            enhanced_records = []
            for record in media_records:
                enhanced_record = self._enhance_media_record_for_review(record)
                if enhanced_record:
                    enhanced_records.append(enhanced_record)
            
            # Sort by upload time (newest first)
            enhanced_records.sort(
                key=lambda x: x.get('upload_time', ''), 
                reverse=True
            )
            
            return enhanced_records
            
        except Exception as e:
            print(f"Error getting media for review: {e}")
            return []
    
    def _enhance_media_record_for_review(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Enhance media record with review-specific information."""
        try:
            # Get associated task information
            task_id = record.get('linked_task_id', '')
            task = self.db.find_one('tasks', {'_id': task_id})
            
            if not task:
                return None
            
            # Get file paths
            file_path = self.media_service.get_media_file_path(record['_id'])
            thumbnail_path = self.media_service.get_thumbnail_path(record['_id'])
            
            # Build enhanced record
            enhanced_record = {
                # Original media record data
                **record,
                
                # File access information
                'file_path': file_path,
                'thumbnail_path': thumbnail_path,
                'file_exists': file_path and os.path.exists(file_path),
                'thumbnail_exists': thumbnail_path and os.path.exists(thumbnail_path),
                
                # Task information for review context
                'task_info': {
                    'shot': task.get('shot', 'Unknown'),
                    'sequence': task.get('sequence', 'Unknown'),
                    'episode': task.get('episode', 'Unknown'),
                    'task_type': task.get('task', 'Unknown'),
                    'artist': task.get('artist', 'Unknown'),
                    'status': task.get('status', 'Unknown'),
                    'priority': task.get('priority', 'medium')
                },
                
                # Review workflow information
                'review_info': {
                    'approval_status': record.get('approval_status', 'pending'),
                    'review_selected': record.get('review_selected', False),
                    'review_notes': record.get('review_notes', ''),
                    'reviewer': record.get('reviewer', ''),
                    'review_date': record.get('review_date', ''),
                    'approval_date': record.get('approval_date', '')
                },
                
                # Media metadata for display
                'display_info': self._get_display_info(record)
            }
            
            return enhanced_record
            
        except Exception as e:
            print(f"Error enhancing media record: {e}")
            return None
    
    def _get_display_info(self, record: Dict[str, Any]) -> Dict[str, str]:
        """Get formatted display information for media."""
        metadata = record.get('metadata', {})
        
        display_info = {
            'file_size_formatted': self._format_file_size(metadata.get('file_size', 0)),
            'duration_formatted': self._format_duration(metadata.get('duration')),
            'resolution_formatted': self._format_resolution(
                metadata.get('width'), metadata.get('height')
            ),
            'upload_date_formatted': self._format_date(record.get('upload_time', '')),
            'media_type_display': record.get('media_type', 'unknown').title()
        }
        
        return display_info
    
    def submit_for_review(self, media_id: str, reviewer: str = "Unknown") -> bool:
        """Submit media for review."""
        try:
            success = self.media_service.update_media_info(
                media_id,
                review_selected=True,
                approval_status='under_review'
            )
            
            if success:
                # Add review submission record
                self.db.update_one(
                    'media_records',
                    {'_id': media_id},
                    {'$set': {
                        'reviewer': reviewer,
                        'review_submitted_date': datetime.now().isoformat()
                    }}
                )
            
            return success
            
        except Exception as e:
            print(f"Error submitting media for review: {e}")
            return False
    
    def approve_media(self, media_id: str, reviewer: str, notes: str = "") -> bool:
        """Approve media after review."""
        try:
            success = self.db.update_one(
                'media_records',
                {'_id': media_id},
                {'$set': {
                    'approval_status': 'approved',
                    'reviewer': reviewer,
                    'review_notes': notes,
                    'review_date': datetime.now().isoformat(),
                    'approval_date': datetime.now().isoformat()
                }}
            )
            
            return success
            
        except Exception as e:
            print(f"Error approving media: {e}")
            return False
    
    def reject_media(self, media_id: str, reviewer: str, notes: str = "") -> bool:
        """Reject media after review."""
        try:
            success = self.db.update_one(
                'media_records',
                {'_id': media_id},
                {'$set': {
                    'approval_status': 'rejected',
                    'reviewer': reviewer,
                    'review_notes': notes,
                    'review_date': datetime.now().isoformat()
                }}
            )
            
            return success
            
        except Exception as e:
            print(f"Error rejecting media: {e}")
            return False
    
    def add_review_annotation(self, media_id: str, annotation_data: Dict[str, Any]) -> str:
        """Add annotation to media for review."""
        try:
            annotation_record = {
                '_id': f"annotation_{media_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'media_id': media_id,
                'annotation_type': annotation_data.get('type', 'note'),
                'content': annotation_data.get('content', ''),
                'position': annotation_data.get('position', {}),  # x, y, frame for video
                'author': annotation_data.get('author', 'Unknown'),
                'created_at': datetime.now().isoformat(),
                'status': 'active'
            }
            
            annotation_id = self.db.insert_one('annotations', annotation_record)
            
            # Update media record to indicate it has annotations
            self.db.update_one(
                'media_records',
                {'_id': media_id},
                {'$set': {'has_annotations': True}}
            )
            
            return annotation_id
            
        except Exception as e:
            print(f"Error adding annotation: {e}")
            return ""
    
    def get_media_annotations(self, media_id: str) -> List[Dict[str, Any]]:
        """Get all annotations for a media file."""
        try:
            annotations = self.db.find('annotations', {
                'media_id': media_id,
                'status': 'active'
            })
            
            # Sort by creation date
            annotations.sort(key=lambda x: x.get('created_at', ''))
            
            return annotations
            
        except Exception as e:
            print(f"Error getting annotations: {e}")
            return []
    
    def get_review_statistics(self, project_id: str) -> Dict[str, Any]:
        """Get review statistics for a project."""
        try:
            # Get project media statistics
            media_stats = self.media_service.get_media_statistics(project_id=project_id)
            
            # Get review-specific statistics
            tasks = self.db.find('tasks', {'project': project_id})
            task_ids = [task['_id'] for task in tasks]
            
            if not task_ids:
                return {'error': 'No tasks found for project'}
            
            media_records = self.db.find('media_records', {
                'linked_task_id': {'$in': task_ids}
            })
            
            review_stats = {
                'total_media': len(media_records),
                'pending_review': 0,
                'under_review': 0,
                'approved': 0,
                'rejected': 0,
                'archived': 0,
                'with_annotations': 0,
                'review_selected': 0
            }
            
            for record in media_records:
                status = record.get('approval_status', 'pending')
                review_stats[status] = review_stats.get(status, 0) + 1
                
                if record.get('has_annotations'):
                    review_stats['with_annotations'] += 1
                
                if record.get('review_selected'):
                    review_stats['review_selected'] += 1
            
            # Combine with media statistics
            combined_stats = {
                **media_stats,
                'review_workflow': review_stats
            }
            
            return combined_stats
            
        except Exception as e:
            print(f"Error getting review statistics: {e}")
            return {}
    
    def cleanup_old_media(self, project_id: str, days_old: int = 30) -> Dict[str, int]:
        """Clean up old media files for a project."""
        try:
            from datetime import timedelta
            
            cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
            
            # Get tasks for project
            tasks = self.db.find('tasks', {'project': project_id})
            task_ids = [task['_id'] for task in tasks]
            
            if not task_ids:
                return {'error': 'No tasks found'}
            
            # Find old media records
            old_media = self.db.find('media_records', {
                'linked_task_id': {'$in': task_ids},
                'upload_time': {'$lt': cutoff_date},
                'approval_status': {'$in': ['rejected', 'archived']}
            })
            
            cleanup_stats = {
                'files_removed': 0,
                'records_archived': 0,
                'space_freed': 0
            }
            
            for record in old_media:
                # Archive record instead of deleting
                success = self.media_service.archive_media(record['_id'])
                if success:
                    cleanup_stats['records_archived'] += 1
                    
                    # Add to space freed calculation
                    metadata = record.get('metadata', {})
                    file_size = metadata.get('file_size', 0)
                    cleanup_stats['space_freed'] += file_size
            
            return cleanup_stats
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            return {}
    
    @staticmethod
    def _format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def _format_duration(duration_seconds: Optional[float]) -> str:
        """Format duration in human-readable format."""
        if not duration_seconds:
            return "Unknown"
        
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)
        
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    @staticmethod
    def _format_resolution(width: Optional[int], height: Optional[int]) -> str:
        """Format resolution in human-readable format."""
        if width and height:
            return f"{width}x{height}"
        return "Unknown"
    
    @staticmethod
    def _format_date(iso_date: str) -> str:
        """Format ISO date in human-readable format."""
        if not iso_date:
            return "Unknown"
        
        try:
            dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return iso_date
