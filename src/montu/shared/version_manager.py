"""
Backward compatibility wrapper for VersionManager
DEPRECATED: Use montu.core.version.manager instead

This module is deprecated and will be removed in a future version.
Please update your imports to use montu.core.version.manager instead.
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "montu.shared.version_manager is deprecated. Use montu.core.version.manager instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import from new location
from montu.core.version.manager import VersionManager, VersionStatus, VersionInfo

__all__ = ["VersionManager", "VersionStatus", "VersionInfo"]