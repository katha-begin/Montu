#!/usr/bin/env python3
"""
Launch script for Montu Manager Review Application

Launches the Review Application with proper environment setup.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def main():
    """Launch the Review Application."""
    try:
        print("🎬 Launching Montu Manager - Review Application...")
        
        # Import and run the Review Application
        from montu.review_app.main import main as review_main
        
        return review_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install PySide6")
        return 1
    except Exception as e:
        print(f"❌ Error launching Review Application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
