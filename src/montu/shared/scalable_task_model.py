"""
Backward compatibility wrapper for ScalableTaskModel
DEPRECATED: Use montu.shared.ui.models instead

This module is deprecated and will be removed in a future version.
Please update your imports to use montu.shared.ui.models.ScalableTaskModel instead.
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "montu.shared.scalable_task_model is deprecated. Use montu.shared.ui.models instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import from new location
from .ui.models import ScalableTaskModel

__all__ = ["ScalableTaskModel"]