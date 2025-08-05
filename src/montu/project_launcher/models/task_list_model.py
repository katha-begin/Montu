"""
Task List Model

Qt model for displaying and managing tasks in the Project Launcher.
Provides table-based display with sorting, filtering, and real-time updates.
"""

from typing import Dict, List, Any, Optional
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, Signal
from PySide6.QtGui import QColor, QBrush


class TaskListModel(QAbstractTableModel):
    """
    Qt model for task list display with database integration.
    
    Provides table-based view of tasks with status-based styling,
    sorting capabilities, and real-time updates.
    """
    
    # Signals
    taskStatusChanged = Signal(str, str)  # task_id, new_status
    taskSelectionChanged = Signal(str)    # task_id
    
    # Column definitions
    COLUMNS = [
        ('Task ID', '_id'),
        ('Episode', 'episode'),
        ('Sequence', 'sequence_clean'),
        ('Shot', 'shot_clean'),
        ('Task', 'task'),
        ('Artist', 'artist'),
        ('Status', 'status'),
        ('Priority', 'priority'),
        ('Frame Range', 'frame_range'),
        ('Duration (hrs)', 'estimated_duration_hours'),
        ('Working File', 'working_file_path')
    ]
    
    # Status color mapping
    STATUS_COLORS = {
        'not_started': QColor(200, 200, 200),      # Light gray
        'in_progress': QColor(255, 193, 7),        # Amber
        'completed': QColor(40, 167, 69),          # Green
        'on_hold': QColor(255, 152, 0),            # Orange
        'cancelled': QColor(220, 53, 69),          # Red
        'approved': QColor(25, 135, 84)            # Dark green
    }
    
    # Priority color mapping
    PRIORITY_COLORS = {
        'low': QColor(108, 117, 125),              # Gray
        'medium': QColor(13, 110, 253),            # Blue
        'high': QColor(255, 193, 7),               # Amber
        'urgent': QColor(220, 53, 69)              # Red
    }
    
    def __init__(self, parent=None):
        """Initialize task list model."""
        super().__init__(parent)
        self.tasks: List[Dict[str, Any]] = []
        self.filtered_tasks: List[Dict[str, Any]] = []
        self.current_filters: Dict[str, Any] = {}
        
    def set_tasks(self, tasks: List[Dict[str, Any]]):
        """Set task data and refresh model."""
        self.beginResetModel()
        self.tasks = tasks.copy()
        self.apply_filters()
        self.endResetModel()
    
    def apply_filters(self, filters: Optional[Dict[str, Any]] = None):
        """Apply filters to task list."""
        if filters is not None:
            self.current_filters = filters

        if not self.current_filters:
            self.filtered_tasks = self.tasks.copy()
        else:
            self.filtered_tasks = []
            for task in self.tasks:
                match = True
                for key, value in self.current_filters.items():
                    if key == 'search':
                        # Text search across multiple fields
                        search_fields = ['_id', 'task', 'artist', 'sequence', 'shot']
                        found = False
                        for field in search_fields:
                            if value.lower() in str(task.get(field, '')).lower():
                                found = True
                                break
                        if not found:
                            match = False
                            break
                    elif key == 'exclude_cancelled':
                        # Special filter to exclude cancelled/archived tasks
                        if value and task.get('status') == 'cancelled':
                            match = False
                            break
                    else:
                        task_value = task.get(key)
                        if task_value != value:
                            match = False
                            break

                if match:
                    self.filtered_tasks.append(task)
    
    def refresh_filters(self):
        """Refresh current filters."""
        self.beginResetModel()
        self.apply_filters()
        self.endResetModel()
    
    def get_task_by_row(self, row: int) -> Optional[Dict[str, Any]]:
        """Get task data by row index."""
        if 0 <= row < len(self.filtered_tasks):
            return self.filtered_tasks[row]
        return None
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task data by task ID."""
        for task in self.tasks:
            if task.get('_id') == task_id:
                return task
        return None
    
    def update_task_status(self, task_id: str, status: str):
        """Update task status in model."""
        # Update in main task list
        for task in self.tasks:
            if task.get('_id') == task_id:
                task['status'] = status
                break
        
        # Update in filtered list
        for task in self.filtered_tasks:
            if task.get('_id') == task_id:
                task['status'] = status
                break
        
        # Find row and emit data changed
        for row, task in enumerate(self.filtered_tasks):
            if task.get('_id') == task_id:
                status_col = next(i for i, (_, field) in enumerate(self.COLUMNS) if field == 'status')
                index = self.createIndex(row, status_col)
                self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.BackgroundRole])
                break
        
        # Emit custom signal
        self.taskStatusChanged.emit(task_id, status)
    
    # Qt Model Interface
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return number of rows."""
        return len(self.filtered_tasks)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return number of columns."""
        return len(self.COLUMNS)
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        """Return header data."""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if 0 <= section < len(self.COLUMNS):
                return self.COLUMNS[section][0]
        return None
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        """Return data for given index and role."""
        if not index.isValid() or index.row() >= len(self.filtered_tasks):
            return None
        
        task = self.filtered_tasks[index.row()]
        column_name, field_name = self.COLUMNS[index.column()]
        
        if role == Qt.DisplayRole:
            value = task.get(field_name, '')
            
            # Special formatting for certain fields
            if field_name == 'frame_range':
                if isinstance(value, dict):
                    start = value.get('start', 0)
                    end = value.get('end', 0)
                    return f"{start}-{end}"
                return str(value)
            
            elif field_name == 'estimated_duration_hours':
                try:
                    hours = float(value)
                    return f"{hours:.1f}"
                except (ValueError, TypeError):
                    return str(value)
            
            elif field_name in ['sequence_clean', 'shot_clean']:
                # Use cleaned names if available, fallback to original
                if not value:
                    original_field = field_name.replace('_clean', '')
                    original_value = task.get(original_field, '')
                    # Simple cleaning for display
                    if original_value and '_' in original_value:
                        parts = original_value.split('_')
                        return parts[-1] if parts else original_value
                    return original_value
                return value
            
            elif field_name == 'working_file_path':
                # Show filename only for display
                if value:
                    return value.split('/')[-1].split('\\')[-1]
                return 'Not generated'
            
            return str(value)
        
        elif role == Qt.BackgroundRole:
            # Color coding based on status and priority
            status = task.get('status', '')
            priority = task.get('priority', '')
            
            if field_name == 'status' and status in self.STATUS_COLORS:
                return QBrush(self.STATUS_COLORS[status])
            
            elif field_name == 'priority' and priority in self.PRIORITY_COLORS:
                return QBrush(self.PRIORITY_COLORS[priority])
        
        elif role == Qt.ToolTipRole:
            # Provide tooltips for certain fields
            if field_name == 'working_file_path':
                return task.get(field_name, 'Path not generated')
            
            elif field_name == 'status':
                status = task.get('status', '')
                return f"Status: {status.replace('_', ' ').title()}"
            
            elif field_name == 'priority':
                priority = task.get('priority', '')
                return f"Priority: {priority.title()}"
            
            elif field_name == '_id':
                return f"Task ID: {task.get('_id', '')}"
        
        return None
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Return item flags."""
        if not index.isValid():
            return Qt.NoItemFlags
        
        # Make status column editable
        column_name, field_name = self.COLUMNS[index.column()]
        if field_name == 'status':
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
        """Set data for editable fields."""
        if not index.isValid() or role != Qt.EditRole:
            return False
        
        task = self.filtered_tasks[index.row()]
        column_name, field_name = self.COLUMNS[index.column()]
        
        if field_name == 'status':
            task_id = task.get('_id')
            if task_id:
                self.update_task_status(task_id, str(value))
                return True
        
        return False
