"""
Task Creator Application

CSV import tool for bulk task creation with data validation and batch processing.

Target Users: Pipeline TDs and supervisors

Modular Structure:
- gui/: User interface components and dialogs
- core/: Core business logic and data management
- utils/: Application-specific utility functions
"""

__version__ = "0.1.0"

# Import main components for convenience
from .core import DirectoryManager
from .gui.main_window import TaskCreatorMainWindow

__all__ = ['DirectoryManager', 'TaskCreatorMainWindow']
