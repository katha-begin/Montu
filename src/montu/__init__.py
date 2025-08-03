"""
Montu Manager Ecosystem

A comprehensive DCC-agnostic file, task, and media management system
consisting of four integrated applications:

1. Project Launcher - Standalone desktop application for project management
2. Task Creator - CSV import tool for bulk task creation
3. DCC Integration Suite - Plugin system for Maya, Nuke, and other DCCs
4. Review Application - Media browser for review and approval workflows

All applications share a common MongoDB backend and are designed to work
together seamlessly in VFX/animation production pipelines.
"""

__version__ = "0.1.0"
__author__ = "Montu Development Team"
__email__ = "dev@montu-manager.com"

# Application modules
from . import project_launcher
from . import task_creator
from . import dcc_integration
from . import review_app
from . import shared
from . import cli

__all__ = [
    "project_launcher",
    "task_creator", 
    "dcc_integration",
    "review_app",
    "shared",
    "cli",
]
