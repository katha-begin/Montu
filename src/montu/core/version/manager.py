"""
Version Management System

Comprehensive version management system for the Montu Manager ecosystem
providing auto-incrementing versions, publish/lock functionality, and metadata handling.
"""

import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..data.database import JSONDatabase


class VersionStatus(Enum):
    """Version status enumeration."""
    WIP = "wip"                    # Work in progress
    REVIEW = "review"              # Under review
    APPROVED = "approved"          # Approved for use
    PUBLISHED = "published"        # Published/locked version
    ARCHIVED = "archived"          # Archived version
    REJECTED = "rejected"          # Rejected version


@dataclass
class VersionInfo:
    """Version information data structure."""
    version: str                   # Version string (e.g., "v001")
    version_number: int           # Numeric version (e.g., 1)
    status: VersionStatus         # Version status
    author: str                   # Version author
    created_date: str             # Creation timestamp
    modified_date: str            # Last modification timestamp
    description: str              # Version description/notes
    file_path: str               # File path for this version
    file_size: int               # File size in bytes
    is_locked: bool              # Whether version is locked
    parent_version: Optional[str] # Previous version reference
    metadata: Dict[str, Any]     # Additional metadata


class VersionManager:
    """
    Comprehensive version management system.
    
    Handles version creation, auto-incrementing, publishing, locking,
    and metadata management for tasks and media files.
    """
    
    def __init__(self, db: JSONDatabase = None):
        """Initialize version manager."""
        self.db = db or JSONDatabase()
        
        # Version format settings (can be overridden by project config)
        self.default_settings = {
            'padding': 3,
            'start_version': 1,
            'increment': 1,
            'format': 'v{version:03d}',
            'auto_increment': True,
            'require_notes': False,
            'lock_on_publish': True
        }
    
    def get_project_version_settings(self, project_id: str) -> Dict[str, Any]:
        """Get version settings for a specific project."""
        try:
            project_config = self.db.find_one('project_configs', {'_id': project_id})
            if project_config and 'version_settings' in project_config:
                settings = self.default_settings.copy()
                settings.update(project_config['version_settings'])
                return settings
            return self.default_settings
        except Exception as e:
            print(f"Error getting project version settings: {e}")
            return self.default_settings
    
    def parse_version_string(self, version_str: str) -> Tuple[int, str]:
        """
        Parse version string to extract numeric version and format.
        
        Args:
            version_str: Version string (e.g., "v001", "version_002")
            
        Returns:
            Tuple of (version_number, format_prefix)
        """
        # Common version patterns
        patterns = [
            r'^v(\d+)$',           # v001, v002
            r'^version_(\d+)$',    # version_001
            r'^ver(\d+)$',         # ver001
            r'^(\d+)$'             # 001, 002
        ]
        
        for pattern in patterns:
            match = re.match(pattern, version_str, re.IGNORECASE)
            if match:
                version_num = int(match.group(1))
                prefix = version_str[:match.start(1)]
                return version_num, prefix
        
        # Default fallback
        return 1, "v"
    
    def format_version_string(self, version_num: int, project_id: str = None) -> str:
        """
        Format version number according to project settings.
        
        Args:
            version_num: Numeric version
            project_id: Project identifier for settings lookup
            
        Returns:
            Formatted version string
        """
        settings = self.get_project_version_settings(project_id) if project_id else self.default_settings
        
        try:
            return settings['format'].format(version=version_num)
        except (KeyError, ValueError):
            # Fallback to default format
            padding = settings.get('padding', 3)
            return f"v{version_num:0{padding}d}"
    
    def get_next_version(self, task_id: str, project_id: str = None) -> str:
        """
        Get the next available version number for a task.
        
        Args:
            task_id: Task identifier
            project_id: Project identifier
            
        Returns:
            Next version string (e.g., "v002")
        """
        try:
            # Get existing versions for this task
            existing_versions = self.get_task_versions(task_id)
            
            if not existing_versions:
                # No existing versions, start with initial version
                settings = self.get_project_version_settings(project_id) if project_id else self.default_settings
                start_version = settings.get('start_version', 1)
                return self.format_version_string(start_version, project_id)
            
            # Find highest version number
            max_version = 0
            for version_info in existing_versions:
                version_num, _ = self.parse_version_string(version_info.version)
                max_version = max(max_version, version_num)
            
            # Increment by configured amount
            settings = self.get_project_version_settings(project_id) if project_id else self.default_settings
            increment = settings.get('increment', 1)
            next_version = max_version + increment
            
            return self.format_version_string(next_version, project_id)
            
        except Exception as e:
            print(f"Error getting next version for task {task_id}: {e}")
            return self.format_version_string(1, project_id)
    
    def create_version(self, task_id: str, file_path: str, author: str,
                      description: str = "", version: str = None,
                      project_id: str = None, metadata: Dict[str, Any] = None) -> Optional[VersionInfo]:
        """
        Create a new version for a task.
        
        Args:
            task_id: Task identifier
            file_path: Path to the file for this version
            author: Version author
            description: Version description/notes
            version: Specific version string (auto-generated if None)
            project_id: Project identifier
            metadata: Additional metadata
            
        Returns:
            VersionInfo object if successful, None otherwise
        """
        try:
            # Auto-generate version if not provided
            if not version:
                version = self.get_next_version(task_id, project_id)
            
            # Validate version doesn't already exist
            existing_version = self.get_version_info(task_id, version)
            if existing_version:
                raise ValueError(f"Version {version} already exists for task {task_id}")
            
            # Get file information
            file_size = 0
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
            
            # Create version info
            now = datetime.now().isoformat()
            version_info = VersionInfo(
                version=version,
                version_number=self.parse_version_string(version)[0],
                status=VersionStatus.WIP,
                author=author,
                created_date=now,
                modified_date=now,
                description=description,
                file_path=file_path,
                file_size=file_size,
                is_locked=False,
                parent_version=self.get_latest_version(task_id),
                metadata=metadata or {}
            )
            
            # Store version in database
            version_record = {
                '_id': f"{task_id}_{version}",
                'task_id': task_id,
                'version': version,
                'version_number': version_info.version_number,
                'status': version_info.status.value,
                'author': author,
                'created_date': now,
                'modified_date': now,
                'description': description,
                'file_path': file_path,
                'file_size': file_size,
                'is_locked': False,
                'parent_version': version_info.parent_version,
                'metadata': metadata or {}
            }
            
            # Create versions collection if it doesn't exist
            self.db.insert_one('versions', version_record)
            
            # Update task's current version
            self.update_task_current_version(task_id, version)
            
            print(f"Created version {version} for task {task_id}")
            return version_info
            
        except Exception as e:
            print(f"Error creating version: {e}")
            return None
    
    def get_task_versions(self, task_id: str) -> List[VersionInfo]:
        """
        Get all versions for a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            List of VersionInfo objects sorted by version number
        """
        try:
            version_records = self.db.find('versions', {'task_id': task_id})
            
            versions = []
            for record in version_records:
                version_info = VersionInfo(
                    version=record['version'],
                    version_number=record['version_number'],
                    status=VersionStatus(record['status']),
                    author=record['author'],
                    created_date=record['created_date'],
                    modified_date=record['modified_date'],
                    description=record['description'],
                    file_path=record['file_path'],
                    file_size=record['file_size'],
                    is_locked=record['is_locked'],
                    parent_version=record.get('parent_version'),
                    metadata=record.get('metadata', {})
                )
                versions.append(version_info)
            
            # Sort by version number
            versions.sort(key=lambda v: v.version_number)
            return versions
            
        except Exception as e:
            print(f"Error getting task versions: {e}")
            return []
    
    def get_version_info(self, task_id: str, version: str) -> Optional[VersionInfo]:
        """
        Get information for a specific version.
        
        Args:
            task_id: Task identifier
            version: Version string
            
        Returns:
            VersionInfo object if found, None otherwise
        """
        try:
            record = self.db.find_one('versions', {'task_id': task_id, 'version': version})
            if not record:
                return None
            
            return VersionInfo(
                version=record['version'],
                version_number=record['version_number'],
                status=VersionStatus(record['status']),
                author=record['author'],
                created_date=record['created_date'],
                modified_date=record['modified_date'],
                description=record['description'],
                file_path=record['file_path'],
                file_size=record['file_size'],
                is_locked=record['is_locked'],
                parent_version=record.get('parent_version'),
                metadata=record.get('metadata', {})
            )
            
        except Exception as e:
            print(f"Error getting version info: {e}")
            return None

    def get_latest_version(self, task_id: str) -> Optional[str]:
        """
        Get the latest version string for a task.

        Args:
            task_id: Task identifier

        Returns:
            Latest version string or None if no versions exist
        """
        versions = self.get_task_versions(task_id)
        if not versions:
            return None

        # Return the highest version number
        latest = max(versions, key=lambda v: v.version_number)
        return latest.version

    def get_published_version(self, task_id: str) -> Optional[str]:
        """
        Get the latest published version for a task.

        Args:
            task_id: Task identifier

        Returns:
            Latest published version string or None
        """
        versions = self.get_task_versions(task_id)
        published_versions = [v for v in versions if v.status == VersionStatus.PUBLISHED]

        if not published_versions:
            return None

        # Return the highest published version
        latest_published = max(published_versions, key=lambda v: v.version_number)
        return latest_published.version

    def publish_version(self, task_id: str, version: str, publisher: str,
                       notes: str = "") -> bool:
        """
        Publish a version (mark as published and optionally lock).

        Args:
            task_id: Task identifier
            version: Version to publish
            publisher: User publishing the version
            notes: Publication notes

        Returns:
            True if successful, False otherwise
        """
        try:
            version_info = self.get_version_info(task_id, version)
            if not version_info:
                print(f"Version {version} not found for task {task_id}")
                return False

            if version_info.is_locked:
                print(f"Version {version} is already locked")
                return False

            # Get project settings to check if we should lock on publish
            task = self.db.find_one('tasks', {'_id': task_id})
            project_id = task.get('project') if task else None
            settings = self.get_project_version_settings(project_id)
            lock_on_publish = settings.get('lock_on_publish', True)

            # Update version status and metadata
            update_data = {
                'status': VersionStatus.PUBLISHED.value,
                'modified_date': datetime.now().isoformat(),
                'is_locked': lock_on_publish,
                'metadata.publisher': publisher,
                'metadata.published_date': datetime.now().isoformat(),
                'metadata.publication_notes': notes
            }

            success = self.db.update_one(
                'versions',
                {'task_id': task_id, 'version': version},
                {'$set': update_data}
            )

            if success:
                # Update task's published version
                self.update_task_published_version(task_id, version)
                print(f"Published version {version} for task {task_id}")
                return True

            return False

        except Exception as e:
            print(f"Error publishing version: {e}")
            return False

    def lock_version(self, task_id: str, version: str, locker: str,
                    reason: str = "") -> bool:
        """
        Lock a version to prevent modifications.

        Args:
            task_id: Task identifier
            version: Version to lock
            locker: User locking the version
            reason: Reason for locking

        Returns:
            True if successful, False otherwise
        """
        try:
            version_info = self.get_version_info(task_id, version)
            if not version_info:
                print(f"Version {version} not found for task {task_id}")
                return False

            if version_info.is_locked:
                print(f"Version {version} is already locked")
                return True

            # Update version lock status
            update_data = {
                'is_locked': True,
                'modified_date': datetime.now().isoformat(),
                'metadata.locker': locker,
                'metadata.locked_date': datetime.now().isoformat(),
                'metadata.lock_reason': reason
            }

            success = self.db.update_one(
                'versions',
                {'task_id': task_id, 'version': version},
                {'$set': update_data}
            )

            if success:
                print(f"Locked version {version} for task {task_id}")
                return True

            return False

        except Exception as e:
            print(f"Error locking version: {e}")
            return False

    def unlock_version(self, task_id: str, version: str, unlocker: str,
                      reason: str = "") -> bool:
        """
        Unlock a version to allow modifications.

        Args:
            task_id: Task identifier
            version: Version to unlock
            unlocker: User unlocking the version
            reason: Reason for unlocking

        Returns:
            True if successful, False otherwise
        """
        try:
            version_info = self.get_version_info(task_id, version)
            if not version_info:
                print(f"Version {version} not found for task {task_id}")
                return False

            if not version_info.is_locked:
                print(f"Version {version} is not locked")
                return True

            # Update version lock status
            update_data = {
                'is_locked': False,
                'modified_date': datetime.now().isoformat(),
                'metadata.unlocker': unlocker,
                'metadata.unlocked_date': datetime.now().isoformat(),
                'metadata.unlock_reason': reason
            }

            success = self.db.update_one(
                'versions',
                {'task_id': task_id, 'version': version},
                {'$set': update_data}
            )

            if success:
                print(f"Unlocked version {version} for task {task_id}")
                return True

            return False

        except Exception as e:
            print(f"Error unlocking version: {e}")
            return False

    def update_version_status(self, task_id: str, version: str,
                             status: VersionStatus, updater: str,
                             notes: str = "") -> bool:
        """
        Update version status.

        Args:
            task_id: Task identifier
            version: Version to update
            status: New status
            updater: User making the update
            notes: Update notes

        Returns:
            True if successful, False otherwise
        """
        try:
            version_info = self.get_version_info(task_id, version)
            if not version_info:
                print(f"Version {version} not found for task {task_id}")
                return False

            if version_info.is_locked and status != VersionStatus.PUBLISHED:
                print(f"Cannot update locked version {version}")
                return False

            # Update version status
            update_data = {
                'status': status.value,
                'modified_date': datetime.now().isoformat(),
                'metadata.status_updater': updater,
                'metadata.status_updated_date': datetime.now().isoformat(),
                'metadata.status_notes': notes
            }

            success = self.db.update_one(
                'versions',
                {'task_id': task_id, 'version': version},
                {'$set': update_data}
            )

            if success:
                print(f"Updated version {version} status to {status.value}")
                return True

            return False

        except Exception as e:
            print(f"Error updating version status: {e}")
            return False

    def update_task_current_version(self, task_id: str, version: str) -> bool:
        """Update task's current version field."""
        try:
            return self.db.update_one(
                'tasks',
                {'_id': task_id},
                {'$set': {
                    'current_version': version,
                    '_updated_at': datetime.now().isoformat()
                }}
            )
        except Exception as e:
            print(f"Error updating task current version: {e}")
            return False

    def update_task_published_version(self, task_id: str, version: str) -> bool:
        """Update task's published version field."""
        try:
            return self.db.update_one(
                'tasks',
                {'_id': task_id},
                {'$set': {
                    'published_version': version,
                    '_updated_at': datetime.now().isoformat()
                }}
            )
        except Exception as e:
            print(f"Error updating task published version: {e}")
            return False

    def get_version_history(self, task_id: str) -> List[Dict[str, Any]]:
        """
        Get version history with change tracking.

        Args:
            task_id: Task identifier

        Returns:
            List of version history entries
        """
        try:
            versions = self.get_task_versions(task_id)
            history = []

            for version in versions:
                entry = {
                    'version': version.version,
                    'status': version.status.value,
                    'author': version.author,
                    'created_date': version.created_date,
                    'modified_date': version.modified_date,
                    'description': version.description,
                    'file_size': version.file_size,
                    'is_locked': version.is_locked,
                    'parent_version': version.parent_version,
                    'metadata': version.metadata
                }
                history.append(entry)

            return history

        except Exception as e:
            print(f"Error getting version history: {e}")
            return []

    def compare_versions(self, task_id: str, version1: str, version2: str) -> Dict[str, Any]:
        """
        Compare two versions and return differences.

        Args:
            task_id: Task identifier
            version1: First version to compare
            version2: Second version to compare

        Returns:
            Dictionary containing comparison results
        """
        try:
            v1_info = self.get_version_info(task_id, version1)
            v2_info = self.get_version_info(task_id, version2)

            if not v1_info or not v2_info:
                return {'error': 'One or both versions not found'}

            comparison = {
                'task_id': task_id,
                'version1': {
                    'version': v1_info.version,
                    'status': v1_info.status.value,
                    'author': v1_info.author,
                    'created_date': v1_info.created_date,
                    'file_size': v1_info.file_size,
                    'description': v1_info.description
                },
                'version2': {
                    'version': v2_info.version,
                    'status': v2_info.status.value,
                    'author': v2_info.author,
                    'created_date': v2_info.created_date,
                    'file_size': v2_info.file_size,
                    'description': v2_info.description
                },
                'differences': {
                    'status_changed': v1_info.status != v2_info.status,
                    'author_changed': v1_info.author != v2_info.author,
                    'size_changed': v1_info.file_size != v2_info.file_size,
                    'size_difference': v2_info.file_size - v1_info.file_size,
                    'description_changed': v1_info.description != v2_info.description
                }
            }

            return comparison

        except Exception as e:
            print(f"Error comparing versions: {e}")
            return {'error': str(e)}

    def archive_version(self, task_id: str, version: str, archiver: str,
                       reason: str = "") -> bool:
        """
        Archive a version (mark as archived but keep in database).

        Args:
            task_id: Task identifier
            version: Version to archive
            archiver: User archiving the version
            reason: Reason for archiving

        Returns:
            True if successful, False otherwise
        """
        return self.update_version_status(
            task_id, version, VersionStatus.ARCHIVED, archiver, reason
        )

    def delete_version(self, task_id: str, version: str, deleter: str,
                      force: bool = False) -> bool:
        """
        Delete a version from the database.

        Args:
            task_id: Task identifier
            version: Version to delete
            deleter: User deleting the version
            force: Force deletion even if locked

        Returns:
            True if successful, False otherwise
        """
        try:
            version_info = self.get_version_info(task_id, version)
            if not version_info:
                print(f"Version {version} not found for task {task_id}")
                return False

            if version_info.is_locked and not force:
                print(f"Cannot delete locked version {version}")
                return False

            if version_info.status == VersionStatus.PUBLISHED and not force:
                print(f"Cannot delete published version {version}")
                return False

            # Remove version from database
            success = self.db.delete_one('versions', {'task_id': task_id, 'version': version})

            if success:
                print(f"Deleted version {version} for task {task_id}")

                # Update task current version if this was the current version
                task = self.db.find_one('tasks', {'_id': task_id})
                if task and task.get('current_version') == version:
                    # Set to latest remaining version
                    latest = self.get_latest_version(task_id)
                    if latest:
                        self.update_task_current_version(task_id, latest)
                    else:
                        self.update_task_current_version(task_id, "v000")

                return True

            return False

        except Exception as e:
            print(f"Error deleting version: {e}")
            return False

    def get_version_statistics(self, task_id: str = None, project_id: str = None) -> Dict[str, Any]:
        """
        Get version statistics for a task or project.

        Args:
            task_id: Task identifier (optional)
            project_id: Project identifier (optional)

        Returns:
            Dictionary containing version statistics
        """
        try:
            query = {}
            if task_id:
                query['task_id'] = task_id
            elif project_id:
                # Get all tasks for project
                tasks = self.db.find('tasks', {'project': project_id})
                task_ids = [task['_id'] for task in tasks]
                query['task_id'] = {'$in': task_ids}

            versions = self.db.find('versions', query)

            stats = {
                'total_versions': len(versions),
                'status_breakdown': {},
                'authors': set(),
                'total_file_size': 0,
                'locked_versions': 0,
                'published_versions': 0,
                'latest_version_date': None,
                'oldest_version_date': None
            }

            for version in versions:
                # Status breakdown
                status = version.get('status', 'unknown')
                stats['status_breakdown'][status] = stats['status_breakdown'].get(status, 0) + 1

                # Authors
                stats['authors'].add(version.get('author', 'Unknown'))

                # File size
                stats['total_file_size'] += version.get('file_size', 0)

                # Locked versions
                if version.get('is_locked', False):
                    stats['locked_versions'] += 1

                # Published versions
                if status == VersionStatus.PUBLISHED.value:
                    stats['published_versions'] += 1

                # Date tracking
                created_date = version.get('created_date')
                if created_date:
                    if not stats['oldest_version_date'] or created_date < stats['oldest_version_date']:
                        stats['oldest_version_date'] = created_date
                    if not stats['latest_version_date'] or created_date > stats['latest_version_date']:
                        stats['latest_version_date'] = created_date

            # Convert authors set to list
            stats['authors'] = list(stats['authors'])
            stats['unique_authors'] = len(stats['authors'])

            return stats

        except Exception as e:
            print(f"Error getting version statistics: {e}")
            return {}

    def cleanup_old_versions(self, task_id: str, keep_count: int = 5,
                           keep_published: bool = True) -> int:
        """
        Clean up old versions, keeping only the most recent ones.

        Args:
            task_id: Task identifier
            keep_count: Number of recent versions to keep
            keep_published: Whether to always keep published versions

        Returns:
            Number of versions cleaned up
        """
        try:
            versions = self.get_task_versions(task_id)
            if len(versions) <= keep_count:
                return 0

            # Sort by version number (newest first)
            versions.sort(key=lambda v: v.version_number, reverse=True)

            # Determine which versions to keep
            keep_versions = set()

            # Keep the most recent versions
            for i in range(min(keep_count, len(versions))):
                keep_versions.add(versions[i].version)

            # Keep published versions if requested
            if keep_published:
                for version in versions:
                    if version.status == VersionStatus.PUBLISHED:
                        keep_versions.add(version.version)

            # Delete versions not in keep list
            deleted_count = 0
            for version in versions:
                if version.version not in keep_versions and not version.is_locked:
                    if self.delete_version(task_id, version.version, "system_cleanup", force=False):
                        deleted_count += 1

            print(f"Cleaned up {deleted_count} old versions for task {task_id}")
            return deleted_count

        except Exception as e:
            print(f"Error cleaning up versions: {e}")
            return 0
