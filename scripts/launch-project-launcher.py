#!/usr/bin/env python3
"""
Project Launcher Launch Script

Convenient script to launch the Project Launcher application with proper
environment setup and dependency checking.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def main():
    """Launch the Project Launcher application."""
    try:
        from montu.project_launcher.main import main as launcher_main
        return launcher_main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure you're running from the project root directory")
        return 1
    except Exception as e:
        print(f"❌ Error launching Project Launcher: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
