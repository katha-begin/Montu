"""
Pattern Configuration Dialog

Dialog for manually configuring CSV parsing patterns for Episode, Sequence, and Shot fields.
Provides intelligent pattern detection and manual override capabilities.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QGroupBox, QComboBox, QTextEdit,
    QSplitter, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ..csv_parser import NamingPattern


class PatternConfigDialog(QDialog):
    """Dialog for configuring CSV parsing patterns."""
    
    def __init__(self, csv_file: Path, current_pattern: Optional[NamingPattern] = None, parent=None):
        super().__init__(parent)
        self.csv_file = csv_file
        self.current_pattern = current_pattern
        self.sample_data: List[Dict[str, Any]] = []
        self.detected_patterns: List[NamingPattern] = []
        
        self.setup_ui()
        self.load_sample_data()
        self.analyze_patterns()
        
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Configure Naming Pattern")
        self.setMinimumSize(800, 600)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Configure CSV Parsing Pattern")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)
        
        # Description
        desc = QLabel(
            "Configure how Episode, Sequence, and Shot fields should be parsed from your CSV data. "
            "The system will auto-detect common patterns, but you can customize them below."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; margin-bottom: 16px;")
        layout.addWidget(desc)
        
        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left side - Pattern configuration
        config_group = self.create_pattern_config()
        splitter.addWidget(config_group)
        
        # Right side - Sample data preview
        preview_group = self.create_sample_preview()
        splitter.addWidget(preview_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.auto_detect_button = QPushButton("Auto-Detect")
        button_layout.addWidget(self.auto_detect_button)
        
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.cancel_button)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.setDefault(True)
        self.ok_button.setStyleSheet("""
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
        """)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.auto_detect_button.clicked.connect(self.auto_detect_patterns)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.clicked.connect(self.accept)
        
    def create_pattern_config(self) -> QGroupBox:
        """Create pattern configuration section."""
        group = QGroupBox("Pattern Configuration")
        layout = QVBoxLayout(group)
        
        # Delimiter selection
        delimiter_layout = QHBoxLayout()
        delimiter_layout.addWidget(QLabel("Field Delimiter:"))
        
        self.delimiter_combo = QComboBox()
        self.delimiter_combo.addItems(["_ (underscore)", "- (dash)", ". (dot)", "| (pipe)"])
        self.delimiter_combo.setCurrentText("_ (underscore)")
        delimiter_layout.addWidget(self.delimiter_combo)
        
        delimiter_layout.addStretch()
        layout.addLayout(delimiter_layout)
        
        # Pattern fields
        fields_layout = QVBoxLayout()
        
        # Episode pattern
        episode_layout = QHBoxLayout()
        episode_layout.addWidget(QLabel("Episode Pattern:"))
        self.episode_pattern_edit = QLineEdit()
        self.episode_pattern_edit.setPlaceholderText("e.g., part[1] for second part after split")
        episode_layout.addWidget(self.episode_pattern_edit)
        fields_layout.addLayout(episode_layout)
        
        # Sequence pattern
        sequence_layout = QHBoxLayout()
        sequence_layout.addWidget(QLabel("Sequence Pattern:"))
        self.sequence_pattern_edit = QLineEdit()
        self.sequence_pattern_edit.setPlaceholderText("e.g., part[2] for third part after split")
        sequence_layout.addWidget(self.sequence_pattern_edit)
        fields_layout.addLayout(sequence_layout)
        
        # Shot pattern
        shot_layout = QHBoxLayout()
        shot_layout.addWidget(QLabel("Shot Pattern:"))
        self.shot_pattern_edit = QLineEdit()
        self.shot_pattern_edit.setPlaceholderText("e.g., part[2] for third part after split")
        shot_layout.addWidget(self.shot_pattern_edit)
        fields_layout.addLayout(shot_layout)
        
        layout.addLayout(fields_layout)
        
        # Pattern explanation
        explanation = QTextEdit()
        explanation.setMaximumHeight(120)
        explanation.setPlainText(
            "Pattern Syntax:\n"
            "• part[0] = first part after splitting\n"
            "• part[1] = second part after splitting\n"
            "• part[-1] = last part after splitting\n\n"
            "Example: 'SWA_Ep00_sq0010' with '_' delimiter:\n"
            "• part[0] = 'SWA'\n"
            "• part[1] = 'Ep00'\n"
            "• part[2] = 'sq0010'"
        )
        explanation.setReadOnly(True)
        explanation.setStyleSheet("background-color: #f5f5f5; font-family: monospace;")
        layout.addWidget(explanation)
        
        return group
    
    def create_sample_preview(self) -> QGroupBox:
        """Create sample data preview section."""
        group = QGroupBox("Sample Data Preview")
        layout = QVBoxLayout(group)
        
        # Sample table
        self.sample_table = QTableWidget()
        self.sample_table.setAlternatingRowColors(True)
        layout.addWidget(self.sample_table)
        
        # Parsed result preview
        result_label = QLabel("Parsed Result Preview:")
        result_label.setStyleSheet("font-weight: bold; margin-top: 8px;")
        layout.addWidget(result_label)
        
        self.result_text = QTextEdit()
        self.result_text.setMaximumHeight(100)
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("background-color: #f9f9f9; font-family: monospace;")
        layout.addWidget(self.result_text)
        
        return group
    
    def load_sample_data(self):
        """Load sample data from CSV file."""
        try:
            import pandas as pd
            df = pd.read_csv(self.csv_file, nrows=10)  # Load first 10 rows
            self.sample_data = df.to_dict('records')
            
            # Update sample table
            if self.sample_data:
                headers = list(self.sample_data[0].keys())
                self.sample_table.setColumnCount(len(headers))
                self.sample_table.setHorizontalHeaderLabels(headers)
                self.sample_table.setRowCount(len(self.sample_data))
                
                for row, data in enumerate(self.sample_data):
                    for col, header in enumerate(headers):
                        value = str(data.get(header, ''))
                        self.sample_table.setItem(row, col, QTableWidgetItem(value))
                
                self.sample_table.resizeColumnsToContents()
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load sample data: {str(e)}")
    
    def analyze_patterns(self):
        """Analyze and detect naming patterns."""
        if not self.sample_data:
            return
        
        from ..csv_parser import CSVParser
        parser = CSVParser()
        
        try:
            self.detected_patterns = parser.detect_naming_patterns(self.sample_data)
            
            # Apply best pattern if available
            if self.detected_patterns:
                best_pattern = self.detected_patterns[0]
                self.apply_pattern(best_pattern)
            elif self.current_pattern:
                self.apply_pattern(self.current_pattern)
                
        except Exception as e:
            print(f"Pattern analysis failed: {e}")
    
    def apply_pattern(self, pattern: NamingPattern):
        """Apply a naming pattern to the UI."""
        # Set delimiter
        delimiter_map = {
            "_": "_ (underscore)",
            "-": "- (dash)",
            ".": ". (dot)",
            "|": "| (pipe)"
        }
        delimiter_text = delimiter_map.get(pattern.delimiter, "_ (underscore)")
        self.delimiter_combo.setCurrentText(delimiter_text)
        
        # Set patterns
        self.episode_pattern_edit.setText(pattern.episode_pattern)
        self.sequence_pattern_edit.setText(pattern.sequence_pattern)
        self.shot_pattern_edit.setText(pattern.shot_pattern)
        
        # Update preview
        self.update_preview()
    
    def auto_detect_patterns(self):
        """Auto-detect patterns and apply the best one."""
        if self.detected_patterns:
            best_pattern = self.detected_patterns[0]
            self.apply_pattern(best_pattern)
            
            confidence = int(best_pattern.confidence * 100)
            QMessageBox.information(
                self,
                "Pattern Detected",
                f"Applied auto-detected pattern with {confidence}% confidence.\n"
                "You can still modify the pattern manually if needed."
            )
        else:
            QMessageBox.warning(
                self,
                "No Pattern Detected",
                "Could not automatically detect a naming pattern.\n"
                "Please configure the pattern manually."
            )
    
    def update_preview(self):
        """Update the parsed result preview."""
        if not self.sample_data:
            return
        
        try:
            pattern = self.get_pattern()
            delimiter = self.get_delimiter()
            
            # Preview parsing results
            preview_lines = []
            for i, row in enumerate(self.sample_data[:3]):  # Show first 3 rows
                sequence = str(row.get('Sequence', ''))
                shot = str(row.get('Shot', ''))
                episode = str(row.get('Episode', ''))
                
                # Parse using pattern
                parsed_episode = self.parse_field(episode, pattern.episode_pattern, delimiter)
                parsed_sequence = self.parse_field(sequence, pattern.sequence_pattern, delimiter)
                parsed_shot = self.parse_field(shot, pattern.shot_pattern, delimiter)
                
                preview_lines.append(
                    f"Row {i+1}: Episode='{parsed_episode}', "
                    f"Sequence='{parsed_sequence}', Shot='{parsed_shot}'"
                )
            
            self.result_text.setPlainText("\n".join(preview_lines))
            
        except Exception as e:
            self.result_text.setPlainText(f"Preview error: {str(e)}")
    
    def parse_field(self, value: str, pattern: str, delimiter: str) -> str:
        """Parse a field using the specified pattern."""
        if not value or not pattern:
            return value
        
        # Simple pattern parsing for part[index]
        if pattern.startswith('part[') and pattern.endswith(']'):
            try:
                index_str = pattern[5:-1]  # Extract index from part[index]
                index = int(index_str)
                parts = value.split(delimiter)
                
                if -len(parts) <= index < len(parts):
                    return parts[index]
                else:
                    return value
            except (ValueError, IndexError):
                return value
        
        return value
    
    def get_delimiter(self) -> str:
        """Get the selected delimiter."""
        delimiter_map = {
            "_ (underscore)": "_",
            "- (dash)": "-",
            ". (dot)": ".",
            "| (pipe)": "|"
        }
        return delimiter_map.get(self.delimiter_combo.currentText(), "_")
    
    def get_pattern(self) -> NamingPattern:
        """Get the configured naming pattern."""
        return NamingPattern(
            episode_pattern=self.episode_pattern_edit.text().strip(),
            sequence_pattern=self.sequence_pattern_edit.text().strip(),
            shot_pattern=self.shot_pattern_edit.text().strip(),
            delimiter=self.get_delimiter(),
            confidence=1.0  # Manual configuration has full confidence
        )
