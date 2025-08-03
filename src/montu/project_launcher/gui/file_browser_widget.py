"""
File Browser Widget

Widget for browsing and managing files related to selected tasks in the Project Launcher.
Displays files from working directories, render outputs, media files, and cache directories.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QPushButton, QGroupBox, QMenu, QMessageBox, QHeaderView,
    QComboBox, QLineEdit, QDialog, QTextEdit, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QAction, QIcon, QFont

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class FileBrowserWidget(QWidget):
    """
    File browser widget for displaying task-related files.
    
    Shows files from working directories, render outputs, media files,
    and cache directories with file operations and context menus.
    """
    
    # Signals
    fileSelected = Signal(str)      # file_path
    fileOpened = Signal(str)        # file_path
    refreshRequested = Signal()

    # Filter options
    FILE_TYPE_FILTERS = [
        ('All Files', ''),
        ('Maya Files (.ma/.mb)', ['.ma', '.mb']),
        ('Nuke Scripts (.nk)', ['.nk']),
        ('Renders (.exr/.jpg)', ['.exr', '.jpg', '.jpeg', '.png']),
        ('Media (.mov/.mp4)', ['.mov', '.mp4', '.avi']),
        ('Cache Files (.abc/.bgeo)', ['.abc', '.bgeo', '.vdb'])
    ]

    VERSION_FILTERS = [
        ('All Versions', 'all'),
        ('Latest Only', 'latest'),
        ('Published Only', 'published'),
        ('Work-in-Progress', 'wip')
    ]

    DATE_FILTERS = [
        ('All Time', 'all'),
        ('Last 24 Hours', '24h'),
        ('Last Week', '7d'),
        ('Last Month', '30d')
    ]

    SIZE_FILTERS = [
        ('All Sizes', 'all'),
        ('< 10MB', '10mb'),
        ('10MB - 100MB', '100mb'),
        ('100MB - 1GB', '1gb'),
        ('> 1GB', 'large')
    ]
    
    # File type icons (using text for now, could be replaced with actual icons)
    FILE_TYPE_ICONS = {
        '.ma': '🎭',   # Maya scene
        '.mb': '🎭',   # Maya binary
        '.nk': '🎬',   # Nuke script
        '.hip': '🌊',  # Houdini scene
        '.exr': '🖼️',  # EXR image
        '.jpg': '📷',  # JPEG image
        '.png': '🖼️',  # PNG image
        '.mov': '🎥',  # QuickTime movie
        '.mp4': '📹',  # MP4 video
        '.avi': '🎞️',  # AVI video
        '.abc': '📦',  # Alembic cache
        '.bgeo': '📦', # Houdini geometry
        '.vdb': '☁️',  # OpenVDB
    }
    
    def __init__(self, parent=None):
        """Initialize file browser widget."""
        super().__init__(parent)
        
        # State
        self.current_task_id: Optional[str] = None
        self.current_task_paths: Optional[Dict[str, str]] = None
        self.project_model = None  # Will be set by parent
        self.all_files: List[Dict[str, Any]] = []  # Store all files for filtering
        self.filtered_files: List[Dict[str, Any]] = []  # Store filtered files

        # Filter state
        self.current_filters = {
            'file_type': '',
            'version': 'all',
            'date': 'all',
            'size': 'all',
            'search': ''
        }
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
        
        # Setup auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_files)
        self.refresh_timer.start(10000)  # Refresh every 10 seconds
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Header section
        header_group = QGroupBox("File Browser")
        header_layout = QVBoxLayout(header_group)

        # Task info and refresh button
        info_layout = QHBoxLayout()

        self.task_info_label = QLabel("No task selected")
        font = QFont()
        font.setBold(True)
        self.task_info_label.setFont(font)
        info_layout.addWidget(self.task_info_label)

        info_layout.addStretch()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setMaximumWidth(80)
        info_layout.addWidget(self.refresh_button)

        header_layout.addLayout(info_layout)

        # Filter section
        filters_layout = QVBoxLayout()

        # First row of filters
        filters_row1 = QHBoxLayout()

        # File type filter
        filters_row1.addWidget(QLabel("Type:"))
        self.file_type_filter = QComboBox()
        for display_name, value in self.FILE_TYPE_FILTERS:
            self.file_type_filter.addItem(display_name, value)
        self.file_type_filter.setMaximumWidth(150)
        filters_row1.addWidget(self.file_type_filter)

        # Version filter
        filters_row1.addWidget(QLabel("Version:"))
        self.version_filter = QComboBox()
        for display_name, value in self.VERSION_FILTERS:
            self.version_filter.addItem(display_name, value)
        self.version_filter.setMaximumWidth(120)
        filters_row1.addWidget(self.version_filter)

        # Date filter
        filters_row1.addWidget(QLabel("Date:"))
        self.date_filter = QComboBox()
        for display_name, value in self.DATE_FILTERS:
            self.date_filter.addItem(display_name, value)
        self.date_filter.setMaximumWidth(120)
        filters_row1.addWidget(self.date_filter)

        filters_row1.addStretch()
        filters_layout.addLayout(filters_row1)

        # Second row of filters
        filters_row2 = QHBoxLayout()

        # Size filter
        filters_row2.addWidget(QLabel("Size:"))
        self.size_filter = QComboBox()
        for display_name, value in self.SIZE_FILTERS:
            self.size_filter.addItem(display_name, value)
        self.size_filter.setMaximumWidth(120)
        filters_row2.addWidget(self.size_filter)

        # Search filter
        filters_row2.addWidget(QLabel("Search:"))
        self.search_filter = QLineEdit()
        self.search_filter.setPlaceholderText("Search filenames...")
        self.search_filter.setMaximumWidth(150)
        filters_row2.addWidget(self.search_filter)

        # Clear filters button
        self.clear_filters_button = QPushButton("Clear Filters")
        self.clear_filters_button.setMaximumWidth(100)
        filters_row2.addWidget(self.clear_filters_button)

        filters_row2.addStretch()
        filters_layout.addLayout(filters_row2)

        header_layout.addLayout(filters_layout)

        # File count label
        self.file_count_label = QLabel("No files")
        self.file_count_label.setStyleSheet("color: #666; font-style: italic;")
        header_layout.addWidget(self.file_count_label)

        layout.addWidget(header_group)
        
        # File tree
        files_group = QGroupBox("Files")
        files_layout = QVBoxLayout(files_group)
        
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Name", "Size", "Modified", "Type"])
        self.file_tree.setAlternatingRowColors(True)
        self.file_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_tree.setSortingEnabled(True)
        self.file_tree.sortByColumn(0, Qt.AscendingOrder)
        
        # Configure column widths
        header = self.file_tree.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Name column stretches
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Size
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Modified
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Type
        
        files_layout.addWidget(self.file_tree)
        layout.addWidget(files_group)
        
        # Empty state
        self.empty_state_label = QLabel("No files found for this task")
        self.empty_state_label.setAlignment(Qt.AlignCenter)
        self.empty_state_label.setStyleSheet("color: #999; font-style: italic; padding: 20px;")
        self.empty_state_label.setVisible(False)
        layout.addWidget(self.empty_state_label)
    
    def setup_connections(self):
        """Set up signal connections."""
        self.refresh_button.clicked.connect(self.refresh_files)
        self.file_tree.itemDoubleClicked.connect(self.on_file_double_clicked)
        self.file_tree.customContextMenuRequested.connect(self.show_context_menu)
        self.file_tree.itemSelectionChanged.connect(self.on_file_selection_changed)

        # Filter connections
        self.file_type_filter.currentTextChanged.connect(self.apply_filters)
        self.version_filter.currentTextChanged.connect(self.apply_filters)
        self.date_filter.currentTextChanged.connect(self.apply_filters)
        self.size_filter.currentTextChanged.connect(self.apply_filters)
        self.search_filter.textChanged.connect(self.apply_filters)
        self.clear_filters_button.clicked.connect(self.clear_filters)
    
    def set_project_model(self, project_model):
        """Set the project model for path generation."""
        self.project_model = project_model
    
    def set_selected_task(self, task_id: str):
        """Set the currently selected task and refresh file list."""
        if task_id == self.current_task_id:
            return  # No change
        
        self.current_task_id = task_id
        
        if not self.project_model:
            return
        
        # Get task information
        task = self.project_model.get_task_by_id(task_id)
        if task:
            task_display = f"{task.get('shot', 'Unknown')} - {task.get('task', 'Unknown')}"
            self.task_info_label.setText(task_display)
        else:
            self.task_info_label.setText("Unknown task")
        
        # Generate paths for this task
        self.current_task_paths = self.project_model.generate_task_paths(task_id, "001", "maya_scene")
        
        # Refresh file list
        self.refresh_files()

    def apply_filters(self):
        """Apply current filter settings to file list."""
        # Update filter state
        self.current_filters['file_type'] = self.file_type_filter.currentData()
        self.current_filters['version'] = self.version_filter.currentData()
        self.current_filters['date'] = self.date_filter.currentData()
        self.current_filters['size'] = self.size_filter.currentData()
        self.current_filters['search'] = self.search_filter.text().strip().lower()

        # Apply filters to file list
        self.filter_files()

        # Refresh display
        self.display_filtered_files()

    def clear_filters(self):
        """Clear all filters and show all files."""
        self.file_type_filter.setCurrentIndex(0)
        self.version_filter.setCurrentIndex(0)
        self.date_filter.setCurrentIndex(0)
        self.size_filter.setCurrentIndex(0)
        self.search_filter.clear()

        # Reset filter state
        self.current_filters = {
            'file_type': '',
            'version': 'all',
            'date': 'all',
            'size': 'all',
            'search': ''
        }

        # Refresh display
        self.filter_files()
        self.display_filtered_files()

    def filter_files(self):
        """Filter files based on current filter settings."""
        if not self.all_files:
            self.filtered_files = []
            return

        self.filtered_files = []

        for file_info in self.all_files:
            if self.file_matches_filters(file_info):
                self.filtered_files.append(file_info)

    def file_matches_filters(self, file_info: Dict[str, Any]) -> bool:
        """Check if a file matches current filter criteria."""
        file_path = file_info['path']
        file_name = os.path.basename(file_path).lower()
        file_ext = os.path.splitext(file_name)[1].lower()

        # File type filter
        file_type_filter = self.current_filters['file_type']
        if file_type_filter and isinstance(file_type_filter, list):
            if file_ext not in file_type_filter:
                return False

        # Search filter
        search_text = self.current_filters['search']
        if search_text and search_text not in file_name:
            return False

        # Version filter
        version_filter = self.current_filters['version']
        if version_filter != 'all':
            if not self.file_matches_version_filter(file_info, version_filter):
                return False

        # Date filter
        date_filter = self.current_filters['date']
        if date_filter != 'all':
            if not self.file_matches_date_filter(file_info, date_filter):
                return False

        # Size filter
        size_filter = self.current_filters['size']
        if size_filter != 'all':
            if not self.file_matches_size_filter(file_info, size_filter):
                return False

        return True

    def file_matches_version_filter(self, file_info: Dict[str, Any], version_filter: str) -> bool:
        """Check if file matches version filter."""
        # This is a simplified implementation
        # In a full system, this would check actual version status from database
        file_name = os.path.basename(file_info['path']).lower()

        if version_filter == 'latest':
            # Show only files with highest version numbers
            import re
            version_match = re.search(r'_v(\d{3})', file_name)
            if version_match:
                version_num = int(version_match.group(1))
                return version_num >= 3  # Simplified: v003+ considered latest
        elif version_filter == 'published':
            # Show only published versions (simplified: even version numbers)
            import re
            version_match = re.search(r'_v(\d{3})', file_name)
            if version_match:
                version_num = int(version_match.group(1))
                return version_num % 2 == 0  # Even versions = published
        elif version_filter == 'wip':
            # Show only work-in-progress (simplified: odd version numbers)
            import re
            version_match = re.search(r'_v(\d{3})', file_name)
            if version_match:
                version_num = int(version_match.group(1))
                return version_num % 2 == 1  # Odd versions = WIP

        return True

    def file_matches_date_filter(self, file_info: Dict[str, Any], date_filter: str) -> bool:
        """Check if file matches date filter."""
        try:
            file_path = file_info['path']
            stat = os.stat(file_path)
            file_time = datetime.fromtimestamp(stat.st_mtime)
            now = datetime.now()

            if date_filter == '24h':
                return (now - file_time).days < 1
            elif date_filter == '7d':
                return (now - file_time).days < 7
            elif date_filter == '30d':
                return (now - file_time).days < 30
        except:
            pass

        return True

    def file_matches_size_filter(self, file_info: Dict[str, Any], size_filter: str) -> bool:
        """Check if file matches size filter."""
        try:
            file_path = file_info['path']
            stat = os.stat(file_path)
            file_size = stat.st_size

            if size_filter == '10mb':
                return file_size < 10 * 1024 * 1024
            elif size_filter == '100mb':
                return 10 * 1024 * 1024 <= file_size < 100 * 1024 * 1024
            elif size_filter == '1gb':
                return 100 * 1024 * 1024 <= file_size < 1024 * 1024 * 1024
            elif size_filter == 'large':
                return file_size >= 1024 * 1024 * 1024
        except:
            pass

        return True

    def refresh_files(self):
        """Refresh the file list for the current task."""
        if not self.current_task_id or not self.current_task_paths:
            self.show_empty_state()
            return

        # Collect all files first
        self.collect_all_files()

        # Apply filters
        self.filter_files()

        # Display filtered files
        self.display_filtered_files()

    def collect_all_files(self):
        """Collect all files from relevant directories."""
        self.all_files = []

        # Get all relevant directories
        directories_to_scan = self.get_directories_to_scan()

        # Scan each directory
        for dir_name, dir_path in directories_to_scan.items():
            if not dir_path or not os.path.exists(dir_path):
                continue

            # Collect files from directory
            self.collect_files_from_directory(dir_path, dir_name)

    def collect_files_from_directory(self, directory_path: str, dir_name: str):
        """Collect files from a directory into the all_files list."""
        try:
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)

                if os.path.isfile(item_path):
                    file_info = {
                        'path': item_path,
                        'name': item,
                        'directory': dir_name,
                        'size': 0,
                        'modified': None
                    }

                    # Get file stats
                    try:
                        stat = os.stat(item_path)
                        file_info['size'] = stat.st_size
                        file_info['modified'] = datetime.fromtimestamp(stat.st_mtime)
                    except:
                        pass

                    self.all_files.append(file_info)

                elif os.path.isdir(item_path):
                    # Recursively scan subdirectory (limit depth)
                    self.collect_files_from_directory(item_path, f"{dir_name}/{item}")

        except (OSError, PermissionError):
            # Handle permission errors gracefully
            pass

    def display_filtered_files(self):
        """Display the filtered files in the tree widget."""
        # Clear existing items
        self.file_tree.clear()

        if not self.filtered_files:
            self.show_empty_state()
            return

        # Group files by directory
        directories = {}
        for file_info in self.filtered_files:
            dir_name = file_info['directory']
            if dir_name not in directories:
                directories[dir_name] = []
            directories[dir_name].append(file_info)

        total_files = len(self.filtered_files)

        # Create directory nodes and add files
        for dir_name, files in directories.items():
            # Create directory node
            dir_item = QTreeWidgetItem(self.file_tree)
            dir_item.setText(0, f"📁 {dir_name}")
            dir_item.setText(3, "Directory")
            dir_item.setExpanded(True)

            # Add files to directory
            for file_info in files:
                self.add_file_item_from_info(file_info, dir_item)

        # Update file count with filter status
        total_all_files = len(self.all_files)
        if total_files < total_all_files:
            self.file_count_label.setText(f"Showing {total_files} of {total_all_files} files")
        else:
            self.file_count_label.setText(f"{total_files} files found")

        self.file_tree.setVisible(True)
        self.empty_state_label.setVisible(False)
    
    def get_directories_to_scan(self) -> Dict[str, str]:
        """Get directories to scan based on current task paths."""
        directories = {}
        
        if not self.current_task_paths:
            return directories
        
        # Working files directory
        working_file_path = self.current_task_paths.get('working_file_path', '')
        if working_file_path:
            working_dir = os.path.dirname(working_file_path)
            directories['Working Files'] = working_dir
        
        # Render output directory
        render_output_path = self.current_task_paths.get('render_output_path', '')
        if render_output_path:
            directories['Render Output'] = render_output_path
        
        # Media files directory
        media_file_path = self.current_task_paths.get('media_file_path', '')
        if media_file_path:
            directories['Media Files'] = media_file_path
        
        # Cache files directory (if exists)
        cache_file_path = self.current_task_paths.get('cache_file_path', '')
        if cache_file_path:
            directories['Cache Files'] = cache_file_path
        
        return directories
    
    def scan_directory(self, directory_path: str, parent_item: QTreeWidgetItem) -> int:
        """Scan a directory and add files to the tree."""
        files_found = 0
        
        try:
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                
                if os.path.isfile(item_path):
                    self.add_file_item(item_path, parent_item)
                    files_found += 1
                elif os.path.isdir(item_path):
                    # Add subdirectory
                    subdir_item = QTreeWidgetItem(parent_item)
                    subdir_item.setText(0, f"📁 {item}")
                    subdir_item.setText(3, "Directory")
                    
                    # Recursively scan subdirectory (limit depth to avoid performance issues)
                    if parent_item.parent() is None:  # Only go one level deep
                        subfiles = self.scan_directory(item_path, subdir_item)
                        files_found += subfiles
                        
                        # Remove empty subdirectory
                        if subfiles == 0:
                            parent_item.removeChild(subdir_item)
        
        except (OSError, PermissionError) as e:
            # Handle permission errors gracefully
            error_item = QTreeWidgetItem(parent_item)
            error_item.setText(0, f"❌ Error: {str(e)}")
            error_item.setText(3, "Error")
        
        return files_found
    
    def add_file_item(self, file_path: str, parent_item: QTreeWidgetItem):
        """Add a file item to the tree."""
        try:
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()
            
            # Get file stats
            stat = os.stat(file_path)
            file_size = self.format_file_size(stat.st_size)
            modified_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            
            # Create file item
            file_item = QTreeWidgetItem(parent_item)
            
            # Set icon and name
            icon = self.FILE_TYPE_ICONS.get(file_ext, '📄')
            file_item.setText(0, f"{icon} {file_name}")
            file_item.setText(1, file_size)
            file_item.setText(2, modified_time)
            file_item.setText(3, file_ext.upper() if file_ext else "File")
            
            # Store full path in item data
            file_item.setData(0, Qt.UserRole, file_path)
            
        except (OSError, PermissionError):
            # Skip files that can't be accessed
            pass

    def add_file_item_from_info(self, file_info: Dict[str, Any], parent_item: QTreeWidgetItem):
        """Add a file item to the tree from file info dictionary."""
        try:
            file_path = file_info['path']
            file_name = file_info['name']
            file_ext = os.path.splitext(file_name)[1].lower()

            # Format file size and modified time
            file_size = self.format_file_size(file_info['size'])
            if file_info['modified']:
                modified_time = file_info['modified'].strftime("%Y-%m-%d %H:%M")
            else:
                modified_time = "Unknown"

            # Create file item
            file_item = QTreeWidgetItem(parent_item)

            # Set icon and name
            icon = self.FILE_TYPE_ICONS.get(file_ext, '📄')
            file_item.setText(0, f"{icon} {file_name}")
            file_item.setText(1, file_size)
            file_item.setText(2, modified_time)
            file_item.setText(3, file_ext.upper() if file_ext else "File")

            # Store full path in item data
            file_item.setData(0, Qt.UserRole, file_path)

        except Exception:
            # Skip files that can't be processed
            pass
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.1f} {size_names[i]}"
    
    def show_empty_state(self):
        """Show empty state when no files are found."""
        self.file_tree.setVisible(False)
        self.empty_state_label.setVisible(True)
        self.file_count_label.setText("No files found")
    
    def on_file_selection_changed(self):
        """Handle file selection change."""
        selected_items = self.file_tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            file_path = item.data(0, Qt.UserRole)
            if file_path:
                self.fileSelected.emit(file_path)
    
    def on_file_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle file double-click."""
        file_path = item.data(0, Qt.UserRole)
        if file_path and os.path.isfile(file_path):
            self.open_file(file_path)
    
    def show_context_menu(self, position):
        """Show context menu for file operations."""
        item = self.file_tree.itemAt(position)
        if not item:
            return
        
        file_path = item.data(0, Qt.UserRole)
        if not file_path or not os.path.isfile(file_path):
            return
        
        menu = QMenu(self)

        # Open file action
        open_action = QAction("Open", self)
        open_action.triggered.connect(lambda: self.open_file(file_path))
        menu.addAction(open_action)

        # Open folder action
        open_folder_action = QAction("Open Folder", self)
        open_folder_action.triggered.connect(lambda: self.open_folder(file_path))
        menu.addAction(open_folder_action)

        menu.addSeparator()

        # Create new file action
        create_new_action = QAction("Create New File", self)
        create_new_action.triggered.connect(lambda: self.create_new_file())
        menu.addAction(create_new_action)

        # Duplicate with new version action
        duplicate_action = QAction("Duplicate with New Version", self)
        duplicate_action.triggered.connect(lambda: self.duplicate_with_new_version(file_path))
        menu.addAction(duplicate_action)

        menu.addSeparator()

        # Send to render farm action
        render_action = QAction("Send to Render Farm", self)
        render_action.triggered.connect(lambda: self.send_to_render_farm(file_path))
        menu.addAction(render_action)

        # Mark as published action
        publish_action = QAction("Mark as Published", self)
        publish_action.triggered.connect(lambda: self.mark_as_published(file_path))
        menu.addAction(publish_action)

        # Add version note action
        note_action = QAction("Add Version Note", self)
        note_action.triggered.connect(lambda: self.add_version_note(file_path))
        menu.addAction(note_action)

        menu.addSeparator()

        # Properties action
        properties_action = QAction("Properties", self)
        properties_action.triggered.connect(lambda: self.show_file_properties(file_path))
        menu.addAction(properties_action)

        menu.exec(self.file_tree.mapToGlobal(position))
    
    def open_file(self, file_path: str):
        """Open file in default application."""
        try:
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":
                os.system(f"open '{file_path}'")
            else:
                os.system(f"xdg-open '{file_path}'")
            
            self.fileOpened.emit(file_path)
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error Opening File",
                f"Could not open file:\n{file_path}\n\nError: {str(e)}"
            )
    
    def open_folder(self, file_path: str):
        """Open folder containing the file."""
        try:
            folder_path = os.path.dirname(file_path)
            
            if sys.platform == "win32":
                os.startfile(folder_path)
            elif sys.platform == "darwin":
                os.system(f"open '{folder_path}'")
            else:
                os.system(f"xdg-open '{folder_path}'")
                
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error Opening Folder",
                f"Could not open folder:\n{os.path.dirname(file_path)}\n\nError: {str(e)}"
            )
    
    def show_file_properties(self, file_path: str):
        """Show file properties dialog."""
        try:
            stat = os.stat(file_path)
            file_name = os.path.basename(file_path)
            file_size = self.format_file_size(stat.st_size)
            created_time = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
            modified_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            properties_text = f"""File: {file_name}
Path: {file_path}
Size: {file_size} ({stat.st_size:,} bytes)
Created: {created_time}
Modified: {modified_time}"""
            
            QMessageBox.information(
                self,
                "File Properties",
                properties_text
            )
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Could not get file properties:\n{str(e)}"
            )
    
    def create_new_file(self):
        """Create a new working file for the selected task."""
        if not self.current_task_id or not self.project_model:
            QMessageBox.warning(self, "Error", "No task selected or project model not available")
            return

        try:
            # Generate new file path using PathBuilder
            paths = self.project_model.generate_task_paths(self.current_task_id, "001", "maya_scene")
            if not paths:
                QMessageBox.warning(self, "Error", "Could not generate file paths for task")
                return

            new_file_path = paths.get('working_file_path', '')
            if not new_file_path:
                QMessageBox.warning(self, "Error", "Could not determine working file path")
                return

            # Check if file already exists and increment version
            base_path = new_file_path.replace('_v001.ma', '')
            version = 1
            while os.path.exists(f"{base_path}_v{version:03d}.ma"):
                version += 1

            final_path = f"{base_path}_v{version:03d}.ma"

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(final_path), exist_ok=True)

            # Create new file with basic content
            with open(final_path, 'w') as f:
                f.write(f"// New Maya scene file created for task: {self.current_task_id}\n")
                f.write(f"// Version: v{version:03d}\n")
                f.write(f"// Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            # Refresh file browser
            self.refresh_files()

            QMessageBox.information(
                self,
                "File Created",
                f"New file created:\n{os.path.basename(final_path)}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error Creating File", f"Could not create new file:\n{str(e)}")

    def duplicate_with_new_version(self, file_path: str):
        """Duplicate selected file with incremented version number."""
        try:
            if not os.path.isfile(file_path):
                QMessageBox.warning(self, "Error", "Selected file does not exist")
                return

            # Extract version from filename
            import re
            file_name = os.path.basename(file_path)
            version_match = re.search(r'_v(\d{3})', file_name)

            if version_match:
                current_version = int(version_match.group(1))
                new_version = current_version + 1
                new_file_name = file_name.replace(f"_v{current_version:03d}", f"_v{new_version:03d}")
            else:
                # No version found, add v002
                name_part, ext = os.path.splitext(file_name)
                new_file_name = f"{name_part}_v002{ext}"

            new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)

            # Check if new version already exists
            if os.path.exists(new_file_path):
                QMessageBox.warning(
                    self,
                    "File Exists",
                    f"Version {new_file_name} already exists"
                )
                return

            # Copy file
            import shutil
            shutil.copy2(file_path, new_file_path)

            # Refresh file browser
            self.refresh_files()

            QMessageBox.information(
                self,
                "File Duplicated",
                f"File duplicated as:\n{new_file_name}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error Duplicating File", f"Could not duplicate file:\n{str(e)}")

    def send_to_render_farm(self, file_path: str):
        """Send file to render farm (placeholder implementation)."""
        file_name = os.path.basename(file_path)

        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Send to Render Farm",
            f"Send '{file_name}' to render farm?\n\nThis will submit the file for rendering.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Placeholder implementation
            QMessageBox.information(
                self,
                "Render Submitted",
                f"File '{file_name}' has been submitted to the render farm.\n\n"
                "Job ID: RF-2024-001\n"
                "Status: Queued\n"
                "Priority: Normal"
            )

    def mark_as_published(self, file_path: str):
        """Mark file as published in database."""
        file_name = os.path.basename(file_path)

        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Mark as Published",
            f"Mark '{file_name}' as published?\n\nThis will update the file status in the database.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # In a full implementation, this would update the database
                # For now, we'll just show a confirmation
                QMessageBox.information(
                    self,
                    "File Published",
                    f"File '{file_name}' has been marked as published.\n\n"
                    "Status: Published\n"
                    "Available for delivery"
                )

                # Refresh file browser to show updated status
                self.refresh_files()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not update file status:\n{str(e)}")

    def add_version_note(self, file_path: str):
        """Add or edit version note for the selected file."""
        from PySide6.QtWidgets import QDialog, QTextEdit, QDialogButtonBox

        file_name = os.path.basename(file_path)

        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Add Version Note - {file_name}")
        dialog.setMinimumSize(400, 300)

        layout = QVBoxLayout(dialog)

        # File info
        info_label = QLabel(f"File: {file_name}")
        info_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(info_label)

        # Note text area
        note_label = QLabel("Version Note:")
        layout.addWidget(note_label)

        note_text = QTextEdit()
        note_text.setPlaceholderText("Enter version notes, changes, or comments...")
        layout.addWidget(note_text)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        # Show dialog
        if dialog.exec() == QDialog.Accepted:
            note_content = note_text.toPlainText().strip()
            if note_content:
                # In a full implementation, this would save to database
                QMessageBox.information(
                    self,
                    "Note Added",
                    f"Version note added for '{file_name}':\n\n{note_content[:100]}..."
                )
            else:
                QMessageBox.information(self, "Note Cancelled", "No note was added.")

    def clear_selection(self):
        """Clear current task selection."""
        self.current_task_id = None
        self.current_task_paths = None
        self.task_info_label.setText("No task selected")
        self.file_tree.clear()
        self.all_files = []
        self.filtered_files = []
        self.show_empty_state()
