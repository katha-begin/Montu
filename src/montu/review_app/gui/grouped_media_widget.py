"""
Grouped Media Widget

Advanced media list widget with sequence-based grouping, sorting,
and collapsible group headers for the Review Application.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QPushButton, QFrame, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter


class GroupedMediaWidget(QWidget):
    """
    Grouped media list widget with sequence-based organization.
    
    Provides hierarchical display of media files grouped by sequence
    with Latest Date → Version sorting and collapsible group headers.
    """
    
    # Signals
    mediaSelected = Signal(dict)  # media_item
    mediaDoubleClicked = Signal(dict)  # media_item
    
    def __init__(self, parent=None):
        """Initialize grouped media widget."""
        super().__init__(parent)
        
        # State
        self.media_items: List[Dict[str, Any]] = []
        self.grouped_data: Dict[str, List[Dict[str, Any]]] = {}
        self.current_selection: Optional[Dict[str, Any]] = None
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Set up the grouped media widget user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create tree widget for hierarchical display
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Media Files", "Version", "Status", "Author"])
        self.tree_widget.setRootIsDecorated(True)
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tree_widget.setUniformRowHeights(False)
        
        # Configure tree widget appearance
        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                background-color: #fafafa;
                border: 1px solid #ddd;
                font-size: 12px;
            }
            QTreeWidget::item {
                padding: 4px;
                border-bottom: 1px solid #eee;
            }
            QTreeWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #e8f5e8;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(none);
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                border-image: none;
                image: url(none);
            }
        """)
        
        # Configure header
        header = self.tree_widget.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Media Files column
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Version column
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Status column
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Author column
        
        layout.addWidget(self.tree_widget)
        
        # Summary label
        self.summary_label = QLabel("No media files loaded")
        self.summary_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                padding: 5px;
                background-color: #f5f5f5;
                border-top: 1px solid #ddd;
            }
        """)
        layout.addWidget(self.summary_label)
    
    def setup_connections(self):
        """Set up signal connections."""
        self.tree_widget.itemSelectionChanged.connect(self.on_selection_changed)
        self.tree_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
    
    def set_media_items(self, media_items: List[Dict[str, Any]]):
        """Set media items and update the grouped display."""
        self.media_items = media_items
        self.group_media_by_sequence()
        self.populate_tree_widget()
        self.update_summary()
    
    def group_media_by_sequence(self):
        """Group media items by sequence."""
        self.grouped_data.clear()
        
        for item in self.media_items:
            # Extract sequence from task_id
            task_id = item.get('task_id', '')
            sequence = self.extract_sequence_from_task_id(task_id)
            
            if sequence not in self.grouped_data:
                self.grouped_data[sequence] = []
            
            self.grouped_data[sequence].append(item)
        
        # Sort items within each group
        for sequence in self.grouped_data:
            self.grouped_data[sequence] = self.sort_media_items(self.grouped_data[sequence])
    
    def extract_sequence_from_task_id(self, task_id: str) -> str:
        """Extract sequence identifier from task_id."""
        if not task_id:
            return "unknown"
        
        parts = task_id.split('_')
        if len(parts) >= 2:
            return parts[1]  # sq010, sq020, etc.
        
        return "unknown"
    
    def sort_media_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort media items by Latest Date → Version."""
        def sort_key(item):
            # Primary sort: Latest date (most recent first)
            created_date = item.get('created_date', '')
            try:
                date_obj = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                date_timestamp = date_obj.timestamp()
            except:
                date_timestamp = 0
            
            # Secondary sort: Version (v003, v002, v001)
            version = item.get('version', 'v001')
            version_num = 0
            try:
                if version.startswith('v'):
                    version_num = int(version[1:])
            except:
                version_num = 0
            
            # Return tuple for sorting (negative date for descending, negative version for descending)
            return (-date_timestamp, -version_num)
        
        return sorted(items, key=sort_key)
    
    def populate_tree_widget(self):
        """Populate the tree widget with grouped media data."""
        self.tree_widget.clear()
        
        # Sort sequences for consistent display
        sorted_sequences = sorted(self.grouped_data.keys())
        
        for sequence in sorted_sequences:
            items = self.grouped_data[sequence]
            if not items:
                continue
            
            # Create sequence group header
            group_item = QTreeWidgetItem(self.tree_widget)
            group_item.setText(0, f"📁 {sequence.upper()} - Sequence {sequence[2:]} ({len(items)} files)")
            group_item.setText(1, "")
            group_item.setText(2, "")
            group_item.setText(3, "")
            
            # Style group header
            font = QFont()
            font.setBold(True)
            font.setPointSize(11)
            group_item.setFont(0, font)
            group_item.setBackground(0, Qt.lightGray)
            group_item.setBackground(1, Qt.lightGray)
            group_item.setBackground(2, Qt.lightGray)
            group_item.setBackground(3, Qt.lightGray)
            
            # Set group item as non-selectable
            group_item.setFlags(group_item.flags() & ~Qt.ItemIsSelectable)
            
            # Add media items to group
            for media_item in items:
                self.add_media_item_to_group(group_item, media_item)
            
            # Expand group by default
            group_item.setExpanded(True)
    
    def add_media_item_to_group(self, group_item: QTreeWidgetItem, media_item: Dict[str, Any]):
        """Add a media item to a sequence group."""
        item = QTreeWidgetItem(group_item)
        
        # Format media file name with icon
        file_name = media_item.get('file_name', 'Unknown')
        media_type = media_item.get('media_type', 'unknown')
        file_extension = media_item.get('file_extension', '')
        
        # Add type icon
        if media_type == 'video':
            icon = "🎬"
        elif file_extension in ['.exr', '.jpg', '.jpeg', '.png', '.tiff']:
            icon = "🖼️"
        else:
            icon = "📄"
        
        # Truncate long file names
        display_name = file_name
        if len(display_name) > 50:
            display_name = display_name[:47] + "..."
        
        item.setText(0, f"{icon} {display_name}")
        
        # Version
        version = media_item.get('version', 'v001')
        item.setText(1, version)
        
        # Status with emoji
        status = media_item.get('approval_status', 'pending')
        status_display = self.format_status_display(status)
        item.setText(2, status_display)
        
        # Author
        author = media_item.get('author', 'Unknown')
        item.setText(3, author)
        
        # Store media item data
        item.setData(0, Qt.UserRole, media_item)
        
        # Style based on status
        self.style_item_by_status(item, status)
    
    def format_status_display(self, status: str) -> str:
        """Format status with appropriate emoji."""
        status_map = {
            'pending': '⏳ Pending',
            'under_review': '👁️ Under Review',
            'approved': '✅ Approved',
            'rejected': '❌ Rejected',
            'archived': '📦 Archived'
        }
        return status_map.get(status, f"❓ {status.title()}")
    
    def style_item_by_status(self, item: QTreeWidgetItem, status: str):
        """Apply styling based on approval status."""
        if status == 'approved':
            item.setBackground(0, Qt.green.lighter(180))
            item.setBackground(1, Qt.green.lighter(180))
            item.setBackground(2, Qt.green.lighter(180))
            item.setBackground(3, Qt.green.lighter(180))
        elif status == 'rejected':
            item.setBackground(0, Qt.red.lighter(180))
            item.setBackground(1, Qt.red.lighter(180))
            item.setBackground(2, Qt.red.lighter(180))
            item.setBackground(3, Qt.red.lighter(180))
        elif status == 'under_review':
            item.setBackground(0, Qt.yellow.lighter(180))
            item.setBackground(1, Qt.yellow.lighter(180))
            item.setBackground(2, Qt.yellow.lighter(180))
            item.setBackground(3, Qt.yellow.lighter(180))
    
    def update_summary(self):
        """Update the summary label with media statistics."""
        if not self.media_items:
            self.summary_label.setText("No media files loaded")
            return
        
        total_files = len(self.media_items)
        total_sequences = len(self.grouped_data)
        
        # Count by status
        status_counts = {}
        for item in self.media_items:
            status = item.get('approval_status', 'pending')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Format summary
        summary_parts = [f"{total_files} files in {total_sequences} sequences"]
        
        if status_counts:
            status_summary = []
            for status, count in status_counts.items():
                emoji = {'pending': '⏳', 'under_review': '👁️', 'approved': '✅', 'rejected': '❌'}.get(status, '❓')
                status_summary.append(f"{emoji}{count}")
            summary_parts.append(" | ".join(status_summary))
        
        self.summary_label.setText(" | ".join(summary_parts))
    
    def on_selection_changed(self):
        """Handle selection changes in the tree widget."""
        selected_items = self.tree_widget.selectedItems()
        if not selected_items:
            self.current_selection = None
            return
        
        item = selected_items[0]
        media_item = item.data(0, Qt.UserRole)
        
        if media_item:  # Only emit for media items, not group headers
            self.current_selection = media_item
            self.mediaSelected.emit(media_item)
    
    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double-click events."""
        media_item = item.data(0, Qt.UserRole)
        if media_item:
            self.mediaDoubleClicked.emit(media_item)
    
    def get_selected_media_item(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected media item."""
        return self.current_selection
    
    def clear(self):
        """Clear all media items and reset the widget."""
        self.media_items.clear()
        self.grouped_data.clear()
        self.current_selection = None
        self.tree_widget.clear()
        self.summary_label.setText("No media files loaded")
