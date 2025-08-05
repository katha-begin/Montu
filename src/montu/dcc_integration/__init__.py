"""
DCC Integration Suite

Plugin system for Maya, Nuke, and other DCCs with embedded UI panels,
file operations, and version management for the Montu Manager ecosystem.
"""

__version__ = "1.0.0"
__author__ = "Montu Manager Development Team"

# Import only available modules to prevent import errors
__all__ = []

# Try to import base integration
try:
    from .base_integration import BaseDCCIntegration
    __all__.append('BaseDCCIntegration')
except ImportError:
    pass

# Try to import Maya integration
try:
    from .maya_integration import MayaIntegration
    __all__.append('MayaIntegration')
except ImportError:
    pass

# Try to import Nuke integration
try:
    from .nuke_integration import NukeIntegration
    __all__.append('NukeIntegration')
except ImportError:
    pass
