"""
Backward compatibility wrapper for CSVParser
DEPRECATED: Use montu.shared.parsers.csv_parser instead

This module is deprecated and will be removed in a future version.
Please update your imports to use montu.shared.parsers.csv_parser instead.
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "montu.task_creator.csv_parser is deprecated. Use montu.shared.parsers.csv_parser instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import from new location
from ..shared.parsers.csv_parser import CSVParser, NamingPattern, TaskRecord

__all__ = ["CSVParser", "NamingPattern", "TaskRecord"]