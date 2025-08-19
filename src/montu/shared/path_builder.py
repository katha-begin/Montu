"""
Backward compatibility wrapper for PathBuilder
DEPRECATED: Use montu.core.path.builder instead

This module is deprecated and will be removed in a future version.
Please update your imports to use montu.core.path.builder.PathBuilder instead.
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "montu.shared.path_builder is deprecated. Use montu.core.path.builder instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import from new location
from montu.core.path.builder import (
    PathBuilder,
    PathGenerationResult,
    TemplateProcessor
)

__all__ = ['PathBuilder', 'PathGenerationResult', 'TemplateProcessor']