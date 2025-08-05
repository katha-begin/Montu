"""
Scalable Task Management Widget for Ra: Task Creator

High-performance task management widget for handling large CSV imports and task datasets.
"""

from typing import Dict, List, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QHeaderView,
    QGroupBox, QLabel, QSplitter, QFrame, QProgressBar, QPushButton,
    QCheckBox, QSpinBox, QComboBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

from ...shared.scalable_task_model import ScalableTaskModel
from ...shared.pagination_widget import PaginationWidget, AdvancedFilterWidget
from ...shared.advanced_search_widget import AdvancedSearchWidget


class ScalableTaskManagementWidget(QWidget):
    """
    High-performance task management widget for Ra: Task Creator.
    
    Features:
    - Handles large CSV imports (200+ tasks) efficiently
    - Batch operations with progress tracking
    - Advanced filtering and search
    - Memory-efficient task editing
    - Bulk task selection and operations
    - Real-time validation feedback
    """
    
    # Signals
    taskSelectionChanged = Signal(list)  # selected_task_ids
    tasksModified = Signal(list)         # modified_task_ids
    bulkOperationRequested = Signal(str, list)  # operation, task_ids
    validationRequested = Signal(list)   # task_ids
    
    def __init__(self, db_instance, parent=None):
        """Initialize scalable task management widget."""
        super().__init__(parent)
        
        # Database connection
        self.db = db_instance
        
        # Initialize scalable model
        self.task_model = ScalableTaskModel(self.db, self)
        
        # State
        self.selected_task_ids: List[str] = []
        self.modified_task_ids: List[str] = []
        self.bulk_operation_mode = False
        
        # Setup UI and connections
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Header with task statistics
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("Task Management")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        self.title_label.setFont(title_font)
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Task statistics
        self.stats_label = QLabel("No tasks loaded")
        self.stats_label.setStyleSheet("color: #666; font-size: 11px;")
        header_layout.addWidget(self.stats_label)
        
        layout.addLayout(header_layout)
        
        # Main content splitter
        main_splitter = QSplitter(Qt.Vertical)
        
        # Search and filters section
        search_filters_widget = self.create_search_filters_section()
        main_splitter.addWidget(search_filters_widget)
        
        # Task table section
        table_widget = self.create_table_section()
        main_splitter.addWidget(table_widget)
        
        # Bulk operations section
        bulk_ops_widget = self.create_bulk_operations_section()
        main_splitter.addWidget(bulk_ops_widget)
        
        # Pagination section
        pagination_widget = self.create_pagination_section()
        main_splitter.addWidget(pagination_widget)
        
        # Set splitter proportions
        main_splitter.setSizes([120, 350, 80, 60])
        main_splitter.setChildrenCollapsible(False)
        
        layout.addWidget(main_splitter)
    
    def create_search_filters_section(self) -> QWidget:
        """Create search and filters section."""
        section = QGroupBox("Search & Filters")
        layout = QVBoxLayout(section)
        
        # Advanced search widget
        self.search_widget = AdvancedSearchWidget()
        layout.addWidget(self.search_widget)
        
        # Task Creator specific filters
        filters_layout = QHBoxLayout()
        
        # Validation status filter
        filters_layout.addWidget(QLabel("Validation:"))
        self.validation_filter = QComboBox()
        self.validation_filter.addItems([
            "All Tasks", "Valid Tasks", "Invalid Tasks", "Modified Tasks"
        ])
        filters_layout.addWidget(self.validation_filter)
        
        # Import batch filter
        filters_layout.addWidget(QLabel("Import Batch:"))
        self.batch_filter = QComboBox()
        self.batch_filter.addItems(["All Batches", "Latest Import", "Previous Imports"])
        filters_layout.addWidget(self.batch_filter)
        
        filters_layout.addStretch()
        layout.addLayout(filters_layout)
        
        return section
    
    def create_table_section(self) -> QWidget:
        """Create task table section."""
        section = QGroupBox("Tasks")
        layout = QVBoxLayout(section)
        
        # Table controls
        controls_layout = QHBoxLayout()
        
        # Select all checkbox
        self.select_all_cb = QCheckBox("Select All")
        controls_layout.addWidget(self.select_all_cb)
        
        controls_layout.addStretch()
        
        # Selection info
        self.selection_label = QLabel("0 selected")
        self.selection_label.setStyleSheet("color: #666; font-size: 11px;")
        controls_layout.addWidget(self.selection_label)
        
        layout.addLayout(controls_layout)
        
        # Loading indicator
        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 0)  # Indeterminate
        self.loading_bar.setVisible(False)
        layout.addWidget(self.loading_bar)
        
        # Task table
        self.task_table = QTableView()
        self.task_table.setModel(self.task_model)
        self.task_table.setSelectionBehavior(QTableView.SelectRows)
        self.task_table.setSelectionMode(QTableView.ExtendedSelection)  # Multi-select
        self.task_table.setAlternatingRowColors(True)
        self.task_table.setSortingEnabled(True)
        self.task_table.setShowGrid(True)
        
        # Configure table headers
        header = self.task_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        layout.addWidget(self.task_table)
        
        return section
    
    def create_bulk_operations_section(self) -> QWidget:
        """Create bulk operations section."""
        section = QGroupBox("Bulk Operations")
        layout = QHBoxLayout(section)
        
        # Bulk operation buttons
        self.bulk_validate_btn = QPushButton("Validate Selected")
        self.bulk_validate_btn.setEnabled(False)
        layout.addWidget(self.bulk_validate_btn)
        
        self.bulk_delete_btn = QPushButton("Delete Selected")
        self.bulk_delete_btn.setEnabled(False)
        self.bulk_delete_btn.setStyleSheet("QPushButton { color: red; }")
        layout.addWidget(self.bulk_delete_btn)
        
        self.bulk_export_btn = QPushButton("Export Selected")
        self.bulk_export_btn.setEnabled(False)
        layout.addWidget(self.bulk_export_btn)
        
        layout.addStretch()
        
        # Batch size control
        layout.addWidget(QLabel("Batch Size:"))
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(10, 1000)
        self.batch_size_spin.setValue(100)
        self.batch_size_spin.setSuffix(" tasks")
        layout.addWidget(self.batch_size_spin)
        
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
        
        # Filter connections
        self.validation_filter.currentTextChanged.connect(self.on_validation_filter_changed)
        self.batch_filter.currentTextChanged.connect(self.on_batch_filter_changed)
        
        # Table connections
        self.select_all_cb.toggled.connect(self.on_select_all_toggled)
        self.task_table.selectionModel().selectionChanged.connect(self.on_selection_changed)
        
        # Bulk operation connections
        self.bulk_validate_btn.clicked.connect(self.on_bulk_validate)
        self.bulk_delete_btn.clicked.connect(self.on_bulk_delete)
        self.bulk_export_btn.clicked.connect(self.on_bulk_export)
        
        # Pagination connections
        self.pagination_widget.pageChanged.connect(self.on_page_changed)
        self.pagination_widget.pageSizeChanged.connect(self.on_page_size_changed)
        
        # Model connections
        self.task_model.loadingStateChanged.connect(self.on_loading_state_changed)
        self.task_model.totalCountChanged.connect(self.on_total_count_changed)
    
    def on_search_changed(self, search_text: str):
        """Handle search text changes."""
        self.task_model.set_search_text(search_text)
    
    def on_search_cleared(self):
        """Handle search cleared."""
        self.task_model.set_search_text("")
    
    def on_validation_filter_changed(self, filter_text: str):
        """Handle validation filter changes."""
        # Apply validation-specific filters
        filters = {}
        if filter_text == "Valid Tasks":
            filters['validation_status'] = 'valid'
        elif filter_text == "Invalid Tasks":
            filters['validation_status'] = 'invalid'
        elif filter_text == "Modified Tasks":
            filters['modified'] = True
        
        self.task_model.apply_filters(filters)
    
    def on_batch_filter_changed(self, filter_text: str):
        """Handle batch filter changes."""
        # Apply batch-specific filters
        filters = {}
        if filter_text == "Latest Import":
            filters['import_batch'] = 'latest'
        elif filter_text == "Previous Imports":
            filters['import_batch'] = 'previous'
        
        self.task_model.apply_filters(filters)
    
    def on_select_all_toggled(self, checked: bool):
        """Handle select all checkbox."""
        if checked:
            self.task_table.selectAll()
        else:
            self.task_table.clearSelection()
    
    def on_selection_changed(self, selected, deselected):
        """Handle task selection changes."""
        selected_rows = self.task_table.selectionModel().selectedRows()
        self.selected_task_ids = []
        
        for index in selected_rows:
            task = self.task_model.get_task_by_row(index.row())
            if task:
                self.selected_task_ids.append(task.get('_id'))
        
        # Update UI
        self.update_selection_ui()
        self.taskSelectionChanged.emit(self.selected_task_ids)
    
    def update_selection_ui(self):
        """Update selection-related UI elements."""
        count = len(self.selected_task_ids)
        self.selection_label.setText(f"{count} selected")
        
        # Enable/disable bulk operation buttons
        has_selection = count > 0
        self.bulk_validate_btn.setEnabled(has_selection)
        self.bulk_delete_btn.setEnabled(has_selection)
        self.bulk_export_btn.setEnabled(has_selection)
    
    def on_bulk_validate(self):
        """Handle bulk validation request."""
        if self.selected_task_ids:
            self.bulkOperationRequested.emit("validate", self.selected_task_ids)
    
    def on_bulk_delete(self):
        """Handle bulk delete request."""
        if self.selected_task_ids:
            self.bulkOperationRequested.emit("delete", self.selected_task_ids)
    
    def on_bulk_export(self):
        """Handle bulk export request."""
        if self.selected_task_ids:
            self.bulkOperationRequested.emit("export", self.selected_task_ids)
    
    def on_page_changed(self, page_number: int):
        """Handle page navigation."""
        self.task_model.load_page(page_number)
    
    def on_page_size_changed(self, page_size: int):
        """Handle page size changes."""
        self.task_model.page_size = page_size
        self.task_model.reset_model()
    
    def on_loading_state_changed(self, is_loading: bool):
        """Handle loading state changes."""
        self.loading_bar.setVisible(is_loading)
        self.pagination_widget.set_loading_state(is_loading)
    
    def on_total_count_changed(self, total_count: int):
        """Handle total count changes."""
        pagination_info = self.task_model.get_pagination_info()
        self.pagination_widget.update_pagination_info(pagination_info)
        
        # Update statistics
        self.stats_label.setText(f"Total: {total_count} tasks")
    
    def load_tasks_from_csv(self, tasks: List[Dict[str, Any]]):
        """Load tasks from CSV import."""
        # This method would be called after CSV import
        # For now, we'll just trigger a model refresh
        self.task_model.reset_model()
    
    def get_performance_info(self) -> Dict[str, Any]:
        """Get performance information."""
        pagination_info = self.task_model.get_pagination_info()
        return {
            'total_tasks': pagination_info['total_items'],
            'selected_tasks': len(self.selected_task_ids),
            'modified_tasks': len(self.modified_task_ids),
            'current_page': pagination_info['current_page'],
            'total_pages': pagination_info['total_pages'],
            'cache_size': len(self.task_model.task_cache),
            'memory_usage': len(self.task_model.tasks)
        }
