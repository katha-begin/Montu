"""
Path Builder Engine

Template-based path generation system for Montu Manager ecosystem.
Handles drive mapping, name cleaning, and path template processing.
"""

import re
import os
import platform
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass


@dataclass
class PathGenerationResult:
    """Result of path generation with all path types."""
    working_file_path: str
    render_output_path: str
    media_file_path: str
    cache_file_path: str
    submission_path: str
    filename: str
    version_formatted: str
    sequence_clean: str
    shot_clean: str
    episode_clean: str


class PathBuilder:
    """
    Template-based path generation engine for Montu Manager.
    
    Generates file paths using project configuration templates and handles:
    - Drive letter mapping (Windows/Linux)
    - Name cleaning (sequence/shot/episode)
    - Template variable substitution
    - Cross-platform path handling
    """
    
    def __init__(self, project_config: Dict[str, Any]):
        """
        Initialize Path Builder with project configuration.
        
        Args:
            project_config: Project configuration dictionary from database
        """
        self.config = project_config
        self.platform = platform.system().lower()
        
        # Validate required configuration sections
        self._validate_config()
    
    def _validate_config(self):
        """Validate that project configuration has required sections."""
        required_sections = [
            'drive_mapping', 'path_segments', 'templates', 
            'filename_patterns', 'name_cleaning_rules'
        ]
        
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")
    
    def generate_all_paths(self, task_data: Dict[str, Any], version: str = "001", 
                          file_type: str = "maya_scene") -> PathGenerationResult:
        """
        Generate all path types for a task.
        
        Args:
            task_data: Task information dictionary
            version: Version string (e.g., "003")
            file_type: File type for filename pattern (e.g., "maya_scene", "nuke_script")
            
        Returns:
            PathGenerationResult with all generated paths
        """
        # Clean names using project rules
        episode_clean = self._clean_episode_name(task_data.get('episode', ''))
        sequence_clean = self._clean_sequence_name(task_data.get('sequence', ''))
        shot_clean = self._clean_shot_name(task_data.get('shot', ''))
        
        # Format version
        version_formatted = self._format_version(version)
        
        # Generate filename
        filename = self._generate_filename(
            task_data, episode_clean, sequence_clean, shot_clean, 
            version_formatted, file_type
        )
        
        # Prepare template variables
        template_vars = self._prepare_template_variables(
            task_data, episode_clean, sequence_clean, shot_clean, 
            version_formatted, filename
        )
        
        # Generate all path types
        working_file_path = self._generate_path('working_file', template_vars)
        render_output_path = self._generate_path('render_output', template_vars)
        media_file_path = self._generate_path('media_file', template_vars)
        cache_file_path = self._generate_path('cache_file', template_vars)
        submission_path = self._generate_path('submission', template_vars)
        
        return PathGenerationResult(
            working_file_path=working_file_path,
            render_output_path=render_output_path,
            media_file_path=media_file_path,
            cache_file_path=cache_file_path,
            submission_path=submission_path,
            filename=filename,
            version_formatted=version_formatted,
            sequence_clean=sequence_clean,
            shot_clean=shot_clean,
            episode_clean=episode_clean
        )
    
    def generate_working_file_path(self, task_data: Dict[str, Any], 
                                  version: str = "001", 
                                  file_type: str = "maya_scene") -> str:
        """
        Generate working file path.
        
        Example: V:/SWA/all/scene/Ep00/sq0020/SH0090/lighting/version/Ep00_sq0020_SH0090_lighting_master_v003.ma
        """
        result = self.generate_all_paths(task_data, version, file_type)
        return result.working_file_path
    
    def generate_render_output_path(self, task_data: Dict[str, Any], 
                                   version: str = "015") -> str:
        """
        Generate render output directory path.
        
        Example: W:/SWA/all/scene/Ep00/sq0010/SH0020/comp/version/v015/
        """
        result = self.generate_all_paths(task_data, version)
        return result.render_output_path
    
    def _clean_episode_name(self, episode: str) -> str:
        """Clean episode name using project rules."""
        if not episode:
            return "Unknown"
        
        pattern = self.config['name_cleaning_rules'].get('episode_pattern', '')
        replacement = self.config['name_cleaning_rules'].get('episode_replacement', '\\1')
        
        if pattern:
            match = re.match(pattern, episode)
            if match:
                return re.sub(pattern, replacement, episode)
        
        return episode
    
    def _clean_sequence_name(self, sequence: str) -> str:
        """
        Clean sequence name using project rules.
        
        Example: 'SWA_Ep00_sq0010' -> 'sq0010'
        """
        if not sequence:
            return "Unknown"
        
        pattern = self.config['name_cleaning_rules'].get('sequence_pattern', '')
        replacement = self.config['name_cleaning_rules'].get('sequence_replacement', '\\1')
        
        if pattern:
            match = re.match(pattern, sequence)
            if match:
                return re.sub(pattern, replacement, sequence)
        
        return sequence
    
    def _clean_shot_name(self, shot: str) -> str:
        """
        Clean shot name using project rules.
        
        Example: 'SWA_Ep00_SH0020' -> 'SH0020'
        """
        if not shot:
            return "Unknown"
        
        pattern = self.config['name_cleaning_rules'].get('shot_pattern', '')
        replacement = self.config['name_cleaning_rules'].get('shot_replacement', '\\1')
        
        if pattern:
            match = re.match(pattern, shot)
            if match:
                return re.sub(pattern, replacement, shot)
        
        return shot
    
    def _format_version(self, version: str) -> str:
        """Format version string according to project settings."""
        # Remove 'v' prefix if present
        version_num = version.lstrip('v')
        
        try:
            version_int = int(version_num)
            padding = self.config['version_settings'].get('padding', 3)
            return f"{version_int:0{padding}d}"
        except ValueError:
            return version_num
    
    def _generate_filename(self, task_data: Dict[str, Any], episode_clean: str, 
                          sequence_clean: str, shot_clean: str, version_formatted: str,
                          file_type: str) -> str:
        """Generate filename using project patterns."""
        filename_pattern = self.config['filename_patterns'].get(file_type, '')
        
        if not filename_pattern:
            # Fallback to generic pattern
            task_name = task_data.get('task', 'unknown').lower()
            ext = self.config['task_settings']['default_file_extensions'].get(task_name, '.ma')
            filename_pattern = f"{{episode}}_{{sequence_clean}}_{{shot_clean}}_{{task}}_master_v{{version}}{ext}"
        
        return filename_pattern.format(
            episode=episode_clean,
            sequence_clean=sequence_clean,
            shot_clean=shot_clean,
            task=task_data.get('task', 'unknown').lower(),
            version=version_formatted
        )
    
    def _prepare_template_variables(self, task_data: Dict[str, Any], episode_clean: str,
                                   sequence_clean: str, shot_clean: str, 
                                   version_formatted: str, filename: str) -> Dict[str, str]:
        """Prepare all template variables for path generation."""
        # Get drive mappings based on platform
        drive_mapping = self._get_platform_drive_mapping()
        
        # Get path segments
        path_segments = self.config['path_segments']
        
        return {
            # Drive mappings
            'drive_working': drive_mapping.get('working_files', 'V:'),
            'drive_render': drive_mapping.get('render_outputs', 'W:'),
            'drive_media': drive_mapping.get('media_files', 'J:'),
            'drive_cache': drive_mapping.get('cache_files', 'T:'),
            
            # Project info
            'project': self.config.get('_id', 'Unknown'),
            
            # Path segments
            'middle_path': path_segments.get('middle_path', 'all/scene'),
            'version_dir': path_segments.get('version_dir', 'version'),
            'work_dir': path_segments.get('work_dir', 'work'),
            'publish_dir': path_segments.get('publish_dir', 'publish'),
            'cache_dir': path_segments.get('cache_dir', 'cache'),
            
            # Cleaned names
            'episode': episode_clean,
            'sequence_clean': sequence_clean,
            'shot_clean': shot_clean,
            
            # Task info
            'task': task_data.get('task', 'unknown').lower(),
            
            # Version info
            'version': version_formatted,
            
            # Filename
            'filename': filename,
            
            # Client info (for submission paths)
            'client': self.config['client_settings'].get('default_client', 'Client'),
            'client_version': version_formatted  # Can be mapped differently later
        }
    
    def _get_platform_drive_mapping(self) -> Dict[str, str]:
        """Get drive mapping based on current platform."""
        if self.platform == 'windows':
            return self.config['drive_mapping']
        else:
            # Use Linux paths from platform_settings
            platform_settings = self.config.get('platform_settings', {}).get('linux', {})
            return {
                'working_files': platform_settings.get('working_root', '/mnt/projects'),
                'render_outputs': platform_settings.get('render_root', '/mnt/renders'),
                'media_files': platform_settings.get('media_root', '/mnt/media'),
                'cache_files': '/tmp/cache',
                'backup_files': '/mnt/backup'
            }
    
    def _generate_path(self, path_type: str, template_vars: Dict[str, str]) -> str:
        """Generate a specific path type using template variables."""
        template = self.config['templates'].get(path_type, '')
        
        if not template:
            raise ValueError(f"No template found for path type: {path_type}")
        
        try:
            path = template.format(**template_vars)
            
            # Normalize path separators for current platform
            if self.platform == 'windows':
                path = path.replace('/', '\\')
            else:
                path = path.replace('\\', '/')
            
            return path
            
        except KeyError as e:
            raise ValueError(f"Missing template variable {e} for path type {path_type}")
    
    def validate_path_template(self, template: str) -> List[str]:
        """
        Validate a path template and return list of required variables.
        
        Args:
            template: Template string to validate
            
        Returns:
            List of required variable names
        """
        import string
        
        # Extract variable names from template
        formatter = string.Formatter()
        variables = [field_name for _, field_name, _, _ in formatter.parse(template) if field_name]
        
        return variables
    
    def get_task_file_extension(self, task_name: str) -> str:
        """Get default file extension for a task type."""
        return self.config['task_settings']['default_file_extensions'].get(
            task_name.lower(), '.ma'
        )
    
    def get_render_formats(self, task_name: str) -> List[str]:
        """Get expected render formats for a task type."""
        return self.config['task_settings']['render_formats'].get(
            task_name.lower(), ['exr']
        )
