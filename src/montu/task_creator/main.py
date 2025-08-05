#!/usr/bin/env python3
"""
Ra: Task Creator Application

Main entry point for the Ra: Task Creator GUI application.
Provides CSV import functionality with intelligent naming pattern detection.
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from montu.task_creator.gui.main_window import TaskCreatorMainWindow


def main():
    """Main entry point for Task Creator application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Montu Task Creator")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("Montu Manager")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = TaskCreatorMainWindow()
    window.show()
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
