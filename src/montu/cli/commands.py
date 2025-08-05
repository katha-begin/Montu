"""
CLI Commands

Command implementations for the Montu Manager CLI interface.
"""

import os
import sys
import json
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from montu.shared.json_database import JSONDatabase


class BaseCommands:
    """Base class for CLI command groups."""
    
    def __init__(self):
        self.db = JSONDatabase()
    
    @staticmethod
    def print_table(headers: List[str], rows: List[List[str]], max_width: int = 80):
        """Print a formatted table."""
        if not rows:
            print("No data to display")
            return
        
        # Calculate column widths
        col_widths = [len(header) for header in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Adjust for max width
        total_width = sum(col_widths) + len(headers) * 3 - 1
        if total_width > max_width:
            # Reduce the last column width
            col_widths[-1] = max(10, col_widths[-1] - (total_width - max_width))
        
        # Print header
        header_row = " | ".join(header.ljust(col_widths[i]) for i, header in enumerate(headers))
        print(header_row)
        print("-" * len(header_row))
        
        # Print rows
        for row in rows:
            formatted_row = []
            for i, cell in enumerate(row):
                cell_str = str(cell)
                if i < len(col_widths):
                    if len(cell_str) > col_widths[i]:
                        cell_str = cell_str[:col_widths[i]-3] + "..."
                    formatted_row.append(cell_str.ljust(col_widths[i]))
            print(" | ".join(formatted_row))


class ProjectCommands(BaseCommands):
    """Project management commands."""
    
    @staticmethod
    def setup_parser(parser):
        """Set up project command parser."""
        subparsers = parser.add_subparsers(dest='project_action', help='Project actions')
        
        # List projects
        list_parser = subparsers.add_parser('list', help='List all projects')
        list_parser.add_argument('--format', choices=['table', 'json'], default='table',
                               help='Output format')
        
        # Project info
        info_parser = subparsers.add_parser('info', help='Show project information')
        info_parser.add_argument('project_id', help='Project ID')
        info_parser.add_argument('--format', choices=['table', 'json'], default='table',
                               help='Output format')
        
        # Create project
        create_parser = subparsers.add_parser('create', help='Create new project')
        create_parser.add_argument('project_id', help='Project ID')
        create_parser.add_argument('--name', required=True, help='Project name')
        create_parser.add_argument('--config', help='Path to project config JSON file')
    
    @classmethod
    def handle(cls, args) -> int:
        """Handle project commands."""
        commands = cls()
        
        if args.project_action == 'list':
            return commands.list_projects(args)
        elif args.project_action == 'info':
            return commands.project_info(args)
        elif args.project_action == 'create':
            return commands.create_project(args)
        else:
            print("Unknown project action")
            return 1
    
    def list_projects(self, args) -> int:
        """List all projects."""
        try:
            projects = self.db.find('project_configs', {})
            
            if args.format == 'json':
                print(json.dumps(projects, indent=2))
                return 0
            
            if not projects:
                print("No projects found")
                return 0
            
            # Format as table
            headers = ['Project ID', 'Name', 'Created', 'Tasks']
            rows = []
            
            for project in projects:
                project_id = project.get('project_id', 'Unknown')
                name = project.get('name', 'Unknown')
                created = project.get('created_date', 'Unknown')
                
                # Count tasks for this project
                task_count = len(self.db.find('tasks', {'project': project_id}))
                
                rows.append([project_id, name, created, str(task_count)])
            
            self.print_table(headers, rows)
            print(f"\nTotal: {len(projects)} projects")
            return 0
            
        except Exception as e:
            print(f"Error listing projects: {e}")
            return 1
    
    def project_info(self, args) -> int:
        """Show detailed project information."""
        try:
            project = self.db.find_one('project_configs', {'project_id': args.project_id})
            
            if not project:
                print(f"Project '{args.project_id}' not found")
                return 1
            
            if args.format == 'json':
                print(json.dumps(project, indent=2))
                return 0
            
            # Format as readable info
            print(f"Project Information: {args.project_id}")
            print("=" * 50)
            print(f"Name: {project.get('name', 'Unknown')}")
            print(f"Created: {project.get('created_date', 'Unknown')}")
            print(f"Description: {project.get('description', 'No description')}")
            
            # Show path configuration
            paths = project.get('paths', {})
            if paths:
                print("\nPath Configuration:")
                for key, value in paths.items():
                    print(f"  {key}: {value}")
            
            # Show task statistics
            tasks = self.db.find('tasks', {'project': args.project_id})
            print(f"\nTasks: {len(tasks)} total")
            
            if tasks:
                # Count by status
                status_counts = {}
                for task in tasks:
                    status = task.get('status', 'unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                for status, count in status_counts.items():
                    print(f"  {status}: {count}")
            
            return 0
            
        except Exception as e:
            print(f"Error getting project info: {e}")
            return 1
    
    def create_project(self, args) -> int:
        """Create a new project."""
        try:
            # Check if project already exists
            existing = self.db.find_one('project_configs', {'project_id': args.project_id})
            if existing:
                print(f"Project '{args.project_id}' already exists")
                return 1
            
            # Create project config
            project_config = {
                'project_id': args.project_id,
                'name': args.name,
                'description': f"Project {args.name}",
                'created_date': datetime.now().isoformat(),
                'paths': {
                    'working_files': 'E:',
                    'render_output': 'E:',
                    'media_files': 'E:',
                    'cache_files': 'E:',
                    'backup_files': 'E:'
                },
                'path_templates': {
                    'working_file_path': '{working_files}/{project}/{episode}/{sequence}/{shot}/{task}/work/{shot}_{task}_v{version:03d}.ma',
                    'render_output_path': '{render_output}/{project}/{episode}/{sequence}/{shot}/{task}/render/v{version:03d}',
                    'media_file_path': '{media_files}/{project}/{episode}/{sequence}/{shot}/{task}/media/{shot}_{task}_v{version:03d}.mov',
                    'cache_file_path': '{cache_files}/{project}/{episode}/{sequence}/{shot}/{task}/cache/{shot}_{task}_v{version:03d}.abc'
                }
            }
            
            # Load additional config from file if provided
            if args.config and os.path.exists(args.config):
                with open(args.config, 'r') as f:
                    additional_config = json.load(f)
                    project_config.update(additional_config)
            
            # Insert into database
            result = self.db.insert_one('project_configs', project_config)
            
            if result:
                print(f"✅ Created project '{args.project_id}' successfully")
                return 0
            else:
                print(f"❌ Failed to create project '{args.project_id}'")
                return 1
                
        except Exception as e:
            print(f"Error creating project: {e}")
            return 1


class TaskCommands(BaseCommands):
    """Task management commands."""
    
    @staticmethod
    def setup_parser(parser):
        """Set up task command parser."""
        subparsers = parser.add_subparsers(dest='task_action', help='Task actions')
        
        # List tasks
        list_parser = subparsers.add_parser('list', help='List tasks')
        list_parser.add_argument('--project', help='Filter by project')
        list_parser.add_argument('--status', help='Filter by status')
        list_parser.add_argument('--format', choices=['table', 'json'], default='table')
        
        # Task info
        info_parser = subparsers.add_parser('info', help='Show task information')
        info_parser.add_argument('task_id', help='Task ID')
        
        # Update task
        update_parser = subparsers.add_parser('update', help='Update task')
        update_parser.add_argument('task_id', help='Task ID')
        update_parser.add_argument('--status', help='New status')
        update_parser.add_argument('--priority', help='New priority')
        
        # Create tasks from CSV
        create_parser = subparsers.add_parser('create', help='Create tasks from CSV')
        create_parser.add_argument('--csv', required=True, help='CSV file path')
        create_parser.add_argument('--project', required=True, help='Project ID')
    
    @classmethod
    def handle(cls, args) -> int:
        """Handle task commands."""
        commands = cls()
        
        if args.task_action == 'list':
            return commands.list_tasks(args)
        elif args.task_action == 'info':
            return commands.task_info(args)
        elif args.task_action == 'update':
            return commands.update_task(args)
        elif args.task_action == 'create':
            return commands.create_tasks_from_csv(args)
        else:
            print("Unknown task action")
            return 1
    
    def list_tasks(self, args) -> int:
        """List tasks with optional filtering."""
        try:
            # Build query
            query = {}
            if args.project:
                query['project'] = args.project
            if args.status:
                query['status'] = args.status
            
            tasks = self.db.find('tasks', query)
            
            if args.format == 'json':
                print(json.dumps(tasks, indent=2))
                return 0
            
            if not tasks:
                print("No tasks found")
                return 0
            
            # Format as table
            headers = ['Task ID', 'Shot', 'Task', 'Artist', 'Status', 'Priority']
            rows = []
            
            for task in tasks:
                task_id = task.get('_id', 'Unknown')
                shot = task.get('shot', 'Unknown')
                task_type = task.get('task', 'Unknown')
                artist = task.get('artist', 'Unassigned')
                status = task.get('status', 'unknown')
                priority = task.get('priority', 'medium')
                
                rows.append([task_id, shot, task_type, artist, status, priority])
            
            self.print_table(headers, rows)
            print(f"\nTotal: {len(tasks)} tasks")
            return 0
            
        except Exception as e:
            print(f"Error listing tasks: {e}")
            return 1
    
    def task_info(self, args) -> int:
        """Show detailed task information."""
        try:
            task = self.db.find_one('tasks', {'_id': args.task_id})
            
            if not task:
                print(f"Task '{args.task_id}' not found")
                return 1
            
            print(f"Task Information: {args.task_id}")
            print("=" * 50)
            
            for key, value in task.items():
                if key != '_id':
                    print(f"{key}: {value}")
            
            return 0
            
        except Exception as e:
            print(f"Error getting task info: {e}")
            return 1
    
    def update_task(self, args) -> int:
        """Update task properties."""
        try:
            # Build update data
            update_data = {}
            if args.status:
                update_data['status'] = args.status
            if args.priority:
                update_data['priority'] = args.priority
            
            if not update_data:
                print("No update data provided")
                return 1
            
            # Update task
            result = self.db.update_one(
                'tasks',
                {'_id': args.task_id},
                {'$set': update_data}
            )
            
            if result:
                print(f"✅ Updated task '{args.task_id}' successfully")
                return 0
            else:
                print(f"❌ Failed to update task '{args.task_id}' (task may not exist)")
                return 1
                
        except Exception as e:
            print(f"Error updating task: {e}")
            return 1
    
    def create_tasks_from_csv(self, args) -> int:
        """Create tasks from CSV file."""
        try:
            if not os.path.exists(args.csv):
                print(f"CSV file not found: {args.csv}")
                return 1
            
            # Import CSV parser
            from montu.task_creator.csv_parser import CSVParser
            
            parser = CSVParser()
            tasks = parser.parse_csv_file(Path(args.csv))
            
            if not tasks:
                print("No valid tasks found in CSV")
                return 1
            
            # Insert tasks into database
            success_count = 0
            for task in tasks:
                # Convert TaskRecord to dictionary
                task_dict = task.to_dict()
                result = self.db.insert_one('tasks', task_dict)
                if result:
                    success_count += 1
            
            print(f"✅ Created {success_count} tasks from CSV")
            if success_count < len(tasks):
                print(f"⚠️  {len(tasks) - success_count} tasks failed to create")
            
            return 0
            
        except Exception as e:
            print(f"Error creating tasks from CSV: {e}")
            return 1


class MediaCommands(BaseCommands):
    """Media file management commands."""
    
    @staticmethod
    def setup_parser(parser):
        """Set up media command parser."""
        subparsers = parser.add_subparsers(dest='media_action', help='Media actions')
        
        # List media
        list_parser = subparsers.add_parser('list', help='List media files')
        list_parser.add_argument('--project', help='Filter by project')
        list_parser.add_argument('--task', help='Filter by task ID')
        
        # Media info
        info_parser = subparsers.add_parser('info', help='Show media information')
        info_parser.add_argument('file_path', help='Media file path')
    
    @classmethod
    def handle(cls, args) -> int:
        """Handle media commands."""
        commands = cls()
        
        if args.media_action == 'list':
            return commands.list_media(args)
        elif args.media_action == 'info':
            return commands.media_info(args)
        else:
            print("Unknown media action")
            return 1
    
    def list_media(self, args) -> int:
        """List media files."""
        try:
            # Build query for tasks
            query = {}
            if args.project:
                query['project'] = args.project
            if args.task:
                query['_id'] = args.task
            
            tasks = self.db.find('tasks', query)
            
            if not tasks:
                print("No tasks found")
                return 0
            
            print("Media Files:")
            print("=" * 50)
            
            media_count = 0
            for task in tasks:
                task_id = task.get('_id', 'Unknown')
                
                # Generate media paths for this task
                paths = self.db.generate_task_paths(task_id, "001", "maya_scene")
                if paths:
                    media_path = paths.get('media_file_path', '')
                    if media_path:
                        print(f"Task: {task_id}")
                        print(f"  Media: {media_path}")
                        print(f"  Exists: {'Yes' if os.path.exists(media_path) else 'No'}")
                        print()
                        media_count += 1
            
            print(f"Total: {media_count} media files")
            return 0
            
        except Exception as e:
            print(f"Error listing media: {e}")
            return 1
    
    def media_info(self, args) -> int:
        """Show media file information."""
        try:
            file_path = args.file_path
            
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return 1
            
            # Get file stats
            stat = os.stat(file_path)
            file_size = stat.st_size
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            
            print(f"Media File Information: {os.path.basename(file_path)}")
            print("=" * 50)
            print(f"Path: {file_path}")
            print(f"Size: {file_size:,} bytes ({file_size / (1024*1024):.1f} MB)")
            print(f"Modified: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Extension: {os.path.splitext(file_path)[1]}")
            
            return 0
            
        except Exception as e:
            print(f"Error getting media info: {e}")
            return 1
