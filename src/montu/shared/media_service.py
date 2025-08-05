"""
Media Service CRUD Operations

Comprehensive media file management system providing storage, retrieval,
metadata extraction, thumbnail generation, and versioning capabilities.
"""

import os
import json
import hashlib
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, BinaryIO
from datetime import datetime
import uuid
import mimetypes

# Try to import optional dependencies for media processing
try:
    from PIL import Image, ImageOps
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

from .json_database import JSONDatabase


class MediaMetadata:
    """Media metadata container."""
    
    def __init__(self):
        self.file_size: int = 0
        self.mime_type: str = ""
        self.duration: Optional[float] = None
        self.width: Optional[int] = None
        self.height: Optional[int] = None
        self.frame_rate: Optional[float] = None
        self.codec: Optional[str] = None
        self.bit_rate: Optional[int] = None
        self.color_space: Optional[str] = None
        self.creation_date: Optional[str] = None
        self.modification_date: Optional[str] = None
        self.checksum: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'duration': self.duration,
            'width': self.width,
            'height': self.height,
            'frame_rate': self.frame_rate,
            'codec': self.codec,
            'bit_rate': self.bit_rate,
            'color_space': self.color_space,
            'creation_date': self.creation_date,
            'modification_date': self.modification_date,
            'checksum': self.checksum
        }


class MediaStorageBackend:
    """Abstract base class for media storage backends."""
    
    def store_file(self, source_path: str, destination_key: str) -> str:
        """Store file and return storage URL."""
        raise NotImplementedError
    
    def retrieve_file(self, storage_key: str, destination_path: str) -> bool:
        """Retrieve file from storage."""
        raise NotImplementedError
    
    def delete_file(self, storage_key: str) -> bool:
        """Delete file from storage."""
        raise NotImplementedError
    
    def file_exists(self, storage_key: str) -> bool:
        """Check if file exists in storage."""
        raise NotImplementedError


class LocalFileSystemBackend(MediaStorageBackend):
    """Local filesystem storage backend."""
    
    def __init__(self, base_path: str):
        """Initialize with base storage path."""
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def store_file(self, source_path: str, destination_key: str) -> str:
        """Store file in local filesystem."""
        destination_path = self.base_path / destination_key
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(source_path, destination_path)
        return str(destination_path)
    
    def retrieve_file(self, storage_key: str, destination_path: str) -> bool:
        """Retrieve file from local storage."""
        source_path = self.base_path / storage_key
        if source_path.exists():
            shutil.copy2(source_path, destination_path)
            return True
        return False
    
    def delete_file(self, storage_key: str) -> bool:
        """Delete file from local storage."""
        file_path = self.base_path / storage_key
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def file_exists(self, storage_key: str) -> bool:
        """Check if file exists in local storage."""
        return (self.base_path / storage_key).exists()
    
    def get_file_path(self, storage_key: str) -> str:
        """Get full file path for local access."""
        return str(self.base_path / storage_key)


class MediaMetadataExtractor:
    """Media metadata extraction utilities."""
    
    @staticmethod
    def extract_basic_metadata(file_path: str) -> MediaMetadata:
        """Extract basic file metadata."""
        metadata = MediaMetadata()
        
        if not os.path.exists(file_path):
            return metadata
        
        # Basic file information
        stat = os.stat(file_path)
        metadata.file_size = stat.st_size
        metadata.creation_date = datetime.fromtimestamp(stat.st_ctime).isoformat()
        metadata.modification_date = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        # MIME type
        metadata.mime_type, _ = mimetypes.guess_type(file_path)
        if not metadata.mime_type:
            metadata.mime_type = 'application/octet-stream'
        
        # File checksum
        metadata.checksum = MediaMetadataExtractor._calculate_checksum(file_path)
        
        return metadata
    
    @staticmethod
    def extract_image_metadata(file_path: str) -> MediaMetadata:
        """Extract image-specific metadata."""
        metadata = MediaMetadataExtractor.extract_basic_metadata(file_path)
        
        if not PIL_AVAILABLE:
            return metadata
        
        try:
            with Image.open(file_path) as img:
                metadata.width, metadata.height = img.size
                metadata.color_space = img.mode
                
                # Extract EXIF data if available
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    # Add specific EXIF processing here if needed
                    
        except Exception as e:
            print(f"Error extracting image metadata: {e}")
        
        return metadata
    
    @staticmethod
    def extract_video_metadata(file_path: str) -> MediaMetadata:
        """Extract video-specific metadata."""
        metadata = MediaMetadataExtractor.extract_basic_metadata(file_path)
        
        if not CV2_AVAILABLE:
            return metadata
        
        try:
            cap = cv2.VideoCapture(file_path)
            
            if cap.isOpened():
                # Video dimensions
                metadata.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                metadata.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                # Frame rate
                metadata.frame_rate = cap.get(cv2.CAP_PROP_FPS)
                
                # Duration (frames / fps)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                if metadata.frame_rate > 0:
                    metadata.duration = frame_count / metadata.frame_rate
                
                # Codec information
                fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
                metadata.codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
            
            cap.release()
            
        except Exception as e:
            print(f"Error extracting video metadata: {e}")
        
        return metadata
    
    @staticmethod
    def _calculate_checksum(file_path: str) -> str:
        """Calculate MD5 checksum of file."""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""


class ThumbnailGenerator:
    """Thumbnail generation utilities."""
    
    @staticmethod
    def generate_image_thumbnail(source_path: str, output_path: str, 
                               size: tuple = (256, 256)) -> bool:
        """Generate thumbnail for image file."""
        if not PIL_AVAILABLE:
            return False
        
        try:
            with Image.open(source_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Generate thumbnail
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Ensure output directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Save thumbnail
                img.save(output_path, 'JPEG', quality=85)
                return True
                
        except Exception as e:
            print(f"Error generating image thumbnail: {e}")
            return False
    
    @staticmethod
    def generate_video_thumbnail(source_path: str, output_path: str, 
                               timestamp: float = 1.0, size: tuple = (256, 256)) -> bool:
        """Generate thumbnail for video file."""
        if not CV2_AVAILABLE:
            return False
        
        try:
            cap = cv2.VideoCapture(source_path)
            
            if not cap.isOpened():
                return False
            
            # Seek to timestamp
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_number = int(timestamp * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            # Read frame
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return False
            
            # Resize frame
            height, width = frame.shape[:2]
            aspect_ratio = width / height
            
            if aspect_ratio > 1:
                new_width = size[0]
                new_height = int(size[0] / aspect_ratio)
            else:
                new_height = size[1]
                new_width = int(size[1] * aspect_ratio)
            
            resized_frame = cv2.resize(frame, (new_width, new_height))
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save thumbnail
            cv2.imwrite(output_path, resized_frame)
            return True
            
        except Exception as e:
            print(f"Error generating video thumbnail: {e}")
            return False


class MediaService:
    """
    Comprehensive media service providing CRUD operations for media files.
    
    Features:
    - Media file storage and retrieval
    - Metadata extraction and management
    - Thumbnail generation
    - Version management
    - Task linking
    """
    
    def __init__(self, db: JSONDatabase, storage_backend: MediaStorageBackend):
        """Initialize media service."""
        self.db = db
        self.storage = storage_backend
        
        # Supported media types
        self.supported_image_types = {'.jpg', '.jpeg', '.png', '.tiff', '.tga', '.exr', '.bmp', '.gif'}
        self.supported_video_types = {'.mov', '.mp4', '.avi', '.mkv', '.webm', '.flv', '.wmv'}
        self.supported_audio_types = {'.wav', '.mp3', '.aac', '.flac', '.ogg'}
    
    def upload_media(self, file_path: str, task_id: str, version: str = "v001", 
                    author: str = "Unknown", description: str = "", 
                    tags: List[str] = None) -> Optional[str]:
        """
        Upload media file and create database record.
        
        Args:
            file_path: Path to source media file
            task_id: Associated task ID
            version: Version string
            author: Author/uploader name
            description: Media description
            tags: Optional tags list
            
        Returns:
            Media record ID if successful, None otherwise
        """
        if not os.path.exists(file_path):
            print(f"Source file not found: {file_path}")
            return None
        
        try:
            # Generate unique media ID
            media_id = str(uuid.uuid4())
            
            # Determine file type and extract metadata
            file_ext = os.path.splitext(file_path)[1].lower()
            media_type = self._determine_media_type(file_ext)
            
            if media_type == 'image':
                metadata = MediaMetadataExtractor.extract_image_metadata(file_path)
            elif media_type == 'video':
                metadata = MediaMetadataExtractor.extract_video_metadata(file_path)
            else:
                metadata = MediaMetadataExtractor.extract_basic_metadata(file_path)
            
            # Generate storage key
            filename = os.path.basename(file_path)
            storage_key = f"media/{task_id}/{version}/{media_id}_{filename}"
            
            # Store file
            storage_url = self.storage.store_file(file_path, storage_key)
            
            # Generate thumbnail
            thumbnail_key = None
            if media_type in ['image', 'video']:
                thumbnail_key = f"thumbnails/{task_id}/{version}/{media_id}_thumb.jpg"
                thumbnail_path = self.storage.get_file_path(thumbnail_key) if hasattr(self.storage, 'get_file_path') else None
                
                if thumbnail_path:
                    if media_type == 'image':
                        ThumbnailGenerator.generate_image_thumbnail(file_path, thumbnail_path)
                    elif media_type == 'video':
                        ThumbnailGenerator.generate_video_thumbnail(file_path, thumbnail_path)
            
            # Create media record
            media_record = {
                '_id': media_id,
                'linked_task_id': task_id,
                'linked_version': version,
                'author': author,
                'file_name': filename,
                'media_type': media_type,
                'file_extension': file_ext,
                'storage_key': storage_key,
                'storage_url': storage_url,
                'thumbnail_key': thumbnail_key,
                'description': description,
                'tags': tags or [],
                'metadata': metadata.to_dict(),
                'upload_time': datetime.now().isoformat(),
                'status': 'active',
                'review_selected': False,
                'approval_status': 'pending'
            }
            
            # Insert into database
            result_id = self.db.insert_one('media_records', media_record)
            
            print(f"Successfully uploaded media: {media_id}")
            return result_id

        except Exception as e:
            print(f"Error uploading media: {e}")
            return None

    def get_media_by_id(self, media_id: str) -> Optional[Dict[str, Any]]:
        """Get media record by ID."""
        return self.db.find_one('media_records', {'_id': media_id})

    def get_media_by_task(self, task_id: str, version: str = None) -> List[Dict[str, Any]]:
        """Get media records for a task, optionally filtered by version."""
        query = {'linked_task_id': task_id}
        if version:
            query['linked_version'] = version

        return self.db.find('media_records', query)

    def get_media_versions(self, task_id: str) -> List[str]:
        """Get all versions of media for a task."""
        media_records = self.db.find('media_records', {'linked_task_id': task_id})
        versions = list(set(record.get('linked_version', '') for record in media_records))
        return sorted(versions)

    def update_media_metadata(self, media_id: str, metadata_updates: Dict[str, Any]) -> bool:
        """Update media metadata."""
        try:
            update_data = {
                'metadata': metadata_updates,
                '_updated_at': datetime.now().isoformat()
            }

            success = self.db.update_one(
                'media_records',
                {'_id': media_id},
                {'$set': update_data}
            )

            return success

        except Exception as e:
            print(f"Error updating media metadata: {e}")
            return False

    def update_media_info(self, media_id: str, description: str = None,
                         tags: List[str] = None, review_selected: bool = None,
                         approval_status: str = None) -> bool:
        """Update media information."""
        try:
            update_data = {'_updated_at': datetime.now().isoformat()}

            if description is not None:
                update_data['description'] = description
            if tags is not None:
                update_data['tags'] = tags
            if review_selected is not None:
                update_data['review_selected'] = review_selected
            if approval_status is not None:
                update_data['approval_status'] = approval_status

            success = self.db.update_one(
                'media_records',
                {'_id': media_id},
                {'$set': update_data}
            )

            return success

        except Exception as e:
            print(f"Error updating media info: {e}")
            return False

    def delete_media(self, media_id: str, remove_files: bool = True) -> bool:
        """Delete media record and optionally remove files."""
        try:
            # Get media record
            media_record = self.get_media_by_id(media_id)
            if not media_record:
                return False

            # Remove files if requested
            if remove_files:
                storage_key = media_record.get('storage_key')
                thumbnail_key = media_record.get('thumbnail_key')

                if storage_key:
                    self.storage.delete_file(storage_key)
                if thumbnail_key:
                    self.storage.delete_file(thumbnail_key)

            # Remove database record
            success = self.db.delete_one('media_records', {'_id': media_id})

            if success:
                print(f"Successfully deleted media: {media_id}")

            return success

        except Exception as e:
            print(f"Error deleting media: {e}")
            return False

    def archive_media(self, media_id: str) -> bool:
        """Archive media (soft delete)."""
        return self.update_media_info(media_id, approval_status='archived')

    def restore_media(self, media_id: str) -> bool:
        """Restore archived media."""
        return self.update_media_info(media_id, approval_status='pending')

    def get_media_file_path(self, media_id: str) -> Optional[str]:
        """Get local file path for media."""
        media_record = self.get_media_by_id(media_id)
        if not media_record:
            return None

        storage_key = media_record.get('storage_key')
        if not storage_key:
            return None

        if hasattr(self.storage, 'get_file_path'):
            return self.storage.get_file_path(storage_key)

        return None

    def get_thumbnail_path(self, media_id: str) -> Optional[str]:
        """Get thumbnail file path for media."""
        media_record = self.get_media_by_id(media_id)
        if not media_record:
            return None

        thumbnail_key = media_record.get('thumbnail_key')
        if not thumbnail_key:
            return None

        if hasattr(self.storage, 'get_file_path'):
            return self.storage.get_file_path(thumbnail_key)

        return None

    def regenerate_thumbnail(self, media_id: str, timestamp: float = 1.0) -> bool:
        """Regenerate thumbnail for media."""
        try:
            media_record = self.get_media_by_id(media_id)
            if not media_record:
                return False

            # Get source file path
            source_path = self.get_media_file_path(media_id)
            if not source_path or not os.path.exists(source_path):
                return False

            # Get thumbnail path
            thumbnail_key = media_record.get('thumbnail_key')
            if not thumbnail_key:
                return False

            thumbnail_path = self.storage.get_file_path(thumbnail_key) if hasattr(self.storage, 'get_file_path') else None
            if not thumbnail_path:
                return False

            # Generate thumbnail based on media type
            media_type = media_record.get('media_type', '')

            if media_type == 'image':
                success = ThumbnailGenerator.generate_image_thumbnail(source_path, thumbnail_path)
            elif media_type == 'video':
                success = ThumbnailGenerator.generate_video_thumbnail(source_path, thumbnail_path, timestamp)
            else:
                return False

            if success:
                # Update thumbnail generation timestamp
                self.db.update_one(
                    'media_records',
                    {'_id': media_id},
                    {'$set': {'thumbnail_generated_at': datetime.now().isoformat()}}
                )

            return success

        except Exception as e:
            print(f"Error regenerating thumbnail: {e}")
            return False

    def create_media_version(self, source_media_id: str, new_file_path: str,
                           version: str, author: str = "Unknown",
                           description: str = "") -> Optional[str]:
        """Create new version of existing media."""
        try:
            # Get source media record
            source_record = self.get_media_by_id(source_media_id)
            if not source_record:
                return None

            # Upload new version
            new_media_id = self.upload_media(
                file_path=new_file_path,
                task_id=source_record['linked_task_id'],
                version=version,
                author=author,
                description=description,
                tags=source_record.get('tags', [])
            )

            if new_media_id:
                # Link to previous version
                self.db.update_one(
                    'media_records',
                    {'_id': new_media_id},
                    {'$set': {'previous_version_id': source_media_id}}
                )

            return new_media_id

        except Exception as e:
            print(f"Error creating media version: {e}")
            return None

    def get_media_statistics(self, task_id: str = None, project_id: str = None) -> Dict[str, Any]:
        """Get media statistics."""
        try:
            query = {}

            if task_id:
                query['linked_task_id'] = task_id
            elif project_id:
                # Get tasks for project first
                tasks = self.db.find('tasks', {'project': project_id})
                task_ids = [task['_id'] for task in tasks]
                query['linked_task_id'] = {'$in': task_ids}

            media_records = self.db.find('media_records', query)

            stats = {
                'total_media': len(media_records),
                'by_type': {},
                'by_status': {},
                'total_size': 0,
                'versions': set(),
                'authors': set()
            }

            for record in media_records:
                # Count by type
                media_type = record.get('media_type', 'unknown')
                stats['by_type'][media_type] = stats['by_type'].get(media_type, 0) + 1

                # Count by status
                status = record.get('approval_status', 'unknown')
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1

                # Total size
                metadata = record.get('metadata', {})
                file_size = metadata.get('file_size', 0)
                stats['total_size'] += file_size

                # Collect versions and authors
                stats['versions'].add(record.get('linked_version', ''))
                stats['authors'].add(record.get('author', ''))

            # Convert sets to lists
            stats['versions'] = sorted(list(stats['versions']))
            stats['authors'] = sorted(list(stats['authors']))

            return stats

        except Exception as e:
            print(f"Error getting media statistics: {e}")
            return {}

    def search_media(self, query: str, task_id: str = None,
                    media_type: str = None, author: str = None) -> List[Dict[str, Any]]:
        """Search media records."""
        try:
            search_filters = {}

            if task_id:
                search_filters['linked_task_id'] = task_id
            if media_type:
                search_filters['media_type'] = media_type
            if author:
                search_filters['author'] = author

            # Get all matching records
            media_records = self.db.find('media_records', search_filters)

            # Filter by text query
            if query:
                query_lower = query.lower()
                filtered_records = []

                for record in media_records:
                    # Search in filename, description, and tags
                    searchable_text = " ".join([
                        record.get('file_name', ''),
                        record.get('description', ''),
                        " ".join(record.get('tags', []))
                    ]).lower()

                    if query_lower in searchable_text:
                        filtered_records.append(record)

                return filtered_records

            return media_records

        except Exception as e:
            print(f"Error searching media: {e}")
            return []

    def _determine_media_type(self, file_extension: str) -> str:
        """Determine media type from file extension."""
        ext = file_extension.lower()

        if ext in self.supported_image_types:
            return 'image'
        elif ext in self.supported_video_types:
            return 'video'
        elif ext in self.supported_audio_types:
            return 'audio'
        else:
            return 'other'

    def cleanup_orphaned_files(self) -> Dict[str, int]:
        """Clean up orphaned media files."""
        try:
            # Get all media records
            media_records = self.db.find('media_records', {})

            # Track cleanup statistics
            cleanup_stats = {
                'orphaned_files_removed': 0,
                'missing_files_cleaned': 0,
                'thumbnails_regenerated': 0
            }

            # Check for missing files and orphaned records
            for record in media_records:
                media_id = record['_id']
                storage_key = record.get('storage_key')

                if storage_key and not self.storage.file_exists(storage_key):
                    # File is missing, mark record as missing
                    self.db.update_one(
                        'media_records',
                        {'_id': media_id},
                        {'$set': {'status': 'missing_file'}}
                    )
                    cleanup_stats['missing_files_cleaned'] += 1

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
