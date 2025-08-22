"""
Review Application

Media browser application for review workflows with playback, annotation tools,
and approval tracking for the Montu Manager ecosystem.

Modular Structure:
- gui/: User interface components and widgets
- core/: Core business logic, models, and services
- utils/: Application-specific utility functions
"""

__version__ = "1.0.0"
__author__ = "Montu Manager Development Team"

from .main import main
from .core import ReviewModel, ReviewMediaService
from .gui.main_window import ReviewAppMainWindow

__all__ = ['main', 'ReviewModel', 'ReviewMediaService', 'ReviewAppMainWindow']
