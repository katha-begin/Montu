# Montu Manager - Product Requirements Document (v3.0)

**Status**: ✅ **Production Ready** | **Phase**: 1 Complete, Phase 2 Planning | **Date**: August 15, 2025

## 🌍 Product Vision

Montu Manager is a **production-ready** DCC-agnostic file, task, and media management ecosystem consisting of four integrated applications for VFX/Animation studios, freelancers, and vendor teams. The system provides comprehensive version control, project management, and media review capabilities with professional-grade performance and reliability.

**Current Status**: Phase 1 complete with all core applications functional and tested. Ready for production deployment.

---

## 🏗️ Application Architecture

**Four Integrated Applications** (3 Complete, 1 in Phase 2):

### 1. **Task Creator (Ra)** ✅ **COMPLETE**
**Status**: Production ready with comprehensive features
**Purpose**: Project lifecycle management and bulk task creation
**Key Features**:
- Project creation, editing, and archiving
- CSV import with data validation
- Template customization and path generation
- Media configuration management
- Manual task creation with scrollable UI

### 2. **Project Launcher** ✅ **COMPLETE**
**Status**: Production ready with version control
**Purpose**: Central project management and file operations
**Key Features**:
- 500+ task support with advanced filtering
- Integrated file browser and operations
- Complete version management system
- Multi-project navigation

### 3. **Review Application** ✅ **COMPLETE**
**Status**: Production ready with professional media player
**Purpose**: Media review and approval workflows
**Key Features**:
- OpenRV media player integration
- Advanced filtering (episode/sequence/shot/artist/status)
- Collapsible annotation panels
- Complete approval workflow

### 4. **DCC Integration Suite** 🔄 **PHASE 2**
**Status**: Planned for Phase 2 development
**Purpose**: In-application workflows for artists
**Planned Features**: Maya/Nuke plugins, save/load/publish workflows

---

## 🛠️ Core Features (Shared Across Applications)

### File & Version Management

* Save, load, and auto-increment versioned DCC files
* Lock and tag versions as "published"
* Attach artist and supervisor notes per version

### Task-Based Workflow

* Centralized task tracking (e.g. lighting, comp, FX)
* Milestone system (e.g. single\_frame → final\_comp)
* Priority setting, deadline, and time tracking

### Project Configuration

* **Enhanced Project Management**: Complete project lifecycle with creation, editing, and archival
* **Media Configuration**: Resolution settings, format selection, and frame rate management
* **Template Customization**: Configurable filename patterns and path templates
* **Archive System**: Project archival with system-wide filtering and restoration
* **Database-driven**: All configurations stored in centralized database
* **Platform Support**: Output roots configurable per platform (Windows/Linux)
* **Validation**: Real-time validation for all configuration parameters

### Media & Review System

* Track multiple media files per version (e.g., playblast, AOVs)
* Mark one media file as "review selected"
* Support internal vs client version mapping

### Application Integration

* **Project Launcher**: PySide6 desktop application with project selection dropdown, task/shot navigation, version display, and workflow controls
* **Task Creator**: CSV import interface with validation and batch processing
* **DCC Integration**: Plugin system for Maya, Nuke, and other DCCs with embedded UI panels
* **Review Application**: Dedicated media browser with playback and annotation tools
* **CLI Access**: Command-line interface available across all applications for automation

### Cross-Platform Support

* Windows & Linux compatible
* Configurable per platform path roots

---

## 🛋️ User Personas

### 🌟 RIN – Junior Artist

* Wants fast onboarding with minimal training
* Needs auto-versioning, quick file save/load
* Should be protected from breaking naming rules

### 🧑‍💼 KEN – Pipeline TD

* Wants folder structure to match any client
* Needs centralized task tracking and config management
* Prefers single config source of truth in database

### 👩‍💼 MAYA – Supervisor

* Needs clear visibility into publish history
* Wants ability to leave review notes per version
* Filters priority shots for daily tracking

---

## 🌐 Architecture Overview

### Application-Specific Architecture

#### **Project Launcher** (Standalone)
* PyInstaller-packaged PySide6 desktop application
* Direct MongoDB connection for project/task management
* Cross-platform file operations and path handling
* Central hub for launching other applications

#### **Task Creator** (Import Tool)
* Lightweight Python application with CSV processing
* Database validation and batch insertion capabilities
* Error reporting and data integrity checking
* Integration with Project Launcher for immediate task visibility

#### **DCC Integration Suite** (Plugins)
* Maya: MEL/Python plugin with shelf tools and embedded UI
* Nuke: Python plugin with menu integration and panels
* Extensible architecture for additional DCCs (Houdini, Blender)
* Shared core library for consistent functionality

#### **Review Application** (Media Browser)
* PySide6 application optimized for media playback
* Integration with media_records database collection
* Annotation and approval workflow tools
* Client-facing interface capabilities

### Shared Backend Infrastructure

* **MongoDB**: Centralized database (local or cloud) shared by all applications
* **FastAPI** (future): RESTful APIs for web interface and external integrations
* **File System**: Shared project structure and media storage
* **Configuration**: Unified project templates and settings across all applications

---

## 📊 Database Collections (MongoDB)

### `tasks`

```json
{
  "_id": "ep01_seq0010_sh0010_lighting",
  "project": "SWA",
  "type": "shot",
  "episode": "EP01",
  "sequence": "SEQ0010",
  "shot": "SH0010",
  "task": "lighting",
  "artist": "Pun",
  "status": "in_progress",
  "milestone": "low_quality",
  "milestone_note": "Needs rim fill",
  "frame_range": { "start": 1001, "end": 1050 },
  "priority": "high",
  "start_time": "2025-08-01T10:00:00",
  "deadline": "2025-08-05T18:00:00",
  "actual_time_logged": 14.25,
  "client_submission_history": [
    {
      "client_version": "v001",
      "internal_version": "v010",
      "submitted_on": "2025-08-03T14:32:00",
      "notes": "First client render"
    }
  ],
  "versions": [
    {
      "version": "v010",
      "path": "shots/EP01/SEQ0010/SH0010/lighting/v010/scene.ma",
      "author": "Pun",
      "date": "2025-08-03",
      "is_published": true,
      "is_locked": true,
      "artist_note": "Final bounce test",
      "review_note": "Approved by supervisor"
    }
  ]
}
```

### `project_configs`

```json
{
  "_id": "SWA",
  "name": "Sky Wars Anthology",
  "base_path": "/mnt/projects/SWA",
  "output_windows_root": "W:/SWA",
  "output_linux_root": "/mnt/projects/SWA",
  "media_root": {
    "windows": "J:/SWA",
    "linux": "/mnt/media/SWA"
  },
  "shot_template": "shots/{episode}/{sequence}/{shot}/{task}/work/v{version}",
  "asset_template": "assets/{type}/{asset}/{task}/work/v{version}",
  "submission_template": "deliveries/{client}/{episode}/{sequence}/{shot}/{task}/v{client_version}",
  "milestones": [
    "not_started", "single_frame", "low_quality", "final_render", "final_comp", "approved"
  ],
  "task_types": ["model", "lookdev", "lighting", "composite", "fx"],
  "client_version_reset": true,
  "default_priority": "medium",
  "frame_padding": 4
}
```

### `media_records`

```json
{
  "_id": "media_000123",
  "linked_task_id": "ep01_seq0010_sh0010_lighting",
  "linked_version": "v010",
  "author": "Pun",
  "file_name": "v010_preview.mov",
  "media_type": "mov",
  "resolution": "HD",
  "path": "shots/EP01/SEQ0010/SH0010/lighting/v010/v010_preview.mov",
  "review_selected": true,
  "comment": "Bounce pass for lead review",
  "upload_time": "2025-08-03T14:20:00"
}
```

---

## 🧰 User Journeys: Application-Specific Workflows

### **Project Launcher Workflow** (Primary Desktop Application)
1. Launch Project Launcher standalone application
2. Select project from dropdown → Navigate to task/shot
3. View version history and current status
4. Open working files in appropriate DCC or standalone editor
5. Monitor task progress and deadlines
6. Access other Montu applications from central hub

### **Task Creator Workflow** (Pipeline Setup)
1. Pipeline TD exports task list from production tracking (CSV format)
2. Launch Task Creator application
3. Import CSV file with data validation
4. Review parsed tasks and resolve any conflicts
5. Batch create tasks in database
6. Verify task creation in Project Launcher

### **DCC Integration Workflow** (Artist Daily Work)
1. Open Maya/Nuke with Montu plugin loaded
2. Use Montu shelf/menu to select project and task
3. Load most recent version or create new one
4. Work and save to create new version (auto v002 → v003...)
5. Add artist note at save time
6. Upload media files (playblasts, renders) through DCC interface
7. Submit final to supervisor (lock version, publish flag)

### **Review Application Workflow** (Supervisor/Client Review)
1. Launch Review Application
2. Filter tasks by priority, status, or deadline
3. View submitted media with version comparison
4. Add review notes and annotations
5. Approve or request changes
6. If approved, map to client version (v010 → v001) for delivery
7. Generate delivery packages using submission templates

---

## 🌐 Deployment Plan

### Initial

* Local install (via PyInstaller)
* Config pulled from shared DB or mounted volume

### Network

* Auto-updater checks latest version from manifest file
* Builds deployed per environment:

  * `dist/dev/`, `dist/staging/`, `dist/prod/`

### Cloud (Future)

* MongoDB Atlas or private FastAPI backend
* Optionally expose limited frontend for task status + media preview

---

## 📐 Roadmap: Application-Focused Development

### **Phase 1: Foundation & Backend Setup**
* Project structure and Docker configuration
* MongoDB schema design and documentation
* Cross-platform path handling
* Database connection architecture

### **Phase 2: Core Application Development**
* **Project Launcher**: PySide6 GUI mockup with JSON mock database
* **Task Creator**: CSV import tool with validation
* Database design documentation and CRUD operations
* GUI-database connection testing and validation

### **Phase 3: DCC Integration Implementation**
* **DCC Integration Suite**: Maya and Nuke plugins
* DCC-agnostic interface architecture
* File operations and version management within DCCs
* Integration testing across applications

### **Phase 4: Review & Advanced Features**
* **Review Application**: Media browser and approval workflows
* Client version mapping and delivery pipeline
* PyInstaller packaging for all applications
* Comprehensive testing suite and documentation

### **Application Integration Milestones**
* **Milestone 1**: Project Launcher + Task Creator working with JSON mock database
* **Milestone 2**: MongoDB integration and DCC plugins functional
* **Milestone 3**: Review Application integrated with complete workflow
* **Milestone 4**: Full ecosystem deployment with auto-update system

---

## 🚀 You're Ready To:

* Save/load cleanly versioned files
* Match folder structure per project config
* Track milestone and time per task
* Upload and select media per version
* Sync review notes and submission history
* Package clean delivery for client per version mapping
