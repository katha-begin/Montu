"""
Project Selector Widget

Widget for selecting and managing projects in the Project Launcher.
Provides dropdown selection and project information display.
"""

from typing import List, Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, 
    QPushButton, QGroupBox, QTextEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class ProjectSelector(QWidget):
    """
    Project selection widget with dropdown and project information display.
    
    Provides interface for selecting projects and displaying project details
    including task counts and configuration information.
    """
    
    # Signals
    projectChanged = Signal(str)  # project_id
    refreshRequested = Signal()
    
    def __init__(self, parent=None):
        """Initialize project selector widget."""
        super().__init__(parent)
        self.current_project_id: Optional[str] = None
        self.available_projects: List[Dict[str, str]] = []
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Project selection group
        selection_group = QGroupBox("Project Selection")
        selection_layout = QVBoxLayout(selection_group)
        
        # Project dropdown
        dropdown_layout = QHBoxLayout()
        
        dropdown_layout.addWidget(QLabel("Project:"))
        
        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(200)
        self.project_combo.setPlaceholderText("Select a project...")
        dropdown_layout.addWidget(self.project_combo)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setMaximumWidth(80)
        dropdown_layout.addWidget(self.refresh_button)
        
        dropdown_layout.addStretch()
        selection_layout.addLayout(dropdown_layout)
        
        layout.addWidget(selection_group)
        
        # Project information group
        info_group = QGroupBox("Project Information")
        info_layout = QVBoxLayout(info_group)
        
        # Project details
        details_layout = QVBoxLayout()
        
        self.project_name_label = QLabel("No project selected")
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        self.project_name_label.setFont(font)
        details_layout.addWidget(self.project_name_label)
        
        self.project_stats_label = QLabel("")
        self.project_stats_label.setStyleSheet("color: #666;")
        details_layout.addWidget(self.project_stats_label)
        
        info_layout.addLayout(details_layout)
        
        # Project description
        self.project_description = QTextEdit()
        self.project_description.setMaximumHeight(80)
        self.project_description.setReadOnly(True)
        self.project_description.setPlaceholderText("Project description will appear here...")
        info_layout.addWidget(self.project_description)
        
        layout.addWidget(info_group)
        
        # Set initial state
        self.set_no_project_state()
    
    def setup_connections(self):
        """Set up signal connections."""
        self.project_combo.currentTextChanged.connect(self.on_project_selection_changed)
        self.refresh_button.clicked.connect(self.refresh_projects)
    
    def set_available_projects(self, projects: List[Dict[str, str]]):
        """
        Set available projects for selection.
        
        Args:
            projects: List of project dictionaries with 'id', 'name', 'description'
        """
        self.available_projects = projects
        
        # Update combo box
        self.project_combo.blockSignals(True)
        self.project_combo.clear()
        
        if projects:
            for project in projects:
                project_name = project.get('name', project.get('id', 'Unknown'))
                self.project_combo.addItem(project_name, project.get('id'))
        else:
            self.project_combo.addItem("No projects available", None)
        
        self.project_combo.blockSignals(False)
        
        # Reset selection if current project not in list
        if self.current_project_id:
            project_ids = [p.get('id') for p in projects]
            if self.current_project_id not in project_ids:
                self.set_no_project_state()
    
    def set_current_project(self, project_info: Dict[str, Any]):
        """
        Set current project information.
        
        Args:
            project_info: Dictionary with project details
        """
        project_id = project_info.get('id')
        project_name = project_info.get('name', 'Unknown Project')
        description = project_info.get('description', '')
        task_count = project_info.get('task_count', 0)
        
        self.current_project_id = project_id
        
        # Update UI
        self.project_name_label.setText(project_name)
        self.project_stats_label.setText(f"Tasks: {task_count}")
        self.project_description.setPlainText(description)
        
        # Update combo box selection
        for i in range(self.project_combo.count()):
            if self.project_combo.itemData(i) == project_id:
                self.project_combo.blockSignals(True)
                self.project_combo.setCurrentIndex(i)
                self.project_combo.blockSignals(False)
                break
        
        # Enable controls
        self.project_combo.setEnabled(True)
    
    def set_no_project_state(self):
        """Set UI to no project selected state."""
        self.current_project_id = None
        self.project_name_label.setText("No project selected")
        self.project_stats_label.setText("")
        self.project_description.setPlainText("")
        
        # Reset combo box
        self.project_combo.blockSignals(True)
        self.project_combo.setCurrentIndex(-1)
        self.project_combo.blockSignals(False)
    
    def set_loading_state(self, loading: bool = True):
        """Set UI to loading state."""
        if loading:
            self.project_name_label.setText("Loading project...")
            self.project_stats_label.setText("")
            self.project_description.setPlainText("")
            self.project_combo.setEnabled(False)
            self.refresh_button.setEnabled(False)
        else:
            self.project_combo.setEnabled(True)
            self.refresh_button.setEnabled(True)
    
    def on_project_selection_changed(self, project_name: str):
        """Handle project selection change."""
        if not project_name or project_name == "No projects available":
            return
        
        # Find project ID by name
        project_id = None
        current_index = self.project_combo.currentIndex()
        if current_index >= 0:
            project_id = self.project_combo.itemData(current_index)
        
        if project_id and project_id != self.current_project_id:
            self.set_loading_state(True)
            self.projectChanged.emit(project_id)
    
    def refresh_projects(self):
        """Request project list refresh."""
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("Refreshing...")
        self.refreshRequested.emit()
    
    def refresh_complete(self):
        """Called when refresh is complete."""
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText("Refresh")
    
    def get_current_project_id(self) -> Optional[str]:
        """Get currently selected project ID."""
        return self.current_project_id
    
    def update_project_stats(self, stats: Dict[str, Any]):
        """
        Update project statistics display.
        
        Args:
            stats: Dictionary with project statistics
        """
        if not self.current_project_id:
            return
        
        current_project = stats.get('current_project', {})
        task_count = current_project.get('task_count', 0)
        status_breakdown = current_project.get('status_breakdown', {})
        
        # Format status breakdown
        status_text = f"Tasks: {task_count}"
        if status_breakdown:
            status_parts = []
            for status, count in status_breakdown.items():
                status_display = status.replace('_', ' ').title()
                status_parts.append(f"{status_display}: {count}")
            
            if status_parts:
                status_text += f" ({', '.join(status_parts)})"
        
        self.project_stats_label.setText(status_text)
