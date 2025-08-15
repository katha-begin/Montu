"""
Project Edit Dialog for Ra: Task Creator

Dialog for editing existing project configurations with:
- Pre-populated form fields from existing project data
- Read-only Project ID field
- Save Changes functionality with modification tracking
- Reset to Original capability
"""

from typing import Dict, Any, List
from datetime import datetime

from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Signal

from .project_creation_dialog import ProjectCreationDialog


class ProjectEditDialog(ProjectCreationDialog):
    """
    Project editing dialog inheriting from ProjectCreationDialog.
    
    Provides functionality to edit existing project configurations
    with pre-populated form fields and change tracking.
    """
    
    project_updated = Signal(dict)  # Emitted when project is successfully updated
    
    def __init__(self, parent=None, existing_projects: List[str] = None, project_config: Dict[str, Any] = None):
        """
        Initialize project edit dialog.
        
        Args:
            parent: Parent widget
            existing_projects: List of existing project IDs for uniqueness validation
            project_config: Existing project configuration to edit
        """
        self.original_project_config = project_config or {}
        self.is_editing = True
        
        # Initialize parent with existing projects (excluding current project for uniqueness check)
        current_project_id = self.original_project_config.get('_id', '')
        filtered_existing_projects = [p for p in (existing_projects or []) if p != current_project_id]
        
        super().__init__(parent, filtered_existing_projects)
        
        # Load project configuration after UI is set up
        if self.original_project_config:
            self.load_project_config(self.original_project_config)
            
    def setup_ui(self):
        """Set up the user interface for editing."""
        # Call parent setup
        super().setup_ui()
        
        # Update window title
        self.setWindowTitle("Ra: Edit Project Configuration")
        
        # Update header label
        if hasattr(self, 'findChild'):
            header_labels = self.findChildren(type(self.layout().itemAt(0).widget()))
            if header_labels:
                header_labels[0].setText("Edit Project Configuration")
        
        # Make Project ID read-only
        self.project_id_edit.setReadOnly(True)
        self.project_id_edit.setStyleSheet("background-color: #f0f0f0; color: #666666;")
        self.auto_generate_id_btn.setEnabled(False)
        self.auto_generate_id_btn.setToolTip("Project ID cannot be changed after creation")
        
        # Update button text
        self.create_button.setText("Save Changes")
        self.create_button.clicked.disconnect()  # Disconnect original handler
        self.create_button.clicked.connect(self.save_changes)
        
        # Add Reset to Original button
        self.reset_button = self.create_button.__class__("Reset to Original")
        self.reset_button.clicked.connect(self.reset_to_original)
        
        # Insert reset button before save button
        button_layout = self.create_button.parent().layout()
        button_layout.insertWidget(button_layout.count() - 1, self.reset_button)
        
    def load_project_config(self, project_config: Dict[str, Any]):
        """Load existing project configuration into form fields."""
        try:
            # Basic Information
            self.project_name_edit.setText(project_config.get('name', ''))
            self.project_id_edit.setText(project_config.get('_id', ''))
            self.project_description_edit.setPlainText(project_config.get('description', ''))
            
            # Project Type
            # Note: Project type cannot be changed after creation to maintain consistency
            
            # Task Types
            task_types = project_config.get('task_types', [])
            self.task_types_list.clear()
            for task_type in task_types:
                item = self.task_types_list.__class__.QListWidgetItem(task_type)
                item.setFlags(item.flags() | self.task_types_list.__class__.Qt.ItemIsEditable)
                self.task_types_list.addItem(item)
                
            # Timeline & Budget
            timeline = project_config.get('project_timeline', {})
            if timeline:
                start_date = timeline.get('start_date', '')
                end_date = timeline.get('end_date', '')
                if start_date:
                    self.start_date_edit.setDate(self.start_date_edit.date().fromString(start_date, "yyyy-MM-dd"))
                if end_date:
                    self.end_date_edit.setDate(self.end_date_edit.date().fromString(end_date, "yyyy-MM-dd"))
                    
            budget = project_config.get('project_budget', {})
            if budget:
                self.total_mandays_spin.setValue(budget.get('total_mandays', 100))
                
            # Color Pipeline
            color_pipeline = project_config.get('color_pipeline', {})
            if color_pipeline:
                self.ocio_config_edit.setText(color_pipeline.get('ocio_config_path', ''))
                
                working_colorspace = color_pipeline.get('working_colorspace', 'ACEScg')
                index = self.working_colorspace_combo.findText(working_colorspace)
                if index >= 0:
                    self.working_colorspace_combo.setCurrentIndex(index)
                    
                display_colorspace = color_pipeline.get('display_colorspace', 'sRGB')
                index = self.display_colorspace_combo.findText(display_colorspace)
                if index >= 0:
                    self.display_colorspace_combo.setCurrentIndex(index)
                    
            # Drive Mappings
            drive_mapping = project_config.get('drive_mapping', {})
            if drive_mapping:
                self.working_files_edit.setText(drive_mapping.get('working_files', 'V:'))
                self.render_outputs_edit.setText(drive_mapping.get('render_outputs', 'W:'))
                self.media_files_edit.setText(drive_mapping.get('media_files', 'E:'))
                self.cache_files_edit.setText(drive_mapping.get('cache_files', 'E:'))
                self.backup_files_edit.setText(drive_mapping.get('backup_files', 'E:'))
                
            # Filename Patterns
            filename_patterns = project_config.get('filename_patterns', {})
            for pattern_key, edit in self.filename_pattern_edits.items():
                edit.setText(filename_patterns.get(pattern_key, ''))
                
            # Path Templates
            templates = project_config.get('templates', {})
            for template_key, edit in self.path_template_edits.items():
                edit.setText(templates.get(template_key, ''))
                
            # Media Configuration (with defaults for backward compatibility)
            media_config = project_config.get('media_configuration', {})
            if not media_config:
                # Provide default media configuration for older projects
                media_config = {
                    "final_delivery_resolution": {"width": 3840, "height": 2160, "name": "4K UHD"},
                    "daily_review_resolution": {"width": 1920, "height": 1080, "name": "HD 1080p"},
                    "final_delivery_formats": ["exr", "mov"],
                    "daily_review_formats": ["mov", "jpg"],
                    "default_frame_rate": 24
                }
            self.load_media_configuration(media_config)
                
        except Exception as e:
            QMessageBox.warning(self, "Error Loading Project", 
                              f"Failed to load project configuration:\n{str(e)}")
                              
    def load_media_configuration(self, media_config: Dict[str, Any]):
        """Load media configuration into form fields."""
        # Final Delivery Resolution
        final_resolution = media_config.get('final_delivery_resolution', {})
        if final_resolution:
            self.set_resolution_combo(
                self.final_delivery_resolution_combo,
                self.final_width_spin,
                self.final_height_spin,
                final_resolution
            )
            
        # Daily/Review Resolution
        daily_resolution = media_config.get('daily_review_resolution', {})
        if daily_resolution:
            self.set_resolution_combo(
                self.daily_review_resolution_combo,
                self.daily_width_spin,
                self.daily_height_spin,
                daily_resolution
            )
            
        # Final Delivery Formats
        final_formats = media_config.get('final_delivery_formats', [])
        for i in range(self.final_delivery_formats_list.count()):
            item = self.final_delivery_formats_list.item(i)
            item.setSelected(item.text().lower() in final_formats)
            
        # Daily/Review Formats
        daily_formats = media_config.get('daily_review_formats', [])
        for i in range(self.daily_review_formats_list.count()):
            item = self.daily_review_formats_list.item(i)
            item.setSelected(item.text().lower() in daily_formats)
            
        # Frame Rate
        frame_rate = str(media_config.get('default_frame_rate', 24))
        index = self.frame_rate_combo.findText(frame_rate)
        if index >= 0:
            self.frame_rate_combo.setCurrentIndex(index)
            
    def set_resolution_combo(self, combo, width_spin, height_spin, resolution_data):
        """Set resolution combo box and spin boxes from resolution data."""
        width = resolution_data.get('width', 1920)
        height = resolution_data.get('height', 1080)
        name = resolution_data.get('name', 'Custom')
        
        # Try to find matching predefined resolution
        resolution_text = f"{name} ({width}x{height})"
        index = combo.findText(resolution_text)
        
        if index >= 0:
            combo.setCurrentIndex(index)
        else:
            # Set to custom
            combo.setCurrentText("Custom")
            width_spin.setValue(width)
            height_spin.setValue(height)
            
    def reset_to_original(self):
        """Reset all form fields to original project configuration."""
        if self.original_project_config:
            self.load_project_config(self.original_project_config)
            
    def save_changes(self):
        """Save project changes and emit signal."""
        if not self.validate_form():
            return
            
        try:
            # Build updated project configuration
            updated_config = self.build_project_config()
            
            # Preserve original creation timestamp and update modification timestamp
            updated_config['_created_at'] = self.original_project_config.get('_created_at', datetime.now().isoformat())
            updated_config['_updated_at'] = datetime.now().isoformat()
            
            # Emit signal with updated configuration
            self.project_updated.emit(updated_config)
            
            # Close dialog
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error Saving Changes", 
                               f"Failed to save project changes:\n{str(e)}")
                               
    def validate_project_id(self):
        """Override to skip validation since ID is read-only in edit mode."""
        return True  # Always valid since it can't be changed
