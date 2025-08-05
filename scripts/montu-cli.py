#!/usr/bin/env python3
"""
Montu Manager CLI Launcher

Command-line interface launcher for Montu Manager.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def main():
    """Launch the CLI interface."""
    try:
        from montu.cli.main import main as cli_main
        return cli_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure the Montu Manager package is properly installed.")
        return 1
    except Exception as e:
        print(f"❌ Error launching CLI: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
