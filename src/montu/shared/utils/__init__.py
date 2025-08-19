"""
Montu Manager Shared Utilities

Utility functions and classes shared across Montu Manager applications.
"""

from .platform import (
    PlatformManager, PlatformType, platform_manager,
    get_platform_type, normalize_path, map_drive_path,
    is_windows, is_linux, is_macos
)

__all__ = [
    'PlatformManager',
    'PlatformType',
    'platform_manager',
    'get_platform_type',
    'normalize_path',
    'map_drive_path',
    'is_windows',
    'is_linux',
    'is_macos'
]
