"""
Annotation Widget

Widget for adding and managing review annotations with drawing tools,
text notes, and frame-specific feedback for the Review Application.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QGroupBox, QLabel, QComboBox, QListWidget, QListWidgetItem,
    QSpinBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor


class AnnotationWidget(QWidget):
    """
    Annotation widget for review feedback and drawing tools.
    
    Provides text annotations, drawing tools, and frame-specific
    feedback capabilities for the Review Application.
    """
    
    # Signals
    annotationAdded = Signal(dict)      # annotation_data
    annotationUpdated = Signal(dict)    # annotation_data
    annotationDeleted = Signal(str)     # annotation_id
    
    # Annotation types
    ANNOTATION_TYPES = [
        ('Note', 'note'),
        ('Issue', 'issue'),
        ('Approval', 'approval'),
        ('Question', 'question'),
        ('Change Request', 'change_request')
    ]
    
    # Priority levels
    PRIORITY_LEVELS = [
        ('Low', 'low'),
        ('Medium', 'medium'),
        ('High', 'high'),
        ('Critical', 'critical')
    ]
    
    def __init__(self, parent=None):
        """Initialize annotation widget."""
        super().__init__(parent)
        
        # State
        self.current_media_item: Optional[Dict[str, Any]] = None
        self.current_frame = 0
        self.annotations: List[Dict[str, Any]] = []
        self.selected_annotation_id: Optional[str] = None
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Annotation tools
        tools_group = QGroupBox("Annotation Tools")
        tools_layout = QVBoxLayout(tools_group)
        
        # Annotation type and priority
        type_layout = QHBoxLayout()
        
        type_layout.addWidget(QLabel("Type:"))
        self.annotation_type_combo = QComboBox()
        for display_name, value in self.ANNOTATION_TYPES:
            self.annotation_type_combo.addItem(display_name, value)
        type_layout.addWidget(self.annotation_type_combo)
        
        type_layout.addWidget(QLabel("Priority:"))
        self.priority_combo = QComboBox()
        for display_name, value in self.PRIORITY_LEVELS:
            self.priority_combo.addItem(display_name, value)
        self.priority_combo.setCurrentIndex(1)  # Default to Medium
        type_layout.addWidget(self.priority_combo)
        
        tools_layout.addLayout(type_layout)
        
        # Frame-specific annotation
        frame_layout = QHBoxLayout()
        
        self.frame_specific_checkbox = QCheckBox("Frame-specific")
        self.frame_specific_checkbox.setChecked(True)
        frame_layout.addWidget(self.frame_specific_checkbox)
        
        frame_layout.addWidget(QLabel("Frame:"))
        self.frame_spinbox = QSpinBox()
        self.frame_spinbox.setMinimum(0)
        self.frame_spinbox.setMaximum(9999)
        self.frame_spinbox.setValue(0)
        frame_layout.addWidget(self.frame_spinbox)
        
        frame_layout.addStretch()
        tools_layout.addLayout(frame_layout)
        
        # Annotation text
        self.annotation_text = QTextEdit()
        self.annotation_text.setPlaceholderText("Enter annotation text...")
        self.annotation_text.setMaximumHeight(80)
        tools_layout.addWidget(self.annotation_text)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.add_annotation_button = QPushButton("Add Annotation")
        self.add_annotation_button.setStyleSheet("background-color: #4CAF50; color: white;")
        buttons_layout.addWidget(self.add_annotation_button)
        
        self.clear_text_button = QPushButton("Clear")
        buttons_layout.addWidget(self.clear_text_button)
        
        tools_layout.addLayout(buttons_layout)
        layout.addWidget(tools_group)
        
        # Existing annotations list
        annotations_group = QGroupBox("Annotations")
        annotations_layout = QVBoxLayout(annotations_group)
        
        # Annotations list
        self.annotations_list = QListWidget()
        self.annotations_list.setMaximumHeight(150)
        annotations_layout.addWidget(self.annotations_list)
        
        # Annotation management buttons
        manage_layout = QHBoxLayout()
        
        self.delete_annotation_button = QPushButton("Delete")
        self.delete_annotation_button.setEnabled(False)
        self.delete_annotation_button.setStyleSheet("background-color: #f44336; color: white;")
        manage_layout.addWidget(self.delete_annotation_button)
        
        self.clear_all_button = QPushButton("Clear All")
        self.clear_all_button.setStyleSheet("background-color: #ff9800; color: white;")
        manage_layout.addWidget(self.clear_all_button)
        
        manage_layout.addStretch()
        annotations_layout.addLayout(manage_layout)
        layout.addWidget(annotations_group)
        
        # Annotation statistics
        self.stats_label = QLabel("No annotations")
        self.stats_label.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(self.stats_label)
        
        # Add stretch to push content to top
        layout.addStretch()
    
    def setup_connections(self):
        """Set up signal connections."""
        # Annotation tools
        self.add_annotation_button.clicked.connect(self.add_annotation)
        self.clear_text_button.clicked.connect(self.clear_annotation_text)
        
        # Frame-specific checkbox
        self.frame_specific_checkbox.toggled.connect(self.on_frame_specific_toggled)
        
        # Annotations list
        self.annotations_list.itemSelectionChanged.connect(self.on_annotation_selected)
        
        # Management buttons
        self.delete_annotation_button.clicked.connect(self.delete_selected_annotation)
        self.clear_all_button.clicked.connect(self.clear_all_annotations)
    
    def set_media_item(self, media_item: Dict[str, Any]):
        """Set the current media item and load its annotations."""
        self.current_media_item = media_item
        self.load_annotations()
        
        # Update frame range
        total_frames = media_item.get('total_frames', 100)
        self.frame_spinbox.setMaximum(max(0, total_frames - 1))
    
    def set_current_frame(self, frame: int):
        """Set the current frame number."""
        self.current_frame = frame
        self.frame_spinbox.setValue(frame)
    
    def load_annotations(self):
        """Load annotations for current media item."""
        if not self.current_media_item:
            self.annotations = []
        else:
            # In a full implementation, this would load from database
            # For demo purposes, we'll start with empty annotations
            self.annotations = []
        
        self.refresh_annotations_list()
    
    def add_annotation(self):
        """Add new annotation."""
        text = self.annotation_text.toPlainText().strip()
        if not text:
            return
        
        annotation_type = self.annotation_type_combo.currentData()
        priority = self.priority_combo.currentData()
        frame_specific = self.frame_specific_checkbox.isChecked()
        frame_number = self.frame_spinbox.value() if frame_specific else None
        
        # Create annotation data
        annotation = {
            'id': f"ann_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            'text': text,
            'type': annotation_type,
            'priority': priority,
            'frame_specific': frame_specific,
            'frame_number': frame_number,
            'timestamp': datetime.now().isoformat(),
            'author': 'Current User',
            'status': 'open'
        }
        
        # Add to annotations list
        self.annotations.append(annotation)
        
        # Refresh display
        self.refresh_annotations_list()
        
        # Clear text
        self.clear_annotation_text()
        
        # Emit signal
        self.annotationAdded.emit(annotation)
    
    def delete_selected_annotation(self):
        """Delete the selected annotation."""
        if not self.selected_annotation_id:
            return
        
        # Find and remove annotation
        for i, annotation in enumerate(self.annotations):
            if annotation['id'] == self.selected_annotation_id:
                self.annotations.pop(i)
                break
        
        # Refresh display
        self.refresh_annotations_list()
        
        # Emit signal
        self.annotationDeleted.emit(self.selected_annotation_id)
        
        # Clear selection
        self.selected_annotation_id = None
        self.delete_annotation_button.setEnabled(False)
    
    def clear_all_annotations(self):
        """Clear all annotations."""
        self.annotations.clear()
        self.refresh_annotations_list()
        
        # Clear selection
        self.selected_annotation_id = None
        self.delete_annotation_button.setEnabled(False)
    
    def clear_annotation_text(self):
        """Clear the annotation text field."""
        self.annotation_text.clear()
    
    def refresh_annotations_list(self):
        """Refresh the annotations list display."""
        self.annotations_list.clear()
        
        for annotation in self.annotations:
            item_text = self.format_annotation_text(annotation)
            list_item = QListWidgetItem(item_text)
            list_item.setData(Qt.UserRole, annotation['id'])
            
            # Color code by priority
            priority = annotation.get('priority', 'medium')
            if priority == 'critical':
                list_item.setBackground(QColor(255, 235, 235))  # Light red
            elif priority == 'high':
                list_item.setBackground(QColor(255, 245, 235))  # Light orange
            elif priority == 'low':
                list_item.setBackground(QColor(235, 255, 235))  # Light green
            
            self.annotations_list.addItem(list_item)
        
        # Update statistics
        self.update_statistics()
    
    def format_annotation_text(self, annotation: Dict[str, Any]) -> str:
        """Format annotation for display in list."""
        text = annotation['text']
        if len(text) > 40:
            text = text[:37] + "..."
        
        annotation_type = annotation['type'].replace('_', ' ').title()
        priority = annotation['priority'].title()
        
        if annotation['frame_specific'] and annotation['frame_number'] is not None:
            frame_info = f" [F{annotation['frame_number']}]"
        else:
            frame_info = " [General]"
        
        return f"{annotation_type} ({priority}){frame_info}: {text}"
    
    def on_annotation_selected(self):
        """Handle annotation selection change."""
        current_item = self.annotations_list.currentItem()
        if current_item:
            self.selected_annotation_id = current_item.data(Qt.UserRole)
            self.delete_annotation_button.setEnabled(True)
        else:
            self.selected_annotation_id = None
            self.delete_annotation_button.setEnabled(False)
    
    def on_frame_specific_toggled(self, checked: bool):
        """Handle frame-specific checkbox toggle."""
        self.frame_spinbox.setEnabled(checked)
        if checked:
            self.frame_spinbox.setValue(self.current_frame)
    
    def update_statistics(self):
        """Update annotation statistics display."""
        total = len(self.annotations)
        if total == 0:
            self.stats_label.setText("No annotations")
            return
        
        # Count by priority
        priority_counts = {}
        for annotation in self.annotations:
            priority = annotation['priority']
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Format statistics
        stats_text = f"Total: {total}"
        if priority_counts:
            priority_text = ", ".join([f"{k.title()}: {v}" for k, v in priority_counts.items()])
            stats_text += f" | {priority_text}"
        
        self.stats_label.setText(stats_text)
    
    def clear_annotations(self):
        """Clear all annotations (called from main window)."""
        self.clear_all_annotations()
