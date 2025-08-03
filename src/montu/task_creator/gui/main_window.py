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
    QComboBox, QSpinBox, QCheckBox
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QIcon

from ..csv_parser import CSVParser, TaskRecord, NamingPattern
from .pattern_dialog import PatternConfigDialog


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


class TaskCreatorMainWindow(QMainWindow):
    """Main window for Task Creator application."""
    
    def __init__(self):
        super().__init__()
        self.tasks: List[TaskRecord] = []
        self.csv_file: Optional[Path] = None
        self.naming_pattern: Optional[NamingPattern] = None
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Montu Task Creator - CSV Import Tool")
        self.setMinimumSize(1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Header
        header_layout = self.create_header()
        layout.addLayout(header_layout)
        
        # Main content splitter
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)
        
        # Import section
        import_group = self.create_import_section()
        splitter.addWidget(import_group)
        
        # Preview section
        preview_group = self.create_preview_section()
        splitter.addWidget(preview_group)
        
        # Status bar
        self.statusBar().showMessage("Ready to import CSV files")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar)
        
    def create_header(self) -> QHBoxLayout:
        """Create header section with title and info."""
        layout = QHBoxLayout()
        
        # Title
        title = QLabel("Task Creator")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Info label
        info = QLabel("Import tasks from CSV files with intelligent naming pattern detection")
        info.setStyleSheet("color: #666;")
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
        
        # Task table
        self.task_table = QTableWidget()
        self.task_table.setAlternatingRowColors(True)
        self.task_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.task_table)
        
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
        self.export_json_button.clicked.connect(self.export_to_json)
    
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
        if dialog.exec() == dialog.Accepted:
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
        
        # Enable export if we have tasks
        self.export_json_button.setEnabled(len(tasks) > 0)
        
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
            self.task_table.setRowCount(0)
            self.task_table.setColumnCount(0)
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
        self.task_table.setColumnCount(len(headers))
        self.task_table.setHorizontalHeaderLabels(headers)
        self.task_table.setRowCount(len(self.tasks))
        
        for row, task in enumerate(self.tasks):
            self.task_table.setItem(row, 0, QTableWidgetItem(task.task_id))
            self.task_table.setItem(row, 1, QTableWidgetItem(task.project))
            self.task_table.setItem(row, 2, QTableWidgetItem(task.episode))
            self.task_table.setItem(row, 3, QTableWidgetItem(task.sequence))
            self.task_table.setItem(row, 4, QTableWidgetItem(task.shot))
            self.task_table.setItem(row, 5, QTableWidgetItem(task.task))
            self.task_table.setItem(row, 6, QTableWidgetItem(f"{task.estimated_duration_hours:.1f}"))
            
            frame_range = f"{task.frame_range['start']}-{task.frame_range['end']}"
            self.task_table.setItem(row, 7, QTableWidgetItem(frame_range))
        
        self.task_table.resizeColumnsToContents()
    
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
