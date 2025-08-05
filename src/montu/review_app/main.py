#!/usr/bin/env python3
"""
Montu Manager Review Application

Main entry point for the Review Application.
Provides media browser with playback, annotation tools, and approval tracking.
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from montu.review_app.gui.main_window import ReviewAppMainWindow


def main():
    """Main entry point for Review Application."""
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Montu Manager - Review Application")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Montu Manager")
    
    # Set application style
    app.setStyle('Fusion')
    
    try:
        print("🎬 Starting Montu Manager - Review Application")
        
        # Create and show main window
        window = ReviewAppMainWindow()
        window.show()
        
        print("✅ Review Application started successfully")
        
        # Run application
        return app.exec()
        
    except Exception as e:
        print(f"❌ Failed to start Review Application: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
