"""
Version Management Widget

GUI widget for version management functionality providing
version creation, publishing, locking, and history display.
"""

from typing import Dict, List, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox, QGroupBox,
    QMessageBox, QDialog, QDialogButtonBox, QFormLayout, QCheckBox,
    QProgressBar, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter

from .version_manager import VersionManager, VersionStatus, VersionInfo


class VersionHistoryWidget(QWidget):
    """Widget for displaying version history and management."""
    
    # Signals
    versionSelected = Signal(str)  # version
    versionCreated = Signal(str)   # version
    versionPublished = Signal(str) # version
    
    def __init__(self, parent=None):
        """Initialize version history widget."""
        super().__init__(parent)
        
        # State
        self.version_manager = VersionManager()
        self.current_task_id: Optional[str] = None
        self.current_project_id: Optional[str] = None
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Set up the version history widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Header with task info
        self.header_label = QLabel("No task selected")
        self.header_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                padding: 5px;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.header_label)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Version list tab
        self.setup_version_list_tab()
        self.tab_widget.addTab(self.version_list_widget, "Versions")
        
        # Statistics tab
        self.setup_statistics_tab()
        self.tab_widget.addTab(self.statistics_widget, "Statistics")
        
        layout.addWidget(self.tab_widget)
        
        # Action buttons
        self.setup_action_buttons(layout)
    
    def setup_version_list_tab(self):
        """Set up the version list tab."""
        self.version_list_widget = QWidget()
        layout = QVBoxLayout(self.version_list_widget)
        
        # Version tree
        self.version_tree = QTreeWidget()
        self.version_tree.setHeaderLabels([
            "Version", "Status", "Author", "Created", "Size", "Description"
        ])
        self.version_tree.setAlternatingRowColors(True)
        self.version_tree.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # Configure column widths
        header = self.version_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Version
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Author
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Created
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Size
        header.setSectionResizeMode(5, QHeaderView.Stretch)           # Description
        
        layout.addWidget(self.version_tree)
        
        # Version details
        details_group = QGroupBox("Version Details")
        details_layout = QVBoxLayout(details_group)
        
        self.version_details_label = QLabel("Select a version to view details")
        self.version_details_label.setWordWrap(True)
        self.version_details_label.setStyleSheet("padding: 10px; background-color: #fafafa;")
        details_layout.addWidget(self.version_details_label)
        
        layout.addWidget(details_group)
    
    def setup_statistics_tab(self):
        """Set up the statistics tab."""
        self.statistics_widget = QWidget()
        layout = QVBoxLayout(self.statistics_widget)
        
        # Statistics display
        self.statistics_table = QTableWidget()
        self.statistics_table.setColumnCount(2)
        self.statistics_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.statistics_table.horizontalHeader().setStretchLastSection(True)
        self.statistics_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.statistics_table)
    
    def setup_action_buttons(self, layout):
        """Set up action buttons."""
        buttons_layout = QHBoxLayout()
        
        # Create version button
        self.create_version_btn = QPushButton("Create Version")
        self.create_version_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        buttons_layout.addWidget(self.create_version_btn)
        
        # Publish version button
        self.publish_version_btn = QPushButton("Publish Version")
        self.publish_version_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        buttons_layout.addWidget(self.publish_version_btn)
        
        # Lock/Unlock version button
        self.lock_version_btn = QPushButton("Lock Version")
        self.lock_version_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        buttons_layout.addWidget(self.lock_version_btn)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #455A64;
            }
        """)
        buttons_layout.addWidget(self.refresh_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Initially disable action buttons
        self.update_button_states()
    
    def setup_connections(self):
        """Set up signal connections."""
        self.version_tree.itemSelectionChanged.connect(self.on_version_selected)
        self.create_version_btn.clicked.connect(self.create_version)
        self.publish_version_btn.clicked.connect(self.publish_version)
        self.lock_version_btn.clicked.connect(self.toggle_version_lock)
        self.refresh_btn.clicked.connect(self.refresh_versions)
    
    def set_task(self, task_id: str, project_id: str = None):
        """Set the current task for version management."""
        self.current_task_id = task_id
        self.current_project_id = project_id
        
        # Update header
        self.header_label.setText(f"Versions for Task: {task_id}")
        
        # Load versions
        self.refresh_versions()
        
        # Enable buttons
        self.update_button_states()
    
    def refresh_versions(self):
        """Refresh the version list."""
        if not self.current_task_id:
            return
        
        # Clear existing items
        self.version_tree.clear()
        
        # Get versions
        versions = self.version_manager.get_task_versions(self.current_task_id)
        
        # Populate tree
        for version in versions:
            item = QTreeWidgetItem(self.version_tree)
            
            # Version
            item.setText(0, version.version)
            
            # Status with icon
            status_text = self.format_status_display(version.status)
            item.setText(1, status_text)
            
            # Author
            item.setText(2, version.author)
            
            # Created date (formatted)
            try:
                from datetime import datetime
                created_dt = datetime.fromisoformat(version.created_date.replace('Z', '+00:00'))
                created_str = created_dt.strftime("%Y-%m-%d %H:%M")
            except:
                created_str = version.created_date
            item.setText(3, created_str)
            
            # File size (formatted)
            size_str = self.format_file_size(version.file_size)
            item.setText(4, size_str)
            
            # Description
            description = version.description or "No description"
            if len(description) > 50:
                description = description[:47] + "..."
            item.setText(5, description)
            
            # Store version info
            item.setData(0, Qt.UserRole, version)
            
            # Style based on status
            self.style_version_item(item, version)
        
        # Update statistics
        self.update_statistics()
        
        # Clear selection
        self.version_details_label.setText("Select a version to view details")
    
    def format_status_display(self, status: VersionStatus) -> str:
        """Format status with appropriate icon."""
        status_map = {
            VersionStatus.WIP: "🔧 WIP",
            VersionStatus.REVIEW: "👁️ Review",
            VersionStatus.APPROVED: "✅ Approved",
            VersionStatus.PUBLISHED: "📦 Published",
            VersionStatus.ARCHIVED: "📁 Archived",
            VersionStatus.REJECTED: "❌ Rejected"
        }
        return status_map.get(status, f"❓ {status.value}")
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.1f} TB"
    
    def style_version_item(self, item: QTreeWidgetItem, version: VersionInfo):
        """Apply styling based on version status."""
        if version.status == VersionStatus.PUBLISHED:
            # Green background for published
            for col in range(item.columnCount()):
                item.setBackground(col, Qt.green.lighter(180))
        elif version.status == VersionStatus.REJECTED:
            # Red background for rejected
            for col in range(item.columnCount()):
                item.setBackground(col, Qt.red.lighter(180))
        elif version.status == VersionStatus.REVIEW:
            # Yellow background for review
            for col in range(item.columnCount()):
                item.setBackground(col, Qt.yellow.lighter(180))
        
        # Bold font for locked versions
        if version.is_locked:
            font = QFont()
            font.setBold(True)
            for col in range(item.columnCount()):
                item.setFont(col, font)

    def on_version_selected(self):
        """Handle version selection."""
        selected_items = self.version_tree.selectedItems()
        if not selected_items:
            self.version_details_label.setText("Select a version to view details")
            self.update_button_states()
            return

        item = selected_items[0]
        version = item.data(0, Qt.UserRole)

        if version:
            # Update details display
            details = self.format_version_details(version)
            self.version_details_label.setText(details)

            # Emit signal
            self.versionSelected.emit(version.version)

        # Update button states
        self.update_button_states()

    def format_version_details(self, version: VersionInfo) -> str:
        """Format version details for display."""
        details = []
        details.append(f"<b>Version:</b> {version.version}")
        details.append(f"<b>Status:</b> {self.format_status_display(version.status)}")
        details.append(f"<b>Author:</b> {version.author}")
        details.append(f"<b>Created:</b> {version.created_date}")
        details.append(f"<b>Modified:</b> {version.modified_date}")
        details.append(f"<b>File Size:</b> {self.format_file_size(version.file_size)}")
        details.append(f"<b>Locked:</b> {'Yes' if version.is_locked else 'No'}")

        if version.parent_version:
            details.append(f"<b>Parent Version:</b> {version.parent_version}")

        if version.description:
            details.append(f"<b>Description:</b> {version.description}")

        # Add metadata if available
        if version.metadata:
            details.append("<b>Metadata:</b>")
            for key, value in version.metadata.items():
                details.append(f"  • {key}: {value}")

        return "<br>".join(details)

    def update_button_states(self):
        """Update button enabled/disabled states."""
        has_task = self.current_task_id is not None
        selected_items = self.version_tree.selectedItems()
        has_selection = len(selected_items) > 0

        # Create version - enabled if task is set
        self.create_version_btn.setEnabled(has_task)

        # Other buttons - enabled if version is selected
        self.publish_version_btn.setEnabled(has_selection)
        self.lock_version_btn.setEnabled(has_selection)

        # Update lock button text based on selection
        if has_selection:
            item = selected_items[0]
            version = item.data(0, Qt.UserRole)
            if version and version.is_locked:
                self.lock_version_btn.setText("Unlock Version")
            else:
                self.lock_version_btn.setText("Lock Version")

    def create_version(self):
        """Create a new version."""
        if not self.current_task_id:
            return

        dialog = CreateVersionDialog(self.current_task_id, self.current_project_id, self)
        if dialog.exec() == QDialog.Accepted:
            # Refresh versions
            self.refresh_versions()
            self.versionCreated.emit(dialog.created_version)

    def publish_version(self):
        """Publish the selected version."""
        selected_items = self.version_tree.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        version = item.data(0, Qt.UserRole)

        if not version:
            return

        # Confirm publication
        reply = QMessageBox.question(
            self,
            "Publish Version",
            f"Are you sure you want to publish version {version.version}?\n\n"
            f"This will mark it as the official published version.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Get publication notes
            notes, ok = self.get_publication_notes()
            if ok:
                success = self.version_manager.publish_version(
                    self.current_task_id,
                    version.version,
                    "current_user",  # TODO: Get actual user
                    notes
                )

                if success:
                    QMessageBox.information(self, "Success", f"Version {version.version} published successfully!")
                    self.refresh_versions()
                    self.versionPublished.emit(version.version)
                else:
                    QMessageBox.warning(self, "Error", "Failed to publish version.")

    def toggle_version_lock(self):
        """Toggle lock status of selected version."""
        selected_items = self.version_tree.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        version = item.data(0, Qt.UserRole)

        if not version:
            return

        if version.is_locked:
            # Unlock version
            success = self.version_manager.unlock_version(
                self.current_task_id,
                version.version,
                "current_user",  # TODO: Get actual user
                "Unlocked via GUI"
            )
            action = "unlocked"
        else:
            # Lock version
            success = self.version_manager.lock_version(
                self.current_task_id,
                version.version,
                "current_user",  # TODO: Get actual user
                "Locked via GUI"
            )
            action = "locked"

        if success:
            QMessageBox.information(self, "Success", f"Version {version.version} {action} successfully!")
            self.refresh_versions()
        else:
            QMessageBox.warning(self, "Error", f"Failed to {action.replace('ed', '')} version.")

    def get_publication_notes(self) -> tuple:
        """Get publication notes from user."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Publication Notes")
        dialog.setModal(True)
        dialog.resize(400, 200)

        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("Enter publication notes (optional):"))

        notes_edit = QTextEdit()
        notes_edit.setPlaceholderText("Describe what's new in this version...")
        layout.addWidget(notes_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.Accepted:
            return notes_edit.toPlainText(), True

        return "", False

    def update_statistics(self):
        """Update the statistics display."""
        if not self.current_task_id:
            return

        stats = self.version_manager.get_version_statistics(task_id=self.current_task_id)

        # Clear existing rows
        self.statistics_table.setRowCount(0)

        # Add statistics
        stats_to_display = [
            ("Total Versions", stats.get('total_versions', 0)),
            ("Published Versions", stats.get('published_versions', 0)),
            ("Locked Versions", stats.get('locked_versions', 0)),
            ("Unique Authors", stats.get('unique_authors', 0)),
            ("Total File Size", self.format_file_size(stats.get('total_file_size', 0))),
            ("Latest Version Date", stats.get('latest_version_date', 'N/A')),
            ("Oldest Version Date", stats.get('oldest_version_date', 'N/A'))
        ]

        # Add status breakdown
        status_breakdown = stats.get('status_breakdown', {})
        for status, count in status_breakdown.items():
            stats_to_display.append((f"Status: {status.title()}", count))

        # Populate table
        self.statistics_table.setRowCount(len(stats_to_display))
        for row, (metric, value) in enumerate(stats_to_display):
            self.statistics_table.setItem(row, 0, QTableWidgetItem(str(metric)))
            self.statistics_table.setItem(row, 1, QTableWidgetItem(str(value)))


class CreateVersionDialog(QDialog):
    """Dialog for creating a new version."""

    def __init__(self, task_id: str, project_id: str = None, parent=None):
        """Initialize create version dialog."""
        super().__init__(parent)

        self.task_id = task_id
        self.project_id = project_id
        self.version_manager = VersionManager()
        self.created_version = None

        self.setup_ui()
        self.setup_connections()

        # Pre-populate next version
        next_version = self.version_manager.get_next_version(task_id, project_id)
        self.version_edit.setText(next_version)

    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Create New Version")
        self.setModal(True)
        self.resize(500, 400)

        layout = QVBoxLayout(self)

        # Form layout
        form_layout = QFormLayout()

        # Version
        self.version_edit = QLineEdit()
        self.version_edit.setPlaceholderText("e.g., v001")
        form_layout.addRow("Version:", self.version_edit)

        # File path
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Path to version file...")
        form_layout.addRow("File Path:", self.file_path_edit)

        # Author
        self.author_edit = QLineEdit()
        self.author_edit.setText("current_user")  # TODO: Get actual user
        form_layout.addRow("Author:", self.author_edit)

        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Describe this version...")
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description_edit)

        layout.addLayout(form_layout)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.create_version)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def setup_connections(self):
        """Set up signal connections."""
        pass

    def create_version(self):
        """Create the version."""
        version = self.version_edit.text().strip()
        file_path = self.file_path_edit.text().strip()
        author = self.author_edit.text().strip()
        description = self.description_edit.toPlainText().strip()

        if not version:
            QMessageBox.warning(self, "Error", "Version is required.")
            return

        if not file_path:
            QMessageBox.warning(self, "Error", "File path is required.")
            return

        if not author:
            QMessageBox.warning(self, "Error", "Author is required.")
            return

        # Create version
        version_info = self.version_manager.create_version(
            self.task_id,
            file_path,
            author,
            description,
            version,
            self.project_id
        )

        if version_info:
            self.created_version = version
            QMessageBox.information(self, "Success", f"Version {version} created successfully!")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to create version.")


# Export the main widget
__all__ = ['VersionHistoryWidget', 'CreateVersionDialog']
