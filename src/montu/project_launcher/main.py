"""
Project Launcher Main Application

Entry point for the Project Launcher application with proper PySide6 setup
and integration with the validated Phase 1 infrastructure.
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .gui.main_window import ProjectLauncherMainWindow


def setup_application():
    """Set up the QApplication with proper configuration."""
    # Create application
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Montu Manager - Project Launcher")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Montu Manager")
    app.setOrganizationDomain("montu-manager.com")
    
    # Set application style
    app.setStyle("Fusion")  # Modern cross-platform style
    
    # Set high DPI support
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    return app


def check_dependencies():
    """Check that required dependencies are available."""
    try:
        # Test database connection
        from montu.shared.json_database import JSONDatabase
        db = JSONDatabase()
        
        # Test basic database operations
        stats = db.get_stats()
        if not stats:
            raise Exception("Database connection failed")
        
        # Test project configuration
        projects = db.find('project_configs', {})
        if not projects:
            raise Exception("No project configurations found")
        
        print(f"✅ Database check passed: {stats.get('total_documents', 0)} documents")
        return True
        
    except ImportError as e:
        QMessageBox.critical(
            None,
            "Dependency Error",
            f"Required modules not found:\n{e}\n\n"
            f"Please ensure the Montu Manager shared modules are properly installed."
        )
        return False
    
    except Exception as e:
        QMessageBox.critical(
            None,
            "Database Error",
            f"Database connection failed:\n{e}\n\n"
            f"Please ensure the Phase 1 infrastructure is properly set up."
        )
        return False


def main():
    """Main application entry point."""
    print("🚀 Starting Montu Manager - Project Launcher")
    
    # Set up application
    app = setup_application()
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    try:
        # Create and show main window
        main_window = ProjectLauncherMainWindow()
        main_window.show()
        
        print("✅ Project Launcher started successfully")
        
        # Run application event loop
        return app.exec()
        
    except Exception as e:
        print(f"❌ Failed to start Project Launcher: {e}")
        
        QMessageBox.critical(
            None,
            "Startup Error",
            f"Failed to start Project Launcher:\n{e}\n\n"
            f"Please check the console for more details."
        )
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
