"""
Backward compatibility wrapper for JSONDatabase
DEPRECATED: Use montu.core.data.database instead

This module is deprecated and will be removed in a future version.
Please update your imports to use montu.core.data.database.JSONDatabase instead.
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "montu.shared.json_database is deprecated. Use montu.core.data.database instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import from new location
from montu.core.data.database import JSONDatabase

__all__ = ["JSONDatabase"]