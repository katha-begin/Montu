"""
Directory Manager for Task Creator

Handles automatic directory creation, preview, and undo functionality
for task import operations.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from montu.shared.path_builder import PathBuilder
from montu.shared.json_database import JSONDatabase


@dataclass
class DirectoryOperation:
    """Represents a directory operation for undo tracking."""
    operation_type: str  # 'create_dir', 'create_file'
    path: str
    timestamp: str
    task_id: str
    success: bool = True


@dataclass
class DirectoryPreview:
    """Preview information for directory creation."""
    task_id: str
    working_dir: str
    render_dir: str
    media_dir: str
    cache_dir: str
    estimated_size_mb: float = 0.1  # Estimated directory overhead


class DirectoryManager:
    """
    Manages directory creation, preview, and undo operations for Task Creator.
    
    Integrates with PathBuilder Engine to create directory structures
    based on project configuration templates.
    """
    
    def __init__(self, project_config: Dict[str, Any]):
        """
        Initialize Directory Manager.
        
        Args:
            project_config: Project configuration from database
        """
        self.project_config = project_config
        self.path_builder = PathBuilder(project_config)
        self.db = JSONDatabase()
        self.operations_log: List[DirectoryOperation] = []
    
    def generate_directory_preview(self, tasks: List[Any]) -> List[DirectoryPreview]:
        """
        Generate preview of directories that will be created.

        Args:
            tasks: List of TaskRecord objects

        Returns:
            List of DirectoryPreview objects
        """
        previews = []

        for task in tasks:
            try:
                # Generate base task directories (without version subdirectories)
                task_data = {
                    'task_id': task.task_id,
                    'project': getattr(task, 'project', 'Unknown'),
                    'episode': getattr(task, 'episode', 'Unknown'),
                    'sequence': getattr(task, 'sequence', 'Unknown'),
                    'shot': getattr(task, 'shot', 'Unknown'),
                    'task': getattr(task, 'task', 'Unknown')
                }
                base_paths = self.path_builder.generate_base_task_directories(task_data)

                preview = DirectoryPreview(
                    task_id=task.task_id,
                    working_dir=base_paths['working_base'],
                    render_dir=base_paths['render_base'],
                    media_dir=base_paths['media_base'],
                    cache_dir=base_paths['cache_base'],
                    estimated_size_mb=0.1
                )

                previews.append(preview)

            except Exception as e:
                print(f"Error generating preview for task {task.task_id}: {e}")
                continue

        return previews
    
    def create_directories_for_tasks(self, tasks: List[Any]) -> Tuple[int, int, List[str]]:
        """
        Create base task directories for all tasks (without version subdirectories).

        Version directories (v001, v002, etc.) will be created only when files are saved.

        Args:
            tasks: List of TaskRecord objects

        Returns:
            Tuple of (success_count, total_count, error_messages)
        """
        success_count = 0
        error_messages = []
        operation_id = datetime.now().isoformat()

        for task in tasks:
            try:
                # Generate base task directories (without version subdirectories)
                task_data = {
                    'task_id': task.task_id,
                    'project': getattr(task, 'project', 'Unknown'),
                    'episode': getattr(task, 'episode', 'Unknown'),
                    'sequence': getattr(task, 'sequence', 'Unknown'),
                    'shot': getattr(task, 'shot', 'Unknown'),
                    'task': getattr(task, 'task', 'Unknown')
                }
                base_paths = self.path_builder.generate_base_task_directories(task_data)

                # Create base directories only
                directories_to_create = [
                    base_paths['working_base'],
                    base_paths['render_base'],
                    base_paths['media_base'],
                    base_paths['cache_base']
                ]

                task_success = True
                for directory in directories_to_create:
                    try:
                        Path(directory).mkdir(parents=True, exist_ok=True)

                        # Log the operation for undo
                        operation = DirectoryOperation(
                            operation_type='create_dir',
                            path=directory,
                            timestamp=operation_id,
                            task_id=task.task_id,
                            success=True
                        )
                        self.operations_log.append(operation)

                    except Exception as e:
                        error_messages.append(f"Failed to create {directory}: {e}")
                        task_success = False

                if task_success:
                    success_count += 1

            except Exception as e:
                error_messages.append(f"Error processing task {task.task_id}: {e}")

        # Save operations log to database for persistence
        self._save_operations_log(operation_id)

        return success_count, len(tasks), error_messages
    
    def get_directory_tree_preview(self, tasks: List[Any]) -> Dict[str, List[str]]:
        """
        Generate a hierarchical directory tree preview for base task directories.

        Args:
            tasks: List of TaskRecord objects

        Returns:
            Dictionary with directory structure organized by root paths
        """
        tree = {}

        for task in tasks:
            try:
                task_data = {
                    'task_id': task.task_id,
                    'project': getattr(task, 'project', 'Unknown'),
                    'episode': getattr(task, 'episode', 'Unknown'),
                    'sequence': getattr(task, 'sequence', 'Unknown'),
                    'shot': getattr(task, 'shot', 'Unknown'),
                    'task': getattr(task, 'task', 'Unknown')
                }
                base_paths = self.path_builder.generate_base_task_directories(task_data)

                # Organize by root directory
                directories = [
                    base_paths['working_base'],
                    base_paths['render_base'],
                    base_paths['media_base'],
                    base_paths['cache_base']
                ]

                for directory in directories:
                    # Get the root drive/path
                    root = str(Path(directory).parts[0]) if Path(directory).parts else "Unknown"

                    if root not in tree:
                        tree[root] = []

                    if directory not in tree[root]:
                        tree[root].append(directory)

            except Exception as e:
                print(f"Error generating tree for task {task.task_id}: {e}")
                continue

        return tree
    
    def get_undo_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent operations that can be undone.
        
        Args:
            limit: Maximum number of operations to return
            
        Returns:
            List of operation summaries
        """
        # Group operations by timestamp
        operations_by_timestamp = {}
        for op in self.operations_log[-limit*50:]:  # Get more to group properly
            if op.timestamp not in operations_by_timestamp:
                operations_by_timestamp[op.timestamp] = []
            operations_by_timestamp[op.timestamp].append(op)
        
        # Create summaries
        summaries = []
        for timestamp, ops in sorted(operations_by_timestamp.items(), reverse=True)[:limit]:
            summary = {
                'timestamp': timestamp,
                'operation_count': len(ops),
                'task_count': len(set(op.task_id for op in ops)),
                'directories_created': len([op for op in ops if op.operation_type == 'create_dir']),
                'can_undo': all(op.success for op in ops)
            }
            summaries.append(summary)
        
        return summaries
    
    def undo_last_operation(self) -> Tuple[bool, str, int]:
        """
        Undo the last directory creation operation.
        
        Returns:
            Tuple of (success, message, directories_removed)
        """
        if not self.operations_log:
            return False, "No operations to undo", 0
        
        # Get the last timestamp
        last_timestamp = self.operations_log[-1].timestamp
        operations_to_undo = [op for op in self.operations_log if op.timestamp == last_timestamp]
        
        if not operations_to_undo:
            return False, "No operations found to undo", 0
        
        directories_removed = 0
        errors = []
        
        # Reverse the operations (remove directories)
        for operation in reversed(operations_to_undo):
            if operation.operation_type == 'create_dir':
                try:
                    directory_path = Path(operation.path)
                    if directory_path.exists() and directory_path.is_dir():
                        # Only remove if directory is empty or contains only our created structure
                        if self._is_safe_to_remove(directory_path):
                            shutil.rmtree(directory_path)
                            directories_removed += 1
                        else:
                            errors.append(f"Directory not empty, skipped: {directory_path}")
                except Exception as e:
                    errors.append(f"Failed to remove {operation.path}: {e}")
        
        # Remove operations from log
        self.operations_log = [op for op in self.operations_log if op.timestamp != last_timestamp]
        
        if errors:
            return True, f"Partially undone. Removed {directories_removed} directories. Errors: {'; '.join(errors)}", directories_removed
        else:
            return True, f"Successfully undone. Removed {directories_removed} directories.", directories_removed
    
    def _get_file_type_from_task(self, task_name: str) -> str:
        """Get file type based on task name."""
        task_lower = task_name.lower()
        
        if 'lighting' in task_lower:
            return 'maya_scene'
        elif 'comp' in task_lower:
            return 'nuke_script'
        elif 'fx' in task_lower:
            return 'houdini_scene'
        else:
            return 'maya_scene'  # Default
    
    def _save_operations_log(self, operation_id: str):
        """Save operations log to database for persistence."""
        try:
            # Convert operations to dictionaries
            operations_data = [asdict(op) for op in self.operations_log if op.timestamp == operation_id]
            
            log_record = {
                '_id': f"dir_ops_{operation_id}",
                'timestamp': operation_id,
                'operations': operations_data,
                'created_at': datetime.now().isoformat()
            }
            
            self.db.insert_one('directory_operations', log_record)
            
        except Exception as e:
            print(f"Failed to save operations log: {e}")
    
    def _is_safe_to_remove(self, directory_path: Path) -> bool:
        """Check if directory is safe to remove (empty or only contains our structure)."""
        try:
            if not directory_path.exists():
                return True
            
            # Check if directory is empty
            contents = list(directory_path.iterdir())
            if not contents:
                return True
            
            # Check if it only contains subdirectories we created (no files)
            for item in contents:
                if item.is_file():
                    return False  # Contains files, not safe to remove
            
            return True  # Only contains directories, safe to remove
            
        except Exception:
            return False  # If we can't check, don't remove
