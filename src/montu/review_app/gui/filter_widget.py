"""
Filter Widget

Advanced filtering controls for the Review Application providing
Episode, Sequence, Shot, Artist, Status, and File Type filtering.
"""

from typing import Dict, List, Any, Optional, Set
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QComboBox, QPushButton, QCheckBox, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class FilterWidget(QWidget):
    """
    Advanced filtering widget for media organization.
    
    Provides filtering controls for Episode, Sequence, Shot, Artist,
    Approval Status, and File Type with multi-select capabilities.
    """
    
    # Signals
    filtersChanged = Signal(dict)  # filter_criteria
    filtersCleared = Signal()      # all filters cleared
    
    def __init__(self, parent=None):
        """Initialize filter widget."""
        super().__init__(parent)
        
        # Filter state
        self.current_filters: Dict[str, Any] = {
            'episodes': set(),
            'sequences': set(),
            'shots': set(),
            'artists': set(),
            'statuses': set(),
            'file_types': set()
        }
        
        # Available options (populated from data)
        self.available_options: Dict[str, Set[str]] = {
            'episodes': set(),
            'sequences': set(),
            'shots': set(),
            'artists': set(),
            'statuses': set(),
            'file_types': set()
        }
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Set up the filter widget user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Filter group
        filter_group = QGroupBox("Advanced Filters")
        filter_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        filter_layout = QVBoxLayout(filter_group)
        
        # Create filter controls
        self.create_filter_controls(filter_layout)
        
        # Action buttons
        self.create_action_buttons(filter_layout)
        
        layout.addWidget(filter_group)
        layout.addStretch()
    
    def create_filter_controls(self, layout):
        """Create individual filter control sections."""
        # Episode filter
        self.episode_combo = self.create_filter_combo("Episode:", "All Episodes")
        layout.addWidget(self.episode_combo)
        
        # Sequence filter
        self.sequence_combo = self.create_filter_combo("Sequence:", "All Sequences")
        layout.addWidget(self.sequence_combo)
        
        # Shot filter
        self.shot_combo = self.create_filter_combo("Shot:", "All Shots")
        layout.addWidget(self.shot_combo)
        
        # Artist filter
        self.artist_combo = self.create_filter_combo("Artist:", "All Artists")
        layout.addWidget(self.artist_combo)
        
        # Status filter
        self.status_combo = self.create_filter_combo("Status:", "All Statuses")
        layout.addWidget(self.status_combo)
        
        # File Type filter
        self.file_type_combo = self.create_filter_combo("File Type:", "All Types")
        layout.addWidget(self.file_type_combo)
    
    def create_filter_combo(self, label_text: str, default_text: str) -> QWidget:
        """Create a filter combo box with label."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Label
        label = QLabel(label_text)
        label.setStyleSheet("font-weight: bold; color: #333;")
        layout.addWidget(label)
        
        # Combo box
        combo = QComboBox()
        combo.addItem(default_text, "all")
        combo.setStyleSheet("""
            QComboBox {
                padding: 4px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
            QComboBox:hover {
                border-color: #4CAF50;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666;
                margin-right: 5px;
            }
        """)
        layout.addWidget(combo)
        
        return container
    
    def create_action_buttons(self, layout):
        """Create action buttons for filter operations."""
        buttons_layout = QHBoxLayout()
        
        # Clear filters button
        self.clear_button = QPushButton("Clear All")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        buttons_layout.addWidget(self.clear_button)
        
        # Apply filters button
        self.apply_button = QPushButton("Apply Filters")
        self.apply_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        buttons_layout.addWidget(self.apply_button)
        
        layout.addLayout(buttons_layout)
    
    def setup_connections(self):
        """Set up signal connections."""
        # Combo box changes
        self.episode_combo.findChild(QComboBox).currentTextChanged.connect(self.on_filter_changed)
        self.sequence_combo.findChild(QComboBox).currentTextChanged.connect(self.on_filter_changed)
        self.shot_combo.findChild(QComboBox).currentTextChanged.connect(self.on_filter_changed)
        self.artist_combo.findChild(QComboBox).currentTextChanged.connect(self.on_filter_changed)
        self.status_combo.findChild(QComboBox).currentTextChanged.connect(self.on_filter_changed)
        self.file_type_combo.findChild(QComboBox).currentTextChanged.connect(self.on_filter_changed)
        
        # Button clicks
        self.clear_button.clicked.connect(self.clear_all_filters)
        self.apply_button.clicked.connect(self.apply_filters)
    
    def populate_filter_options(self, media_items: List[Dict[str, Any]]):
        """Populate filter options from media data."""
        # Clear existing options
        for key in self.available_options:
            self.available_options[key].clear()
        
        # Extract unique values from media items
        for item in media_items:
            task_id = item.get('task_id', '')
            
            # Parse task_id for episode, sequence, shot
            if task_id:
                parts = task_id.split('_')
                if len(parts) >= 3:
                    episode = parts[0]  # ep00
                    sequence = parts[1]  # sq010
                    shot = parts[2]     # sh020
                    
                    self.available_options['episodes'].add(episode)
                    self.available_options['sequences'].add(sequence)
                    self.available_options['shots'].add(shot)
            
            # Extract other filter options
            author = item.get('author', '')
            if author:
                self.available_options['artists'].add(author)
            
            status = item.get('approval_status', '')
            if status:
                self.available_options['statuses'].add(status.replace('_', ' ').title())
            
            file_ext = item.get('file_extension', '')
            if file_ext:
                self.available_options['file_types'].add(file_ext)
        
        # Update combo boxes
        self.update_combo_options()
    
    def update_combo_options(self):
        """Update combo box options with available values."""
        combos = [
            (self.episode_combo.findChild(QComboBox), 'episodes', 'All Episodes'),
            (self.sequence_combo.findChild(QComboBox), 'sequences', 'All Sequences'),
            (self.shot_combo.findChild(QComboBox), 'shots', 'All Shots'),
            (self.artist_combo.findChild(QComboBox), 'artists', 'All Artists'),
            (self.status_combo.findChild(QComboBox), 'statuses', 'All Statuses'),
            (self.file_type_combo.findChild(QComboBox), 'file_types', 'All Types')
        ]
        
        for combo, option_key, default_text in combos:
            # Clear existing items (except "All" option)
            combo.clear()
            combo.addItem(default_text, "all")
            
            # Add sorted options
            options = sorted(list(self.available_options[option_key]))
            for option in options:
                combo.addItem(option, option)
    
    def on_filter_changed(self):
        """Handle filter change events."""
        # Auto-apply filters when changed (optional - can be disabled for manual apply only)
        pass
    
    def apply_filters(self):
        """Apply current filter selections."""
        # Get current selections
        filters = {
            'episode': self.episode_combo.findChild(QComboBox).currentData(),
            'sequence': self.sequence_combo.findChild(QComboBox).currentData(),
            'shot': self.shot_combo.findChild(QComboBox).currentData(),
            'artist': self.artist_combo.findChild(QComboBox).currentData(),
            'status': self.status_combo.findChild(QComboBox).currentData(),
            'file_type': self.file_type_combo.findChild(QComboBox).currentData()
        }
        
        # Remove "all" selections
        active_filters = {k: v for k, v in filters.items() if v != "all"}
        
        # Emit signal
        self.filtersChanged.emit(active_filters)
        
        print(f"Applied filters: {active_filters}")
    
    def clear_all_filters(self):
        """Clear all filter selections."""
        # Reset all combo boxes to "All" option
        combos = [
            self.episode_combo.findChild(QComboBox),
            self.sequence_combo.findChild(QComboBox),
            self.shot_combo.findChild(QComboBox),
            self.artist_combo.findChild(QComboBox),
            self.status_combo.findChild(QComboBox),
            self.file_type_combo.findChild(QComboBox)
        ]
        
        for combo in combos:
            combo.setCurrentIndex(0)  # Select "All" option
        
        # Clear filter state
        for key in self.current_filters:
            self.current_filters[key].clear()
        
        # Emit signal
        self.filtersCleared.emit()
        
        print("All filters cleared")
    
    def get_active_filters(self) -> Dict[str, Any]:
        """Get currently active filter criteria."""
        filters = {
            'episode': self.episode_combo.findChild(QComboBox).currentData(),
            'sequence': self.sequence_combo.findChild(QComboBox).currentData(),
            'shot': self.shot_combo.findChild(QComboBox).currentData(),
            'artist': self.artist_combo.findChild(QComboBox).currentData(),
            'status': self.status_combo.findChild(QComboBox).currentData(),
            'file_type': self.file_type_combo.findChild(QComboBox).currentData()
        }
        
        # Remove "all" selections
        return {k: v for k, v in filters.items() if v != "all"}
