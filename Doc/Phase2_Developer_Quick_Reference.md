# Phase 2 Developer Quick Reference Guide

**Target Audience**: GUI developers starting Project Launcher implementation  
**Prerequisites**: Phase 1 infrastructure completed and validated  
**Date**: August 3, 2025  

---

## 🚀 Quick Start for Phase 2 Development

### Essential Setup Commands
```bash
# 1. Start backend infrastructure
python3 scripts/docker-manager.py start

# 2. Verify path generation system
python3 scripts/test-path-generation.py

# 3. Check database status
python3 -c "from src.montu.shared.json_database import JSONDatabase; db = JSONDatabase(); print(db.get_stats())"
```

### Import Statements for GUI Development
```python
# Core database and path generation (NEW LOCATIONS)
from montu.core.data.database import JSONDatabase
from montu.core.path.builder import PathBuilder

# Task Creator components (for reference)
from montu.shared.parsers.csv_parser import CSVParser, TaskRecord
```

---

## 🗄️ Database Operations Cheat Sheet

### Basic Database Operations
```python
# Initialize database
db = JSONDatabase()

# Query tasks
all_tasks = db.find('tasks', {})
swa_tasks = db.find('tasks', {'project': 'SWA'})
lighting_tasks = db.find('tasks', {'task': 'lighting'})
in_progress = db.find('tasks', {'status': 'in_progress'})

# Get specific task
task = db.find_one('tasks', {'_id': 'ep00_sq0020_sh0090_lighting'})

# Update task status
db.update_one('tasks', {'_id': task_id}, {'$set': {'status': 'in_progress'}})

# Get database statistics
stats = db.get_stats()
```

### Path Generation Operations
```python
# Generate all paths for a task
paths = db.generate_task_paths('ep00_sq0020_sh0090_lighting', '003', 'maya_scene')

# Result structure:
{
    'working_file_path': 'V:/SWA/all/scene/Ep00/sq0020/SH0090/lighting/version/...',
    'render_output_path': 'W:/SWA/all/scene/Ep00/sq0020/SH0090/lighting/version/v003/',
    'media_file_path': 'J:/SWA/all/scene/Ep00/sq0020/SH0090/lighting/version/v003/media/',
    'filename': 'Ep00_sq0020_SH0090_lighting_master_v003.ma',
    'sequence_clean': 'sq0020',
    'shot_clean': 'SH0090'
}

# Update task with generated paths
success = db.update_task_with_paths('ep00_sq0020_sh0090_lighting', '003', 'maya_scene')
```

### Project Configuration Access
```python
# Get project configuration
config = db.get_project_config('SWA')

# Validate project configuration
validation = db.validate_project_config('SWA')
if validation['valid']:
    print("Configuration is valid")
else:
    print("Errors:", validation['errors'])

# Get PathBuilder for direct use
path_builder = db.get_path_builder('SWA')
```

---

## 🛠️ Path Generation Examples

### Common Path Generation Patterns
```python
# Working file paths (for opening in DCC applications)
working_path = db.generate_task_paths(task_id, '003', 'maya_scene')['working_file_path']
# Result: V:/SWA/all/scene/Ep00/sq0020/SH0090/lighting/version/Ep00_sq0020_SH0090_lighting_master_v003.ma

# Render output directories (for render farm)
render_path = db.generate_task_paths(task_id, '015')['render_output_path']
# Result: W:/SWA/all/scene/Ep00/sq0010/SH0020/comp/version/v015/

# Media files (for review and playback)
media_path = db.generate_task_paths(task_id, '003')['media_file_path']
# Result: J:/SWA/all/scene/Ep00/sq0020/SH0090/lighting/version/v003/media/
```

### File Type Specific Generation
```python
# Maya scene files
maya_paths = db.generate_task_paths(task_id, '003', 'maya_scene')
# Filename: Ep00_sq0020_SH0090_lighting_master_v003.ma

# Nuke scripts
nuke_paths = db.generate_task_paths(task_id, '003', 'nuke_script')
# Filename: Ep00_sq0020_SH0090_comp_master_v003.nk

# Houdini scenes
houdini_paths = db.generate_task_paths(task_id, '003', 'houdini_scene')
# Filename: Ep00_sq0020_SH0090_fx_master_v003.hip
```

---

## 📊 Task Data Structure Reference

### Complete TaskRecord Fields
```python
# Core identification
task_id: str                    # "ep00_sq0020_sh0090_lighting"
project: str                    # "SWA"
type: str                       # "shot" or "asset"
episode: str                    # "Ep00"
sequence: str                   # "SWA_Ep00_sq0020"
shot: str                       # "SWA_Ep00_SH0090"
task: str                       # "lighting"

# Assignment and status
artist: str                     # "John Doe"
status: str                     # "not_started", "in_progress", "completed"
milestone: str                  # "not_started", "single_frame", "low_quality", etc.
priority: str                   # "low", "medium", "high", "urgent"

# Timing and scope
frame_range: Dict[str, int]     # {"start": 1001, "end": 1120}
estimated_duration_hours: float # 24.0
actual_time_logged: float      # 0.0
start_time: Optional[str]       # ISO datetime string
deadline: Optional[str]         # ISO datetime string

# Path generation fields (populated automatically)
current_version: str            # "v001"
published_version: str          # "v000"
file_extension: str             # ".ma"
working_file_path: str          # Full working file path
render_output_path: str         # Render output directory
filename: str                   # Generated filename
sequence_clean: str             # "sq0020"
shot_clean: str                 # "SH0090"
episode_clean: str              # "Ep00"
```

### Task Status Values
```python
STATUS_OPTIONS = [
    "not_started",
    "in_progress", 
    "completed",
    "on_hold",
    "cancelled"
]

MILESTONE_OPTIONS = [
    "not_started",
    "single_frame",
    "low_quality", 
    "final_render",
    "final_comp",
    "approved"
]

PRIORITY_OPTIONS = [
    "low",
    "medium",
    "high", 
    "urgent"
]
```

---

## 🎨 GUI Integration Patterns

### Task List Display Pattern
```python
def load_tasks_for_display():
    """Load tasks with path information for GUI display"""
    db = JSONDatabase()
    tasks = db.find('tasks', {'project': 'SWA'})
    
    # Enhance tasks with path information if needed
    for task in tasks:
        if not task.get('working_file_path'):
            # Generate paths for tasks that don't have them
            db.update_task_with_paths(task['_id'], task.get('current_version', '001'))
    
    return tasks

def format_task_for_display(task):
    """Format task data for GUI display"""
    return {
        'id': task['_id'],
        'name': f"{task['shot']} - {task['task']}",
        'status': task['status'].replace('_', ' ').title(),
        'artist': task['artist'],
        'priority': task['priority'].title(),
        'working_file': task.get('working_file_path', 'Not generated'),
        'render_output': task.get('render_output_path', 'Not generated')
    }
```

### Task Status Update Pattern
```python
def update_task_status(task_id, new_status, artist=None):
    """Update task status with optional artist assignment"""
    db = JSONDatabase()
    
    update_data = {'status': new_status}
    if artist:
        update_data['artist'] = artist
    
    success = db.update_one('tasks', {'_id': task_id}, {'$set': update_data})
    
    if success:
        # Optionally regenerate paths if version changed
        task = db.find_one('tasks', {'_id': task_id})
        if task and not task.get('working_file_path'):
            db.update_task_with_paths(task_id)
    
    return success
```

### File Path Operations Pattern
```python
def open_working_file(task_id, version=None):
    """Generate working file path and prepare for DCC launch"""
    db = JSONDatabase()
    task = db.find_one('tasks', {'_id': task_id})
    
    if not task:
        return None
    
    # Use specified version or current version
    version = version or task.get('current_version', '001').lstrip('v')
    
    # Determine file type based on task
    file_type_map = {
        'lighting': 'maya_scene',
        'composite': 'nuke_script', 
        'comp': 'nuke_script',
        'fx': 'houdini_scene'
    }
    file_type = file_type_map.get(task['task'].lower(), 'maya_scene')
    
    # Generate path
    paths = db.generate_task_paths(task_id, version, file_type)
    
    return {
        'working_file_path': paths['working_file_path'],
        'filename': paths['filename'],
        'file_type': file_type,
        'dcc_application': file_type.split('_')[0]  # 'maya', 'nuke', 'houdini'
    }
```

---

## 🔧 Configuration and Customization

### Adding New Projects
```python
def add_new_project(project_id, project_name, drive_config):
    """Add a new project configuration"""
    db = JSONDatabase()
    
    # Use SWA as template and modify
    swa_config = db.get_project_config('SWA')
    new_config = swa_config.copy()
    
    new_config['_id'] = project_id
    new_config['name'] = project_name
    new_config['drive_mapping'] = drive_config
    
    # Insert new configuration
    config_id = db.insert_one('project_configs', new_config)
    
    # Validate the new configuration
    validation = db.validate_project_config(project_id)
    
    return validation['valid'], validation.get('errors', [])
```

### Custom Path Templates
```python
def update_project_templates(project_id, new_templates):
    """Update path templates for a project"""
    db = JSONDatabase()
    
    # Validate templates first
    path_builder = db.get_path_builder(project_id)
    errors = []
    
    for template_name, template in new_templates.items():
        try:
            variables = path_builder.validate_path_template(template)
            # Check if all required variables are available
            # (implementation depends on specific requirements)
        except Exception as e:
            errors.append(f"Template {template_name}: {str(e)}")
    
    if not errors:
        # Update configuration
        db.update_one('project_configs', 
                     {'_id': project_id}, 
                     {'$set': {'templates': new_templates}})
        
        # Clear cached PathBuilder to force reload
        if project_id in db._path_builders:
            del db._path_builders[project_id]
    
    return len(errors) == 0, errors
```

---

## 🐛 Common Issues and Solutions

### Issue: Path Generation Fails
```python
# Check project configuration
validation = db.validate_project_config('SWA')
if not validation['valid']:
    print("Configuration errors:", validation['errors'])

# Check task data completeness
task = db.find_one('tasks', {'_id': task_id})
required_fields = ['project', 'episode', 'sequence', 'shot', 'task']
missing = [field for field in required_fields if not task.get(field)]
if missing:
    print("Missing task fields:", missing)
```

### Issue: Database Connection Problems
```python
# Check database status
try:
    db = JSONDatabase()
    stats = db.get_stats()
    print("Database OK:", stats)
except Exception as e:
    print("Database error:", e)
```

### Issue: Template Variable Errors
```python
# Debug template variables
path_builder = db.get_path_builder('SWA')
task_data = {'project': 'SWA', 'episode': 'Ep00', ...}

try:
    result = path_builder.generate_all_paths(task_data, '003', 'maya_scene')
    print("Path generation successful")
except Exception as e:
    print("Template error:", e)
    # Check which variables are missing
    template = path_builder.config['templates']['working_file']
    variables = path_builder.validate_path_template(template)
    print("Required variables:", variables)
```

---

## 📚 Additional Resources

### Testing and Validation
```bash
# Run comprehensive path generation tests
python3 scripts/test-path-generation.py

# Test CSV conversion (for reference)
python3 scripts/convert-csv-to-json.py

# Check Docker services
python3 scripts/docker-manager.py status
```

### File Locations
- **Database Files**: `data/json_db/`
- **Project Configs**: `data/json_db/project_configs.json`
- **Task Data**: `data/json_db/tasks.json`
- **Test Scripts**: `scripts/`
- **Core Modules**: `src/montu/shared/`

### Key Constants
```python
# File extensions by task type
TASK_EXTENSIONS = {
    'lighting': '.ma',
    'composite': '.nk',
    'comp': '.nk', 
    'modeling': '.ma',
    'rigging': '.ma',
    'animation': '.ma',
    'fx': '.hip',
    'lookdev': '.ma',
    'layout': '.ma'
}

# Default version format
DEFAULT_VERSION = "v001"
VERSION_PADDING = 3

# Drive mappings (Windows)
WINDOWS_DRIVES = {
    'working_files': 'V:',
    'render_outputs': 'W:',
    'media_files': 'J:'
}
```

---

## 🆕 Ra: Task Creator Enhanced Features (NEW)

### ✅ **Enhanced Project Management**
- **Complete Project Creation**: Comprehensive project configuration with media settings, templates, and validation
- **Media Format Configuration**: Resolution settings (4K UHD, 4K DCI, 2K DCI, HD 1080p, HD 720p, Custom), format selection (EXR, MOV, MP4, MXF, TIFF, DPX, JPEG, PNG), and frame rate management (23.976-60 fps)
- **Template Customization**: Editable filename patterns and path templates with real-time validation and preview functionality
- **Project Editing System**: Complete project modification with pre-populated forms, change tracking, and validation
- **Project Archival System**: Archive/unarchive projects with system-wide filtering and visual indicators
- **Enhanced UI**: Project Management tab with context menus, selection handling, and detailed project views

### Enhanced Database Operations
```python
# Get active (non-archived) projects
active_projects = db.get_active_projects()

# Archive project
archive_data = {
    'archived': True,
    'archived_at': datetime.now().isoformat(),
    'archived_by': 'Application Name'
}
db.update_one('project_configs', {'_id': project_id}, {'$set': archive_data})

# Enhanced project configuration with media settings
project_config = {
    # ... existing fields ...
    "media_configuration": {
        "final_delivery_resolution": {"width": 4096, "height": 2160, "name": "4K DCI"},
        "daily_review_resolution": {"width": 1920, "height": 1080, "name": "HD 1080p"},
        "final_delivery_formats": ["exr", "mov", "dpx"],
        "daily_review_formats": ["mov", "jpeg"],
        "default_frame_rate": 24
    },
    "archived": False
}
```

### Enhanced File Structure
```
src/montu/task_creator/gui/
├── main_window.py                    # Enhanced with editing and archival
├── project_creation_dialog.py       # Enhanced with media configuration
├── project_edit_dialog.py          # NEW: Project editing dialog
└── ...
```

### Integration Notes for Phase 2
- **Archive Filtering**: Use `db.get_active_projects()` instead of `db.find('project_configs')` to exclude archived projects
- **Media Configuration**: Access media settings via `project_config['media_configuration']` for resolution and format information
- **Template Validation**: Enhanced projects may have custom filename patterns and path templates
- **Project Editing**: Projects can be modified after creation (except Project ID)

---

**Quick Reference Status**: ✅ READY FOR PHASE 2 DEVELOPMENT
**Last Updated**: January 15, 2025 (Enhanced Features Added)
**Next Phase**: Project Launcher GUI Implementation with Enhanced Project Support
