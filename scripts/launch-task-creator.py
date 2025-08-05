#!/usr/bin/env python3
"""
Launch script for Montu Manager Task Creator

Launches the Task Creator application with proper environment setup.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def main():
    """Launch the Task Creator application."""
    try:
        print("📝 Launching Ra: Task Creator...")
        
        # Import and run the Task Creator
        from montu.task_creator.main import main as task_creator_main
        
        return task_creator_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install PySide6 pandas")
        return 1
    except Exception as e:
        print(f"❌ Error launching Ra: Task Creator: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
