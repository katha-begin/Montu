"""
Task Creator Main Window

Main GUI window for the Task Creator application with CSV import,
pattern configuration, and batch task creation functionality.
"""

import sys
from pathlib import Path
from typing import List, Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QProgressBar, QSplitter, QGroupBox,
    QComboBox, QSpinBox, QCheckBox, QDialog, QHeaderView, QAbstractItemView,
    QTabWidget, QFrame, QDateEdit, QDoubleSpinBox, QApplication,
    QMenu, QToolBar, QStatusBar
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QDate, QDateTime
from PySide6.QtGui import QFont, QIcon, QColor, QBrush, QKeySequence, QUndoStack, QUndoCommand, QAction

from ..csv_parser import CSVParser, TaskRecord, NamingPattern
from .pattern_dialog import PatternConfigDialog
from .directory_preview_widget import DirectoryPreviewWidget
from .bulk_edit_dialog import BulkEditDialog

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from montu.shared.json_database import JSONDatabase
from ..directory_manager import DirectoryManager


class TaskImportWorker(QThread):
    """Worker thread for CSV import processing."""
    
    progress_updated = Signal(int)
    status_updated = Signal(str)
    import_completed = Signal(list, list)  # tasks, errors
    
    def __init__(self, csv_file: Path, naming_pattern: Optional[NamingPattern] = None):
        super().__init__()
        self.csv_file = csv_file
        self.naming_pattern = naming_pattern
        self.parser = CSVParser()
    
    def run(self):
        """Run the import process."""
        try:
            self.status_updated.emit("Reading CSV file...")
            self.progress_updated.emit(20)
            
            # Parse CSV
            tasks = self.parser.parse_csv_file(self.csv_file, self.naming_pattern)
            self.progress_updated.emit(60)
            
            self.status_updated.emit("Validating tasks...")
            
            # Validate tasks
            valid_tasks, errors = self.parser.validate_tasks(tasks)
            self.progress_updated.emit(100)
            
            self.status_updated.emit(f"Import completed: {len(valid_tasks)} tasks, {len(errors)} errors")
            self.import_completed.emit(valid_tasks, errors)
            
        except Exception as e:
            self.status_updated.emit(f"Import failed: {str(e)}")
            self.import_completed.emit([], [str(e)])


class TaskEditCommand(QUndoCommand):
    """Undo command for task editing operations."""

    def __init__(self, task_id: str, field: str, old_value, new_value, main_window):
        super().__init__(f"Edit {field} for {task_id}")
        self.task_id = task_id
        self.field = field
        self.old_value = old_value
        self.new_value = new_value
        self.main_window = main_window

    def redo(self):
        """Apply the edit."""
        self.main_window.apply_task_edit(self.task_id, self.field, self.new_value)

    def undo(self):
        """Revert the edit."""
        self.main_window.apply_task_edit(self.task_id, self.field, self.old_value)


class TaskCreatorMainWindow(QMainWindow):
    """Enhanced Task Creator with comprehensive task management functionality."""

    # Signals
    taskModified = Signal(str)  # task_id
    tasksLoaded = Signal(int)   # count

    def __init__(self):
        super().__init__()
        # Core data
        self.tasks: List[TaskRecord] = []
        self.current_project: Optional[str] = None
        self.modified_tasks: set = set()  # Track modified task IDs
        self.csv_file: Optional[Path] = None
        self.naming_pattern: Optional[NamingPattern] = None

        # Database and managers
        self.db = JSONDatabase()
        self.directory_manager: Optional[DirectoryManager] = None

        # Undo/Redo functionality
        self.undo_stack = QUndoStack(self)

        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save_changes)
        self.auto_save_timer.setSingleShot(True)

        # UI state
        self.is_editing_enabled = True
        self.last_save_time = QDateTime.currentDateTime()

        self.setup_ui()
        self.setup_connections()
        self.initialize_directory_manager()
        self.load_projects()

        # Enable auto-save (5 seconds after last edit)
        self.auto_save_timer.setInterval(5000)

    def load_projects(self):
        """Load available projects from database."""
        try:
            projects = self.db.find('project_configs')
            self.project_combo.clear()
            self.project_combo.addItem("Select Project...")

            for project in projects:
                self.project_combo.addItem(project['name'], project['_id'])

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load projects: {e}")

    def on_project_changed(self, project_name: str):
        """Handle project selection change."""
        print(f"DEBUG: Project changed to: {project_name}")
        if project_name == "Select Project...":
            self.current_project = None
            self.tasks = []
            self.update_task_table()
            self.update_task_summary()
            return

        # Get project ID from combo box data
        current_index = self.project_combo.currentIndex()
        print(f"DEBUG: Current combo index: {current_index}")
        if current_index > 0:  # Skip "Select Project..." item
            project_id = self.project_combo.itemData(current_index)
            print(f"DEBUG: Project ID from combo data: {project_id}")
            self.current_project = project_id
            self.load_project_tasks()

    def load_project_tasks(self):
        """Load tasks for the selected project."""
        if not self.current_project:
            print("DEBUG: No current project selected")
            return

        print(f"DEBUG: Loading tasks for project: {self.current_project}")
        try:
            # Load tasks from database
            tasks_data = self.db.find('tasks', {'project': self.current_project})
            print(f"DEBUG: Found {len(tasks_data)} tasks in database")

            # Convert to TaskRecord objects
            self.tasks = []
            for task_data in tasks_data:
                try:
                    task = TaskRecord.from_dict(task_data)
                    self.tasks.append(task)
                except Exception as e:
                    print(f"Error loading task {task_data.get('_id', 'unknown')}: {e}")

            print(f"DEBUG: Successfully loaded {len(self.tasks)} TaskRecord objects")

            # Update UI
            self.update_task_table()
            self.update_task_summary()
            self.update_filter_options()
            self.tasksLoaded.emit(len(self.tasks))

        except Exception as e:
            print(f"DEBUG: Exception in load_project_tasks: {e}")
            QMessageBox.warning(self, "Error", f"Failed to load project tasks: {e}")

    def update_task_table(self):
        """Update the task table with current tasks."""
        if not hasattr(self, 'task_management_table'):
            return  # Table not created yet (CSV import tab)

        # Disable editing during table population to prevent validation loops
        self.is_editing_enabled = False

        try:
            # Clear existing rows
            self.task_management_table.setRowCount(0)

            if not self.tasks:
                return

            # Filter tasks based on current filters
            filtered_tasks = self.get_filtered_tasks()

            # Set row count
            self.task_management_table.setRowCount(len(filtered_tasks))

            # Populate table
            for row, task in enumerate(filtered_tasks):
                self.populate_task_row(row, task)

            # Update selection count
            self.update_selection_count()

            # Perform validation summary after table is populated
            self.validate_task_data_summary(filtered_tasks)

        finally:
            # Re-enable editing after table population is complete
            self.is_editing_enabled = True

    def populate_task_row(self, row: int, task: TaskRecord):
        """Populate a single task row in the table."""
        # Column 0: Select checkbox
        checkbox = QCheckBox()
        self.task_management_table.setCellWidget(row, 0, checkbox)
        checkbox.stateChanged.connect(self.on_task_selection_changed)

        # Column 1: Task ID (read-only)
        task_id_item = QTableWidgetItem(task.task_id)
        task_id_item.setFlags(task_id_item.flags() & ~Qt.ItemIsEditable)
        if task.task_id in self.modified_tasks:
            task_id_item.setText(task.task_id + "*")
            task_id_item.setBackground(QBrush(QColor(255, 255, 200)))  # Light yellow
        self.task_management_table.setItem(row, 1, task_id_item)

        # Column 2: Episode (read-only)
        episode_item = QTableWidgetItem(task.episode)
        episode_item.setFlags(episode_item.flags() & ~Qt.ItemIsEditable)
        self.task_management_table.setItem(row, 2, episode_item)

        # Column 3: Sequence (read-only)
        sequence_item = QTableWidgetItem(task.sequence)
        sequence_item.setFlags(sequence_item.flags() & ~Qt.ItemIsEditable)
        self.task_management_table.setItem(row, 3, sequence_item)

        # Column 4: Shot (read-only)
        shot_item = QTableWidgetItem(task.shot)
        shot_item.setFlags(shot_item.flags() & ~Qt.ItemIsEditable)
        self.task_management_table.setItem(row, 4, shot_item)

        # Column 5: Task Type (read-only)
        task_type_item = QTableWidgetItem(task.task)
        task_type_item.setFlags(task_type_item.flags() & ~Qt.ItemIsEditable)
        self.task_management_table.setItem(row, 5, task_type_item)

        # Column 6: Artist (editable)
        artist_item = QTableWidgetItem(task.artist or "")
        self.task_management_table.setItem(row, 6, artist_item)

        # Column 7: Status (editable via combo)
        status_combo = QComboBox()
        status_combo.addItems(["not_started", "in_progress", "completed", "on_hold", "cancelled"])
        status_combo.setCurrentText(task.status)
        status_combo.currentTextChanged.connect(lambda value, r=row: self.on_status_changed(r, value))
        self.task_management_table.setCellWidget(row, 7, status_combo)

        # Column 8: Priority (editable via combo)
        priority_combo = QComboBox()
        priority_combo.addItems(["low", "medium", "high", "urgent"])
        priority_combo.setCurrentText(task.priority)
        priority_combo.currentTextChanged.connect(lambda value, r=row: self.on_priority_changed(r, value))
        self.task_management_table.setCellWidget(row, 8, priority_combo)

        # Column 9: Frame Range (editable)
        frame_range = f"{task.frame_range['start']}-{task.frame_range['end']}"
        frame_range_item = QTableWidgetItem(frame_range)
        self.task_management_table.setItem(row, 9, frame_range_item)

        # Column 10: Duration (editable)
        duration_item = QTableWidgetItem(str(task.estimated_duration_hours))
        self.task_management_table.setItem(row, 10, duration_item)

        # Column 11: Created (read-only)
        created_date = getattr(task, '_created_at', 'Unknown')
        if created_date and created_date != 'Unknown':
            try:
                created_dt = QDateTime.fromString(created_date, Qt.ISODate)
                created_display = created_dt.toString("yyyy-MM-dd hh:mm")
            except:
                created_display = created_date
        else:
            created_display = "Unknown"
        created_item = QTableWidgetItem(created_display)
        created_item.setFlags(created_item.flags() & ~Qt.ItemIsEditable)
        self.task_management_table.setItem(row, 11, created_item)

        # Column 12: Modified (read-only)
        modified_date = getattr(task, '_updated_at', 'Never')
        if modified_date and modified_date != 'Never':
            try:
                modified_dt = QDateTime.fromString(modified_date, Qt.ISODate)
                modified_display = modified_dt.toString("yyyy-MM-dd hh:mm")
            except:
                modified_display = modified_date
        else:
            modified_display = "Never"
        modified_item = QTableWidgetItem(modified_display)
        modified_item.setFlags(modified_item.flags() & ~Qt.ItemIsEditable)
        self.task_management_table.setItem(row, 12, modified_item)

        # Column 13: Actions (buttons)
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(2, 2, 2, 2)

        # Archive button
        archive_btn = QPushButton("Archive")
        archive_btn.setMaximumSize(60, 25)
        archive_btn.clicked.connect(lambda checked, r=row: self.archive_task(r))
        actions_layout.addWidget(archive_btn)

        self.task_management_table.setCellWidget(row, 13, actions_widget)

    def on_task_item_changed(self, item: QTableWidgetItem):
        """Handle task table cell edits."""
        if not self.is_editing_enabled:
            return

        row = item.row()
        column = item.column()
        new_value = item.text()

        # Get task ID for this row
        task_id_item = self.task_management_table.item(row, 1)
        if not task_id_item:
            return

        task_id = task_id_item.text().rstrip('*')  # Remove modification indicator

        # Find the task
        task = self.find_task_by_id(task_id)
        if not task:
            return

        # Validate and apply edit based on column
        try:
            if column == 6:  # Artist
                old_value = task.artist
                if self.validate_artist_edit(new_value):
                    self.apply_task_edit_with_undo(task_id, 'artist', old_value, new_value)
                else:
                    item.setText(old_value or "")  # Revert

            elif column == 9:  # Frame Range
                old_value = f"{task.frame_range['start']}-{task.frame_range['end']}"
                if self.validate_frame_range_edit(new_value):
                    self.apply_task_edit_with_undo(task_id, 'frame_range', old_value, new_value)
                else:
                    item.setText(old_value)  # Revert

            elif column == 10:  # Duration
                old_value = str(task.estimated_duration_hours)
                if self.validate_duration_edit(new_value):
                    self.apply_task_edit_with_undo(task_id, 'duration', old_value, new_value)
                else:
                    item.setText(old_value)  # Revert

        except Exception as e:
            QMessageBox.warning(self, "Edit Error", f"Failed to apply edit: {e}")
            self.update_task_table()  # Refresh table

    def on_status_changed(self, row: int, new_status: str):
        """Handle status change via combo box."""
        task_id_item = self.task_management_table.item(row, 1)
        if not task_id_item:
            return

        task_id = task_id_item.text().rstrip('*')
        task = self.find_task_by_id(task_id)
        if task:
            old_status = task.status
            self.apply_task_edit_with_undo(task_id, 'status', old_status, new_status)

    def on_priority_changed(self, row: int, new_priority: str):
        """Handle priority change via combo box."""
        task_id_item = self.task_management_table.item(row, 1)
        if not task_id_item:
            return

        task_id = task_id_item.text().rstrip('*')
        task = self.find_task_by_id(task_id)
        if task:
            old_priority = task.priority
            self.apply_task_edit_with_undo(task_id, 'priority', old_priority, new_priority)

    def apply_task_edit_with_undo(self, task_id: str, field: str, old_value, new_value):
        """Apply task edit with undo support."""
        if old_value != new_value:
            command = TaskEditCommand(task_id, field, old_value, new_value, self)
            self.undo_stack.push(command)

    def apply_task_edit(self, task_id: str, field: str, value):
        """Apply a task edit directly."""
        task = self.find_task_by_id(task_id)
        if not task:
            return

        # Apply the edit
        if field == 'artist':
            task.artist = value
        elif field == 'status':
            task.status = value
        elif field == 'priority':
            task.priority = value
        elif field == 'frame_range':
            start_str, end_str = value.split('-')
            task.frame_range = {'start': int(start_str.strip()), 'end': int(end_str.strip())}
        elif field == 'duration':
            task.estimated_duration_hours = float(value)

        # Mark as modified
        self.modified_tasks.add(task_id)
        self.taskModified.emit(task_id)

        # Update UI
        self.update_task_table()
        self.update_modified_indicator()

        # Start auto-save timer
        self.auto_save_timer.start()

    def find_task_by_id(self, task_id: str) -> Optional[TaskRecord]:
        """Find a task by its ID."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def validate_artist_edit(self, value: str) -> bool:
        """Validate artist field edit."""
        # Artist can be empty or any string
        return True

    def validate_frame_range_edit(self, value: str) -> bool:
        """Validate frame range edit."""
        try:
            if '-' not in value:
                QMessageBox.warning(self, "Invalid Frame Range",
                                  "Frame range must be in format 'start-end' (e.g., '1001-1100')")
                return False

            start_str, end_str = value.split('-', 1)
            start_frame = int(start_str.strip())
            end_frame = int(end_str.strip())

            if start_frame >= end_frame:
                QMessageBox.warning(self, "Invalid Frame Range",
                                  "Start frame must be less than end frame")
                return False

            if start_frame < 1:
                QMessageBox.warning(self, "Invalid Frame Range",
                                  "Frame numbers must be positive")
                return False

            return True

        except ValueError:
            QMessageBox.warning(self, "Invalid Frame Range",
                              "Frame range must contain valid integers")
            return False

    def validate_duration_edit(self, value: str) -> bool:
        """
        Validate duration edit for individual task editing.

        Duration is measured in working hours (8-hour business days).
        Reasonable ranges:
        - Small tasks: 1-8 hours (0.125-1 working day)
        - Medium tasks: 8-40 hours (1-5 working days)
        - Large tasks: 40-200 hours (5-25 working days)
        - Very large tasks: 200+ hours (25+ working days) - requires confirmation
        """
        try:
            duration = float(value)
            if duration <= 0:
                QMessageBox.warning(self, "Invalid Duration",
                                  "Duration must be a positive number")
                return False

            # Increased threshold for working hours (25 working days = 200 hours)
            if duration > 200:
                reply = QMessageBox.question(
                    self, "Large Duration Confirmation",
                    f"Duration of {duration} hours ({duration/8:.1f} working days) is very large.\n\n"
                    "This equals approximately:\n"
                    f"• {duration/8:.1f} working days (8-hour days)\n"
                    f"• {duration/24:.1f} calendar days (24-hour days)\n\n"
                    "Do you want to proceed with this duration?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                return reply == QMessageBox.Yes

            return True
        except ValueError:
            QMessageBox.warning(self, "Invalid Duration",
                              "Duration must be a valid number")
            return False

    def validate_task_data_summary(self, tasks: List[TaskRecord]):
        """
        Perform validation summary for all tasks and show non-blocking notifications.

        Args:
            tasks: List of tasks to validate
        """
        if not tasks:
            return

        validation_issues = []
        large_duration_tasks = []
        invalid_frame_ranges = []

        for task in tasks:
            # Check for large durations (over 200 working hours = 25 working days)
            if task.estimated_duration_hours > 200:
                working_days = task.estimated_duration_hours / 8
                calendar_days = task.estimated_duration_hours / 24
                large_duration_tasks.append({
                    'task_id': task.task_id,
                    'duration': task.estimated_duration_hours,
                    'working_days': working_days,
                    'calendar_days': calendar_days
                })

            # Check for invalid frame ranges
            try:
                start = task.frame_range.get('start', 0)
                end = task.frame_range.get('end', 0)
                if start >= end or start < 1:
                    invalid_frame_ranges.append({
                        'task_id': task.task_id,
                        'frame_range': f"{start}-{end}"
                    })
            except:
                invalid_frame_ranges.append({
                    'task_id': task.task_id,
                    'frame_range': 'Invalid'
                })

        # Show summary in status bar instead of blocking popups
        status_messages = []

        if large_duration_tasks:
            count = len(large_duration_tasks)
            max_duration = max(t['duration'] for t in large_duration_tasks)
            max_working_days = max_duration / 8
            status_messages.append(f"{count} tasks with large durations (max: {max_duration}h = {max_working_days:.1f} working days)")

        if invalid_frame_ranges:
            count = len(invalid_frame_ranges)
            status_messages.append(f"{count} tasks with invalid frame ranges")

        if status_messages:
            summary_message = " | ".join(status_messages)
            self.statusBar().showMessage(f"⚠️ Validation: {summary_message}", 10000)  # Show for 10 seconds

            # Also update the task count label to include validation info
            if hasattr(self, 'task_count_label'):
                total_tasks = len(tasks)
                issues_count = len(large_duration_tasks) + len(invalid_frame_ranges)
                self.task_count_label.setText(f"{total_tasks} tasks loaded ({issues_count} with validation warnings)")
        else:
            # Clear any previous validation messages
            if hasattr(self, 'task_count_label'):
                self.task_count_label.setText(f"{len(tasks)} tasks loaded")

    def setup_ui(self):
        """Set up the enhanced user interface with task management capabilities."""
        self.setWindowTitle("Ra: Task Creator - Task Management & CSV Import")
        self.setMinimumSize(1400, 900)

        # Create menu bar and toolbar
        self.create_menu_bar()
        self.create_toolbar()

        # Central widget with tab interface
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 5, 10, 10)
        layout.setSpacing(5)

        # Project selection header
        project_header = self.create_project_header()
        layout.addLayout(project_header)

        # Tab widget for different modes
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Task Management Tab
        task_management_tab = self.create_task_management_tab()
        self.tab_widget.addTab(task_management_tab, "Task Management")

        # CSV Import Tab
        csv_import_tab = self.create_csv_import_tab()
        self.tab_widget.addTab(csv_import_tab, "CSV Import")

        # Set default tab
        self.tab_widget.setCurrentIndex(0)

        # Enhanced status bar
        self.create_enhanced_status_bar()

    def create_menu_bar(self):
        """Create enhanced menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('&File')

        # Import CSV action
        import_csv_action = QAction('&Import CSV...', self)
        import_csv_action.setShortcut(QKeySequence('Ctrl+I'))
        import_csv_action.triggered.connect(self.browse_csv_file)
        file_menu.addAction(import_csv_action)

        # Export actions
        export_menu = file_menu.addMenu('&Export')

        export_json_action = QAction('Export to &JSON...', self)
        export_json_action.triggered.connect(self.export_to_json)
        export_menu.addAction(export_json_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu('&Edit')

        # Undo/Redo actions
        undo_action = self.undo_stack.createUndoAction(self, '&Undo')
        undo_action.setShortcut(QKeySequence.Undo)
        edit_menu.addAction(undo_action)

        redo_action = self.undo_stack.createRedoAction(self, '&Redo')
        redo_action.setShortcut(QKeySequence.Redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        # Bulk edit action
        bulk_edit_action = QAction('&Bulk Edit...', self)
        bulk_edit_action.setShortcut(QKeySequence('Ctrl+B'))
        bulk_edit_action.triggered.connect(self.show_bulk_edit_dialog)
        edit_menu.addAction(bulk_edit_action)

        # View menu
        view_menu = menubar.addMenu('&View')

        # Refresh action
        refresh_action = QAction('&Refresh', self)
        refresh_action.setShortcut(QKeySequence.Refresh)
        refresh_action.triggered.connect(self.refresh_tasks)
        view_menu.addAction(refresh_action)

    def create_toolbar(self):
        """Create main toolbar."""
        toolbar = self.addToolBar('Main')
        toolbar.setMovable(False)

        # Save action
        save_action = QAction('Save All', self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_all_changes)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        # Refresh action
        refresh_action = QAction('Refresh', self)
        refresh_action.triggered.connect(self.refresh_tasks)
        toolbar.addAction(refresh_action)

        toolbar.addSeparator()

        # Undo/Redo actions
        toolbar.addAction(self.undo_stack.createUndoAction(self, 'Undo'))
        toolbar.addAction(self.undo_stack.createRedoAction(self, 'Redo'))

    def create_enhanced_status_bar(self):
        """Create enhanced status bar with task information."""
        status_bar = self.statusBar()

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_bar.addPermanentWidget(self.progress_bar)

        # Task count label
        self.task_count_label = QLabel("No tasks loaded")
        status_bar.addPermanentWidget(self.task_count_label)

        # Modified tasks indicator
        self.modified_indicator = QLabel("")
        status_bar.addPermanentWidget(self.modified_indicator)

        # Last save time
        self.last_save_label = QLabel("")
        status_bar.addPermanentWidget(self.last_save_label)

        status_bar.showMessage("Ra: Task Creator - Ready for task management")

    def create_project_header(self) -> QHBoxLayout:
        """Create project selection header."""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 5, 0, 5)

        # Project selection
        project_label = QLabel("Project:")
        project_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(project_label)

        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(200)
        self.project_combo.currentTextChanged.connect(self.on_project_changed)
        layout.addWidget(self.project_combo)

        layout.addSpacing(20)

        # Task summary
        self.task_summary_label = QLabel("No project selected")
        self.task_summary_label.setStyleSheet("color: #666666; font-style: italic;")
        layout.addWidget(self.task_summary_label)

        layout.addStretch()

        # Quick actions
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_tasks)
        layout.addWidget(self.refresh_button)

        self.save_all_button = QPushButton("Save All Changes")
        self.save_all_button.setEnabled(False)
        self.save_all_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.save_all_button.clicked.connect(self.save_all_changes)
        layout.addWidget(self.save_all_button)

        return layout

    def create_task_management_tab(self) -> QWidget:
        """Create the main task management tab."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)

        # Task filtering and search
        filter_layout = self.create_task_filters()
        layout.addLayout(filter_layout)

        # Main task table
        self.task_management_table = QTableWidget()
        self.setup_task_management_table()
        layout.addWidget(self.task_management_table)

        # Task operations
        operations_layout = self.create_task_operations()
        layout.addLayout(operations_layout)

        return tab_widget

    def create_task_filters(self) -> QHBoxLayout:
        """Create task filtering controls."""
        layout = QHBoxLayout()

        # Search box
        search_label = QLabel("Search:")
        layout.addWidget(search_label)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search tasks by ID, artist, or description...")
        self.search_edit.textChanged.connect(self.filter_tasks)
        layout.addWidget(self.search_edit)

        layout.addSpacing(10)

        # Status filter
        status_label = QLabel("Status:")
        layout.addWidget(status_label)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "not_started", "in_progress", "completed", "on_hold", "cancelled"])
        self.status_filter.currentTextChanged.connect(self.filter_tasks)
        layout.addWidget(self.status_filter)

        # Task type filter
        type_label = QLabel("Task Type:")
        layout.addWidget(type_label)

        self.task_type_filter = QComboBox()
        self.task_type_filter.addItem("All")
        self.task_type_filter.currentTextChanged.connect(self.filter_tasks)
        layout.addWidget(self.task_type_filter)

        # Artist filter
        artist_label = QLabel("Artist:")
        layout.addWidget(artist_label)

        self.artist_filter = QComboBox()
        self.artist_filter.addItem("All")
        self.artist_filter.currentTextChanged.connect(self.filter_tasks)
        layout.addWidget(self.artist_filter)

        layout.addStretch()

        # Show archived tasks checkbox
        self.show_archived_checkbox = QCheckBox("Show Archived")
        self.show_archived_checkbox.setToolTip("Show tasks with 'cancelled' status (archived tasks)")
        self.show_archived_checkbox.setChecked(False)  # Default: hide archived tasks
        self.show_archived_checkbox.toggled.connect(self.filter_tasks)
        layout.addWidget(self.show_archived_checkbox)

        # Clear filters button
        clear_filters_btn = QPushButton("Clear Filters")
        clear_filters_btn.clicked.connect(self.clear_filters)
        layout.addWidget(clear_filters_btn)

        return layout

    def create_task_operations(self) -> QHBoxLayout:
        """Create task operation buttons."""
        layout = QHBoxLayout()

        # Archive selected tasks
        self.archive_button = QPushButton("Archive Selected")
        self.archive_button.setEnabled(False)
        self.archive_button.clicked.connect(self.archive_selected_tasks)
        layout.addWidget(self.archive_button)

        # Bulk edit
        self.bulk_edit_button = QPushButton("Bulk Edit...")
        self.bulk_edit_button.setEnabled(False)
        self.bulk_edit_button.clicked.connect(self.show_bulk_edit_dialog)
        layout.addWidget(self.bulk_edit_button)

        layout.addStretch()

        # Task count display
        self.selected_count_label = QLabel("0 tasks selected")
        layout.addWidget(self.selected_count_label)

        return layout

    def create_csv_import_tab(self) -> QWidget:
        """Create the CSV import tab (existing functionality)."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)

        # Main horizontal splitter (left: CSV import/preview, right: directory preview)
        main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)

        # Left side: CSV import and task preview (vertical splitter)
        left_splitter = QSplitter(Qt.Vertical)

        # Import section
        import_group = self.create_import_section()
        left_splitter.addWidget(import_group)

        # Preview section
        preview_group = self.create_preview_section()
        left_splitter.addWidget(preview_group)

        # Set proportions for left side (6% import, 94% preview)
        left_splitter.setSizes([40, 560])

        main_splitter.addWidget(left_splitter)

        # Right side: Directory preview section
        self.directory_preview = DirectoryPreviewWidget()
        main_splitter.addWidget(self.directory_preview)

        # Set main splitter proportions (70% left, 30% right)
        main_splitter.setSizes([840, 360])

        return tab_widget

    def setup_task_management_table(self):
        """Set up the enhanced task management table with editing capabilities."""
        # Define columns
        columns = [
            "Select", "Task ID", "Episode", "Sequence", "Shot", "Task Type",
            "Artist", "Status", "Priority", "Frame Range", "Duration (working hrs)",
            "Created", "Modified", "Actions"
        ]

        self.task_management_table.setColumnCount(len(columns))
        self.task_management_table.setHorizontalHeaderLabels(columns)

        # Add tooltips to clarify column meanings
        header = self.task_management_table.horizontalHeader()
        header.setToolTip("Duration column: Working hours (8-hour business days)\n"
                         "Examples: 8 hrs = 1 working day, 40 hrs = 1 working week")

        # Configure table properties
        self.task_management_table.setAlternatingRowColors(True)
        self.task_management_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.task_management_table.setSortingEnabled(True)
        self.task_management_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.EditKeyPressed)

        # Set column widths
        header = self.task_management_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Select checkbox
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # Task ID
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # Episode
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # Sequence
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # Shot
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # Task Type
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # Artist
        header.setSectionResizeMode(7, QHeaderView.Fixed)  # Status
        header.setSectionResizeMode(8, QHeaderView.Fixed)  # Priority
        header.setSectionResizeMode(9, QHeaderView.Fixed)  # Frame Range
        header.setSectionResizeMode(10, QHeaderView.Fixed)  # Duration
        header.setSectionResizeMode(11, QHeaderView.Fixed)  # Created
        header.setSectionResizeMode(12, QHeaderView.Fixed)  # Modified
        header.setSectionResizeMode(13, QHeaderView.Fixed)  # Actions

        # Set specific column widths
        self.task_management_table.setColumnWidth(0, 50)   # Select
        self.task_management_table.setColumnWidth(1, 200)  # Task ID
        self.task_management_table.setColumnWidth(2, 60)   # Episode
        self.task_management_table.setColumnWidth(3, 80)   # Sequence
        self.task_management_table.setColumnWidth(4, 80)   # Shot
        self.task_management_table.setColumnWidth(5, 80)   # Task Type
        self.task_management_table.setColumnWidth(7, 100)  # Status
        self.task_management_table.setColumnWidth(8, 80)   # Priority
        self.task_management_table.setColumnWidth(9, 120)  # Frame Range
        self.task_management_table.setColumnWidth(10, 80)  # Duration
        self.task_management_table.setColumnWidth(11, 100) # Created
        self.task_management_table.setColumnWidth(12, 100) # Modified
        self.task_management_table.setColumnWidth(13, 80)  # Actions

        # Connect signals
        self.task_management_table.itemChanged.connect(self.on_task_item_changed)
        self.task_management_table.itemSelectionChanged.connect(self.on_task_selection_changed)

    def create_header(self) -> QHBoxLayout:
        """Create header section with title and info."""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 2, 0, 2)  # Very minimal vertical margins
        layout.setSpacing(10)  # Reduce spacing between elements

        # Title
        title = QLabel("Task Creator")
        title_font = QFont()
        title_font.setPointSize(12)  # Reduced from 16 to 12
        title_font.setBold(True)
        title.setFont(title_font)
        title.setMaximumHeight(25)  # Limit title height
        layout.addWidget(title)

        layout.addStretch()

        # Info label
        info = QLabel("Import tasks from CSV files with intelligent naming pattern detection")
        info.setStyleSheet("color: #666; font-size: 10px;")  # Added smaller font size
        info.setMaximumHeight(20)  # Limit info label height
        layout.addWidget(info)

        return layout
    
    def create_import_section(self) -> QGroupBox:
        """Create CSV import section."""
        group = QGroupBox("CSV Import")
        layout = QVBoxLayout(group)
        
        # File selection
        file_layout = QHBoxLayout()
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select CSV file to import...")
        self.file_path_edit.setReadOnly(True)
        file_layout.addWidget(self.file_path_edit)
        
        self.browse_button = QPushButton("Browse...")
        file_layout.addWidget(self.browse_button)
        
        layout.addLayout(file_layout)
        
        # Pattern configuration
        pattern_layout = QHBoxLayout()
        
        pattern_layout.addWidget(QLabel("Naming Pattern:"))
        
        self.pattern_label = QLabel("Auto-detect")
        self.pattern_label.setStyleSheet("font-weight: bold; color: #0066cc;")
        pattern_layout.addWidget(self.pattern_label)
        
        pattern_layout.addStretch()
        
        self.configure_pattern_button = QPushButton("Configure Pattern...")
        self.configure_pattern_button.setEnabled(False)
        pattern_layout.addWidget(self.configure_pattern_button)
        
        layout.addLayout(pattern_layout)
        
        # Import controls
        controls_layout = QHBoxLayout()
        
        self.import_button = QPushButton("Import Tasks")
        self.import_button.setEnabled(False)
        self.import_button.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        controls_layout.addWidget(self.import_button)
        
        controls_layout.addStretch()

        # Save to database button
        self.save_to_db_button = QPushButton("Save to Database")
        self.save_to_db_button.setEnabled(False)
        self.save_to_db_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        controls_layout.addWidget(self.save_to_db_button)

        self.export_json_button = QPushButton("Export to JSON")
        self.export_json_button.setEnabled(False)
        controls_layout.addWidget(self.export_json_button)
        
        layout.addLayout(controls_layout)
        
        return group
    
    def create_preview_section(self) -> QGroupBox:
        """Create task preview section."""
        group = QGroupBox("Task Preview")
        layout = QVBoxLayout(group)
        
        # Summary
        self.summary_label = QLabel("No tasks loaded")
        self.summary_label.setStyleSheet("font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(self.summary_label)
        
        # Task preview table (for CSV import)
        self.csv_preview_table = QTableWidget()
        self.csv_preview_table.setAlternatingRowColors(True)
        self.csv_preview_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.csv_preview_table)
        
        # Error display
        self.error_text = QTextEdit()
        self.error_text.setMaximumHeight(150)
        self.error_text.setPlaceholderText("Import errors will appear here...")
        layout.addWidget(self.error_text)
        
        return group
    
    def setup_connections(self):
        """Set up signal connections."""
        self.browse_button.clicked.connect(self.browse_csv_file)
        self.configure_pattern_button.clicked.connect(self.configure_pattern)
        self.import_button.clicked.connect(self.import_tasks)
        self.save_to_db_button.clicked.connect(self.save_to_database)
        self.export_json_button.clicked.connect(self.export_to_json)

    # Task Management Methods

    def get_filtered_tasks(self) -> List[TaskRecord]:
        """Get tasks filtered by current filter settings."""
        if not self.tasks:
            return []

        filtered = self.tasks.copy()

        # Apply search filter
        if hasattr(self, 'search_edit') and self.search_edit.text().strip():
            search_text = self.search_edit.text().strip().lower()
            filtered = [task for task in filtered if
                       search_text in task.task_id.lower() or
                       search_text in (task.artist or "").lower() or
                       search_text in task.task.lower()]

        # Apply status filter
        if hasattr(self, 'status_filter') and self.status_filter.currentText() != "All":
            status = self.status_filter.currentText()
            filtered = [task for task in filtered if task.status == status]

        # Apply task type filter
        if hasattr(self, 'task_type_filter') and self.task_type_filter.currentText() != "All":
            task_type = self.task_type_filter.currentText()
            filtered = [task for task in filtered if task.task == task_type]

        # Apply artist filter
        if hasattr(self, 'artist_filter') and self.artist_filter.currentText() != "All":
            artist = self.artist_filter.currentText()
            filtered = [task for task in filtered if task.artist == artist]

        # Apply archived tasks filter (hide cancelled tasks by default)
        if hasattr(self, 'show_archived_checkbox') and not self.show_archived_checkbox.isChecked():
            filtered = [task for task in filtered if task.status != 'cancelled']

        return filtered

    def filter_tasks(self):
        """Apply current filters and update table."""
        self.update_task_table()

    def clear_filters(self):
        """Clear all filters except archived tasks filter."""
        if hasattr(self, 'search_edit'):
            self.search_edit.clear()
        if hasattr(self, 'status_filter'):
            self.status_filter.setCurrentText("All")
        if hasattr(self, 'task_type_filter'):
            self.task_type_filter.setCurrentText("All")
        if hasattr(self, 'artist_filter'):
            self.artist_filter.setCurrentText("All")
        # Keep archived tasks filter state - don't reset it
        self.update_task_table()

    def update_filter_options(self):
        """Update filter dropdown options based on current tasks."""
        if not hasattr(self, 'task_type_filter'):
            return

        # Update task type filter
        task_types = set(task.task for task in self.tasks)
        current_task_type = self.task_type_filter.currentText()
        self.task_type_filter.clear()
        self.task_type_filter.addItem("All")
        for task_type in sorted(task_types):
            self.task_type_filter.addItem(task_type)

        # Restore selection if still valid
        index = self.task_type_filter.findText(current_task_type)
        if index >= 0:
            self.task_type_filter.setCurrentIndex(index)

        # Update artist filter
        artists = set(task.artist for task in self.tasks if task.artist)
        current_artist = self.artist_filter.currentText()
        self.artist_filter.clear()
        self.artist_filter.addItem("All")
        for artist in sorted(artists):
            self.artist_filter.addItem(artist)

        # Restore selection if still valid
        index = self.artist_filter.findText(current_artist)
        if index >= 0:
            self.artist_filter.setCurrentIndex(index)

    def update_task_summary(self):
        """Update task summary display."""
        if not self.current_project:
            self.task_summary_label.setText("No project selected")
            return

        total_tasks = len(self.tasks)
        if total_tasks == 0:
            self.task_summary_label.setText("No tasks found for this project")
            return

        # Count by status
        status_counts = {}
        for task in self.tasks:
            status = task.status
            status_counts[status] = status_counts.get(status, 0) + 1

        # Create summary text
        summary_parts = [f"Total: {total_tasks}"]
        for status in ["not_started", "in_progress", "completed", "on_hold"]:
            count = status_counts.get(status, 0)
            if count > 0:
                summary_parts.append(f"{status.replace('_', ' ').title()}: {count}")

        self.task_summary_label.setText(" | ".join(summary_parts))

    def on_task_selection_changed(self):
        """Handle task selection changes."""
        self.update_selection_count()

        # Enable/disable buttons based on selection
        selected_count = self.get_selected_task_count()
        if hasattr(self, 'archive_button'):
            self.archive_button.setEnabled(selected_count > 0)
        if hasattr(self, 'bulk_edit_button'):
            self.bulk_edit_button.setEnabled(selected_count > 0)

    def get_selected_task_count(self) -> int:
        """Get number of selected tasks."""
        if not hasattr(self, 'task_management_table'):
            return 0

        count = 0
        for row in range(self.task_management_table.rowCount()):
            checkbox = self.task_management_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                count += 1
        return count

    def get_selected_tasks(self) -> List[TaskRecord]:
        """Get list of selected tasks."""
        if not hasattr(self, 'task_management_table'):
            return []

        selected_tasks = []
        for row in range(self.task_management_table.rowCount()):
            checkbox = self.task_management_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                task_id_item = self.task_management_table.item(row, 1)
                if task_id_item:
                    task_id = task_id_item.text().rstrip('*')
                    task = self.find_task_by_id(task_id)
                    if task:
                        selected_tasks.append(task)
        return selected_tasks

    def update_selection_count(self):
        """Update selection count display."""
        if hasattr(self, 'selected_count_label'):
            count = self.get_selected_task_count()
            self.selected_count_label.setText(f"{count} tasks selected")

    def archive_task(self, row: int):
        """Archive a single task."""
        task_id_item = self.task_management_table.item(row, 1)
        if not task_id_item:
            return

        task_id = task_id_item.text().rstrip('*')
        task = self.find_task_by_id(task_id)
        if not task:
            return

        reply = QMessageBox.question(
            self, "Archive Task",
            f"Archive task '{task_id}'?\n\nThis will change its status to 'cancelled' and hide it from the active view.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            old_status = task.status
            self.apply_task_edit_with_undo(task_id, 'status', old_status, 'cancelled')

    def archive_selected_tasks(self):
        """Archive all selected tasks."""
        selected_tasks = self.get_selected_tasks()
        if not selected_tasks:
            return

        reply = QMessageBox.question(
            self, "Archive Tasks",
            f"Archive {len(selected_tasks)} selected tasks?\n\nThis will change their status to 'cancelled' and hide them from the active view.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            for task in selected_tasks:
                old_status = task.status
                self.apply_task_edit_with_undo(task.task_id, 'status', old_status, 'cancelled')

    def show_bulk_edit_dialog(self):
        """Show bulk edit dialog for selected tasks."""
        selected_tasks = self.get_selected_tasks()
        if not selected_tasks:
            return

        dialog = BulkEditDialog(selected_tasks, self)
        if dialog.exec() == QDialog.Accepted:
            changes = dialog.get_changes()
            self.apply_bulk_changes(selected_tasks, changes)

    def apply_bulk_changes(self, tasks: List[TaskRecord], changes: dict):
        """Apply bulk changes to multiple tasks."""
        for task in tasks:
            for field, new_value in changes.items():
                if field == 'status':
                    old_value = task.status
                elif field == 'priority':
                    old_value = task.priority
                elif field == 'artist':
                    old_value = task.artist
                else:
                    continue

                if old_value != new_value:
                    self.apply_task_edit_with_undo(task.task_id, field, old_value, new_value)

    def refresh_tasks(self):
        """Refresh tasks from database."""
        if self.current_project:
            self.load_project_tasks()

    def auto_save_changes(self):
        """Auto-save modified tasks."""
        if self.modified_tasks:
            self.save_all_changes()

    def save_all_changes(self):
        """Save all modified tasks to database."""
        if not self.modified_tasks:
            QMessageBox.information(self, "No Changes", "No changes to save.")
            return

        try:
            saved_count = 0
            errors = []

            for task_id in self.modified_tasks:
                task = self.find_task_by_id(task_id)
                if task:
                    try:
                        task_dict = task.to_dict()
                        task_dict['_updated_at'] = QDateTime.currentDateTime().toString(Qt.ISODate)

                        # Upsert to database
                        result = self.db.upsert('tasks', {'_id': task_id}, {'$set': task_dict})
                        if result:
                            saved_count += 1
                        else:
                            errors.append(f"Failed to save task {task_id}")
                    except Exception as e:
                        errors.append(f"Error saving task {task_id}: {e}")

            # Clear modified tasks
            self.modified_tasks.clear()

            # Update UI
            self.update_modified_indicator()
            self.update_task_table()
            self.last_save_time = QDateTime.currentDateTime()
            self.update_last_save_display()

            # Show result
            if errors:
                QMessageBox.warning(
                    self, "Save Completed with Errors",
                    f"Saved {saved_count} tasks successfully.\n\nErrors:\n" + "\n".join(errors[:5])
                )
            else:
                self.statusBar().showMessage(f"Saved {saved_count} tasks successfully", 3000)

        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save changes: {e}")

    def update_modified_indicator(self):
        """Update the modified tasks indicator."""
        if hasattr(self, 'modified_indicator'):
            count = len(self.modified_tasks)
            if count > 0:
                self.modified_indicator.setText(f"{count} unsaved changes")
                self.modified_indicator.setStyleSheet("color: orange; font-weight: bold;")
                self.save_all_button.setEnabled(True)
            else:
                self.modified_indicator.setText("")
                self.save_all_button.setEnabled(False)

    def update_last_save_display(self):
        """Update last save time display."""
        if hasattr(self, 'last_save_label'):
            time_str = self.last_save_time.toString("hh:mm:ss")
            self.last_save_label.setText(f"Last saved: {time_str}")

    def toggle_active_filter(self, checked: bool):
        """Toggle showing only active tasks."""
        # This would be implemented to filter out cancelled/archived tasks
        self.update_task_table()

    def new_project(self):
        """Create a new project (placeholder)."""
        QMessageBox.information(self, "New Project", "New project creation will be implemented in a future version.")

    def export_to_csv(self):
        """Export current tasks to CSV."""
        if not self.tasks:
            QMessageBox.information(self, "No Tasks", "No tasks to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Tasks to CSV",
            str(Path.home() / "montu_tasks_export.csv"),
            "CSV Files (*.csv)"
        )

        if file_path:
            try:
                from ..csv_parser import CSVParser
                parser = CSVParser()
                parser.export_to_csv(self.tasks, Path(file_path))
                QMessageBox.information(self, "Export Successful", f"Tasks exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export tasks: {e}")

        # Directory preview connections
        self.directory_preview.directories_created.connect(self.on_directories_created)
        self.directory_preview.undo_requested.connect(self.on_undo_requested)
    
    def browse_csv_file(self):
        """Browse for CSV file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            str(Path.home()),
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            self.csv_file = Path(file_path)
            self.file_path_edit.setText(str(self.csv_file))
            self.configure_pattern_button.setEnabled(True)
            self.import_button.setEnabled(True)
            
            # Auto-detect pattern
            self.auto_detect_pattern()
    
    def auto_detect_pattern(self):
        """Auto-detect naming pattern from CSV file."""
        if not self.csv_file:
            return
        
        try:
            parser = CSVParser()
            
            # Read sample data for pattern detection
            import pandas as pd
            df = pd.read_csv(self.csv_file, nrows=5)  # Read first 5 rows
            sample_data = df.to_dict('records')
            
            # Detect patterns
            patterns = parser.detect_naming_patterns(sample_data)
            
            if patterns:
                self.naming_pattern = patterns[0]
                confidence = int(self.naming_pattern.confidence * 100)
                self.pattern_label.setText(f"Auto-detected ({confidence}% confidence)")
                self.pattern_label.setStyleSheet("font-weight: bold; color: #009900;")
            else:
                self.pattern_label.setText("No pattern detected")
                self.pattern_label.setStyleSheet("font-weight: bold; color: #cc6600;")
                
        except Exception as e:
            self.pattern_label.setText("Detection failed")
            self.pattern_label.setStyleSheet("font-weight: bold; color: #cc0000;")
            self.statusBar().showMessage(f"Pattern detection failed: {str(e)}")
    
    def configure_pattern(self):
        """Open pattern configuration dialog."""
        if not self.csv_file:
            return
        
        dialog = PatternConfigDialog(self.csv_file, self.naming_pattern, self)
        if dialog.exec() == QDialog.Accepted:
            self.naming_pattern = dialog.get_pattern()
            self.pattern_label.setText("Custom pattern")
            self.pattern_label.setStyleSheet("font-weight: bold; color: #0066cc;")
    
    def import_tasks(self):
        """Import tasks from CSV file."""
        if not self.csv_file:
            return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.import_button.setEnabled(False)
        
        # Start import worker
        self.import_worker = TaskImportWorker(self.csv_file, self.naming_pattern)
        self.import_worker.progress_updated.connect(self.progress_bar.setValue)
        self.import_worker.status_updated.connect(self.statusBar().showMessage)
        self.import_worker.import_completed.connect(self.on_import_completed)
        self.import_worker.start()
    
    def on_import_completed(self, tasks: List[TaskRecord], errors: List[str]):
        """Handle import completion."""
        self.tasks = tasks
        
        # Hide progress
        self.progress_bar.setVisible(False)
        self.import_button.setEnabled(True)
        
        # Update UI
        self.update_task_preview()
        self.display_errors(errors)

        # Update directory preview
        self.directory_preview.update_preview(tasks)

        # Enable export and save buttons if we have tasks
        has_tasks = len(tasks) > 0
        self.save_to_db_button.setEnabled(has_tasks)
        self.export_json_button.setEnabled(has_tasks)
        
        # Show completion message
        if errors:
            QMessageBox.warning(
                self,
                "Import Completed with Errors",
                f"Imported {len(tasks)} tasks with {len(errors)} errors.\n"
                "Check the error panel for details."
            )
        else:
            QMessageBox.information(
                self,
                "Import Successful",
                f"Successfully imported {len(tasks)} tasks!"
            )
    
    def update_task_preview(self):
        """Update the task preview table."""
        if not self.tasks:
            self.summary_label.setText("No tasks loaded")
            self.csv_preview_table.setRowCount(0)
            self.csv_preview_table.setColumnCount(0)
            return
        
        # Update summary
        task_types = {}
        for task in self.tasks:
            task_types[task.task] = task_types.get(task.task, 0) + 1
        
        summary_parts = [f"{len(self.tasks)} total tasks"]
        for task_type, count in task_types.items():
            summary_parts.append(f"{count} {task_type}")
        
        self.summary_label.setText(" | ".join(summary_parts))
        
        # Update table
        headers = ['Task ID', 'Project', 'Episode', 'Sequence', 'Shot', 'Task', 'Duration (hrs)', 'Frame Range']
        self.csv_preview_table.setColumnCount(len(headers))
        self.csv_preview_table.setHorizontalHeaderLabels(headers)
        self.csv_preview_table.setRowCount(len(self.tasks))

        for row, task in enumerate(self.tasks):
            self.csv_preview_table.setItem(row, 0, QTableWidgetItem(task.task_id))
            self.csv_preview_table.setItem(row, 1, QTableWidgetItem(task.project))
            self.csv_preview_table.setItem(row, 2, QTableWidgetItem(task.episode))
            self.csv_preview_table.setItem(row, 3, QTableWidgetItem(task.sequence))
            self.csv_preview_table.setItem(row, 4, QTableWidgetItem(task.shot))
            self.csv_preview_table.setItem(row, 5, QTableWidgetItem(task.task))
            self.csv_preview_table.setItem(row, 6, QTableWidgetItem(f"{task.estimated_duration_hours:.1f}"))

            frame_range = f"{task.frame_range['start']}-{task.frame_range['end']}"
            self.csv_preview_table.setItem(row, 7, QTableWidgetItem(frame_range))

        self.csv_preview_table.resizeColumnsToContents()
    
    def display_errors(self, errors: List[str]):
        """Display import errors."""
        if errors:
            self.error_text.setPlainText("\n".join(errors))
            self.error_text.setStyleSheet("background-color: #fff5f5; color: #cc0000;")
        else:
            self.error_text.setPlainText("No errors")
            self.error_text.setStyleSheet("background-color: #f5fff5; color: #009900;")
    
    def export_to_json(self):
        """Export tasks to JSON file."""
        if not self.tasks:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Tasks to JSON",
            str(Path.home() / "montu_tasks.json"),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                import json
                
                # Convert tasks to dictionaries
                task_dicts = [task.to_dict() for task in self.tasks]
                
                # Write to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(task_dicts, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Exported {len(self.tasks)} tasks to {file_path}"
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Failed to export tasks: {str(e)}"
                )

    def display_errors(self, errors: List[str]):
        """Display import errors."""
        if errors:
            self.error_text.setPlainText("\n".join(errors))
        else:
            self.error_text.clear()

    def initialize_directory_manager(self):
        """Initialize directory manager with project configuration."""
        try:
            # Get project configuration from database
            project_configs = self.db.find('project_configs', {})
            if project_configs:
                project_config = project_configs[0]  # Use first available project
                self.directory_manager = DirectoryManager(project_config)
                self.directory_preview.set_directory_manager(self.directory_manager)
            else:
                print("No project configuration found for directory manager")
        except Exception as e:
            print(f"Failed to initialize directory manager: {e}")

    def on_directories_created(self, success_count: int, total_count: int):
        """Handle directory creation completion."""
        self.statusBar().showMessage(
            f"Created directories for {success_count}/{total_count} tasks",
            5000
        )

    def on_undo_requested(self):
        """Handle undo operation request."""
        self.statusBar().showMessage("Directory operation undone", 3000)

    def save_to_database(self):
        """Save tasks to the database with optional directory creation."""
        if not self.tasks:
            QMessageBox.warning(self, "No Tasks", "No tasks to save. Please import tasks first.")
            return

        try:
            # Check if auto-create directories is enabled
            auto_create = self.directory_preview.is_auto_create_enabled()

            # Show confirmation dialog
            message = f"Save {len(self.tasks)} tasks to the database?"
            if auto_create:
                message += "\n\nDirectories will be automatically created for all tasks."

            reply = QMessageBox.question(
                self,
                "Save to Database",
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply != QMessageBox.Yes:
                return

            # Save tasks to database
            saved_count = 0
            failed_count = 0

            for task in self.tasks:
                try:
                    # Convert TaskRecord to dictionary
                    task_dict = task.to_dict()

                    # Check if task already exists
                    existing_task = self.db.find_one('tasks', {'_id': task_dict['_id']})

                    if existing_task:
                        # Update existing task
                        result = self.db.update_one(
                            'tasks',
                            {'_id': task_dict['_id']},
                            {'$set': task_dict}
                        )
                    else:
                        # Insert new task
                        result = self.db.insert_one('tasks', task_dict)

                    if result:
                        saved_count += 1
                    else:
                        failed_count += 1

                except Exception as e:
                    print(f"Error saving task {task.task_id}: {e}")
                    failed_count += 1

            # Create directories if auto-create is enabled
            if auto_create and self.directory_manager and saved_count > 0:
                try:
                    dir_success, dir_total, dir_errors = self.directory_manager.create_directories_for_tasks(self.tasks)
                    if dir_errors:
                        print(f"Directory creation errors: {dir_errors}")
                except Exception as e:
                    print(f"Error creating directories: {e}")

            # Show results
            if failed_count == 0:
                message = f"Successfully saved {saved_count} tasks to the database!"
                if auto_create:
                    message += "\nDirectories have been created."
                QMessageBox.information(self, "Save Successful", message)
                self.statusBar().showMessage(f"Saved {saved_count} tasks to database", 5000)
            else:
                QMessageBox.warning(
                    self,
                    "Save Completed with Errors",
                    f"Saved {saved_count} tasks successfully.\n"
                    f"{failed_count} tasks failed to save."
                )
                self.statusBar().showMessage(f"Saved {saved_count} tasks, {failed_count} failed", 5000)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save tasks to database:\n{str(e)}")
