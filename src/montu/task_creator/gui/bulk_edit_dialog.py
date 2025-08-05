"""
Bulk Edit Dialog for Ra: Task Creator.
Allows editing multiple tasks simultaneously.
"""

from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QLineEdit, QPushButton, QGroupBox, QCheckBox, QFormLayout,
    QDialogButtonBox, QTextEdit
)
from PySide6.QtCore import Qt

from ..csv_parser import TaskRecord


class BulkEditDialog(QDialog):
    """Dialog for bulk editing multiple tasks."""
    
    def __init__(self, tasks: List[TaskRecord], parent=None):
        super().__init__(parent)
        self.tasks = tasks
        self.changes = {}
        
        self.setWindowTitle(f"Bulk Edit - {len(tasks)} Tasks")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        self.setup_ui()
        self.populate_current_values()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(f"Editing {len(self.tasks)} selected tasks:")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header_label)
        
        # Task list preview
        task_preview = QTextEdit()
        task_preview.setMaximumHeight(100)
        task_preview.setReadOnly(True)
        task_ids = [task.task_id for task in self.tasks[:10]]  # Show first 10
        if len(self.tasks) > 10:
            task_ids.append(f"... and {len(self.tasks) - 10} more")
        task_preview.setPlainText(", ".join(task_ids))
        layout.addWidget(task_preview)
        
        # Edit options
        edit_group = QGroupBox("Edit Options")
        edit_layout = QFormLayout(edit_group)
        
        # Status editing
        self.status_checkbox = QCheckBox("Change Status")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["not_started", "in_progress", "completed", "on_hold", "cancelled"])
        self.status_combo.setEnabled(False)
        self.status_checkbox.toggled.connect(self.status_combo.setEnabled)
        
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_checkbox)
        status_layout.addWidget(self.status_combo)
        status_layout.addStretch()
        edit_layout.addRow("Status:", status_layout)
        
        # Priority editing
        self.priority_checkbox = QCheckBox("Change Priority")
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["low", "medium", "high", "urgent"])
        self.priority_combo.setEnabled(False)
        self.priority_checkbox.toggled.connect(self.priority_combo.setEnabled)
        
        priority_layout = QHBoxLayout()
        priority_layout.addWidget(self.priority_checkbox)
        priority_layout.addWidget(self.priority_combo)
        priority_layout.addStretch()
        edit_layout.addRow("Priority:", priority_layout)
        
        # Artist editing
        self.artist_checkbox = QCheckBox("Change Artist")
        self.artist_edit = QLineEdit()
        self.artist_edit.setEnabled(False)
        self.artist_checkbox.toggled.connect(self.artist_edit.setEnabled)
        
        artist_layout = QHBoxLayout()
        artist_layout.addWidget(self.artist_checkbox)
        artist_layout.addWidget(self.artist_edit)
        edit_layout.addRow("Artist:", artist_layout)
        
        layout.addWidget(edit_group)
        
        # Current values info
        info_group = QGroupBox("Current Values")
        info_layout = QVBoxLayout(info_group)
        
        self.current_values_label = QLabel()
        self.current_values_label.setWordWrap(True)
        self.current_values_label.setStyleSheet("color: #666666; font-size: 11px;")
        info_layout.addWidget(self.current_values_label)
        
        layout.addWidget(info_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def populate_current_values(self):
        """Show current values for the selected tasks."""
        if not self.tasks:
            return
        
        # Analyze current values
        statuses = set(task.status for task in self.tasks)
        priorities = set(task.priority for task in self.tasks)
        artists = set(task.artist for task in self.tasks if task.artist)
        
        info_parts = []
        
        if len(statuses) == 1:
            info_parts.append(f"All tasks have status: {list(statuses)[0]}")
        else:
            info_parts.append(f"Mixed statuses: {', '.join(sorted(statuses))}")
        
        if len(priorities) == 1:
            info_parts.append(f"All tasks have priority: {list(priorities)[0]}")
        else:
            info_parts.append(f"Mixed priorities: {', '.join(sorted(priorities))}")
        
        if len(artists) == 0:
            info_parts.append("No artists assigned")
        elif len(artists) == 1:
            info_parts.append(f"All tasks assigned to: {list(artists)[0]}")
        else:
            info_parts.append(f"Mixed artists: {', '.join(sorted(artists))}")
        
        self.current_values_label.setText("\n".join(info_parts))
        
        # Set default values in combos
        if len(statuses) == 1:
            self.status_combo.setCurrentText(list(statuses)[0])
        
        if len(priorities) == 1:
            self.priority_combo.setCurrentText(list(priorities)[0])
        
        if len(artists) == 1:
            self.artist_edit.setText(list(artists)[0])
    
    def get_changes(self) -> Dict[str, Any]:
        """Get the changes to apply."""
        changes = {}
        
        if self.status_checkbox.isChecked():
            changes['status'] = self.status_combo.currentText()
        
        if self.priority_checkbox.isChecked():
            changes['priority'] = self.priority_combo.currentText()
        
        if self.artist_checkbox.isChecked():
            changes['artist'] = self.artist_edit.text().strip()
        
        return changes
    
    def accept(self):
        """Accept the dialog and validate changes."""
        changes = self.get_changes()
        
        if not changes:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "No Changes", "Please select at least one field to change.")
            return
        
        # Confirm changes
        from PySide6.QtWidgets import QMessageBox
        change_descriptions = []
        for field, value in changes.items():
            change_descriptions.append(f"{field.title()}: {value}")
        
        reply = QMessageBox.question(
            self, "Confirm Bulk Edit",
            f"Apply the following changes to {len(self.tasks)} tasks?\n\n" + 
            "\n".join(change_descriptions),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            super().accept()
