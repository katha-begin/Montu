# Montu Manager Codebase Reorganization Implementation Guide

**Version**: 1.0  
**Date**: August 19, 2025  
**Status**: Implementation Ready  

## 🎯 Executive Summary

This document provides step-by-step procedures for safely reorganizing the Montu Manager codebase to improve code reusability, prepare for DCC integrations, and create a more maintainable architecture while preserving the current production-ready status.

## 📋 Prerequisites

### Required Tools
- Git (version control)
- Python 3.12+
- PySide6
- All current Montu Manager dependencies

### Team Requirements
- **Lead Developer**: Oversees migration process
- **QA Tester**: Validates each phase
- **Backup Administrator**: Manages backups and rollback procedures

### Pre-Migration Checklist
- [ ] All current tests passing
- [ ] Complete backup of current codebase
- [ ] Development branch created
- [ ] Team notified of migration timeline
- [ ] Rollback procedures documented and tested

---

## 🚀 Phase 1: Core Extraction (2-3 weeks)

### Week 1: Path & Data Core Migration

#### Day 1-2: Setup and PathBuilder Migration

**Step 1: Create Core Directory Structure**
```bash
mkdir -p src/montu/core/{path,data,version,media,project,task}
touch src/montu/core/__init__.py
touch src/montu/core/path/__init__.py
touch src/montu/core/data/__init__.py
```

**Step 2: Extract TemplateProcessor from PathBuilder**
```python
# Create src/montu/core/path/templates.py
# Move TemplateProcessor class from path_builder.py
```

**Step 3: Migrate PathBuilder**
```bash
# Copy original file
cp src/montu/shared/path_builder.py src/montu/core/path/builder.py
```

**Step 4: Update PathBuilder imports**
```python
# In src/montu/core/path/builder.py
from .templates import TemplateProcessor
from ..data.models import PathGenerationResult
```

**Step 5: Create Backward Compatibility Wrapper**
```python
# Update src/montu/shared/path_builder.py
import warnings
from montu.core.path.builder import PathBuilder as CorePathBuilder
from montu.core.path.builder import PathGenerationResult

PathBuilder = CorePathBuilder

warnings.warn(
    "montu.shared.path_builder is deprecated. Use montu.core.path.builder instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['PathBuilder', 'PathGenerationResult']
```

**Step 6: Test PathBuilder Migration**
```bash
# Run existing tests
python test_task_mapping_simple.py
python test_enhanced_manual_task_creation.py

# Test both import paths
python -c "from montu.shared.path_builder import PathBuilder; print('Old import works')"
python -c "from montu.core.path.builder import PathBuilder; print('New import works')"
```

#### Day 3-4: Database Migration

**Step 1: Migrate JSONDatabase**
```bash
cp src/montu/shared/json_database.py src/montu/core/data/database.py
```

**Step 2: Create Data Models**
```python
# Create src/montu/core/data/models.py
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class PathGenerationResult:
    working_file_path: str
    render_output_path: str
    # ... rest of the model
```

**Step 3: Update Database Imports**
```python
# In src/montu/core/data/database.py
from .models import PathGenerationResult
```

**Step 4: Create Backward Compatibility**
```python
# Update src/montu/shared/json_database.py
import warnings
from montu.core.data.database import JSONDatabase as CoreJSONDatabase

JSONDatabase = CoreJSONDatabase

warnings.warn(
    "montu.shared.json_database is deprecated. Use montu.core.data.database instead.",
    DeprecationWarning,
    stacklevel=2
)
```

#### Day 5: Version Manager Migration

**Step 1: Migrate VersionManager**
```bash
cp src/montu/shared/version_manager.py src/montu/core/version/manager.py
```

**Step 2: Create Backward Compatibility**
```python
# Update src/montu/shared/version_manager.py
import warnings
from montu.core.version.manager import (
    VersionManager as CoreVersionManager,
    VersionStatus,
    VersionInfo
)

VersionManager = CoreVersionManager

warnings.warn(
    "montu.shared.version_manager is deprecated. Use montu.core.version.manager instead.",
    DeprecationWarning,
    stacklevel=2
)
```

### Week 2: Task & Project Core

#### Day 1-2: Extract Task ID Generation

**Step 1: Create Task Core Module**
```python
# Create src/montu/core/task/id_generator.py
class TaskIDGenerator:
    """Extracted from CSVParser for reusability."""
    
    @staticmethod
    def generate_task_id(project: str, episode: str, sequence: str, 
                        shot: str, task: str) -> str:
        """Generate task ID using PRD pattern."""
        # Move logic from CSVParser.generate_task_id()
        pass
    
    @staticmethod
    def _clean_identifier(identifier: str) -> str:
        """Clean identifier for task ID generation."""
        # Move logic from CSVParser._clean_identifier()
        pass
```

**Step 2: Update CSVParser to use TaskIDGenerator**
```python
# In src/montu/task_creator/csv_parser.py
from montu.core.task.id_generator import TaskIDGenerator

class CSVParser:
    def generate_task_id(self, project: str, episode: str, sequence: str, 
                        shot: str, task: str) -> str:
        return TaskIDGenerator.generate_task_id(project, episode, sequence, shot, task)
```

#### Day 3-4: Project Configuration Utilities

**Step 1: Create Project Core Module**
```python
# Create src/montu/core/project/config.py
class ProjectConfigManager:
    """Centralized project configuration management."""
    
    @staticmethod
    def validate_project_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate project configuration."""
        pass
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get default project configuration."""
        pass
```

#### Day 5: Name Cleaning Utilities

**Step 1: Create Task Utils**
```python
# Create src/montu/core/task/utils.py
class NameCleaner:
    """Name cleaning utilities for episodes, sequences, shots."""
    
    @staticmethod
    def clean_episode_name(episode: str, rules: Dict[str, str]) -> str:
        """Clean episode name using project rules."""
        pass
    
    @staticmethod
    def clean_sequence_name(sequence: str, rules: Dict[str, str]) -> str:
        """Clean sequence name using project rules."""
        pass
    
    @staticmethod
    def clean_shot_name(shot: str, rules: Dict[str, str]) -> str:
        """Clean shot name using project rules."""
        pass
```

### Week 3: Media & Validation

#### Day 1-2: Media Service Migration

**Step 1: Migrate MediaService**
```bash
cp src/montu/shared/media_service.py src/montu/core/media/service.py
```

**Step 2: Create Backward Compatibility**
```python
# Update src/montu/shared/media_service.py
import warnings
from montu.core.media.service import MediaService as CoreMediaService

MediaService = CoreMediaService

warnings.warn(
    "montu.shared.media_service is deprecated. Use montu.core.media.service instead.",
    DeprecationWarning,
    stacklevel=2
)
```

#### Day 3-4: Validation Utilities

**Step 1: Create Validation Module**
```python
# Create src/montu/core/data/validation.py
class DataValidator:
    """Centralized data validation utilities."""
    
    @staticmethod
    def validate_task_data(task_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate task data structure."""
        pass
    
    @staticmethod
    def validate_project_data(project_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate project data structure."""
        pass
```

#### Day 5: Testing and Validation

**Step 1: Run Comprehensive Tests**
```bash
# Test all applications
python scripts/launch-task-creator.py &
python scripts/launch-project-launcher.py &
python scripts/launch-review-app.py &

# Run all individual tests
python test_task_mapping_simple.py
python test_enhanced_manual_task_creation.py
python test_episode_sequence_dropdowns.py
```

**Step 2: Performance Testing**
```python
# Create performance_test.py
import time
from montu.core.data.database import JSONDatabase
from montu.core.path.builder import PathBuilder

def test_performance():
    start_time = time.time()
    
    db = JSONDatabase()
    stats = db.get_stats()
    
    end_time = time.time()
    print(f"Database stats query: {end_time - start_time:.4f}s")
    
    # Should be < 0.1s for acceptable performance
    assert end_time - start_time < 0.1
```

---

## 🔄 Phase 2: Shared Layer Reorganization (2 weeks)

### Week 1: UI Components Migration

#### Day 1-2: Move UI Components

**Step 1: Create Shared UI Structure**
```bash
mkdir -p src/montu/shared/ui
mkdir -p src/montu/shared/parsers
mkdir -p src/montu/shared/utils
```

**Step 2: Move UI Components**
```bash
mv src/montu/shared/scalable_task_model.py src/montu/shared/ui/models.py
mv src/montu/shared/pagination_widget.py src/montu/shared/ui/widgets.py
mv src/montu/shared/advanced_search_widget.py src/montu/shared/ui/widgets.py
```

#### Day 3-4: Extract CSV Parser

**Step 1: Move CSV Parser to Shared**
```bash
mv src/montu/task_creator/csv_parser.py src/montu/shared/parsers/csv_parser.py
```

**Step 2: Update Task Creator Imports**
```python
# In src/montu/task_creator/gui/main_window.py
from montu.shared.parsers.csv_parser import CSVParser, TaskRecord, NamingPattern
```

#### Day 5: Platform Utilities

**Step 1: Create Platform Utils**
```python
# Create src/montu/shared/utils/platform.py
import platform
from typing import Dict, Any
from pathlib import Path

class PlatformManager:
    @staticmethod
    def get_platform_config(base_config: Dict[str, Any]) -> Dict[str, Any]:
        system = platform.system().lower()
        return base_config.get(system, base_config)
    
    @staticmethod
    def normalize_path(path: str) -> str:
        return str(Path(path).resolve())
```

### Week 2: Integration Framework

#### Day 1-3: Create Integration Framework

**Step 1: Create Integration Structure**
```bash
mkdir -p src/montu/integrations/{base,maya,nuke}
```

**Step 2: Create Base DCC Interface**
```python
# Create src/montu/integrations/base/dcc_interface.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from montu.core.path.builder import PathBuilder
from montu.core.data.database import JSONDatabase

class DCCInterface(ABC):
    def __init__(self, project_config: Dict[str, Any]):
        self.path_builder = PathBuilder(project_config)
        self.db = JSONDatabase()
        self.dcc_name = self.get_dcc_name()
    
    @abstractmethod
    def get_dcc_name(self) -> str:
        pass
    
    @abstractmethod
    def open_file(self, file_path: str) -> bool:
        pass
    
    @abstractmethod
    def save_file(self, file_path: str) -> bool:
        pass
```

#### Day 4-5: Maya Integration Prototype

**Step 1: Create Maya Integration**
```python
# Create src/montu/integrations/maya/plugin.py
from ..base.dcc_interface import DCCInterface

class MayaIntegration(DCCInterface):
    def get_dcc_name(self) -> str:
        return "maya"
    
    def open_file(self, file_path: str) -> bool:
        try:
            import maya.cmds as cmds
            cmds.file(file_path, open=True, force=True)
            return True
        except Exception as e:
            print(f"Failed to open file: {e}")
            return False
    
    def save_file(self, file_path: str) -> bool:
        try:
            import maya.cmds as cmds
            cmds.file(rename=file_path)
            cmds.file(save=True, type='mayaAscii')
            return True
        except Exception as e:
            print(f"Failed to save file: {e}")
            return False
```

---

## 🏗️ Phase 3: Application Restructuring (1-2 weeks)

### Week 1: Directory Reorganization

#### Day 1-2: Rename Application Directories

**Step 1: Create Applications Structure**
```bash
mkdir -p src/montu/applications
mv src/montu/task_creator src/montu/applications/task_creator
mv src/montu/project_launcher src/montu/applications/project_launcher
mv src/montu/review_app src/montu/applications/review_app
mv src/montu/cli src/montu/applications/cli
```

#### Day 3-4: Separate GUI from Business Logic

**Step 1: Reorganize Task Creator**
```bash
mkdir -p src/montu/applications/task_creator/business
mv src/montu/applications/task_creator/directory_manager.py src/montu/applications/task_creator/business/
```

#### Day 5: Update Launch Scripts

**Step 1: Update Launch Scripts**
```python
# Update scripts/launch-task-creator.py
from montu.applications.task_creator.main import main as task_creator_main
```

### Week 2: API Layer

#### Day 1-3: Create External API Framework

**Step 1: Create API Structure**
```bash
mkdir -p src/montu/api/{rest,sdk}
```

**Step 2: Implement MontuClient SDK**
```python
# Create src/montu/api/sdk/client.py
from typing import Dict, Any, List, Optional
from montu.core.path.builder import PathBuilder
from montu.core.data.database import JSONDatabase
from montu.core.version.manager import VersionManager

class MontuClient:
    def __init__(self, project_id: str):
        self.db = JSONDatabase()
        self.project_config = self.db.find_one('project_configs', {'_id': project_id})
        self.path_builder = PathBuilder(self.project_config)
        self.version_manager = VersionManager(self.db)
    
    def get_task_paths(self, task_id: str, version: str = "latest") -> Dict[str, str]:
        task = self.db.find_one('tasks', {'_id': task_id})
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        if version == "latest":
            version = self.version_manager.get_latest_version(task_id)
        
        result = self.path_builder.generate_all_paths(task, version)
        return {
            'working_file': result.working_file_path,
            'render_output': result.render_output_path,
            'media_file': result.media_file_path,
            'cache_file': result.cache_file_path
        }
```

#### Day 4-5: Final Integration Testing

**Step 1: Test All Applications**
```bash
python src/montu/applications/task_creator/main.py
python src/montu/applications/project_launcher/main.py
python src/montu/applications/review_app/main.py
```

---

## 🧪 Testing Procedures

### Automated Testing

**Step 1: Create Migration Test Suite**
```python
# Create tests/test_migration_compatibility.py
import unittest

class MigrationCompatibilityTest(unittest.TestCase):
    def test_old_imports_work(self):
        from montu.shared.path_builder import PathBuilder
        from montu.shared.json_database import JSONDatabase
        # Test functionality
    
    def test_new_imports_work(self):
        from montu.core.path.builder import PathBuilder
        from montu.core.data.database import JSONDatabase
        # Test functionality
    
    def test_functionality_preserved(self):
        # Test that all core functionality works
        pass
```

**Step 2: Performance Testing**
```python
# Create tests/test_performance.py
def test_database_performance():
    # Ensure no performance regression
    pass

def test_path_generation_performance():
    # Ensure path generation is still fast
    pass
```

### Manual Testing Checklist

- [ ] All applications launch successfully
- [ ] CSV import functionality works
- [ ] Path generation produces correct paths
- [ ] Version management functions correctly
- [ ] Database operations complete successfully
- [ ] No error messages or warnings (except deprecation warnings)

---

## 🔄 Rollback Procedures

### Immediate Rollback (< 1 hour)

**Step 1: Git Rollback**
```bash
# Switch back to main branch
git checkout main

# Verify applications work
python scripts/launch-task-creator.py
```

### Partial Rollback (Specific Components)

**Step 1: Restore Specific Files**
```bash
# Restore specific file from backup
git checkout main -- src/montu/shared/path_builder.py
```

### Complete Rollback (Full Restoration)

**Step 1: Restore from Backup**
```bash
# Remove new structure
rm -rf src/montu/core
rm -rf src/montu/integrations
rm -rf src/montu/applications

# Restore from backup
cp -r migration_backup/src/* src/
```

---

## 📅 Timeline and Resources

### Phase 1: Core Extraction (2-3 weeks)
- **Resources**: 1 Lead Developer, 1 QA Tester
- **Risk Level**: Medium
- **Rollback Time**: < 1 hour

### Phase 2: Shared Layer (2 weeks)
- **Resources**: 1 Lead Developer, 1 QA Tester
- **Risk Level**: Low
- **Rollback Time**: < 30 minutes

### Phase 3: Application Restructuring (1-2 weeks)
- **Resources**: 1 Lead Developer, 1 QA Tester
- **Risk Level**: Low
- **Rollback Time**: < 15 minutes

### Total Timeline: 5-7 weeks
### Total Resources: 2 people (Lead Developer + QA Tester)

---

## ✅ Success Criteria

- [ ] All existing functionality preserved
- [ ] No performance degradation (< 5% acceptable)
- [ ] All applications launch and function normally
- [ ] Backward compatibility maintained during transition
- [ ] New core modules properly tested
- [ ] DCC integration framework functional
- [ ] External SDK operational
- [ ] Documentation updated
- [ ] Team trained on new structure

---

## 📞 Support and Escalation

**Technical Issues**: Lead Developer  
**Process Issues**: Project Manager  
**Rollback Decision**: Technical Lead + Project Manager  

**Emergency Rollback Trigger**: Any critical functionality broken for > 2 hours

---

## 📋 Code Examples for Backward Compatibility

### PathBuilder Compatibility Wrapper
```python
# src/montu/shared/path_builder.py (Updated)
"""
Backward compatibility wrapper for PathBuilder
DEPRECATED: Use montu.core.path.builder instead
"""

import warnings
from montu.core.path.builder import PathBuilder as CorePathBuilder
from montu.core.path.builder import PathGenerationResult, TemplateProcessor

# Maintain exact same API
class PathBuilder(CorePathBuilder):
    """Backward compatible PathBuilder wrapper."""

    def __init__(self, project_config):
        # Issue deprecation warning on first use
        warnings.warn(
            "montu.shared.path_builder is deprecated. "
            "Use montu.core.path.builder.PathBuilder instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(project_config)

# Re-export all public classes and functions
__all__ = ['PathBuilder', 'PathGenerationResult', 'TemplateProcessor']
```

### Database Compatibility Wrapper
```python
# src/montu/shared/json_database.py (Updated)
"""
Backward compatibility wrapper for JSONDatabase
DEPRECATED: Use montu.core.data.database instead
"""

import warnings
from montu.core.data.database import JSONDatabase as CoreJSONDatabase

class JSONDatabase(CoreJSONDatabase):
    """Backward compatible JSONDatabase wrapper."""

    def __init__(self, data_dir="data/json_db"):
        warnings.warn(
            "montu.shared.json_database is deprecated. "
            "Use montu.core.data.database.JSONDatabase instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(data_dir)

__all__ = ['JSONDatabase']
```

### Application Import Updates
```python
# Example: src/montu/applications/task_creator/gui/main_window.py
# OLD imports (still work with warnings)
from montu.shared.json_database import JSONDatabase
from montu.shared.path_builder import PathBuilder

# NEW imports (recommended)
from montu.core.data.database import JSONDatabase
from montu.core.path.builder import PathBuilder

# Mixed approach during transition
try:
    from montu.core.data.database import JSONDatabase
    from montu.core.path.builder import PathBuilder
except ImportError:
    # Fallback to old imports during transition
    from montu.shared.json_database import JSONDatabase
    from montu.shared.path_builder import PathBuilder
```

---

## 🔧 Migration Scripts

### Automated Migration Script
```python
#!/usr/bin/env python3
"""
Automated migration script for Montu Manager reorganization
Usage: python scripts/migrate_codebase.py --phase 1
"""

import os
import shutil
import sys
import argparse
from pathlib import Path
from datetime import datetime

class MontuMigrator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backup_dir = project_root / "migration_backup"
        self.log_file = project_root / "migration.log"

    def log(self, message: str):
        """Log migration progress."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"

        print(message)
        with open(self.log_file, 'a') as f:
            f.write(log_entry)

    def create_backup(self):
        """Create complete backup before migration."""
        self.log("Creating backup of current codebase...")

        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)

        # Backup entire src directory
        shutil.copytree(
            self.project_root / "src",
            self.backup_dir / "src"
        )

        # Backup important files
        important_files = [
            "requirements.txt",
            "README.md",
            "CURRENT_STATUS.md"
        ]

        for file in important_files:
            if (self.project_root / file).exists():
                shutil.copy2(
                    self.project_root / file,
                    self.backup_dir / file
                )

        self.log(f"✅ Backup created at {self.backup_dir}")

    def migrate_phase_1(self):
        """Execute Phase 1: Core Extraction."""
        self.log("Starting Phase 1: Core Extraction")

        # Create core directory structure
        core_dirs = [
            "src/montu/core",
            "src/montu/core/path",
            "src/montu/core/data",
            "src/montu/core/version",
            "src/montu/core/media",
            "src/montu/core/project",
            "src/montu/core/task"
        ]

        for dir_path in core_dirs:
            (self.project_root / dir_path).mkdir(parents=True, exist_ok=True)
            (self.project_root / dir_path / "__init__.py").touch()

        # Migrate core files
        migrations = [
            ("src/montu/shared/path_builder.py", "src/montu/core/path/builder.py"),
            ("src/montu/shared/json_database.py", "src/montu/core/data/database.py"),
            ("src/montu/shared/version_manager.py", "src/montu/core/version/manager.py"),
            ("src/montu/shared/media_service.py", "src/montu/core/media/service.py"),
        ]

        for old_path, new_path in migrations:
            self._migrate_file(old_path, new_path)

        self.log("✅ Phase 1 completed successfully")

    def _migrate_file(self, old_path: str, new_path: str):
        """Migrate a single file with backup compatibility wrapper."""
        old_file = self.project_root / old_path
        new_file = self.project_root / new_path

        if not old_file.exists():
            self.log(f"⚠️  Source file not found: {old_path}")
            return

        # Copy to new location
        shutil.copy2(old_file, new_file)

        # Create backward compatibility wrapper
        self._create_compatibility_wrapper(old_file, new_path)

        self.log(f"✅ Migrated {old_path} → {new_path}")

    def _create_compatibility_wrapper(self, old_file: Path, new_path: str):
        """Create backward compatibility wrapper."""
        module_name = old_file.stem
        new_module_path = new_path.replace('src/', '').replace('/', '.').replace('.py', '')

        wrapper_content = f'''"""
Backward compatibility wrapper for {module_name}
DEPRECATED: Use {new_module_path} instead
"""

import warnings
from {new_module_path} import *

warnings.warn(
    "{old_file.as_posix()} is deprecated. Use {new_module_path} instead.",
    DeprecationWarning,
    stacklevel=2
)
'''

        with open(old_file, 'w') as f:
            f.write(wrapper_content)

    def rollback(self):
        """Rollback migration to previous state."""
        self.log("Starting rollback procedure...")

        if not self.backup_dir.exists():
            self.log("❌ No backup found for rollback")
            return False

        # Remove new directories
        new_dirs = [
            "src/montu/core",
            "src/montu/integrations",
            "src/montu/applications"
        ]

        for dir_path in new_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                shutil.rmtree(full_path)

        # Restore from backup
        shutil.copytree(
            self.backup_dir / "src",
            self.project_root / "src",
            dirs_exist_ok=True
        )

        self.log("✅ Rollback completed successfully")
        return True

def main():
    parser = argparse.ArgumentParser(description='Montu Manager Migration Tool')
    parser.add_argument('--phase', type=int, choices=[1, 2, 3],
                       help='Migration phase to execute')
    parser.add_argument('--rollback', action='store_true',
                       help='Rollback to previous state')
    parser.add_argument('--backup', action='store_true',
                       help='Create backup only')

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    migrator = MontuMigrator(project_root)

    if args.rollback:
        migrator.rollback()
    elif args.backup:
        migrator.create_backup()
    elif args.phase == 1:
        migrator.create_backup()
        migrator.migrate_phase_1()
    else:
        print("Please specify --phase, --rollback, or --backup")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
```

---

## 🧪 Validation Scripts

### Pre-Migration Validation
```python
#!/usr/bin/env python3
"""
Pre-migration validation script
Ensures system is ready for migration
"""

import sys
from pathlib import Path

def validate_current_system():
    """Validate current system before migration."""
    print("🔍 Validating current system...")

    # Check if all applications can be imported
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

        from montu.shared.json_database import JSONDatabase
        from montu.shared.path_builder import PathBuilder
        from montu.shared.version_manager import VersionManager

        print("✅ Core modules import successfully")

        # Test database connection
        db = JSONDatabase()
        stats = db.get_stats()
        print(f"✅ Database connection works: {stats['total_documents']} documents")

        # Test path generation
        projects = db.find('project_configs', {})
        if projects:
            path_builder = PathBuilder(projects[0])
            print("✅ PathBuilder initialization works")

        return True

    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

def validate_test_suite():
    """Validate that test suite passes."""
    print("🧪 Validating test suite...")

    import subprocess

    # Run key tests
    test_files = [
        "test_task_mapping_simple.py",
        "test_enhanced_manual_task_creation.py"
    ]

    for test_file in test_files:
        try:
            result = subprocess.run(
                ["python", test_file],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print(f"✅ {test_file} passes")
            else:
                print(f"❌ {test_file} fails")
                return False

        except Exception as e:
            print(f"❌ Error running {test_file}: {e}")
            return False

    return True

if __name__ == "__main__":
    print("🚀 Montu Manager Pre-Migration Validation")
    print("=" * 50)

    system_valid = validate_current_system()
    tests_valid = validate_test_suite()

    if system_valid and tests_valid:
        print("\n✅ System is ready for migration!")
        sys.exit(0)
    else:
        print("\n❌ System is NOT ready for migration!")
        sys.exit(1)
```

### Post-Migration Validation
```python
#!/usr/bin/env python3
"""
Post-migration validation script
Ensures migration completed successfully
"""

import sys
import warnings
from pathlib import Path

def validate_new_imports():
    """Test that new import paths work."""
    print("🔍 Validating new import paths...")

    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

        # Test new core imports
        from montu.core.path.builder import PathBuilder
        from montu.core.data.database import JSONDatabase
        from montu.core.version.manager import VersionManager

        print("✅ New core imports work")
        return True

    except ImportError as e:
        print(f"❌ New imports failed: {e}")
        return False

def validate_backward_compatibility():
    """Test that old import paths still work with warnings."""
    print("🔍 Validating backward compatibility...")

    try:
        # Capture warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            from montu.shared.path_builder import PathBuilder
            from montu.shared.json_database import JSONDatabase

            # Check that deprecation warnings were issued
            deprecation_warnings = [warning for warning in w
                                  if issubclass(warning.category, DeprecationWarning)]

            if deprecation_warnings:
                print("✅ Backward compatibility works with deprecation warnings")
                return True
            else:
                print("⚠️  Backward compatibility works but no deprecation warnings")
                return True

    except ImportError as e:
        print(f"❌ Backward compatibility failed: {e}")
        return False

def validate_functionality():
    """Test that core functionality still works."""
    print("🔍 Validating core functionality...")

    try:
        from montu.core.data.database import JSONDatabase
        from montu.core.path.builder import PathBuilder

        # Test database
        db = JSONDatabase()
        stats = db.get_stats()

        if stats['total_documents'] > 0:
            print(f"✅ Database functionality works: {stats['total_documents']} documents")
        else:
            print("⚠️  Database works but no documents found")

        # Test path generation
        projects = db.find('project_configs', {})
        if projects:
            path_builder = PathBuilder(projects[0])

            # Test path generation
            task_data = {
                'project': 'TEST',
                'episode': 'ep01',
                'sequence': 'sq010',
                'shot': 'sh020',
                'task': 'lighting'
            }

            result = path_builder.generate_all_paths(task_data)
            if result.working_file_path:
                print("✅ Path generation functionality works")
            else:
                print("❌ Path generation failed")
                return False

        return True

    except Exception as e:
        print(f"❌ Functionality validation failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Montu Manager Post-Migration Validation")
    print("=" * 50)

    new_imports_valid = validate_new_imports()
    backward_compat_valid = validate_backward_compatibility()
    functionality_valid = validate_functionality()

    if new_imports_valid and backward_compat_valid and functionality_valid:
        print("\n✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Migration validation failed!")
        sys.exit(1)
```
