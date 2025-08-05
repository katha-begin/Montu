"""
Scalable Task Widget

High-performance task management widget for handling large datasets in Project Launcher.
"""

from typing import Dict, List, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QHeaderView,
    QGroupBox, QLabel, QSplitter, QFrame, QProgressBar, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

from ...shared.scalable_task_model import ScalableTaskModel
from ...shared.pagination_widget import PaginationWidget, AdvancedFilterWidget
from ...shared.advanced_search_widget import AdvancedSearchWidget


class ScalableTaskWidget(QWidget):
    """
    High-performance task management widget with pagination and advanced filtering.
    
    Features:
    - Handles 500+ tasks efficiently with pagination
    - Advanced search with debouncing
    - Real-time filtering
    - Virtual scrolling for smooth performance
    - Memory-efficient data loading
    - Performance monitoring
    """
    
    # Signals
    taskSelected = Signal(str)           # task_id
    taskStatusChanged = Signal(str, str) # task_id, new_status
    taskPriorityChanged = Signal(str, str) # task_id, new_priority
    openWorkingFile = Signal(str)        # task_id
    refreshRequested = Signal()
    
    def __init__(self, db_instance, parent=None):
        """Initialize scalable task widget."""
        super().__init__(parent)
        
        # Database connection
        self.db = db_instance
        
        # Initialize scalable model
        self.task_model = ScalableTaskModel(self.db, self)
        
        # State
        self.current_project_id = ""
        self.selected_task_id: Optional[str] = None
        self.show_archived_tasks = False  # Default: hide archived/cancelled tasks
        self.performance_stats = {
            'last_load_time': 0,
            'total_queries': 0,
            'cache_hits': 0
        }
        
        # Setup UI and connections
        self.setup_ui()
        self.setup_connections()

        # Apply default filter to hide cancelled tasks
        self.apply_default_filters()

        # Performance monitoring timer
        self.perf_timer = QTimer()
        self.perf_timer.timeout.connect(self.update_performance_stats)
        self.perf_timer.start(5000)  # Update every 5 seconds
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Header with performance info
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("Task Management")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        self.title_label.setFont(title_font)
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Performance indicator
        self.perf_label = QLabel("Ready")
        self.perf_label.setStyleSheet("color: #666; font-size: 10px;")
        header_layout.addWidget(self.perf_label)
        
        layout.addLayout(header_layout)
        
        # Main content splitter
        main_splitter = QSplitter(Qt.Vertical)
        
        # Search and filters section
        search_filters_widget = self.create_search_filters_section()
        main_splitter.addWidget(search_filters_widget)
        
        # Task table section
        table_widget = self.create_table_section()
        main_splitter.addWidget(table_widget)
        
        # Pagination section
        pagination_widget = self.create_pagination_section()
        main_splitter.addWidget(pagination_widget)
        
        # Set splitter proportions
        main_splitter.setSizes([150, 400, 80])  # Search: 150px, Table: 400px, Pagination: 80px
        main_splitter.setChildrenCollapsible(False)
        
        layout.addWidget(main_splitter)
    
    def create_search_filters_section(self) -> QWidget:
        """Create search and filters section."""
        section = QGroupBox("Search & Filters")
        layout = QVBoxLayout(section)

        # Advanced search widget
        self.search_widget = AdvancedSearchWidget()
        layout.addWidget(self.search_widget)

        # Advanced filters widget
        self.filters_widget = AdvancedFilterWidget()
        layout.addWidget(self.filters_widget)

        # Archived tasks filter
        archived_layout = QHBoxLayout()
        self.show_archived_checkbox = QCheckBox("Show Archived Tasks")
        self.show_archived_checkbox.setToolTip("Show tasks with 'cancelled' status (archived tasks)")
        self.show_archived_checkbox.setChecked(self.show_archived_tasks)
        archived_layout.addWidget(self.show_archived_checkbox)
        archived_layout.addStretch()
        layout.addLayout(archived_layout)

        return section
    
    def create_table_section(self) -> QWidget:
        """Create task table section."""
        section = QGroupBox("Tasks")
        layout = QVBoxLayout(section)
        
        # Loading indicator
        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0)  # Indeterminate
        self.loading_bar.setVisible(False)
        layout.addWidget(self.loading_bar)
        
        # Task table
        self.task_table = QTableView()
        self.task_table.setModel(self.task_model)
        self.task_table.setSelectionBehavior(QTableView.SelectRows)
        self.task_table.setSelectionMode(QTableView.SingleSelection)
        self.task_table.setAlternatingRowColors(True)
        self.task_table.setSortingEnabled(True)
        self.task_table.setShowGrid(False)
        
        # Configure table headers
        header = self.task_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        # Set column widths for better display
        self.task_table.setColumnWidth(0, 200)  # Task ID
        self.task_table.setColumnWidth(1, 80)   # Episode
        self.task_table.setColumnWidth(2, 100)  # Sequence
        self.task_table.setColumnWidth(3, 100)  # Shot
        self.task_table.setColumnWidth(4, 80)   # Task
        self.task_table.setColumnWidth(5, 100)  # Artist
        self.task_table.setColumnWidth(6, 100)  # Status
        self.task_table.setColumnWidth(7, 80)   # Priority
        
        layout.addWidget(self.task_table)
        
        return section
    
    def create_pagination_section(self) -> QWidget:
        """Create pagination section."""
        section = QFrame()
        section.setFrameStyle(QFrame.Box)
        layout = QVBoxLayout(section)
        
        # Pagination widget
        self.pagination_widget = PaginationWidget()
        layout.addWidget(self.pagination_widget)
        
        return section
    
    def setup_connections(self):
        """Set up signal connections."""
        # Search widget connections
        self.search_widget.searchChanged.connect(self.on_search_changed)
        self.search_widget.searchCleared.connect(self.on_search_cleared)
        self.search_widget.advancedSearchRequested.connect(self.on_advanced_search)
        
        # Filter widget connections
        self.filters_widget.filtersChanged.connect(self.on_filters_changed)
        self.filters_widget.filtersCleared.connect(self.on_filters_cleared)
        self.show_archived_checkbox.toggled.connect(self.on_show_archived_toggled)
        
        # Pagination widget connections
        self.pagination_widget.pageChanged.connect(self.on_page_changed)
        self.pagination_widget.pageSizeChanged.connect(self.on_page_size_changed)
        self.pagination_widget.refreshRequested.connect(self.refresh_data)
        
        # Model connections
        self.task_model.loadingStateChanged.connect(self.on_loading_state_changed)
        self.task_model.totalCountChanged.connect(self.on_total_count_changed)
        
        # Table connections
        self.task_table.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.task_table.doubleClicked.connect(self.on_task_double_clicked)
    
    def set_project(self, project_id: str):
        """Set current project and load tasks."""
        if self.current_project_id != project_id:
            self.current_project_id = project_id
            self.task_model.set_project(project_id)
            self.update_title()
    
    def update_title(self):
        """Update widget title with project info."""
        if self.current_project_id:
            self.title_label.setText(f"Task Management - {self.current_project_id}")
        else:
            self.title_label.setText("Task Management")
    
    def on_search_changed(self, search_text: str):
        """Handle search text changes."""
        self.task_model.set_search_text(search_text)
        self.update_search_suggestions()
    
    def on_search_cleared(self):
        """Handle search cleared."""
        self.task_model.set_search_text("")
    
    def on_advanced_search(self, criteria: Dict[str, Any]):
        """Handle advanced search request."""
        # Convert advanced search criteria to database query
        # This is a simplified implementation - can be expanded
        search_text = criteria.get('text', '')
        self.task_model.set_search_text(search_text)
    
    def on_filters_changed(self, filters: Dict[str, Any]):
        """Handle filter changes."""
        self.task_model.apply_filters(filters)
    
    def on_filters_cleared(self):
        """Handle filters cleared."""
        self.task_model.apply_filters({})
    
    def on_page_changed(self, page_number: int):
        """Handle page navigation."""
        self.task_model.load_page(page_number)
    
    def on_page_size_changed(self, page_size: int):
        """Handle page size changes."""
        self.task_model.page_size = page_size
        self.task_model.reset_model()  # Reload with new page size
    
    def on_loading_state_changed(self, is_loading: bool):
        """Handle loading state changes."""
        self.loading_bar.setVisible(is_loading)
        self.pagination_widget.set_loading_state(is_loading)
        
        if is_loading:
            self.perf_label.setText("Loading...")
        else:
            self.update_performance_stats()
    
    def on_total_count_changed(self, total_count: int):
        """Handle total count changes."""
        # Update pagination info
        pagination_info = self.task_model.get_pagination_info()
        self.pagination_widget.update_pagination_info(pagination_info)
    
    def on_selection_changed(self, selected, deselected):
        """Handle task selection changes."""
        indexes = selected.indexes()
        if indexes:
            row = indexes[0].row()
            task = self.task_model.get_task_by_row(row)
            if task:
                self.selected_task_id = task.get('_id')
                self.taskSelected.emit(self.selected_task_id)
        else:
            self.selected_task_id = None
    
    def on_task_double_clicked(self, index):
        """Handle task double-click."""
        if self.selected_task_id:
            self.openWorkingFile.emit(self.selected_task_id)
    
    def refresh_data(self):
        """Refresh current data."""
        self.task_model.task_cache.clear()  # Clear cache
        current_page = self.task_model.current_page
        self.task_model.load_page(current_page)
        self.refreshRequested.emit()
    
    def update_search_suggestions(self):
        """Update search suggestions based on current data."""
        # Extract unique values for suggestions
        suggestions = set()
        for task in self.task_model.tasks:
            suggestions.add(task.get('task', ''))
            suggestions.add(task.get('artist', ''))
            suggestions.add(task.get('status', ''))
        
        # Remove empty values and convert to list
        suggestions = [s for s in suggestions if s and s != 'Unassigned']
        self.search_widget.set_suggestions(sorted(suggestions))
    
    def update_performance_stats(self):
        """Update performance statistics display."""
        if not self.task_model.is_loading:
            pagination_info = self.task_model.get_pagination_info()
            cache_size = len(self.task_model.task_cache)
            
            self.perf_label.setText(
                f"Page {pagination_info['current_page']}/{pagination_info['total_pages']} | "
                f"Cache: {cache_size} pages | "
                f"Items: {pagination_info['items_on_page']}/{pagination_info['total_items']}"
            )
    
    def get_selected_task(self) -> Optional[Dict[str, Any]]:
        """Get currently selected task."""
        if self.selected_task_id:
            return self.task_model.get_task_by_id(self.selected_task_id)
        return None
    
    def get_performance_info(self) -> Dict[str, Any]:
        """Get performance information."""
        pagination_info = self.task_model.get_pagination_info()
        return {
            'total_tasks': pagination_info['total_items'],
            'current_page': pagination_info['current_page'],
            'total_pages': pagination_info['total_pages'],
            'cache_size': len(self.task_model.task_cache),
            'memory_usage': len(self.task_model.tasks),
            'is_loading': self.task_model.is_loading
        }

    def apply_default_filters(self):
        """Apply default filters on initialization."""
        # Hide cancelled/archived tasks by default
        filters = {'exclude_cancelled': True}
        self.task_model.apply_filters(filters)

    def on_show_archived_toggled(self, checked: bool):
        """Handle show archived tasks checkbox toggle."""
        self.show_archived_tasks = checked

        # Update filters
        current_filters = self.filters_widget.get_current_filters()
        if not checked:
            current_filters['exclude_cancelled'] = True
        else:
            current_filters.pop('exclude_cancelled', None)

        self.task_model.apply_filters(current_filters)

    def get_archived_task_count(self) -> int:
        """Get count of archived (cancelled) tasks."""
        return sum(1 for task in self.task_model.tasks if task.get('status') == 'cancelled')
