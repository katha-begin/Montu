"""
Project Launcher Main Window

Main application window for the Project Launcher, integrating project selection,
task management, and file operations with the validated Phase 1 infrastructure.
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QStatusBar, QMenuBar, QMessageBox, QProgressBar, QLabel
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QAction, QIcon

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from .project_selector import ProjectSelector
from .task_list_widget import TaskListWidget
from .file_browser_widget import FileBrowserWidget
from .version_notes_widget import VersionNotesWidget
from ..core.models.project_model import ProjectModel


class ProjectLauncherMainWindow(QMainWindow):
    """
    Main window for the Project Launcher application.
    
    Integrates project selection, task management, and file operations
    using the validated Phase 1 infrastructure including PathBuilder Engine
    and enhanced JSON database.
    """
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Initialize data model
        self.project_model = ProjectModel()
        
        # State
        self.current_project_id: Optional[str] = None
        
        # Setup UI
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.setup_connections()
        
        # Initialize with available projects
        self.load_available_projects()
        
        # Setup auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh_stats)
        self.refresh_timer.start(60000)  # Refresh stats every minute
    
    def setup_ui(self):
        """Set up the main user interface."""
        self.setWindowTitle("Montu Manager - Project Launcher")
        self.setMinimumSize(1200, 800)
        self.resize(1600, 900)  # Increased width for file browser

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Create horizontal splitter for main sections
        main_splitter = QSplitter(Qt.Horizontal)

        # Left side: Project selector and task list in vertical splitter
        left_splitter = QSplitter(Qt.Vertical)

        # Project selector (top left)
        self.project_selector = ProjectSelector()
        self.project_selector.setMaximumHeight(200)
        left_splitter.addWidget(self.project_selector)

        # Task list (bottom left)
        self.task_list = TaskListWidget()
        left_splitter.addWidget(self.task_list)

        # Set left splitter proportions
        left_splitter.setSizes([200, 600])

        # Right side: File browser and version notes in vertical splitter
        right_splitter = QSplitter(Qt.Vertical)

        # File browser (top right)
        self.file_browser = FileBrowserWidget()
        self.file_browser.set_project_model(self.project_model)
        right_splitter.addWidget(self.file_browser)

        # Version notes (bottom right)
        self.version_notes = VersionNotesWidget()
        self.version_notes.set_project_model(self.project_model)
        right_splitter.addWidget(self.version_notes)

        # Set right splitter proportions (70% file browser, 30% version notes)
        right_splitter.setSizes([420, 180])

        # Add to main splitter
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(right_splitter)

        # Set main splitter proportions (70% left, 30% right)
        main_splitter.setSizes([1120, 480])

        main_layout.addWidget(main_splitter)
    
    def setup_menu_bar(self):
        """Set up the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        refresh_action = QAction("Refresh All", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_all)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Project menu
        project_menu = menubar.addMenu("Project")

        reload_project_action = QAction("Reload Current Project", self)
        reload_project_action.triggered.connect(self.reload_current_project)
        project_menu.addAction(reload_project_action)

        project_menu.addSeparator()

        refresh_config_action = QAction("Refresh Configuration", self)
        refresh_config_action.setShortcut("Ctrl+R")
        refresh_config_action.triggered.connect(self.refresh_configuration)
        project_menu.addAction(refresh_config_action)
        
        # Task menu
        task_menu = menubar.addMenu("Tasks")
        
        refresh_tasks_action = QAction("Refresh Tasks", self)
        refresh_tasks_action.triggered.connect(self.refresh_tasks)
        task_menu.addAction(refresh_tasks_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Set up the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status labels
        self.project_status_label = QLabel("No project loaded")
        self.status_bar.addWidget(self.project_status_label)
        
        self.status_bar.addPermanentWidget(QLabel("|"))
        
        self.task_status_label = QLabel("No tasks")
        self.status_bar.addPermanentWidget(self.task_status_label)
        
        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def setup_connections(self):
        """Set up signal connections between components."""
        # Project selector connections
        self.project_selector.projectChanged.connect(self.load_project)
        self.project_selector.refreshRequested.connect(self.load_available_projects)
        
        # Task list connections
        self.task_list.taskSelected.connect(self.on_task_selected)
        self.task_list.taskStatusChanged.connect(self.update_task_status)
        self.task_list.taskPriorityChanged.connect(self.update_task_priority)
        self.task_list.openWorkingFile.connect(self.open_working_file)
        self.task_list.refreshRequested.connect(self.refresh_tasks)

        # File browser connections
        self.file_browser.fileSelected.connect(self.on_file_selected)
        self.file_browser.fileOpened.connect(self.on_file_opened)
        self.file_browser.refreshRequested.connect(self.refresh_file_browser)

        # Version notes connections
        self.file_browser.fileSelected.connect(self.version_notes.set_selected_file)
    
    def load_available_projects(self):
        """Load available projects from database."""
        try:
            projects = self.project_model.get_available_projects()
            self.project_selector.set_available_projects(projects)
            self.project_selector.refresh_complete()
            
            if projects:
                self.status_bar.showMessage(f"Loaded {len(projects)} available projects", 3000)
            else:
                self.status_bar.showMessage("No projects found in database", 5000)
                
        except Exception as e:
            self.show_error("Failed to load projects", str(e))
            self.project_selector.refresh_complete()
    
    def load_project(self, project_id: str):
        """Load a specific project."""
        try:
            self.show_progress("Loading project...")
            
            # Load project in model
            success = self.project_model.load_project(project_id)
            
            if success:
                self.current_project_id = project_id
                
                # Update project selector
                project_info = self.project_model.get_current_project()
                if project_info:
                    self.project_selector.set_current_project(project_info)
                
                # Load tasks
                tasks = self.project_model.get_tasks()
                self.task_list.set_tasks(tasks)
                
                # Update status
                self.update_status_display()
                
                self.status_bar.showMessage(f"Loaded project {project_id} with {len(tasks)} tasks", 3000)
                
            else:
                self.show_error("Failed to load project", f"Could not load project {project_id}")
                self.project_selector.set_no_project_state()
            
        except Exception as e:
            self.show_error("Error loading project", str(e))
            self.project_selector.set_no_project_state()
        
        finally:
            self.hide_progress()
            self.project_selector.set_loading_state(False)
    
    def reload_current_project(self):
        """Reload the current project."""
        if self.current_project_id:
            self.load_project(self.current_project_id)
    
    def refresh_tasks(self):
        """Refresh task list from database."""
        if not self.current_project_id:
            self.task_list.refresh_complete()
            return
        
        try:
            self.show_progress("Refreshing tasks...")
            
            # Refresh tasks in model
            success = self.project_model.refresh_tasks()
            
            if success:
                # Update task list
                tasks = self.project_model.get_tasks()
                self.task_list.set_tasks(tasks)
                
                # Update status
                self.update_status_display()
                
                self.status_bar.showMessage(f"Refreshed {len(tasks)} tasks", 3000)
            else:
                self.show_error("Failed to refresh tasks", "Could not refresh task list")
            
        except Exception as e:
            self.show_error("Error refreshing tasks", str(e))
        
        finally:
            self.hide_progress()
            self.task_list.refresh_complete()
    
    def refresh_all(self):
        """Refresh all data."""
        self.load_available_projects()
        if self.current_project_id:
            self.refresh_tasks()

    def refresh_configuration(self):
        """Refresh project configuration and clear caches."""
        try:
            self.show_progress("Refreshing configuration...")

            # Clear database cache
            self.project_model.db.clear_path_builder_cache()

            # Refresh task list configuration
            self.task_list.refresh_configuration()

            # Reload current project to pick up new configuration
            if self.current_project_id:
                self.load_project(self.current_project_id)

            self.status_bar.showMessage("Configuration refreshed successfully", 3000)

        except Exception as e:
            self.show_error("Configuration Refresh Failed", f"Failed to refresh configuration: {str(e)}")

        finally:
            self.hide_progress()
    
    def on_task_selected(self, task_id: str):
        """Handle task selection."""
        task = self.project_model.get_task_by_id(task_id)
        if task:
            task_display = f"{task.get('shot', 'Unknown')} - {task.get('task', 'Unknown')}"
            self.status_bar.showMessage(f"Selected: {task_display}", 5000)

            # Update file browser with selected task
            self.file_browser.set_selected_task(task_id)
    
    def update_task_status(self, task_id: str, status: str):
        """Update task status."""
        try:
            self.show_progress("Updating task status...")

            success = self.project_model.update_task_status(task_id, status)

            if success:
                # Refresh the entire task list to ensure consistency
                tasks = self.project_model.get_tasks()
                self.task_list.set_tasks(tasks)

                # Update status display
                self.update_status_display()

                self.status_bar.showMessage(f"Updated task status to {status}", 3000)
            else:
                self.show_error("Failed to update status", f"Could not update task {task_id}")

        except Exception as e:
            self.show_error("Error updating task status", str(e))

        finally:
            self.hide_progress()
    
    def open_working_file(self, task_id: str):
        """Open working file for task."""
        try:
            self.show_progress("Generating file path...")
            
            # Get working file path
            working_file_path = self.project_model.get_working_file_path(task_id)
            
            if working_file_path:
                # For now, just show the path - in Phase 2B we'll add DCC launching
                QMessageBox.information(
                    self,
                    "Working File Path",
                    f"Working file path:\n\n{working_file_path}\n\n"
                    f"DCC application launching will be implemented in Phase 2B."
                )
                
                self.status_bar.showMessage(f"Generated working file path", 3000)
            else:
                self.show_error("Path Generation Failed", f"Could not generate working file path for task {task_id}")
            
        except Exception as e:
            self.show_error("Error opening working file", str(e))
        
        finally:
            self.hide_progress()

    def update_task_priority(self, task_id: str, priority: str):
        """Update task priority."""
        try:
            self.show_progress("Updating task priority...")

            success = self.project_model.update_task_priority(task_id, priority)

            if success:
                # Refresh the entire task list to ensure consistency
                tasks = self.project_model.get_tasks()
                self.task_list.set_tasks(tasks)

                # Update status display
                self.update_status_display()

                self.status_bar.showMessage(f"Updated task priority to {priority}", 3000)
            else:
                self.show_error("Failed to update priority", f"Could not update task {task_id}")

        except Exception as e:
            self.show_error("Error updating task priority", str(e))

        finally:
            self.hide_progress()

    def on_file_selected(self, file_path: str):
        """Handle file selection in file browser."""
        file_name = file_path.split('/')[-1].split('\\')[-1]  # Cross-platform filename
        self.status_bar.showMessage(f"Selected file: {file_name}", 3000)

    def on_file_opened(self, file_path: str):
        """Handle file opened from file browser."""
        file_name = file_path.split('/')[-1].split('\\')[-1]  # Cross-platform filename
        self.status_bar.showMessage(f"Opened file: {file_name}", 5000)

    def refresh_file_browser(self):
        """Refresh file browser."""
        self.file_browser.refresh_files()
        self.status_bar.showMessage("File browser refreshed", 2000)

    def update_status_display(self):
        """Update status bar display."""
        if self.current_project_id:
            project_info = self.project_model.get_current_project()
            if project_info:
                self.project_status_label.setText(f"Project: {project_info['name']}")
                self.task_status_label.setText(f"Tasks: {project_info['task_count']}")
                
                # Update project selector stats
                stats = self.project_model.get_database_stats()
                self.project_selector.update_project_stats(stats)
        else:
            self.project_status_label.setText("No project loaded")
            self.task_status_label.setText("No tasks")
    
    def auto_refresh_stats(self):
        """Auto-refresh statistics display."""
        if self.current_project_id:
            try:
                stats = self.project_model.get_database_stats()
                self.project_selector.update_project_stats(stats)
            except Exception:
                pass  # Silently ignore auto-refresh errors
    
    def show_progress(self, message: str):
        """Show progress bar with message."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_bar.showMessage(message)
    
    def hide_progress(self):
        """Hide progress bar."""
        self.progress_bar.setVisible(False)
    
    def show_error(self, title: str, message: str):
        """Show error message dialog."""
        QMessageBox.critical(self, title, message)
        self.status_bar.showMessage(f"Error: {title}", 5000)
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Project Launcher",
            "Montu Manager - Project Launcher v1.0\n\n"
            "Central project management and file operations application\n"
            "for the Montu Manager ecosystem.\n\n"
            "Built with PySide6 and integrated with the validated\n"
            "Phase 1 infrastructure including PathBuilder Engine\n"
            "and enhanced JSON database."
        )
    
    def closeEvent(self, event):
        """Handle application close."""
        # Stop timers
        self.refresh_timer.stop()
        
        # Accept close event
        event.accept()
