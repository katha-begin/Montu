# Montu Manager Backup Strategy Recommendations

**Version**: 1.0  
**Date**: August 19, 2025  
**Status**: Implementation Ready  

## 🎯 Executive Summary

This document provides comprehensive backup strategy recommendations for the Montu Manager codebase reorganization, ensuring the current production-ready system is protected while enabling safe migration to the new architecture.

## 🌿 Git Branching Strategy

### **Primary Branch Protection**
```
main (production-ready)
├── feature/codebase-reorganization (current work)
├── hotfix/* (emergency fixes)
└── release/* (version releases)
```

### **Branch Naming Convention**
- **Main Branch**: `main` - Production-ready code
- **Feature Branch**: `feature/codebase-reorganization` - Reorganization work
- **Hotfix Branches**: `hotfix/issue-description` - Critical fixes
- **Release Branches**: `release/v1.x.x` - Version releases

### **Branch Protection Rules**
```bash
# Protect main branch from direct pushes
git config branch.main.pushRemote origin
git config branch.main.merge refs/heads/main

# Require pull request reviews for main
# (Configure in GitHub/GitLab repository settings)
```

### **Safe Development Workflow**
1. **Always work in feature branch**: `feature/codebase-reorganization`
2. **Regular commits**: Commit frequently with descriptive messages
3. **Backup commits**: Push to remote regularly
4. **Testing checkpoints**: Test after each major change
5. **Rollback ready**: Maintain ability to quickly return to main

## 💾 Database Backup Procedures

### **JSON Database Backup**

#### **Automated Backup Script**
```python
#!/usr/bin/env python3
"""
Automated JSON Database Backup Script
Creates timestamped backups of the JSON database
"""

import shutil
import os
from datetime import datetime
from pathlib import Path

def backup_json_database():
    """Create timestamped backup of JSON database."""
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data" / "json_db"
    backup_dir = project_root / "backups" / "database"
    
    if not data_dir.exists():
        print("❌ JSON database directory not found")
        return False
    
    # Create backup directory
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"json_db_backup_{timestamp}"
    backup_path = backup_dir / backup_name
    
    try:
        shutil.copytree(data_dir, backup_path)
        print(f"✅ Database backup created: {backup_path}")
        
        # Keep only last 10 backups
        cleanup_old_backups(backup_dir, keep=10)
        
        return True
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def cleanup_old_backups(backup_dir: Path, keep: int = 10):
    """Keep only the most recent backups."""
    backups = sorted([d for d in backup_dir.iterdir() if d.is_dir()], 
                    key=lambda x: x.stat().st_mtime, reverse=True)
    
    for old_backup in backups[keep:]:
        shutil.rmtree(old_backup)
        print(f"🗑️  Removed old backup: {old_backup.name}")

if __name__ == "__main__":
    backup_json_database()
```

#### **Manual Backup Commands**
```bash
# Create manual backup
mkdir -p backups/database
cp -r data/json_db backups/database/json_db_manual_$(date +%Y%m%d_%H%M%S)

# Verify backup
ls -la backups/database/
```

### **Database Backup Schedule**
- **Before migration**: Complete backup before starting any phase
- **After each phase**: Backup after completing each migration phase
- **Daily during migration**: Automated daily backups during active development
- **Before major changes**: Manual backup before significant modifications

### **Backup Verification**
```python
def verify_backup(backup_path: Path) -> bool:
    """Verify backup integrity."""
    required_files = [
        "tasks.json",
        "project_configs.json", 
        "media_records.json",
        "versions.json"
    ]
    
    for file in required_files:
        file_path = backup_path / file
        if not file_path.exists():
            print(f"❌ Missing file in backup: {file}")
            return False
        
        # Verify JSON is valid
        try:
            with open(file_path, 'r') as f:
                json.load(f)
        except json.JSONDecodeError:
            print(f"❌ Corrupted JSON in backup: {file}")
            return False
    
    print("✅ Backup verification passed")
    return True
```

## 🧪 Testing Environment Setup

### **Isolated Testing Environment**
```bash
# Create testing branch from feature branch
git checkout feature/codebase-reorganization
git checkout -b testing/phase-1-validation

# Run tests in isolation
python scripts/migration_test_framework.py

# If tests pass, merge back to feature branch
git checkout feature/codebase-reorganization
git merge testing/phase-1-validation
git branch -d testing/phase-1-validation
```

### **Test Data Backup**
```bash
# Backup test data before running tests
mkdir -p backups/test_data
cp -r test_data backups/test_data/test_data_$(date +%Y%m%d_%H%M%S)

# Restore test data if needed
cp -r backups/test_data/test_data_YYYYMMDD_HHMMSS/* test_data/
```

### **Virtual Environment Backup**
```bash
# Export current environment
pip freeze > requirements_backup_$(date +%Y%m%d).txt

# Create environment backup
conda env export > environment_backup_$(date +%Y%m%d).yml
```

## 🔄 Rollback Procedures

### **Immediate Rollback (< 5 minutes)**

#### **Git Rollback to Main**
```bash
# Quick rollback to main branch
git stash  # Save current work
git checkout main
git pull origin main

# Verify applications work
python scripts/launch-task-creator.py
python scripts/launch-project-launcher.py
python scripts/launch-review-app.py
```

#### **Database Rollback**
```bash
# Restore database from latest backup
rm -rf data/json_db
cp -r backups/database/json_db_backup_LATEST data/json_db

# Verify database integrity
python -c "from montu.shared.json_database import JSONDatabase; db = JSONDatabase(); print(db.get_stats())"
```

### **Partial Rollback (Specific Components)**

#### **Rollback Specific Files**
```bash
# Rollback specific core module
git checkout main -- src/montu/shared/path_builder.py

# Test specific functionality
python test_task_mapping_simple.py
```

#### **Rollback Database Collections**
```python
def rollback_collection(collection_name: str, backup_path: Path):
    """Rollback specific database collection."""
    import json
    from pathlib import Path
    
    # Load from backup
    backup_file = backup_path / f"{collection_name}.json"
    current_file = Path("data/json_db") / f"{collection_name}.json"
    
    if backup_file.exists():
        shutil.copy2(backup_file, current_file)
        print(f"✅ Rolled back {collection_name}")
    else:
        print(f"❌ Backup not found for {collection_name}")
```

### **Complete System Rollback (Full Restoration)**

#### **Full Git Rollback**
```bash
# Complete rollback to main branch
git checkout main
git reset --hard origin/main
git clean -fd  # Remove untracked files

# Verify clean state
git status
```

#### **Full Database Restoration**
```bash
# Restore complete database from backup
rm -rf data/json_db
cp -r backups/database/json_db_backup_BEFORE_MIGRATION data/json_db

# Restore test data
rm -rf test_data
cp -r backups/test_data/test_data_BEFORE_MIGRATION test_data
```

#### **Environment Restoration**
```bash
# Restore Python environment
pip install -r requirements_backup_YYYYMMDD.txt

# Or restore conda environment
conda env create -f environment_backup_YYYYMMDD.yml
```

## 🚨 Emergency Procedures

### **Emergency Rollback Triggers**
- **Critical functionality broken** for > 2 hours
- **Data corruption** detected in database
- **Multiple test failures** after migration step
- **Performance degradation** > 50%
- **Import errors** preventing application launch

### **Emergency Contact Protocol**
1. **Technical Lead**: Immediate notification
2. **Project Manager**: Status update within 1 hour
3. **Team**: Notification via team channel
4. **Stakeholders**: Update if rollback affects deliverables

### **Emergency Rollback Script**
```bash
#!/bin/bash
# Emergency rollback script - USE ONLY IN EMERGENCIES

echo "🚨 EMERGENCY ROLLBACK INITIATED"
echo "This will restore the system to the last known good state"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" = "yes" ]; then
    echo "🔄 Rolling back to main branch..."
    git stash
    git checkout main
    git reset --hard origin/main
    
    echo "🔄 Restoring database..."
    rm -rf data/json_db
    cp -r backups/database/json_db_backup_BEFORE_MIGRATION data/json_db
    
    echo "🧪 Testing system..."
    python test_task_mapping_simple.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Emergency rollback completed successfully"
    else
        echo "❌ Emergency rollback failed - manual intervention required"
    fi
else
    echo "❌ Emergency rollback cancelled"
fi
```

## 📋 Backup Checklist

### **Pre-Migration Checklist**
- [ ] Git repository backed up to remote
- [ ] Main branch protected from direct pushes
- [ ] Feature branch created and pushed
- [ ] JSON database backed up with timestamp
- [ ] Test data backed up
- [ ] Python environment exported
- [ ] All tests passing on main branch
- [ ] Team notified of migration start

### **During Migration Checklist**
- [ ] Commit frequently with descriptive messages
- [ ] Push to remote after each major milestone
- [ ] Run migration test framework after each phase
- [ ] Create database backup after each phase
- [ ] Document any issues or deviations
- [ ] Test rollback procedures periodically

### **Post-Migration Checklist**
- [ ] All tests passing on feature branch
- [ ] Performance benchmarks met
- [ ] Database integrity verified
- [ ] Applications launch successfully
- [ ] Documentation updated
- [ ] Team trained on new structure
- [ ] Rollback procedures tested and documented

## 🎯 Success Metrics

### **Backup Success Criteria**
- **Recovery Time**: < 5 minutes for immediate rollback
- **Data Integrity**: 100% data preservation
- **System Availability**: < 1 hour downtime maximum
- **Test Coverage**: All critical functionality tested post-rollback

### **Risk Mitigation**
- **Multiple Backup Locations**: Local + Remote + Cloud
- **Automated Verification**: Backup integrity checks
- **Regular Testing**: Monthly rollback procedure testing
- **Documentation**: Clear, step-by-step procedures
- **Team Training**: All team members know rollback procedures

## 📞 Support Contacts

**Emergency Rollback**: Technical Lead  
**Backup Issues**: System Administrator  
**Database Problems**: Database Administrator  
**Process Questions**: Project Manager  

**Escalation Path**: Technical Lead → Project Manager → Department Head
