"""
Shared Components

Common utilities, database connections, path handling, version management,
and other shared functionality used across all Montu applications.
"""

from .json_database import JSONDatabase
from .path_builder import PathBuilder
from .version_manager import VersionManager, VersionStatus, VersionInfo
from .version_widget import VersionHistoryWidget, CreateVersionDialog

__version__ = "0.1.0"

__all__ = [
    'JSONDatabase',
    'PathBuilder',
    'VersionManager',
    'VersionStatus',
    'VersionInfo',
    'VersionHistoryWidget',
    'CreateVersionDialog'
]
