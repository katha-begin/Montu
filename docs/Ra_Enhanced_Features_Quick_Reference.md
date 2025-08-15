# Ra: Task Creator - Enhanced Features Quick Reference

## 🚀 Quick Start

### **Launch Application**
```bash
python3 scripts/launch-task-creator.py
```

### **Access Enhanced Features**
1. **Project Management Tab** - First tab in the application
2. **Create New Project** - Button or Ctrl+N
3. **Edit Project** - Double-click project or Edit button
4. **Archive Project** - Select project and click Archive button

## 📋 Project Creation Checklist

### **Required Sections**
- [ ] **Basic Info**: Name, ID, Description
- [ ] **Project Type**: Episode-based or Non-episode
- [ ] **Task Types**: At least one task type selected
- [ ] **Timeline**: Start date before end date
- [ ] **Media Formats**: At least one format for final delivery and daily review

### **Optional Sections**
- [ ] **Color Pipeline**: OCIO config path and colorspaces
- [ ] **Drive Mappings**: Custom drive letter assignments
- [ ] **Filename Patterns**: Custom patterns (defaults provided)
- [ ] **Path Templates**: Custom templates (defaults provided)
- [ ] **Budget**: Manday allocation

## 🎛️ Media Configuration Quick Setup

### **Standard Configurations**

#### **Feature Film**
- **Final Delivery**: 4K DCI (4096x2160), EXR + MOV, 24fps
- **Daily Review**: HD 1080p (1920x1080), MOV + JPEG, 24fps

#### **TV/Streaming**
- **Final Delivery**: 4K UHD (3840x2160), EXR + MOV, 23.976fps
- **Daily Review**: HD 1080p (1920x1080), MOV + JPEG, 23.976fps

#### **Commercial/Short Form**
- **Final Delivery**: HD 1080p (1920x1080), MOV + MP4, 30fps
- **Daily Review**: HD 1080p (1920x1080), MOV + JPEG, 30fps

### **Format Recommendations**
- **Final Delivery**: EXR (for VFX), MOV (for editorial), DPX (for film)
- **Daily Review**: MOV (for playback), JPEG (for stills)

## 🔧 Template Variables Reference

### **Essential Variables (Required)**
- `{project}` - Project ID
- `{task}` - Task type (lighting, comp, etc.)
- `{version}` - Version number (001, 002, etc.)
- `{drive_*}` - Drive mappings (drive_working, drive_render, etc.)

### **Common Variables**
- `{episode}` - Episode identifier (auto-removed for non-episode projects)
- `{sequence_clean}` - Cleaned sequence name
- `{shot_clean}` - Cleaned shot name
- `{version_dir}` - Version directory name
- `{middle_path}` - Project middle path segment
- `{frame}` - Frame number for sequences
- `{ext}` - File extension
- `{client}` - Client name
- `{client_version}` - Client version number

### **Example Patterns**
```
Maya Scene: {episode}_{sequence_clean}_{shot_clean}_{task}_master_v{version}.ma
Render Sequence: {episode}_{sequence_clean}_{shot_clean}_{task}_v{version}.{frame}.{ext}
Working File Path: {drive_working}/{project}/{middle_path}/{episode}/{sequence_clean}/{shot_clean}/{task}/{version_dir}/{filename}
```

## ✏️ Project Editing Quick Actions

### **Edit Access**
- **Double-click** project row
- **Select + Edit button**
- **Right-click > Edit Project**

### **Common Edits**
1. **Update Timeline**: Extend project end date
2. **Add Task Types**: Include new pipeline stages
3. **Change Media Config**: Update resolution or formats
4. **Modify Patterns**: Adjust filename conventions
5. **Update Budget**: Revise manday allocation

### **Edit Validation**
- ⚠️ **Red text** = Missing required variables
- ✅ **Green indicators** = Valid configuration
- 🔄 **Reset to Original** = Undo all changes

## 📦 Archive Management Quick Guide

### **Archive Project**
1. Select project in Project Management tab
2. Click "Archive Selected Project"
3. Confirm in dialog (explains impact)
4. Project hidden from all applications

### **View Archived Projects**
1. Enable "Show Archived Projects" checkbox
2. Archived projects appear grayed out
3. Status column shows "Archived [date]"

### **Unarchive Project**
1. Enable "Show Archived Projects"
2. Select archived project
3. Click "Unarchive Selected Project"
4. Confirm restoration

### **Archive Effects**
- ❌ **Hidden from**: Project dropdowns, task loading, media browsing
- ✅ **Preserved**: All project data, tasks, media records
- 🔄 **Reversible**: Full restoration with unarchive

## 🛠️ Troubleshooting Quick Fixes

### **Validation Errors**
| Error | Quick Fix |
|-------|-----------|
| "Missing required variables" | Add `{task}` and `{version}` to patterns |
| "At least one format required" | Select formats in media configuration |
| "OCIO config not found" | Browse for valid .ocio file or clear field |
| "End date before start date" | Adjust timeline dates |
| "Custom resolution invalid" | Use values between 1-8192 pixels |

### **Common Issues**
| Issue | Solution |
|-------|----------|
| Can't change Project ID | By design - IDs are read-only after creation |
| Archived projects visible | Disable "Show Archived Projects" toggle |
| Edit button disabled | Select a project first |
| Changes not saving | Check validation errors and database connection |
| Templates not updating | Use "Reset to Defaults" to restore patterns |

## 🎯 Best Practices

### **Project Creation**
1. **Use descriptive names** - "Sky Wars Season 2" not "SWS2"
2. **Verify auto-generated ID** - Check uniqueness and clarity
3. **Set realistic timeline** - Include buffer time for delays
4. **Choose appropriate media config** - Match delivery requirements
5. **Validate templates** - Use preview to check path generation

### **Project Editing**
1. **Coordinate changes** - Inform team before major modifications
2. **Test template changes** - Use preview before saving
3. **Document reasons** - Note why changes were made
4. **Backup considerations** - Major changes may affect existing tasks
5. **Validate after editing** - Ensure all fields are still valid

### **Archive Management**
1. **Archive completed projects** - Keep active list manageable
2. **Document before archiving** - Note completion status
3. **Regular cleanup** - Archive old projects periodically
4. **Team communication** - Inform team before archiving shared projects
5. **Preserve important data** - Ensure deliverables are backed up

## 📞 Quick Help

### **Keyboard Shortcuts**
- **Ctrl+N** - Create New Project
- **F5** - Refresh Projects List
- **Enter** - Edit Selected Project
- **Delete** - Archive Selected Project (with confirmation)
- **Ctrl+Z** - Undo (in edit dialogs)

### **UI Indicators**
- 🟢 **Green text** - Valid/successful operations
- 🔴 **Red text** - Errors or missing required fields
- 🟡 **Orange text** - Warnings or unsaved changes
- 🔘 **Grayed out** - Archived projects or disabled fields
- ⚠️ **Warning icons** - Validation issues

### **Context Menus**
- **Right-click project** - Edit, Archive, View Details
- **Right-click table header** - Sort and column options
- **Right-click form fields** - Copy, paste, select all

This quick reference covers the essential enhanced features of Ra: Task Creator. For detailed information, refer to the complete user guide and feature documentation.
