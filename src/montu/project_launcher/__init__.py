"""
Project Launcher Application

Central project management and file operations application for the Montu Manager ecosystem.
Provides project navigation, task assignment, version control, and file operations.

Modular Structure:
- gui/: User interface components and widgets
- core/: Core business logic, models, and controllers
- utils/: Application-specific utility functions
"""

__version__ = "1.0.0"
__author__ = "Montu Manager Development Team"

from .main import main
from .core import ProjectModel, TaskListModel
from .gui.main_window import ProjectLauncherMainWindow

__all__ = ['main', 'ProjectModel', 'TaskListModel', 'ProjectLauncherMainWindow']
