"""
Directory Preview Widget

Widget for displaying directory structure preview and managing
directory creation operations in the Task Creator.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QPushButton, QGroupBox, QTextEdit, QProgressBar,
    QMessageBox, QSplitter, QCheckBox, QFrame, QTreeWidgetItemIterator
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont, QIcon, QColor, QBrush, QPalette

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from ..directory_manager import DirectoryManager, DirectoryPreview


class CollapsibleGroupBox(QGroupBox):
    """A collapsible group box widget."""

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.setCheckable(True)
        self.setChecked(False)  # Start collapsed
        self.toggled.connect(self.on_toggled)

        # Create content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.content_widget)

        # Initially hide content
        self.content_widget.setVisible(False)

    def on_toggled(self, checked: bool):
        """Handle toggle state change."""
        self.content_widget.setVisible(checked)

    def addWidget(self, widget):
        """Add widget to the collapsible content."""
        self.content_layout.addWidget(widget)

    def addLayout(self, layout):
        """Add layout to the collapsible content."""
        self.content_layout.addLayout(layout)


class TaskTreeItem(QTreeWidgetItem):
    """Custom tree item for task representation with selection state."""

    def __init__(self, parent, task_info: 'TaskDirectoryInfo'):
        super().__init__(parent)
        self.task_info = task_info
        self.checkbox = None
        self.setup_item()

    def setup_item(self):
        """Set up the tree item with task information."""
        # Set task ID as the main text
        self.setText(0, self.task_info.task.task_id)

        # Set task type information
        task_type = f"{self.task_info.task.task} ({self.task_info.task.type})"
        self.setText(1, task_type)

        # Set selection status
        self.update_selection_display()

        # Set existence status
        self.update_existence_display()

    def update_selection_display(self):
        """Update the visual display of selection state."""
        if self.task_info.selected:
            self.setIcon(0, self.get_icon("✓", QColor(0, 150, 0)))
            self.setText(2, "Selected")
        else:
            self.setIcon(0, self.get_icon("○", QColor(150, 150, 150)))
            self.setText(2, "Not Selected")

    def update_existence_display(self):
        """Update the visual display of directory existence."""
        if self.task_info.has_existing_directories:
            existing_count = self.task_info.existing_count
            total_count = len(self.task_info.directories_exist)
            self.setText(3, f"{existing_count}/{total_count} exist")
            self.setBackground(3, QBrush(QColor(255, 165, 0, 100)))  # Orange
        else:
            self.setText(3, "All new")
            self.setBackground(3, QBrush(QColor(144, 238, 144, 100)))  # Light green

    def get_icon(self, text: str, color: QColor):
        """Create a simple text-based icon."""
        # For now, we'll use text. In a full implementation, you'd create actual icons
        return QIcon()  # Placeholder

    def toggle_selection(self):
        """Toggle the selection state of this task."""
        self.task_info.selected = not self.task_info.selected
        self.update_selection_display()


class DirectoryTreeItem(QTreeWidgetItem):
    """Custom tree item for directory representation."""

    def __init__(self, parent, directory_path: str, directory_type: str, exists: bool):
        super().__init__(parent)
        self.directory_path = directory_path
        self.directory_type = directory_type
        self.exists = exists
        self.setup_item()

    def setup_item(self):
        """Set up the directory item."""
        # Show directory name (last part of path)
        dir_name = Path(self.directory_path).name or self.directory_path
        self.setText(0, dir_name)
        self.setText(1, self.directory_type.title())

        # Set full path as tooltip
        self.setToolTip(0, self.directory_path)
        self.setToolTip(1, self.directory_path)

        # Set existence status and color
        if self.exists:
            self.setText(2, "Exists")
            self.setBackground(0, QBrush(QColor(255, 165, 0, 100)))  # Orange
            self.setIcon(0, self.get_icon("📁", QColor(255, 140, 0)))
        else:
            self.setText(2, "New")
            self.setBackground(0, QBrush(QColor(144, 238, 144, 100)))  # Light green
            self.setIcon(0, self.get_icon("📂", QColor(0, 150, 0)))

    def get_icon(self, text: str, color: QColor):
        """Create a simple text-based icon."""
        return QIcon()  # Placeholder


class TaskDirectoryInfo:
    """Information about a task's directory structure and selection state."""

    def __init__(self, task, preview: DirectoryPreview):
        self.task = task
        self.preview = preview
        self.selected = True  # Default to selected
        self.directories_exist = {}  # Dict of directory_type -> exists (bool)
        self.check_directory_existence()

    def check_directory_existence(self):
        """Check if directories already exist on the file system."""
        directories = {
            'working': self.preview.working_dir,
            'render': self.preview.render_dir,
            'media': self.preview.media_dir,
            'cache': self.preview.cache_dir
        }

        for dir_type, dir_path in directories.items():
            self.directories_exist[dir_type] = Path(dir_path).exists()

    @property
    def has_existing_directories(self) -> bool:
        """Check if any directories already exist."""
        return any(self.directories_exist.values())

    @property
    def existing_count(self) -> int:
        """Count of existing directories."""
        return sum(1 for exists in self.directories_exist.values() if exists)


class DirectoryCreationWorker(QThread):
    """Worker thread for directory creation operations."""

    progress_updated = Signal(int)
    status_updated = Signal(str)
    creation_completed = Signal(int, int, list)  # success_count, total_count, errors

    def __init__(self, directory_manager: DirectoryManager, selected_tasks: List[Any]):
        super().__init__()
        self.directory_manager = directory_manager
        self.selected_tasks = selected_tasks

    def run(self):
        """Run directory creation process for selected tasks only."""
        try:
            self.status_updated.emit(f"Creating directories for {len(self.selected_tasks)} selected tasks...")
            self.progress_updated.emit(20)

            success_count, total_count, errors = self.directory_manager.create_directories_for_tasks(self.selected_tasks)

            self.progress_updated.emit(100)
            self.status_updated.emit(f"Directory creation completed: {success_count}/{total_count} successful")
            self.creation_completed.emit(success_count, total_count, errors)

        except Exception as e:
            self.status_updated.emit(f"Directory creation failed: {str(e)}")
            self.creation_completed.emit(0, len(self.selected_tasks), [str(e)])


class DirectoryPreviewWidget(QWidget):
    """
    Widget for previewing and managing directory creation operations.
    
    Shows directory structure preview, estimated disk usage,
    and provides controls for directory creation and undo operations.
    """
    
    # Signals
    directories_created = Signal(int, int)  # success_count, total_count
    undo_requested = Signal()
    
    def __init__(self, parent=None):
        """Initialize directory preview widget."""
        super().__init__(parent)

        # State
        self.directory_manager: Optional[DirectoryManager] = None
        self.current_tasks: List[Any] = []
        self.current_previews: List[DirectoryPreview] = []
        self.task_directory_info: List[TaskDirectoryInfo] = []  # Enhanced task info with selection state

        # Setup UI
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Directory Preview")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Auto-create checkbox
        self.auto_create_checkbox = QCheckBox("Auto-create directories on import")
        self.auto_create_checkbox.setChecked(True)
        header_layout.addWidget(self.auto_create_checkbox)
        
        layout.addLayout(header_layout)

        # Selection controls
        selection_layout = QHBoxLayout()

        self.select_all_button = QPushButton("Select All")
        self.select_all_button.setMaximumWidth(100)
        selection_layout.addWidget(self.select_all_button)

        self.deselect_all_button = QPushButton("Deselect All")
        self.deselect_all_button.setMaximumWidth(100)
        selection_layout.addWidget(self.deselect_all_button)

        selection_layout.addStretch()

        # Existence warning label
        self.existence_warning = QLabel("")
        self.existence_warning.setStyleSheet("color: #ff6600; font-weight: bold;")
        self.existence_warning.setVisible(False)
        selection_layout.addWidget(self.existence_warning)

        layout.addLayout(selection_layout)

        # Directory tree section (main area - takes most space)
        tree_group = QGroupBox("Directory Structure & Selection")
        tree_layout = QVBoxLayout(tree_group)

        # Create hierarchical tree widget
        self.directory_tree = QTreeWidget()
        self.directory_tree.setHeaderLabels([
            "Path/Name", "Type", "Selection", "Status"
        ])
        self.directory_tree.setAlternatingRowColors(True)
        self.directory_tree.setRootIsDecorated(True)
        self.directory_tree.setExpandsOnDoubleClick(True)
        self.directory_tree.setItemsExpandable(True)

        # Set column widths for better display
        self.directory_tree.setColumnWidth(0, 300)  # Path/Name
        self.directory_tree.setColumnWidth(1, 100)  # Type
        self.directory_tree.setColumnWidth(2, 100)  # Selection
        self.directory_tree.setColumnWidth(3, 100)  # Status

        # Enable item interaction
        self.directory_tree.itemClicked.connect(self.on_tree_item_clicked)
        self.directory_tree.itemDoubleClicked.connect(self.on_tree_item_double_clicked)

        tree_layout.addWidget(self.directory_tree)

        # Directory statistics
        self.stats_label = QLabel("No directories to preview")
        self.stats_label.setStyleSheet("color: #666666; font-style: italic;")
        tree_layout.addWidget(self.stats_label)

        layout.addWidget(tree_group)

        # Compact directory operations section (bottom)
        operations_group = QGroupBox("Directory Operations")
        operations_layout = QVBoxLayout(operations_group)
        operations_group.setMaximumHeight(120)  # Limit height for more tree space

        # Main operations in horizontal layout
        main_ops_layout = QHBoxLayout()

        # Create directories button
        self.create_dirs_button = QPushButton("Create Directories")
        self.create_dirs_button.setEnabled(False)
        self.create_dirs_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-radius: 4px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        main_ops_layout.addWidget(self.create_dirs_button)

        # Undo button (compact)
        self.undo_button = QPushButton("Undo Last")
        self.undo_button.setEnabled(False)
        self.undo_button.setMaximumWidth(100)
        self.undo_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        main_ops_layout.addWidget(self.undo_button)

        operations_layout.addLayout(main_ops_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(20)
        operations_layout.addWidget(self.progress_bar)

        layout.addWidget(operations_group)

        # Collapsible undo history section
        self.undo_history_group = CollapsibleGroupBox("Undo History (Click to expand)")

        self.undo_history = QTextEdit()
        self.undo_history.setMaximumHeight(80)
        self.undo_history.setPlaceholderText("No operations to undo...")
        self.undo_history_group.addWidget(self.undo_history)

        layout.addWidget(self.undo_history_group)
    
    def setup_connections(self):
        """Set up signal connections."""
        self.create_dirs_button.clicked.connect(self.create_directories)
        self.undo_button.clicked.connect(self.undo_last_operation)
        self.select_all_button.clicked.connect(self.select_all_tasks)
        self.deselect_all_button.clicked.connect(self.deselect_all_tasks)

    def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle tree item click events."""
        if isinstance(item, TaskTreeItem):
            # Toggle task selection on click
            item.toggle_selection()
            self.update_statistics()
            self.update_create_button_state()

    def on_tree_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle tree item double-click events."""
        if isinstance(item, TaskTreeItem):
            # Double-click to expand/collapse task directories
            item.setExpanded(not item.isExpanded())
    
    def set_directory_manager(self, directory_manager: DirectoryManager):
        """Set the directory manager instance."""
        self.directory_manager = directory_manager
        self.update_undo_history()
    
    def update_preview(self, tasks: List[Any]):
        """Update the directory preview with new tasks and check directory existence."""
        self.current_tasks = tasks

        if not self.directory_manager or not tasks:
            self.clear_preview()
            return

        try:
            # Generate previews
            self.current_previews = self.directory_manager.generate_directory_preview(tasks)

            # Create enhanced task directory info with existence checking
            self.task_directory_info = []
            for task, preview in zip(tasks, self.current_previews):
                task_info = TaskDirectoryInfo(task, preview)
                self.task_directory_info.append(task_info)

            # Update tree
            self.update_directory_tree()

            # Update statistics
            self.update_statistics()

            # Check for existing directories and show warning
            self.check_and_show_existence_warning()

            # Enable create button
            self.create_dirs_button.setEnabled(len(self.current_previews) > 0)

        except Exception as e:
            QMessageBox.warning(self, "Preview Error", f"Failed to generate directory preview: {e}")
            self.clear_preview()
    
    def update_directory_tree(self):
        """Update the directory tree with hierarchical task and directory structure."""
        self.directory_tree.clear()

        if not self.task_directory_info:
            return

        # Build hierarchical structure: Project -> Episode -> Sequence -> Shot -> Task -> Directories
        project_items = {}

        for task_info in self.task_directory_info:
            task = task_info.task

            # Get or create project item
            project_key = task.project
            if project_key not in project_items:
                project_item = QTreeWidgetItem(self.directory_tree)
                project_item.setText(0, f"Project: {task.project}")
                project_item.setText(1, "Project")
                project_item.setExpanded(True)
                project_items[project_key] = {'item': project_item, 'episodes': {}}

            project_data = project_items[project_key]

            # Get or create episode item
            episode_key = task.episode
            if episode_key not in project_data['episodes']:
                episode_item = QTreeWidgetItem(project_data['item'])
                episode_item.setText(0, f"Episode: {task.episode}")
                episode_item.setText(1, "Episode")
                episode_item.setExpanded(True)
                project_data['episodes'][episode_key] = {'item': episode_item, 'sequences': {}}

            episode_data = project_data['episodes'][episode_key]

            # Get or create sequence item
            sequence_key = task.sequence
            if sequence_key not in episode_data['sequences']:
                sequence_item = QTreeWidgetItem(episode_data['item'])
                sequence_item.setText(0, f"Sequence: {task.sequence}")
                sequence_item.setText(1, "Sequence")
                sequence_item.setExpanded(True)
                episode_data['sequences'][sequence_key] = {'item': sequence_item, 'shots': {}}

            sequence_data = episode_data['sequences'][sequence_key]

            # Get or create shot item
            shot_key = task.shot
            if shot_key not in sequence_data['shots']:
                shot_item = QTreeWidgetItem(sequence_data['item'])
                shot_item.setText(0, f"Shot: {task.shot}")
                shot_item.setText(1, "Shot")
                shot_item.setExpanded(True)
                sequence_data['shots'][shot_key] = {'item': shot_item, 'tasks': {}}

            shot_data = sequence_data['shots'][shot_key]

            # Create task item
            task_item = TaskTreeItem(shot_data['item'], task_info)
            task_item.setExpanded(True)

            # Add directory items under task
            directories = [
                ('working', task_info.preview.working_dir, task_info.directories_exist.get('working', False)),
                ('render', task_info.preview.render_dir, task_info.directories_exist.get('render', False)),
                ('media', task_info.preview.media_dir, task_info.directories_exist.get('media', False)),
                ('cache', task_info.preview.cache_dir, task_info.directories_exist.get('cache', False))
            ]

            for dir_type, dir_path, exists in directories:
                dir_item = DirectoryTreeItem(task_item, dir_path, dir_type, exists)

        # Expand all items by default for better visibility
        self.directory_tree.expandAll()

    def select_all_tasks(self):
        """Select all tasks for directory creation."""
        for task_info in self.task_directory_info:
            task_info.selected = True
        self.refresh_tree_selection_display()
        self.update_statistics()
        self.update_create_button_state()

    def deselect_all_tasks(self):
        """Deselect all tasks for directory creation."""
        for task_info in self.task_directory_info:
            task_info.selected = False
        self.refresh_tree_selection_display()
        self.update_statistics()
        self.update_create_button_state()

    def refresh_tree_selection_display(self):
        """Refresh the selection display in the tree."""
        # Find all TaskTreeItem instances and update their display
        iterator = QTreeWidgetItemIterator(self.directory_tree)
        while iterator.value():
            item = iterator.value()
            if isinstance(item, TaskTreeItem):
                item.update_selection_display()
            iterator += 1

    def update_create_button_state(self):
        """Update the create directories button state based on selection."""
        selected_count = sum(1 for task_info in self.task_directory_info if task_info.selected)
        self.create_dirs_button.setEnabled(selected_count > 0)

        if selected_count > 0:
            self.create_dirs_button.setText(f"Create Directories ({selected_count} selected)")
        else:
            self.create_dirs_button.setText("Create Directories")

    def check_and_show_existence_warning(self):
        """Check for existing directories and show warning if needed."""
        existing_tasks = [task_info for task_info in self.task_directory_info if task_info.has_existing_directories]

        if existing_tasks:
            total_existing = sum(task_info.existing_count for task_info in existing_tasks)
            self.existence_warning.setText(
                f"⚠️ {len(existing_tasks)} tasks have {total_existing} existing directories"
            )
            self.existence_warning.setVisible(True)
        else:
            self.existence_warning.setVisible(False)

    def update_statistics(self):
        """Update directory statistics display with selection and existence info."""
        if not self.task_directory_info:
            self.stats_label.setText("No directories to preview")
            return

        total_tasks = len(self.task_directory_info)
        selected_tasks = sum(1 for task_info in self.task_directory_info if task_info.selected)
        existing_dirs = sum(task_info.existing_count for task_info in self.task_directory_info)
        total_dirs = selected_tasks * 4  # 4 dirs per selected task
        new_dirs = total_dirs - sum(task_info.existing_count for task_info in self.task_directory_info if task_info.selected)

        total_size = sum(preview.estimated_size_mb for preview in self.current_previews)

        self.stats_label.setText(
            f"Tasks: {selected_tasks}/{total_tasks} selected | "
            f"New Directories: {new_dirs} | "
            f"Existing: {existing_dirs} | "
            f"Estimated Size: {total_size:.1f} MB"
        )
    
    def clear_preview(self):
        """Clear the preview display."""
        self.directory_tree.clear()
        self.current_previews = []
        self.current_tasks = []
        self.task_directory_info = []
        self.stats_label.setText("No directories to preview")
        self.create_dirs_button.setEnabled(False)
        self.create_dirs_button.setText("Create Directories")
        self.existence_warning.setVisible(False)
    
    def create_directories(self):
        """Create directories for selected tasks only."""
        if not self.directory_manager or not self.task_directory_info:
            return

        # Get selected tasks
        selected_tasks = [task_info.task for task_info in self.task_directory_info if task_info.selected]

        if not selected_tasks:
            QMessageBox.information(self, "No Selection", "Please select at least one task for directory creation.")
            return

        # Check for existing directories in selected tasks
        selected_with_existing = [task_info for task_info in self.task_directory_info
                                 if task_info.selected and task_info.has_existing_directories]

        # Build confirmation message
        message = f"Create directories for {len(selected_tasks)} selected tasks?\n\n"
        message += f"This will create approximately {len(selected_tasks) * 4} directories."

        if selected_with_existing:
            existing_count = sum(task_info.existing_count for task_info in selected_with_existing)
            message += f"\n\n⚠️ Warning: {len(selected_with_existing)} tasks have {existing_count} existing directories."
            message += "\nExisting directories will be skipped."

        # Confirm with user
        reply = QMessageBox.question(
            self,
            "Create Directories",
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if reply != QMessageBox.Yes:
            return

        # Show progress and start worker
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.create_dirs_button.setEnabled(False)

        self.creation_worker = DirectoryCreationWorker(self.directory_manager, selected_tasks)
        self.creation_worker.progress_updated.connect(self.progress_bar.setValue)
        self.creation_worker.creation_completed.connect(self.on_creation_completed)
        self.creation_worker.start()
    
    def on_creation_completed(self, success_count: int, total_count: int, errors: List[str]):
        """Handle directory creation completion."""
        # Hide progress
        self.progress_bar.setVisible(False)
        self.create_dirs_button.setEnabled(True)

        # Refresh directory existence status
        for task_info in self.task_directory_info:
            task_info.check_directory_existence()

        # Update display
        self.update_directory_tree()
        self.update_statistics()
        self.check_and_show_existence_warning()
        self.update_create_button_state()

        # Update undo history
        self.update_undo_history()

        # Emit signal
        self.directories_created.emit(success_count, total_count)

        # Show results
        if errors:
            QMessageBox.warning(
                self,
                "Directory Creation Completed with Errors",
                f"Created directories for {success_count}/{total_count} selected tasks.\n\n"
                f"Errors:\n" + "\n".join(errors[:5])  # Show first 5 errors
            )
        else:
            QMessageBox.information(
                self,
                "Directory Creation Successful",
                f"Successfully created directories for {success_count} selected tasks!"
            )
    
    def update_undo_history(self):
        """Update the undo history display."""
        if not self.directory_manager:
            return
        
        try:
            operations = self.directory_manager.get_undo_operations(5)
            
            if operations:
                history_text = "Recent Operations:\n\n"
                for i, op in enumerate(operations):
                    timestamp = op['timestamp'][:19].replace('T', ' ')  # Format timestamp
                    history_text += f"{i+1}. {timestamp}\n"
                    history_text += f"   Tasks: {op['task_count']}, Dirs: {op['directories_created']}\n"
                    history_text += f"   Can undo: {'Yes' if op['can_undo'] else 'No'}\n\n"
                
                self.undo_history.setPlainText(history_text)
                self.undo_button.setEnabled(operations[0]['can_undo'] if operations else False)
            else:
                self.undo_history.setPlainText("No operations to undo...")
                self.undo_button.setEnabled(False)
                
        except Exception as e:
            print(f"Error updating undo history: {e}")
    
    def undo_last_operation(self):
        """Undo the last directory creation operation."""
        if not self.directory_manager:
            return
        
        # Confirm with user
        reply = QMessageBox.question(
            self,
            "Undo Directory Creation",
            "Undo the last directory creation operation?\n\n"
            "This will remove empty directories that were created.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            success, message, dirs_removed = self.directory_manager.undo_last_operation()
            
            if success:
                QMessageBox.information(self, "Undo Successful", message)
                self.update_undo_history()
                self.undo_requested.emit()
            else:
                QMessageBox.warning(self, "Undo Failed", message)
                
        except Exception as e:
            QMessageBox.critical(self, "Undo Error", f"Failed to undo operation: {e}")
    
    def is_auto_create_enabled(self) -> bool:
        """Check if auto-create directories is enabled."""
        return self.auto_create_checkbox.isChecked()
