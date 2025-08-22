"""
Manual Task Creation Dialog for Ra: Task Creator

Comprehensive dialog for creating individual tasks with:
- Shot and Asset task type selection
- Dynamic form fields based on task type
- Asset dependencies and variants management
- Batch task creation capabilities
- Task templating and copy functionality
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Set

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QPushButton, QGroupBox, QTabWidget, QListWidget,
    QListWidgetItem, QMessageBox, QScrollArea, QWidget, QFrame,
    QSplitter, QTreeWidget, QTreeWidgetItem, QButtonGroup, QRadioButton,
    QProgressBar, QTextBrowser
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QIcon, QColor, QPalette

# Import directory manager for automatic directory creation
from ..core.directory_manager import DirectoryManager


class ManualTaskCreationDialog(QDialog):
    """
    Comprehensive manual task creation dialog for Ra: Task Creator.
    
    Supports both shot and asset task creation with dynamic form fields,
    validation, batch creation, and templating capabilities.
    """
    
    task_created = Signal(dict)  # Emitted when task is successfully created
    tasks_created = Signal(list)  # Emitted when multiple tasks are created
    
    def __init__(self, parent=None, db=None, existing_projects: List[str] = None):
        """
        Initialize manual task creation dialog.

        Args:
            parent: Parent widget
            db: Database instance for operations
            existing_projects: List of available project IDs
        """
        super().__init__(parent)
        self.db = db
        self.existing_projects = existing_projects or []
        self.current_project_config = None
        self.current_project_id = None  # Track current project ID for database queries
        self.existing_tasks = []
        self.existing_artists = set()
        self.directory_manager = None

        # Asset categories (project-specific with global defaults)
        self.default_asset_categories = [
            "char", "prop", "veh", "set", "env", "fx", "matte"
        ]

        # Custom task types storage
        self.custom_task_types = set()

        self.setup_ui()
        self.setup_connections()
        self.load_defaults()
        
    def setup_ui(self):
        """Set up the comprehensive user interface."""
        self.setWindowTitle("Ra: Create New Task")
        self.setModal(True)

        # Set size constraints for better scrolling behavior
        self.setMinimumSize(900, 600)  # Reduced minimum height for smaller screens
        self.setMaximumSize(1400, 1000)  # Prevent dialog from becoming too large
        self.resize(1000, 750)  # Slightly reduced default height
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header
        header_label = QLabel("Create New Task")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Task creation form
        form_widget = self.create_form_panel()
        splitter.addWidget(form_widget)
        
        # Right panel - Preview and batch options
        preview_widget = self.create_preview_panel()
        splitter.addWidget(preview_widget)
        
        # Set splitter proportions (70% form, 30% preview)
        splitter.setSizes([700, 300])
        
        # Validation feedback area
        self.validation_label = QLabel()
        self.validation_label.setStyleSheet("color: red; font-weight: bold;")
        self.validation_label.setWordWrap(True)
        self.validation_label.hide()
        layout.addWidget(self.validation_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.copy_from_task_btn = QPushButton("Copy from Existing Task")
        self.copy_from_task_btn.clicked.connect(self.show_copy_task_dialog)
        button_layout.addWidget(self.copy_from_task_btn)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.create_button = QPushButton("Create Task")
        self.create_button.setDefault(True)
        self.create_button.clicked.connect(self.create_task)
        button_layout.addWidget(self.create_button)
        
        self.create_batch_button = QPushButton("Create Batch")
        self.create_batch_button.clicked.connect(self.create_batch_tasks)
        button_layout.addWidget(self.create_batch_button)
        
        layout.addLayout(button_layout)
        
    def create_form_panel(self) -> QWidget:
        """Create the main task creation form panel with scroll area."""
        from PySide6.QtWidgets import QSizePolicy

        # Main container widget
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Ensure scroll area expands to fill available space
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create scrollable content widget
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(8)  # Reduced spacing to save space
        layout.setContentsMargins(8, 8, 8, 8)  # Reduced margins to prevent overflow

        # Ensure content widget expands to fill scroll area width and never exceeds it
        content_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        # Set maximum width to prevent content from exceeding scroll area viewport
        content_widget.setMaximumWidth(16777215)  # Qt maximum, will be constrained by parent

        # Project Selection
        project_group = QGroupBox("Project Selection")
        project_layout = QFormLayout(project_group)

        self.project_combo = QComboBox()
        self.project_combo.addItem("Select Project...")
        for project_id in self.existing_projects:
            self.project_combo.addItem(project_id, project_id)
        self.project_combo.currentTextChanged.connect(self.on_project_changed)
        project_layout.addRow("Project*:", self.project_combo)

        layout.addWidget(project_group)
        
        # Task Type Selection
        type_group = QGroupBox("Task Type")
        type_layout = QVBoxLayout(type_group)
        
        type_radio_layout = QHBoxLayout()
        self.task_type_group = QButtonGroup()
        
        self.shot_radio = QRadioButton("Shot Task")
        self.shot_radio.setChecked(True)
        self.task_type_group.addButton(self.shot_radio, 0)
        type_radio_layout.addWidget(self.shot_radio)
        
        self.asset_radio = QRadioButton("Asset Task")
        self.task_type_group.addButton(self.asset_radio, 1)
        type_radio_layout.addWidget(self.asset_radio)
        
        type_radio_layout.addStretch()
        type_layout.addLayout(type_radio_layout)
        
        # Task type description
        self.type_description_label = QLabel(
            "Shot Task: Traditional shot-based VFX workflow with episode/sequence/shot hierarchy\n"
            "Asset Task: Asset-based workflow with category/asset_name structure and dependency tracking"
        )
        self.type_description_label.setStyleSheet("color: #666666; font-style: italic;")
        type_layout.addWidget(self.type_description_label)
        
        layout.addWidget(type_group)
        
        # Dynamic form area
        self.form_stack_widget = QWidget()
        self.form_stack_layout = QVBoxLayout(self.form_stack_widget)
        
        # Shot task form
        self.shot_form = self.create_shot_task_form()
        self.form_stack_layout.addWidget(self.shot_form)
        
        # Asset task form
        self.asset_form = self.create_asset_task_form()
        self.asset_form.hide()
        self.form_stack_layout.addWidget(self.asset_form)
        
        layout.addWidget(self.form_stack_widget)

        # Set the content widget to the scroll area
        scroll_area.setWidget(content_widget)

        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)

        # Ensure no horizontal scrolling by enforcing scroll bar policies
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Explicitly disable horizontal scroll bar to prevent any horizontal scrolling
        h_scrollbar = scroll_area.horizontalScrollBar()
        if h_scrollbar:
            h_scrollbar.setEnabled(False)
            h_scrollbar.hide()

        # Connect to viewport resize to ensure content widget adapts to available width
        def on_viewport_resize():
            viewport_width = scroll_area.viewport().width()
            # Account for margins and ensure content fits within viewport
            available_width = max(viewport_width - 20, 400)  # 20px for margins, minimum 400px
            content_widget.setMaximumWidth(available_width)

        # Set initial size constraint
        on_viewport_resize()

        # Connect resize event (note: this is a simple approach, more robust event handling could be added)
        scroll_area.resizeEvent = lambda event: (on_viewport_resize(), QScrollArea.resizeEvent(scroll_area, event))[1]

        return main_widget
        
    def create_shot_task_form(self) -> QGroupBox:
        """Create shot task specific form fields."""
        group = QGroupBox("Shot Task Configuration")
        layout = QFormLayout(group)
        
        # Episode (dropdown with existing episodes)
        self.shot_episode_combo = QComboBox()
        self.shot_episode_combo.setEditable(True)
        self.shot_episode_combo.lineEdit().setPlaceholderText("e.g., Ep01, Ep02")
        self.shot_episode_combo.currentTextChanged.connect(self.update_task_id_preview)
        self.shot_episode_combo.currentTextChanged.connect(self.on_episode_changed)
        layout.addRow("Episode*:", self.shot_episode_combo)

        # Sequence (dropdown with existing sequences, filtered by episode)
        self.shot_sequence_combo = QComboBox()
        self.shot_sequence_combo.setEditable(True)
        self.shot_sequence_combo.lineEdit().setPlaceholderText("e.g., sq010, sq020")
        self.shot_sequence_combo.currentTextChanged.connect(self.update_task_id_preview)
        layout.addRow("Sequence*:", self.shot_sequence_combo)
        
        # Shot
        self.shot_shot_edit = QLineEdit()
        self.shot_shot_edit.setPlaceholderText("e.g., sh010, sh020")
        self.shot_shot_edit.textChanged.connect(self.update_task_id_preview)
        layout.addRow("Shot*:", self.shot_shot_edit)
        
        # Task Types (Multiple Selection)
        task_types_layout = QVBoxLayout()
        task_types_layout.setSpacing(8)

        # Task types selection label with count
        self.shot_task_types_label = QLabel("Available Task Types:")
        self.shot_task_types_label.setStyleSheet("font-weight: bold; color: #333333;")
        task_types_layout.addWidget(self.shot_task_types_label)

        # Task types list widget for multiple selection
        self.shot_task_types_list = QListWidget()
        self.shot_task_types_list.setMinimumHeight(180)
        self.shot_task_types_list.setMaximumHeight(200)
        self.shot_task_types_list.setSelectionMode(QListWidget.MultiSelection)
        self.shot_task_types_list.itemSelectionChanged.connect(self.update_task_id_preview)
        self.shot_task_types_list.itemSelectionChanged.connect(self.update_shot_task_types_label)
        self.shot_task_types_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                selection-background-color: #e3f2fd;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 4px 8px;
                border-bottom: 1px solid #eeeeee;
            }
            QListWidget::item:selected {
                background-color: #2196f3;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        task_types_layout.addWidget(self.shot_task_types_list)

        # Custom task type input section
        custom_task_group = QGroupBox("Add Custom Task Type")
        custom_task_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #555555;
            }
        """)
        custom_task_layout = QHBoxLayout(custom_task_group)

        self.shot_custom_task_edit = QLineEdit()
        self.shot_custom_task_edit.setPlaceholderText("Enter custom task type (e.g., previz, techvis, matchmove)")
        self.shot_custom_task_edit.setStyleSheet("""
            QLineEdit {
                padding: 6px 8px;
                border: 2px solid #cccccc;
                border-radius: 4px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #2196f3;
            }
        """)
        self.shot_custom_task_edit.returnPressed.connect(self.add_custom_shot_task_type)
        custom_task_layout.addWidget(self.shot_custom_task_edit)

        self.shot_add_custom_btn = QPushButton("Add Custom")
        self.shot_add_custom_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.shot_add_custom_btn.clicked.connect(self.add_custom_shot_task_type)
        custom_task_layout.addWidget(self.shot_add_custom_btn)

        task_types_layout.addWidget(custom_task_group)

        # Task type selection buttons
        task_buttons_layout = QHBoxLayout()
        task_buttons_layout.setSpacing(8)

        self.shot_select_all_btn = QPushButton("Select All")
        self.shot_select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.shot_select_all_btn.clicked.connect(self.select_all_shot_task_types)
        task_buttons_layout.addWidget(self.shot_select_all_btn)

        self.shot_select_none_btn = QPushButton("Select None")
        self.shot_select_none_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        self.shot_select_none_btn.clicked.connect(self.select_none_shot_task_types)
        task_buttons_layout.addWidget(self.shot_select_none_btn)

        task_buttons_layout.addStretch()

        # Selected count indicator
        self.shot_selected_count_label = QLabel("0 selected")
        self.shot_selected_count_label.setStyleSheet("color: #666666; font-size: 10px; font-style: italic;")
        task_buttons_layout.addWidget(self.shot_selected_count_label)

        task_types_layout.addLayout(task_buttons_layout)

        layout.addRow("Task Types*:", task_types_layout)
        
        # Frame Range
        frame_layout = QHBoxLayout()
        
        self.shot_frame_start_spin = QSpinBox()
        self.shot_frame_start_spin.setRange(1, 999999)
        self.shot_frame_start_spin.setValue(1001)
        frame_layout.addWidget(QLabel("Start:"))
        frame_layout.addWidget(self.shot_frame_start_spin)
        
        frame_layout.addSpacing(20)
        
        self.shot_frame_end_spin = QSpinBox()
        self.shot_frame_end_spin.setRange(1, 999999)
        self.shot_frame_end_spin.setValue(1100)
        frame_layout.addWidget(QLabel("End:"))
        frame_layout.addWidget(self.shot_frame_end_spin)
        
        frame_layout.addStretch()
        layout.addRow("Frame Range:", frame_layout)
        
        # Common fields
        self.add_common_fields(layout)
        
        return group

    def create_asset_task_form(self) -> QGroupBox:
        """Create asset task specific form fields."""
        group = QGroupBox("Asset Task Configuration")
        layout = QFormLayout(group)

        # Asset Category (replaces sequence)
        category_layout = QHBoxLayout()

        self.asset_category_combo = QComboBox()
        self.asset_category_combo.setEditable(True)
        self.asset_category_combo.currentTextChanged.connect(self.update_task_id_preview)
        category_layout.addWidget(self.asset_category_combo)

        self.manage_categories_btn = QPushButton("Manage Categories")
        self.manage_categories_btn.clicked.connect(self.manage_asset_categories)
        category_layout.addWidget(self.manage_categories_btn)

        layout.addRow("Asset Category*:", category_layout)

        # Asset Name (replaces shot)
        self.asset_name_edit = QLineEdit()
        self.asset_name_edit.setPlaceholderText("e.g., hero_character, magic_sword")
        self.asset_name_edit.textChanged.connect(self.update_task_id_preview)
        layout.addRow("Asset Name*:", self.asset_name_edit)

        # Task Types (Multiple Selection)
        asset_task_types_layout = QVBoxLayout()
        asset_task_types_layout.setSpacing(8)

        # Task types selection label with count
        self.asset_task_types_label = QLabel("Available Task Types:")
        self.asset_task_types_label.setStyleSheet("font-weight: bold; color: #333333;")
        asset_task_types_layout.addWidget(self.asset_task_types_label)

        # Task types list widget for multiple selection
        self.asset_task_types_list = QListWidget()
        self.asset_task_types_list.setMinimumHeight(180)
        self.asset_task_types_list.setMaximumHeight(200)
        self.asset_task_types_list.setSelectionMode(QListWidget.MultiSelection)
        self.asset_task_types_list.itemSelectionChanged.connect(self.update_task_id_preview)
        self.asset_task_types_list.itemSelectionChanged.connect(self.update_asset_task_types_label)
        self.asset_task_types_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                selection-background-color: #e3f2fd;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 4px 8px;
                border-bottom: 1px solid #eeeeee;
            }
            QListWidget::item:selected {
                background-color: #2196f3;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        asset_task_types_layout.addWidget(self.asset_task_types_list)

        # Custom task type input section
        asset_custom_task_group = QGroupBox("Add Custom Task Type")
        asset_custom_task_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #555555;
            }
        """)
        asset_custom_task_layout = QHBoxLayout(asset_custom_task_group)

        self.asset_custom_task_edit = QLineEdit()
        self.asset_custom_task_edit.setPlaceholderText("Enter custom task type (e.g., previz, techvis, matchmove)")
        self.asset_custom_task_edit.setStyleSheet("""
            QLineEdit {
                padding: 6px 8px;
                border: 2px solid #cccccc;
                border-radius: 4px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #2196f3;
            }
        """)
        self.asset_custom_task_edit.returnPressed.connect(self.add_custom_asset_task_type)
        asset_custom_task_layout.addWidget(self.asset_custom_task_edit)

        self.asset_add_custom_btn = QPushButton("Add Custom")
        self.asset_add_custom_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.asset_add_custom_btn.clicked.connect(self.add_custom_asset_task_type)
        asset_custom_task_layout.addWidget(self.asset_add_custom_btn)

        asset_task_types_layout.addWidget(asset_custom_task_group)

        # Task type selection buttons
        asset_task_buttons_layout = QHBoxLayout()
        asset_task_buttons_layout.setSpacing(8)

        self.asset_select_all_btn = QPushButton("Select All")
        self.asset_select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.asset_select_all_btn.clicked.connect(self.select_all_asset_task_types)
        asset_task_buttons_layout.addWidget(self.asset_select_all_btn)

        self.asset_select_none_btn = QPushButton("Select None")
        self.asset_select_none_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        self.asset_select_none_btn.clicked.connect(self.select_none_asset_task_types)
        asset_task_buttons_layout.addWidget(self.asset_select_none_btn)

        asset_task_buttons_layout.addStretch()

        # Selected count indicator
        self.asset_selected_count_label = QLabel("0 selected")
        self.asset_selected_count_label.setStyleSheet("color: #666666; font-size: 10px; font-style: italic;")
        asset_task_buttons_layout.addWidget(self.asset_selected_count_label)

        asset_task_types_layout.addLayout(asset_task_buttons_layout)

        layout.addRow("Task Types*:", asset_task_types_layout)

        # Asset Dependencies
        dependencies_layout = QVBoxLayout()

        self.dependencies_list = QListWidget()
        self.dependencies_list.setMaximumHeight(100)
        self.dependencies_list.setSelectionMode(QListWidget.MultiSelection)
        dependencies_layout.addWidget(self.dependencies_list)

        dep_buttons_layout = QHBoxLayout()
        self.add_dependency_btn = QPushButton("Add Dependency")
        self.add_dependency_btn.clicked.connect(self.add_asset_dependency)
        dep_buttons_layout.addWidget(self.add_dependency_btn)

        self.remove_dependency_btn = QPushButton("Remove Selected")
        self.remove_dependency_btn.clicked.connect(self.remove_asset_dependency)
        dep_buttons_layout.addWidget(self.remove_dependency_btn)

        dep_buttons_layout.addStretch()
        dependencies_layout.addLayout(dep_buttons_layout)

        layout.addRow("Dependencies:", dependencies_layout)

        # Asset Variants
        variants_group = QGroupBox("Asset Variants (Optional)")
        variants_layout = QFormLayout(variants_group)

        self.variant_type_combo = QComboBox()
        self.variant_type_combo.addItems([
            "", "costume_change", "damage_state", "age_progression",
            "seasonal_variant", "material_variant", "custom"
        ])
        self.variant_type_combo.setEditable(True)
        variants_layout.addRow("Variant Type:", self.variant_type_combo)

        self.variant_name_edit = QLineEdit()
        self.variant_name_edit.setPlaceholderText("e.g., winter_outfit, damaged")
        variants_layout.addRow("Variant Name:", self.variant_name_edit)

        self.parent_asset_combo = QComboBox()
        self.parent_asset_combo.setEditable(True)
        variants_layout.addRow("Parent Asset:", self.parent_asset_combo)

        layout.addRow(variants_group)

        # Common fields
        self.add_common_fields(layout)

        return group

    def add_common_fields(self, layout: QFormLayout):
        """Add common fields used by both shot and asset tasks."""
        # Artist
        self.artist_combo = QComboBox()
        self.artist_combo.setEditable(True)
        self.artist_combo.addItem("Unassigned")
        layout.addRow("Artist:", self.artist_combo)

        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            "not_started", "in_progress", "pending_review",
            "approved", "changes_requested", "on_hold", "cancelled"
        ])
        layout.addRow("Status:", self.status_combo)

        # Milestone
        self.milestone_combo = QComboBox()
        self.milestone_combo.addItems([
            "not_started", "single_frame", "low_quality",
            "final_render", "final_comp", "approved"
        ])
        layout.addRow("Milestone:", self.milestone_combo)

        # Priority
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["low", "medium", "high", "urgent"])
        self.priority_combo.setCurrentText("medium")
        layout.addRow("Priority:", self.priority_combo)

        # Estimated Duration
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0, 9999)
        self.duration_spin.setSuffix(" hours")
        self.duration_spin.setValue(8.0)
        layout.addRow("Estimated Duration:", self.duration_spin)

        # Milestone Note
        self.milestone_note_edit = QTextEdit()
        self.milestone_note_edit.setMaximumHeight(60)
        self.milestone_note_edit.setPlaceholderText("Optional notes about the task...")
        layout.addRow("Notes:", self.milestone_note_edit)

    def create_preview_panel(self) -> QWidget:
        """Create the preview and batch options panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Task ID Preview
        preview_group = QGroupBox("Task ID Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.task_id_preview_label = QLabel("No task ID generated")
        self.task_id_preview_label.setStyleSheet(
            "font-family: monospace; font-size: 12px; "
            "background-color: #f0f0f0; padding: 8px; border: 1px solid #ccc;"
        )
        self.task_id_preview_label.setWordWrap(True)
        preview_layout.addWidget(self.task_id_preview_label)

        # Validation status
        self.validation_status_label = QLabel("✓ Ready to create")
        self.validation_status_label.setStyleSheet("color: green; font-weight: bold;")
        preview_layout.addWidget(self.validation_status_label)

        layout.addWidget(preview_group)

        # Batch Creation Options
        batch_group = QGroupBox("Batch Creation Options")
        batch_layout = QVBoxLayout(batch_group)

        self.batch_create_checkbox = QCheckBox("Create all pipeline tasks for this shot/asset")
        batch_layout.addWidget(self.batch_create_checkbox)

        # Task types for batch creation
        self.batch_task_types_list = QListWidget()
        self.batch_task_types_list.setMaximumHeight(150)
        self.batch_task_types_list.setSelectionMode(QListWidget.MultiSelection)
        batch_layout.addWidget(self.batch_task_types_list)

        batch_buttons_layout = QHBoxLayout()
        self.select_all_tasks_btn = QPushButton("Select All")
        self.select_all_tasks_btn.clicked.connect(self.select_all_batch_tasks)
        batch_buttons_layout.addWidget(self.select_all_tasks_btn)

        self.select_none_tasks_btn = QPushButton("Select None")
        self.select_none_tasks_btn.clicked.connect(self.select_none_batch_tasks)
        batch_buttons_layout.addWidget(self.select_none_tasks_btn)

        batch_layout.addLayout(batch_buttons_layout)

        layout.addWidget(batch_group)

        # Directory Creation Options
        directory_group = QGroupBox("Directory Creation")
        directory_layout = QVBoxLayout(directory_group)

        self.auto_create_dirs_checkbox = QCheckBox("Create directories automatically")
        self.auto_create_dirs_checkbox.setChecked(True)
        self.auto_create_dirs_checkbox.toggled.connect(self.on_auto_create_dirs_toggled)
        directory_layout.addWidget(self.auto_create_dirs_checkbox)

        # Directory preview
        self.directory_preview_text = QTextBrowser()
        self.directory_preview_text.setMaximumHeight(150)
        self.directory_preview_text.setStyleSheet(
            "font-family: monospace; font-size: 10px; background-color: #f8f8f8;"
        )
        directory_layout.addWidget(self.directory_preview_text)

        # Directory creation progress
        self.directory_progress_bar = QProgressBar()
        self.directory_progress_bar.setVisible(False)
        directory_layout.addWidget(self.directory_progress_bar)

        layout.addWidget(directory_group)

        # Existing Tasks Preview
        existing_group = QGroupBox("Existing Similar Tasks")
        existing_layout = QVBoxLayout(existing_group)

        self.existing_tasks_list = QListWidget()
        self.existing_tasks_list.setMaximumHeight(120)
        existing_layout.addWidget(self.existing_tasks_list)

        layout.addWidget(existing_group)

        layout.addStretch()

        return widget

    def setup_connections(self):
        """Set up signal connections."""
        # Task type radio buttons
        self.task_type_group.buttonToggled.connect(self.on_task_type_changed)

        # Real-time validation timer
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self.validate_form)

        # Batch creation checkbox
        self.batch_create_checkbox.toggled.connect(self.on_batch_create_toggled)

    def load_defaults(self):
        """Load default values and populate form fields."""
        # Load asset categories
        self.load_asset_categories()

        # Load existing artists
        self.load_existing_artists()

        # Load existing tasks for preview
        self.load_existing_tasks()

    def load_asset_categories(self):
        """Load asset categories for the current project."""
        self.asset_category_combo.clear()

        # Add default categories
        for category in self.default_asset_categories:
            self.asset_category_combo.addItem(category)

        # Add project-specific categories if available
        if self.current_project_config:
            project_categories = self.current_project_config.get('asset_categories', [])
            for category in project_categories:
                if category not in self.default_asset_categories:
                    self.asset_category_combo.addItem(category)

    def load_episodes(self):
        """Load existing episodes from the current project's tasks."""
        self.shot_episode_combo.clear()

        if not self.db or not hasattr(self, 'current_project_id') or not self.current_project_id:
            return

        try:
            # Query tasks to get unique episodes for this project
            tasks = self.db.find('tasks', {'project_id': self.current_project_id})
            episodes = set()

            for task in tasks:
                # First try to get episode from the episode field directly
                episode = task.get('episode', '')
                if episode and episode not in ['asset']:  # Exclude asset tasks
                    episodes.add(episode)
                else:
                    # Fallback: Extract episode from task_id pattern: episode_sequence_shot_task
                    task_id = task.get('task_id', task.get('_id', ''))
                    if '_' in task_id:
                        parts = task_id.split('_')
                        if len(parts) >= 4:  # episode_sequence_shot_task format
                            episode = parts[0]
                            if episode and episode not in ['asset']:  # Exclude asset tasks
                                episodes.add(episode)

            # Sort episodes naturally (Ep01, Ep02, etc.)
            sorted_episodes = sorted(episodes, key=lambda x: (len(x), x.lower()))

            # Add episodes to combo box
            for episode in sorted_episodes:
                self.shot_episode_combo.addItem(episode)

        except Exception as e:
            print(f"Error loading episodes: {e}")

    def load_sequences(self, episode_filter: str = None):
        """Load existing sequences from the current project's tasks, optionally filtered by episode."""
        self.shot_sequence_combo.clear()

        if not self.db or not hasattr(self, 'current_project_id') or not self.current_project_id:
            return

        try:
            # Query tasks to get unique sequences for this project
            tasks = self.db.find('tasks', {'project_id': self.current_project_id})
            sequences = set()

            for task in tasks:
                # First try to get episode and sequence from direct fields
                task_episode = task.get('episode', '')
                sequence = task.get('sequence', '')

                if task_episode and sequence:
                    # Filter by episode if specified
                    if episode_filter:
                        if task_episode.lower() == episode_filter.lower():
                            sequences.add(sequence)
                    else:
                        # No episode filter, add all sequences (exclude asset tasks)
                        if task_episode not in ['asset']:
                            sequences.add(sequence)
                else:
                    # Fallback: Extract sequence from task_id pattern: episode_sequence_shot_task
                    task_id = task.get('task_id', task.get('_id', ''))
                    if '_' in task_id:
                        parts = task_id.split('_')
                        if len(parts) >= 4:  # episode_sequence_shot_task format
                            task_episode = parts[0]
                            sequence = parts[1]

                            # Filter by episode if specified
                            if episode_filter:
                                if task_episode.lower() == episode_filter.lower() and sequence:
                                    sequences.add(sequence)
                            else:
                                # No episode filter, add all sequences
                                if sequence and task_episode not in ['asset']:  # Exclude asset tasks
                                    sequences.add(sequence)

            # Sort sequences naturally (sq010, sq020, etc.)
            sorted_sequences = sorted(sequences, key=lambda x: (len(x), x.lower()))

            # Add sequences to combo box
            for sequence in sorted_sequences:
                self.shot_sequence_combo.addItem(sequence)

        except Exception as e:
            print(f"Error loading sequences: {e}")

    def on_episode_changed(self):
        """Handle episode selection change to filter sequences."""
        current_episode = self.shot_episode_combo.currentText().strip()
        if current_episode:
            # Reload sequences filtered by the selected episode
            self.load_sequences(current_episode)
        else:
            # No episode selected, load all sequences
            self.load_sequences()

    def load_existing_artists(self):
        """Load existing artist names from database."""
        if not self.db:
            return

        try:
            tasks = self.db.find('tasks')
            self.existing_artists = set()

            for task in tasks:
                artist = task.get('artist', '')
                if artist and artist != 'Unassigned':
                    self.existing_artists.add(artist)

            # Populate artist combo
            self.artist_combo.clear()
            self.artist_combo.addItem("Unassigned")
            for artist in sorted(self.existing_artists):
                self.artist_combo.addItem(artist)

        except Exception as e:
            print(f"Error loading existing artists: {e}")

    def load_existing_tasks(self):
        """Load existing tasks for preview and validation."""
        if not self.db:
            return

        try:
            self.existing_tasks = self.db.find('tasks')
        except Exception as e:
            print(f"Error loading existing tasks: {e}")
            self.existing_tasks = []

    def on_project_changed(self):
        """Handle project selection changes."""
        project_id = self.project_combo.currentData()
        if not project_id or project_id == "Select Project...":
            self.current_project_config = None
            self.current_project_id = None
            return

        # Store current project ID for database queries
        self.current_project_id = project_id

        # Load project configuration
        try:
            self.current_project_config = self.db.find_one('project_configs', {'_id': project_id})
            if self.current_project_config:
                self.load_project_task_types()
                self.load_asset_categories()
                self.load_episodes()  # Load existing episodes
                self.load_sequences()  # Load all sequences initially
                self.update_existing_tasks_preview()
        except Exception as e:
            print(f"Error loading project configuration: {e}")

    def load_project_task_types(self):
        """Load task types from project configuration."""
        if not self.current_project_config:
            return

        task_types = self.current_project_config.get('task_types', [])

        # Load custom task types from project config
        custom_task_types = self.current_project_config.get('custom_task_types', [])
        all_task_types = task_types + custom_task_types
        self.custom_task_types.update(custom_task_types)

        # Update shot task types list
        self.shot_task_types_list.clear()
        for task_type in all_task_types:
            item = QListWidgetItem(task_type)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.shot_task_types_list.addItem(item)

        # Update asset task types list
        self.asset_task_types_list.clear()
        for task_type in all_task_types:
            item = QListWidgetItem(task_type)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.asset_task_types_list.addItem(item)

        # Update batch task types list
        self.batch_task_types_list.clear()
        for task_type in all_task_types:
            item = QListWidgetItem(task_type)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            self.batch_task_types_list.addItem(item)

        # Initialize directory manager
        if self.current_project_config:
            self.directory_manager = DirectoryManager(self.current_project_config)

    def on_task_type_changed(self, button, checked):
        """Handle task type radio button changes."""
        if not checked:
            return

        if button == self.shot_radio:
            # Show shot form, hide asset form
            self.shot_form.show()
            self.asset_form.hide()
        else:
            # Show asset form, hide shot form
            self.shot_form.hide()
            self.asset_form.show()

        self.update_task_id_preview()
        self.update_existing_tasks_preview()
        self.update_directory_preview()

    def update_task_id_preview(self):
        """Update the task ID preview based on current form values."""
        task_ids = self.generate_task_ids()

        if task_ids:
            # Check for duplicates
            duplicates = []
            for task_id in task_ids:
                if any(task.get('_id') == task_id for task in self.existing_tasks):
                    duplicates.append(task_id)

            if duplicates:
                preview_text = f"⚠️ {len(task_ids)} task(s) will be created\n"
                preview_text += f"❌ {len(duplicates)} duplicate(s): {', '.join(duplicates[:3])}"
                if len(duplicates) > 3:
                    preview_text += f" (+{len(duplicates) - 3} more)"

                self.task_id_preview_label.setText(preview_text)
                self.task_id_preview_label.setStyleSheet(
                    "font-family: monospace; font-size: 12px; "
                    "background-color: #ffe6e6; padding: 8px; border: 1px solid #ff9999; color: red;"
                )
                self.validation_status_label.setText("❌ Duplicate task IDs found")
                self.validation_status_label.setStyleSheet("color: red; font-weight: bold;")
            else:
                preview_text = f"✓ {len(task_ids)} task(s) will be created:\n"
                preview_text += "\n".join(task_ids[:5])  # Show first 5
                if len(task_ids) > 5:
                    preview_text += f"\n... and {len(task_ids) - 5} more"

                self.task_id_preview_label.setText(preview_text)
                self.task_id_preview_label.setStyleSheet(
                    "font-family: monospace; font-size: 12px; "
                    "background-color: #e6ffe6; padding: 8px; border: 1px solid #99ff99; color: green;"
                )
                self.validation_status_label.setText("✓ Ready to create")
                self.validation_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.task_id_preview_label.setText("Incomplete information")
            self.task_id_preview_label.setStyleSheet(
                "font-family: monospace; font-size: 12px; "
                "background-color: #f0f0f0; padding: 8px; border: 1px solid #ccc;"
            )
            self.validation_status_label.setText("⏳ Fill required fields")
            self.validation_status_label.setStyleSheet("color: orange; font-weight: bold;")

        # Trigger validation timer
        self.validation_timer.start(500)

    def generate_task_ids(self) -> List[str]:
        """Generate task IDs for all selected task types."""
        task_ids = []

        if self.shot_radio.isChecked():
            # Shot tasks: {episode}_{sequence}_{shot}_{task}
            episode = self.shot_episode_combo.currentText().strip()
            sequence = self.shot_sequence_combo.currentText().strip()
            shot = self.shot_shot_edit.text().strip()

            if all([episode, sequence, shot]):
                selected_tasks = self.get_selected_shot_task_types()
                for task in selected_tasks:
                    task_id = f"{episode.lower()}_{sequence.lower()}_{shot.lower()}_{task.lower()}"
                    task_ids.append(task_id)
        else:
            # Asset tasks: asset_{category}_{asset_name}_{task}
            category = self.asset_category_combo.currentText().strip()
            asset_name = self.asset_name_edit.text().strip()

            if all([category, asset_name]):
                selected_tasks = self.get_selected_asset_task_types()
                for task in selected_tasks:
                    task_id = f"asset_{category.lower()}_{asset_name.lower()}_{task.lower()}"
                    task_ids.append(task_id)

        return task_ids

    def generate_task_id(self) -> str:
        """Generate single task ID for backward compatibility."""
        task_ids = self.generate_task_ids()
        return task_ids[0] if task_ids else ""

    def get_selected_shot_task_types(self) -> List[str]:
        """Get selected shot task types."""
        selected_types = []
        for i in range(self.shot_task_types_list.count()):
            item = self.shot_task_types_list.item(i)
            if item.isSelected():
                selected_types.append(item.text())
        return selected_types

    def get_selected_asset_task_types(self) -> List[str]:
        """Get selected asset task types."""
        selected_types = []
        for i in range(self.asset_task_types_list.count()):
            item = self.asset_task_types_list.item(i)
            if item.isSelected():
                selected_types.append(item.text())
        return selected_types

    def update_existing_tasks_preview(self):
        """Update the existing tasks preview list."""
        self.existing_tasks_list.clear()

        if not self.existing_tasks:
            return

        # Filter tasks based on current context
        if self.shot_radio.isChecked():
            # Show similar shot tasks
            episode = self.shot_episode_combo.currentText().strip().lower()
            sequence = self.shot_sequence_combo.currentText().strip().lower()
            shot = self.shot_shot_edit.text().strip().lower()

            similar_tasks = []
            for task in self.existing_tasks:
                task_episode = task.get('episode', '').lower()
                task_sequence = task.get('sequence', '').lower()
                task_shot = task.get('shot', '').lower()

                # Match by episode/sequence or shot
                if (episode and task_episode == episode) or \
                   (sequence and task_sequence == sequence) or \
                   (shot and task_shot == shot):
                    similar_tasks.append(task)
        else:
            # Show similar asset tasks
            category = self.asset_category_combo.currentText().strip().lower()
            asset_name = self.asset_name_edit.text().strip().lower()

            similar_tasks = []
            for task in self.existing_tasks:
                if task.get('type') == 'asset':
                    task_sequence = task.get('sequence', '').lower()  # category for assets
                    task_shot = task.get('shot', '').lower()  # asset_name for assets

                    if (category and task_sequence == category) or \
                       (asset_name and task_shot == asset_name):
                        similar_tasks.append(task)

        # Populate list
        for task in similar_tasks[:10]:  # Limit to 10 items
            task_id = task.get('_id', 'Unknown')
            artist = task.get('artist', 'Unassigned')
            status = task.get('status', 'unknown')

            item_text = f"{task_id} - {artist} ({status})"
            self.existing_tasks_list.addItem(item_text)

    def add_custom_shot_task_type(self):
        """Add custom task type for shot tasks."""
        custom_task = self.shot_custom_task_edit.text().strip()
        if self.validate_custom_task_name(custom_task):
            self.add_custom_task_type(custom_task, self.shot_task_types_list)
            self.shot_custom_task_edit.clear()

    def add_custom_asset_task_type(self):
        """Add custom task type for asset tasks."""
        custom_task = self.asset_custom_task_edit.text().strip()
        if self.validate_custom_task_name(custom_task):
            self.add_custom_task_type(custom_task, self.asset_task_types_list)
            self.asset_custom_task_edit.clear()

    def validate_custom_task_name(self, task_name: str) -> bool:
        """Validate custom task name."""
        if not task_name:
            QMessageBox.warning(self, "Invalid Task Name", "Task name cannot be empty.")
            return False

        # Check for valid characters (alphanumeric and underscores only)
        if not re.match(r'^[a-zA-Z0-9_]+$', task_name):
            QMessageBox.warning(
                self,
                "Invalid Task Name",
                "Task name can only contain letters, numbers, and underscores."
            )
            return False

        # Check if already exists
        existing_tasks = set()
        for i in range(self.shot_task_types_list.count()):
            existing_tasks.add(self.shot_task_types_list.item(i).text().lower())
        for i in range(self.asset_task_types_list.count()):
            existing_tasks.add(self.asset_task_types_list.item(i).text().lower())

        if task_name.lower() in existing_tasks:
            QMessageBox.warning(
                self,
                "Task Type Exists",
                f"Task type '{task_name}' already exists."
            )
            return False

        return True

    def add_custom_task_type(self, task_name: str, list_widget: QListWidget):
        """Add custom task type to the specified list widget."""
        # Add to custom task types set
        self.custom_task_types.add(task_name)

        # Add to list widget
        item = QListWidgetItem(task_name)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        list_widget.addItem(item)

        # Automatically select the new item
        item.setSelected(True)

        # Scroll to the new item to make it visible
        list_widget.scrollToItem(item)

        # Save to project configuration
        self.save_custom_task_types_to_project()

        # Update preview and labels
        self.update_task_id_preview()
        self.update_shot_task_types_label()
        self.update_asset_task_types_label()

        # Show success feedback
        self.show_custom_task_success_feedback(task_name)

    def save_custom_task_types_to_project(self):
        """Save custom task types to project configuration."""
        if not self.current_project_config or not self.db:
            return

        try:
            project_id = self.current_project_config.get('_id')
            if project_id:
                # Update project config with custom task types
                custom_task_types = list(self.custom_task_types)
                update_data = {
                    'custom_task_types': custom_task_types,
                    '_updated_at': datetime.now().isoformat()
                }

                success = self.db.update_one('project_configs', {'_id': project_id}, {'$set': update_data})
                if success:
                    # Update local config
                    self.current_project_config['custom_task_types'] = custom_task_types

        except Exception as e:
            print(f"Error saving custom task types: {e}")

    def select_all_shot_task_types(self):
        """Select all shot task types."""
        for i in range(self.shot_task_types_list.count()):
            item = self.shot_task_types_list.item(i)
            item.setSelected(True)
        self.update_task_id_preview()
        self.update_shot_task_types_label()

    def select_none_shot_task_types(self):
        """Deselect all shot task types."""
        self.shot_task_types_list.clearSelection()
        self.update_task_id_preview()
        self.update_shot_task_types_label()

    def select_all_asset_task_types(self):
        """Select all asset task types."""
        for i in range(self.asset_task_types_list.count()):
            item = self.asset_task_types_list.item(i)
            item.setSelected(True)
        self.update_task_id_preview()
        self.update_asset_task_types_label()

    def select_none_asset_task_types(self):
        """Deselect all asset task types."""
        self.asset_task_types_list.clearSelection()
        self.update_task_id_preview()
        self.update_asset_task_types_label()

    def update_shot_task_types_label(self):
        """Update the shot task types label with selection count."""
        selected_count = len(self.get_selected_shot_task_types())
        total_count = self.shot_task_types_list.count()

        if selected_count == 0:
            self.shot_task_types_label.setText("Available Task Types:")
            self.shot_selected_count_label.setText("0 selected")
        elif selected_count == 1:
            self.shot_task_types_label.setText("Available Task Types:")
            self.shot_selected_count_label.setText("1 selected")
        else:
            self.shot_task_types_label.setText("Available Task Types:")
            self.shot_selected_count_label.setText(f"{selected_count} selected")

        # Update label color based on selection
        if selected_count > 0:
            self.shot_selected_count_label.setStyleSheet("color: #2196f3; font-size: 10px; font-weight: bold;")
        else:
            self.shot_selected_count_label.setStyleSheet("color: #666666; font-size: 10px; font-style: italic;")

    def update_asset_task_types_label(self):
        """Update the asset task types label with selection count."""
        selected_count = len(self.get_selected_asset_task_types())
        total_count = self.asset_task_types_list.count()

        if selected_count == 0:
            self.asset_task_types_label.setText("Available Task Types:")
            self.asset_selected_count_label.setText("0 selected")
        elif selected_count == 1:
            self.asset_task_types_label.setText("Available Task Types:")
            self.asset_selected_count_label.setText("1 selected")
        else:
            self.asset_task_types_label.setText("Available Task Types:")
            self.asset_selected_count_label.setText(f"{selected_count} selected")

        # Update label color based on selection
        if selected_count > 0:
            self.asset_selected_count_label.setStyleSheet("color: #2196f3; font-size: 10px; font-weight: bold;")
        else:
            self.asset_selected_count_label.setStyleSheet("color: #666666; font-size: 10px; font-style: italic;")

    def show_custom_task_success_feedback(self, task_name: str):
        """Show visual feedback when a custom task type is successfully added."""
        # Show success message briefly
        if hasattr(self, 'validation_label'):
            original_text = self.validation_label.text()
            original_style = self.validation_label.styleSheet()

            self.validation_label.setText(f"✓ Custom task type '{task_name}' added successfully!")
            self.validation_label.setStyleSheet("color: green; font-weight: bold;")
            self.validation_label.show()

            # Reset after 2 seconds
            QTimer.singleShot(2000, lambda: self.reset_validation_message(original_text, original_style))

    def reset_validation_message(self, original_text: str, original_style: str):
        """Reset validation message to original state."""
        if hasattr(self, 'validation_label'):
            self.validation_label.setText(original_text)
            self.validation_label.setStyleSheet(original_style)
            if not original_text:
                self.validation_label.hide()

    def on_auto_create_dirs_toggled(self, checked: bool):
        """Handle auto create directories checkbox toggle."""
        self.directory_preview_text.setEnabled(checked)
        if checked:
            self.update_directory_preview()
        else:
            self.directory_preview_text.clear()

    def update_directory_preview(self):
        """Update directory creation preview."""
        if not self.auto_create_dirs_checkbox.isChecked() or not self.directory_manager:
            self.directory_preview_text.clear()
            return

        try:
            # Generate preview for the first task (representative)
            task_ids = self.generate_task_ids()
            if not task_ids:
                self.directory_preview_text.setText("No tasks to preview")
                return

            # Create a mock task record for preview
            if self.shot_radio.isChecked():
                mock_task = type('MockTask', (), {
                    'task_id': task_ids[0],
                    'project': self.project_combo.currentData(),
                    'episode': self.shot_episode_combo.currentText().strip(),
                    'sequence': self.shot_sequence_combo.currentText().strip(),
                    'shot': self.shot_shot_edit.text().strip(),
                    'task': task_ids[0].split('_')[-1] if task_ids else 'unknown'
                })()
            else:
                mock_task = type('MockTask', (), {
                    'task_id': task_ids[0],
                    'project': self.project_combo.currentData(),
                    'episode': 'asset',
                    'sequence': self.asset_category_combo.currentText().strip(),
                    'shot': self.asset_name_edit.text().strip(),
                    'task': task_ids[0].split('_')[-1] if task_ids else 'unknown'
                })()

            # Generate directory preview
            previews = self.directory_manager.generate_directory_preview([mock_task])

            if previews:
                preview = previews[0]
                preview_text = f"Directories for {len(task_ids)} task(s):\n\n"
                preview_text += f"Working: {preview.working_dir}\n"
                preview_text += f"Render:  {preview.render_dir}\n"
                preview_text += f"Media:   {preview.media_dir}\n"
                preview_text += f"Cache:   {preview.cache_dir}\n"

                if len(task_ids) > 1:
                    preview_text += f"\n... and similar directories for {len(task_ids) - 1} more task(s)"

                self.directory_preview_text.setText(preview_text)
            else:
                self.directory_preview_text.setText("Unable to generate directory preview")

        except Exception as e:
            self.directory_preview_text.setText(f"Preview error: {str(e)}")
            print(f"Directory preview error: {e}")

    def validate_form(self) -> bool:
        """Validate all form fields."""
        errors = []

        # Project selection
        if not self.project_combo.currentData():
            errors.append("Project must be selected")

        # Task type specific validation
        if self.shot_radio.isChecked():
            if not self.shot_episode_combo.currentText().strip():
                errors.append("Episode is required for shot tasks")
            if not self.shot_sequence_combo.currentText().strip():
                errors.append("Sequence is required for shot tasks")
            if not self.shot_shot_edit.text().strip():
                errors.append("Shot is required for shot tasks")

            selected_shot_tasks = self.get_selected_shot_task_types()
            if not selected_shot_tasks:
                errors.append("At least one task type must be selected for shot tasks")

            # Frame range validation
            if self.shot_frame_start_spin.value() >= self.shot_frame_end_spin.value():
                errors.append("Frame end must be greater than frame start")
        else:
            if not self.asset_category_combo.currentText().strip():
                errors.append("Asset category is required for asset tasks")
            if not self.asset_name_edit.text().strip():
                errors.append("Asset name is required for asset tasks")

            selected_asset_tasks = self.get_selected_asset_task_types()
            if not selected_asset_tasks:
                errors.append("At least one task type must be selected for asset tasks")

            # Dependency validation (check for circular dependencies)
            dependencies = self.get_asset_dependencies()
            if dependencies:
                task_id = self.generate_task_id()
                if task_id in dependencies:
                    errors.append("Task cannot depend on itself")

                # Check for circular dependencies
                if self.has_circular_dependency(task_id, dependencies):
                    errors.append("Circular dependency detected")

        # Task ID uniqueness
        task_ids = self.generate_task_ids()
        duplicate_ids = []
        for task_id in task_ids:
            if any(task.get('_id') == task_id for task in self.existing_tasks):
                duplicate_ids.append(task_id)

        if duplicate_ids:
            errors.append(f"Duplicate task IDs: {', '.join(duplicate_ids)}")

        # Show validation errors
        if errors:
            self.show_validation_error("; ".join(errors))
            return False
        else:
            self.show_validation_error("")
            return True

    def has_circular_dependency(self, task_id: str, dependencies: List[str]) -> bool:
        """Check for circular dependencies in asset dependency chain."""
        def check_dependency_chain(current_id: str, visited: Set[str]) -> bool:
            if current_id in visited:
                return True  # Circular dependency found

            visited.add(current_id)

            # Find dependencies of current task
            for task in self.existing_tasks:
                if task.get('_id') == current_id:
                    task_deps = task.get('dependencies', [])
                    for dep in task_deps:
                        if check_dependency_chain(dep, visited.copy()):
                            return True
            return False

        # Check each dependency
        for dep in dependencies:
            if check_dependency_chain(dep, set()):
                return True
        return False

    def show_validation_error(self, message: str):
        """Show or hide validation error message."""
        if message:
            self.validation_label.setText(f"⚠️ {message}")
            self.validation_label.show()
        else:
            self.validation_label.hide()

    def create_task(self):
        """Create tasks for all selected task types."""
        if not self.validate_form():
            return

        try:
            # Get all task data for selected task types
            all_task_data = self.build_all_task_data()

            if not all_task_data:
                QMessageBox.warning(
                    self,
                    "No Tasks to Create",
                    "No task types are selected. Please select at least one task type."
                )
                return

            # Show confirmation for multiple tasks
            if len(all_task_data) > 1:
                task_types = [task['task'] for task in all_task_data]
                reply = QMessageBox.question(
                    self,
                    "Create Multiple Tasks",
                    f"Create {len(all_task_data)} tasks?\n\nTask types: {', '.join(task_types)}",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )

                if reply != QMessageBox.Yes:
                    return

            # Create tasks
            created_tasks = []
            failed_tasks = []

            for task_data in all_task_data:
                try:
                    success = self.db.insert_one('tasks', task_data)
                    if success:
                        created_tasks.append(task_data)
                    else:
                        failed_tasks.append(task_data['_id'])
                except Exception as e:
                    failed_tasks.append(f"{task_data['_id']} ({str(e)})")

            # Create directories if enabled
            directory_errors = []
            if self.auto_create_dirs_checkbox.isChecked() and created_tasks and self.directory_manager:
                try:
                    self.directory_progress_bar.setVisible(True)
                    self.directory_progress_bar.setValue(0)

                    # Create mock task objects for directory creation
                    mock_tasks = []
                    for task_data in created_tasks:
                        mock_task = type('MockTask', (), {
                            'task_id': task_data['_id'],
                            'project': task_data['project'],
                            'episode': task_data['episode'],
                            'sequence': task_data['sequence'],
                            'shot': task_data['shot'],
                            'task': task_data['task']
                        })()
                        mock_tasks.append(mock_task)

                    # Create directories
                    success_count, total_count, errors = self.directory_manager.create_directories_for_tasks(mock_tasks)
                    directory_errors = errors

                    self.directory_progress_bar.setValue(100)

                except Exception as e:
                    directory_errors.append(f"Directory creation error: {str(e)}")
                finally:
                    self.directory_progress_bar.setVisible(False)

            # Show results
            if created_tasks:
                message = f"Successfully created {len(created_tasks)} task(s)."

                if failed_tasks:
                    message += f"\n\nFailed to create {len(failed_tasks)} task(s):\n"
                    message += "\n".join(failed_tasks[:5])
                    if len(failed_tasks) > 5:
                        message += f"\n... and {len(failed_tasks) - 5} more"

                if directory_errors:
                    message += f"\n\nDirectory creation issues:\n"
                    message += "\n".join(directory_errors[:3])
                    if len(directory_errors) > 3:
                        message += f"\n... and {len(directory_errors) - 3} more"

                QMessageBox.information(self, "Tasks Created", message)

                # Emit signals
                if len(created_tasks) == 1:
                    self.task_created.emit(created_tasks[0])
                else:
                    self.tasks_created.emit(created_tasks)

                # Close dialog
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    "Task Creation Failed",
                    "Failed to create any tasks. Please check database connectivity."
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Task Creation Error",
                f"An error occurred while creating tasks:\n{str(e)}"
            )

    def create_batch_tasks(self):
        """Create multiple tasks based on batch selection."""
        if not self.validate_form():
            return

        if not self.batch_create_checkbox.isChecked():
            QMessageBox.information(
                self,
                "Batch Creation Disabled",
                "Please enable 'Create all pipeline tasks' to use batch creation."
            )
            return

        # Get selected task types
        selected_task_types = []
        for i in range(self.batch_task_types_list.count()):
            item = self.batch_task_types_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_task_types.append(item.text())

        if not selected_task_types:
            QMessageBox.information(
                self,
                "No Task Types Selected",
                "Please select at least one task type for batch creation."
            )
            return

        # Confirm batch creation
        reply = QMessageBox.question(
            self,
            "Confirm Batch Creation",
            f"Create {len(selected_task_types)} tasks for the selected shot/asset?\n\n"
            f"Task types: {', '.join(selected_task_types)}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            created_tasks = []

            # Create tasks for each selected task type
            timestamp = datetime.now().isoformat()

            for task_type in selected_task_types:
                if self.shot_radio.isChecked():
                    task_data = {
                        "_id": f"{self.shot_episode_combo.currentText().strip().lower()}_{self.shot_sequence_combo.currentText().strip().lower()}_{self.shot_shot_edit.text().strip().lower()}_{task_type.lower()}",
                        "project": self.project_combo.currentData(),
                        "type": "shot",
                        "episode": self.shot_episode_combo.currentText().strip(),
                        "sequence": self.shot_sequence_combo.currentText().strip(),
                        "shot": self.shot_shot_edit.text().strip(),
                        "task": task_type,
                        "artist": self.artist_combo.currentText() if self.artist_combo.currentText() != "Unassigned" else "",
                        "status": self.status_combo.currentText(),
                        "milestone": self.milestone_combo.currentText(),
                        "milestone_note": self.milestone_note_edit.toPlainText().strip(),
                        "frame_range": f"{self.shot_frame_start_spin.value()}-{self.shot_frame_end_spin.value()}",
                        "priority": self.priority_combo.currentText(),
                        "estimated_duration": self.duration_spin.value(),
                        "_created_at": timestamp,
                        "_updated_at": timestamp
                    }
                else:
                    task_data = {
                        "_id": f"asset_{self.asset_category_combo.currentText().strip().lower()}_{self.asset_name_edit.text().strip().lower()}_{task_type.lower()}",
                        "project": self.project_combo.currentData(),
                        "type": "asset",
                        "episode": "asset",
                        "sequence": self.asset_category_combo.currentText().strip(),
                        "shot": self.asset_name_edit.text().strip(),
                        "task": task_type,
                        "artist": self.artist_combo.currentText() if self.artist_combo.currentText() != "Unassigned" else "",
                        "status": self.status_combo.currentText(),
                        "milestone": self.milestone_combo.currentText(),
                        "milestone_note": self.milestone_note_edit.toPlainText().strip(),
                        "priority": self.priority_combo.currentText(),
                        "estimated_duration": self.duration_spin.value(),
                        "dependencies": self.get_asset_dependencies(),
                        "variants": self.get_asset_variants(),
                        "_created_at": timestamp,
                        "_updated_at": timestamp
                    }

                # Check if task already exists
                if not any(task.get('_id') == task_data['_id'] for task in self.existing_tasks):
                    success = self.db.insert_one('tasks', task_data)
                    if success:
                        created_tasks.append(task_data)

            if created_tasks:
                QMessageBox.information(
                    self,
                    "Batch Tasks Created Successfully",
                    f"Successfully created {len(created_tasks)} tasks."
                )

                # Emit signal
                self.tasks_created.emit(created_tasks)

                # Close dialog
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "No Tasks Created",
                    "No new tasks were created. All selected tasks may already exist."
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Batch Creation Error",
                f"An error occurred during batch creation:\n{str(e)}"
            )

    def build_task_data(self) -> Dict[str, Any]:
        """Build complete task data from form fields."""
        timestamp = datetime.now().isoformat()

        if self.shot_radio.isChecked():
            # Shot task data
            task_data = {
                "_id": self.generate_task_id(),
                "project": self.project_combo.currentData(),
                "type": "shot",
                "episode": self.shot_episode_combo.currentText().strip(),
                "sequence": self.shot_sequence_combo.currentText().strip(),
                "shot": self.shot_shot_edit.text().strip(),
                "task": self.get_selected_shot_task_types()[0] if self.get_selected_shot_task_types() else "",
                "artist": self.artist_combo.currentText() if self.artist_combo.currentText() != "Unassigned" else "",
                "status": self.status_combo.currentText(),
                "milestone": self.milestone_combo.currentText(),
                "milestone_note": self.milestone_note_edit.toPlainText().strip(),
                "frame_range": f"{self.shot_frame_start_spin.value()}-{self.shot_frame_end_spin.value()}",
                "priority": self.priority_combo.currentText(),
                "estimated_duration": self.duration_spin.value(),
                "_created_at": timestamp,
                "_updated_at": timestamp
            }
        else:
            # Asset task data
            task_data = {
                "_id": self.generate_task_id(),
                "project": self.project_combo.currentData(),
                "type": "asset",
                "episode": "asset",  # Fixed value for assets
                "sequence": self.asset_category_combo.currentText().strip(),  # Asset category
                "shot": self.asset_name_edit.text().strip(),  # Asset name
                "task": self.asset_task_combo.currentText().strip(),
                "artist": self.artist_combo.currentText() if self.artist_combo.currentText() != "Unassigned" else "",
                "status": self.status_combo.currentText(),
                "milestone": self.milestone_combo.currentText(),
                "milestone_note": self.milestone_note_edit.toPlainText().strip(),
                "priority": self.priority_combo.currentText(),
                "estimated_duration": self.duration_spin.value(),
                "dependencies": self.get_asset_dependencies(),
                "variants": self.get_asset_variants(),
                "_created_at": timestamp,
                "_updated_at": timestamp
            }

        return task_data

    def build_all_task_data(self) -> List[Dict[str, Any]]:
        """Build task data for all selected task types."""
        all_task_data = []
        timestamp = datetime.now().isoformat()

        if self.shot_radio.isChecked():
            # Shot tasks
            selected_task_types = self.get_selected_shot_task_types()

            for task_type in selected_task_types:
                task_data = {
                    "_id": f"{self.shot_episode_combo.currentText().strip().lower()}_{self.shot_sequence_combo.currentText().strip().lower()}_{self.shot_shot_edit.text().strip().lower()}_{task_type.lower()}",
                    "project": self.project_combo.currentData(),
                    "type": "shot",
                    "episode": self.shot_episode_combo.currentText().strip(),
                    "sequence": self.shot_sequence_combo.currentText().strip(),
                    "shot": self.shot_shot_edit.text().strip(),
                    "task": task_type,
                    "artist": self.artist_combo.currentText() if self.artist_combo.currentText() != "Unassigned" else "",
                    "status": self.status_combo.currentText(),
                    "milestone": self.milestone_combo.currentText(),
                    "milestone_note": self.milestone_note_edit.toPlainText().strip(),
                    "frame_range": f"{self.shot_frame_start_spin.value()}-{self.shot_frame_end_spin.value()}",
                    "priority": self.priority_combo.currentText(),
                    "estimated_duration": self.duration_spin.value(),
                    "_created_at": timestamp,
                    "_updated_at": timestamp
                }
                all_task_data.append(task_data)
        else:
            # Asset tasks
            selected_task_types = self.get_selected_asset_task_types()

            for task_type in selected_task_types:
                task_data = {
                    "_id": f"asset_{self.asset_category_combo.currentText().strip().lower()}_{self.asset_name_edit.text().strip().lower()}_{task_type.lower()}",
                    "project": self.project_combo.currentData(),
                    "type": "asset",
                    "episode": "asset",  # Fixed value for assets
                    "sequence": self.asset_category_combo.currentText().strip(),  # Asset category
                    "shot": self.asset_name_edit.text().strip(),  # Asset name
                    "task": task_type,
                    "artist": self.artist_combo.currentText() if self.artist_combo.currentText() != "Unassigned" else "",
                    "status": self.status_combo.currentText(),
                    "milestone": self.milestone_combo.currentText(),
                    "milestone_note": self.milestone_note_edit.toPlainText().strip(),
                    "priority": self.priority_combo.currentText(),
                    "estimated_duration": self.duration_spin.value(),
                    "dependencies": self.get_asset_dependencies(),
                    "variants": self.get_asset_variants(),
                    "_created_at": timestamp,
                    "_updated_at": timestamp
                }
                all_task_data.append(task_data)

        return all_task_data

    def get_asset_dependencies(self) -> List[str]:
        """Get asset dependencies from the dependencies list."""
        dependencies = []
        for i in range(self.dependencies_list.count()):
            item = self.dependencies_list.item(i)
            if item:
                dependencies.append(item.text())
        return dependencies

    def get_asset_variants(self) -> Dict[str, Any]:
        """Get asset variants information."""
        variant_type = self.variant_type_combo.currentText().strip()
        variant_name = self.variant_name_edit.text().strip()
        parent_asset = self.parent_asset_combo.currentText().strip()

        if not variant_type and not variant_name and not parent_asset:
            return {}

        variants = {}
        if variant_type:
            variants["variant_type"] = variant_type
        if variant_name:
            variants["variant_name"] = variant_name
        if parent_asset:
            variants["parent_asset"] = parent_asset

        # Set base asset (current task ID without the task type)
        if self.asset_category_combo.currentText() and self.asset_name_edit.text():
            base_id = f"asset_{self.asset_category_combo.currentText().strip().lower()}_{self.asset_name_edit.text().strip().lower()}"
            variants["base_asset"] = base_id

        return variants

    def add_asset_dependency(self):
        """Add an asset dependency."""
        from PySide6.QtWidgets import QInputDialog

        # Get available assets
        available_assets = []
        for task in self.existing_tasks:
            if task.get('type') == 'asset':
                asset_id = task.get('_id', '')
                if asset_id and asset_id not in available_assets:
                    available_assets.append(asset_id)

        if not available_assets:
            QMessageBox.information(
                self,
                "No Assets Available",
                "No existing assets found to add as dependencies."
            )
            return

        # Show selection dialog
        asset_id, ok = QInputDialog.getItem(
            self,
            "Add Asset Dependency",
            "Select asset to add as dependency:",
            available_assets,
            0,
            False
        )

        if ok and asset_id:
            # Check if already added
            existing_deps = [self.dependencies_list.item(i).text()
                           for i in range(self.dependencies_list.count())]

            if asset_id not in existing_deps:
                self.dependencies_list.addItem(asset_id)
            else:
                QMessageBox.information(
                    self,
                    "Dependency Exists",
                    f"Asset '{asset_id}' is already in the dependencies list."
                )

    def remove_asset_dependency(self):
        """Remove selected asset dependency."""
        current_item = self.dependencies_list.currentItem()
        if current_item:
            row = self.dependencies_list.row(current_item)
            self.dependencies_list.takeItem(row)

    def manage_asset_categories(self):
        """Manage project-specific asset categories."""
        # This could be expanded to a full category management dialog
        from PySide6.QtWidgets import QInputDialog

        category, ok = QInputDialog.getText(
            self,
            "Add Asset Category",
            "Enter new asset category:",
            text=""
        )

        if ok and category.strip():
            category = category.strip().lower()

            # Check if already exists
            existing_categories = [self.asset_category_combo.itemText(i)
                                 for i in range(self.asset_category_combo.count())]

            if category not in existing_categories:
                self.asset_category_combo.addItem(category)
                self.asset_category_combo.setCurrentText(category)
            else:
                QMessageBox.information(
                    self,
                    "Category Exists",
                    f"Asset category '{category}' already exists."
                )

    def on_batch_create_toggled(self, checked):
        """Handle batch create checkbox toggle."""
        self.batch_task_types_list.setEnabled(checked)
        self.select_all_tasks_btn.setEnabled(checked)
        self.select_none_tasks_btn.setEnabled(checked)
        self.create_batch_button.setEnabled(checked)

    def select_all_batch_tasks(self):
        """Select all task types for batch creation."""
        for i in range(self.batch_task_types_list.count()):
            item = self.batch_task_types_list.item(i)
            item.setCheckState(Qt.Checked)

    def select_none_batch_tasks(self):
        """Deselect all task types for batch creation."""
        for i in range(self.batch_task_types_list.count()):
            item = self.batch_task_types_list.item(i)
            item.setCheckState(Qt.Unchecked)

    def show_copy_task_dialog(self):
        """Show dialog to copy from existing task."""
        if not self.existing_tasks:
            QMessageBox.information(
                self,
                "No Tasks Available",
                "No existing tasks found to copy from."
            )
            return

        # Create simple selection dialog
        from PySide6.QtWidgets import QInputDialog

        task_options = []
        for task in self.existing_tasks:
            task_id = task.get('_id', 'Unknown')
            task_type = task.get('task', 'unknown')
            artist = task.get('artist', 'Unassigned')
            task_options.append(f"{task_id} ({task_type} - {artist})")

        selected_task, ok = QInputDialog.getItem(
            self,
            "Copy from Existing Task",
            "Select task to copy settings from:",
            task_options,
            0,
            False
        )

        if ok and selected_task:
            # Find the selected task
            task_id = selected_task.split(' (')[0]
            source_task = None

            for task in self.existing_tasks:
                if task.get('_id') == task_id:
                    source_task = task
                    break

            if source_task:
                self.copy_task_settings(source_task)

    def copy_task_settings(self, source_task: Dict[str, Any]):
        """Copy settings from source task to current form."""
        # Copy common fields
        artist = source_task.get('artist', '')
        if artist:
            index = self.artist_combo.findText(artist)
            if index >= 0:
                self.artist_combo.setCurrentIndex(index)

        status = source_task.get('status', 'not_started')
        index = self.status_combo.findText(status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)

        milestone = source_task.get('milestone', 'not_started')
        index = self.milestone_combo.findText(milestone)
        if index >= 0:
            self.milestone_combo.setCurrentIndex(index)

        priority = source_task.get('priority', 'medium')
        index = self.priority_combo.findText(priority)
        if index >= 0:
            self.priority_combo.setCurrentIndex(index)

        duration = source_task.get('estimated_duration', 8.0)
        self.duration_spin.setValue(duration)

        milestone_note = source_task.get('milestone_note', '')
        self.milestone_note_edit.setPlainText(milestone_note)

        QMessageBox.information(
            self,
            "Settings Copied",
            f"Settings copied from task '{source_task.get('_id', 'Unknown')}'.\n\n"
            f"You can now modify the shot/asset details and create the new task."
        )
