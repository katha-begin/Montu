"""
Collapsible Panel Widget

Reusable collapsible panel component with smooth hide/show toggle
functionality and customizable content for the Review Application.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame,
    QSizePolicy, QPropertyAnimation, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, Signal, QEasingCurve, QPropertyAnimation, QRect, pyqtProperty
from PySide6.QtGui import QIcon, QPainter, QPixmap


class CollapsiblePanel(QWidget):
    """
    Collapsible panel widget with smooth animations.
    
    Provides a toggle button to hide/show content with smooth
    transitions and customizable appearance.
    """
    
    # Signals
    toggled = Signal(bool)  # expanded state
    
    def __init__(self, title: str = "Panel", parent=None):
        """Initialize collapsible panel."""
        super().__init__(parent)
        
        # State
        self.title = title
        self.is_expanded = True
        self.content_widget: Optional[QWidget] = None
        self.animation_duration = 300  # milliseconds
        
        # Setup UI
        self.setup_ui()
        self.setup_animations()
    
    def setup_ui(self):
        """Set up the collapsible panel user interface."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Header with toggle button
        self.header_frame = QFrame()
        self.header_frame.setFrameStyle(QFrame.StyledPanel)
        self.header_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 2px;
            }
        """)
        
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(5, 5, 5, 5)
        
        # Toggle button
        self.toggle_button = QPushButton()
        self.toggle_button.setFixedSize(20, 20)
        self.toggle_button.setFlat(True)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-radius: 10px;
            }
        """)
        self.update_toggle_button()
        header_layout.addWidget(self.toggle_button)
        
        # Title label
        self.title_label = QPushButton(self.title)
        self.title_label.setFlat(True)
        self.title_label.setStyleSheet("""
            QPushButton {
                text-align: left;
                border: none;
                background-color: transparent;
                font-weight: bold;
                font-size: 12px;
                padding: 2px 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-radius: 3px;
            }
        """)
        header_layout.addWidget(self.title_label)
        
        # Spacer
        header_layout.addStretch()
        
        # Collapse/Expand indicator
        self.indicator_label = QPushButton("◄")
        self.indicator_label.setFixedSize(20, 20)
        self.indicator_label.setFlat(True)
        self.indicator_label.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                font-weight: bold;
                font-size: 10px;
                color: #666;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-radius: 10px;
                color: #333;
            }
        """)
        header_layout.addWidget(self.indicator_label)
        
        self.main_layout.addWidget(self.header_frame)
        
        # Content container
        self.content_container = QFrame()
        self.content_container.setFrameStyle(QFrame.StyledPanel)
        self.content_container.setStyleSheet("""
            QFrame {
                border: 1px solid #ccc;
                border-top: none;
                border-radius: 0px 0px 4px 4px;
                background-color: white;
            }
        """)
        
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        
        self.main_layout.addWidget(self.content_container)
        
        # Setup connections
        self.toggle_button.clicked.connect(self.toggle)
        self.title_label.clicked.connect(self.toggle)
        self.indicator_label.clicked.connect(self.toggle)
    
    def setup_animations(self):
        """Set up smooth animations for expand/collapse."""
        # Size animation
        self.size_animation = QPropertyAnimation(self.content_container, b"maximumHeight")
        self.size_animation.setDuration(self.animation_duration)
        self.size_animation.setEasingCurve(QEasingCurve.InOutCubic)
        
        # Opacity animation
        self.opacity_effect = QGraphicsOpacityEffect()
        self.content_container.setGraphicsEffect(self.opacity_effect)
        
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(self.animation_duration)
        self.opacity_animation.setEasingCurve(QEasingCurve.InOutCubic)
    
    def set_content_widget(self, widget: QWidget):
        """Set the content widget for the collapsible panel."""
        # Remove existing content
        if self.content_widget:
            self.content_layout.removeWidget(self.content_widget)
            self.content_widget.setParent(None)
        
        # Add new content
        self.content_widget = widget
        if widget:
            self.content_layout.addWidget(widget)
    
    def toggle(self):
        """Toggle the panel expanded/collapsed state."""
        self.set_expanded(not self.is_expanded)
    
    def set_expanded(self, expanded: bool):
        """Set the panel expanded state with animation."""
        if self.is_expanded == expanded:
            return
        
        self.is_expanded = expanded
        
        if expanded:
            self.expand()
        else:
            self.collapse()
        
        self.update_toggle_button()
        self.toggled.emit(self.is_expanded)
    
    def expand(self):
        """Expand the panel with smooth animation."""
        # Get the content height
        if self.content_widget:
            content_height = self.content_widget.sizeHint().height() + 20  # Add padding
        else:
            content_height = 100  # Default height
        
        # Animate size
        self.size_animation.setStartValue(0)
        self.size_animation.setEndValue(content_height)
        self.size_animation.start()
        
        # Animate opacity
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.start()
        
        # Show content
        self.content_container.show()
    
    def collapse(self):
        """Collapse the panel with smooth animation."""
        # Animate size
        current_height = self.content_container.height()
        self.size_animation.setStartValue(current_height)
        self.size_animation.setEndValue(0)
        self.size_animation.start()
        
        # Animate opacity
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.start()
        
        # Hide content after animation
        self.size_animation.finished.connect(self.hide_content_after_collapse)
    
    def hide_content_after_collapse(self):
        """Hide content container after collapse animation."""
        if not self.is_expanded:
            self.content_container.hide()
        self.size_animation.finished.disconnect()
    
    def update_toggle_button(self):
        """Update toggle button appearance based on state."""
        if self.is_expanded:
            self.toggle_button.setText("▼")
            self.indicator_label.setText("◄")
            self.indicator_label.setToolTip("Hide panel")
        else:
            self.toggle_button.setText("►")
            self.indicator_label.setText("►")
            self.indicator_label.setToolTip("Show panel")
    
    def set_title(self, title: str):
        """Set the panel title."""
        self.title = title
        self.title_label.setText(title)
    
    def get_title(self) -> str:
        """Get the panel title."""
        return self.title
    
    def is_panel_expanded(self) -> bool:
        """Check if the panel is currently expanded."""
        return self.is_expanded
    
    def set_animation_duration(self, duration: int):
        """Set the animation duration in milliseconds."""
        self.animation_duration = duration
        self.size_animation.setDuration(duration)
        self.opacity_animation.setDuration(duration)


class CollapsiblePanelContainer(QWidget):
    """
    Container widget that manages collapsible panels and layout adjustments.
    
    Handles automatic layout adjustments when panels are collapsed/expanded
    and provides coordinated panel management.
    """
    
    # Signals
    panelToggled = Signal(str, bool)  # panel_name, expanded
    
    def __init__(self, parent=None):
        """Initialize collapsible panel container."""
        super().__init__(parent)
        
        # State
        self.panels: Dict[str, CollapsiblePanel] = {}
        
        # Setup UI
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
    
    def add_panel(self, name: str, title: str, content_widget: QWidget) -> CollapsiblePanel:
        """Add a collapsible panel to the container."""
        panel = CollapsiblePanel(title, self)
        panel.set_content_widget(content_widget)
        panel.toggled.connect(lambda expanded: self.panelToggled.emit(name, expanded))
        
        self.panels[name] = panel
        self.layout.addWidget(panel)
        
        return panel
    
    def get_panel(self, name: str) -> Optional[CollapsiblePanel]:
        """Get a panel by name."""
        return self.panels.get(name)
    
    def expand_panel(self, name: str):
        """Expand a specific panel."""
        panel = self.panels.get(name)
        if panel:
            panel.set_expanded(True)
    
    def collapse_panel(self, name: str):
        """Collapse a specific panel."""
        panel = self.panels.get(name)
        if panel:
            panel.set_expanded(False)
    
    def toggle_panel(self, name: str):
        """Toggle a specific panel."""
        panel = self.panels.get(name)
        if panel:
            panel.toggle()
    
    def expand_all(self):
        """Expand all panels."""
        for panel in self.panels.values():
            panel.set_expanded(True)
    
    def collapse_all(self):
        """Collapse all panels."""
        for panel in self.panels.values():
            panel.set_expanded(False)
