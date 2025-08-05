"""
Version Management Integration Example

Example showing how to integrate the Version Management System
into the Project Launcher application.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSplitter, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal

from ...shared import VersionManager, VersionHistoryWidget


class VersionAwareFileWidget(QWidget):
    """
    Example widget showing version-aware file management integration.
    
    This demonstrates how to integrate the Version Management System
    into existing Project Launcher functionality.
    """
    
    # Signals
    fileVersionChanged = Signal(str, str)  # task_id, version
    
    def __init__(self, parent=None):
        """Initialize version-aware file widget."""
        super().__init__(parent)
        
        # State
        self.version_manager = VersionManager()
        self.current_task_id: Optional[str] = None
        self.current_project_id: Optional[str] = None
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Header
        header_layout = QHBoxLayout()
        
        self.task_label = QLabel("No task selected")
        self.task_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                padding: 5px;
                background-color: #e8f4fd;
                border: 1px solid #bee5eb;
                border-radius: 3px;
            }
        """)
        header_layout.addWidget(self.task_label)
        
        # Quick action buttons
        self.new_version_btn = QPushButton("New Version")
        self.new_version_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        header_layout.addWidget(self.new_version_btn)
        
        self.open_latest_btn = QPushButton("Open Latest")
        self.open_latest_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        header_layout.addWidget(self.open_latest_btn)
        
        layout.addLayout(header_layout)
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # File operations panel
        self.setup_file_operations_panel(splitter)
        
        # Version history panel
        self.version_history_widget = VersionHistoryWidget()
        version_group = QGroupBox("Version History")
        version_layout = QVBoxLayout(version_group)
        version_layout.addWidget(self.version_history_widget)
        splitter.addWidget(version_group)
        
        # Set splitter proportions (60% file ops, 40% version history)
        splitter.setSizes([600, 400])
        
        layout.addWidget(splitter)
        
        # Initially disable buttons
        self.update_button_states()
    
    def setup_file_operations_panel(self, parent):
        """Set up the file operations panel."""
        file_ops_group = QGroupBox("File Operations")
        layout = QVBoxLayout(file_ops_group)
        
        # Current version info
        self.current_version_label = QLabel("Current Version: None")
        self.current_version_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                padding: 8px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.current_version_label)
        
        # Published version info
        self.published_version_label = QLabel("Published Version: None")
        self.published_version_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                padding: 8px;
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.published_version_label)
        
        # File operation buttons
        buttons_layout = QVBoxLayout()
        
        self.save_new_version_btn = QPushButton("Save as New Version")
        self.save_new_version_btn.clicked.connect(self.save_new_version)
        buttons_layout.addWidget(self.save_new_version_btn)
        
        self.open_version_btn = QPushButton("Open Specific Version...")
        self.open_version_btn.clicked.connect(self.open_specific_version)
        buttons_layout.addWidget(self.open_version_btn)
        
        self.compare_versions_btn = QPushButton("Compare Versions...")
        self.compare_versions_btn.clicked.connect(self.compare_versions)
        buttons_layout.addWidget(self.compare_versions_btn)
        
        layout.addLayout(buttons_layout)
        
        parent.addWidget(file_ops_group)
    
    def setup_connections(self):
        """Set up signal connections."""
        self.new_version_btn.clicked.connect(self.create_new_version)
        self.open_latest_btn.clicked.connect(self.open_latest_version)
        
        # Connect version history signals
        self.version_history_widget.versionSelected.connect(self.on_version_selected)
        self.version_history_widget.versionCreated.connect(self.on_version_created)
        self.version_history_widget.versionPublished.connect(self.on_version_published)
    
    def set_task(self, task_id: str, project_id: str = None):
        """Set the current task for version management."""
        self.current_task_id = task_id
        self.current_project_id = project_id
        
        # Update UI
        self.task_label.setText(f"Task: {task_id}")
        
        # Set task in version history widget
        self.version_history_widget.set_task(task_id, project_id)
        
        # Update version info
        self.update_version_info()
        
        # Enable buttons
        self.update_button_states()
    
    def update_version_info(self):
        """Update current and published version information."""
        if not self.current_task_id:
            self.current_version_label.setText("Current Version: None")
            self.published_version_label.setText("Published Version: None")
            return
        
        # Get latest version
        latest_version = self.version_manager.get_latest_version(self.current_task_id)
        if latest_version:
            self.current_version_label.setText(f"Current Version: {latest_version}")
        else:
            self.current_version_label.setText("Current Version: None")
        
        # Get published version
        published_version = self.version_manager.get_published_version(self.current_task_id)
        if published_version:
            self.published_version_label.setText(f"Published Version: {published_version}")
        else:
            self.published_version_label.setText("Published Version: None")
    
    def update_button_states(self):
        """Update button enabled/disabled states."""
        has_task = self.current_task_id is not None
        
        self.new_version_btn.setEnabled(has_task)
        self.open_latest_btn.setEnabled(has_task)
        self.save_new_version_btn.setEnabled(has_task)
        self.open_version_btn.setEnabled(has_task)
        self.compare_versions_btn.setEnabled(has_task)
    
    def create_new_version(self):
        """Create a new version using the version history widget."""
        self.version_history_widget.create_version()
    
    def open_latest_version(self):
        """Open the latest version of the current task."""
        if not self.current_task_id:
            return
        
        latest_version = self.version_manager.get_latest_version(self.current_task_id)
        if latest_version:
            version_info = self.version_manager.get_version_info(self.current_task_id, latest_version)
            if version_info:
                # In a real implementation, this would open the file in the appropriate DCC
                QMessageBox.information(
                    self,
                    "Open File",
                    f"Opening latest version: {latest_version}\n"
                    f"File: {version_info.file_path}\n"
                    f"Author: {version_info.author}\n"
                    f"Status: {version_info.status.value}"
                )
                
                # Emit signal for other components
                self.fileVersionChanged.emit(self.current_task_id, latest_version)
        else:
            QMessageBox.information(self, "No Versions", "No versions found for this task.")
    
    def save_new_version(self):
        """Save current work as a new version."""
        if not self.current_task_id:
            return
        
        # In a real implementation, this would:
        # 1. Save the current file
        # 2. Create a new version record
        # 3. Update the UI
        
        QMessageBox.information(
            self,
            "Save New Version",
            "This would save the current work as a new version.\n\n"
            "Implementation would:\n"
            "1. Save current file with version naming\n"
            "2. Create version record in database\n"
            "3. Update version history display"
        )
    
    def open_specific_version(self):
        """Open a specific version selected by the user."""
        # This would show a version selection dialog
        QMessageBox.information(
            self,
            "Open Specific Version",
            "This would show a dialog to select and open a specific version."
        )
    
    def compare_versions(self):
        """Compare two versions."""
        # This would show a version comparison dialog
        QMessageBox.information(
            self,
            "Compare Versions",
            "This would show a dialog to compare two versions side-by-side."
        )
    
    def on_version_selected(self, version: str):
        """Handle version selection from history widget."""
        print(f"Version selected: {version}")
        # Could update preview, enable specific actions, etc.
    
    def on_version_created(self, version: str):
        """Handle new version creation."""
        print(f"New version created: {version}")
        self.update_version_info()
        
        # Show success message
        QMessageBox.information(
            self,
            "Version Created",
            f"Successfully created version {version}!"
        )
    
    def on_version_published(self, version: str):
        """Handle version publication."""
        print(f"Version published: {version}")
        self.update_version_info()
        
        # Show success message
        QMessageBox.information(
            self,
            "Version Published",
            f"Successfully published version {version}!"
        )


# Example usage function
def create_version_integration_example():
    """Create an example of version management integration."""
    from PySide6.QtWidgets import QApplication, QMainWindow
    import sys
    
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Version Management Integration Example")
    window.resize(1200, 800)
    
    # Create and set the version-aware widget
    version_widget = VersionAwareFileWidget()
    window.setCentralWidget(version_widget)
    
    # Set a test task
    version_widget.set_task("ep00_sq0010_sh0020_lighting", "SWA")
    
    window.show()
    return app, window


if __name__ == "__main__":
    app, window = create_version_integration_example()
    app.exec()
