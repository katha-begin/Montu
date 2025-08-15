"""
Project Creation Dialog for Ra: Task Creator

Comprehensive dialog for creating new project configurations with:
- Basic project information
- Project type selection (episode-based vs non-episode)
- Task types customization
- Timeline and budget settings
- Color pipeline configuration
- Drive mappings and path settings
"""

import re
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Any

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QDateEdit, QCheckBox, QPushButton, QGroupBox, QTabWidget,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
    QScrollArea, QWidget, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont, QIcon


class ProjectCreationDialog(QDialog):
    """
    Comprehensive project creation dialog with organized form sections.
    
    Follows Egyptian mythology naming conventions and integrates with
    existing Ra application architecture.
    """
    
    project_created = Signal(dict)  # Emitted when project is successfully created
    
    def __init__(self, parent=None, existing_projects: List[str] = None):
        """
        Initialize project creation dialog.
        
        Args:
            parent: Parent widget
            existing_projects: List of existing project IDs for uniqueness validation
        """
        super().__init__(parent)
        self.existing_projects = existing_projects or []
        self.project_config = {}
        
        self.setup_ui()
        self.setup_connections()
        self.load_defaults()
        
    def setup_ui(self):
        """Set up the comprehensive user interface."""
        self.setWindowTitle("Ra: Create New Project")
        self.setModal(True)
        self.setMinimumSize(800, 700)
        self.resize(900, 800)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header
        header_label = QLabel("Create New Project Configuration")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Scroll area for form content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Form widget
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(15)
        
        # Basic Information Section
        basic_info_group = self.create_basic_info_section()
        form_layout.addWidget(basic_info_group)
        
        # Project Type Section
        project_type_group = self.create_project_type_section()
        form_layout.addWidget(project_type_group)
        
        # Task Types Section
        task_types_group = self.create_task_types_section()
        form_layout.addWidget(task_types_group)
        
        # Timeline and Budget Section
        timeline_budget_group = self.create_timeline_budget_section()
        form_layout.addWidget(timeline_budget_group)
        
        # Color Pipeline Section
        color_pipeline_group = self.create_color_pipeline_section()
        form_layout.addWidget(color_pipeline_group)
        
        # Drive Mappings Section
        drive_mappings_group = self.create_drive_mappings_section()
        form_layout.addWidget(drive_mappings_group)

        # Filename Patterns Section
        filename_patterns_group = self.create_filename_patterns_section()
        form_layout.addWidget(filename_patterns_group)

        # Path Templates Section
        path_templates_group = self.create_path_templates_section()
        form_layout.addWidget(path_templates_group)

        # Media & Resolution Configuration Section
        media_config_group = self.create_media_configuration_section()
        form_layout.addWidget(media_config_group)
        
        scroll_area.setWidget(form_widget)
        layout.addWidget(scroll_area)
        
        # Validation feedback area
        self.validation_label = QLabel()
        self.validation_label.setStyleSheet("color: red; font-weight: bold;")
        self.validation_label.setWordWrap(True)
        self.validation_label.hide()
        layout.addWidget(self.validation_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.create_button = QPushButton("Create Project")
        self.create_button.setDefault(True)
        self.create_button.clicked.connect(self.create_project)
        button_layout.addWidget(self.create_button)
        
        layout.addLayout(button_layout)
        
    def create_basic_info_section(self) -> QGroupBox:
        """Create basic project information section."""
        group = QGroupBox("Basic Project Information")
        layout = QFormLayout(group)
        
        # Project Name
        self.project_name_edit = QLineEdit()
        self.project_name_edit.setPlaceholderText("e.g., Sky Wars Season 2")
        self.project_name_edit.textChanged.connect(self.on_project_name_changed)
        layout.addRow("Project Name*:", self.project_name_edit)
        
        # Project ID (auto-generated with manual override)
        id_layout = QHBoxLayout()
        self.project_id_edit = QLineEdit()
        self.project_id_edit.setPlaceholderText("Auto-generated from name")
        self.project_id_edit.textChanged.connect(self.validate_project_id)
        id_layout.addWidget(self.project_id_edit)
        
        self.auto_generate_id_btn = QPushButton("Auto-Generate")
        self.auto_generate_id_btn.clicked.connect(self.auto_generate_project_id)
        id_layout.addWidget(self.auto_generate_id_btn)
        
        layout.addRow("Project ID*:", id_layout)
        
        # Project Description
        self.project_description_edit = QTextEdit()
        self.project_description_edit.setMaximumHeight(80)
        self.project_description_edit.setPlaceholderText("Brief description of the project...")
        layout.addRow("Description:", self.project_description_edit)
        
        return group
        
    def create_project_type_section(self) -> QGroupBox:
        """Create project type selection section."""
        group = QGroupBox("Project Type Configuration")
        layout = QVBoxLayout(group)
        
        # Project type selection
        type_layout = QHBoxLayout()
        
        self.episode_based_radio = QCheckBox("Episode-based Project")
        self.episode_based_radio.setChecked(True)
        self.episode_based_radio.toggled.connect(self.on_project_type_changed)
        type_layout.addWidget(self.episode_based_radio)
        
        self.non_episode_radio = QCheckBox("Non-episode Project")
        self.non_episode_radio.toggled.connect(self.on_project_type_changed)
        type_layout.addWidget(self.non_episode_radio)
        
        type_layout.addStretch()
        layout.addLayout(type_layout)
        
        # Type description
        self.type_description_label = QLabel(
            "Episode-based: Full episode/sequence/shot hierarchy (like SWA)\n"
            "Non-episode: Simplified shot-based or asset-based structure"
        )
        self.type_description_label.setStyleSheet("color: #666666; font-style: italic;")
        layout.addWidget(self.type_description_label)
        
        return group
        
    def create_task_types_section(self) -> QGroupBox:
        """Create task types customization section."""
        group = QGroupBox("Task Types Configuration")
        layout = QVBoxLayout(group)
        
        # Instructions
        instructions = QLabel("Customize the task types available for this project:")
        instructions.setStyleSheet("font-weight: bold;")
        layout.addWidget(instructions)
        
        # Task types list with add/remove functionality
        list_layout = QHBoxLayout()
        
        # Available task types list
        self.task_types_list = QListWidget()
        self.task_types_list.setMaximumHeight(150)
        list_layout.addWidget(self.task_types_list)
        
        # Control buttons
        button_layout = QVBoxLayout()
        
        self.add_task_type_btn = QPushButton("Add Custom")
        self.add_task_type_btn.clicked.connect(self.add_custom_task_type)
        button_layout.addWidget(self.add_task_type_btn)
        
        self.remove_task_type_btn = QPushButton("Remove Selected")
        self.remove_task_type_btn.clicked.connect(self.remove_selected_task_type)
        button_layout.addWidget(self.remove_task_type_btn)
        
        self.reset_task_types_btn = QPushButton("Reset to Defaults")
        self.reset_task_types_btn.clicked.connect(self.reset_task_types)
        button_layout.addWidget(self.reset_task_types_btn)
        
        button_layout.addStretch()
        list_layout.addLayout(button_layout)
        
        layout.addLayout(list_layout)

        return group

    def create_timeline_budget_section(self) -> QGroupBox:
        """Create timeline and budget configuration section."""
        group = QGroupBox("Timeline & Budget Configuration")
        layout = QFormLayout(group)

        # Timeline settings
        timeline_layout = QHBoxLayout()

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)
        timeline_layout.addWidget(QLabel("Start:"))
        timeline_layout.addWidget(self.start_date_edit)

        timeline_layout.addSpacing(20)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate().addMonths(6))
        self.end_date_edit.setCalendarPopup(True)
        timeline_layout.addWidget(QLabel("End:"))
        timeline_layout.addWidget(self.end_date_edit)

        timeline_layout.addStretch()
        layout.addRow("Project Timeline:", timeline_layout)

        # Budget settings
        budget_layout = QHBoxLayout()

        self.total_mandays_spin = QDoubleSpinBox()
        self.total_mandays_spin.setRange(0, 10000)
        self.total_mandays_spin.setSuffix(" days")
        self.total_mandays_spin.setValue(100)
        budget_layout.addWidget(self.total_mandays_spin)

        budget_layout.addStretch()
        layout.addRow("Total Mandays:", budget_layout)

        return group

    def create_color_pipeline_section(self) -> QGroupBox:
        """Create color pipeline configuration section."""
        group = QGroupBox("Color Pipeline Configuration")
        layout = QFormLayout(group)

        # OCIO Config Path
        ocio_layout = QHBoxLayout()
        self.ocio_config_edit = QLineEdit()
        self.ocio_config_edit.setPlaceholderText("Path to OCIO config file...")
        ocio_layout.addWidget(self.ocio_config_edit)

        self.browse_ocio_btn = QPushButton("Browse...")
        self.browse_ocio_btn.clicked.connect(self.browse_ocio_config)
        ocio_layout.addWidget(self.browse_ocio_btn)

        layout.addRow("OCIO Config Path:", ocio_layout)

        # Working Colorspace
        self.working_colorspace_combo = QComboBox()
        self.working_colorspace_combo.addItems([
            "ACEScg", "ACES2065-1", "Rec.709", "sRGB", "Linear Rec.709"
        ])
        self.working_colorspace_combo.setCurrentText("ACEScg")
        layout.addRow("Working Colorspace:", self.working_colorspace_combo)

        # Display Colorspace
        self.display_colorspace_combo = QComboBox()
        self.display_colorspace_combo.addItems([
            "sRGB", "Rec.709", "P3-D65", "Rec.2020"
        ])
        self.display_colorspace_combo.setCurrentText("sRGB")
        layout.addRow("Display Colorspace:", self.display_colorspace_combo)

        return group

    def create_drive_mappings_section(self) -> QGroupBox:
        """Create drive mappings configuration section."""
        group = QGroupBox("Drive Mappings & Path Configuration")
        layout = QFormLayout(group)

        # Drive mappings
        self.working_files_edit = QLineEdit("V:")
        layout.addRow("Working Files Drive:", self.working_files_edit)

        self.render_outputs_edit = QLineEdit("W:")
        layout.addRow("Render Outputs Drive:", self.render_outputs_edit)

        self.media_files_edit = QLineEdit("E:")
        layout.addRow("Media Files Drive:", self.media_files_edit)

        self.cache_files_edit = QLineEdit("E:")
        layout.addRow("Cache Files Drive:", self.cache_files_edit)

        self.backup_files_edit = QLineEdit("E:")
        layout.addRow("Backup Files Drive:", self.backup_files_edit)

        return group

    def setup_connections(self):
        """Set up signal connections."""
        # Make checkboxes mutually exclusive
        self.episode_based_radio.toggled.connect(
            lambda checked: self.non_episode_radio.setChecked(not checked) if checked else None
        )
        self.non_episode_radio.toggled.connect(
            lambda checked: self.episode_based_radio.setChecked(not checked) if checked else None
        )

    def load_defaults(self):
        """Load default values and populate form fields."""
        # Load default task types
        self.default_task_types = [
            "modeling", "rigging", "animation", "layout",
            "lighting", "comp", "fx", "lookdev"
        ]
        self.reset_task_types()

        # Load default filename patterns
        self.reset_filename_patterns()

        # Load default path templates
        self.reset_path_templates()

    def on_project_name_changed(self):
        """Handle project name changes and auto-generate ID if needed."""
        if not self.project_id_edit.text() or self.project_id_edit.placeholderText() == "Auto-generated from name":
            self.auto_generate_project_id()

    def auto_generate_project_id(self):
        """Generate project ID from project name using intelligent abbreviation."""
        name = self.project_name_edit.text().strip()
        if not name:
            self.project_id_edit.clear()
            return

        # Intelligent abbreviation logic
        project_id = self.generate_project_abbreviation(name)
        self.project_id_edit.setText(project_id)

    def generate_project_abbreviation(self, name: str) -> str:
        """
        Generate intelligent project abbreviation from name.

        Examples:
        - "Sky Wars Season 2" -> "SWS2"
        - "Avatar Water Scenes" -> "AWS"
        - "The Matrix Reloaded" -> "TMR"
        """
        # Remove common words and articles
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}

        words = re.findall(r'\b\w+\b', name.lower())
        filtered_words = [word for word in words if word not in common_words]

        if not filtered_words:
            filtered_words = words  # Fallback to all words if all were filtered

        # Generate abbreviation
        abbreviation = ""

        # Take first letter of each significant word
        for word in filtered_words:
            if word.isdigit():
                abbreviation += word  # Keep numbers as-is
            else:
                abbreviation += word[0].upper()

        # Limit length and ensure it's reasonable
        if len(abbreviation) > 6:
            abbreviation = abbreviation[:6]
        elif len(abbreviation) < 2:
            # Fallback: take first 3 characters of first word
            abbreviation = filtered_words[0][:3].upper() if filtered_words else "PRJ"

        return abbreviation

    def validate_project_id(self):
        """Validate project ID format and uniqueness."""
        project_id = self.project_id_edit.text().strip()

        if not project_id:
            self.show_validation_error("")
            return False

        # Format validation
        if not re.match(r'^[A-Za-z0-9_-]+$', project_id):
            self.show_validation_error("Project ID can only contain letters, numbers, underscores, and hyphens.")
            return False

        if len(project_id) > 20:
            self.show_validation_error("Project ID must be 20 characters or less.")
            return False

        # Uniqueness validation
        if project_id.upper() in [p.upper() for p in self.existing_projects]:
            self.show_validation_error(f"Project ID '{project_id}' already exists. Please choose a different ID.")
            return False

        self.show_validation_error("")
        return True

    def on_project_type_changed(self):
        """Handle project type selection changes."""
        # Update templates based on project type
        if hasattr(self, 'path_template_edits') and hasattr(self, 'filename_pattern_edits'):
            if self.episode_based_radio.isChecked():
                # Restore episode-based templates
                self.reset_path_templates()
                self.reset_filename_patterns()
            else:
                # Adjust for non-episode project
                for template_key, edit in self.path_template_edits.items():
                    current_template = edit.text()
                    # Remove episode components
                    adjusted_template = current_template.replace("/{episode}", "").replace("{episode}/", "")
                    edit.setText(adjusted_template)

                for pattern_key, edit in self.filename_pattern_edits.items():
                    current_pattern = edit.text()
                    # Remove episode components
                    adjusted_pattern = current_pattern.replace("{episode}_", "")
                    edit.setText(adjusted_pattern)

    def add_custom_task_type(self):
        """Add a custom task type to the list."""
        from PySide6.QtWidgets import QInputDialog

        task_type, ok = QInputDialog.getText(
            self,
            "Add Custom Task Type",
            "Enter task type name:",
            text=""
        )

        if ok and task_type.strip():
            task_type = task_type.strip().lower()

            # Check if already exists
            existing_types = [self.task_types_list.item(i).text()
                            for i in range(self.task_types_list.count())]

            if task_type not in existing_types:
                item = QListWidgetItem(task_type)
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                self.task_types_list.addItem(item)
            else:
                QMessageBox.information(self, "Task Type Exists",
                                      f"Task type '{task_type}' already exists.")

    def remove_selected_task_type(self):
        """Remove selected task type from the list."""
        current_item = self.task_types_list.currentItem()
        if current_item:
            # Ensure at least one task type remains
            if self.task_types_list.count() <= 1:
                QMessageBox.warning(self, "Cannot Remove",
                                  "At least one task type must be specified.")
                return

            row = self.task_types_list.row(current_item)
            self.task_types_list.takeItem(row)

    def reset_task_types(self):
        """Reset task types to default VFX pipeline types."""
        self.task_types_list.clear()

        for task_type in self.default_task_types:
            item = QListWidgetItem(task_type)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.task_types_list.addItem(item)

    def browse_ocio_config(self):
        """Browse for OCIO configuration file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select OCIO Configuration File",
            "",
            "OCIO Config Files (*.ocio);;All Files (*)"
        )

        if file_path:
            self.ocio_config_edit.setText(file_path)

    def reset_filename_patterns(self):
        """Reset filename patterns to defaults."""
        for key, pattern in self.default_filename_patterns.items():
            if key in self.filename_pattern_edits:
                self.filename_pattern_edits[key].setText(pattern)

    def reset_path_templates(self):
        """Reset path templates to defaults."""
        for key, template in self.default_path_templates.items():
            if key in self.path_template_edits:
                self.path_template_edits[key].setText(template)

    def validate_filename_patterns(self):
        """Validate filename patterns for required variables."""
        errors = []
        required_vars = ["{task}", "{version}"]

        for pattern_name, edit in self.filename_pattern_edits.items():
            pattern = edit.text().strip()
            if pattern:
                missing_vars = [var for var in required_vars if var not in pattern]
                if missing_vars:
                    errors.append(f"{pattern_name}: Missing {', '.join(missing_vars)}")

        if errors:
            self.filename_patterns_validation_label.setText("⚠️ " + "; ".join(errors))
            self.filename_patterns_validation_label.show()
            return False
        else:
            self.filename_patterns_validation_label.hide()
            return True

    def validate_path_templates(self):
        """Validate path templates for required variables."""
        errors = []
        required_vars = {
            "working_file": ["{project}", "{task}", "{drive_working}"],
            "render_output": ["{project}", "{task}", "{drive_render}"],
            "media_file": ["{project}", "{task}", "{drive_media}"],
            "cache_file": ["{project}", "{task}", "{drive_cache}"],
            "submission": ["{project}", "{task}", "{drive_render}"]
        }

        for template_name, edit in self.path_template_edits.items():
            template = edit.text().strip()
            if template and template_name in required_vars:
                missing_vars = [var for var in required_vars[template_name] if var not in template]
                if missing_vars:
                    errors.append(f"{template_name}: Missing {', '.join(missing_vars)}")

        if errors:
            self.path_templates_validation_label.setText("⚠️ " + "; ".join(errors))
            self.path_templates_validation_label.show()
            return False
        else:
            self.path_templates_validation_label.hide()
            return True

    def preview_path_templates(self):
        """Show preview of generated paths."""
        project_id = self.project_id_edit.text().strip() or "PROJECT"

        # Sample data for preview
        sample_data = {
            "project": project_id,
            "episode": "ep01",
            "sequence_clean": "sq010",
            "shot_clean": "sh020",
            "task": "lighting",
            "version": "001",
            "version_dir": "version",
            "middle_path": "all/scene",
            "drive_working": "V:",
            "drive_render": "W:",
            "drive_media": "E:",
            "drive_cache": "E:",
            "client": "Client",
            "client_version": "v001",
            "filename": "sample_file.ma"
        }

        preview_text = "Path Preview Examples:\n\n"

        for template_name, edit in self.path_template_edits.items():
            template = edit.text().strip()
            if template:
                try:
                    # Simple template substitution for preview
                    preview_path = template.format(**sample_data)
                    preview_text += f"{template_name}:\n{preview_path}\n\n"
                except KeyError as e:
                    preview_text += f"{template_name}:\nError - Missing variable {e}\n\n"

        QMessageBox.information(self, "Path Templates Preview", preview_text)

    def on_final_resolution_changed(self):
        """Handle final delivery resolution selection changes."""
        is_custom = self.final_delivery_resolution_combo.currentText() == "Custom"

        # Show/hide custom resolution inputs
        self.final_width_spin.setVisible(is_custom)
        self.final_height_spin.setVisible(is_custom)

        # Update spinbox values based on selection
        if not is_custom:
            resolution_map = {
                "4K UHD (3840x2160)": (3840, 2160),
                "4K DCI (4096x2160)": (4096, 2160),
                "2K DCI (2048x1080)": (2048, 1080),
                "HD 1080p (1920x1080)": (1920, 1080),
                "HD 720p (1280x720)": (1280, 720)
            }

            current_text = self.final_delivery_resolution_combo.currentText()
            if current_text in resolution_map:
                width, height = resolution_map[current_text]
                self.final_width_spin.setValue(width)
                self.final_height_spin.setValue(height)

    def on_daily_resolution_changed(self):
        """Handle daily/review resolution selection changes."""
        is_custom = self.daily_review_resolution_combo.currentText() == "Custom"

        # Show/hide custom resolution inputs
        self.daily_width_spin.setVisible(is_custom)
        self.daily_height_spin.setVisible(is_custom)

        # Update spinbox values based on selection
        if not is_custom:
            resolution_map = {
                "4K UHD (3840x2160)": (3840, 2160),
                "4K DCI (4096x2160)": (4096, 2160),
                "2K DCI (2048x1080)": (2048, 1080),
                "HD 1080p (1920x1080)": (1920, 1080),
                "HD 720p (1280x720)": (1280, 720)
            }

            current_text = self.daily_review_resolution_combo.currentText()
            if current_text in resolution_map:
                width, height = resolution_map[current_text]
                self.daily_width_spin.setValue(width)
                self.daily_height_spin.setValue(height)

    def show_validation_error(self, message: str):
        """Show or hide validation error message."""
        if message:
            self.validation_label.setText(message)
            self.validation_label.show()
        else:
            self.validation_label.hide()

    def validate_form(self) -> bool:
        """Validate all form fields."""
        # Project name validation
        if not self.project_name_edit.text().strip():
            self.show_validation_error("Project name is required.")
            return False

        # Project ID validation
        if not self.validate_project_id():
            return False

        # Timeline validation
        if self.start_date_edit.date() >= self.end_date_edit.date():
            self.show_validation_error("Project end date must be after start date.")
            return False

        # Task types validation
        if self.task_types_list.count() == 0:
            self.show_validation_error("At least one task type must be specified.")
            return False

        # OCIO config validation (if specified)
        ocio_path = self.ocio_config_edit.text().strip()
        if ocio_path and not Path(ocio_path).exists():
            self.show_validation_error(f"OCIO config file not found: {ocio_path}")
            return False

        # Filename patterns validation
        if not self.validate_filename_patterns():
            self.show_validation_error("Please fix filename pattern validation errors.")
            return False

        # Path templates validation
        if not self.validate_path_templates():
            self.show_validation_error("Please fix path template validation errors.")
            return False

        # Media configuration validation
        final_formats = [item.text() for item in self.final_delivery_formats_list.selectedItems()]
        daily_formats = [item.text() for item in self.daily_review_formats_list.selectedItems()]

        if not final_formats:
            self.show_validation_error("At least one final delivery format must be selected.")
            return False

        if not daily_formats:
            self.show_validation_error("At least one daily/review format must be selected.")
            return False

        self.show_validation_error("")
        return True

    def create_project(self):
        """Create the project configuration and emit signal."""
        if not self.validate_form():
            return

        try:
            # Build project configuration from form data
            project_config = self.build_project_config()

            # Emit signal with project configuration
            self.project_created.emit(project_config)

            # Close dialog
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error Creating Project",
                               f"Failed to create project configuration:\n{str(e)}")

    def build_project_config(self) -> Dict[str, Any]:
        """Build complete project configuration from form data."""
        # Get current timestamp
        timestamp = datetime.now().isoformat()

        # Get task types from list
        task_types = []
        for i in range(self.task_types_list.count()):
            task_types.append(self.task_types_list.item(i).text())

        # Build configuration based on SWA template structure
        project_config = {
            "_id": self.project_id_edit.text().strip(),
            "name": self.project_name_edit.text().strip(),
            "description": self.project_description_edit.toPlainText().strip(),

            # Drive mappings
            "drive_mapping": {
                "working_files": self.working_files_edit.text().strip(),
                "render_outputs": self.render_outputs_edit.text().strip(),
                "media_files": self.media_files_edit.text().strip(),
                "cache_files": self.cache_files_edit.text().strip(),
                "backup_files": self.backup_files_edit.text().strip()
            },

            # Path segments (using SWA defaults)
            "path_segments": {
                "middle_path": "all/scene",
                "version_dir": "version",
                "work_dir": "work",
                "publish_dir": "publish",
                "cache_dir": "cache"
            },

            # Templates (from form)
            "templates": {
                "working_file": self.path_template_edits["working_file"].text().strip(),
                "render_output": self.path_template_edits["render_output"].text().strip(),
                "media_file": self.path_template_edits["media_file"].text().strip(),
                "cache_file": self.path_template_edits["cache_file"].text().strip(),
                "submission": self.path_template_edits["submission"].text().strip()
            },

            # Filename patterns (from form)
            "filename_patterns": {
                "maya_scene": self.filename_pattern_edits["maya_scene"].text().strip(),
                "nuke_script": self.filename_pattern_edits["nuke_script"].text().strip(),
                "houdini_scene": self.filename_pattern_edits["houdini_scene"].text().strip(),
                "blender_scene": self.filename_pattern_edits["blender_scene"].text().strip(),
                "render_sequence": self.filename_pattern_edits["render_sequence"].text().strip(),
                "playblast": self.filename_pattern_edits["playblast"].text().strip(),
                "thumbnail": self.filename_pattern_edits["thumbnail"].text().strip()
            },

            # Name cleaning rules (project-specific, can be customized)
            "name_cleaning_rules": self.build_name_cleaning_rules(),

            # Version settings (using SWA defaults)
            "version_settings": {
                "padding": 3,
                "start_version": 1,
                "increment": 1,
                "format": "v{version:03d}"
            },

            # Task settings with customized task types
            "task_settings": {
                "default_file_extensions": self.build_default_file_extensions(task_types),
                "render_formats": self.build_render_formats(task_types)
            },

            # Milestones (using SWA defaults)
            "milestones": [
                "not_started", "single_frame", "low_quality",
                "final_render", "final_comp", "approved"
            ],

            # Custom task types from form
            "task_types": task_types,

            # Priority levels (using SWA defaults)
            "priority_levels": ["low", "medium", "high", "urgent"],

            # Client settings (using SWA structure)
            "client_settings": {
                "version_reset": True,
                "default_client": f"{self.project_id_edit.text().strip()}_Client",
                "delivery_formats": ["mov", "mp4"],
                "approval_required": True
            },

            # Platform settings (using project-specific paths)
            "platform_settings": self.build_platform_settings(),

            # Frame settings (using SWA defaults)
            "frame_settings": {
                "padding": 4,
                "default_start": 1001,
                "default_fps": 24
            },

            # Extended fields - Project Budget
            "project_budget": {
                "total_mandays": self.total_mandays_spin.value(),
                "allocated_mandays": 0,
                "remaining_mandays": self.total_mandays_spin.value()
            },

            # Extended fields - Project Timeline
            "project_timeline": {
                "start_date": self.start_date_edit.date().toString("yyyy-MM-dd"),
                "end_date": self.end_date_edit.date().toString("yyyy-MM-dd")
            },

            # Extended fields - Color Pipeline
            "color_pipeline": {
                "ocio_config_path": self.ocio_config_edit.text().strip(),
                "working_colorspace": self.working_colorspace_combo.currentText(),
                "display_colorspace": self.display_colorspace_combo.currentText()
            },

            # Extended fields - Media Configuration
            "media_configuration": self.build_media_configuration(),

            # Metadata
            "_created_at": timestamp,
            "_updated_at": timestamp
        }

        # Adjust templates for non-episode projects
        if not self.episode_based_radio.isChecked():
            project_config = self.adjust_for_non_episode_project(project_config)

        return project_config

    def build_name_cleaning_rules(self) -> Dict[str, str]:
        """Build name cleaning rules based on project type and ID."""
        project_id = self.project_id_edit.text().strip()

        if self.episode_based_radio.isChecked():
            # Episode-based project rules (similar to SWA)
            return {
                "sequence_pattern": f"^{project_id}_Ep[0-9]+_(.+)$",
                "sequence_replacement": "\\1",
                "shot_pattern": f"^{project_id}_Ep[0-9]+_(.+)$",
                "shot_replacement": "\\1",
                "episode_pattern": "^(Ep[0-9]+)$",
                "episode_replacement": "\\1"
            }
        else:
            # Non-episode project rules (simplified)
            return {
                "sequence_pattern": f"^{project_id}_(.+)$",
                "sequence_replacement": "\\1",
                "shot_pattern": f"^{project_id}_(.+)$",
                "shot_replacement": "\\1",
                "episode_pattern": "^(.+)$",
                "episode_replacement": "\\1"
            }

    def build_default_file_extensions(self, task_types: List[str]) -> Dict[str, str]:
        """Build default file extensions mapping for task types."""
        # Standard VFX pipeline file extensions
        extension_mapping = {
            "lighting": ".ma",
            "comp": ".nk",
            "modeling": ".ma",
            "rigging": ".ma",
            "animation": ".ma",
            "fx": ".hip",
            "lookdev": ".ma",
            "layout": ".ma",
            "texturing": ".ma",
            "matte_painting": ".psd",
            "concept": ".psd",
            "previz": ".ma"
        }

        # Build mapping for selected task types
        result = {}
        for task_type in task_types:
            result[task_type] = extension_mapping.get(task_type, ".ma")  # Default to Maya

        return result

    def build_render_formats(self, task_types: List[str]) -> Dict[str, List[str]]:
        """Build render formats mapping for task types."""
        # Standard VFX pipeline render formats
        format_mapping = {
            "lighting": ["exr", "jpg"],
            "comp": ["exr", "mov", "jpg"],
            "fx": ["exr", "mov"],
            "lookdev": ["exr", "jpg"],
            "layout": ["mov", "jpg"],
            "animation": ["mov", "jpg"],
            "modeling": ["jpg", "png"],
            "rigging": ["jpg", "png"],
            "texturing": ["jpg", "png"],
            "matte_painting": ["exr", "jpg", "png"],
            "concept": ["jpg", "png"],
            "previz": ["mov", "jpg"]
        }

        # Build mapping for selected task types
        result = {}
        for task_type in task_types:
            result[task_type] = format_mapping.get(task_type, ["jpg"])  # Default to JPG

        return result

    def build_platform_settings(self) -> Dict[str, Dict[str, str]]:
        """Build platform-specific path settings."""
        project_id = self.project_id_edit.text().strip()

        return {
            "windows": {
                "working_root": f"{self.working_files_edit.text().strip()}/{project_id}",
                "render_root": f"{self.render_outputs_edit.text().strip()}/{project_id}",
                "media_root": f"{self.media_files_edit.text().strip()}/{project_id}"
            },
            "linux": {
                "working_root": f"/mnt/projects/{project_id}",
                "render_root": f"/mnt/renders/{project_id}",
                "media_root": f"/mnt/media/{project_id}"
            }
        }

    def adjust_for_non_episode_project(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust configuration for non-episode based projects."""
        # Remove episode components from templates
        for template_key, template_value in config["templates"].items():
            # Remove {episode}/ from paths
            config["templates"][template_key] = template_value.replace("/{episode}", "").replace("{episode}/", "")

        # Remove episode components from filename patterns
        for pattern_key, pattern_value in config["filename_patterns"].items():
            # Remove {episode}_ from filenames
            config["filename_patterns"][pattern_key] = pattern_value.replace("{episode}_", "")

        return config

    def build_media_configuration(self) -> Dict[str, Any]:
        """Build media configuration from form data."""
        # Get final delivery resolution
        final_resolution = self.get_resolution_from_combo(
            self.final_delivery_resolution_combo,
            self.final_width_spin,
            self.final_height_spin
        )

        # Get daily/review resolution
        daily_resolution = self.get_resolution_from_combo(
            self.daily_review_resolution_combo,
            self.daily_width_spin,
            self.daily_height_spin
        )

        # Get selected formats
        final_formats = [item.text().lower() for item in self.final_delivery_formats_list.selectedItems()]
        daily_formats = [item.text().lower() for item in self.daily_review_formats_list.selectedItems()]

        # Get frame rate
        frame_rate = float(self.frame_rate_combo.currentText())

        return {
            "final_delivery_resolution": final_resolution,
            "daily_review_resolution": daily_resolution,
            "final_delivery_formats": final_formats,
            "daily_review_formats": daily_formats,
            "default_frame_rate": frame_rate
        }

    def get_resolution_from_combo(self, combo: QComboBox, width_spin: QSpinBox, height_spin: QSpinBox) -> Dict[str, Any]:
        """Get resolution data from combo box and spin boxes."""
        current_text = combo.currentText()

        if current_text == "Custom":
            return {
                "width": width_spin.value(),
                "height": height_spin.value(),
                "name": "Custom"
            }
        else:
            # Parse predefined resolution
            resolution_map = {
                "4K UHD (3840x2160)": {"width": 3840, "height": 2160, "name": "4K UHD"},
                "4K DCI (4096x2160)": {"width": 4096, "height": 2160, "name": "4K DCI"},
                "2K DCI (2048x1080)": {"width": 2048, "height": 1080, "name": "2K DCI"},
                "HD 1080p (1920x1080)": {"width": 1920, "height": 1080, "name": "HD 1080p"},
                "HD 720p (1280x720)": {"width": 1280, "height": 720, "name": "HD 720p"}
            }

            return resolution_map.get(current_text, {"width": 1920, "height": 1080, "name": "HD 1080p"})

    def create_filename_patterns_section(self) -> QGroupBox:
        """Create filename patterns configuration section."""
        group = QGroupBox("Filename Patterns Configuration")
        layout = QFormLayout(group)

        # Instructions
        instructions = QLabel("Customize filename patterns for different file types:")
        instructions.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addRow(instructions)

        # Default patterns from SWA
        self.default_filename_patterns = {
            "maya_scene": "{episode}_{sequence_clean}_{shot_clean}_{task}_master_v{version}.ma",
            "nuke_script": "{episode}_{sequence_clean}_{shot_clean}_{task}_master_v{version}.nk",
            "houdini_scene": "{episode}_{sequence_clean}_{shot_clean}_{task}_master_v{version}.hip",
            "blender_scene": "{episode}_{sequence_clean}_{shot_clean}_{task}_master_v{version}.blend",
            "render_sequence": "{episode}_{sequence_clean}_{shot_clean}_{task}_v{version}.{frame}.{ext}",
            "playblast": "{episode}_{sequence_clean}_{shot_clean}_{task}_v{version}_playblast.mov",
            "thumbnail": "{episode}_{sequence_clean}_{shot_clean}_{task}_v{version}_thumb.jpg"
        }

        # Create editable fields for each pattern
        self.filename_pattern_edits = {}

        self.filename_pattern_edits["maya_scene"] = QLineEdit()
        self.filename_pattern_edits["maya_scene"].textChanged.connect(self.validate_filename_patterns)
        layout.addRow("Maya Scene:", self.filename_pattern_edits["maya_scene"])

        self.filename_pattern_edits["nuke_script"] = QLineEdit()
        self.filename_pattern_edits["nuke_script"].textChanged.connect(self.validate_filename_patterns)
        layout.addRow("Nuke Script:", self.filename_pattern_edits["nuke_script"])

        self.filename_pattern_edits["houdini_scene"] = QLineEdit()
        self.filename_pattern_edits["houdini_scene"].textChanged.connect(self.validate_filename_patterns)
        layout.addRow("Houdini Scene:", self.filename_pattern_edits["houdini_scene"])

        self.filename_pattern_edits["blender_scene"] = QLineEdit()
        self.filename_pattern_edits["blender_scene"].textChanged.connect(self.validate_filename_patterns)
        layout.addRow("Blender Scene:", self.filename_pattern_edits["blender_scene"])

        self.filename_pattern_edits["render_sequence"] = QLineEdit()
        self.filename_pattern_edits["render_sequence"].textChanged.connect(self.validate_filename_patterns)
        layout.addRow("Render Sequence:", self.filename_pattern_edits["render_sequence"])

        self.filename_pattern_edits["playblast"] = QLineEdit()
        self.filename_pattern_edits["playblast"].textChanged.connect(self.validate_filename_patterns)
        layout.addRow("Playblast:", self.filename_pattern_edits["playblast"])

        self.filename_pattern_edits["thumbnail"] = QLineEdit()
        self.filename_pattern_edits["thumbnail"].textChanged.connect(self.validate_filename_patterns)
        layout.addRow("Thumbnail:", self.filename_pattern_edits["thumbnail"])

        # Validation feedback
        self.filename_patterns_validation_label = QLabel()
        self.filename_patterns_validation_label.setStyleSheet("color: red; font-weight: bold;")
        self.filename_patterns_validation_label.setWordWrap(True)
        self.filename_patterns_validation_label.hide()
        layout.addRow(self.filename_patterns_validation_label)

        # Reset button
        reset_patterns_layout = QHBoxLayout()
        reset_patterns_layout.addStretch()

        self.reset_filename_patterns_btn = QPushButton("Reset to Defaults")
        self.reset_filename_patterns_btn.clicked.connect(self.reset_filename_patterns)
        reset_patterns_layout.addWidget(self.reset_filename_patterns_btn)

        layout.addRow(reset_patterns_layout)

        return group

    def create_path_templates_section(self) -> QGroupBox:
        """Create path templates configuration section."""
        group = QGroupBox("Path Templates Configuration")
        layout = QFormLayout(group)

        # Instructions
        instructions = QLabel("Customize path templates for different file types:")
        instructions.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addRow(instructions)

        # Default templates from SWA
        self.default_path_templates = {
            "working_file": "{drive_working}/{project}/{middle_path}/{episode}/{sequence_clean}/{shot_clean}/{task}/{version_dir}/{filename}",
            "render_output": "{drive_render}/{project}/{middle_path}/{episode}/{sequence_clean}/{shot_clean}/{task}/{version_dir}/v{version}/",
            "media_file": "{drive_media}/{project}/{middle_path}/{episode}/{sequence_clean}/{shot_clean}/{task}/{version_dir}/v{version}/media/",
            "cache_file": "{drive_cache}/{project}/{middle_path}/{episode}/{sequence_clean}/{shot_clean}/{task}/cache/",
            "submission": "{drive_render}/{project}/deliveries/{client}/{episode}/{sequence_clean}/{shot_clean}/{task}/v{client_version}/"
        }

        # Create editable fields for each template
        self.path_template_edits = {}

        self.path_template_edits["working_file"] = QLineEdit()
        self.path_template_edits["working_file"].textChanged.connect(self.validate_path_templates)
        layout.addRow("Working File:", self.path_template_edits["working_file"])

        self.path_template_edits["render_output"] = QLineEdit()
        self.path_template_edits["render_output"].textChanged.connect(self.validate_path_templates)
        layout.addRow("Render Output:", self.path_template_edits["render_output"])

        self.path_template_edits["media_file"] = QLineEdit()
        self.path_template_edits["media_file"].textChanged.connect(self.validate_path_templates)
        layout.addRow("Media File:", self.path_template_edits["media_file"])

        self.path_template_edits["cache_file"] = QLineEdit()
        self.path_template_edits["cache_file"].textChanged.connect(self.validate_path_templates)
        layout.addRow("Cache File:", self.path_template_edits["cache_file"])

        self.path_template_edits["submission"] = QLineEdit()
        self.path_template_edits["submission"].textChanged.connect(self.validate_path_templates)
        layout.addRow("Submission:", self.path_template_edits["submission"])

        # Validation feedback
        self.path_templates_validation_label = QLabel()
        self.path_templates_validation_label.setStyleSheet("color: red; font-weight: bold;")
        self.path_templates_validation_label.setWordWrap(True)
        self.path_templates_validation_label.hide()
        layout.addRow(self.path_templates_validation_label)

        # Control buttons
        buttons_layout = QHBoxLayout()

        self.preview_paths_btn = QPushButton("Preview Paths")
        self.preview_paths_btn.clicked.connect(self.preview_path_templates)
        buttons_layout.addWidget(self.preview_paths_btn)

        buttons_layout.addStretch()

        self.reset_path_templates_btn = QPushButton("Reset to Defaults")
        self.reset_path_templates_btn.clicked.connect(self.reset_path_templates)
        buttons_layout.addWidget(self.reset_path_templates_btn)

        layout.addRow(buttons_layout)

        return group

    def create_media_configuration_section(self) -> QGroupBox:
        """Create media and resolution configuration section."""
        group = QGroupBox("Media & Resolution Configuration")
        layout = QFormLayout(group)

        # Final Delivery Resolution
        final_res_layout = QHBoxLayout()

        self.final_delivery_resolution_combo = QComboBox()
        self.final_delivery_resolution_combo.addItems([
            "4K UHD (3840x2160)", "4K DCI (4096x2160)", "2K DCI (2048x1080)",
            "HD 1080p (1920x1080)", "HD 720p (1280x720)", "Custom"
        ])
        self.final_delivery_resolution_combo.setCurrentText("4K UHD (3840x2160)")
        self.final_delivery_resolution_combo.currentTextChanged.connect(self.on_final_resolution_changed)
        final_res_layout.addWidget(self.final_delivery_resolution_combo)

        # Custom resolution inputs (initially hidden)
        self.final_width_spin = QSpinBox()
        self.final_width_spin.setRange(1, 8192)
        self.final_width_spin.setValue(3840)
        self.final_width_spin.setSuffix(" px")
        self.final_width_spin.hide()
        final_res_layout.addWidget(QLabel("W:"))
        final_res_layout.addWidget(self.final_width_spin)

        self.final_height_spin = QSpinBox()
        self.final_height_spin.setRange(1, 8192)
        self.final_height_spin.setValue(2160)
        self.final_height_spin.setSuffix(" px")
        self.final_height_spin.hide()
        final_res_layout.addWidget(QLabel("H:"))
        final_res_layout.addWidget(self.final_height_spin)

        final_res_layout.addStretch()
        layout.addRow("Final Delivery Resolution:", final_res_layout)

        # Daily/Review Resolution
        daily_res_layout = QHBoxLayout()

        self.daily_review_resolution_combo = QComboBox()
        self.daily_review_resolution_combo.addItems([
            "4K UHD (3840x2160)", "4K DCI (4096x2160)", "2K DCI (2048x1080)",
            "HD 1080p (1920x1080)", "HD 720p (1280x720)", "Custom"
        ])
        self.daily_review_resolution_combo.setCurrentText("HD 1080p (1920x1080)")
        self.daily_review_resolution_combo.currentTextChanged.connect(self.on_daily_resolution_changed)
        daily_res_layout.addWidget(self.daily_review_resolution_combo)

        # Custom resolution inputs (initially hidden)
        self.daily_width_spin = QSpinBox()
        self.daily_width_spin.setRange(1, 8192)
        self.daily_width_spin.setValue(1920)
        self.daily_width_spin.setSuffix(" px")
        self.daily_width_spin.hide()
        daily_res_layout.addWidget(QLabel("W:"))
        daily_res_layout.addWidget(self.daily_width_spin)

        self.daily_height_spin = QSpinBox()
        self.daily_height_spin.setRange(1, 8192)
        self.daily_height_spin.setValue(1080)
        self.daily_height_spin.setSuffix(" px")
        self.daily_height_spin.hide()
        daily_res_layout.addWidget(QLabel("H:"))
        daily_res_layout.addWidget(self.daily_height_spin)

        daily_res_layout.addStretch()
        layout.addRow("Daily/Review Resolution:", daily_res_layout)

        # Final Delivery Formats
        self.final_delivery_formats_list = QListWidget()
        self.final_delivery_formats_list.setMaximumHeight(100)
        self.final_delivery_formats_list.setSelectionMode(QListWidget.MultiSelection)

        final_formats = ["EXR", "MOV", "MP4", "MXF", "TIFF", "DPX"]
        for fmt in final_formats:
            item = QListWidgetItem(fmt)
            self.final_delivery_formats_list.addItem(item)
            if fmt in ["EXR", "MOV"]:  # Default selections
                item.setSelected(True)

        layout.addRow("Final Delivery Formats:", self.final_delivery_formats_list)

        # Daily/Review Formats
        self.daily_review_formats_list = QListWidget()
        self.daily_review_formats_list.setMaximumHeight(100)
        self.daily_review_formats_list.setSelectionMode(QListWidget.MultiSelection)

        daily_formats = ["MOV", "MP4", "JPEG", "PNG"]
        for fmt in daily_formats:
            item = QListWidgetItem(fmt)
            self.daily_review_formats_list.addItem(item)
            if fmt in ["MOV", "JPEG"]:  # Default selections
                item.setSelected(True)

        layout.addRow("Daily/Review Formats:", self.daily_review_formats_list)

        # Frame Rate
        self.frame_rate_combo = QComboBox()
        self.frame_rate_combo.addItems([
            "23.976", "24", "25", "29.97", "30", "50", "59.94", "60"
        ])
        self.frame_rate_combo.setCurrentText("24")
        layout.addRow("Frame Rate (fps):", self.frame_rate_combo)

        return group
