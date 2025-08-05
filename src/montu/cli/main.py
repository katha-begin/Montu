#!/usr/bin/env python3
"""
Montu Manager CLI Main

Command-line interface for batch operations and pipeline integration.
Provides commands for task management, project operations, and media handling.
"""

import sys
import argparse
from pathlib import Path
from typing import List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .commands import TaskCommands, ProjectCommands, MediaCommands


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog='montu',
        description='Montu Manager CLI - VFX/Animation Pipeline Management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  montu project list                    # List all projects
  montu project info SWA                # Show project information
  
  montu task list --project SWA         # List tasks for project
  montu task create --csv tasks.csv     # Create tasks from CSV
  montu task update TASK_ID --status completed
  
  montu media list --project SWA        # List media files
  montu media upload file.mov --task TASK_ID
  
For more help on a specific command, use:
  montu <command> --help
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Montu Manager CLI v1.0.0'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    # Create subparsers for different command groups
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        metavar='COMMAND'
    )
    
    # Project commands
    project_parser = subparsers.add_parser(
        'project',
        help='Project management commands'
    )
    ProjectCommands.setup_parser(project_parser)
    
    # Task commands
    task_parser = subparsers.add_parser(
        'task',
        help='Task management commands'
    )
    TaskCommands.setup_parser(task_parser)
    
    # Media commands
    media_parser = subparsers.add_parser(
        'media',
        help='Media file management commands'
    )
    MediaCommands.setup_parser(media_parser)
    
    return parser


def main(args: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    
    # Parse arguments
    if args is None:
        args = sys.argv[1:]
    
    parsed_args = parser.parse_args(args)
    
    # Set up verbose logging if requested
    if getattr(parsed_args, 'verbose', False):
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # Handle no command provided
    if not parsed_args.command:
        parser.print_help()
        return 0
    
    try:
        # Route to appropriate command handler
        if parsed_args.command == 'project':
            return ProjectCommands.handle(parsed_args)
        elif parsed_args.command == 'task':
            return TaskCommands.handle(parsed_args)
        elif parsed_args.command == 'media':
            return MediaCommands.handle(parsed_args)
        else:
            print(f"Unknown command: {parsed_args.command}")
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 130
    except Exception as e:
        print(f"❌ Error: {e}")
        if getattr(parsed_args, 'verbose', False):
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
