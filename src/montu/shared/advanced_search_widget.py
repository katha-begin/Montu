"""
Advanced Search Widget

High-performance search widget with debouncing, suggestions, and advanced search features.
"""

from typing import List, Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, 
    QLabel, QCompleter, QListWidget, QFrame, QCheckBox, QComboBox
)
from PySide6.QtCore import Signal, QTimer, Qt, QStringListModel
from PySide6.QtGui import QIcon


class AdvancedSearchWidget(QWidget):
    """
    Advanced search widget with real-time search, suggestions, and filters.
    
    Features:
    - Debounced search input to prevent excessive queries
    - Auto-complete suggestions based on existing data
    - Search history
    - Advanced search operators
    - Field-specific search
    - Search result highlighting
    """
    
    # Signals
    searchChanged = Signal(str)      # search_text
    searchCleared = Signal()
    advancedSearchRequested = Signal(dict)  # search_criteria
    
    # Search configuration
    DEBOUNCE_MS = 300
    MAX_SUGGESTIONS = 10
    MAX_HISTORY = 20
    
    def __init__(self, parent=None):
        """Initialize advanced search widget."""
        super().__init__(parent)
        
        # Search state
        self.current_search = ""
        self.search_history: List[str] = []
        self.suggestions: List[str] = []
        self.is_advanced_mode = False
        
        # Debouncing timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._execute_search)
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main search row
        search_row = QHBoxLayout()
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tasks, artists, sequences... (use quotes for exact match)")
        self.search_input.setClearButtonEnabled(True)
        search_row.addWidget(self.search_input)
        
        # Advanced search toggle
        self.advanced_button = QPushButton("Advanced")
        self.advanced_button.setCheckable(True)
        self.advanced_button.setMaximumWidth(80)
        search_row.addWidget(self.advanced_button)
        
        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.setMaximumWidth(60)
        search_row.addWidget(self.search_button)
        
        layout.addLayout(search_row)
        
        # Advanced search panel (initially hidden)
        self.advanced_panel = self.create_advanced_panel()
        self.advanced_panel.setVisible(False)
        layout.addWidget(self.advanced_panel)
        
        # Search suggestions (initially hidden)
        self.suggestions_list = QListWidget()
        self.suggestions_list.setMaximumHeight(150)
        self.suggestions_list.setVisible(False)
        layout.addWidget(self.suggestions_list)
        
        # Search info/stats
        self.search_info_label = QLabel("")
        self.search_info_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.search_info_label)
    
    def create_advanced_panel(self) -> QWidget:
        """Create advanced search panel."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Box)
        panel.setStyleSheet("QFrame { background-color: #f5f5f5; border: 1px solid #ccc; }")
        
        layout = QVBoxLayout(panel)
        
        # Field-specific search
        field_row = QHBoxLayout()
        field_row.addWidget(QLabel("Search in:"))
        
        self.field_combo = QComboBox()
        self.field_combo.addItems([
            "All Fields", "Task ID", "Task Type", "Artist", 
            "Episode", "Sequence", "Shot", "Status"
        ])
        field_row.addWidget(self.field_combo)
        
        field_row.addStretch()
        layout.addLayout(field_row)
        
        # Search options
        options_row = QHBoxLayout()
        
        self.case_sensitive_cb = QCheckBox("Case sensitive")
        options_row.addWidget(self.case_sensitive_cb)
        
        self.exact_match_cb = QCheckBox("Exact match")
        options_row.addWidget(self.exact_match_cb)
        
        self.regex_cb = QCheckBox("Regular expression")
        options_row.addWidget(self.regex_cb)
        
        options_row.addStretch()
        layout.addLayout(options_row)
        
        # Quick search templates
        templates_row = QHBoxLayout()
        templates_row.addWidget(QLabel("Quick searches:"))
        
        self.template_buttons = []
        templates = [
            ("My Tasks", "artist:@me"),
            ("In Progress", "status:in_progress"),
            ("This Week", "created:this_week"),
            ("High Priority", "priority:high")
        ]
        
        for name, query in templates:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, q=query: self.set_search_text(q))
            btn.setMaximumWidth(80)
            templates_row.addWidget(btn)
            self.template_buttons.append(btn)
        
        templates_row.addStretch()
        layout.addLayout(templates_row)
        
        return panel
    
    def setup_connections(self):
        """Set up signal connections."""
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.returnPressed.connect(self.execute_immediate_search)
        self.search_button.clicked.connect(self.execute_immediate_search)
        self.advanced_button.toggled.connect(self.toggle_advanced_mode)
        self.suggestions_list.itemClicked.connect(self.on_suggestion_selected)
        
        # Advanced panel connections
        self.field_combo.currentTextChanged.connect(self.on_advanced_options_changed)
        self.case_sensitive_cb.toggled.connect(self.on_advanced_options_changed)
        self.exact_match_cb.toggled.connect(self.on_advanced_options_changed)
        self.regex_cb.toggled.connect(self.on_advanced_options_changed)
    
    def on_search_text_changed(self, text: str):
        """Handle search text changes with debouncing."""
        self.current_search = text.strip()
        
        if self.current_search:
            # Show suggestions if available
            self.update_suggestions()
            # Start debounce timer
            self.search_timer.start(self.DEBOUNCE_MS)
        else:
            # Clear search immediately
            self.suggestions_list.setVisible(False)
            self.search_timer.stop()
            self._execute_search()
    
    def _execute_search(self):
        """Execute search after debounce period."""
        if self.current_search != self.search_input.text().strip():
            self.current_search = self.search_input.text().strip()
        
        # Add to history if not empty and not duplicate
        if self.current_search and (not self.search_history or self.search_history[0] != self.current_search):
            self.search_history.insert(0, self.current_search)
            self.search_history = self.search_history[:self.MAX_HISTORY]
        
        # Hide suggestions
        self.suggestions_list.setVisible(False)
        
        # Update search info
        if self.current_search:
            self.search_info_label.setText(f"Searching for: '{self.current_search}'")
        else:
            self.search_info_label.setText("")
        
        # Emit search signal
        if self.current_search:
            if self.is_advanced_mode:
                search_criteria = self.build_advanced_search_criteria()
                self.advancedSearchRequested.emit(search_criteria)
            else:
                self.searchChanged.emit(self.current_search)
        else:
            self.searchCleared.emit()
    
    def execute_immediate_search(self):
        """Execute search immediately without debouncing."""
        self.search_timer.stop()
        self._execute_search()
    
    def toggle_advanced_mode(self, enabled: bool):
        """Toggle advanced search mode."""
        self.is_advanced_mode = enabled
        self.advanced_panel.setVisible(enabled)
        
        if enabled:
            self.search_input.setPlaceholderText("Advanced search (use field:value syntax)")
            self.advanced_button.setText("Simple")
        else:
            self.search_input.setPlaceholderText("Search tasks, artists, sequences... (use quotes for exact match)")
            self.advanced_button.setText("Advanced")
        
        # Re-execute search with new mode
        if self.current_search:
            self._execute_search()
    
    def build_advanced_search_criteria(self) -> Dict[str, Any]:
        """Build advanced search criteria dictionary."""
        criteria = {
            'text': self.current_search,
            'field': self.field_combo.currentText(),
            'case_sensitive': self.case_sensitive_cb.isChecked(),
            'exact_match': self.exact_match_cb.isChecked(),
            'regex': self.regex_cb.isChecked()
        }
        return criteria
    
    def on_advanced_options_changed(self):
        """Handle advanced options changes."""
        if self.is_advanced_mode and self.current_search:
            self._execute_search()
    
    def update_suggestions(self):
        """Update search suggestions based on current input."""
        if not self.current_search or len(self.current_search) < 2:
            self.suggestions_list.setVisible(False)
            return
        
        # Filter suggestions based on current input
        matching_suggestions = []
        
        # Add history matches
        for item in self.search_history:
            if self.current_search.lower() in item.lower() and item != self.current_search:
                matching_suggestions.append(f"🕒 {item}")
        
        # Add predefined suggestions
        for suggestion in self.suggestions:
            if self.current_search.lower() in suggestion.lower():
                matching_suggestions.append(f"💡 {suggestion}")
        
        # Show suggestions if any
        if matching_suggestions:
            self.suggestions_list.clear()
            self.suggestions_list.addItems(matching_suggestions[:self.MAX_SUGGESTIONS])
            self.suggestions_list.setVisible(True)
        else:
            self.suggestions_list.setVisible(False)
    
    def on_suggestion_selected(self, item):
        """Handle suggestion selection."""
        suggestion_text = item.text()
        # Remove emoji prefix
        if suggestion_text.startswith('🕒 ') or suggestion_text.startswith('💡 '):
            suggestion_text = suggestion_text[2:]
        
        self.search_input.setText(suggestion_text)
        self.suggestions_list.setVisible(False)
        self.execute_immediate_search()
    
    def set_search_text(self, text: str):
        """Set search text programmatically."""
        self.search_input.setText(text)
        self.execute_immediate_search()
    
    def clear_search(self):
        """Clear search input and results."""
        self.search_input.clear()
        self.suggestions_list.setVisible(False)
        self.search_info_label.setText("")
    
    def set_suggestions(self, suggestions: List[str]):
        """Set available suggestions list."""
        self.suggestions = suggestions[:self.MAX_SUGGESTIONS]
    
    def get_search_history(self) -> List[str]:
        """Get search history."""
        return self.search_history.copy()
    
    def clear_search_history(self):
        """Clear search history."""
        self.search_history.clear()
    
    def update_search_stats(self, total_results: int, search_time_ms: int):
        """Update search statistics display."""
        if self.current_search:
            self.search_info_label.setText(
                f"Found {total_results} results for '{self.current_search}' ({search_time_ms}ms)"
            )
        else:
            self.search_info_label.setText("")
