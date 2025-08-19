"""
Montu Manager Core Module

This module contains the core utilities and functionality that are shared
across all Montu Manager applications and can be used by external tools
and DCC integrations.

Core modules:
- path: Path generation and template processing
- data: Database operations and data models
- version: Version management and lifecycle
- media: Media file operations and storage
- project: Project configuration and validation
- task: Task management and utilities
"""

__version__ = "1.0.0"
__author__ = "Montu Manager Team"

# Core module imports for convenience
from .path.builder import PathBuilder
from .data.database import JSONDatabase
from .version.manager import VersionManager

__all__ = [
    'PathBuilder',
    'JSONDatabase', 
    'VersionManager'
]
