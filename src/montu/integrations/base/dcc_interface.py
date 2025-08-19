"""
Base DCC Interface

Abstract base class defining the interface for all DCC integrations.
Provides a unified API for interacting with different DCC applications.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class DCCType(Enum):
    """Supported DCC application types."""
    MAYA = "maya"
    NUKE = "nuke"
    HOUDINI = "houdini"
    BLENDER = "blender"
    UNKNOWN = "unknown"


class FileStatus(Enum):
    """File status enumeration."""
    NEW = "new"
    MODIFIED = "modified"
    SAVED = "saved"
    PUBLISHED = "published"


@dataclass
class SceneInfo:
    """Information about the current scene/file."""
    file_path: Optional[Path]
    file_name: str
    is_saved: bool
    is_modified: bool
    version: str
    task_id: Optional[str] = None
    project: Optional[str] = None


@dataclass
class VersionInfo:
    """Version information for files."""
    version: str
    file_path: Path
    created_by: str
    created_at: str
    comment: str
    status: FileStatus


class DCCInterface(ABC):
    """
    Abstract base class for DCC integrations.
    
    This class defines the standard interface that all DCC integrations
    must implement to work with the Montu Manager pipeline.
    """
    
    def __init__(self, dcc_type: DCCType):
        """
        Initialize DCC interface.
        
        Args:
            dcc_type: Type of DCC application
        """
        self.dcc_type = dcc_type
        self._is_connected = False
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to DCC application."""
        return self._is_connected
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to the DCC application.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from the DCC application.
        
        Returns:
            True if disconnection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_scene_info(self) -> SceneInfo:
        """
        Get information about the current scene/file.
        
        Returns:
            SceneInfo object with current scene details
        """
        pass
    
    @abstractmethod
    def open_file(self, file_path: Path) -> bool:
        """
        Open a file in the DCC application.
        
        Args:
            file_path: Path to file to open
            
        Returns:
            True if file opened successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def save_file(self, file_path: Optional[Path] = None) -> bool:
        """
        Save the current file.
        
        Args:
            file_path: Optional path to save to (uses current if None)
            
        Returns:
            True if file saved successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def save_as(self, file_path: Path) -> bool:
        """
        Save the current file with a new name/location.
        
        Args:
            file_path: Path to save file to
            
        Returns:
            True if file saved successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def new_file(self) -> bool:
        """
        Create a new file/scene.
        
        Returns:
            True if new file created successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def import_file(self, file_path: Path, **kwargs) -> bool:
        """
        Import a file into the current scene.
        
        Args:
            file_path: Path to file to import
            **kwargs: DCC-specific import options
            
        Returns:
            True if import successful, False otherwise
        """
        pass
    
    @abstractmethod
    def export_selection(self, file_path: Path, **kwargs) -> bool:
        """
        Export selected objects/elements to file.
        
        Args:
            file_path: Path to export to
            **kwargs: DCC-specific export options
            
        Returns:
            True if export successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_version_info(self, file_path: Path) -> Optional[VersionInfo]:
        """
        Get version information for a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            VersionInfo object or None if not found
        """
        pass
    
    @abstractmethod
    def create_version(self, comment: str = "") -> Optional[VersionInfo]:
        """
        Create a new version of the current file.
        
        Args:
            comment: Version comment
            
        Returns:
            VersionInfo object for new version or None if failed
        """
        pass
    
    @abstractmethod
    def publish_version(self, version: str, comment: str = "") -> bool:
        """
        Publish a specific version.
        
        Args:
            version: Version to publish
            comment: Publish comment
            
        Returns:
            True if publish successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_available_versions(self, file_path: Path) -> List[VersionInfo]:
        """
        Get list of available versions for a file.
        
        Args:
            file_path: Base file path
            
        Returns:
            List of VersionInfo objects
        """
        pass
    
    @abstractmethod
    def execute_command(self, command: str) -> Any:
        """
        Execute a DCC-specific command.
        
        Args:
            command: Command to execute
            
        Returns:
            Command result
        """
        pass
    
    @abstractmethod
    def get_selection(self) -> List[str]:
        """
        Get currently selected objects/elements.
        
        Returns:
            List of selected object names
        """
        pass
    
    @abstractmethod
    def set_selection(self, objects: List[str]) -> bool:
        """
        Set selection to specified objects/elements.
        
        Args:
            objects: List of object names to select
            
        Returns:
            True if selection successful, False otherwise
        """
        pass
    
    def get_dcc_version(self) -> str:
        """
        Get DCC application version.
        
        Returns:
            Version string
        """
        return "Unknown"
    
    def is_file_modified(self) -> bool:
        """
        Check if current file has unsaved modifications.
        
        Returns:
            True if file is modified, False otherwise
        """
        scene_info = self.get_scene_info()
        return scene_info.is_modified
    
    def validate_file_path(self, file_path: Path) -> bool:
        """
        Validate that a file path is appropriate for this DCC.
        
        Args:
            file_path: Path to validate
            
        Returns:
            True if path is valid, False otherwise
        """
        return file_path.exists() and file_path.is_file()
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported file formats.
        
        Returns:
            List of file extensions (e.g., ['.ma', '.mb'])
        """
        return []
    
    def __str__(self) -> str:
        """String representation of DCC interface."""
        return f"{self.__class__.__name__}({self.dcc_type.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"{self.__class__.__name__}(dcc_type={self.dcc_type.value}, connected={self.is_connected})"


# Utility functions for DCC integration
def detect_dcc_environment() -> DCCType:
    """
    Detect which DCC environment we're running in.

    Returns:
        DCCType enum value
    """
    try:
        import maya.cmds
        return DCCType.MAYA
    except ImportError:
        pass

    try:
        import nuke
        return DCCType.NUKE
    except ImportError:
        pass

    try:
        import hou
        return DCCType.HOUDINI
    except ImportError:
        pass

    try:
        import bpy
        return DCCType.BLENDER
    except ImportError:
        pass

    return DCCType.UNKNOWN


def create_dcc_interface(dcc_type: Optional[DCCType] = None) -> Optional[DCCInterface]:
    """
    Factory function to create appropriate DCC interface.

    Args:
        dcc_type: Specific DCC type to create, or None to auto-detect

    Returns:
        DCCInterface instance or None if not supported
    """
    if dcc_type is None:
        dcc_type = detect_dcc_environment()

    if dcc_type == DCCType.MAYA:
        from ..maya.plugin import MayaInterface
        return MayaInterface()
    elif dcc_type == DCCType.NUKE:
        # Future: from ..nuke.plugin import NukeInterface
        # return NukeInterface()
        pass
    elif dcc_type == DCCType.HOUDINI:
        # Future: from ..houdini.plugin import HoudiniInterface
        # return HoudiniInterface()
        pass
    elif dcc_type == DCCType.BLENDER:
        # Future: from ..blender.plugin import BlenderInterface
        # return BlenderInterface()
        pass

    return None
