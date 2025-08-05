"""
Approval Widget

Widget for managing approval workflow with status tracking,
supervisor notes, and client version mapping for the Review Application.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QGroupBox, QLabel, QComboBox, QListWidget, QListWidgetItem,
    QCheckBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont


class ApprovalWidget(QWidget):
    """
    Approval widget for review workflow management.
    
    Provides approval status tracking, supervisor notes,
    and client version mapping interface.
    """
    
    # Signals
    approvalChanged = Signal(dict)      # approval_data
    
    # Approval statuses
    APPROVAL_STATUSES = [
        ('Pending Review', 'pending'),
        ('Approved', 'approved'),
        ('Approved with Notes', 'approved_with_notes'),
        ('Rejected', 'rejected'),
        ('Needs Revision', 'needs_revision'),
        ('Client Review', 'client_review'),
        ('Final Approved', 'final_approved')
    ]
    
    def __init__(self, parent=None):
        """Initialize approval widget."""
        super().__init__(parent)
        
        # State
        self.current_media_item: Optional[Dict[str, Any]] = None
        self.current_approval_data: Dict[str, Any] = {}
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Current status display
        status_group = QGroupBox("Current Status")
        status_layout = QVBoxLayout(status_group)
        
        self.current_status_label = QLabel("No media selected")
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        self.current_status_label.setFont(font)
        self.current_status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.current_status_label)
        
        # Status details
        self.status_details_label = QLabel("Select media to view approval status")
        self.status_details_label.setStyleSheet("color: #666; font-size: 9pt;")
        self.status_details_label.setAlignment(Qt.AlignCenter)
        self.status_details_label.setWordWrap(True)
        status_layout.addWidget(self.status_details_label)
        
        layout.addWidget(status_group)
        
        # Approval controls
        controls_group = QGroupBox("Approval Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Status selection
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        
        self.status_combo = QComboBox()
        for display_name, value in self.APPROVAL_STATUSES:
            self.status_combo.addItem(display_name, value)
        status_layout.addWidget(self.status_combo)
        
        controls_layout.addLayout(status_layout)
        
        # Supervisor notes
        notes_layout = QVBoxLayout()
        notes_layout.addWidget(QLabel("Supervisor Notes:"))
        
        self.supervisor_notes = QTextEdit()
        self.supervisor_notes.setPlaceholderText("Enter supervisor notes...")
        self.supervisor_notes.setMaximumHeight(80)
        notes_layout.addWidget(self.supervisor_notes)
        
        controls_layout.addLayout(notes_layout)
        
        # Client delivery options
        client_layout = QVBoxLayout()
        
        self.client_delivery_checkbox = QCheckBox("Mark for Client Delivery")
        client_layout.addWidget(self.client_delivery_checkbox)
        
        client_version_layout = QHBoxLayout()
        client_version_layout.addWidget(QLabel("Client Version:"))
        
        self.client_version_combo = QComboBox()
        self.client_version_combo.addItem("Auto-assign", "auto")
        self.client_version_combo.addItem("v1.0", "v1.0")
        self.client_version_combo.addItem("v1.1", "v1.1")
        self.client_version_combo.addItem("v2.0", "v2.0")
        self.client_version_combo.setEnabled(False)
        client_version_layout.addWidget(self.client_version_combo)
        
        client_layout.addLayout(client_version_layout)
        controls_layout.addLayout(client_layout)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.update_approval_button = QPushButton("Update Approval")
        self.update_approval_button.setStyleSheet("background-color: #2196F3; color: white;")
        self.update_approval_button.setEnabled(False)
        buttons_layout.addWidget(self.update_approval_button)
        
        self.reset_button = QPushButton("Reset")
        buttons_layout.addWidget(self.reset_button)
        
        controls_layout.addLayout(buttons_layout)
        layout.addWidget(controls_group)
        
        # Approval history
        history_group = QGroupBox("Approval History")
        history_layout = QVBoxLayout(history_group)
        
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(120)
        history_layout.addWidget(self.history_list)
        
        layout.addWidget(history_group)
        
        # Quick actions
        quick_group = QGroupBox("Quick Actions")
        quick_layout = QHBoxLayout(quick_group)
        
        self.approve_button = QPushButton("✓ Approve")
        self.approve_button.setStyleSheet("background-color: #4CAF50; color: white;")
        self.approve_button.setEnabled(False)
        quick_layout.addWidget(self.approve_button)
        
        self.reject_button = QPushButton("✗ Reject")
        self.reject_button.setStyleSheet("background-color: #f44336; color: white;")
        self.reject_button.setEnabled(False)
        quick_layout.addWidget(self.reject_button)
        
        self.needs_revision_button = QPushButton("⚠ Needs Revision")
        self.needs_revision_button.setStyleSheet("background-color: #ff9800; color: white;")
        self.needs_revision_button.setEnabled(False)
        quick_layout.addWidget(self.needs_revision_button)
        
        layout.addWidget(quick_group)
        
        # Add stretch to push content to top
        layout.addStretch()
    
    def setup_connections(self):
        """Set up signal connections."""
        # Status controls
        self.status_combo.currentTextChanged.connect(self.on_status_changed)
        self.supervisor_notes.textChanged.connect(self.on_notes_changed)
        self.client_delivery_checkbox.toggled.connect(self.on_client_delivery_toggled)
        
        # Action buttons
        self.update_approval_button.clicked.connect(self.update_approval)
        self.reset_button.clicked.connect(self.reset_form)
        
        # Quick action buttons
        self.approve_button.clicked.connect(self.quick_approve)
        self.reject_button.clicked.connect(self.quick_reject)
        self.needs_revision_button.clicked.connect(self.quick_needs_revision)
    
    def set_media_item(self, media_item: Dict[str, Any]):
        """Set the current media item and load its approval data."""
        self.current_media_item = media_item
        self.load_approval_data()
        self.enable_controls(True)
    
    def load_approval_data(self):
        """Load approval data for current media item."""
        if not self.current_media_item:
            self.current_approval_data = {}
            self.enable_controls(False)
            return
        
        # In a full implementation, this would load from database
        # For demo purposes, we'll create sample approval data
        task_id = self.current_media_item.get('task_id', 'unknown')
        version = self.current_media_item.get('version', 'v001')
        
        # Sample approval data
        self.current_approval_data = {
            'status': 'pending',
            'supervisor_notes': '',
            'client_delivery': False,
            'client_version': 'auto',
            'history': [
                {
                    'timestamp': datetime.now().isoformat(),
                    'status': 'pending',
                    'user': 'System',
                    'notes': 'Initial submission for review'
                }
            ]
        }
        
        # Update UI with loaded data
        self.update_status_display()
        self.update_form_from_data()
        self.update_history_display()
    
    def update_status_display(self):
        """Update the current status display."""
        if not self.current_media_item:
            self.current_status_label.setText("No media selected")
            self.status_details_label.setText("Select media to view approval status")
            return
        
        task_id = self.current_media_item.get('task_id', 'Unknown')
        version = self.current_media_item.get('version', 'v001')
        status = self.current_approval_data.get('status', 'pending')
        
        # Format status display
        status_display = status.replace('_', ' ').title()
        self.current_status_label.setText(f"{status_display}")
        
        # Set status color
        if status == 'approved' or status == 'final_approved':
            self.current_status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        elif status == 'rejected':
            self.current_status_label.setStyleSheet("color: #f44336; font-weight: bold;")
        elif status == 'needs_revision':
            self.current_status_label.setStyleSheet("color: #ff9800; font-weight: bold;")
        else:
            self.current_status_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        
        # Update details
        details = f"Task: {task_id} | Version: {version}"
        if self.current_approval_data.get('client_delivery'):
            client_version = self.current_approval_data.get('client_version', 'auto')
            details += f" | Client: {client_version}"
        
        self.status_details_label.setText(details)
    
    def update_form_from_data(self):
        """Update form controls from current approval data."""
        # Set status combo
        status = self.current_approval_data.get('status', 'pending')
        for i in range(self.status_combo.count()):
            if self.status_combo.itemData(i) == status:
                self.status_combo.setCurrentIndex(i)
                break
        
        # Set supervisor notes
        notes = self.current_approval_data.get('supervisor_notes', '')
        self.supervisor_notes.setPlainText(notes)
        
        # Set client delivery options
        client_delivery = self.current_approval_data.get('client_delivery', False)
        self.client_delivery_checkbox.setChecked(client_delivery)
        self.client_version_combo.setEnabled(client_delivery)
        
        client_version = self.current_approval_data.get('client_version', 'auto')
        for i in range(self.client_version_combo.count()):
            if self.client_version_combo.itemData(i) == client_version:
                self.client_version_combo.setCurrentIndex(i)
                break
    
    def update_history_display(self):
        """Update the approval history display."""
        self.history_list.clear()
        
        history = self.current_approval_data.get('history', [])
        for entry in reversed(history):  # Show most recent first
            timestamp = entry.get('timestamp', '')
            status = entry.get('status', '').replace('_', ' ').title()
            user = entry.get('user', 'Unknown')
            notes = entry.get('notes', '')
            
            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime('%m/%d %H:%M')
            except:
                time_str = 'Unknown'
            
            # Create history item text
            item_text = f"{time_str} - {status} by {user}"
            if notes:
                item_text += f": {notes[:50]}{'...' if len(notes) > 50 else ''}"
            
            list_item = QListWidgetItem(item_text)
            
            # Color code by status
            if 'approved' in status.lower():
                list_item.setBackground(QColor(235, 255, 235))  # Light green
            elif 'rejected' in status.lower():
                list_item.setBackground(QColor(255, 235, 235))  # Light red
            elif 'revision' in status.lower():
                list_item.setBackground(QColor(255, 245, 235))  # Light orange
            
            self.history_list.addItem(list_item)
    
    def enable_controls(self, enabled: bool):
        """Enable or disable approval controls."""
        self.status_combo.setEnabled(enabled)
        self.supervisor_notes.setEnabled(enabled)
        self.client_delivery_checkbox.setEnabled(enabled)
        self.update_approval_button.setEnabled(enabled)
        self.approve_button.setEnabled(enabled)
        self.reject_button.setEnabled(enabled)
        self.needs_revision_button.setEnabled(enabled)
    
    def on_status_changed(self):
        """Handle status combo change."""
        self.update_approval_button.setEnabled(True)
    
    def on_notes_changed(self):
        """Handle supervisor notes change."""
        self.update_approval_button.setEnabled(True)
    
    def on_client_delivery_toggled(self, checked: bool):
        """Handle client delivery checkbox toggle."""
        self.client_version_combo.setEnabled(checked)
        self.update_approval_button.setEnabled(True)
    
    def update_approval(self):
        """Update approval status with current form data."""
        if not self.current_media_item:
            return
        
        # Collect form data
        new_status = self.status_combo.currentData()
        supervisor_notes = self.supervisor_notes.toPlainText().strip()
        client_delivery = self.client_delivery_checkbox.isChecked()
        client_version = self.client_version_combo.currentData() if client_delivery else None
        
        # Update approval data
        self.current_approval_data.update({
            'status': new_status,
            'supervisor_notes': supervisor_notes,
            'client_delivery': client_delivery,
            'client_version': client_version,
            'last_updated': datetime.now().isoformat()
        })
        
        # Add to history
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'status': new_status,
            'user': 'Current User',
            'notes': supervisor_notes
        }
        
        if 'history' not in self.current_approval_data:
            self.current_approval_data['history'] = []
        self.current_approval_data['history'].append(history_entry)
        
        # Update displays
        self.update_status_display()
        self.update_history_display()
        
        # Disable update button
        self.update_approval_button.setEnabled(False)
        
        # Emit signal
        self.approvalChanged.emit(self.current_approval_data)
    
    def reset_form(self):
        """Reset form to original approval data."""
        self.update_form_from_data()
        self.update_approval_button.setEnabled(False)
    
    def quick_approve(self):
        """Quick approve action."""
        self.status_combo.setCurrentText("Approved")
        self.supervisor_notes.setPlainText("Approved for delivery")
        self.update_approval()
    
    def quick_reject(self):
        """Quick reject action."""
        self.status_combo.setCurrentText("Rejected")
        self.supervisor_notes.setPlainText("Rejected - see notes for details")
        self.update_approval()
    
    def quick_needs_revision(self):
        """Quick needs revision action."""
        self.status_combo.setCurrentText("Needs Revision")
        self.supervisor_notes.setPlainText("Needs revision - see notes for details")
        self.update_approval()
