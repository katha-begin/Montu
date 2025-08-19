"""
Maya Integration Plugin for Montu Manager

Maya-specific implementation of the DCC interface providing scene management,
version control, and pipeline integration within Maya.
"""

from typing import List, Optional, Any
from pathlib import Path
import os
import re

from ..base.dcc_interface import (
    DCCInterface, DCCType, SceneInfo, VersionInfo, FileStatus
)


class MayaInterface(DCCInterface):
    """
    Maya-specific implementation of DCCInterface.
    
    Provides Maya scene management, version control, and pipeline integration.
    """
    
    def __init__(self):
        """Initialize Maya interface."""
        super().__init__(DCCType.MAYA)
        self._maya_cmds = None
        self._maya_mel = None
    
    def connect(self) -> bool:
        """
        Connect to Maya.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            import maya.cmds as cmds
            import maya.mel as mel
            self._maya_cmds = cmds
            self._maya_mel = mel
            self._is_connected = True
            return True
        except ImportError:
            self._is_connected = False
            return False
    
    def disconnect(self) -> bool:
        """
        Disconnect from Maya.
        
        Returns:
            True if disconnection successful, False otherwise
        """
        self._maya_cmds = None
        self._maya_mel = None
        self._is_connected = False
        return True
    
    def get_scene_info(self) -> SceneInfo:
        """
        Get information about the current Maya scene.
        
        Returns:
            SceneInfo object with current scene details
        """
        if not self.is_connected:
            return SceneInfo(
                file_path=None,
                file_name="untitled",
                is_saved=False,
                is_modified=False,
                version="v001"
            )
        
        # Get current file path
        current_file = self._maya_cmds.file(query=True, sceneName=True)
        file_path = Path(current_file) if current_file else None
        
        # Get file name
        file_name = file_path.name if file_path else "untitled"
        
        # Check if file is saved and modified
        is_saved = bool(current_file)
        is_modified = self._maya_cmds.file(query=True, modified=True)
        
        # Extract version from filename
        version = self._extract_version_from_filename(file_name)
        
        # Extract task ID and project from path
        task_id, project = self._extract_task_info_from_path(file_path)
        
        return SceneInfo(
            file_path=file_path,
            file_name=file_name,
            is_saved=is_saved,
            is_modified=is_modified,
            version=version,
            task_id=task_id,
            project=project
        )
    
    def open_file(self, file_path: Path) -> bool:
        """
        Open a Maya file.
        
        Args:
            file_path: Path to Maya file to open
            
        Returns:
            True if file opened successfully, False otherwise
        """
        if not self.is_connected:
            return False
        
        try:
            self._maya_cmds.file(str(file_path), open=True, force=True)
            return True
        except Exception as e:
            print(f"Error opening Maya file {file_path}: {e}")
            return False
    
    def save_file(self, file_path: Optional[Path] = None) -> bool:
        """
        Save the current Maya file.
        
        Args:
            file_path: Optional path to save to (uses current if None)
            
        Returns:
            True if file saved successfully, False otherwise
        """
        if not self.is_connected:
            return False
        
        try:
            if file_path:
                self._maya_cmds.file(rename=str(file_path))
            self._maya_cmds.file(save=True)
            return True
        except Exception as e:
            print(f"Error saving Maya file: {e}")
            return False
    
    def save_as(self, file_path: Path) -> bool:
        """
        Save the current Maya file with a new name/location.
        
        Args:
            file_path: Path to save file to
            
        Returns:
            True if file saved successfully, False otherwise
        """
        if not self.is_connected:
            return False
        
        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Determine file type based on extension
            file_type = "mayaAscii" if file_path.suffix == ".ma" else "mayaBinary"
            
            self._maya_cmds.file(str(file_path), save=True, type=file_type)
            return True
        except Exception as e:
            print(f"Error saving Maya file as {file_path}: {e}")
            return False
    
    def new_file(self) -> bool:
        """
        Create a new Maya scene.
        
        Returns:
            True if new file created successfully, False otherwise
        """
        if not self.is_connected:
            return False
        
        try:
            self._maya_cmds.file(new=True, force=True)
            return True
        except Exception as e:
            print(f"Error creating new Maya file: {e}")
            return False
    
    def import_file(self, file_path: Path, **kwargs) -> bool:
        """
        Import a file into the current Maya scene.
        
        Args:
            file_path: Path to file to import
            **kwargs: Maya-specific import options
            
        Returns:
            True if import successful, False otherwise
        """
        if not self.is_connected:
            return False
        
        try:
            # Default import options
            options = {
                'i': True,  # import
                'type': kwargs.get('type', 'mayaAscii'),
                'ignoreVersion': kwargs.get('ignoreVersion', True),
                'mergeNamespacesOnClash': kwargs.get('mergeNamespaces', False),
                'namespace': kwargs.get('namespace', ':'),
                'preserveReferences': kwargs.get('preserveReferences', True)
            }
            
            self._maya_cmds.file(str(file_path), **options)
            return True
        except Exception as e:
            print(f"Error importing Maya file {file_path}: {e}")
            return False
    
    def export_selection(self, file_path: Path, **kwargs) -> bool:
        """
        Export selected objects to file.
        
        Args:
            file_path: Path to export to
            **kwargs: Maya-specific export options
            
        Returns:
            True if export successful, False otherwise
        """
        if not self.is_connected:
            return False
        
        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Default export options
            file_type = "mayaAscii" if file_path.suffix == ".ma" else "mayaBinary"
            options = {
                'exportSelected': True,
                'type': kwargs.get('type', file_type),
                'preserveReferences': kwargs.get('preserveReferences', True),
                'channels': kwargs.get('channels', True),
                'constraints': kwargs.get('constraints', True),
                'expressions': kwargs.get('expressions', True),
                'constructionHistory': kwargs.get('constructionHistory', True)
            }
            
            self._maya_cmds.file(str(file_path), **options)
            return True
        except Exception as e:
            print(f"Error exporting Maya selection to {file_path}: {e}")
            return False
    
    def get_version_info(self, file_path: Path) -> Optional[VersionInfo]:
        """
        Get version information for a Maya file.
        
        Args:
            file_path: Path to Maya file
            
        Returns:
            VersionInfo object or None if not found
        """
        if not file_path.exists():
            return None
        
        # Extract version from filename
        version = self._extract_version_from_filename(file_path.name)
        
        # Get file stats
        stat = file_path.stat()
        
        return VersionInfo(
            version=version,
            file_path=file_path,
            created_by="Unknown",  # Could be enhanced to read from file metadata
            created_at=str(stat.st_mtime),
            comment="",
            status=FileStatus.SAVED
        )
    
    def create_version(self, comment: str = "") -> Optional[VersionInfo]:
        """
        Create a new version of the current Maya file.
        
        Args:
            comment: Version comment
            
        Returns:
            VersionInfo object for new version or None if failed
        """
        scene_info = self.get_scene_info()
        if not scene_info.file_path:
            return None
        
        # Generate next version number
        current_version = scene_info.version
        next_version = self._increment_version(current_version)
        
        # Create new version file path
        new_file_path = self._get_versioned_file_path(scene_info.file_path, next_version)
        
        # Save as new version
        if self.save_as(new_file_path):
            return VersionInfo(
                version=next_version,
                file_path=new_file_path,
                created_by=os.getenv('USERNAME', 'Unknown'),
                created_at=str(Path(new_file_path).stat().st_mtime),
                comment=comment,
                status=FileStatus.SAVED
            )
        
        return None
    
    def publish_version(self, version: str, comment: str = "") -> bool:
        """
        Publish a specific version (Maya-specific implementation).
        
        Args:
            version: Version to publish
            comment: Publish comment
            
        Returns:
            True if publish successful, False otherwise
        """
        # Maya-specific publish logic would go here
        # For now, just mark as published
        print(f"Publishing Maya version {version}: {comment}")
        return True
    
    def get_available_versions(self, file_path: Path) -> List[VersionInfo]:
        """
        Get list of available versions for a Maya file.
        
        Args:
            file_path: Base file path
            
        Returns:
            List of VersionInfo objects
        """
        versions = []
        
        # Look for version files in the same directory
        if file_path.parent.exists():
            base_name = file_path.stem
            extension = file_path.suffix
            
            # Find all version files
            for version_file in file_path.parent.glob(f"{base_name}_v*{extension}"):
                version_info = self.get_version_info(version_file)
                if version_info:
                    versions.append(version_info)
        
        return sorted(versions, key=lambda v: v.version)
    
    def execute_command(self, command: str) -> Any:
        """
        Execute a Maya command.
        
        Args:
            command: Maya command to execute
            
        Returns:
            Command result
        """
        if not self.is_connected:
            return None
        
        try:
            # Try MEL command first
            return self._maya_mel.eval(command)
        except:
            try:
                # Try as Python command
                return eval(command)
            except Exception as e:
                print(f"Error executing Maya command '{command}': {e}")
                return None
    
    def get_selection(self) -> List[str]:
        """
        Get currently selected Maya objects.
        
        Returns:
            List of selected object names
        """
        if not self.is_connected:
            return []
        
        try:
            return self._maya_cmds.ls(selection=True) or []
        except Exception as e:
            print(f"Error getting Maya selection: {e}")
            return []
    
    def set_selection(self, objects: List[str]) -> bool:
        """
        Set selection to specified Maya objects.
        
        Args:
            objects: List of object names to select
            
        Returns:
            True if selection successful, False otherwise
        """
        if not self.is_connected:
            return False
        
        try:
            if objects:
                self._maya_cmds.select(objects)
            else:
                self._maya_cmds.select(clear=True)
            return True
        except Exception as e:
            print(f"Error setting Maya selection: {e}")
            return False
    
    def get_dcc_version(self) -> str:
        """
        Get Maya version.
        
        Returns:
            Maya version string
        """
        if not self.is_connected:
            return "Unknown"
        
        try:
            return self._maya_cmds.about(version=True)
        except:
            return "Unknown"
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported Maya file formats.
        
        Returns:
            List of file extensions
        """
        return ['.ma', '.mb']
    
    def _extract_version_from_filename(self, filename: str) -> str:
        """Extract version number from filename."""
        match = re.search(r'_v(\d+)', filename)
        return f"v{match.group(1)}" if match else "v001"
    
    def _extract_task_info_from_path(self, file_path: Optional[Path]) -> tuple:
        """Extract task ID and project from file path."""
        if not file_path:
            return None, None
        
        # Simple extraction - could be enhanced based on path structure
        parts = file_path.parts
        project = parts[0] if len(parts) > 0 else None
        task_id = file_path.stem if file_path else None
        
        return task_id, project
    
    def _increment_version(self, version: str) -> str:
        """Increment version number."""
        match = re.search(r'v(\d+)', version)
        if match:
            current_num = int(match.group(1))
            return f"v{current_num + 1:03d}"
        return "v002"
    
    def _get_versioned_file_path(self, base_path: Path, version: str) -> Path:
        """Get file path with version number."""
        stem = base_path.stem
        # Remove existing version if present
        stem = re.sub(r'_v\d+$', '', stem)
        return base_path.parent / f"{stem}_{version}{base_path.suffix}"
