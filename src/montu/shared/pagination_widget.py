"""
Pagination Widget

Reusable pagination control widget for navigating large datasets.
"""

from typing import Dict, Any
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox, 
    QSpinBox, QProgressBar, QFrame
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont


class PaginationWidget(QWidget):
    """
    Pagination control widget with navigation and page size controls.
    
    Features:
    - First/Previous/Next/Last navigation
    - Direct page number input
    - Page size selection
    - Loading indicator
    - Item count display
    """
    
    # Signals
    pageChanged = Signal(int)        # new_page_number (0-based)
    pageSizeChanged = Signal(int)    # new_page_size
    refreshRequested = Signal()
    
    # Page size options
    PAGE_SIZE_OPTIONS = [25, 50, 100, 200, 500]
    
    def __init__(self, parent=None):
        """Initialize pagination widget."""
        super().__init__(parent)
        
        # State
        self.current_page = 0
        self.total_pages = 0
        self.total_items = 0
        self.page_size = 100
        self.is_loading = False
        
        self.setup_ui()
        self.setup_connections()
        self.update_display()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Loading indicator
        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0)  # Indeterminate progress
        self.loading_bar.setMaximumHeight(20)
        self.loading_bar.setVisible(False)
        layout.addWidget(self.loading_bar)
        
        # Item count display
        self.item_count_label = QLabel("No items")
        self.item_count_label.setStyleSheet("color: #666; font-weight: bold;")
        layout.addWidget(self.item_count_label)
        
        layout.addStretch()
        
        # Page size selector
        layout.addWidget(QLabel("Items per page:"))
        self.page_size_combo = QComboBox()
        for size in self.PAGE_SIZE_OPTIONS:
            self.page_size_combo.addItem(str(size), size)
        self.page_size_combo.setCurrentText("100")
        layout.addWidget(self.page_size_combo)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Navigation buttons
        self.first_button = QPushButton("⏮")
        self.first_button.setToolTip("First page")
        self.first_button.setMaximumWidth(30)
        layout.addWidget(self.first_button)
        
        self.prev_button = QPushButton("◀")
        self.prev_button.setToolTip("Previous page")
        self.prev_button.setMaximumWidth(30)
        layout.addWidget(self.prev_button)
        
        # Page number input
        layout.addWidget(QLabel("Page:"))
        self.page_spinbox = QSpinBox()
        self.page_spinbox.setMinimum(1)
        self.page_spinbox.setMaximum(1)
        self.page_spinbox.setValue(1)
        self.page_spinbox.setMaximumWidth(60)
        layout.addWidget(self.page_spinbox)
        
        self.page_info_label = QLabel("of 1")
        layout.addWidget(self.page_info_label)
        
        self.next_button = QPushButton("▶")
        self.next_button.setToolTip("Next page")
        self.next_button.setMaximumWidth(30)
        layout.addWidget(self.next_button)
        
        self.last_button = QPushButton("⏭")
        self.last_button.setToolTip("Last page")
        self.last_button.setMaximumWidth(30)
        layout.addWidget(self.last_button)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator2)
        
        # Refresh button
        self.refresh_button = QPushButton("🔄")
        self.refresh_button.setToolTip("Refresh data")
        self.refresh_button.setMaximumWidth(30)
        layout.addWidget(self.refresh_button)
    
    def setup_connections(self):
        """Set up signal connections."""
        self.first_button.clicked.connect(self.go_to_first_page)
        self.prev_button.clicked.connect(self.go_to_previous_page)
        self.next_button.clicked.connect(self.go_to_next_page)
        self.last_button.clicked.connect(self.go_to_last_page)
        self.page_spinbox.valueChanged.connect(self.on_page_number_changed)
        self.page_size_combo.currentTextChanged.connect(self.on_page_size_changed)
        self.refresh_button.clicked.connect(self.refreshRequested.emit)
    
    def update_pagination_info(self, info: Dict[str, Any]):
        """Update pagination display with new information."""
        self.current_page = info.get('current_page', 1) - 1  # Convert to 0-based
        self.total_pages = info.get('total_pages', 1)
        self.total_items = info.get('total_items', 0)
        self.page_size = info.get('page_size', 100)
        
        start_item = info.get('start_item', 0)
        end_item = info.get('end_item', 0)
        items_on_page = info.get('items_on_page', 0)
        
        # Update item count display
        if self.total_items == 0:
            self.item_count_label.setText("No items")
        elif self.total_items <= self.page_size:
            self.item_count_label.setText(f"{self.total_items} items")
        else:
            self.item_count_label.setText(
                f"Showing {start_item}-{end_item} of {self.total_items} items"
            )
        
        # Update page controls
        self.page_spinbox.setMaximum(max(1, self.total_pages))
        self.page_spinbox.setValue(self.current_page + 1)  # Convert to 1-based
        self.page_info_label.setText(f"of {self.total_pages}")
        
        # Update page size combo
        self.page_size_combo.setCurrentText(str(self.page_size))
        
        self.update_button_states()
    
    def update_button_states(self):
        """Update navigation button enabled states."""
        has_items = self.total_items > 0
        is_first_page = self.current_page == 0
        is_last_page = self.current_page >= self.total_pages - 1
        
        self.first_button.setEnabled(has_items and not is_first_page and not self.is_loading)
        self.prev_button.setEnabled(has_items and not is_first_page and not self.is_loading)
        self.next_button.setEnabled(has_items and not is_last_page and not self.is_loading)
        self.last_button.setEnabled(has_items and not is_last_page and not self.is_loading)
        self.page_spinbox.setEnabled(has_items and not self.is_loading)
        self.page_size_combo.setEnabled(not self.is_loading)
        self.refresh_button.setEnabled(not self.is_loading)
    
    def set_loading_state(self, is_loading: bool):
        """Set loading state and update UI."""
        self.is_loading = is_loading
        self.loading_bar.setVisible(is_loading)
        self.update_button_states()
        
        if is_loading:
            self.item_count_label.setText("Loading...")
    
    def go_to_first_page(self):
        """Navigate to first page."""
        if self.current_page != 0:
            self.pageChanged.emit(0)
    
    def go_to_previous_page(self):
        """Navigate to previous page."""
        if self.current_page > 0:
            self.pageChanged.emit(self.current_page - 1)
    
    def go_to_next_page(self):
        """Navigate to next page."""
        if self.current_page < self.total_pages - 1:
            self.pageChanged.emit(self.current_page + 1)
    
    def go_to_last_page(self):
        """Navigate to last page."""
        last_page = max(0, self.total_pages - 1)
        if self.current_page != last_page:
            self.pageChanged.emit(last_page)
    
    def on_page_number_changed(self, page_number: int):
        """Handle page number spinbox change."""
        # Convert from 1-based to 0-based
        target_page = page_number - 1
        if target_page != self.current_page and 0 <= target_page < self.total_pages:
            self.pageChanged.emit(target_page)
    
    def on_page_size_changed(self, size_text: str):
        """Handle page size combo change."""
        try:
            new_size = int(size_text)
            if new_size != self.page_size:
                self.page_size = new_size
                self.pageSizeChanged.emit(new_size)
        except ValueError:
            pass
    
    def update_display(self):
        """Update all display elements."""
        self.update_button_states()
        
        # Set default display
        if self.total_items == 0:
            self.item_count_label.setText("No items")
            self.page_info_label.setText("of 1")
            self.page_spinbox.setMaximum(1)
            self.page_spinbox.setValue(1)


class AdvancedFilterWidget(QWidget):
    """
    Advanced filtering widget with multiple filter types.
    
    Provides comprehensive filtering options for large datasets.
    """
    
    # Signals
    filtersChanged = Signal(dict)  # filters_dict
    filtersCleared = Signal()
    
    def __init__(self, parent=None):
        """Initialize advanced filter widget."""
        super().__init__(parent)
        
        # Filter state
        self.current_filters = {}
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QHBoxLayout(self)
        
        # Quick filters
        layout.addWidget(QLabel("Quick Filters:"))
        
        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "All Statuses", "Not Started", "In Progress", 
            "Completed", "On Hold", "Cancelled", "Approved"
        ])
        layout.addWidget(self.status_filter)
        
        self.task_type_filter = QComboBox()
        self.task_type_filter.addItems([
            "All Tasks", "Lighting", "Composite", "Modeling", 
            "Rigging", "Animation", "FX"
        ])
        layout.addWidget(self.task_type_filter)
        
        self.priority_filter = QComboBox()
        self.priority_filter.addItems([
            "All Priorities", "Low", "Medium", "High", "Urgent"
        ])
        layout.addWidget(self.priority_filter)
        
        layout.addStretch()
        
        # Clear filters button
        self.clear_button = QPushButton("Clear All Filters")
        layout.addWidget(self.clear_button)
    
    def setup_connections(self):
        """Set up signal connections."""
        self.status_filter.currentTextChanged.connect(self.on_filters_changed)
        self.task_type_filter.currentTextChanged.connect(self.on_filters_changed)
        self.priority_filter.currentTextChanged.connect(self.on_filters_changed)
        self.clear_button.clicked.connect(self.clear_all_filters)
    
    def on_filters_changed(self):
        """Handle filter changes."""
        filters = {}
        
        # Status filter
        status = self.status_filter.currentText()
        if status != "All Statuses":
            filters['status'] = status.lower().replace(' ', '_')
        
        # Task type filter
        task_type = self.task_type_filter.currentText()
        if task_type != "All Tasks":
            filters['task'] = task_type.lower()
        
        # Priority filter
        priority = self.priority_filter.currentText()
        if priority != "All Priorities":
            filters['priority'] = priority.lower()
        
        self.current_filters = filters
        self.filtersChanged.emit(filters)
    
    def clear_all_filters(self):
        """Clear all filters."""
        self.status_filter.setCurrentIndex(0)
        self.task_type_filter.setCurrentIndex(0)
        self.priority_filter.setCurrentIndex(0)
        self.current_filters = {}
        self.filtersCleared.emit()
    
    def get_current_filters(self) -> Dict[str, Any]:
        """Get current filter settings."""
        return self.current_filters.copy()
