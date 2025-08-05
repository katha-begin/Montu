#!/usr/bin/env python3
"""
Configuration Refresh Utility

Utility script to refresh Montu Manager configuration and clear caches
when project configuration files are manually modified.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def main():
    """Refresh Montu Manager configuration."""
    try:
        print("🔄 Refreshing Montu Manager Configuration...")
        print()
        
        # Import database
        from montu.shared.json_database import JSONDatabase
        
        db = JSONDatabase()
        
        # Step 1: Clear all caches
        print("1. Clearing PathBuilder cache...")
        db.clear_path_builder_cache()
        print("   ✅ PathBuilder cache cleared")
        
        # Step 2: Verify configuration loading
        print("2. Verifying project configuration...")
        project_configs = db.find('project_configs', {})
        
        if project_configs:
            project_config = project_configs[0]
            project_name = project_config.get('name', 'Unknown')
            task_types = project_config.get('task_types', [])
            
            print(f"   ✅ Project: {project_name}")
            print(f"   ✅ Task types: {', '.join(task_types)}")
            
            # Check for the specific change
            if 'comp' in task_types:
                print("   ✅ Updated task type 'comp' found in configuration")
            else:
                print("   ⚠️  Task type 'comp' not found in configuration")
                
        else:
            print("   ❌ No project configuration found")
            return 1
        
        # Step 3: Test PathBuilder reload
        print("3. Testing PathBuilder reload...")
        try:
            project_id = project_config.get('_id', project_config.get('project_id', 'SWA'))
            path_builder = db.get_path_builder(project_id)
            
            if path_builder:
                print(f"   ✅ PathBuilder reloaded for project: {project_id}")
            else:
                print(f"   ❌ Failed to reload PathBuilder for project: {project_id}")
                
        except Exception as e:
            print(f"   ❌ PathBuilder reload error: {e}")
        
        # Step 4: Provide instructions
        print()
        print("🎯 CONFIGURATION REFRESH COMPLETE!")
        print()
        print("📋 NEXT STEPS:")
        print("   1. Restart any running Montu Manager applications")
        print("   2. Or use 'Refresh Configuration' from the Project menu (Ctrl+R)")
        print("   3. Verify that task filters now show 'Comp' instead of 'Composite'")
        print()
        print("🔍 VERIFICATION:")
        print("   • Project Launcher: Check task type filter dropdown")
        print("   • Task Creator: Import CSV with 'comp' task types")
        print("   • All applications should now use the updated configuration")
        print()
        
        return 0
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the Montu project root directory")
        return 1
    except Exception as e:
        print(f"❌ Error refreshing configuration: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
