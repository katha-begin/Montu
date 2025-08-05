"""
Path Builder Engine

Advanced template-based path generation system for Montu Manager ecosystem.
Handles drive mapping, name cleaning, path template processing, and dynamic field injection.

Features:
- Template-based path generation with variable substitution
- Dynamic field injection from project configuration
- Cross-platform path handling (Windows/Linux)
- Name cleaning with regex patterns
- Version formatting and management
- Custom template functions and filters
- Conditional path generation
- Path validation and sanitization
"""

import re
import os
import platform
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Callable
from dataclasses import dataclass
from datetime import datetime
import string


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
    template_variables: Dict[str, Any]
    metadata: Dict[str, Any]


class TemplateProcessor:
    """Advanced template processing with dynamic field injection and custom functions."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize template processor with project configuration."""
        self.config = config
        self.custom_functions = self._register_custom_functions()

    def _register_custom_functions(self) -> Dict[str, Callable]:
        """Register custom template functions."""
        return {
            'upper': lambda x: str(x).upper(),
            'lower': lambda x: str(x).lower(),
            'title': lambda x: str(x).title(),
            'pad': lambda x, length=3: str(x).zfill(int(length)),
            'replace': lambda x, old, new: str(x).replace(old, new),
            'truncate': lambda x, length=10: str(x)[:int(length)],
            'date': lambda fmt='%Y%m%d': datetime.now().strftime(fmt),
            'sanitize': lambda x: self._sanitize_filename(str(x)),
            'conditional': lambda condition, true_val, false_val: true_val if condition else false_val
        }

    def process_template(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Process template with advanced features.

        Supports:
        - Variable substitution: {variable}
        - Function calls: {variable|function}
        - Function with args: {variable|function:arg1:arg2}
        - Conditional expressions: {variable|conditional:true_value:false_value}
        - Nested variables: {outer.inner}
        """
        # First pass: handle nested variables
        processed_template = self._process_nested_variables(template, variables)

        # Second pass: handle function calls
        processed_template = self._process_functions(processed_template, variables)

        # Third pass: standard variable substitution
        try:
            return processed_template.format(**variables)
        except KeyError as e:
            # Provide helpful error message
            missing_var = str(e).strip("'")
            available_vars = list(variables.keys())
            raise ValueError(f"Missing template variable '{missing_var}'. Available variables: {available_vars}")

    def _process_nested_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """Process nested variable access like {metadata.artist.name}."""
        pattern = r'\{([^}]+\.[^}|]+)\}'

        def replace_nested(match):
            var_path = match.group(1)
            try:
                value = self._get_nested_value(variables, var_path)
                return str(value)
            except (KeyError, AttributeError, TypeError):
                return match.group(0)  # Return original if not found

        return re.sub(pattern, replace_nested, template)

    def _process_functions(self, template: str, variables: Dict[str, Any]) -> str:
        """Process function calls in templates like {variable|function:arg1:arg2}."""
        pattern = r'\{([^}|]+)\|([^}]+)\}'

        def replace_function(match):
            var_name = match.group(1)
            function_call = match.group(2)

            # Parse function and arguments
            parts = function_call.split(':')
            func_name = parts[0]
            args = parts[1:] if len(parts) > 1 else []

            # Special handling for functions that don't need variables (like date)
            if func_name in ['date', 'timestamp', 'time', 'year', 'month', 'day']:
                if func_name in self.custom_functions:
                    try:
                        func = self.custom_functions[func_name]
                        if args:
                            result = func(*args)
                        else:
                            result = func()
                        return str(result)
                    except Exception:
                        return match.group(0)

            # Get variable value
            if var_name in variables:
                value = variables[var_name]
            else:
                return match.group(0)  # Return original if variable not found

            # Apply function
            if func_name in self.custom_functions:
                try:
                    func = self.custom_functions[func_name]
                    if args:
                        result = func(value, *args)
                    else:
                        result = func(value)
                    return str(result)
                except Exception:
                    return str(value)  # Return original value if function fails

            return str(value)

        return re.sub(pattern, replace_function, template)

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get nested value from dictionary using dot notation."""
        keys = path.split('.')
        value = data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                raise KeyError(f"Key '{key}' not found in path '{path}'")

        return value

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility."""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # Remove control characters
        filename = ''.join(char for char in filename if ord(char) >= 32)

        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext

        return filename


class PathBuilder:
    """
    Advanced template-based path generation engine for Montu Manager.

    Generates file paths using project configuration templates and handles:
    - Drive letter mapping (Windows/Linux)
    - Name cleaning (sequence/shot/episode)
    - Advanced template variable substitution
    - Dynamic field injection
    - Custom template functions
    - Cross-platform path handling
    - Path validation and sanitization
    """

    def __init__(self, project_config: Dict[str, Any]):
        """
        Initialize Path Builder with project configuration.

        Args:
            project_config: Project configuration dictionary from database
        """
        self.config = project_config
        self.platform = platform.system().lower()
        self.template_processor = TemplateProcessor(project_config)

        # Validate required configuration sections
        self._validate_config()

        # Initialize dynamic field registry
        self.dynamic_fields = self._initialize_dynamic_fields()
    
    def _validate_config(self):
        """Validate that project configuration has required sections."""
        required_sections = [
            'drive_mapping', 'path_segments', 'templates',
            'filename_patterns', 'name_cleaning_rules'
        ]

        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")

    def _initialize_dynamic_fields(self) -> Dict[str, Callable]:
        """Initialize dynamic field generators."""
        return {
            'timestamp': lambda: datetime.now().strftime('%Y%m%d_%H%M%S'),
            'date': lambda: datetime.now().strftime('%Y%m%d'),
            'time': lambda: datetime.now().strftime('%H%M%S'),
            'year': lambda: datetime.now().strftime('%Y'),
            'month': lambda: datetime.now().strftime('%m'),
            'day': lambda: datetime.now().strftime('%d'),
            'user': lambda: os.environ.get('USERNAME', os.environ.get('USER', 'unknown')),
            'hostname': lambda: platform.node(),
            'platform': lambda: self.platform,
            'project_id': lambda: self.config.get('_id', 'unknown'),
            'project_name': lambda: self.config.get('name', 'unknown')
        }

    def add_dynamic_field(self, name: str, generator: Callable) -> None:
        """Add custom dynamic field generator."""
        self.dynamic_fields[name] = generator

    def get_dynamic_field_value(self, field_name: str) -> str:
        """Get value for dynamic field."""
        if field_name in self.dynamic_fields:
            try:
                return str(self.dynamic_fields[field_name]())
            except Exception as e:
                print(f"Warning: Failed to generate dynamic field '{field_name}': {e}")
                return f"ERROR_{field_name}"
        return f"UNKNOWN_{field_name}"
    
    def generate_all_paths(self, task_data: Dict[str, Any], version: str = "001",
                          file_type: str = "maya_scene",
                          custom_fields: Dict[str, Any] = None) -> PathGenerationResult:
        """
        Generate all path types for a task with advanced template processing.

        Args:
            task_data: Task information dictionary
            version: Version string (e.g., "003")
            file_type: File type for filename pattern (e.g., "maya_scene", "nuke_script")
            custom_fields: Additional custom fields for template injection

        Returns:
            PathGenerationResult with all generated paths and metadata
        """
        # Clean names using project rules
        episode_clean = self._clean_episode_name(task_data.get('episode', ''))
        sequence_clean = self._clean_sequence_name(task_data.get('sequence', ''))
        shot_clean = self._clean_shot_name(task_data.get('shot', ''))

        # Format version
        version_formatted = self._format_version(version)

        # Generate filename with advanced template processing
        filename = self._generate_filename_advanced(
            task_data, episode_clean, sequence_clean, shot_clean,
            version_formatted, file_type, custom_fields
        )

        # Prepare enhanced template variables with dynamic fields
        template_vars = self._prepare_enhanced_template_variables(
            task_data, episode_clean, sequence_clean, shot_clean,
            version_formatted, filename, custom_fields
        )

        # Generate all path types with advanced template processing
        working_file_path = self._generate_path_advanced('working_file', template_vars)
        render_output_path = self._generate_path_advanced('render_output', template_vars)
        media_file_path = self._generate_path_advanced('media_file', template_vars)
        cache_file_path = self._generate_path_advanced('cache_file', template_vars)
        submission_path = self._generate_path_advanced('submission', template_vars)

        # Generate metadata
        metadata = self._generate_path_metadata(task_data, template_vars, file_type)

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
            episode_clean=episode_clean,
            template_variables=template_vars,
            metadata=metadata
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

    def generate_custom_path(self, template: str, task_data: Dict[str, Any],
                           version: str = "001", custom_fields: Dict[str, Any] = None) -> str:
        """
        Generate custom path using provided template.

        Args:
            template: Custom path template string
            task_data: Task information dictionary
            version: Version string
            custom_fields: Additional custom fields

        Returns:
            Generated path string
        """
        # Clean names
        episode_clean = self._clean_episode_name(task_data.get('episode', ''))
        sequence_clean = self._clean_sequence_name(task_data.get('sequence', ''))
        shot_clean = self._clean_shot_name(task_data.get('shot', ''))
        version_formatted = self._format_version(version)

        # Prepare template variables
        template_vars = self._prepare_enhanced_template_variables(
            task_data, episode_clean, sequence_clean, shot_clean,
            version_formatted, "", custom_fields
        )

        # Process custom template
        return self.template_processor.process_template(template, template_vars)

    def validate_path_template(self, template: str) -> Dict[str, Any]:
        """
        Validate path template and return analysis.

        Args:
            template: Template string to validate

        Returns:
            Dictionary with validation results
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'variables_found': [],
            'functions_found': [],
            'missing_variables': []
        }

        # Find all variables in template
        var_pattern = r'\{([^}]+)\}'
        variables = re.findall(var_pattern, template)

        for var in variables:
            if '|' in var:
                # Function call
                var_name, func_call = var.split('|', 1)
                func_name = func_call.split(':')[0]
                validation_result['variables_found'].append(var_name)
                validation_result['functions_found'].append(func_name)

                # Check if function exists
                if func_name not in self.template_processor.custom_functions:
                    validation_result['errors'].append(f"Unknown function: {func_name}")
                    validation_result['valid'] = False
            else:
                validation_result['variables_found'].append(var)

        # Remove duplicates
        validation_result['variables_found'] = list(set(validation_result['variables_found']))
        validation_result['functions_found'] = list(set(validation_result['functions_found']))

        return validation_result

    def generate_base_task_directories(self, task_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate base task directory paths including 'version' folder but without version number subdirectories.

        This creates the core task structure with version folders:
        - working_base: V:/SWA/all/scene/Ep00/sq0020/SH0090/lighting/version/
        - render_base: W:/SWA/all/scene/Ep00/sq0020/SH0090/lighting/version/
        - media_base: E:/SWA/all/scene/Ep00/sq0020/SH0090/lighting/version/
        - cache_base: E:/SWA/all/scene/Ep00/sq0020/SH0090/lighting/cache/

        Version number subdirectories (v001, v002, etc.) are only created when files are saved.

        Args:
            task_data: Task information dictionary

        Returns:
            Dictionary with base directory paths
        """
        # Clean names using project rules
        episode_clean = self._clean_episode_name(task_data.get('episode', ''))
        sequence_clean = self._clean_sequence_name(task_data.get('sequence', ''))
        shot_clean = self._clean_shot_name(task_data.get('shot', ''))

        # Prepare template variables without version info
        template_vars = self._prepare_base_template_variables(
            task_data, episode_clean, sequence_clean, shot_clean
        )

        # Generate base directory paths
        working_base = self._generate_base_path('working_file', template_vars)
        render_base = self._generate_base_path('render_output', template_vars)
        media_base = self._generate_base_path('media_file', template_vars)
        cache_base = self._generate_base_path('cache_file', template_vars)

        return {
            'working_base': working_base,
            'render_base': render_base,
            'media_base': media_base,
            'cache_base': cache_base
        }
    
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

    def _generate_filename_advanced(self, task_data: Dict[str, Any], episode_clean: str,
                                  sequence_clean: str, shot_clean: str, version_formatted: str,
                                  file_type: str, custom_fields: Dict[str, Any] = None) -> str:
        """Generate filename using advanced template processing."""
        filename_pattern = self.config['filename_patterns'].get(file_type, '')

        if not filename_pattern:
            # Fallback to generic pattern
            task_name = task_data.get('task', 'unknown').lower()
            ext = self.config['task_settings']['default_file_extensions'].get(task_name, '.ma')
            filename_pattern = f"{{episode}}_{{sequence_clean}}_{{shot_clean}}_{{task}}_master_v{{version}}{ext}"

        # Prepare variables for filename
        template_vars = {
            'episode': episode_clean,
            'sequence_clean': sequence_clean,
            'shot_clean': shot_clean,
            'task': task_data.get('task', 'unknown').lower(),
            'version': version_formatted,
            'artist': task_data.get('artist', 'unknown'),
            'project': self.config.get('_id', 'unknown')
        }

        # Add custom fields
        if custom_fields:
            template_vars.update(custom_fields)

        # Add dynamic fields
        for field_name in self.dynamic_fields:
            template_vars[f'dynamic_{field_name}'] = self.get_dynamic_field_value(field_name)

        # Process with advanced template processor
        return self.template_processor.process_template(filename_pattern, template_vars)

    def _prepare_enhanced_template_variables(self, task_data: Dict[str, Any],
                                           episode_clean: str, sequence_clean: str,
                                           shot_clean: str, version_formatted: str,
                                           filename: str, custom_fields: Dict[str, Any] = None) -> Dict[str, str]:
        """Prepare enhanced template variables with dynamic field injection."""
        # Get base drive mapping
        drive_mapping = self._get_platform_drive_mapping()
        path_segments = self.config.get('path_segments', {})

        # Base template variables
        template_vars = {
            # Drive mappings
            'drive_working': drive_mapping.get('working_files', 'V:'),
            'drive_render': drive_mapping.get('render_outputs', 'W:'),
            'drive_media': drive_mapping.get('media_files', 'J:'),
            'drive_cache': drive_mapping.get('cache_files', 'T:'),

            # Project info
            'project': self.config.get('_id', 'Unknown'),
            'project_name': self.config.get('name', 'Unknown'),

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
            'task': self._standardize_task_name(task_data.get('task', 'unknown')),
            'task_original': task_data.get('task', 'unknown'),
            'artist': task_data.get('artist', 'unknown'),
            'status': task_data.get('status', 'unknown'),
            'priority': task_data.get('priority', 'medium'),

            # Version info
            'version': version_formatted,
            'version_raw': version_formatted.lstrip('v'),

            # File info
            'filename': filename,
            'filename_no_ext': os.path.splitext(filename)[0] if filename else '',
            'file_ext': os.path.splitext(filename)[1] if filename else '',

            # Client/delivery info (with defaults)
            'client': task_data.get('client', 'internal'),
            'client_version': task_data.get('client_version', version_formatted),
            'delivery_type': task_data.get('delivery_type', 'review'),
        }

        # Add dynamic fields
        for field_name, generator in self.dynamic_fields.items():
            try:
                template_vars[field_name] = str(generator())
            except Exception as e:
                print(f"Warning: Failed to generate dynamic field '{field_name}': {e}")
                template_vars[field_name] = f"ERROR_{field_name}"

        # Add custom fields
        if custom_fields:
            template_vars.update(custom_fields)

        # Add metadata if available
        if 'metadata' in task_data:
            template_vars['metadata'] = task_data['metadata']

        return template_vars

    def _generate_path_advanced(self, path_type: str, template_vars: Dict[str, str]) -> str:
        """Generate path using advanced template processing."""
        template = self.config['templates'].get(path_type, '')

        if not template:
            raise ValueError(f"No template found for path type: {path_type}")

        try:
            # Use advanced template processor
            path = self.template_processor.process_template(template, template_vars)

            # Normalize path separators for current platform
            if self.platform == 'windows':
                path = path.replace('/', '\\')
            else:
                path = path.replace('\\', '/')

            return path

        except Exception as e:
            raise ValueError(f"Failed to generate path for type '{path_type}': {e}")

    def _generate_path_metadata(self, task_data: Dict[str, Any],
                              template_vars: Dict[str, str],
                              file_type: str) -> Dict[str, Any]:
        """Generate metadata about the path generation process."""
        return {
            'generation_timestamp': datetime.now().isoformat(),
            'path_builder_version': '2.0',
            'platform': self.platform,
            'project_id': self.config.get('_id', 'unknown'),
            'file_type': file_type,
            'template_variables_count': len(template_vars),
            'dynamic_fields_used': list(self.dynamic_fields.keys()),
            'task_id': task_data.get('_id', 'unknown'),
            'generation_context': {
                'artist': task_data.get('artist', 'unknown'),
                'status': task_data.get('status', 'unknown'),
                'priority': task_data.get('priority', 'medium')
            }
        }
    
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
            
            # Task info - standardized and cleaned
            'task': self._standardize_task_name(task_data.get('task', 'unknown')),
            
            # Version info
            'version': version_formatted,
            
            # Filename
            'filename': filename,
            
            # Client info (for submission paths)
            'client': self.config['client_settings'].get('default_client', 'Client'),
            'client_version': version_formatted  # Can be mapped differently later
        }

    def _standardize_task_name(self, task_name: str) -> str:
        """
        Clean and normalize task names for path generation.

        Preserves original task names from CSV/database without transformation,
        only applying basic cleaning (lowercase, strip whitespace).

        Args:
            task_name: Raw task name from database

        Returns:
            Cleaned lowercase task name (no transformations)
        """
        if not task_name:
            return 'unknown'

        # Only apply basic cleaning: lowercase and strip whitespace
        # No name transformations to preserve CSV input exactly
        return task_name.lower().strip()

    def _prepare_base_template_variables(self, task_data: Dict[str, Any], episode_clean: str,
                                        sequence_clean: str, shot_clean: str) -> Dict[str, str]:
        """Prepare template variables for base directory generation (includes version_dir but no version numbers)."""
        # Get drive mappings based on platform
        drive_mapping = self._get_platform_drive_mapping()

        # Get path segments
        path_segments = self.config.get('path_segments', {})

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
            'version_dir': path_segments.get('version_dir', 'version'),  # Include version_dir
            'cache_dir': path_segments.get('cache_dir', 'cache'),

            # Cleaned names
            'episode': episode_clean,
            'sequence_clean': sequence_clean,
            'shot_clean': shot_clean,

            # Task info - standardized and cleaned
            'task': self._standardize_task_name(task_data.get('task', 'unknown')),
        }

    def _generate_base_path(self, path_type: str, template_vars: Dict[str, str]) -> str:
        """Generate base task directory path including 'version' folder but without version number subdirectories."""
        template = self.config['templates'].get(path_type, '')

        if not template:
            raise ValueError(f"No template found for path type: {path_type}")

        # Create base templates that include 'version' folder but exclude version numbers and media subdirs
        base_templates = {
            'working_file': "{drive_working}/{project}/{middle_path}/{episode}/{sequence_clean}/{shot_clean}/{task}/{version_dir}/",
            'render_output': "{drive_render}/{project}/{middle_path}/{episode}/{sequence_clean}/{shot_clean}/{task}/{version_dir}/",
            'media_file': "{drive_media}/{project}/{middle_path}/{episode}/{sequence_clean}/{shot_clean}/{task}/{version_dir}/",
            'cache_file': "{drive_cache}/{project}/{middle_path}/{episode}/{sequence_clean}/{shot_clean}/{task}/{cache_dir}/"
        }

        base_template = base_templates.get(path_type, '')
        if not base_template:
            # Fallback: try to extract base path from original template
            # Remove version number and media subdirectories but keep version_dir
            base_template = template
            base_template = base_template.replace('/v{version}', '')  # Remove version numbers
            base_template = base_template.replace('/{filename}', '')  # Remove filename
            base_template = base_template.replace('/media', '')       # Remove media subdir
            if not base_template.endswith('/'):
                base_template += '/'

        try:
            path = base_template.format(**template_vars)

            # Normalize path separators for current platform
            if self.platform == 'windows':
                path = path.replace('/', '\\')
            else:
                path = path.replace('\\', '/')

            return path

        except KeyError as e:
            raise ValueError(f"Missing template variable {e} for base path type {path_type}")

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
