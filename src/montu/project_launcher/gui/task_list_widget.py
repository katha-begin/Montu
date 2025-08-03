"""
Task List Widget

Widget for displaying and managing tasks in the Project Launcher.
Provides table view with filtering, sorting, and task operations.
"""

from typing import Dict, List, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QHeaderView,
    QLineEdit, QComboBox, QPushButton, QLabel, QGroupBox,
    QMenu, QMessageBox, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QAction

from ..models.task_list_model import TaskListModel


class TaskListWidget(QWidget):
    """
    Task list display widget with filtering and management capabilities.
    
    Provides table-based view of tasks with status updates, filtering,
    and file operations integration.
    """
    
    # Signals
    taskSelected = Signal(str)           # task_id
    taskStatusChanged = Signal(str, str) # task_id, new_status
    taskPriorityChanged = Signal(str, str) # task_id, new_priority
    openWorkingFile = Signal(str)        # task_id
    refreshRequested = Signal()
    
    # Status options for filtering and updates
    STATUS_OPTIONS = [
        ('All Statuses', ''),
        ('Not Started', 'not_started'),
        ('In Progress', 'in_progress'),
        ('Completed', 'completed'),
        ('On Hold', 'on_hold'),
        ('Cancelled', 'cancelled'),
        ('Approved', 'approved')
    ]
    
    # Task type options for filtering
    TASK_TYPE_OPTIONS = [
        ('All Tasks', ''),
        ('Lighting', 'Lighting'),
        ('Composite', 'Composite'),
        ('Modeling', 'Modeling'),
        ('Rigging', 'Rigging'),
        ('Animation', 'Animation'),
        ('FX', 'FX'),
        ('Layout', 'Layout'),
        ('Lookdev', 'Lookdev')
    ]
    
    def __init__(self, parent=None):
        """Initialize task list widget."""
        super().__init__(parent)
        
        # Initialize model
        self.task_model = TaskListModel(self)
        
        # State
        self.current_filters = {}
        self.selected_task_id: Optional[str] = None
        
        # Setup UI and connections
        self.setup_ui()
        self.setup_connections()
        
        # Setup refresh timer for auto-refresh
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh)
        self.refresh_timer.start(30000)  # Auto-refresh every 30 seconds
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Filters section
        filters_group = QGroupBox("Filters")
        filters_layout = QHBoxLayout(filters_group)
        
        # Search filter
        filters_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search tasks, artists, sequences...")
        self.search_edit.setMaximumWidth(200)
        filters_layout.addWidget(self.search_edit)
        
        # Status filter
        filters_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        for display_name, value in self.STATUS_OPTIONS:
            self.status_filter.addItem(display_name, value)
        filters_layout.addWidget(self.status_filter)
        
        # Task type filter
        filters_layout.addWidget(QLabel("Task:"))
        self.task_type_filter = QComboBox()
        for display_name, value in self.TASK_TYPE_OPTIONS:
            self.task_type_filter.addItem(display_name, value)
        filters_layout.addWidget(self.task_type_filter)
        
        # Clear filters button
        self.clear_filters_button = QPushButton("Clear Filters")
        filters_layout.addWidget(self.clear_filters_button)
        
        filters_layout.addStretch()
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        filters_layout.addWidget(self.refresh_button)
        
        layout.addWidget(filters_group)
        
        # Task table
        table_group = QGroupBox("Tasks")
        table_layout = QVBoxLayout(table_group)
        
        # Task count label
        self.task_count_label = QLabel("No tasks loaded")
        self.task_count_label.setStyleSheet("color: #666; font-style: italic;")
        table_layout.addWidget(self.task_count_label)
        
        # Table view
        self.task_table = QTableView()
        self.task_table.setModel(self.task_model)
        self.task_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.task_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.task_table.setAlternatingRowColors(True)
        self.task_table.setSortingEnabled(True)
        self.task_table.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Configure table headers
        header = self.task_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        # Set column widths
        self.task_table.setColumnWidth(0, 200)  # Task ID
        self.task_table.setColumnWidth(1, 80)   # Episode
        self.task_table.setColumnWidth(2, 100)  # Sequence
        self.task_table.setColumnWidth(3, 100)  # Shot
        self.task_table.setColumnWidth(4, 100)  # Task
        self.task_table.setColumnWidth(5, 120)  # Artist
        self.task_table.setColumnWidth(6, 100)  # Status
        self.task_table.setColumnWidth(7, 80)   # Priority
        self.task_table.setColumnWidth(8, 100)  # Frame Range
        self.task_table.setColumnWidth(9, 80)   # Duration
        
        table_layout.addWidget(self.task_table)
        layout.addWidget(table_group)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        self.open_file_button = QPushButton("Open Working File")
        self.open_file_button.setEnabled(False)
        actions_layout.addWidget(self.open_file_button)
        
        self.update_status_button = QPushButton("Update Status")
        self.update_status_button.setEnabled(False)
        actions_layout.addWidget(self.update_status_button)
        
        actions_layout.addStretch()
        
        self.selected_task_label = QLabel("No task selected")
        self.selected_task_label.setStyleSheet("color: #666; font-style: italic;")
        actions_layout.addWidget(self.selected_task_label)
        
        layout.addLayout(actions_layout)
    
    def setup_connections(self):
        """Set up signal connections."""
        # Filter connections
        self.search_edit.textChanged.connect(self.apply_filters)
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        self.task_type_filter.currentTextChanged.connect(self.apply_filters)
        self.clear_filters_button.clicked.connect(self.clear_filters)
        
        # Table connections
        self.task_table.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.task_table.customContextMenuRequested.connect(self.show_context_menu)
        self.task_table.doubleClicked.connect(self.on_task_double_clicked)
        
        # Action button connections
        self.open_file_button.clicked.connect(self.open_selected_working_file)
        self.update_status_button.clicked.connect(self.update_selected_status)
        self.refresh_button.clicked.connect(self.request_refresh)
        
        # Model connections - DO NOT connect taskStatusChanged to avoid infinite loop
        # The TaskListWidget emits taskStatusChanged directly, MainWindow handles it
    
    def set_tasks(self, tasks: List[Dict[str, Any]]):
        """Set task data for display."""
        self.task_model.set_tasks(tasks)
        self.update_task_count()
        
        # Clear selection
        self.task_table.clearSelection()
        self.selected_task_id = None
        self.update_selection_ui()
    
    def apply_filters(self):
        """Apply current filter settings."""
        filters = {}

        # Search filter
        search_text = self.search_edit.text().strip()
        if search_text:
            filters['search'] = search_text

        # Status filter
        status_value = self.status_filter.currentData()
        if status_value:  # Only add if not empty string
            filters['status'] = status_value

        # Task type filter
        task_type_value = self.task_type_filter.currentData()
        if task_type_value:  # Only add if not empty string
            filters['task'] = task_type_value

        self.current_filters = filters
        self.task_model.apply_filters(filters)
        self.task_model.refresh_filters()
        self.update_task_count()
    
    def clear_filters(self):
        """Clear all filters."""
        self.search_edit.clear()
        self.status_filter.setCurrentIndex(0)
        self.task_type_filter.setCurrentIndex(0)
        self.current_filters = {}
        self.task_model.apply_filters({})
        self.task_model.refresh_filters()
        self.update_task_count()
    
    def update_task_count(self):
        """Update task count display."""
        total_tasks = len(self.task_model.tasks)
        filtered_tasks = len(self.task_model.filtered_tasks)
        
        if self.current_filters:
            self.task_count_label.setText(f"Showing {filtered_tasks} of {total_tasks} tasks")
        else:
            self.task_count_label.setText(f"{total_tasks} tasks")
    
    def on_selection_changed(self):
        """Handle task selection change."""
        selection = self.task_table.selectionModel().selectedRows()
        
        if selection:
            row = selection[0].row()
            task = self.task_model.get_task_by_row(row)
            if task:
                self.selected_task_id = task.get('_id')
                self.taskSelected.emit(self.selected_task_id)
        else:
            self.selected_task_id = None
        
        self.update_selection_ui()
    
    def update_selection_ui(self):
        """Update UI based on current selection."""
        has_selection = self.selected_task_id is not None
        
        self.open_file_button.setEnabled(has_selection)
        self.update_status_button.setEnabled(has_selection)
        
        if has_selection:
            task = self.task_model.get_task_by_id(self.selected_task_id)
            if task:
                task_display = f"{task.get('shot', 'Unknown')} - {task.get('task', 'Unknown')}"
                self.selected_task_label.setText(f"Selected: {task_display}")
            else:
                self.selected_task_label.setText("Selected: Unknown task")
        else:
            self.selected_task_label.setText("No task selected")
    
    def show_context_menu(self, position):
        """Show context menu for task operations."""
        if not self.selected_task_id:
            return
        
        menu = QMenu(self)
        
        # Open working file action
        open_action = QAction("Open Working File", self)
        open_action.triggered.connect(self.open_selected_working_file)
        menu.addAction(open_action)
        
        menu.addSeparator()
        
        # Status update actions
        status_menu = menu.addMenu("Update Status")
        for display_name, status_value in self.STATUS_OPTIONS[1:]:  # Skip "All Statuses"
            action = QAction(display_name, self)
            action.triggered.connect(lambda checked, s=status_value: self.update_task_status(s))
            status_menu.addAction(action)

        # Priority update actions
        priority_menu = menu.addMenu("Change Priority")
        priority_options = [
            ('Low', 'low'),
            ('Medium', 'medium'),
            ('High', 'high'),
            ('Urgent', 'urgent')
        ]

        for display_name, priority_value in priority_options:
            action = QAction(display_name, self)
            action.triggered.connect(lambda checked, p=priority_value: self.update_task_priority(p))
            priority_menu.addAction(action)

        menu.exec(self.task_table.mapToGlobal(position))
    
    def on_task_double_clicked(self, index):
        """Handle task double-click."""
        if self.selected_task_id:
            self.open_selected_working_file()
    
    def open_selected_working_file(self):
        """Open working file for selected task."""
        if self.selected_task_id:
            self.openWorkingFile.emit(self.selected_task_id)
    
    def update_selected_status(self):
        """Show status update dialog for selected task."""
        if not self.selected_task_id:
            return
        
        # Simple status update - could be enhanced with a dialog
        task = self.task_model.get_task_by_id(self.selected_task_id)
        if not task:
            return
        
        current_status = task.get('status', 'not_started')
        
        # Cycle through common statuses
        status_cycle = ['not_started', 'in_progress', 'completed']
        try:
            current_index = status_cycle.index(current_status)
            next_status = status_cycle[(current_index + 1) % len(status_cycle)]
        except ValueError:
            next_status = 'in_progress'
        
        self.update_task_status(next_status)
    
    def update_task_status(self, status: str):
        """Update status for selected task."""
        if self.selected_task_id:
            self.taskStatusChanged.emit(self.selected_task_id, status)

    def update_task_priority(self, priority: str):
        """Update priority for selected task."""
        if not self.selected_task_id:
            return

        # Get current task info
        task = self.task_model.get_task_by_id(self.selected_task_id)
        if not task:
            return

        task_display = f"{task.get('shot', 'Unknown')} - {task.get('task', 'Unknown')}"

        # Show confirmation dialog for priority changes
        reply = QMessageBox.question(
            self,
            "Change Priority",
            f"Change priority for '{task_display}' to {priority.title()}?\n\n"
            "This may affect task scheduling and resource allocation.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Emit signal to update priority (similar to status update)
            self.taskPriorityChanged.emit(self.selected_task_id, priority)
    
    def request_refresh(self):
        """Request task list refresh."""
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("Refreshing...")
        self.refreshRequested.emit()
    
    def refresh_complete(self):
        """Called when refresh is complete."""
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText("Refresh")
    
    def auto_refresh(self):
        """Auto-refresh task list."""
        if not self.refresh_button.isEnabled():
            return  # Already refreshing
        
        self.refreshRequested.emit()
    
    def get_selected_task_id(self) -> Optional[str]:
        """Get currently selected task ID."""
        return self.selected_task_id
