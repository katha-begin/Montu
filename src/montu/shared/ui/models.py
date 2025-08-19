"""
Scalable Task Model

High-performance Qt model for handling large task datasets with pagination,
virtual scrolling, and optimized database queries.
"""

from typing import Dict, List, Any, Optional, Tuple
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, Signal, QTimer
from PySide6.QtGui import QColor, QBrush
import time


class ScalableTaskModel(QAbstractTableModel):
    """
    High-performance task model with pagination and virtual scrolling support.
    
    Features:
    - Pagination with configurable page size
    - Virtual scrolling for smooth UI performance
    - Optimized database queries with LIMIT/OFFSET
    - Real-time search with debouncing
    - Efficient filtering with database-level queries
    - Memory-efficient task loading
    """
    
    # Signals
    taskStatusChanged = Signal(str, str)  # task_id, new_status
    taskSelectionChanged = Signal(str)    # task_id
    loadingStateChanged = Signal(bool)    # is_loading
    totalCountChanged = Signal(int)       # total_task_count
    
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
    
    # Performance configuration
    DEFAULT_PAGE_SIZE = 100
    SEARCH_DEBOUNCE_MS = 300
    MAX_MEMORY_TASKS = 500  # Maximum tasks to keep in memory
    
    def __init__(self, db_instance, parent=None):
        """Initialize scalable task model."""
        super().__init__(parent)
        
        # Database connection
        self.db = db_instance
        
        # Data storage
        self.tasks: List[Dict[str, Any]] = []
        self.total_task_count = 0
        self.current_page = 0
        self.page_size = self.DEFAULT_PAGE_SIZE
        
        # Filtering and search
        self.current_filters: Dict[str, Any] = {}
        self.current_search = ""
        self.current_project_id = ""
        
        # Performance optimization
        self.is_loading = False
        self.task_cache: Dict[int, Dict[str, Any]] = {}  # page_number -> tasks
        self.cache_size_limit = 5  # Keep 5 pages in cache
        
        # Search debouncing
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._execute_search)
        
    def set_project(self, project_id: str):
        """Set current project and reset model."""
        if self.current_project_id != project_id:
            self.current_project_id = project_id
            self.reset_model()
    
    def reset_model(self):
        """Reset model and reload first page."""
        self.beginResetModel()
        self.tasks.clear()
        self.task_cache.clear()
        self.current_page = 0
        self.total_task_count = 0
        self.endResetModel()
        
        if self.current_project_id:
            self.load_page(0)
    
    def load_page(self, page_number: int):
        """Load specific page of tasks."""
        if self.is_loading:
            return
        
        # Check cache first
        if page_number in self.task_cache:
            self._apply_cached_page(page_number)
            return
        
        self.is_loading = True
        self.loadingStateChanged.emit(True)
        
        try:
            # Build database query
            query = {'project': self.current_project_id}
            
            # Add filters to query
            if self.current_filters:
                query.update(self.current_filters)
            
            # Add search to query if present
            if self.current_search:
                # Use database-level text search for better performance
                query['$or'] = [
                    {'_id': {'$regex': self.current_search, '$options': 'i'}},
                    {'task': {'$regex': self.current_search, '$options': 'i'}},
                    {'artist': {'$regex': self.current_search, '$options': 'i'}},
                    {'sequence': {'$regex': self.current_search, '$options': 'i'}},
                    {'shot': {'$regex': self.current_search, '$options': 'i'}}
                ]

            # Handle exclude_cancelled filter
            if self.current_filters.get('exclude_cancelled'):
                query['status'] = {'$ne': 'cancelled'}
            
            # Get total count for pagination
            if page_number == 0 or self.total_task_count == 0:
                all_tasks = self.db.find('tasks', query)
                self.total_task_count = len(all_tasks)
                self.totalCountChanged.emit(self.total_task_count)
            
            # Get paginated results
            skip = page_number * self.page_size
            page_tasks = self.db.find_with_options(
                'tasks',
                query=query,
                sort=[('_created_at', -1)],  # Most recent first
                limit=self.page_size,
                skip=skip
            )
            
            # Cache the page
            self.task_cache[page_number] = page_tasks
            self._manage_cache_size()
            
            # Apply to model
            self.beginResetModel()
            self.tasks = page_tasks
            self.current_page = page_number
            self.endResetModel()
            
        except Exception as e:
            print(f"Error loading page {page_number}: {e}")
        finally:
            self.is_loading = False
            self.loadingStateChanged.emit(False)
    
    def _apply_cached_page(self, page_number: int):
        """Apply cached page data to model."""
        self.beginResetModel()
        self.tasks = self.task_cache[page_number]
        self.current_page = page_number
        self.endResetModel()
    
    def _manage_cache_size(self):
        """Manage cache size to prevent memory issues."""
        if len(self.task_cache) > self.cache_size_limit:
            # Remove oldest cached pages
            pages_to_remove = len(self.task_cache) - self.cache_size_limit
            oldest_pages = sorted(self.task_cache.keys())[:pages_to_remove]
            for page in oldest_pages:
                del self.task_cache[page]
    
    def apply_filters(self, filters: Dict[str, Any]):
        """Apply filters and reload data."""
        if filters != self.current_filters:
            self.current_filters = filters
            self.task_cache.clear()  # Clear cache when filters change
            self.load_page(0)  # Reload first page
    
    def set_search_text(self, search_text: str):
        """Set search text with debouncing."""
        self.current_search = search_text.strip()
        self.search_timer.start(self.SEARCH_DEBOUNCE_MS)
    
    def _execute_search(self):
        """Execute search after debounce period."""
        self.task_cache.clear()  # Clear cache when search changes
        self.load_page(0)  # Reload first page
    
    def next_page(self):
        """Load next page of tasks."""
        max_page = (self.total_task_count - 1) // self.page_size
        if self.current_page < max_page:
            self.load_page(self.current_page + 1)
    
    def previous_page(self):
        """Load previous page of tasks."""
        if self.current_page > 0:
            self.load_page(self.current_page - 1)
    
    def get_pagination_info(self) -> Dict[str, int]:
        """Get current pagination information."""
        max_page = max(0, (self.total_task_count - 1) // self.page_size)
        start_item = self.current_page * self.page_size + 1
        end_item = min(start_item + len(self.tasks) - 1, self.total_task_count)
        
        return {
            'current_page': self.current_page + 1,  # 1-based for display
            'total_pages': max_page + 1,
            'page_size': self.page_size,
            'total_items': self.total_task_count,
            'start_item': start_item,
            'end_item': end_item,
            'items_on_page': len(self.tasks)
        }
    
    # Qt Model Interface
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return number of rows in current page."""
        return len(self.tasks)
    
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
        if not index.isValid() or index.row() >= len(self.tasks):
            return None
        
        task = self.tasks[index.row()]
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
            
            elif field_name == 'working_file_path':
                # Show filename only for display
                if value:
                    return value.split('/')[-1].split('\\')[-1]
                return 'Not generated'
            
            return str(value)
        
        elif role == Qt.BackgroundRole:
            # Status-based row coloring
            status = task.get('status', '')
            if status == 'completed':
                return QBrush(QColor(200, 255, 200))  # Light green
            elif status == 'in_progress':
                return QBrush(QColor(255, 255, 200))  # Light yellow
            elif status == 'on_hold':
                return QBrush(QColor(255, 220, 200))  # Light orange
            elif status == 'cancelled':
                return QBrush(QColor(255, 200, 200))  # Light red
        
        return None
    
    def get_task_by_row(self, row: int) -> Optional[Dict[str, Any]]:
        """Get task data by row index."""
        if 0 <= row < len(self.tasks):
            return self.tasks[row]
        return None
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task data by task ID (searches current page only)."""
        for task in self.tasks:
            if task.get('_id') == task_id:
                return task
        return None
