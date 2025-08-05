# Ra: Task Creator - User Guide

## Quick Start Guide

### 1. **Launch the Application**
```bash
python scripts/launch-task-creator.py
```

### 2. **Select a Project**
- Use the **Project** dropdown in the header to select your project
- The application will automatically load all tasks for the selected project
- Task summary statistics will appear next to the project selector

### 3. **View and Filter Tasks**
- Use the **Search** box to find specific tasks by ID, artist, or description
- Apply filters using the **Status**, **Task Type**, and **Artist** dropdowns
- Click **Clear Filters** to reset all filters

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

This user guide covers the essential functionality of the enhanced Ra: Task Creator. For technical details and advanced features, refer to the comprehensive feature documentation.
