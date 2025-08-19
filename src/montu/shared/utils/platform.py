"""
Platform Utilities for Montu Manager

Cross-platform utilities for handling Windows/Linux differences in path handling,
drive mapping, and system-specific operations.
"""

import os
import platform
from pathlib import Path
from typing import Dict, Optional, Union, List
from enum import Enum


class PlatformType(Enum):
    """Supported platform types."""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    UNKNOWN = "unknown"


class PlatformManager:
    """
    Cross-platform utility manager for handling platform-specific operations.
    
    Features:
    - Automatic platform detection
    - Drive mapping for Windows/Linux
    - Path normalization and conversion
    - Platform-specific configuration handling
    - Network path handling
    """
    
    def __init__(self):
        """Initialize platform manager with current platform detection."""
        self.platform_type = self._detect_platform()
        self.is_windows = self.platform_type == PlatformType.WINDOWS
        self.is_linux = self.platform_type == PlatformType.LINUX
        self.is_macos = self.platform_type == PlatformType.MACOS
    
    def _detect_platform(self) -> PlatformType:
        """Detect the current platform."""
        system = platform.system().lower()
        
        if system == "windows":
            return PlatformType.WINDOWS
        elif system == "linux":
            return PlatformType.LINUX
        elif system == "darwin":
            return PlatformType.MACOS
        else:
            return PlatformType.UNKNOWN
    
    def normalize_path(self, path: Union[str, Path]) -> Path:
        """
        Normalize path for current platform.
        
        Args:
            path: Path to normalize
            
        Returns:
            Normalized Path object
        """
        if isinstance(path, str):
            path = Path(path)
        
        # Convert forward slashes to backslashes on Windows
        if self.is_windows:
            return Path(str(path).replace('/', '\\'))
        else:
            return Path(str(path).replace('\\', '/'))
    
    def map_drive_path(self, drive_letter: str, mount_point: str, 
                      relative_path: str = "") -> Path:
        """
        Map drive letter (Windows) to mount point (Linux) or vice versa.
        
        Args:
            drive_letter: Windows drive letter (e.g., "V:")
            mount_point: Linux mount point (e.g., "/mnt/projects")
            relative_path: Additional path to append
            
        Returns:
            Platform-appropriate path
        """
        if self.is_windows:
            base_path = Path(drive_letter)
        else:
            base_path = Path(mount_point)
        
        if relative_path:
            return base_path / relative_path
        return base_path
    
    def get_project_root_paths(self, project_config: Dict) -> Dict[str, Path]:
        """
        Get platform-appropriate project root paths from configuration.
        
        Args:
            project_config: Project configuration dictionary
            
        Returns:
            Dictionary of path types to platform-appropriate paths
        """
        platform_settings = project_config.get("platform_settings", {})
        current_platform = self.platform_type.value
        
        if current_platform not in platform_settings:
            # Fallback to Windows settings if current platform not configured
            current_platform = "windows"
        
        settings = platform_settings.get(current_platform, {})
        
        return {
            "working": Path(settings.get("working_root", "")),
            "render": Path(settings.get("render_root", "")),
            "media": Path(settings.get("media_root", ""))
        }
    
    def convert_network_path(self, path: Union[str, Path]) -> Path:
        """
        Convert network paths between Windows UNC and Linux mount formats.
        
        Args:
            path: Network path to convert
            
        Returns:
            Platform-appropriate network path
        """
        path_str = str(path)
        
        if self.is_windows:
            # Convert Linux mount to Windows UNC if needed
            if path_str.startswith("/mnt/"):
                # Example: /mnt/projects -> \\server\projects
                mount_parts = path_str.split("/")[2:]  # Skip empty and 'mnt'
                if mount_parts:
                    return Path(f"\\\\server\\{'/'.join(mount_parts)}")
        else:
            # Convert Windows UNC to Linux mount if needed
            if path_str.startswith("\\\\"):
                # Example: \\server\projects -> /mnt/projects
                unc_parts = path_str.split("\\")[2:]  # Skip empty parts
                if len(unc_parts) >= 2:
                    return Path(f"/mnt/{'/'.join(unc_parts[1:])}")
        
        return Path(path)
    
    def get_temp_directory(self) -> Path:
        """Get platform-appropriate temporary directory."""
        if self.is_windows:
            return Path(os.environ.get("TEMP", "C:\\temp"))
        else:
            return Path("/tmp")
    
    def get_user_home(self) -> Path:
        """Get user home directory."""
        return Path.home()
    
    def get_executable_extension(self) -> str:
        """Get platform-appropriate executable extension."""
        return ".exe" if self.is_windows else ""
    
    def get_path_separator(self) -> str:
        """Get platform-appropriate path separator."""
        return "\\" if self.is_windows else "/"
    
    def is_absolute_path(self, path: Union[str, Path]) -> bool:
        """Check if path is absolute for current platform."""
        path_obj = Path(path)
        return path_obj.is_absolute()
    
    def join_paths(self, *paths: Union[str, Path]) -> Path:
        """Join paths using platform-appropriate separators."""
        result = Path(paths[0]) if paths else Path()
        
        for path in paths[1:]:
            result = result / path
        
        return self.normalize_path(result)
    
    def ensure_directory_exists(self, path: Union[str, Path]) -> Path:
        """Ensure directory exists, creating it if necessary."""
        path_obj = Path(path)
        path_obj.mkdir(parents=True, exist_ok=True)
        return path_obj
    
    def get_platform_info(self) -> Dict[str, str]:
        """Get detailed platform information."""
        return {
            "platform": self.platform_type.value,
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }


# Global platform manager instance
platform_manager = PlatformManager()


# Convenience functions
def get_platform_type() -> PlatformType:
    """Get current platform type."""
    return platform_manager.platform_type


def normalize_path(path: Union[str, Path]) -> Path:
    """Normalize path for current platform."""
    return platform_manager.normalize_path(path)


def map_drive_path(drive_letter: str, mount_point: str, relative_path: str = "") -> Path:
    """Map drive letter to mount point for current platform."""
    return platform_manager.map_drive_path(drive_letter, mount_point, relative_path)


def is_windows() -> bool:
    """Check if running on Windows."""
    return platform_manager.is_windows


def is_linux() -> bool:
    """Check if running on Linux."""
    return platform_manager.is_linux


def is_macos() -> bool:
    """Check if running on macOS."""
    return platform_manager.is_macos
