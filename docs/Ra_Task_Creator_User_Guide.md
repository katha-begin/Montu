# Ra: Task Creator - User Guide

## Quick Start Guide

### 1. **Launch the Application**
```bash
python scripts/launch-task-creator.py
```

### 2. **Create or Select a Project**
- **Create New Project**: Use the **Project Management** tab to create new project configurations
- **Select Existing Project**: Use the **Project** dropdown in the header to select your project
- The application will automatically load all tasks for the selected project
- Task summary statistics will appear next to the project selector

### 3. **View and Filter Tasks**
- Use the **Search** box to find specific tasks by ID, artist, or description
- Apply filters using the **Status**, **Task Type**, and **Artist** dropdowns
- Click **Clear Filters** to reset all filters

## Project Management

### **Creating New Projects**

Ra: Task Creator now includes comprehensive project creation capabilities:

#### **Access Project Creation**
- Navigate to the **Project Management** tab (first tab)
- Click **Create New Project** button
- Or use **File > Create New Project...** menu
- Or use **Ctrl+N** keyboard shortcut

#### **Project Creation Dialog**

The project creation dialog includes organized sections:

**1. Basic Project Information**
- **Project Name**: Full descriptive name (e.g., "Sky Wars Season 2")
- **Project ID**: Auto-generated abbreviation (e.g., "SWS2") with manual override
- **Description**: Brief project description

**2. Project Type Configuration**
- **Episode-based Project**: Full episode/sequence/shot hierarchy (like SWA)
- **Non-episode Project**: Simplified shot-based or asset-based structure

**3. Task Types Configuration**
- Customize available task types for the project
- Standard VFX defaults: modeling, rigging, animation, layout, lighting, comp, fx, lookdev
- Add custom task types or remove unused ones
- Minimum one task type required

**4. Timeline & Budget Configuration**
- **Project Timeline**: Start and end dates with calendar picker
- **Total Mandays**: Budget allocation for resource planning

**5. Color Pipeline Configuration**
- **OCIO Config Path**: Browse for .ocio configuration file
- **Working Colorspace**: Default ACEScg (ACES workflow)
- **Display Colorspace**: Default sRGB

**6. Drive Mappings & Path Configuration**
- **Working Files Drive**: Default V:
- **Render Outputs Drive**: Default W:
- **Media Files Drive**: Default E:
- **Cache Files Drive**: Default E:
- **Backup Files Drive**: Default E:

**7. Filename Patterns Configuration** *(NEW)*
- **Maya Scene**: `{episode}_{sequence_clean}_{shot_clean}_{task}_master_v{version}.ma`
- **Nuke Script**: `{episode}_{sequence_clean}_{shot_clean}_{task}_master_v{version}.nk`
- **Houdini Scene**: `{episode}_{sequence_clean}_{shot_clean}_{task}_master_v{version}.hip`
- **Blender Scene**: `{episode}_{sequence_clean}_{shot_clean}_{task}_master_v{version}.blend`
- **Render Sequence**: `{episode}_{sequence_clean}_{shot_clean}_{task}_v{version}.{frame}.{ext}`
- **Playblast**: `{episode}_{sequence_clean}_{shot_clean}_{task}_v{version}_playblast.mov`
- **Thumbnail**: `{episode}_{sequence_clean}_{shot_clean}_{task}_v{version}_thumb.jpg`
- **Real-time validation** ensures required variables (`{task}`, `{version}`) are present
- **Reset to Defaults** button restores SWA standard patterns

**8. Path Templates Configuration** *(NEW)*
- **Working File**: `{drive_working}/{project}/{middle_path}/{episode}/{sequence_clean}/{shot_clean}/{task}/{version_dir}/{filename}`
- **Render Output**: `{drive_render}/{project}/{middle_path}/{episode}/{sequence_clean}/{shot_clean}/{task}/{version_dir}/v{version}/`
- **Media File**: `{drive_media}/{project}/{middle_path}/{episode}/{sequence_clean}/{shot_clean}/{task}/{version_dir}/v{version}/media/`
- **Cache File**: `{drive_cache}/{project}/{middle_path}/{episode}/{sequence_clean}/{shot_clean}/{task}/cache/`
- **Submission**: `{drive_render}/{project}/deliveries/{client}/{episode}/{sequence_clean}/{shot_clean}/{task}/v{client_version}/`
- **Path Preview** functionality shows example generated paths
- **Auto-adjustment** for episode-based vs non-episode projects

**9. Media & Resolution Configuration** *(NEW)*
- **Final Delivery Resolution**: 4K UHD, 4K DCI, 2K DCI, HD 1080p, HD 720p, or Custom
- **Daily/Review Resolution**: Same options as final delivery
- **Final Delivery Formats**: EXR, MOV, MP4, MXF, TIFF, DPX (multi-selection)
- **Daily/Review Formats**: MOV, MP4, JPEG, PNG (multi-selection)
- **Frame Rate**: 23.976, 24, 25, 29.97, 30, 50, 59.94, 60 fps

#### **Project ID Generation**

Ra uses intelligent abbreviation logic:
- "Sky Wars Season 2" → "SWS2"
- "Avatar Water Scenes" → "AWS"
- "The Matrix Reloaded" → "TMR"

**Features:**
- Automatic generation from project name
- Manual override capability
- Uniqueness validation against existing projects
- Format constraints (alphanumeric, no spaces, max 20 characters)

#### **Project Templates**

All new projects use the SWA configuration as a base template:
- **Preserves Structure**: All configuration keys and nested objects maintained
- **Customizable Values**: All values can be modified during creation
- **PathBuilder Compatibility**: Full compatibility with existing path generation
- **Database Integration**: Seamless integration with existing JSON database

### **Managing Existing Projects**

The **Project Management** tab displays all existing projects:

**Project List Features:**
- **Project ID**: Unique identifier
- **Project Name**: Full descriptive name
- **Description**: Brief project description (truncated)
- **Task Types**: Available task types (first 3 shown)
- **Timeline**: Project start and end dates
- **Created**: Project creation timestamp

**Operations:**
- **Edit Selected Project**: Modify existing project configurations
- **Archive Selected Project**: Archive/unarchive projects to hide/show them
- **Refresh Projects**: Update project list from database
- **Show Archived Projects**: Toggle to display archived projects
- **Project Count**: Display total number of active projects (with archived count)

### **Enhanced Project Configuration**

#### **Media Format & Resolution Configuration**

**Final Delivery Resolution:**
- Predefined options: 4K UHD (3840x2160), 4K DCI (4096x2160), 2K DCI (2048x1080), HD 1080p (1920x1080), HD 720p (1280x720)
- Custom resolution support with width/height inputs (1-8192 pixels)

**Daily/Review Resolution:**
- Same resolution options as final delivery
- Typically set to HD 1080p for efficient review workflows

**Format Configuration:**
- **Final Delivery Formats**: EXR, MOV, MP4, MXF, TIFF, DPX (multi-selection)
- **Daily/Review Formats**: MOV, MP4, JPEG, PNG (multi-selection)
- **Frame Rate**: 23.976, 24, 25, 29.97, 30, 50, 59.94, 60 fps

#### **Filename Patterns Customization**

Customize filename patterns for different file types:
- **Maya Scene**: `{episode}_{sequence_clean}_{shot_clean}_{task}_master_v{version}.ma`
- **Nuke Script**: `{episode}_{sequence_clean}_{shot_clean}_{task}_master_v{version}.nk`
- **Houdini Scene**: `{episode}_{sequence_clean}_{shot_clean}_{task}_master_v{version}.hip`
- **Blender Scene**: `{episode}_{sequence_clean}_{shot_clean}_{task}_master_v{version}.blend`
- **Render Sequence**: `{episode}_{sequence_clean}_{shot_clean}_{task}_v{version}.{frame}.{ext}`
- **Playblast**: `{episode}_{sequence_clean}_{shot_clean}_{task}_v{version}_playblast.mov`
- **Thumbnail**: `{episode}_{sequence_clean}_{shot_clean}_{task}_v{version}_thumb.jpg`

**Validation:**
- Real-time validation ensures required variables (`{task}`, `{version}`) are present
- Warning indicators for missing essential variables
- "Reset to Defaults" button to restore standard patterns

#### **Path Templates Configuration**

Customize path templates for different file types:
- **Working File**: `{drive_working}/{project}/{middle_path}/{episode}/{sequence_clean}/{shot_clean}/{task}/{version_dir}/{filename}`
- **Render Output**: `{drive_render}/{project}/{middle_path}/{episode}/{sequence_clean}/{shot_clean}/{task}/{version_dir}/v{version}/`
- **Media File**: `{drive_media}/{project}/{middle_path}/{episode}/{sequence_clean}/{shot_clean}/{task}/{version_dir}/v{version}/media/`
- **Cache File**: `{drive_cache}/{project}/{middle_path}/{episode}/{sequence_clean}/{shot_clean}/{task}/cache/`
- **Submission**: `{drive_render}/{project}/deliveries/{client}/{episode}/{sequence_clean}/{shot_clean}/{task}/v{client_version}/`

**Features:**
- Automatic adjustment for episode-based vs non-episode projects
- Path preview functionality with sample data
- Validation for essential variables (`{project}`, `{task}`, `{drive_*}`)

### **Project Editing** *(NEW)*

#### **Editing Existing Projects**

Ra: Task Creator now provides comprehensive project editing capabilities for modifying existing project configurations:

**Access Project Editing:**
- **Double-click** any project row in the Project Management tab
- **Select project** and click "Edit Selected Project" button
- **Right-click** project and select "Edit Project" from context menu
- **Keyboard shortcut**: Select project and press Enter

**Edit Dialog Features:**
- **Pre-populated Forms**: All fields automatically loaded from existing project configuration
- **Read-only Project ID**: Project ID cannot be changed after creation (grayed out with tooltip)
- **Save Changes**: Updates project configuration with automatic timestamp
- **Reset to Original**: Restore all fields to their original values
- **Change Tracking**: Visual indicators show which fields have been modified
- **Comprehensive Validation**: Same validation rules as project creation
- **Confirmation Dialog**: Shows summary of changes before saving

**All Editable Sections:**
- **Basic Project Information**: Name, description
- **Task Types Configuration**: Add, remove, or modify task types
- **Timeline & Budget Settings**: Start/end dates, manday allocation
- **Color Pipeline Configuration**: OCIO config path, colorspaces
- **Drive Mappings**: All drive letter assignments
- **Filename Patterns**: All 7 filename pattern types with validation
- **Path Templates**: All 5 path template types with preview
- **Media Configuration**: Resolutions, formats, frame rates

**Edit Process:**
1. **Select Project**: Choose project from the Project Management tab
2. **Open Editor**: Use any of the access methods above
3. **Modify Settings**: Change any configuration except Project ID
4. **Validate**: Real-time validation ensures all changes are valid
5. **Preview Changes**: Review modification summary in confirmation dialog
6. **Save**: Apply changes with automatic timestamp update
7. **Refresh**: Project list and dropdown automatically update

**Edit Validation:**
- **Required Fields**: Ensures all mandatory fields are completed
- **Template Variables**: Validates filename patterns and path templates
- **Media Formats**: Ensures at least one format is selected for each category
- **Timeline Logic**: Validates that end date is after start date
- **OCIO Config**: Validates file existence if path is specified

### **Project Archival System** *(NEW)*

#### **Complete Archive Management**

Ra: Task Creator provides a comprehensive project archival system for managing project lifecycles:

**Archive Projects:**
- **Select Project**: Choose any active project from the Project Management tab
- **Archive Action**: Click "Archive Selected Project" button or use context menu
- **Confirmation Dialog**: Detailed explanation of archival impact and consequences
- **System Impact**: Archived projects are hidden from all Montu Manager applications
- **Metadata Recording**: Archive timestamp, user information, and reason automatically recorded

**Unarchive Projects:**
- **Show Archived**: Enable "Show Archived Projects" toggle checkbox
- **Select Archived Project**: Choose from grayed-out archived projects
- **Unarchive Action**: Click "Unarchive Selected Project" button
- **Confirmation Dialog**: Explains restoration process and system impact
- **Full Restoration**: Project becomes available in all applications again
- **Metadata Cleanup**: Archive-specific fields removed upon restoration

**Archive Status Indicators:**
- **Active Projects**: Green "Active" status with normal text color
- **Archived Projects**: Gray "Archived [date]" status with grayed-out text and archive icon
- **Project Count**: Shows "X active projects (Y archived)" format
- **Visual Distinction**: Archived projects clearly distinguished in table

**Archive Operations:**
- **Bulk Selection**: Select multiple projects for batch archival (future enhancement)
- **Archive Reason**: Optional reason field for archival tracking
- **Archive History**: Track all archive/unarchive operations with timestamps
- **Permission Control**: Archive operations can be restricted by user role (future enhancement)

#### **System-wide Archive Integration**

**Filtered Project Loading:**
- **Project Dropdown**: Excludes archived projects by default across all applications
- **Task Loading**: Queries automatically filter out tasks from archived projects
- **Media Browsing**: Review Application excludes media from archived projects
- **Path Generation**: PathBuilder Engine respects archive status
- **Database Queries**: All applications use `get_active_projects()` helper method

**Archive Database Schema:**
```json
{
  "archived": false,                    // Archive status (boolean)
  "archived_at": "2025-01-15T10:30:00", // Archive timestamp (ISO format)
  "archived_by": "Ra Task Creator",      // Archive source/user
  "archive_reason": "Project completed" // Optional reason (future)
}
```

**Archive Information Display:**
- **Archive Date**: Formatted display of when project was archived
- **Archive Source**: Shows which application/user performed the archival
- **Status Column**: Dedicated column in projects table for archive status
- **Context Menu**: Right-click options for archive/unarchive operations
- **Tooltip Information**: Hover details for archived projects

**Cross-Application Consistency:**
- **Project Launcher**: Respects archive status for project visibility
- **Review Application**: Filters archived projects from media browsing
- **DCC Integration**: Plugins exclude archived projects from project lists
- **Task Creator**: Archive filtering in all project-related operations

## Manual Task Creation *(NEW)*

### **Creating Individual Tasks**

Ra: Task Creator now includes comprehensive manual task creation capabilities for creating individual tasks:

#### **Access Manual Task Creation**
- **Create Task Button**: Prominent blue button in Project Management tab
- **Menu Access**: File > Create Task... (Ctrl+T keyboard shortcut)
- **Toolbar Access**: Create Task toolbar button
- **Context**: Available when active projects exist

#### **Task Type Selection**
- **Shot Tasks**: Traditional VFX workflow with episode/sequence/shot hierarchy
- **Asset Tasks**: Asset-based workflow with category/asset_name structure
- **Dynamic Forms**: Interface adapts based on selected task type
- **Real-time Preview**: Live preview of generated task ID

#### **Shot Task Creation** *(ENHANCED + NEW DROPDOWNS)*
- **Episode Dropdown**: Smart dropdown populated from existing project episodes + manual entry capability
- **Sequence Dropdown**: Smart dropdown populated from existing project sequences, filtered by episode + manual entry capability
- **Shot Field**: Shot identifier input (e.g., sh010, sh020)
- **Dynamic Filtering**: Sequence dropdown automatically filters based on selected episode
- **Multiple Task Types**: Select multiple task types simultaneously with multi-select interface
- **Custom Task Types**: Add custom task types (e.g., "previz", "techvis", "matchmove")
- **Frame Range**: Start and end frame inputs with validation
- **Task ID Pattern**: `{episode}_{sequence}_{shot}_{task_type}` for each selected task type
- **Batch Creation**: Creates separate task for each selected task type
- **Standard Fields**: Artist, status, milestone, priority, duration, notes

#### **Asset Task Creation** *(ENHANCED)*
- **Asset Categories**: Configurable categories (char, prop, veh, set, env, fx, matte)
- **Multiple Task Types**: Select multiple task types simultaneously with multi-select interface
- **Custom Task Types**: Add custom task types with validation and project storage
- **Asset Dependencies**: Track which assets this asset depends on
- **Asset Variants**: Support for costume changes, damage states, material variants
- **Task ID Pattern**: `asset_{category}_{asset_name}_{task_type}` for each selected task type
- **Batch Creation**: Creates separate task for each selected task type
- **No Frame Range**: Appropriate for asset-based workflows

#### **Advanced Features** *(ENHANCED)*
- **Multiple Task Type Selection**: Select and create multiple task types simultaneously
- **Custom Task Names**: Add custom task types (previz, techvis, matchmove, roto) with validation
- **Automatic Directory Creation**: Creates working, render, media, and cache directories automatically
- **Directory Preview**: Shows directory paths that will be created before task creation
- **Batch Creation**: Create all pipeline tasks for a shot/asset at once
- **Task Templating**: Copy settings from existing tasks
- **Dependency Management**: Add/remove asset dependencies with circular dependency prevention
- **Variant Tracking**: Structured metadata for asset variations
- **Real-time Validation**: Immediate feedback with duplicate detection
- **Progress Feedback**: Progress indicators during directory creation

#### **Enhanced Manual Task Creation Process** *(UPDATED)*
1. **Select Project**: Choose from active projects dropdown
2. **Choose Task Type**: Select Shot or Asset task type
3. **Fill Required Fields**: Complete all mandatory fields (marked with *)
4. **Select Multiple Task Types**: Choose multiple task types from multi-select lists
5. **Add Custom Task Types**: Enter custom task types (e.g., "previz", "techvis") if needed
6. **Configure Options**: Set artist, status, priority, duration, notes
7. **Preview Tasks**: Review all task IDs that will be created
8. **Preview Directories**: Review directory structure that will be created
9. **Create Tasks**: Multiple tasks created simultaneously with directories
10. **Automatic Integration**: All tasks appear immediately in Task Management tab

### **Enhanced Features Details** *(NEW)*

#### **Multiple Task Type Selection** *(ENHANCED UI)*
- **Expanded Selection Area**: Task type lists increased from 120px to 180-200px height
- **Multi-Select Lists**: Task types displayed as selectable lists with enhanced styling
- **Professional Styling**: Modern borders, hover effects, and visual feedback
- **Real-time Selection Count**: Shows "X selected" with dynamic color coding
- **Bulk Selection**: "Select All" and "Select None" buttons with enhanced styling
- **Visual Indicators**: Clear visual feedback for selected task types
- **Unique Task IDs**: Each selected task type generates a unique task ID
- **Batch Confirmation**: Confirmation dialog shows all tasks that will be created

#### **Custom Task Names** *(ENHANCED UI)*
- **Prominent Input Section**: Custom task input in dedicated GroupBox with professional styling
- **Enhanced Input Fields**: Styled text input with focus indicators and Enter key support
- **Automatic Integration**: Newly added custom task types are automatically selected
- **Visual Success Feedback**: Green success message shows when custom task type is added
- **Scroll to New Item**: List automatically scrolls to show newly added custom task type
- **Validation**: Real-time validation ensures valid task names (alphanumeric and underscores only)
- **Project Storage**: Custom task types saved to project configuration for reuse
- **Team Sharing**: Custom task types available to all team members using the project
- **Common Examples**: previz, techvis, matchmove, roto, cleanup, paint

#### **Automatic Directory Creation**
- **PathBuilder Integration**: Uses existing project path templates
- **Directory Types**: Creates working, render, media, and cache directories
- **Optional Creation**: "Create directories automatically" checkbox (enabled by default)
- **Preview System**: Shows directory paths before creation
- **Progress Feedback**: Progress bar during directory creation
- **Error Handling**: Clear feedback on any directory creation issues

#### **Enhanced User Experience** *(ENHANCED UI + SCROLLABLE)*
- **Scrollable Interface**: Vertical scroll area ensures usability on smaller screens
- **Responsive Design**: Dialog adapts to screen size (minimum 600px height)
- **Size Constraints**: Maximum size limits prevent oversized dialogs
- **Professional Visual Design**: Modern, clean interface with consistent styling
- **Expanded Selection Area**: 67% larger task type selection area for better visibility
- **Real-time Selection Feedback**: Dynamic selection count indicators with color coding
- **Enhanced Button Styling**: Professional buttons with hover effects and color coding
- **Improved Visual Hierarchy**: Clear section labels and organized layout
- **Success Feedback**: Visual confirmation when custom task types are added
- **Real-time Preview**: Live preview of task IDs and directory paths
- **Validation Feedback**: Immediate feedback on form inputs and validation errors
- **Multi-Task Display**: Clear indication of how many tasks will be created
- **Duplicate Detection**: Warns about duplicate task IDs before creation
- **Batch Operations**: Efficient creation of multiple related tasks

#### **Smart Episode and Sequence Dropdowns** *(NEW)*
- **Database-Driven**: Automatically populated from existing project task data
- **Episode Dropdown**: Shows all episodes that have tasks in the current project
- **Sequence Dropdown**: Shows sequences filtered by selected episode (or all if no episode selected)
- **Editable Combo Boxes**: Users can select existing values or type new ones
- **Natural Sorting**: Episodes and sequences sorted naturally (Ep01, Ep02, Ep03, Ep10)
- **Dynamic Filtering**: Sequence list updates automatically when episode changes
- **Project-Specific**: Only shows episodes/sequences from the currently selected project
- **Asset Exclusion**: Asset tasks are excluded from episode/sequence lists
- **Fallback Support**: Works with both direct fields and task_id pattern extraction
- **Error Handling**: Gracefully handles empty projects and database errors

#### **Scrollable Interface** *(NEW + FIXED)*
- **Vertical Scroll Area**: Form content wrapped in scroll area for smaller screens
- **Adaptive Height**: Dialog minimum height reduced to 600px for laptop compatibility
- **Maximum Size Limits**: Dialog won't exceed 1400x1000px on large screens
- **Smooth Scrolling**: Native mouse wheel and keyboard navigation support
- **Preserved Layout**: All form sections maintain their layout within scroll area
- **No Horizontal Scrolling**: Horizontal scroll bars completely disabled and prevented
- **Adaptive Content Width**: Content automatically adapts to available viewport width
- **Dynamic Resizing**: Content width adjusts when dialog is resized
- **Clean Appearance**: Scroll area has no border frame for professional look
- **Responsive Behavior**: Only vertical scroll bars appear when content exceeds viewport height

## Editing Tasks

### **Editable Fields**
You can edit the following fields directly in the table:

#### **Artist Assignment**
- **How**: Double-click the Artist cell or press F2
- **Format**: Any text (can be empty)
- **Example**: "John Doe", "Jane Smith", ""

#### **Frame Range**
- **How**: Double-click the Frame Range cell
- **Format**: "start-end" (e.g., "1001-1153")
- **Validation**: Start frame must be less than end frame, both must be positive
- **Example**: "1001-1100", "2001-2500"

#### **Duration**
- **How**: Double-click the Duration cell
- **Format**: Decimal hours (e.g., 8.5 for 8.5 hours)
- **Validation**: Must be positive, warns if over 100 hours
- **Example**: "8.0", "16.5", "24.0"

#### **Status**
- **How**: Click the Status dropdown in the task row
- **Options**: not_started, in_progress, completed, on_hold, cancelled
- **Effect**: Changes are applied immediately

#### **Priority**
- **How**: Click the Priority dropdown in the task row
- **Options**: low, medium, high, urgent
- **Effect**: Changes are applied immediately

### **Visual Feedback**
- **Modified Tasks**: Show yellow background and asterisk (*) in Task ID
- **Invalid Input**: Red border appears for invalid values
- **Auto-Revert**: Invalid changes are automatically reverted with error message

## Saving Changes

### **Auto-Save**
- Changes are automatically saved 5 seconds after your last edit
- No need to manually save individual changes
- Status bar shows "X unsaved changes" while edits are pending

### **Manual Save**
- Click **Save All Changes** button in the header
- Use **Ctrl+S** keyboard shortcut
- Use **File > Save All** from the menu

### **Save Feedback**
- Status bar shows save progress and results
- Success message: "Saved X tasks successfully"
- Error handling: Specific error messages for failed saves

## Bulk Operations

### **Selecting Multiple Tasks**
1. Check the boxes in the **Select** column for tasks you want to modify
2. The selection counter shows "X tasks selected"
3. **Archive Selected** and **Bulk Edit** buttons become enabled

### **Bulk Edit Dialog**
1. Select multiple tasks using checkboxes
2. Click **Bulk Edit** button or use **Ctrl+B**
3. Choose which fields to change:
   - **Change Status**: Select new status for all selected tasks
   - **Change Priority**: Select new priority for all selected tasks
   - **Change Artist**: Enter new artist name for all selected tasks
4. Review current values shown in the dialog
5. Click **OK** to apply changes to all selected tasks

### **Archive Tasks**
- **Single Task**: Click **Archive** button in the task row
- **Multiple Tasks**: Select tasks and click **Archive Selected**
- **Effect**: Changes task status to 'cancelled' and hides from active view
- **Recovery**: Use Undo (Ctrl+Z) to restore archived tasks

## Undo/Redo System

### **Undo Changes**
- **Keyboard**: Press **Ctrl+Z**
- **Menu**: Edit > Undo
- **Toolbar**: Click Undo button
- **Scope**: Undoes the last change made to any task

### **Redo Changes**
- **Keyboard**: Press **Ctrl+Y**
- **Menu**: Edit > Redo
- **Toolbar**: Click Redo button
- **Scope**: Redoes the last undone change

### **Command History**
- Each change creates a command in the undo stack
- Commands have descriptive names (e.g., "Edit frame_range for ep01_sq010_sh020_lighting")
- Full history is maintained during the session

## Filtering and Search

### **Search Functionality**
- **Location**: Search box in the filter controls
- **Scope**: Searches Task ID, Artist name, and Task description
- **Behavior**: Real-time filtering as you type
- **Case**: Case-insensitive search

### **Filter Options**
- **Status Filter**: Show only tasks with specific status
- **Task Type Filter**: Show only specific types of tasks (lighting, comp, etc.)
- **Artist Filter**: Show only tasks assigned to specific artist
- **Combination**: All filters work together (AND logic)

### **Clear Filters**
- Click **Clear Filters** button to reset all filters and search
- Shows all tasks for the selected project

## Import/Export

### **CSV Import** (Original Functionality)
1. Switch to **CSV Import** tab
2. Click **Browse** to select CSV file
3. Configure naming patterns if needed
4. Click **Import Tasks** to process the file
5. Review task preview and errors
6. Click **Save to Database** to store tasks

### **Export Options**
- **Export to JSON**: File > Export > Export to JSON
- **Export to CSV**: File > Export > Export to CSV
- **Scope**: Exports currently filtered tasks
- **Format**: Maintains all task data and metadata

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Ctrl+S** | Save All Changes |
| **Ctrl+Z** | Undo |
| **Ctrl+Y** | Redo |
| **Ctrl+B** | Bulk Edit |
| **Ctrl+I** | Import CSV |
| **F5** | Refresh |
| **Ctrl+Q** | Exit |
| **F2** | Edit selected cell |
| **Escape** | Cancel current edit |

## Status Bar Information

### **Task Information**
- **Task Count**: "X tasks loaded" - shows total tasks for selected project
- **Selection**: "X tasks selected" - shows number of selected tasks
- **Filters**: Shows active filter information

### **Modification Tracking**
- **Unsaved Changes**: "X unsaved changes" in orange text
- **Last Save**: "Last saved: HH:MM:SS" timestamp
- **Save Status**: Progress and result messages

### **Operation Feedback**
- **Loading**: "Loading tasks..." during data retrieval
- **Saving**: Progress bar during save operations
- **Errors**: Red text for error conditions
- **Success**: Green text for successful operations

## Troubleshooting

### **Common Issues**

#### **Invalid Frame Range**
- **Error**: "Frame range must be in format 'start-end'"
- **Solution**: Use format like "1001-1100", ensure start < end

#### **Invalid Duration**
- **Error**: "Duration must be a positive number"
- **Solution**: Enter positive decimal number (e.g., 8.0, 16.5)

#### **Save Failures**
- **Error**: "Failed to save task X"
- **Solution**: Check database connection, try refreshing and saving again

#### **No Tasks Loaded**
- **Issue**: Empty task table after selecting project
- **Solution**: Check if project has tasks, try refreshing (F5)

### **Recovery Options**
- **Undo**: Use Ctrl+Z to revert problematic changes
- **Refresh**: Use F5 to reload clean data from database
- **Restart**: Close and reopen application if issues persist

### **Performance Tips**
- **Large Projects**: Use filters to reduce displayed tasks
- **Frequent Saves**: Let auto-save handle changes, avoid manual saves
- **Bulk Operations**: Use bulk edit for multiple similar changes

## Best Practices

### **Task Management**
1. **Use Filters**: Filter tasks by status or type for focused work
2. **Bulk Operations**: Use bulk edit for similar changes across multiple tasks
3. **Regular Saves**: Let auto-save work, but use manual save before major operations
4. **Archive vs Delete**: Archive completed or cancelled tasks instead of deleting

### **Data Entry**
1. **Frame Ranges**: Use consistent format (1001-1100) for clarity
2. **Artist Names**: Use consistent naming (e.g., "First Last" format)
3. **Status Updates**: Keep status current to reflect actual progress
4. **Duration Estimates**: Be realistic with time estimates

### **Workflow Integration**
1. **Project Selection**: Always verify correct project is selected
2. **Filter Usage**: Use filters to focus on relevant tasks
3. **Bulk Updates**: Coordinate bulk changes with team members
4. **Regular Refresh**: Refresh data when working in team environment

## Enhanced Features Troubleshooting

### **Project Creation & Editing Issues**

#### **Media Configuration Validation**
- **Error**: "At least one format must be selected"
- **Solution**: Select one or more formats for both final delivery and daily review categories

#### **Template Variable Errors**
- **Error**: Red warning text in filename patterns
- **Solution**: Ensure required variables (`{task}`, `{version}`) are present in all patterns
- **Reset Option**: Use "Reset to Defaults" button to restore SWA standard patterns

#### **Path Template Validation**
- **Error**: Missing essential variables warning
- **Solution**: Verify essential variables (`{project}`, `{drive_*}`) are included in path templates
- **Preview**: Use "Preview Paths" button to test template generation

#### **OCIO Configuration Issues**
- **Error**: "OCIO config file not found"
- **Solution**: Ensure the .ocio file exists at the specified path, or clear the field if not needed
- **Browse**: Use the "Browse..." button to select valid OCIO config files

#### **Resolution Settings Problems**
- **Error**: Custom resolution validation failure
- **Solution**: Custom resolutions must be between 1-8192 pixels for both width and height

### **Project Editing Problems**

#### **Read-only Project ID**
- **Issue**: Cannot change project ID in edit dialog
- **Explanation**: Project IDs cannot be changed after creation to maintain database integrity
- **Visual Indicator**: Field is grayed out with explanatory tooltip

#### **Changes Not Saving**
- **Error**: "Failed to save project changes"
- **Solutions**:
  - Check database connectivity
  - Verify file permissions
  - Try refreshing the application
  - Check for validation errors in form fields

#### **Form Reset Issues**
- **Issue**: Modified fields not reverting to original values
- **Solution**: Use "Reset to Original" button to restore all fields to their initial state
- **Alternative**: Close and reopen the edit dialog to discard changes

### **Archive System Issues**

#### **Archived Projects Still Visible**
- **Issue**: Archived projects appear in project lists
- **Solution**: Ensure "Show Archived Projects" toggle is disabled in Project Management tab
- **Check**: Verify project dropdown excludes archived projects

#### **Cannot Archive Project**
- **Error**: Archive button disabled or operation fails
- **Solutions**:
  - Ensure a project is selected in the Project Management tab
  - Check if project is currently active in the main application
  - Verify database write permissions

#### **Unarchive Not Working**
- **Issue**: Cannot see or unarchive archived projects
- **Solution**: Enable "Show Archived Projects" toggle checkbox to display archived projects
- **Visual Check**: Archived projects appear grayed out with archive date

#### **Archive Status Not Updating**
- **Issue**: Archive operations don't reflect in UI
- **Solution**: Use "Refresh Projects" button to update the projects list
- **Auto-refresh**: Project dropdown automatically updates after archive operations

## FAQ - Enhanced Features

**Q: Can I change a project's ID after creation?**
A: No, project IDs cannot be changed after creation to maintain database integrity and prevent breaking existing tasks and media references.

**Q: What happens to tasks when I archive a project?**
A: Tasks remain in the database but are filtered out from all Montu Manager applications. They become visible again when the project is unarchived.

**Q: Can I customize filename patterns for non-episode projects?**
A: Yes, the system automatically removes `{episode}` variables when you switch to non-episode project type, and you can further customize all patterns.

**Q: How do I restore default templates and patterns?**
A: Use the "Reset to Defaults" buttons in the Filename Patterns and Path Templates sections to restore SWA standard configurations.

**Q: What media formats are supported?**
A: Final delivery supports EXR, MOV, MP4, MXF, TIFF, DPX. Daily/review supports MOV, MP4, JPEG, PNG. You can select multiple formats for each category.

**Q: Can I edit multiple projects at once?**
A: Currently, projects must be edited individually. Batch editing is planned for future releases.

**Q: How do I know if a project has been modified?**
A: The projects table shows the last updated timestamp, and the edit dialog displays change indicators for modified fields.

**Q: What happens if I delete an OCIO config file after setting it in a project?**
A: The project will retain the path but validation will fail. You can update the path in the project edit dialog or clear it if no longer needed.

**Q: Can archived projects be permanently deleted?**
A: Currently, archived projects remain in the database. Permanent deletion functionality may be added in future releases with appropriate safeguards.

**Q: Do archived projects affect performance?**
A: No, archived projects are filtered out of all queries by default, so they don't impact application performance.

**Q: Can I see who archived a project and when?**
A: Yes, the archive information includes timestamp and source application. Future releases may include user tracking.

This comprehensive user guide covers all functionality of the enhanced Ra: Task Creator including the new media configuration, project editing, and archival features. For technical implementation details, refer to the complete feature documentation.
