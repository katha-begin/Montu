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
    QLabel, QPushButton, QGroupBox, QMenu, QMessageBox, QHeaderView
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
    
    def refresh_files(self):
        """Refresh the file list for the current task."""
        if not self.current_task_id or not self.current_task_paths:
            self.show_empty_state()
            return
        
        # Clear existing items
        self.file_tree.clear()
        
        # Get all relevant directories
        directories_to_scan = self.get_directories_to_scan()
        
        total_files = 0
        
        # Scan each directory
        for dir_name, dir_path in directories_to_scan.items():
            if not dir_path or not os.path.exists(dir_path):
                continue
            
            # Create directory node
            dir_item = QTreeWidgetItem(self.file_tree)
            dir_item.setText(0, f"📁 {dir_name}")
            dir_item.setText(3, "Directory")
            dir_item.setExpanded(True)
            
            # Scan files in directory
            files_found = self.scan_directory(dir_path, dir_item)
            total_files += files_found
            
            # Remove empty directory nodes
            if files_found == 0:
                self.file_tree.takeTopLevelItem(self.file_tree.indexOfTopLevelItem(dir_item))
        
        # Update file count
        if total_files > 0:
            self.file_count_label.setText(f"{total_files} files found")
            self.file_tree.setVisible(True)
            self.empty_state_label.setVisible(False)
        else:
            self.show_empty_state()
    
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
    
    def clear_selection(self):
        """Clear current task selection."""
        self.current_task_id = None
        self.current_task_paths = None
        self.task_info_label.setText("No task selected")
        self.file_tree.clear()
        self.show_empty_state()
