"""
Project Model

Data model for project management operations including database integration,
path generation, and project configuration management.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from montu.shared.json_database import JSONDatabase
from montu.shared.path_builder import PathBuilder


class ProjectModel:
    """
    Data model for project operations in the Project Launcher.
    
    Handles database operations, path generation, and project configuration
    using the validated Phase 1 infrastructure.
    """
    
    def __init__(self):
        """Initialize project model with database and path generation."""
        self.db = JSONDatabase()
        self.current_project_id: Optional[str] = None
        self.current_project_config: Optional[Dict[str, Any]] = None
        self.path_builder: Optional[PathBuilder] = None
        self.tasks: List[Dict[str, Any]] = []
        
        # Load available projects
        self.available_projects = self._load_available_projects()
    
    def _load_available_projects(self) -> List[Dict[str, str]]:
        """Load available projects from database."""
        try:
            project_configs = self.db.find('project_configs', {})
            projects = []
            
            for config in project_configs:
                projects.append({
                    'id': config.get('_id', 'Unknown'),
                    'name': config.get('name', 'Unknown Project'),
                    'description': config.get('description', '')
                })
            
            return projects
            
        except Exception as e:
            print(f"Error loading projects: {e}")
            return []
    
    def get_available_projects(self) -> List[Dict[str, str]]:
        """Get list of available projects."""
        return self.available_projects
    
    def load_project(self, project_id: str) -> bool:
        """
        Load a project and initialize path generation.
        
        Args:
            project_id: Project identifier (e.g., 'SWA')
            
        Returns:
            True if project loaded successfully
        """
        try:
            # Load project configuration
            self.current_project_config = self.db.get_project_config(project_id)
            if not self.current_project_config:
                print(f"Project configuration not found: {project_id}")
                return False
            
            # Initialize path builder
            self.path_builder = self.db.get_path_builder(project_id)
            if not self.path_builder:
                print(f"Failed to initialize path builder for project: {project_id}")
                return False
            
            # Set current project
            self.current_project_id = project_id
            
            # Load project tasks
            self.tasks = self.db.find('tasks', {'project': project_id})
            
            print(f"Loaded project {project_id} with {len(self.tasks)} tasks")
            return True
            
        except Exception as e:
            print(f"Error loading project {project_id}: {e}")
            return False
    
    def get_current_project(self) -> Optional[Dict[str, Any]]:
        """Get current project information."""
        if not self.current_project_id or not self.current_project_config:
            return None
        
        return {
            'id': self.current_project_id,
            'name': self.current_project_config.get('name', 'Unknown'),
            'description': self.current_project_config.get('description', ''),
            'task_count': len(self.tasks)
        }
    
    def get_tasks(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get tasks for current project with optional filtering.
        
        Args:
            filters: Optional filters to apply (e.g., {'status': 'in_progress'})
            
        Returns:
            List of task dictionaries
        """
        if not self.current_project_id:
            return []
        
        tasks = self.tasks.copy()
        
        # Apply filters if provided
        if filters:
            filtered_tasks = []
            for task in tasks:
                match = True
                for key, value in filters.items():
                    if task.get(key) != value:
                        match = False
                        break
                if match:
                    filtered_tasks.append(task)
            tasks = filtered_tasks
        
        return tasks
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific task by ID."""
        for task in self.tasks:
            if task.get('_id') == task_id:
                return task
        return None
    
    def update_task_status(self, task_id: str, status: str) -> bool:
        """
        Update task status in database and local cache.
        
        Args:
            task_id: Task identifier
            status: New status value
            
        Returns:
            True if update successful
        """
        try:
            # Update in database
            success = self.db.update_one(
                'tasks', 
                {'_id': task_id}, 
                {'$set': {'status': status, '_updated_at': datetime.now().isoformat()}}
            )
            
            if success:
                # Update local cache
                for task in self.tasks:
                    if task.get('_id') == task_id:
                        task['status'] = status
                        task['_updated_at'] = datetime.now().isoformat()
                        break
                
                print(f"Updated task {task_id} status to {status}")
                return True
            else:
                print(f"Failed to update task {task_id} in database")
                return False
                
        except Exception as e:
            print(f"Error updating task status: {e}")
            return False

    def update_task_priority(self, task_id: str, priority: str) -> bool:
        """
        Update task priority in database and local cache.

        Args:
            task_id: Task identifier
            priority: New priority value (low, medium, high, urgent)

        Returns:
            True if update successful
        """
        try:
            # Update in database
            success = self.db.update_one(
                'tasks',
                {'_id': task_id},
                {'$set': {'priority': priority, '_updated_at': datetime.now().isoformat()}}
            )

            if success:
                # Update local cache
                for task in self.tasks:
                    if task.get('_id') == task_id:
                        task['priority'] = priority
                        task['_updated_at'] = datetime.now().isoformat()
                        break

                print(f"Updated task {task_id} priority to {priority}")
                return True
            else:
                print(f"Failed to update task {task_id} priority in database")
                return False

        except Exception as e:
            print(f"Error updating task priority: {e}")
            return False

    def generate_task_paths(self, task_id: str, version: str = "001",
                           file_type: str = "maya_scene") -> Optional[Dict[str, str]]:
        """
        Generate all paths for a task using the PathBuilder Engine.
        
        Args:
            task_id: Task identifier
            version: Version string (e.g., "003")
            file_type: File type for filename pattern
            
        Returns:
            Dictionary with generated paths or None if failed
        """
        if not self.path_builder:
            print("Path builder not initialized")
            return None
        
        try:
            return self.db.generate_task_paths(task_id, version, file_type)
            
        except Exception as e:
            print(f"Error generating paths for task {task_id}: {e}")
            return None
    
    def get_working_file_path(self, task_id: str, version: str = "001") -> Optional[str]:
        """
        Get working file path for a task.
        
        Args:
            task_id: Task identifier
            version: Version string
            
        Returns:
            Working file path or None if failed
        """
        task = self.get_task_by_id(task_id)
        if not task:
            return None
        
        # Determine file type based on task
        file_type_map = {
            'lighting': 'maya_scene',
            'composite': 'nuke_script',
            'comp': 'nuke_script',
            'fx': 'houdini_scene',
            'modeling': 'maya_scene',
            'rigging': 'maya_scene',
            'animation': 'maya_scene',
            'layout': 'maya_scene',
            'lookdev': 'maya_scene'
        }
        
        task_type = task.get('task', '').lower()
        file_type = file_type_map.get(task_type, 'maya_scene')
        
        paths = self.generate_task_paths(task_id, version, file_type)
        return paths['working_file_path'] if paths else None
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for current project."""
        try:
            stats = self.db.get_stats()
            
            # Add project-specific stats
            if self.current_project_id:
                project_tasks = len(self.tasks)
                status_counts = {}
                
                for task in self.tasks:
                    status = task.get('status', 'unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                stats['current_project'] = {
                    'id': self.current_project_id,
                    'task_count': project_tasks,
                    'status_breakdown': status_counts
                }
            
            return stats
            
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {}
    
    def refresh_tasks(self) -> bool:
        """Refresh task list from database."""
        if not self.current_project_id:
            return False
        
        try:
            self.tasks = self.db.find('tasks', {'project': self.current_project_id})
            print(f"Refreshed {len(self.tasks)} tasks for project {self.current_project_id}")
            return True
            
        except Exception as e:
            print(f"Error refreshing tasks: {e}")
            return False
