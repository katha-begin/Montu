"""
Review Application Main Window

Main window for the Review Application providing media browser,
playback controls, annotation tools, and approval workflow.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QStatusBar, QProgressBar, QMessageBox, QGroupBox,
    QLabel, QComboBox, QPushButton, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QAction, QIcon, QFont

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from .media_player_widget import MediaPlayerWidget
from .annotation_widget import AnnotationWidget
from .approval_widget import ApprovalWidget
from .filter_widget import FilterWidget
from .grouped_media_widget import GroupedMediaWidget
from .collapsible_panel import CollapsiblePanelContainer
from ..models.review_model import ReviewModel


class ReviewAppMainWindow(QMainWindow):
    """
    Main window for the Review Application.
    
    Provides media browser, playback controls, annotation tools,
    and approval workflow for reviewing project deliverables.
    """
    
    def __init__(self, parent=None):
        """Initialize Review Application main window."""
        super().__init__(parent)
        
        # Initialize models
        self.review_model = ReviewModel()
        
        # State
        self.current_project_id: Optional[str] = None
        self.current_media_item: Optional[Dict[str, Any]] = None
        self.current_filters: Dict[str, Any] = {}
        
        # Setup UI
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.setup_connections()
        
        # Load initial data
        self.load_available_projects()
        
        # Setup auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_media_list)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def setup_ui(self):
        """Set up the main user interface."""
        self.setWindowTitle("Montu Manager - Review Application")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Project selection header
        header_group = QGroupBox("Project Selection")
        header_layout = QHBoxLayout(header_group)
        
        header_layout.addWidget(QLabel("Project:"))
        self.project_selector = QComboBox()
        self.project_selector.setMinimumWidth(200)
        header_layout.addWidget(self.project_selector)
        
        header_layout.addStretch()
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setMaximumWidth(80)
        header_layout.addWidget(self.refresh_button)
        
        main_layout.addWidget(header_group)
        
        # Main content splitter
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left side: Media browser with filters
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Filter widget
        self.filter_widget = FilterWidget()
        left_layout.addWidget(self.filter_widget)

        # Grouped media list
        media_group = QGroupBox("Media Files")
        media_layout = QVBoxLayout(media_group)

        self.grouped_media_widget = GroupedMediaWidget()
        self.grouped_media_widget.setMinimumWidth(350)
        media_layout.addWidget(self.grouped_media_widget)

        left_layout.addWidget(media_group)
        
        # Center panel: Media player (full height)
        self.media_player = MediaPlayerWidget()

        # Right panel: Collapsible annotation and approval tools
        self.collapsible_container = CollapsiblePanelContainer()

        # Create annotation widget
        self.annotation_widget = AnnotationWidget()
        self.annotation_panel = self.collapsible_container.add_panel(
            "annotations",
            "Annotations & Review",
            self.annotation_widget
        )

        # Create approval widget
        self.approval_widget = ApprovalWidget()
        self.approval_panel = self.collapsible_container.add_panel(
            "approval",
            "Approval Workflow",
            self.approval_widget
        )

        # Store reference to right panel for layout adjustments
        self.right_panel = self.collapsible_container

        # Add panels to main splitter (3-panel layout)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(self.media_player)
        main_splitter.addWidget(self.right_panel)

        # Set main splitter proportions (25% left, 45% center, 30% right)
        main_splitter.setSizes([350, 630, 420])

        # Store main splitter for dynamic resizing
        self.main_splitter = main_splitter
        
        main_layout.addWidget(main_splitter)
    
    def setup_menu_bar(self):
        """Set up the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_media_list)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        fullscreen_action = QAction("Toggle Fullscreen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        view_menu.addSeparator()

        # Panel toggle actions
        toggle_annotations_action = QAction("Toggle Annotations Panel", self)
        toggle_annotations_action.setShortcut("Ctrl+1")
        toggle_annotations_action.triggered.connect(lambda: self.collapsible_container.toggle_panel("annotations"))
        view_menu.addAction(toggle_annotations_action)

        toggle_approval_action = QAction("Toggle Approval Panel", self)
        toggle_approval_action.setShortcut("Ctrl+2")
        toggle_approval_action.triggered.connect(lambda: self.collapsible_container.toggle_panel("approval"))
        view_menu.addAction(toggle_approval_action)

        view_menu.addSeparator()

        # Panel management actions
        expand_all_action = QAction("Expand All Panels", self)
        expand_all_action.triggered.connect(self.collapsible_container.expand_all)
        view_menu.addAction(expand_all_action)

        collapse_all_action = QAction("Collapse All Panels", self)
        collapse_all_action.triggered.connect(self.collapsible_container.collapse_all)
        view_menu.addAction(collapse_all_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        clear_annotations_action = QAction("Clear Annotations", self)
        clear_annotations_action.triggered.connect(self.clear_annotations)
        tools_menu.addAction(clear_annotations_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Set up the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status label
        self.status_bar.showMessage("Ready")
        
        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def setup_connections(self):
        """Set up signal connections between components."""
        # Project selector
        self.project_selector.currentTextChanged.connect(self.on_project_changed)
        self.refresh_button.clicked.connect(self.refresh_media_list)
        
        # Grouped media widget
        self.grouped_media_widget.mediaSelected.connect(self.on_media_selected)
        self.grouped_media_widget.mediaDoubleClicked.connect(self.on_media_double_clicked)
        
        # Media player connections
        self.media_player.mediaLoaded.connect(self.on_media_loaded)
        self.media_player.playbackStateChanged.connect(self.on_playback_state_changed)
        
        # Annotation connections
        self.annotation_widget.annotationAdded.connect(self.on_annotation_added)
        
        # Approval connections
        self.approval_widget.approvalChanged.connect(self.on_approval_changed)

        # Filter connections
        self.filter_widget.filtersChanged.connect(self.on_filters_changed)
        self.filter_widget.filtersCleared.connect(self.on_filters_cleared)

        # Collapsible panel connections
        self.collapsible_container.panelToggled.connect(self.on_panel_toggled)
    
    def load_available_projects(self):
        """Load available projects from database."""
        try:
            projects = self.review_model.get_available_projects()
            
            self.project_selector.clear()
            self.project_selector.addItem("Select Project...", "")
            
            for project in projects:
                project_id = project.get('_id', 'Unknown')
                project_name = project.get('name', project_id)
                self.project_selector.addItem(f"{project_name} ({project_id})", project_id)
            
            if projects:
                self.status_bar.showMessage(f"Loaded {len(projects)} projects")
            else:
                self.status_bar.showMessage("No projects found")
                
        except Exception as e:
            self.show_error("Error Loading Projects", str(e))
    
    def on_project_changed(self, project_text: str):
        """Handle project selection change."""
        project_id = self.project_selector.currentData()
        
        if project_id and project_id != self.current_project_id:
            self.current_project_id = project_id
            self.review_model.set_current_project(project_id)
            self.refresh_media_list()
            self.status_bar.showMessage(f"Selected project: {project_text}")
    
    def refresh_media_list(self):
        """Refresh the media list for current project."""
        if not self.current_project_id:
            self.grouped_media_widget.clear()
            return

        try:
            self.show_progress("Loading media files...")

            # Get media items with current filters
            media_items = self.review_model.get_media_for_project(self.current_project_id, self.current_filters)

            # Update filter options with all available media (without filters)
            if not self.current_filters:  # Only update when no filters are active
                all_media_items = self.review_model.get_media_for_project(self.current_project_id)
                self.filter_widget.populate_filter_options(all_media_items)

            # Set media items in grouped widget
            self.grouped_media_widget.set_media_items(media_items)

            # Update status bar with filter info
            if self.current_filters:
                status_message = f"Loaded {len(media_items)} media files (filtered)"
            else:
                status_message = f"Loaded {len(media_items)} media files"

            self.status_bar.showMessage(status_message)

        except Exception as e:
            self.show_error("Error Loading Media", str(e))
        finally:
            self.hide_progress()
    
    def format_media_item_text(self, media_item: Dict[str, Any]) -> str:
        """Format media item for display in list."""
        task_id = media_item.get('task_id', 'Unknown')
        version = media_item.get('version', 'v001')
        file_type = media_item.get('file_type', 'unknown')
        approval_status = media_item.get('approval_status', 'pending')
        author = media_item.get('author', 'Unknown')
        file_name = media_item.get('file_name', '')
        file_extension = media_item.get('file_extension', '')

        # Get task info if available
        task_info = media_item.get('task_info', {})
        shot = task_info.get('shot', 'Unknown')
        task = task_info.get('task', 'Unknown')

        # Create display name
        if shot != 'Unknown' and task != 'Unknown':
            display_name = f"{shot} - {task} ({version})"
        else:
            # Fallback to parsing task_id
            parts = task_id.split('_')
            if len(parts) >= 4:
                shot = parts[2]
                task = parts[3]
                display_name = f"{shot} - {task} ({version})"
            else:
                display_name = f"{task_id} ({version})"

        # Status emoji
        status_emoji = {
            'pending': '⏳',
            'under_review': '👁️',
            'approved': '✅',
            'rejected': '❌',
            'archived': '📦'
        }.get(approval_status, '❓')

        # File type emoji
        type_emoji = {
            'video': '🎬',
            'image': '🖼️'
        }.get(file_type, '📄')

        # Format: [emoji] Shot-Task (version) [ext] - Author - Status
        if file_extension:
            return f"{type_emoji} {display_name} [{file_extension}] - {author} - {status_emoji} {approval_status}"
        else:
            return f"{type_emoji} {display_name} [{file_type}] - {author} - {status_emoji} {approval_status}"
    
    def on_media_selected(self, media_item: Dict[str, Any]):
        """Handle media selection changes from grouped widget."""
        if not media_item:
            self.current_media_item = None
            self.media_player.clear_media()
            self.annotation_widget.clear_annotations()
            self.approval_widget.clear_approval_data()
            return

        self.current_media_item = media_item

        # Update media player with comprehensive metadata
        if hasattr(self.media_player, 'load_media_with_metadata'):
            # Use enhanced media loading with metadata
            self.media_player.load_media_with_metadata(media_item)
        else:
            # Fallback to basic media loading
            media_path = media_item.get('file_path', '')
            if media_path and os.path.exists(media_path):
                self.media_player.load_media(media_path)
            else:
                self.media_player.clear_media()
                self.status_bar.showMessage("Media file not found")

        # Update annotation widget
        self.annotation_widget.set_media_item(media_item)

        # Update approval widget
        self.approval_widget.set_media_item(media_item)

        # Update info display
        task_id = media_item.get('task_id', 'Unknown')
        version = media_item.get('version', 'v001')
        self.status_bar.showMessage(f"Selected: {task_id} {version}")

    def on_media_double_clicked(self, media_item: Dict[str, Any]):
        """Handle media double-click events."""
        # Double-click could trigger OpenRV launch or full-screen playback
        if hasattr(self.media_player, 'launch_in_openrv'):
            self.media_player.launch_in_openrv()
        print(f"Double-clicked media: {media_item.get('file_name', 'Unknown')}")
    
    def on_media_loaded(self, file_path: str):
        """Handle media loaded in player."""
        self.status_bar.showMessage(f"Loaded: {os.path.basename(file_path)}")
    
    def on_playback_state_changed(self, state: str):
        """Handle playback state change."""
        self.status_bar.showMessage(f"Playback: {state}")
    
    def on_annotation_added(self, annotation: Dict[str, Any]):
        """Handle annotation added."""
        if self.current_media_item:
            # Save annotation to database
            self.review_model.add_annotation(self.current_media_item, annotation)
            self.status_bar.showMessage("Annotation added")
    
    def on_approval_changed(self, approval_data: Dict[str, Any]):
        """Handle approval status change."""
        if self.current_media_item:
            # Update approval status in database
            self.review_model.update_approval_status(self.current_media_item, approval_data)
            self.status_bar.showMessage(f"Approval status: {approval_data.get('status', 'unknown')}")
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def clear_annotations(self):
        """Clear all annotations for current media."""
        if self.current_media_item:
            reply = QMessageBox.question(
                self,
                "Clear Annotations",
                "Clear all annotations for this media item?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.annotation_widget.clear_annotations()
                self.status_bar.showMessage("Annotations cleared")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Review Application",
            "Montu Manager Review Application v1.0.0\n\n"
            "Media browser and review workflow tool for VFX/animation studios.\n\n"
            "Features:\n"
            "• Media playback with frame-accurate scrubbing\n"
            "• Annotation tools for review feedback\n"
            "• Approval workflow tracking\n"
            "• Version comparison capabilities"
        )
    
    def show_progress(self, message: str):
        """Show progress indicator."""
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage(message)
    
    def hide_progress(self):
        """Hide progress indicator."""
        self.progress_bar.setVisible(False)
    
    def show_error(self, title: str, message: str):
        """Show error message dialog."""
        QMessageBox.critical(self, title, message)
        self.status_bar.showMessage(f"Error: {title}")
    
    def closeEvent(self, event):
        """Handle application close event."""
        reply = QMessageBox.question(
            self,
            "Exit Review Application",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def on_filters_changed(self, filters: Dict[str, Any]):
        """Handle filter changes."""
        self.current_filters = filters
        print(f"Filters changed: {filters}")

        # Refresh media list with new filters
        if self.current_project_id:
            self.refresh_media_list()

    def on_filters_cleared(self):
        """Handle filter clearing."""
        self.current_filters = {}
        print("Filters cleared")

        # Refresh media list without filters
        if self.current_project_id:
            self.refresh_media_list()

    def on_panel_toggled(self, panel_name: str, expanded: bool):
        """Handle panel toggle events and adjust layout."""
        print(f"Panel '{panel_name}' {'expanded' if expanded else 'collapsed'}")

        # Adjust main splitter sizes based on panel states
        self.adjust_layout_for_panels()

    def adjust_layout_for_panels(self):
        """Adjust main splitter layout based on panel visibility."""
        # Check which panels are expanded
        annotations_expanded = self.annotation_panel.is_panel_expanded()
        approval_expanded = self.approval_panel.is_panel_expanded()

        # Calculate right panel width based on expanded panels
        if annotations_expanded or approval_expanded:
            # At least one panel is expanded - normal right panel width
            right_width = 420
        else:
            # All panels collapsed - minimal right panel width
            right_width = 50

        # Adjust splitter sizes
        current_sizes = self.main_splitter.sizes()
        total_width = sum(current_sizes)

        # Calculate new proportions
        left_width = 350  # Fixed left panel width
        center_width = total_width - left_width - right_width

        # Apply new sizes
        new_sizes = [left_width, center_width, right_width]
        self.main_splitter.setSizes(new_sizes)

        print(f"Layout adjusted: Left={left_width}, Center={center_width}, Right={right_width}")

    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
