"""
Montu Manager CLI Interface

Command-line interface for batch operations and pipeline integration.
"""

__version__ = "1.0.0"
__author__ = "Montu Manager Development Team"

from .main import main
from .commands import TaskCommands, ProjectCommands, MediaCommands

__all__ = ['main', 'TaskCommands', 'ProjectCommands', 'MediaCommands']
