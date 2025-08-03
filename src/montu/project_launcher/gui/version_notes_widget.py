"""
Version Notes Widget

Widget for displaying version-related metadata and notes when files are selected
in the File Browser. Shows artist notes, review notes, version status, and creation date.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
    QGroupBox, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class VersionNotesWidget(QWidget):
    """
    Version notes display widget for showing file version metadata.
    
    Displays artist notes, review notes, version status, creation date,
    and other version-related information when files are selected.
    """
    
    # Signals
    notesRequested = Signal(str, str)  # task_id, version
    
    def __init__(self, parent=None):
        """Initialize version notes widget."""
        super().__init__(parent)
        
        # State
        self.current_file_path: Optional[str] = None
        self.current_task_id: Optional[str] = None
        self.current_version: Optional[str] = None
        self.project_model = None  # Will be set by parent
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main group box
        main_group = QGroupBox("Version Notes")
        main_layout = QVBoxLayout(main_group)
        
        # File info section
        file_info_frame = QFrame()
        file_info_frame.setFrameStyle(QFrame.StyledPanel)
        file_info_layout = QVBoxLayout(file_info_frame)
        
        # File name label
        self.file_name_label = QLabel("No file selected")
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        self.file_name_label.setFont(font)
        self.file_name_label.setWordWrap(True)
        file_info_layout.addWidget(self.file_name_label)
        
        # Version and status info
        version_layout = QHBoxLayout()
        
        self.version_label = QLabel("Version: --")
        self.version_label.setStyleSheet("color: #666;")
        version_layout.addWidget(self.version_label)
        
        version_layout.addStretch()
        
        self.status_label = QLabel("Status: --")
        self.status_label.setStyleSheet("color: #666;")
        version_layout.addWidget(self.status_label)
        
        file_info_layout.addLayout(version_layout)
        
        # Creation date
        self.creation_date_label = QLabel("Created: --")
        self.creation_date_label.setStyleSheet("color: #666; font-size: 9pt;")
        file_info_layout.addWidget(self.creation_date_label)
        
        main_layout.addWidget(file_info_frame)
        
        # Notes section
        notes_frame = QFrame()
        notes_frame.setFrameStyle(QFrame.StyledPanel)
        notes_layout = QVBoxLayout(notes_frame)
        
        # Artist notes
        artist_notes_label = QLabel("Artist Notes:")
        artist_notes_label.setStyleSheet("font-weight: bold; color: #333;")
        notes_layout.addWidget(artist_notes_label)
        
        self.artist_notes_text = QTextEdit()
        self.artist_notes_text.setReadOnly(True)
        self.artist_notes_text.setMaximumHeight(60)
        self.artist_notes_text.setPlaceholderText("No artist notes available")
        self.artist_notes_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 4px;
                font-size: 9pt;
            }
        """)
        notes_layout.addWidget(self.artist_notes_text)
        
        # Review notes
        review_notes_label = QLabel("Review Notes:")
        review_notes_label.setStyleSheet("font-weight: bold; color: #333;")
        notes_layout.addWidget(review_notes_label)
        
        self.review_notes_text = QTextEdit()
        self.review_notes_text.setReadOnly(True)
        self.review_notes_text.setMaximumHeight(60)
        self.review_notes_text.setPlaceholderText("No review notes available")
        self.review_notes_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 4px;
                font-size: 9pt;
            }
        """)
        notes_layout.addWidget(self.review_notes_text)
        
        # Additional comments
        comments_label = QLabel("Additional Comments:")
        comments_label.setStyleSheet("font-weight: bold; color: #333;")
        notes_layout.addWidget(comments_label)
        
        self.comments_text = QTextEdit()
        self.comments_text.setReadOnly(True)
        self.comments_text.setMaximumHeight(60)
        self.comments_text.setPlaceholderText("No additional comments")
        self.comments_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 4px;
                font-size: 9pt;
            }
        """)
        notes_layout.addWidget(self.comments_text)
        
        main_layout.addWidget(notes_frame)
        
        # Add stretch to push content to top
        main_layout.addStretch()
        
        layout.addWidget(main_group)
        
        # Set initial empty state
        self.set_empty_state()
    
    def set_project_model(self, project_model):
        """Set the project model for database queries."""
        self.project_model = project_model
    
    def set_selected_file(self, file_path: str):
        """Set the currently selected file and load version notes."""
        if file_path == self.current_file_path:
            return  # No change
        
        self.current_file_path = file_path
        
        if not file_path or not os.path.isfile(file_path):
            self.set_empty_state()
            return
        
        # Extract version information from file path
        self.extract_version_info(file_path)
        
        # Load version metadata
        self.load_version_metadata()
    
    def extract_version_info(self, file_path: str):
        """Extract task ID and version from file path."""
        try:
            file_name = os.path.basename(file_path)
            
            # Try to extract version from filename (e.g., v001, v002)
            import re
            version_match = re.search(r'_v(\d{3})', file_name)
            if version_match:
                self.current_version = version_match.group(1)
            else:
                self.current_version = "001"  # Default version
            
            # Try to extract task ID from path structure
            # Expected path: .../project/episode/sequence/shot/task/version/filename
            path_parts = file_path.replace('\\', '/').split('/')
            
            # Look for task ID pattern in path
            for part in reversed(path_parts):
                if '_' in part and any(task_type in part.lower() for task_type in 
                                     ['lighting', 'composite', 'modeling', 'rigging', 'animation']):
                    # This might be a task ID
                    self.current_task_id = part.replace('.ma', '').replace('.nk', '').replace('.hip', '')
                    break
            
            if not self.current_task_id:
                # Fallback: try to match against known tasks
                if self.project_model:
                    tasks = self.project_model.get_tasks()
                    for task in tasks:
                        task_id = task.get('_id', '')
                        if task_id in file_path:
                            self.current_task_id = task_id
                            break
            
        except Exception as e:
            print(f"Error extracting version info: {e}")
            self.current_task_id = None
            self.current_version = "001"
    
    def load_version_metadata(self):
        """Load version metadata from database."""
        if not self.project_model or not self.current_task_id:
            self.set_file_info_only()
            return
        
        try:
            # Get task information
            task = self.project_model.get_task_by_id(self.current_task_id)
            if not task:
                self.set_file_info_only()
                return
            
            # Update file info
            file_name = os.path.basename(self.current_file_path)
            self.file_name_label.setText(file_name)
            self.version_label.setText(f"Version: v{self.current_version}")
            
            # Get file creation date
            try:
                stat = os.stat(self.current_file_path)
                creation_date = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
                self.creation_date_label.setText(f"Created: {creation_date}")
            except:
                self.creation_date_label.setText("Created: Unknown")
            
            # Load version notes from task data (if available)
            # Note: In a full implementation, this would query a versions table
            # For now, we'll use task-level notes as an example
            
            # Set status based on task status
            task_status = task.get('status', 'unknown')
            status_display = task_status.replace('_', ' ').title()
            self.status_label.setText(f"Status: {status_display}")
            
            # Load notes (example data structure)
            version_data = self.get_version_data(task, self.current_version)
            
            # Artist notes
            artist_note = version_data.get('artist_note', '')
            if artist_note:
                self.artist_notes_text.setPlainText(artist_note)
            else:
                self.artist_notes_text.setPlainText("")
            
            # Review notes
            review_note = version_data.get('review_note', '')
            if review_note:
                self.review_notes_text.setPlainText(review_note)
            else:
                self.review_notes_text.setPlainText("")
            
            # Additional comments
            comments = version_data.get('comments', '')
            if comments:
                self.comments_text.setPlainText(comments)
            else:
                self.comments_text.setPlainText("")
            
        except Exception as e:
            print(f"Error loading version metadata: {e}")
            self.set_file_info_only()
    
    def get_version_data(self, task: Dict[str, Any], version: str) -> Dict[str, Any]:
        """Get version-specific data from task or database."""
        # In a full implementation, this would query a versions collection
        # For now, we'll simulate version data based on task information
        
        version_data = {}
        
        # Example version notes based on task status and type
        task_type = task.get('task', '').lower()
        task_status = task.get('status', '')
        
        if task_status == 'completed':
            if task_type == 'lighting':
                version_data['artist_note'] = "Final lighting pass completed"
                version_data['review_note'] = "Approved by lighting supervisor"
            elif task_type == 'composite':
                version_data['artist_note'] = "Final composite with all elements"
                version_data['review_note'] = "Client approved for delivery"
            else:
                version_data['artist_note'] = "Work completed as requested"
                version_data['review_note'] = "Approved by supervisor"
        elif task_status == 'in_progress':
            version_data['artist_note'] = "Work in progress - latest version"
            version_data['review_note'] = "Pending review"
        else:
            version_data['artist_note'] = "Initial version"
            version_data['review_note'] = "Not yet reviewed"
        
        # Add version-specific comments
        if version == "001":
            version_data['comments'] = "Initial version for review"
        elif version == "002":
            version_data['comments'] = "Addressing feedback from v001"
        elif version == "003":
            version_data['comments'] = "Final version incorporating all notes"
        else:
            version_data['comments'] = f"Version {version} - continued iteration"
        
        return version_data
    
    def set_file_info_only(self):
        """Set file info without version metadata."""
        if self.current_file_path:
            file_name = os.path.basename(self.current_file_path)
            self.file_name_label.setText(file_name)
            self.version_label.setText(f"Version: v{self.current_version or '001'}")
            
            # Get file creation date
            try:
                stat = os.stat(self.current_file_path)
                creation_date = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
                self.creation_date_label.setText(f"Created: {creation_date}")
            except:
                self.creation_date_label.setText("Created: Unknown")
            
            self.status_label.setText("Status: Unknown")
        
        # Clear notes
        self.artist_notes_text.setPlainText("")
        self.review_notes_text.setPlainText("")
        self.comments_text.setPlainText("")
    
    def set_empty_state(self):
        """Set widget to empty state when no file is selected."""
        self.current_file_path = None
        self.current_task_id = None
        self.current_version = None
        
        self.file_name_label.setText("No file selected")
        self.version_label.setText("Version: --")
        self.status_label.setText("Status: --")
        self.creation_date_label.setText("Created: --")
        
        self.artist_notes_text.setPlainText("")
        self.review_notes_text.setPlainText("")
        self.comments_text.setPlainText("")
    
    def clear_selection(self):
        """Clear current file selection."""
        self.set_empty_state()
